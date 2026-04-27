from typing import Any

import numpy as np

from backend.app.recommendation.optimizers import FangCollaborativeOptimizer
from backend.app.recommendation.scorers import FangVacancyScorer
from backend.app.recommendation.updaters import FangCollaborativeOptimizerUpdater, FangVacancyScorerUpdater
from backend.app.repositories import ConfigRepository, UserRepository, VacancyRepository

def test_collaborative_optimizer_updater_empty_users():
    class MockUserRepository(UserRepository):
        def __init__(self):
            self.called_count = 0

        def get_all_user_ids(self) -> list[int]:
            self.called_count += 1
            return []
    
    class MockFangCollaborativeOptimizer(FangCollaborativeOptimizer):
        def __init__(self):
            pass

        def optimize(self, user_id: int) -> None:
            assert False, "Shouldn't be called."

    class MockConfigRepository(ConfigRepository):
        def __init__(self):
            pass
        
    user_repo = MockUserRepository()
    config_repo = MockConfigRepository()
    optim = MockFangCollaborativeOptimizer()
    updater = FangCollaborativeOptimizerUpdater(
        user_repository=user_repo,
        config_repository=config_repo,
        collaborative_optimizer=optim
    )
    updater.update()
    assert user_repo.called_count == 1

def test_collaborative_optimizer_updater_one_user_error_same_as_max():
    np.random.seed(120)
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_MAX_ERROR = np.random.exponential()

    class MockUserRepository(UserRepository):
        def __init__(self):
            self.called_count = 0

        def get_all_user_ids(self) -> list[int]:
            self.called_count += 1
            return [CHOSEN_USER_ID]
        
    class MockFangCollaborativeOptimizer(FangCollaborativeOptimizer):
        def __init__(self):
            self.optimize_called_count = 0
            self.get_called_count = 0
            self.current_error = 0.0

        def optimize(self, user_id: int) -> None:
            assert user_id == CHOSEN_USER_ID
            self.optimize_called_count += 1
            self.current_error = CHOSEN_MAX_ERROR

        def get_last_error(self) -> float:
            self.get_called_count += 1
            return self.current_error

    class MockConfigRepository(ConfigRepository):
        def __init__(self):
            self.called_count = 0

        def get_fang_max_train_error(self) -> float:
            self.called_count += 1
            return CHOSEN_MAX_ERROR
        
        def get_fang_max_train_steps(self) -> int:
            return 2
    
    user_repo = MockUserRepository()
    config_repo = MockConfigRepository()
    optim = MockFangCollaborativeOptimizer()
    updater = FangCollaborativeOptimizerUpdater(
        user_repository=user_repo,
        config_repository=config_repo,
        collaborative_optimizer=optim
    )
    updater.update()

    assert user_repo.called_count == 1
    assert optim.optimize_called_count == 1
    assert config_repo.called_count == 1
    assert optim.get_called_count == 1

def test_collaborative_optimizer_updater_one_user_stopped_by_max_steps():
    np.random.seed(120)
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_MAX_ERROR = np.random.exponential()

    class MockUserRepository(UserRepository):
        def __init__(self):
            self.called_count = 0

        def get_all_user_ids(self) -> list[int]:
            self.called_count += 1
            return [CHOSEN_USER_ID]
        
    class MockFangCollaborativeOptimizer(FangCollaborativeOptimizer):
        def __init__(self):
            self.optimize_called_count = 0
            self.get_called_count = 0
            self.current_error = 0.0

        def optimize(self, user_id: int) -> None:
            assert user_id == CHOSEN_USER_ID
            self.optimize_called_count += 1
            self.current_error = 2 * CHOSEN_MAX_ERROR

        def get_last_error(self) -> float:
            self.get_called_count += 1
            return self.current_error

    class MockConfigRepository(ConfigRepository):
        def __init__(self):
            self.error_called_count = 0
            self.steps_called_count = 0

        def get_fang_max_train_error(self) -> float:
            self.error_called_count += 1
            return CHOSEN_MAX_ERROR
        
        def get_fang_max_train_steps(self) -> int:
            self.steps_called_count += 1
            return 1
    
    user_repo = MockUserRepository()
    config_repo = MockConfigRepository()
    optim = MockFangCollaborativeOptimizer()
    updater = FangCollaborativeOptimizerUpdater(
        user_repository=user_repo,
        config_repository=config_repo,
        collaborative_optimizer=optim
    )
    updater.update()

    assert user_repo.called_count == 1
    assert optim.optimize_called_count == 1
    assert config_repo.error_called_count == 1
    assert config_repo.steps_called_count == 1
    assert optim.get_called_count == 1

