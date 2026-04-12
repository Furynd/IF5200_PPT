import numpy as np

from src.recommendation.repositories import FangCollaborativeParameterRepository, FangContentBasedRepository

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
