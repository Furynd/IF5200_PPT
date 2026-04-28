from __future__ import annotations

from typing import Any, Callable

import neo4j
import numpy as np
import numpy.typing as npt

class FangCollaborativeParameterRepository:
    def __init__(self, driver: neo4j.Driver, config_id, database: str | None = None):
        self.driver = driver
        self.config_id = config_id
        self.database = database

    def _get_config_node(self):
        records, _, _ = self.driver.execute_query(
            """
                MATCH (c:FangConfig {id: $id})
                RETURN c;
            """,
            database_=self.database,
            id=self.config_id,
        )
        if len(records) == 0:
            return None
        else:
            return records[0]["c"]
        
    def _get_user_edge(self, user_id):
        records, _, _ = self.driver.execute_query(
            """
                MATCH (:FangConfig {id: $id})-[e:ASSIGNS_PARAMETERS]->(:User {id: $user_id})
                RETURN e;
            """,
            database_=self.database,
            id=self.config_id,
            user_id=user_id
        )
        if len(records) == 0:
            return None
        else:
            return records[0]["e"]
        
    def _get_skill_edge(self, skill_id):
        records, _, _ = self.driver.execute_query(
            """
                MATCH (:FangConfig {id: $id})-[e:ASSIGNS_PARAMETERS]->(:Skill {id: $skill_id})
                RETURN e;
            """,
            database_=self.database,
            id=self.config_id,
            skill_id=skill_id
        )
        if len(records) == 0:
            return None
        else:
            return records[0]["e"]
        
    def _create_new_config_node_and_return_global_bias(self, global_bias: float | None = None):
        if global_bias is None:
            global_bias = np.random.random()
        
        self.driver.execute_query(
            """
                CREATE (c:FangConfig {
                    id: $id,
                    global_bias: $value,
                    embeddings_id: 120,
                    latent_vector_dimension: 16,
                    learning_rate: 0.01,
                    max_train_error: 0.01,
                    max_train_steps: 100,
                    minimum_similarity: 0.87,
                    regularization_factor: 0.01
                })
            """,
            database_=self.database,
            id=self.config_id,
            value=global_bias,
        )
        return global_bias

    def get_global_bias(self) -> float:
        record = self._get_config_node()

        if record is None:
            new_value = self._create_new_config_node_and_return_global_bias()
            return new_value
        
        old_value = record["global_bias"]
        if old_value is not None:
            return float(old_value)
        
        new_value = np.random.randn()
        self.driver.execute_query(
            """
                MATCH (c:FangConfig {
                    id: $id
                })
                SET c.global_bias = $global_bias;
            """,
            database_=self.database,
            id=self.config_id,
            global_bias=new_value,
        )
        return new_value
    
    def _create_new_user_parameters(
            self,
            user_id,
            *,
            latent_vector: npt.NDArray[np.float64] | None = None,
            bias: float | None = None
    ) -> tuple[npt.NDArray[np.float64], float]:
        record = self._get_config_node()
        assert record is not None
        dimension = int(record["latent_vector_dimension"])

        if latent_vector is None:
            latent_vector = np.random.randn(dimension)
        
        if bias is None:
            bias = np.random.randn()
        
        self.driver.execute_query(
            """
                MATCH (c:FangConfig {id: $id})
                MATCH (u:User {id: $user_id})
                CREATE (c)-[:ASSIGNS_PARAMETERS {latent_vector: vector($latent_vector, $dimension, FLOAT), bias: $bias}]->(u);
            """,
            database_=self.database,
            id=self.config_id,
            user_id=user_id,
            latent_vector=latent_vector.tolist(),
            dimension=dimension,
            bias=bias,
        )
        return (latent_vector, bias)
    
    def get_user_latent_vector(self, user_id) -> npt.NDArray[np.float64]:
        record = self._get_config_node()

        if record is None:
            self._create_new_config_node_and_return_global_bias()
            new_value, _ = self._create_new_user_parameters(user_id)
            return new_value
        
        record = self._get_user_edge(user_id)
        if record is None:
            new_value, _ = self._create_new_user_parameters(user_id)
            return new_value
        
        return np.array(record["latent_vector"].to_native())
    
    def get_user_bias(self, user_id) -> float:
        record = self._get_config_node()

        if record is None:
            self._create_new_config_node_and_return_global_bias()
            _, new_value = self._create_new_user_parameters(user_id)
            return new_value
        
        record = self._get_user_edge(user_id)
        if record is None:
            _, new_value = self._create_new_user_parameters(user_id)
            return new_value
        
        return float(record["bias"])
    
    def _create_new_skill_parameters(
            self,
            skill_id,
            *,
            latent_vector: npt.NDArray[np.float64] | None = None,
            bias: float | None = None
    ) -> tuple[npt.NDArray[np.float64], float]:
        record = self._get_config_node()
        assert record is not None
        dimension = int(record["latent_vector_dimension"])

        if latent_vector is None:
            latent_vector = np.random.randn(dimension)
        
        if bias is None:
            bias = np.random.randn()
        
        self.driver.execute_query(
            """
                MATCH (c:FangConfig {id: $id})
                MATCH (s:Skill {id: $skill_id})
                CREATE (c)-[:ASSIGNS_PARAMETERS {latent_vector: vector($latent_vector, $dimension, FLOAT), bias: $bias}]->(s);
            """,
            database_=self.database,
            id=self.config_id,
            skill_id=skill_id,
            latent_vector=latent_vector.tolist(),
            dimension=dimension,
            bias=bias,
        )
        return (latent_vector, bias)

    def get_skill_latent_vector(self, skill_id) -> npt.NDArray[np.float64]:
        record = self._get_config_node()

        if record is None:
            self._create_new_config_node_and_return_global_bias()
            new_value, _ = self._create_new_skill_parameters(skill_id)
            return new_value
        
        record = self._get_skill_edge(skill_id)
        if record is None:
            new_value, _ = self._create_new_skill_parameters(skill_id)
            return new_value
        
        return np.array(record["latent_vector"].to_native())
    
    def get_skill_bias(self, skill_id) -> float:
        record = self._get_config_node()

        if record is None:
            self._create_new_config_node_and_return_global_bias()
            _, new_value = self._create_new_skill_parameters(skill_id)
            return new_value
        
        record = self._get_skill_edge(skill_id)
        if record is None:
            _, new_value = self._create_new_skill_parameters(skill_id)
            return new_value
        
        return float(record["bias"])
    
    def set_global_bias(self, value: float) -> None:
        record = self._get_config_node()

        if record is None:
            self._create_new_config_node_and_return_global_bias(value)
            return
        
        self.driver.execute_query(
            """
                MATCH (c:FangConfig {id: $id})
                SET c.global_bias = $value;
            """,
            database_=self.database,
            id=self.config_id,
            value=value
        )
    
    def set_user_latent_vector(self, user_id, value: npt.NDArray[np.float64]) -> None:
        record = self._get_config_node()

        if record is None:
            self._create_new_config_node_and_return_global_bias()
            record = self._get_config_node()
            assert record is not None
        
        dimension = int(record["latent_vector_dimension"])
        assert len(value) == dimension

        record = self._get_user_edge(user_id)
        if record is None:
            self._create_new_user_parameters(user_id, latent_vector=value)
            return
        
        self.driver.execute_query(
            """
                MATCH (c:FangConfig {id: $id})-[e:ASSIGNS_PARAMETERS]->(u:User {id: $user_id})
                SET e.latent_vector = vector($latent_vector, $dimension, FLOAT);
            """,
            database_=self.database,
            id=self.config_id,
            user_id=user_id,
            latent_vector=value,
            dimension=dimension
        )
    
    def set_user_bias(self, user_id, value: float) -> None:
        record = self._get_config_node()

        if record is None:
            self._create_new_config_node_and_return_global_bias()
            record = self._get_config_node()
            assert record is not None

        record = self._get_user_edge(user_id)
        if record is None:
            self._create_new_user_parameters(user_id, bias=value)
            return
        
        self.driver.execute_query(
            """
                MATCH (c:FangConfig {id: $id})-[e:ASSIGNS_PARAMETERS]->(u:User {id: $user_id})
                SET e.bias = $bias;
            """,
            database_=self.database,
            id=self.config_id,
            user_id=user_id,
            bias=value
        )
    
    def set_skill_latent_vector(self, skill_id, value: npt.NDArray[np.float64]) -> None:
        record = self._get_config_node()

        if record is None:
            self._create_new_config_node_and_return_global_bias()
            record = self._get_config_node()
            assert record is not None
        
        dimension = int(record["latent_vector_dimension"])
        assert len(value) == dimension

        record = self._get_skill_edge(skill_id)
        if record is None:
            self._create_new_skill_parameters(skill_id, latent_vector=value)
            return
        
        self.driver.execute_query(
            """
                MATCH (c:FangConfig {id: $id})-[e:ASSIGNS_PARAMETERS]->(s:Skill {id: $skill_id})
                SET e.latent_vector = vector($latent_vector, $dimension, FLOAT);
            """,
            database_=self.database,
            id=self.config_id,
            skill_id=skill_id,
            latent_vector=value,
            dimension=dimension
        )
    
    def set_skill_bias(self, skill_id, value: float) -> None:
        record = self._get_config_node()

        if record is None:
            self._create_new_config_node_and_return_global_bias()
            record = self._get_config_node()
            assert record is not None

        record = self._get_skill_edge(skill_id)
        if record is None:
            self._create_new_skill_parameters(skill_id, bias=value)
            return
        
        self.driver.execute_query(
            """
                MATCH (c:FangConfig {id: $id})-[e:ASSIGNS_PARAMETERS]->(s:Skill {id: $skill_id})
                SET e.bias = $bias;
            """,
            database_=self.database,
            id=self.config_id,
            skill_id=skill_id,
            bias=value,
        )

