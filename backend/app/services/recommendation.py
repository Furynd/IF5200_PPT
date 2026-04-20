"""
Connection discovery + Fang et al. (2013) ranking.

Two queries are run:
  1. Fetch the seeker's latent_vector, bias, and skill IDs from Neo4j.
  2. Fetch all 1-and-2-hop connections at the target company with their
     vectors, biases, skills, and hop distance.

Scoring (Fang method):
  score = dot(seeker.latent_vector, conn.latent_vector) + seeker.bias + conn.bias

Fallback when either vector is empty (not yet trained):
  score = Jaccard similarity on HAS_SKILL sets

A small hop penalty (0.05 per extra hop) keeps direct connections slightly
preferred when scores are otherwise equal.
"""

import math
from neo4j import AsyncDriver


def _dot(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or len(a) == 0:
        return 0.0
    return sum(x * y for x, y in zip(a, b))


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _fang_score(
    seeker_vec: list[float],
    seeker_bias: float,
    conn_vec: list[float],
    conn_bias: float,
) -> tuple[float, str]:
    """Returns (score, method) where method is 'fang' or 'skill_overlap'."""
    if seeker_vec and conn_vec and len(seeker_vec) == len(conn_vec):
        return _dot(seeker_vec, conn_vec) + seeker_bias + conn_bias, "fang"
    return 0.0, "skill_overlap"


async def get_seeker_profile(driver: AsyncDriver, user_id: str) -> dict | None:
    query = """
    MATCH (me:User {id: $user_id})
    OPTIONAL MATCH (me)-[:HAS_SKILL]->(s:Skill)
    RETURN
        me.latent_vector AS latent_vector,
        me.bias          AS bias,
        collect(s.id)    AS skill_ids
    """
    async with driver.session() as session:
        result = await session.run(query, user_id=user_id)
        record = await result.single()
        if record is None:
            return None
        return {
            "latent_vector": list(record["latent_vector"] or []),
            "bias": float(record["bias"] or 0.0),
            "skill_ids": set(record["skill_ids"]),
        }


async def get_connections_at_company(
    driver: AsyncDriver,
    user_id: str,
    company_id: str,
    max_hops: int = 2,
) -> list[dict]:
    """
    Returns all 1-and-2-hop connections working at company_id.
    Each record includes latent_vector, bias, skills, and hop distance.
    """
    query = """
    MATCH path = (me:User {id: $user_id})-[:CONNECTED_TO*1..$max_hops]-(conn:User)
                 -[:WORKS_AT]->(c:Company {id: $company_id})
    WHERE conn.id <> $user_id
      AND conn.is_open_to_refer = true
    WITH DISTINCT conn, min(length(path) - 1) AS hops
    OPTIONAL MATCH (conn)-[hs:HAS_SKILL]->(s:Skill)
    WITH conn, hops, collect({id: s.id, name: s.name, level: hs.level}) AS skills
    RETURN
        conn.id            AS id,
        conn.full_name     AS full_name,
        conn.latent_vector AS latent_vector,
        conn.bias          AS bias,
        hops,
        skills
    """
    async with driver.session() as session:
        result = await session.run(
            query, user_id=user_id, company_id=company_id, max_hops=max_hops
        )
        records = await result.data()

    connections = []
    for r in records:
        connections.append({
            "id": r["id"],
            "full_name": r["full_name"],
            "latent_vector": list(r["latent_vector"] or []),
            "bias": float(r["bias"] or 0.0),
            "hops": r["hops"],
            "skills": [
                {"id": s["id"], "name": s["name"], "level": s["level"]}
                for s in r["skills"]
                if s["id"] is not None
            ],
        })
    return connections


def rank_connections(seeker: dict, connections: list[dict]) -> list[dict]:
    """
    Score and sort connections using Fang's method (or Jaccard fallback).
    Adds 'score' and 'score_method' to each connection dict.
    Returns a new list sorted by score descending.
    """
    ranked = []
    for conn in connections:
        score, method = _fang_score(
            seeker["latent_vector"], seeker["bias"],
            conn["latent_vector"], conn["bias"],
        )

        if method == "skill_overlap":
            conn_skill_ids = {s["id"] for s in conn["skills"]}
            score = _jaccard(seeker["skill_ids"], conn_skill_ids)

        # Small penalty per extra hop so 1-hop beats 2-hop when scores are tied
        hop_penalty = 0.05 * (conn["hops"] - 1)
        final_score = round(score - hop_penalty, 4)

        ranked.append({
            **conn,
            "score": final_score,
            "score_method": method,
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)
    # Strip internal vector fields before returning to the router
    for c in ranked:
        del c["latent_vector"]
        del c["bias"]
    return ranked


async def get_network_stats(driver: AsyncDriver, user_id: str) -> dict:
    query = """
    MATCH (me:User {id: $user_id})-[:CONNECTED_TO]-(conn:User)
    OPTIONAL MATCH (conn)-[:WORKS_AT]->(c:Company)
    RETURN
        count(DISTINCT conn) AS connections,
        count(DISTINCT c)    AS companies
    """
    async with driver.session() as session:
        result = await session.run(query, user_id=user_id)
        record = await result.single()
        return {
            "connections": record["connections"] if record else 0,
            "companies": record["companies"] if record else 0,
            "referrals_sent": 0,  # filled by Dev A once PostgreSQL is wired
        }
