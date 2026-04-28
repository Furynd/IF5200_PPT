"""
Connection discovery + Fang et al. (2013) ranking.

Scoring (Fang method):
  score = dot(seeker.latent_vector, conn.latent_vector) + seeker.bias + conn.bias

Fallback when either vector is empty (not yet trained):
  score = Jaccard similarity on HAS_SKILL sets

A small hop penalty (0.05 per extra hop) keeps direct connections slightly
preferred when scores are otherwise equal.
"""

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
    Fetch all 1-and-2-hop connections at company_id.

    Returns one record per connection (minimum hop distance).
    path_via contains the name(s) of intermediate users for 2-hop paths.
    nodes(path)[1..-2] isolates intermediate nodes between me and conn,
    excluding both endpoints and the company node.
    """
    path_query = f"""
    MATCH path = (me:User {{id: $user_id}})-[:CONNECTED_TO*1..{max_hops}]-(conn:User)
                 -[wa:WORKS_AT]->(c:Company {{id: $company_id}})
    WHERE conn.id <> $user_id
      AND conn.is_open_to_refer = true
    RETURN
        conn.id               AS id,
        conn.full_name        AS full_name,
        conn.latent_vector    AS latent_vector,
        conn.bias             AS bias,
        conn.is_open_to_refer AS is_open_to_refer,
        wa.job_title          AS job_title,
        length(path) - 1      AS hops,
        [n IN nodes(path)[1..-2] | n.full_name] AS path_via
    ORDER BY hops ASC
    """

    skills_query = """
    UNWIND $conn_ids AS conn_id
    MATCH (conn:User {id: conn_id})-[hs:HAS_SKILL]->(s:Skill)
    RETURN conn_id, s.id AS skill_id, s.name AS skill_name, hs.level AS level
    """

    async with driver.session() as session:
        path_result = await session.run(path_query, user_id=user_id, company_id=company_id)
        path_records = await path_result.data()

    # Deduplicate: keep the minimum-hop record per connection
    seen: dict[str, dict] = {}
    for r in path_records:
        cid = r["id"]
        if cid not in seen or r["hops"] < seen[cid]["hops"]:
            seen[cid] = r

    if not seen:
        return []

    # Fetch skills for all connections in one query
    async with driver.session() as session:
        skills_result = await session.run(skills_query, conn_ids=list(seen.keys()))
        skills_records = await skills_result.data()

    skills_by_conn: dict[str, list] = {cid: [] for cid in seen}
    for s in skills_records:
        skills_by_conn[s["conn_id"]].append({
            "id": s["skill_id"],
            "name": s["skill_name"],
            "level": s["level"],
        })

    return [
        {
            "id": r["id"],
            "full_name": r["full_name"],
            "latent_vector": list(r["latent_vector"] or []),
            "bias": float(r["bias"] or 0.0),
            "is_open_to_refer": r["is_open_to_refer"],
            "job_title": r["job_title"],
            "hops": r["hops"],
            "path_via": r["path_via"] or [],
            "skills": skills_by_conn.get(r["id"], []),
        }
        for r in seen.values()
    ]


def rank_connections(seeker: dict, connections: list[dict]) -> list[dict]:
    """Score and sort connections using Fang's method (or Jaccard fallback)."""
    ranked = []
    for conn in connections:
        score, method = _fang_score(
            seeker["latent_vector"], seeker["bias"],
            conn["latent_vector"], conn["bias"],
        )
        if method == "skill_overlap":
            conn_skill_ids = {s["id"] for s in conn["skills"]}
            score = _jaccard(seeker["skill_ids"], conn_skill_ids)

        final_score = round(score, 4)

        ranked.append({
            "user": {"id": conn["id"], "full_name": conn["full_name"]},
            "job_title": conn["job_title"],
            "company_id": conn.get("company_id"),
            "company_name": conn.get("company_name"),
            "hops": conn["hops"],
            "path_via": conn["path_via"],
            "is_open_to_refer": conn["is_open_to_refer"],
            "skills": conn["skills"],
            "score": final_score,
            "score_method": method,
        })

    ranked.sort(key=lambda x: (x["hops"], -x["score"]))
    return ranked


async def get_all_connections(
    driver: AsyncDriver,
    user_id: str,
    max_hops: int = 2,
) -> list[dict]:
    """
    Fetch all connections (1- and 2-hop) regardless of company, deduplicated by min hop.
    Includes company context when available.
    """
    path_query = f"""
    MATCH path = (me:User {{id: $user_id}})-[:CONNECTED_TO*1..{max_hops}]-(conn:User)
    WHERE conn.id <> $user_id
    OPTIONAL MATCH (conn)-[wa:WORKS_AT]->(c:Company)
    RETURN
        conn.id               AS id,
        conn.full_name        AS full_name,
        conn.latent_vector    AS latent_vector,
        conn.bias             AS bias,
        conn.is_open_to_refer AS is_open_to_refer,
        length(path)          AS hops,
        [n IN nodes(path)[1..-1] | n.full_name] AS path_via,
        wa.job_title          AS job_title,
        c.id                  AS company_id,
        c.name                AS company_name
    ORDER BY hops ASC
    """

    skills_query = """
    UNWIND $conn_ids AS conn_id
    MATCH (conn:User {id: conn_id})-[hs:HAS_SKILL]->(s:Skill)
    RETURN conn_id, s.id AS skill_id, s.name AS skill_name, hs.level AS level
    """

    async with driver.session() as session:
        path_result = await session.run(path_query, user_id=user_id)
        path_records = await path_result.data()

    seen: dict[str, dict] = {}
    for r in path_records:
        cid = r["id"]
        if cid not in seen or r["hops"] < seen[cid]["hops"]:
            seen[cid] = r

    if not seen:
        return []

    async with driver.session() as session:
        skills_result = await session.run(skills_query, conn_ids=list(seen.keys()))
        skills_records = await skills_result.data()

    skills_by_conn: dict[str, list] = {cid: [] for cid in seen}
    for s in skills_records:
        skills_by_conn[s["conn_id"]].append({
            "id": s["skill_id"],
            "name": s["skill_name"],
            "level": s["level"],
        })

    return [
        {
            "id": r["id"],
            "full_name": r["full_name"],
            "latent_vector": list(r["latent_vector"] or []),
            "bias": float(r["bias"] or 0.0),
            "is_open_to_refer": r["is_open_to_refer"],
            "hops": r["hops"],
            "path_via": r["path_via"] or [],
            "job_title": r["job_title"],
            "company_id": r["company_id"],
            "company_name": r["company_name"],
            "skills": skills_by_conn.get(r["id"], []),
        }
        for r in seen.values()
    ]


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
            "referrals_sent": 0,
        }
