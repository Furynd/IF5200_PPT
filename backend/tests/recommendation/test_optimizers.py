import numpy as np
import numpy.typing as npt

from backend.recommendation.optimizers import FangCollaborativeOptimizer
from backend.repositories import ConfigRepository, FangCollaborativeParameterRepository, UserRepository

def test_fang_collaborative_optimizer():
    DIMENSION = 10
    chosen_user_id = np.random.randint(999_999_999)
    initial_global_bias = np.random.randn()
    initial_user_latent_vector = np.random.randn(DIMENSION)
    initial_user_bias = np.random.randn()

    initial_skill_latent_vectors: dict[int, npt.NDArray[np.float64]] = {}
    initial_skill_biases: dict[int, float] = {}
    actual_scores: dict[int, float] = {}

    predicted_score_grad = 0.0
    expected_total_error = 0.0

    for _ in range(3 + int(np.random.exponential(2))):
        stop = False
        skill_id = -1
        while not stop:
            skill_id = np.random.randint(999_999_999)
            stop = skill_id not in initial_skill_latent_vectors
        
        initial_skill_latent_vectors[skill_id] = np.random.randn(DIMENSION)
        initial_skill_biases[skill_id] = np.random.randn()

        initial_predicted_score = (
            initial_global_bias
            + initial_user_bias
            + initial_skill_biases[skill_id]
            + np.dot(initial_user_latent_vector,
                    initial_skill_latent_vectors[skill_id])
        )
        actual_scores[skill_id] = np.random.randn()
        expected_total_error += (initial_predicted_score - actual_scores[skill_id]) ** 2
        predicted_score_grad += 2 * (initial_predicted_score - actual_scores[skill_id])

    learning_rate = np.random.exponential(0.1)
    regularization_factor = np.random.exponential(1)
    
    expected_final_global_bias = initial_global_bias - learning_rate * (
        predicted_score_grad + 2 * regularization_factor * initial_global_bias
    )

    expected_final_user_bias = initial_user_bias - learning_rate * (
        predicted_score_grad + 2 * regularization_factor * initial_user_bias
    )

    expected_final_skill_latent_vectors: dict[int, npt.NDArray[np.float64]] = {}
    expected_final_skill_biases: dict[int, float] = {}
    user_latent_vector_grad = 2 * regularization_factor * initial_user_latent_vector
    for skill_id in initial_skill_latent_vectors.keys():
        expected_final_skill_biases[skill_id] = initial_skill_biases[skill_id] - learning_rate * (
            predicted_score_grad + 2 * regularization_factor * initial_skill_biases[skill_id]
        )
        expected_final_skill_latent_vectors[skill_id] = initial_skill_latent_vectors[skill_id] - learning_rate * (
            predicted_score_grad * initial_user_latent_vector + 2 * regularization_factor * initial_skill_latent_vectors[skill_id]
        )
        user_latent_vector_grad += predicted_score_grad * initial_skill_latent_vectors[skill_id]
    
    expected_final_user_latent_vector = initial_user_latent_vector - learning_rate * user_latent_vector_grad
    
    max_error = 1e-8

    class MockFangCollaborativeParameterRepository(FangCollaborativeParameterRepository):
        def __init__(self):
            self.action_limit = 2 * (3 + 2 * len(initial_skill_latent_vectors))
            
            self.global_bias = initial_global_bias
            self.user_latent_vector = initial_user_latent_vector
            self.user_bias = initial_user_bias
            self.skill_latent_vectors = initial_skill_latent_vectors
            self.skill_biases = initial_skill_biases

        def _act(self):
            assert self.action_limit > 0
            self.action_limit -= 1

        def get_global_bias(self) -> float:
            self._act()
            return self.global_bias
        
        def get_user_latent_vector(self, user_id: int) -> npt.NDArray[np.float64]:
            assert user_id == chosen_user_id
            self._act()
            return self.user_latent_vector
        
        def get_user_bias(self, user_id: int) -> float:
            assert user_id == chosen_user_id
            self._act()
            return self.user_bias
        
        def get_skill_latent_vector(self, skill_id: int) -> npt.NDArray[np.float64]:
            self._act()
            return self.skill_latent_vectors[skill_id]
        
        def get_skill_bias(self, skill_id: int) -> float:
            self._act()
            return self.skill_biases[skill_id]
        
        def set_global_bias(self, value: float) -> None:
            self._act()
            self.global_bias = value
        
        def set_user_latent_vector(self, user_id: int, value: npt.NDArray[np.float64]) -> None:
            assert user_id == chosen_user_id
            self._act()
            self.user_latent_vector = value
        
        def set_user_bias(self, user_id: int, value: float) -> None:
            assert user_id == chosen_user_id
            self._act()
            self.user_bias = value
        
        def set_skill_latent_vector(self, skill_id: int, value: npt.NDArray[np.float64]) -> None:
            self._act()
            self.skill_latent_vectors[skill_id] = value
        
        def set_skill_bias(self, skill_id: int, value: float) -> None:
            self._act()
            self.skill_biases[skill_id] = value

    class MockUserRepository(UserRepository):
        def __init__(self):
            self.action_limit = 1

        def _act(self):
            assert self.action_limit > 0
            self.action_limit -= 1

        def get_all_skills(self, id: int) -> list[tuple[int, float]]:
            assert id == chosen_user_id
            self._act()
            return [(skill_id, score) for skill_id, score in actual_scores.items()]

    class MockConfigRepository(ConfigRepository):
        def __init__(self):
            self.action_limit = 2

        def _act(self):
            assert self.action_limit > 0
            self.action_limit -= 1

        def get_fang_learning_rate(self) -> float:
            self._act()
            return learning_rate
        
        def get_fang_regularization_factor(self) -> float:
            self._act()
            return regularization_factor
        
    param_repo = MockFangCollaborativeParameterRepository()
    user_repo = MockUserRepository()
    config_repo = MockConfigRepository()

    optimizer = FangCollaborativeOptimizer(param_repo, user_repo, config_repo)
    optimizer.optimize(chosen_user_id)
    actual_total_error = optimizer.get_last_error()

    assert abs(param_repo.global_bias - expected_final_global_bias) <= max_error
    assert abs(param_repo.user_bias - expected_final_user_bias) <= max_error
    assert np.all(np.abs(param_repo.user_latent_vector - expected_final_user_latent_vector) <= max_error)

    for skill_id in initial_skill_biases.keys():
        assert abs(param_repo.skill_biases[skill_id] - expected_final_skill_biases[skill_id]) <= max_error
        assert np.all(np.abs(param_repo.skill_latent_vectors[skill_id] - expected_final_skill_latent_vectors[skill_id]) <= max_error)

    assert abs(actual_total_error - expected_total_error) <= 1e-8
