from __future__ import annotations

from typing import Any

from neo4j import Driver

from app.repositories import UserRepository, VacancyRepository


class Neo4jUserRepository(UserRepository):
    def __init__(self, driver: Driver, database: str | None = None):
        super().__init__(driver, database)

    def get_connections(self, id: Any) -> list[tuple[Any, float]]:
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

    def get_suggested_connections(self, id: Any) -> list[tuple[Any, float, bool]]:
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

    def get_vacancies_from_target_current_companies(self, id: Any, target_user_id: Any) -> list[tuple[Any, float]]:
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

    def get_connections_for_specific_company(self, id: Any, company_id: Any) -> list[tuple[Any, float]]:
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

    def get_suggested_connections_for_specific_company(self, id: Any, company_id: Any) -> list[tuple[Any, float]]:
        """
        Return a list of tuples <user_id, score> in two hops. Scores are cached in database.
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

    def get_all_skills(self, id: Any) -> list[tuple[Any, float]]:
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
            id: Any,
            skill_id: Any,
            embed_id: int,
            min_sim_score: float
    ) -> list[tuple[Any, float, float]]:
        """
        Return a list of tuples <skill_id, level, similarity_score> of skills similar to a given skill.
        """
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

    def set_vacancy_score(self, id: Any, vacancy_id: Any, score: float) -> None:
        """
        Set or update the score for a vacancy suggestion.
        """
        records, _, _ = self.driver.execute_query(
            """
                MATCH (:Vacancy {id: $vacancy_id})
                    -[s:SUGGESTED_TO]->(:User {id: $user_id})
                RETURN s;
            """,
            database_=self.database,
            vacancy_id=vacancy_id,
            user_id=id,
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


class Neo4jVacancyRepository(VacancyRepository):
    def __init__(self, driver: Driver, database: str | None = None):
        super().__init__(driver, database)

    def get_required_skills(self, id: Any) -> list[Any]:
        """
        Return a list of skill IDs required for the vacancy.
        """
        records, _, _ = self.driver.execute_query(
            """
                MATCH (:Vacancy {id: $id})-[:REQUIRES]->(s:Skill)
                RETURN s.id AS id;
            """,
            database_=self.database,
            id=id,
        )
        return [r["id"] for r in records]

    def get_info(self, id: Any) -> tuple[Any, str, str]:
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