def test_collaborative_optimizer_updater_two_users_error_same_as_max():
    np.random.seed(120)
    CHOSEN_USER_ID_1 = np.random.randint(999_999_999)
    CHOSEN_USER_ID_2 = np.random.randint(999_999_999)
    assert CHOSEN_USER_ID_1 != CHOSEN_USER_ID_2, "Change the seed"
    chosen_user_ids = [CHOSEN_USER_ID_1, CHOSEN_USER_ID_2]

    CHOSEN_MAX_ERROR = np.random.exponential()

    class MockUserRepository(UserRepository):
        def __init__(self):
            self.called_count = 0

        def get_all_user_ids(self) -> list[int]:
            self.called_count += 1
            return chosen_user_ids.copy()
        
    class MockFangCollaborativeOptimizer(FangCollaborativeOptimizer):
        def __init__(self):
            self.optimize_called_count = 0
            self.get_called_count = 0
            self.current_error = 0.0
            self.expected_user_id_index = 0

        def optimize(self, user_id: int) -> None:
            assert user_id == chosen_user_ids[self.expected_user_id_index]
            self.optimize_called_count += 1
            self.current_error = CHOSEN_MAX_ERROR

            self.expected_user_id_index = 1 - self.expected_user_id_index

        def get_last_error(self) -> float:
            self.get_called_count += 1
            return self.current_error

    class MockConfigRepository(ConfigRepository):
        def __init__(self):
            self.error_called_count = 0
            self.steps_called_count = 0

        def get_fang_max_train_error(self) -> float:
            self.error_called_count += 1
            return CHOSEN_MAX_ERROR
        
        def get_fang_max_train_steps(self) -> int:
            self.steps_called_count += 1
            return 10
    
    user_repo = MockUserRepository()
    config_repo = MockConfigRepository()
    optim = MockFangCollaborativeOptimizer()
    updater = FangCollaborativeOptimizerUpdater(
        user_repository=user_repo,
        config_repository=config_repo,
        collaborative_optimizer=optim
    )
    updater.update()

    assert user_repo.called_count == 1
    assert optim.optimize_called_count == 2
    assert config_repo.error_called_count == 1
    assert config_repo.steps_called_count == 1
    assert optim.get_called_count == 2

