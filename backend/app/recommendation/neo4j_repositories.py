from __future__ import annotations

from neo4j import Driver

from app.repositories import UserRepository, VacancyRepository


class Neo4jUserRepository(UserRepository):
    def __init__(self, driver: Driver):
        self.driver = driver

    @staticmethod
    def _normalize_user_id(user_id: str | int) -> str:
        if isinstance(user_id, int):
            return f"user-{user_id:03d}"
        value = str(user_id).strip()
        if value.isdigit():
            return f"user-{int(value):03d}"
        return value

    def get_connections(self, id: int) -> list[tuple[int, float]]:
        user_id = self._normalize_user_id(id)
        query = """
        MATCH (me:User {id: $user_id})
        MATCH (me)-[:CONNECTED_TO]-(conn:User)
        WHERE conn.id <> me.id
          AND conn.is_open_to_refer = true
                RETURN DISTINCT
            conn.id AS connected_user_id,
            coalesce(conn.bias, 0.0) AS score
        ORDER BY score DESC, connected_user_id ASC
        """
        with self.driver.session() as session:
            rows = session.run(query, user_id=user_id).data()
        return [(r["connected_user_id"], float(r["score"])) for r in rows]

    def get_suggested_connections(self, id: int) -> list[tuple[int, float]]:
        user_id = self._normalize_user_id(id)
        query = """
        MATCH (me:User {id: $user_id})
        MATCH (me)-[:CONNECTED_TO*2..2]-(conn:User)
        WHERE conn.id <> me.id
          AND conn.is_open_to_refer = true
          AND NOT (me)-[:CONNECTED_TO]-(conn)
        RETURN DISTINCT
            conn.id AS connected_user_id,
            coalesce(conn.bias, 0.0) AS score
        ORDER BY score DESC, connected_user_id ASC
        """
        with self.driver.session() as session:
            rows = session.run(query, user_id=user_id).data()
        return [(r["connected_user_id"], float(r["score"])) for r in rows]

    def get_vacancies_from_current_companies(self, id: int) -> list[tuple[int, float]]:
        user_id = self._normalize_user_id(id)
        with self.driver.session() as session:
            label_row = session.run("CALL db.labels() YIELD label RETURN collect(label) AS labels").single()
            labels = set(label_row["labels"] if label_row and label_row["labels"] else [])

        has_vacancy_label = "Vacancy" in labels

        real_vacancy_query = """
        MATCH (me:User {id: $user_id})-[:CONNECTED_TO*1..2]-(conn:User)-[:WORKS_AT]->(c:Company)
        WHERE conn.id <> me.id AND conn.is_open_to_refer = true
        MATCH (v:Vacancy)-[:POSTED_BY]->(c)
        RETURN DISTINCT v.id AS vacancy_id, 0.9 AS score
        ORDER BY score DESC, vacancy_id ASC
        """
        fallback_query = """
        MATCH (me:User {id: $user_id})-[:CONNECTED_TO*1..2]-(conn:User)-[:WORKS_AT]->(c:Company)
        WHERE conn.id <> me.id AND conn.is_open_to_refer = true
        RETURN DISTINCT c.id AS company_id, 0.7 AS score
        ORDER BY company_id ASC
        """

        with self.driver.session() as session:
            if has_vacancy_label:
                vacancy_rows = session.run(real_vacancy_query, user_id=user_id).data()
                if vacancy_rows:
                    return [(r["vacancy_id"], float(r["score"])) for r in vacancy_rows]

            company_rows = session.run(fallback_query, user_id=user_id).data()
        return [(f"company-opportunity:{r['company_id']}", float(r["score"])) for r in company_rows]


class Neo4jVacancyRepository(VacancyRepository):
    def __init__(self, driver: Driver):
        self.driver = driver

    def get_required_skills(self, id: int) -> list[int]:
        vacancy_id = str(id)
        query = """
        MATCH (v:Vacancy {id: $vacancy_id})-[:REQUIRES_SKILL]->(s:Skill)
        RETURN s.id AS skill_id
        """
        with self.driver.session() as session:
            rows = session.run(query, vacancy_id=vacancy_id).data()
        return [r["skill_id"] for r in rows]

    def get_info(self, id: int) -> tuple[int, str, str]:
        vacancy_id = str(id)

        if vacancy_id.startswith("company-opportunity:"):
            company_id = vacancy_id.split(":", maxsplit=1)[1]
            query = """
            MATCH (c:Company {id: $company_id})
            RETURN c.id AS company_id, c.name AS company_name
            """
            with self.driver.session() as session:
                row = session.run(query, company_id=company_id).single()
            if row is None:
                return ("unknown-company", "Opportunity", "")
            return (
                row["company_id"],
                f"Referral opportunity at {row['company_name']}",
                "",
            )

        query = """
        MATCH (v:Vacancy {id: $vacancy_id})-[:POSTED_BY]->(c:Company)
        RETURN
            c.id AS company_id,
            coalesce(v.description, coalesce(v.title, 'Vacancy')) AS description,
            coalesce(v.source_url, '') AS source_url
        """
        with self.driver.session() as session:
            row = session.run(query, vacancy_id=vacancy_id).single()

        if row is None:
            return ("unknown-company", "Unknown vacancy", "")

        return (row["company_id"], row["description"], row["source_url"])
