import numpy as np

from src.repositories import ConfigRepository, FangCollaborativeParameterRepository, UserRepository

class FangCollaborativeOptimizer:
    def __init__(
            self,
            parameter_repository: FangCollaborativeParameterRepository,
            user_repository: UserRepository,
            config_repository: ConfigRepository
    ):
        self.parameter_repository = parameter_repository
        self.user_repository = user_repository
        self.config_repository = config_repository
        self._last_error = None

    def optimize(self, user_id: int):
        global_bias = self.parameter_repository.get_global_bias()
        user_latent_vector = self.parameter_repository.get_user_latent_vector(user_id)
        user_bias = self.parameter_repository.get_user_bias(user_id)
        learning_rate = self.config_repository.get_fang_learning_rate()
        regularization_factor = self.config_repository.get_fang_regularization_factor()

        predicted_score_grad = 0.0
        skill_tuples = self.user_repository.get_all_skills(user_id)
        skill_latent_vectors = {}
        skill_biases = {}
        total_error = 0.0
        for skill_id, score in skill_tuples:
            skill_latent_vectors[skill_id] = self.parameter_repository.get_skill_latent_vector(skill_id)
            skill_biases[skill_id] = self.parameter_repository.get_skill_bias(skill_id)
            
            predicted_score = (
                global_bias
                + user_bias
                + skill_biases[skill_id]
                + np.dot(user_latent_vector,
                        skill_latent_vectors[skill_id])
            )

            predicted_score_grad += 2 * (predicted_score - score)
            total_error += (predicted_score - score) ** 2
        
        user_latent_vector_grad = 2 * regularization_factor * user_latent_vector
        for skill_id, _ in skill_tuples:
            new_skill_latent_vector = skill_latent_vectors[skill_id] - learning_rate * (
                predicted_score_grad * user_latent_vector
                + 2 * regularization_factor * skill_latent_vectors[skill_id]
            )
            new_skill_bias = skill_biases[skill_id] - learning_rate * (
                predicted_score_grad + 2 * regularization_factor * skill_biases[skill_id]
            )
            self.parameter_repository.set_skill_latent_vector(skill_id, new_skill_latent_vector)
            self.parameter_repository.set_skill_bias(skill_id, new_skill_bias)

            user_latent_vector_grad += predicted_score_grad * skill_latent_vectors[skill_id]

        new_global_bias = global_bias - learning_rate * (
            predicted_score_grad + 2 * regularization_factor * global_bias
        )
        new_user_bias = user_bias - learning_rate * (
            predicted_score_grad + 2 * regularization_factor * user_bias
        )
        new_user_latent_vector = user_latent_vector - learning_rate * user_latent_vector_grad

        self.parameter_repository.set_global_bias(new_global_bias)
        self.parameter_repository.set_user_bias(user_id, new_user_bias)
        self.parameter_repository.set_user_latent_vector(user_id, new_user_latent_vector)

        self._last_error = total_error

    def get_last_error(self) -> float:
        assert self._last_error is not None
        return self._last_error
