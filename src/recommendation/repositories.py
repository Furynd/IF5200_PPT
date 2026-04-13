import numpy as np
import numpy.typing as npt

class FangCollaborativeParameterRepository:
    def get_global_bias(self) -> float:
        raise NotImplementedError
    
    def get_user_latent_vector(self, user_id: int) -> npt.NDArray[np.float64]:
        raise NotImplementedError
    
    def get_user_bias(self, user_id: int) -> float:
        raise NotImplementedError
    
    def get_skill_latent_vector(self, skill_id: int) -> npt.NDArray[np.float64]:
        raise NotImplementedError
    
    def get_skill_bias(self, skill_id: int) -> float:
        raise NotImplementedError

class FangContentBasedRepository:
    def get_similar_skills(self, user_id: int, skill_id: int) -> list[tuple[int, float, float]]:
        """
        Return triplet of skill ID, level, and similarity.
        """
        raise NotImplementedError

class VacancyRepository:
    def get_required_skills(self, id: int) -> list[int]:
        raise NotImplementedError
    
    def get_info(self, id: int) -> tuple[int, str, str]:
        """
        Returns a tuple <company_id, description, source_url>.
        """
        raise NotImplementedError

class UserRepository:
    def get_connections(self, id: int) -> list[tuple[int, float]]:
        """
        Return a tuple <user_id, score> in one hop. Scores are cached in database.
        """
        raise NotImplementedError
    
    def get_suggested_connections(self, id: int) -> list[tuple[int, float]]:
        """
        Return a tuple <user_id, score> in two hops. Scores are cached in database.
        """
        raise NotImplementedError
    
    def get_vacancies_from_current_companies(self, id: int) -> list[tuple[int, float]]:
        """
        Return a tuple <vacancy_id, score> that connects to user's companies. Scores are cached in database.
        """
        raise NotImplementedError