class VacancyRepository:
    def __init__(self, driver: neo4j.Driver, database: str | None = None):
        self.driver = driver
        self.database = database

    def get_required_skills(self, id) -> list[Any]:
        records, _, _ = self.driver.execute_query(
            """
                MATCH (:Vacancy {id: $id})-[:REQUIRES]->(s:Skill)
                RETURN s.id AS id;
            """,
            database_=self.database,
            id=id,
        )
        return [r["id"] for r in records]
    
    def get_info(self, id) -> tuple[Any, str, str]:
        """
        Returns a tuple <company_id, description, source_url>.
        """
        records, _, _ = self.driver.execute_query(
            """
                MATCH (v:Vacancy {id: $id})
                RETURN v.description AS description, v.source_url AS source_url;
            """,
            database_=self.database,
            id=id
        )
        assert len(records) > 0
        record = records[0]
        description = str(record["description"])
        source_url = str(record["source_url"])

        records, _, _ = self.driver.execute_query(
            """
                MATCH (c:Company)-[:OPENS]->(v:Vacancy {id: $id})
                RETURN c.id AS id;
            """,
            database_=self.database,
            id=id
        )
        assert len(records) > 0
        company_id = records[0]["id"]

        return (company_id, description, source_url)
    
    def get_all_vacancy_ids(self) -> list[Any]:
        """
        Return a list of all vacancy IDs.
        """
        records, _, _ = self.driver.execute_query(
            """
                MATCH (v:Vacancy)
                RETURN DISTINCT v.id AS id;
            """,
            database_=self.database,
        )
        return [r["id"] for r in records]

