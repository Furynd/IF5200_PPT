import numpy as np

from src.recommendation.optimizers import FangCollaborativeOptimizer
from src.recommendation.updaters import FangVacancyScorerUpdater
from src.repositories import ConfigRepository, UserRepository

def test_vacancy_scorer_updater_empty_users():
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
    updater = FangVacancyScorerUpdater(
        user_repository=user_repo,
        config_repository=config_repo,
        collaborative_optimizer=optim
    )
    updater.update()
    assert user_repo.called_count == 1

def test_vacancy_scorer_updater_one_user_error_same_as_max():
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
    updater = FangVacancyScorerUpdater(
        user_repository=user_repo,
        config_repository=config_repo,
        collaborative_optimizer=optim
    )
    updater.update()

    assert user_repo.called_count == 1
    assert optim.optimize_called_count == 1
    assert config_repo.called_count == 1
    assert optim.get_called_count == 1

def test_vacancy_scorer_updater_one_user_stopped_by_max_steps():
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
    updater = FangVacancyScorerUpdater(
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

def test_vacancy_scorer_updater_two_users_error_same_as_max():
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
    updater = FangVacancyScorerUpdater(
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

def test_vacancy_scorer_updater_one_user_stopped_by_max_error_after_two_steps():
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
    updater = FangVacancyScorerUpdater(
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

def test_vacancy_scorer_updater_two_users_error_same_as_max_after_one_step():
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
    updater = FangVacancyScorerUpdater(
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

def test_vacancy_scorer_updater_two_users_error_same_as_max_when_second_not_converged_at_first():
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
    updater = FangVacancyScorerUpdater(
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