def test_collaborative_optimizer_updater_one_user_stopped_by_max_error_after_two_steps():
    np.random.seed(120)
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_MAX_ERROR = np.random.exponential()

    class MockUserRepository(UserRepository):
        def __init__(self):
            self.called_count = 0

        def get_all_user_ids(self) -> list[int]:
            self.called_count += 1
            return [CHOSEN_USER_ID]
        
    class MockFangCollaborativeOptimizer(FangCollaborativeOptimizer):
        def __init__(self):
            self.optimize_called_count = 0
            self.get_called_count = 0
            self.current_error = 0.0

        def optimize(self, user_id: int) -> None:
            assert user_id == CHOSEN_USER_ID
            self.optimize_called_count += 1
            if self.optimize_called_count < 2:
                self.current_error = 2 * CHOSEN_MAX_ERROR
            else:
                self.current_error = CHOSEN_MAX_ERROR

        def get_last_error(self) -> float:
            self.get_called_count += 1
            return self.current_error

    class MockConfigRepository(ConfigRepository):
        def __init__(self):
            self.error_called_count = 0
            self.steps_called_count = 0

        def get_fang_max_train_error(self) -> float:
            self.error_called_count += 1
            return CHOSEN_MAX_ERROR
        
        def get_fang_max_train_steps(self) -> int:
            self.steps_called_count += 1
            return 10
    
    user_repo = MockUserRepository()
    config_repo = MockConfigRepository()
    optim = MockFangCollaborativeOptimizer()
    updater = FangCollaborativeOptimizerUpdater(
        user_repository=user_repo,
        config_repository=config_repo,
        collaborative_optimizer=optim
    )
    updater.update()

    assert user_repo.called_count == 1
    assert optim.optimize_called_count == 2
    assert config_repo.error_called_count == 1
    assert config_repo.steps_called_count == 1
    assert optim.get_called_count == 2

def test_collaborative_optimizer_updater_two_users_error_same_as_max_after_one_step():
    np.random.seed(120)
    CHOSEN_USER_ID_1 = np.random.randint(999_999_999)
    CHOSEN_USER_ID_2 = np.random.randint(999_999_999)
    assert CHOSEN_USER_ID_1 != CHOSEN_USER_ID_2, "Change the seed"
    chosen_user_ids = [CHOSEN_USER_ID_1, CHOSEN_USER_ID_2]

    CHOSEN_MAX_ERROR = np.random.exponential()

    class MockUserRepository(UserRepository):
        def __init__(self):
            self.called_count = 0

        def get_all_user_ids(self) -> list[int]:
            self.called_count += 1
            return chosen_user_ids.copy()
        
    class MockFangCollaborativeOptimizer(FangCollaborativeOptimizer):
        def __init__(self):
            self.optimize_called_count = 0
            self.get_called_count = 0
            self.current_error = 0.0
            self.expected_user_id_index = 0

        def optimize(self, user_id: int) -> None:
            assert user_id == chosen_user_ids[self.expected_user_id_index]
            self.optimize_called_count += 1
            if self.optimize_called_count <= 1:
                self.current_error = 2 * CHOSEN_MAX_ERROR
            else:
                self.current_error = CHOSEN_MAX_ERROR

            self.expected_user_id_index = 1 - self.expected_user_id_index

        def get_last_error(self) -> float:
            self.get_called_count += 1
            return self.current_error

    class MockConfigRepository(ConfigRepository):
        def __init__(self):
            self.error_called_count = 0
            self.steps_called_count = 0

        def get_fang_max_train_error(self) -> float:
            self.error_called_count += 1
            return CHOSEN_MAX_ERROR
        
        def get_fang_max_train_steps(self) -> int:
            self.steps_called_count += 1
            return 10
    
    user_repo = MockUserRepository()
    config_repo = MockConfigRepository()
    optim = MockFangCollaborativeOptimizer()
    updater = FangCollaborativeOptimizerUpdater(
        user_repository=user_repo,
        config_repository=config_repo,
        collaborative_optimizer=optim
    )
    updater.update()

    assert user_repo.called_count == 1
    assert optim.optimize_called_count == 3
    assert config_repo.error_called_count == 1
    assert config_repo.steps_called_count == 1
    assert optim.get_called_count == 3