class UserRepository:
    def __init__(self, driver: neo4j.Driver, database: str | None = None):
        self.driver = driver
        self.database = database

    def get_connections(self, id) -> list[tuple[Any, float]]:
        """
        Return a list of tuples <user_id, score> in one hop. Scores are cached in database.
        """
        records, _, _ = self.driver.execute_query(
            """
                MATCH (n:User {id: $id})
                    -[:CONNECTED_TO]-(n2:User)
                    -[:WORKS_AT]->(:Company)
                    -[:OPENS]->(v:Vacancy)
                    -[e:SUGGESTED_TO]->(n)
                RETURN n2.id AS id, MAX(e.score) AS score;
            """,
            database_=self.database,
            id=id,
        )
        return [
            (r["id"], float(r["score"]))
            for r in records
        ]
    
    def get_suggested_connections(self, id) -> list[tuple[Any, float, bool]]:
        """
        Return a list of tuples <user_id, score, is_friend_of_friends>. Scores are cached in database.
        """
        records, _, _ = self.driver.execute_query(
            """
                MATCH (n:User {id: $id})
                    -[:CONNECTED_TO]-(:User)
                    -[:CONNECTED_TO]-(n2:User)
                    -[:WORKS_AT]->(:Company)
                    -[:OPENS]->(v:Vacancy)
                    -[e:SUGGESTED_TO]->(n)
                WHERE n <> n2
                AND NOT (n)-[:CONNECTED_TO]-(n2)
                RETURN n2.id AS id, MAX(e.score) AS score;
            """,
            database_=self.database,
            id=id,
        )
        first_results = [
            (r["id"], float(r["score"]), True)
            for r in records
        ]

        records, _, _ = self.driver.execute_query(
            """
                MATCH (n2:User)
                    -[:WORKS_AT]->(:Company)
                    -[:OPENS]->(v:Vacancy)
                    -[e:SUGGESTED_TO]->(n)
                WHERE n <> n2
                AND NOT (n:User {id: $id})-[:CONNECTED_TO]-(n2)
                AND NOT (n:User {id: $id})-[:CONNECTED_TO]-()-[:CONNECTED_TO]-(n2)
                RETURN n2.id AS id, MAX(e.score) AS score;
            """,
            database_=self.database,
            id=id,
        )
        second_results = [
            (r["id"], float(r["score"]), False)
            for r in records
        ]

        return first_results + second_results
    
    def get_vacancies_from_target_current_companies(self, id, target_user_id) -> list[tuple[Any, float]]:
        """
        Return a list of tuples <vacancy_id, score> that connects to target user's companies.
        Scores are cached in database.

        This is used for recommendation.
        """
        records, _, _ = self.driver.execute_query(
            """
                MATCH (n2:User {id: $target_id})
                    -[:WORKS_AT]->(:Company)
                    -[:OPENS]->(v:Vacancy)
                    -[e:SUGGESTED_TO]->(n:User {id: $id})
                WHERE n <> n2
                AND NOT (n)-[:CONNECTED_TO]-(n2)
                RETURN DISTINCT v.id AS id, e.score AS score;
            """,
            database_=self.database,
            id=id,
            target_id=target_user_id
        )
        return [
            (r["id"], float(r["score"]))
            for r in records
        ]
    
    def get_connections_for_specific_company(self, id, company_id) -> list[tuple[Any, float]]:
        """
        Return a list of tuples <user_id, score> in one hop. Scores are cached in database.
        """
        records, _, _ = self.driver.execute_query(
            """
                MATCH (n:User {id: $id})
                    -[:CONNECTED_TO]-(n2:User)
                    -[:WORKS_AT]->(:Company {id: $company_id})
                    -[:OPENS]->(v:Vacancy)
                    -[e:SUGGESTED_TO]->(n)
                RETURN n2.id AS id, MAX(e.score) AS score;
            """,
            database_=self.database,
            id=id,
            company_id=company_id
        )
        return [
            (r["id"], float(r["score"]))
            for r in records
        ]
    
    def get_suggested_connections_for_specific_company(self, id, company_id) -> list[tuple[Any, float]]:
        """
        Return a list of tuples <user_id, score> in two hops. Scores are cached in database.
        """
        """
        Return a list of tuples <user_id, score> in one hop. Scores are cached in database.
        """
        records, _, _ = self.driver.execute_query(
            """
                MATCH (n:User {id: $id})
                    -[:CONNECTED_TO]-(:User)
                    -[:CONNECTED_TO]-(n2:User)
                    -[:WORKS_AT]->(:Company {id: $company_id})
                    -[:OPENS]->(v:Vacancy)
                    -[e:SUGGESTED_TO]->(n)
                WHERE n <> n2
                AND NOT (n)-[:CONNECTED_TO]-(n2)
                RETURN n2.id AS id, MAX(e.score) AS score;
            """,
            database_=self.database,
            id=id,
            company_id=company_id,
        )
        return [
            (r["id"], float(r["score"]))
            for r in records
        ]
    
    def get_all_skills(self, id) -> list[tuple[Any, float]]:
        """
        Return a list of tuples <skill_id, level>.
        """
        records, _, _ = self.driver.execute_query(
            """
                MATCH (:User {id: $id})-[hs:HAS_SKILL]->(s:Skill)
                RETURN s.id AS id, hs.level AS level;
            """,
            database_=self.database,
            id=id
        )
        return [(r["id"], float(r["level"])) for r in records]
    
    def get_all_user_ids(self) -> list[Any]:
        """
        Return a list of user IDs.
        """
        records, _, _ = self.driver.execute_query(
            """
                MATCH (u:User)
                RETURN DISTINCT u.id AS id;
            """,
            database_=self.database,
        )
        return [r["id"] for r in records]
    
    def get_all_similar_skills(
            self,
            id,
            skill_id,
            embed_id: int,
            min_sim_score: float
    ) -> list[tuple[Any, float, float]]:
        records, _, _ = self.driver.execute_query(
            """
                MATCH (m:Embeddings {id: $embed_id})
                MATCH (u:User {id: $user_id})
                MATCH (m)-[e1:HAS_EMBEDDING]->(n:Skill {id: $skill_id})
                MATCH (u)-[e2:HAS_SKILL]->(n2:Skill)
                MATCH (m)-[e3:HAS_EMBEDDING]->(n2)
                WITH n2.id AS id, e2.level AS level, vector.similarity.cosine(e1.values, e3.values) as sim_score
                WHERE sim_score >= $min_sim_score
                RETURN DISTINCT id, level, sim_score;
            """,
            database_=self.database,
            user_id=id,
            skill_id=skill_id,
            embed_id=embed_id,
            min_sim_score=min_sim_score,
        )
        return [
            (r["id"], float(r["level"]), float(r["sim_score"]))
            for r in records
        ]
    
    def set_vacancy_score(self, id, vacancy_id, score: float):
        records, _, _ = self.driver.execute_query(
            """
                MATCH (:Vacancy {id: $vacancy_id})
                    -[s:SUGGESTED_TO]->(:User {id: $user_id})
                RETURN s;
            """,
            database_=self.database,
            vacancy_id=vacancy_id,
            user_id=id,
            score=score
        )

        if len(records) == 0:
            self.driver.execute_query(
                """
                    MATCH (v:Vacancy {id: $vacancy_id})
                    MATCH (u:User {id: $user_id})
                    CREATE (v)-[:SUGGESTED_TO {decided_at: datetime(), score: $score}]->(u);
                """,
                database_=self.database,
                vacancy_id=vacancy_id,
                user_id=id,
                score=score
            )
            return
        
        self.driver.execute_query(
            """
                MATCH (:Vacancy {id: $vacancy_id})
                    -[s:SUGGESTED_TO]->(:User {id: $user_id})
                SET s.decided_at = datetime(), s.score = $score;
            """,
            database_=self.database,
            vacancy_id=vacancy_id,
            user_id=id,
            score=score
        )

