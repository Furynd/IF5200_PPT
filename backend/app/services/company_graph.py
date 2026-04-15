"""
Company-related graph operations.

Companies are pre-seeded by init_neo4j.py and are read-only from the user's
perspective (users don't create new companies, they only select from existing).

For fuzzy search, Neo4j's built-in STRING operations (CONTAINS, STARTS WITH)
work fine for MVP scale (100-300 companies). If we need proper trigram
similarity later, we can mirror company data to PostgreSQL and use pg_trgm.
"""

from neo4j import AsyncDriver


async def search_companies(
    driver: AsyncDriver,
    query: str,
    limit: int = 10,
) -> list[dict]:
    """
    Search companies by name. Case-insensitive substring match.

    Ranking:
      1. Exact match (case-insensitive)
      2. Starts-with match
      3. Contains match

    Returns list of {id, name, industry, connection_count} objects.
    connection_count is the number of registered users who WORKS_AT this company.
    """
    if not query or len(query.strip()) < 2:
        return []

    normalized = query.strip().lower()

    # Cypher's toLower() ensures case-insensitive matching.
    # We compute a rank score so results can be ordered by relevance.
    cypher = """
    MATCH (c:Company)
    WITH c, toLower(c.name) AS lname
    WHERE lname CONTAINS $query
    OPTIONAL MATCH (c)<-[:WORKS_AT]-(u:User)
    WITH c, lname, count(u) AS connection_count
    RETURN
        c.id AS id,
        c.name AS name,
        c.industry AS industry,
        connection_count,
        CASE
            WHEN lname = $query THEN 0
            WHEN lname STARTS WITH $query THEN 1
            ELSE 2
        END AS rank
    ORDER BY rank ASC, connection_count DESC, c.name ASC
    LIMIT $limit
    """

    async with driver.session() as session:
        result = await session.run(cypher, query=normalized, limit=limit)
        records = await result.data()
        return [
            {
                "id": r["id"],
                "name": r["name"],
                "industry": r["industry"],
                "connection_count": r["connection_count"],
            }
            for r in records
        ]


async def get_company(driver: AsyncDriver, company_id: str) -> dict | None:
    """
    Fetch a single company by ID with the count of registered employees.
    """
    query = """
    MATCH (c:Company {id: $company_id})
    OPTIONAL MATCH (c)<-[:WORKS_AT]-(u:User)
    RETURN
        c.id AS id,
        c.name AS name,
        c.industry AS industry,
        count(u) AS connection_count
    """
    async with driver.session() as session:
        result = await session.run(query, company_id=company_id)
        record = await result.single()
        if record is None:
            return None
        return {
            "id": record["id"],
            "name": record["name"],
            "industry": record["industry"],
            "connection_count": record["connection_count"],
        }


async def company_exists(driver: AsyncDriver, company_id: str) -> bool:
    """Quick existence check before creating WORKS_AT edges."""
    query = "MATCH (c:Company {id: $company_id}) RETURN c.id LIMIT 1"
    async with driver.session() as session:
        result = await session.run(query, company_id=company_id)
        record = await result.single()
        return record is not None
