"""
User-related graph operations in Neo4j.

These functions are called from FastAPI routes after validation/auth.
They handle the graph-side of user lifecycle:
  - Creating a User node when registration succeeds
  - Upserting the WORKS_AT edge when a user declares their company
  - Removing WORKS_AT when user changes jobs
"""

from datetime import datetime, timezone
from neo4j import AsyncDriver


async def create_user_node(
    driver: AsyncDriver,
    user_id: str,
    full_name: str,
    phone_number: str,
) -> dict:
    """
    Create a User node in Neo4j. Called after successful registration.

    Uses MERGE to be idempotent — if the node already exists (e.g. from a
    ghost node being resolved), we just update its properties.

    Returns the node's properties.
    """
    query = """
    MERGE (u:User {id: $user_id})
    ON CREATE SET
        u.full_name = $full_name,
        u.phone_number = $phone_number,
        u.latent_vector = [],
        u.bias = 0.0,
        u.created_at = datetime()
    ON MATCH SET
        u.full_name = $full_name,
        u.phone_number = $phone_number
    RETURN u {.id, .full_name, .phone_number} AS user
    """
    async with driver.session() as session:
        result = await session.run(
            query,
            user_id=user_id,
            full_name=full_name,
            phone_number=phone_number,
        )
        record = await result.single()
        return record["user"] if record else None


async def set_user_company(
    driver: AsyncDriver,
    user_id: str,
    company_id: str,
    job_title: str | None = None,
) -> dict | None:
    """
    Declare or update the user's employer.

    If a WORKS_AT edge already exists for this user, it's replaced with
    the new one. This models "I changed jobs" — we only track the current
    employer (historical job data would be a separate concern).

    Returns the company properties if successful, None if company not found.
    """
    # Step 1: Remove any existing WORKS_AT edges from this user
    # (A user has at most one current employer.)
    remove_old = """
    MATCH (u:User {id: $user_id})-[r:WORKS_AT]->(:Company)
    DELETE r
    """

    # Step 2: Create the new WORKS_AT edge, only if the company exists.
    # Using MATCH (not MERGE) on Company so we fail loudly if an invalid
    # company_id is passed — companies are pre-seeded, not created on demand.
    create_new = """
    MATCH (u:User {id: $user_id})
    MATCH (c:Company {id: $company_id})
    CREATE (u)-[r:WORKS_AT {
        job_title: $job_title,
        since: datetime()
    }]->(c)
    RETURN c {.id, .name, .industry} AS company, r.job_title AS job_title
    """

    async with driver.session() as session:
        # Run both in a single transaction so we don't leave the user
        # with no company if the new MATCH fails.
        async with await session.begin_transaction() as tx:
            await tx.run(remove_old, user_id=user_id)
            result = await tx.run(
                create_new,
                user_id=user_id,
                company_id=company_id,
                job_title=job_title,
            )
            record = await result.single()
            if record is None:
                # Company not found — rollback
                await tx.rollback()
                return None
            await tx.commit()
            return {
                "company": record["company"],
                "job_title": record["job_title"],
            }


async def clear_user_company(driver: AsyncDriver, user_id: str) -> bool:
    """
    Remove the user's WORKS_AT edge (e.g., user is unemployed or no longer wants to declare).
    Returns True if an edge was removed, False if none existed.
    """
    query = """
    MATCH (u:User {id: $user_id})-[r:WORKS_AT]->(:Company)
    DELETE r
    RETURN count(r) AS removed
    """
    async with driver.session() as session:
        result = await session.run(query, user_id=user_id)
        record = await result.single()
        return record["removed"] > 0 if record else False


async def get_user_with_company(driver: AsyncDriver, user_id: str) -> dict | None:
    """
    Fetch user + their current company (if any) in one query.
    Used by GET /user/profile and the /auth/me endpoint.
    """
    query = """
    MATCH (u:User {id: $user_id})
    OPTIONAL MATCH (u)-[r:WORKS_AT]->(c:Company)
    RETURN
        u {.id, .full_name, .phone_number} AS user,
        c {.id, .name, .industry} AS company,
        r.job_title AS job_title
    """
    async with driver.session() as session:
        result = await session.run(query, user_id=user_id)
        record = await result.single()
        if record is None:
            return None
        return {
            "user": record["user"],
            "company": record["company"],  # May be None
            "job_title": record["job_title"],
        }


async def create_connection(
    driver: AsyncDriver,
    user_id: str,
    target_user_id: str,
) -> bool:
    """
    Create a CONNECTED_TO relationship between two users.
    Idempotent: if the relationship already exists, it's a no-op.
    Returns True if successful, False if either user doesn't exist.
    """
    query = """
    MATCH (u1:User {id: $user_id})
    MATCH (u2:User {id: $target_user_id})
    MERGE (u1)-[:CONNECTED_TO]-(u2)
    RETURN true
    """
    async with driver.session() as session:
        result = await session.run(query, user_id=user_id, target_user_id=target_user_id)
        record = await result.single()
        return record is not None
