import numpy as np

from src.recommendation.repositories import FangCollaborativeParameterRepository

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