def test_collaborative_optimizer_updater_two_users_error_same_as_max_when_second_not_converged_at_first():
    np.random.seed(120)
    CHOSEN_USER_ID_1 = np.random.randint(999_999_999)
    CHOSEN_USER_ID_2 = np.random.randint(999_999_999)
    assert CHOSEN_USER_ID_1 != CHOSEN_USER_ID_2, "Change the seed"
    chosen_user_ids = [CHOSEN_USER_ID_1, CHOSEN_USER_ID_2]

    CHOSEN_MAX_ERROR = np.random.exponential()

    class MockUserRepository(UserRepository):
        def __init__(self):
            self.called_count = 0

        def get_all_user_ids(self) -> list[int]:
            self.called_count += 1
            return chosen_user_ids.copy()
        
    class MockFangCollaborativeOptimizer(FangCollaborativeOptimizer):
        def __init__(self):
            self.optimize_called_count = 0
            self.get_called_count = 0
            self.current_error = 0.0
            self.expected_user_id_index = 0

        def optimize(self, user_id: int) -> None:
            assert user_id == chosen_user_ids[self.expected_user_id_index]
            self.optimize_called_count += 1
            if self.optimize_called_count == 2:
                self.current_error = 2 * CHOSEN_MAX_ERROR
            else:
                self.current_error = CHOSEN_MAX_ERROR

            self.expected_user_id_index = 1 - self.expected_user_id_index

        def get_last_error(self) -> float:
            self.get_called_count += 1
            return self.current_error

    class MockConfigRepository(ConfigRepository):
        def __init__(self):
            self.error_called_count = 0
            self.steps_called_count = 0

        def get_fang_max_train_error(self) -> float:
            self.error_called_count += 1
            return CHOSEN_MAX_ERROR
        
        def get_fang_max_train_steps(self) -> int:
            self.steps_called_count += 1
            return 10
    
    user_repo = MockUserRepository()
    config_repo = MockConfigRepository()
    optim = MockFangCollaborativeOptimizer()
    updater = FangCollaborativeOptimizerUpdater(
        user_repository=user_repo,
        config_repository=config_repo,
        collaborative_optimizer=optim
    )
    updater.update()

    assert user_repo.called_count == 1
    assert optim.optimize_called_count == 4
    assert config_repo.error_called_count == 1
    assert config_repo.steps_called_count == 1
    assert optim.get_called_count == 4

def test_vacancy_scorer_updater():
    np.random.seed(120)
    N_USERS = 3 + int(np.random.exponential(2))
    N_VACANCIES = 3 + int(np.random.exponential(2))

    user_id_list: list[int] = []
    while len(user_id_list) < N_USERS:
        user_id = np.random.randint(999_999_999)
        if user_id not in user_id_list:
            user_id_list.append(user_id)

    vacancy_id_list: list[int] = []
    while len(vacancy_id_list) < N_VACANCIES:
        vacancy_id = np.random.randint(999_999_999)
        if vacancy_id not in vacancy_id_list:
            vacancy_id_list.append(vacancy_id)

    scores: dict[tuple[int, int], float] = {}
    for u in user_id_list:
        for v in vacancy_id_list:
            scores[(u, v)] = np.random.random() * 5
    
    class MockFangVacancyScorer(FangVacancyScorer):
        def __init__(self):
            pass

        def get_score(self, user_id, vacancy_id) -> float:
            return scores[(user_id, vacancy_id)]
        
    class MockUserRepository(UserRepository):
        def __init__(self):
            self.remaining_tuples = [k for k in scores.keys()]

        def get_all_user_ids(self) -> list[Any]:
            return user_id_list
        
        def set_vacancy_score(self, id, vacancy_id, score: float):
            key = (id, vacancy_id)
            assert key in self.remaining_tuples
            assert score == scores[(id, vacancy_id)]
            self.remaining_tuples.remove(key)
        
    class MockVacancyRepository(VacancyRepository):
        def __init__(self):
            pass

        def get_all_vacancy_ids(self) -> list[Any]:
            return vacancy_id_list

    scorer = MockFangVacancyScorer()
    user_repo = MockUserRepository()
    vacancy_repo = MockVacancyRepository()
    updater = FangVacancyScorerUpdater(
        scorer=scorer,
        user_repository=user_repo,
        vacancy_repository=vacancy_repo
    )
    updater.update()
    assert len(user_repo.remaining_tuples) == 0

