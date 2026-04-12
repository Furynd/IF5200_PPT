import numpy as np
import numpy.typing as npt
from src.recommendation.repositories import FangCollaborativeParameterRepository
from src.recommendation.scorers import FangCollaborativeScorer

def test_fang_collaborative_scorer():
    chosen_user_id = np.random.randint(999_999_999)
    user_latent_vector = np.random.randn(10)
    user_bias = np.random.randn()

    chosen_skill_id = np.random.randint(999_999_999)
    skill_latent_vector = np.random.randn(10)
    skill_bias = np.random.randn()

    global_bias = np.random.randn()

    class MockFangCollaborativeParameterRepository(FangCollaborativeParameterRepository):
        def __init__(self):
            self.fetch_limit = 5

        def _fetch(self):
            assert self.fetch_limit > 0
            self.fetch_limit -= 1

        def get_global_bias(self) -> float:
            self._fetch()
            return global_bias
        
        def get_user_latent_vector(self, user_id: int) -> npt.NDArray[np.float64]:
            assert user_id == chosen_user_id
            self._fetch()
            return user_latent_vector
        
        def get_user_bias(self, user_id: int) -> float:
            assert user_id == chosen_user_id
            self._fetch()
            return user_bias
        
        def get_skill_latent_vector(self, skill_id: int) -> npt.NDArray[np.float64]:
            assert skill_id == chosen_skill_id
            self._fetch()
            return skill_latent_vector
        
        def get_skill_bias(self, skill_id: int) -> float:
            assert skill_id == chosen_skill_id
            self._fetch()
            return skill_bias
    
    expected_score = (
        global_bias
        + user_bias
        + skill_bias
        + np.dot(user_latent_vector,
                 skill_latent_vector)
    )
    expected_score = float(expected_score)
    max_error = 1e-8

    repo = MockFangCollaborativeParameterRepository()
    scorer = FangCollaborativeScorer(repo)

    actual_score = scorer.get_score(chosen_user_id, chosen_skill_id)
    assert abs(actual_score - expected_score) <= max_error
