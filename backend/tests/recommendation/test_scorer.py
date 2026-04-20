import numpy as np
import numpy.typing as npt

from backend.app.repositories import FangCollaborativeParameterRepository, FangContentBasedRepository, VacancyRepository
from backend.app.recommendation.scorers import FangCollaborativeScorer, FangContentBasedScorer, FangScorer, FangVacancyScorer

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

def test_fang_content_based_scorer_normal():
    chosen_user_id = np.random.randint(999_999_999)
    chosen_skill_id = np.random.randint(999_999_999)
    similar_skills: list[tuple[int, float, float]] = []
    used_skill_ids = set()
    for _ in range(1 + int(np.random.exponential(3))):
        stop = False
        new_skill_id = -1
        while not stop:
            new_skill_id = np.random.randint(999_999_999)
            stop = (
                new_skill_id != chosen_skill_id
                and new_skill_id not in used_skill_ids
            )
        
        similar_skills.append((new_skill_id, 1 + np.random.random() * 4, np.random.random()))

    class MockFangContentBasedRepository(FangContentBasedRepository):
        def __init__(self):
            self.fetch_limit = 1

        def _fetch(self):
            assert self.fetch_limit > 0
            self.fetch_limit -= 1

        def get_similar_skills(self, user_id: int, skill_id: int) -> list[tuple[int, float, float]]:
            assert user_id == chosen_user_id
            assert skill_id == chosen_skill_id
            self._fetch()
            return similar_skills
        
    expected_score_numerator = 0.0
    expected_score_denumerator = 0.0
    for _, level, sim in similar_skills:
        expected_score_numerator += level * sim
        expected_score_denumerator += sim
    
    expected_score = expected_score_numerator / expected_score_denumerator
    max_error = 1e-8

    repo = MockFangContentBasedRepository()
    scorer = FangContentBasedScorer(repo)

    actual_score = scorer.get_score(chosen_user_id, chosen_skill_id)
    assert abs(actual_score - expected_score) <= max_error

def test_fang_content_based_scorer_empty_skills():
    chosen_user_id = np.random.randint(999_999_999)
    chosen_skill_id = np.random.randint(999_999_999)
    similar_skills: list[tuple[int, float, float]] = []

    class MockFangContentBasedRepository(FangContentBasedRepository):
        def __init__(self):
            self.fetch_limit = 1

        def _fetch(self):
            assert self.fetch_limit > 0
            self.fetch_limit -= 1

        def get_similar_skills(self, user_id: int, skill_id: int) -> list[tuple[int, float, float]]:
            assert user_id == chosen_user_id
            assert skill_id == chosen_skill_id
            self._fetch()
            return similar_skills
    
    expected_score = 0.0
    max_error = 1e-8

    repo = MockFangContentBasedRepository()
    scorer = FangContentBasedScorer(repo)

    actual_score = scorer.get_score(chosen_user_id, chosen_skill_id)
    assert abs(actual_score - expected_score) <= max_error

def test_fang_scorer():
    chosen_user_id = np.random.randint(999_999_999)
    chosen_skill_id = np.random.randint(999_999_999)
    collaborative_score = np.random.exponential()
    content_based_score = np.random.exponential()

    class MockFangCollaborativeScorer(FangCollaborativeScorer):
        def __init__(self):
            self.fetch_limit = 1

        def _fetch(self):
            assert self.fetch_limit > 0
            self.fetch_limit -= 1

        def get_score(self, user_id: int, skill_id: int) -> float:
            assert user_id == chosen_user_id
            assert skill_id == chosen_skill_id
            self._fetch()
            return collaborative_score
        
    class MockFangContentBasedScorer(FangContentBasedScorer):
        def __init__(self):
            self.fetch_limit = 1

        def _fetch(self):
            assert self.fetch_limit > 0
            self.fetch_limit -= 1

        def get_score(self, user_id: int, skill_id: int) -> float:
            assert user_id == chosen_user_id
            assert skill_id == chosen_skill_id
            self._fetch()
            return content_based_score
        
    expected_score = collaborative_score + content_based_score
    max_error = 1e-8
    
    collab_scorer = MockFangCollaborativeScorer()
    content_based_scorer = MockFangContentBasedScorer()
    scorer = FangScorer(collaborative_scorer=collab_scorer,
                        content_based_scorer=content_based_scorer)
    
    actual_score = scorer.get_score(chosen_user_id, chosen_skill_id)
    assert abs(actual_score - expected_score) <= max_error

def test_fang_vacancy_scorer():
    chosen_user_id = np.random.randint(999_999_999)
    chosen_vacancy_id = np.random.randint(999_999_999)

    skill_scores: dict[int, float] = {}
    for _ in range(1 + int(np.random.exponential(3))):
        stop = False
        new_skill_id = -1
        while not stop:
            new_skill_id = np.random.randint(999_999_999)
            stop = new_skill_id not in skill_scores
        
        skill_scores[new_skill_id] = np.random.exponential()

    expected_score = sum(skill_scores.values()) / len(skill_scores)
    max_error = 1e-8

    class MockFangScorer(FangScorer):
        def __init__(self):
            self.fetch_limit = len(skill_scores)

        def _fetch(self):
            assert self.fetch_limit > 0
            self.fetch_limit -= 1

        def get_score(self, user_id: int, skill_id: int) -> float:
            assert user_id == chosen_user_id
            self._fetch()
            return skill_scores[skill_id]
    
    class MockVacancyRepository(VacancyRepository):
        def __init__(self):
            self.fetch_limit = 1

        def _fetch(self):
            assert self.fetch_limit > 0
            self.fetch_limit -= 1

        def get_required_skills(self, id: int) -> list[int]:
            assert id == chosen_vacancy_id
            self._fetch()
            return list(skill_scores.keys())
    
    child_scorer = MockFangScorer()
    repo = MockVacancyRepository()
    scorer = FangVacancyScorer(child_scorer, repo)

    actual_score = scorer.get_score(chosen_user_id, chosen_vacancy_id)
    assert abs(actual_score - expected_score) <= max_error
