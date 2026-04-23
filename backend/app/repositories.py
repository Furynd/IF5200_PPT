import neo4j
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
    
    def set_global_bias(self, value: float) -> None:
        raise NotImplementedError
    
    def set_user_latent_vector(self, user_id: int, value: npt.NDArray[np.float64]) -> None:
        raise NotImplementedError
    
    def set_user_bias(self, user_id: int, value: float) -> None:
        raise NotImplementedError
    
    def set_skill_latent_vector(self, skill_id: int, value: npt.NDArray[np.float64]) -> None:
        raise NotImplementedError
    
    def set_skill_bias(self, skill_id: int, value: float) -> None:
        raise NotImplementedError

class FangContentBasedRepository:
    """
    DEPRECATED: Need to change (please check design)
    """

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
        Return a list of tuples <user_id, score> in one hop. Scores are cached in database.
        """
        raise NotImplementedError
    
    def get_suggested_connections(self, id: int) -> list[tuple[int, float]]:
        """
        Return a list of tuples <user_id, score> in two hops. Scores are cached in database.
        """
        raise NotImplementedError
    
    def get_vacancies_from_current_companies(self, id: int) -> list[tuple[int, float]]:
        """
        Return a list of tuples <vacancy_id, score> that connects to user's companies. Scores are cached in database.
        """
        raise NotImplementedError
    
    def get_all_skills(self, id: int) -> list[tuple[int, float]]:
        """
        Return a list of tuples <skill_id, level>.
        """
        raise NotImplementedError
    
    def get_all_user_ids(self) -> list[int]:
        """
        Return a list of user IDs.
        """
        raise NotImplementedError

class ConfigRepository:
    def __init__(self, driver: neo4j.Driver, config_id: int, database: str | None = None):
        self.driver = driver
        self.config_id = config_id
        self.database = database

    def get_fang_learning_rate(self) -> float:
        records, _, _ = self.driver.execute_query(
            "MATCH (c:FangConfig {id: $id}) RETURN c.learning_rate AS value;",
            id=self.config_id,
            database_=self.database
        )
        return float(records[0]["value"])
    
    def get_fang_regularization_factor(self) -> float:
        records, _, _ = self.driver.execute_query(
            "MATCH (c:FangConfig {id: $id}) RETURN c.regularization_factor AS value;",
            id=self.config_id,
            database_=self.database
        )
        return float(records[0]["value"])
    
    def get_fang_max_train_error(self) -> float:
        records, _, _ = self.driver.execute_query(
            "MATCH (c:FangConfig {id: $id}) RETURN c.max_train_error AS value;",
            id=self.config_id,
            database_=self.database
        )
        return float(records[0]["value"])
    
    def get_fang_max_train_steps(self) -> int:
        records, _, _ = self.driver.execute_query(
            "MATCH (c:FangConfig {id: $id}) RETURN c.max_train_steps AS value;",
            id=self.config_id,
            database_=self.database
        )
        return int(records[0]["value"])
    
    def get_fang_minimum_similarity(self) -> float:
        records, _, _ = self.driver.execute_query(
            "MATCH (c:FangConfig {id: $id}) RETURN c.minimum_similarity AS value;",
            id=self.config_id,
            database_=self.database
        )
        return float(records[0]["value"])
