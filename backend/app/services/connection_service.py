"""
Neo4j operations for the connection (friendship) feature.

Called only after the PostgreSQL ConnectionRequest record has been
accepted — this is the step that actually writes the graph edge.
"""

from neo4j import AsyncDriver


async def are_connected(driver: AsyncDriver, user_a_id: str, user_b_id: str) -> bool:
    """Return True if a CONNECTED_TO edge already exists between the two users."""
    query = """
    MATCH (a:User {id: $user_a_id})-[:CONNECTED_TO]-(b:User {id: $user_b_id})
    RETURN count(*) > 0 AS connected
    """
    async with driver.session() as session:
        result = await session.run(query, user_a_id=user_a_id, user_b_id=user_b_id)
        record = await result.single()
        return bool(record["connected"]) if record else False


async def create_connected_to(driver: AsyncDriver, user_a_id: str, user_b_id: str) -> bool:
    """
    Create bidirectional CONNECTED_TO edges between two users.

    Uses MERGE so calling this twice is safe. Returns True if both nodes
    were found and the edges were created/confirmed.
    """
    query = """
    MATCH (a:User {id: $user_a_id}), (b:User {id: $user_b_id})
    MERGE (a)-[:CONNECTED_TO {source: 'direct', created_at: datetime()}]->(b)
    MERGE (b)-[:CONNECTED_TO {source: 'direct', created_at: datetime()}]->(a)
    RETURN a.id AS a, b.id AS b
    """
    async with driver.session() as session:
        result = await session.run(query, user_a_id=user_a_id, user_b_id=user_b_id)
        record = await result.single()
        return record is not None
