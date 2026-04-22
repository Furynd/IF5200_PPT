import numpy as np

from backend.app.repositories import FangCollaborativeParameterRepository, FangContentBasedRepository, VacancyRepository

class FangCollaborativeScorer:
    def __init__(self, repository: FangCollaborativeParameterRepository):
        self.repo = repository

    def get_score(self, user_id: int, skill_id: int) -> float:
        global_bias = self.repo.get_global_bias()
        user_latent_vector = self.repo.get_user_latent_vector(user_id)
        user_bias = self.repo.get_user_bias(user_id)
        skill_latent_vector = self.repo.get_skill_latent_vector(skill_id)
        skill_bias = self.repo.get_skill_bias(skill_id)

        return (
            global_bias
            + user_bias
            + skill_bias
            + np.dot(user_latent_vector,
                    skill_latent_vector)
        )
    
class FangContentBasedScorer:
    def __init__(self, repository: FangContentBasedRepository):
        self.repo = repository

    def get_score(self, user_id: int, skill_id: int) -> float:
        similar_skills = self.repo.get_similar_skills(user_id, skill_id)
        if len(similar_skills) == 0:
            return 0.0

        score_numerator = 0.0
        score_denumerator = 0.0
        for _, level, sim in similar_skills:
            score_numerator += level * sim
            score_denumerator += sim

        return score_numerator / score_denumerator

class FangScorer:
    def __init__(self, collaborative_scorer: FangCollaborativeScorer,
                 content_based_scorer: FangContentBasedScorer):
        self.collaborative_scorer = collaborative_scorer
        self.content_based_scorer = content_based_scorer
    
    def get_score(self, user_id: int, skill_id: int) -> float:
        collaborative_score = self.collaborative_scorer.get_score(user_id, skill_id)
        content_based_score = self.content_based_scorer.get_score(user_id, skill_id)
        return collaborative_score + content_based_score

class FangVacancyScorer:
    def __init__(self, child_scorer: FangScorer, repository: VacancyRepository):
        self.child_scorer = child_scorer
        self.repository = repository
    
    def get_score(self, user_id: int, vacancy_id: int) -> float:
        total_score = 0.0
        skill_count = 0

        for skill_id in self.repository.get_required_skills(vacancy_id):
            score = self.child_scorer.get_score(user_id, skill_id)
            total_score += score
            skill_count += 1
        
        return total_score / skill_count
