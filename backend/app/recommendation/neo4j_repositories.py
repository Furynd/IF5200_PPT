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
                    -[r:CONNECTED_TO]-(n2:User)
                OPTIONAL MATCH (n2)-[:WORKS_AT]->(c:Company)
                RETURN n2.id AS id, r.score AS score, n2.full_name AS full_name, n2.job_title AS job_title, c.name AS company_name
                ORDER BY score DESC;
            """,
            database_=self.database,
            id=id,
        )
        return [
            ({
                "user_id": r["id"],
                "score": float(r["score"]) if r["score"] is not None else 0.0,
                "full_name": r.get("full_name"),
                "job_title": r.get("job_title"),
                "company_name": r.get("company_name")
            })
            for r in records
        ]

    def get_suggested_connections(self, id: Any) -> list[tuple[Any, float, bool]]:
        """
        Return a list of tuples <user_id, score, is_friend_of_friends>. Scores are cached in database.
        """
        # Friends of friends (2-hop connections)
        records, _, _ = self.driver.execute_query(
            """
                MATCH (n:User {id: $id})
                    -[:CONNECTED_TO]-(intermediate:User)
                    -[r:CONNECTED_TO]-(n2:User)
                OPTIONAL MATCH (n2)-[:WORKS_AT]->(c:Company)
                WHERE n <> n2
                AND NOT (n)-[:CONNECTED_TO]-(n2)
                RETURN n2.id AS id, r.score AS score, n2.full_name AS full_name, n2.job_title AS job_title, c.name AS company_name;
            """,
            database_=self.database,
            id=id,
        )
        first_results = [
            {
                "user_id": r["id"],
                "score": float(r["score"]) if r["score"] is not None else 0.0,
                "full_name": r.get("full_name"),
                "job_title": r.get("job_title"),
                "company_name": r.get("company_name"),
                "friend_of_friend": True
            }
            for r in records
        ]

        # Other users not in first or second degree
        records, _, _ = self.driver.execute_query(
            """
                MATCH (n:User {id: $id})
                MATCH (n2:User)
                OPTIONAL MATCH (n2)-[:WORKS_AT]->(c:Company)
                WHERE n <> n2
                AND NOT (n)-[:CONNECTED_TO]-(n2)
                AND NOT (n)-[:CONNECTED_TO]-()-[:CONNECTED_TO]-(n2)
                RETURN DISTINCT n2.id AS id, 0.0 AS score, n2.full_name AS full_name, n2.job_title AS job_title, c.name AS company_name;
            """,
            database_=self.database,
            id=id,
        )
        second_results = [
            {
                "user_id": r["id"],
                "score": float(r["score"]),
                "full_name": r.get("full_name"),
                "job_title": r.get("job_title"),
                "company_name": r.get("company_name"),
                "friend_of_friend": False
            }
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
                MATCH (target:User {id: $target_id})
                    -[:WORKS_AT]->(company:Company)
                    -[:OPENS]->(v:Vacancy)
                OPTIONAL MATCH (v)-[r:SUGGESTED_TO]->(user:User {id: $id})
                WHERE target <> user:User {id: $id}
                AND NOT (user:User {id: $id})-[:CONNECTED_TO]-(target)
                RETURN DISTINCT v.id AS id, COALESCE(r.score, 0.5) AS score;
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
        Return a list of tuples <user_id, score> in one hop working at a specific company.
        """
        records, _, _ = self.driver.execute_query(
            """
                MATCH (n:User {id: $id})
                    -[r:CONNECTED_TO]-(n2:User)
                    -[:WORKS_AT]->(company:Company {id: $company_id})
                RETURN n2.id AS id, r.score AS score, n2.full_name AS full_name, n2.job_title AS job_title, company.name AS company_name
                ORDER BY score DESC;
            """,
            database_=self.database,
            id=id,
            company_id=company_id
        )
        return [
            ({
                "user_id": r["id"],
                "score": float(r["score"]) if r["score"] is not None else 0.0,
                "full_name": r.get("full_name"),
                "job_title": r.get("job_title"),
                "company_name": r.get("company_name")
            })
            for r in records
        ]

    def get_suggested_connections_for_specific_company(self, id: Any, company_id: Any) -> list[tuple[Any, float]]:
        """
        Return a list of tuples <user_id, score> in two hops working at a specific company.
        """
        records, _, _ = self.driver.execute_query(
            """
                MATCH (n:User {id: $id})
                    -[:CONNECTED_TO]-(intermediate:User)
                    -[r:CONNECTED_TO]-(n2:User)
                    -[:WORKS_AT]->(company:Company {id: $company_id})
                WHERE n <> n2
                AND NOT (n)-[:CONNECTED_TO]-(n2)
                RETURN n2.id AS id, r.score AS score, n2.full_name AS full_name, n2.job_title AS job_title, company.name AS company_name
                ORDER BY score DESC;
            """,
            database_=self.database,
            id=id,
            company_id=company_id,
        )
        return [
            ({
                "user_id": r["id"],
                "score": float(r["score"]) if r["score"] is not None else 0.0,
                "full_name": r.get("full_name"),
                "job_title": r.get("job_title"),
                "company_name": r.get("company_name")
            })
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