class ConfigRepository:
    def __init__(self, driver: neo4j.Driver, config_id, database: str | None = None):
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
    
    def get_embeddings_id(self) -> int:
        records, _, _ = self.driver.execute_query(
            "MATCH (c:FangConfig {id: $id}) RETURN c.embeddings_id AS value;",
            id=self.config_id,
            database_=self.database
        )
        return int(records[0]["value"])
    
    def get_latent_vector_dimension(self) -> int:
        records, _, _ = self.driver.execute_query(
            "MATCH (c:FangConfig {id: $id}) RETURN c.latent_vector_dimension AS value;",
            id=self.config_id,
            database_=self.database
        )
        return int(records[0]["value"])

class SkillRepository:
    def __init__(self, driver: neo4j.Driver, database: str | None = None):
        self.driver = driver
        self.database = database

    def create_new_embeddings_if_not_exists(self, embed_id: int):
        records, _, _ = self.driver.execute_query(
            """
                MATCH (c:Embeddings {id: $id})
                RETURN c;
            """,
            id=embed_id,
            database_=self.database
        )
        if len(records) > 0:
            return
        
        self.driver.execute_query(
            """
                CREATE (c:Embeddings {id: $embed_id});
            """,
            embed_id=embed_id,
            database_=self.database
        )

    def update_all_uninitialized_embeddings(self, embed_id: int, embed_fn: Callable[[str], list[float]]):
        records, _, _ = self.driver.execute_query(
            """
                MATCH (c:Embeddings {id: $id})
                MATCH (s:Skill)
                WHERE NOT (c)--(s)
                RETURN s.id AS id, s.name AS name;
            """,
            id=embed_id,
            database_=self.database
        )
        for r in records:
            r_id = r["id"]  # can be str or int
            r_name = str(r["name"])
            r_embed = embed_fn(r_name)

            self.driver.execute_query(
                """
                    MATCH (c:Embeddings {id: $embed_id})
                    MATCH (s:Skill {id: $skill_id})
                    CREATE (c)-[:HAS_EMBEDDING {values: vector($values, $length, FLOAT)}]->(s);
                """,
                embed_id=embed_id,
                skill_id=r_id,
                values=r_embed,
                length=len(r_embed),
                database_=self.database
            )
            print(f"Embedding for {r_name} (id: {r_id}) has been initialized!")

        return len(records)
