"""
Algorithmic CV skill extractor.

Matching pipeline (in order, short-circuits on first hit per skill):
  1. Exact word-boundary match (case-insensitive)
  2. Alias match — abbreviations/variants that differ substantially from the skill name
  3. Fuzzy token match via rapidfuzz (threshold 85)

Skills are fetched live from Neo4j so adding new nodes requires no code change.
"""

import re
from typing_extensions import TypedDict
from typing import List

from neo4j import AsyncDriver
from rapidfuzz import fuzz, process

# ---------------------------------------------------------------------------
# Alias table: skill name (lowercased) → list of alternative surface forms
# Only needed when the variant is substantially different from the canonical name.
# ---------------------------------------------------------------------------
_ALIASES: dict[str, list[str]] = {
    "javascript": ["js", "ecmascript", "es6", "es2015", "es2016", "es2017", "es2018"],
    "typescript": ["ts"],
    "react": ["react.js", "reactjs", "react js"],
    "node.js": ["nodejs", "node js", "node"],
    "machine learning": ["ml", "deep learning", "neural network", "neural nets", "dl"],
    "cloud computing (aws/gcp)": ["aws", "gcp", "amazon web services", "google cloud", "azure", "cloud"],
    "ui/ux design": ["ux", "ui", "ux design", "ui design", "user experience", "user interface"],
    "sql": ["mysql", "postgresql", "postgres", "sqlite", "mssql", "mariadb", "t-sql", "pl/sql"],
    "devops": ["ci/cd", "cicd", "continuous integration", "continuous deployment"],
    "cybersecurity": ["infosec", "information security", "pentest", "penetration testing"],
}


class MatchedSkill(TypedDict):
    id: str
    name: str
    score: float          # 0.0–1.0; 1.0 = exact, lower = fuzzy
    match_type: str       # "exact" | "alias" | "fuzzy"


async def fetch_skills(driver: AsyncDriver) -> list[dict]:
    """Return all Skill nodes as [{"id": ..., "name": ...}]."""
    async with driver.session() as session:
        result = await session.run("MATCH (s:Skill) RETURN s.id AS id, s.name AS name")
        return await result.data()


async def store_user_skills(driver: AsyncDriver, user_id: str, matched_skills: List[MatchedSkill]) -> None:
    """Persist matched skills for a user in Neo4j.

    For each matched skill this will MERGE a `HAS_SKILL` relationship from
    the `User` node to the `Skill` node and set properties on the edge:
    - `level`: numeric score (0.0-1.0)
    - `match_type`: one of "exact" | "alias" | "fuzzy"
    Existing edges will be updated with the new values.
    """
    if not matched_skills:
        return

    async with driver.session() as session:
        tx = await session.begin_transaction()
        try:
            for ms in matched_skills:
                # Use MERGE to create the relationship idempotently and
                # SET to update the level/match_type timestamp.
                await tx.run(
                    """
                    MATCH (u:User {id: $user_id})
                    MATCH (s:Skill {id: $skill_id})
                    MERGE (u)-[hs:HAS_SKILL]->(s)
                    SET hs.level = $level, hs.match_type = $match_type, hs.updated_at = datetime()
                    """,
                    user_id=user_id,
                    skill_id=ms["id"],
                    level=float(ms["score"]),
                    match_type=ms["match_type"],
                )
            await tx.commit()
        except Exception:
            await tx.rollback()
            raise


async def extract_and_store_user_skills(driver: AsyncDriver, user_id: str, cv_text: str) -> List[MatchedSkill]:
    """Convenience wrapper: fetch skills, extract matches from `cv_text`, and store them for `user_id`.

    Returns the list of matched skills that were persisted.
    """
    db_skills = await fetch_skills(driver)
    matches = extract_skills(cv_text, db_skills)
    await store_user_skills(driver, user_id, matches)
    return matches


def _normalize(text: str) -> str:
    return text.lower().strip()


def _word_boundary_present(pattern: str, text: str) -> bool:
    """True if pattern appears as a whole token (not mid-word) in text."""
    escaped = re.escape(pattern)
    return bool(re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", text, re.IGNORECASE))


def extract_skills(cv_text: str, db_skills: list[dict]) -> list[MatchedSkill]:
    """
    Match cv_text against db_skills and return matched skills with scores.
    db_skills: list of {"id": str, "name": str} from Neo4j.
    """
    normalized_cv = _normalize(cv_text)
    results: list[MatchedSkill] = []

    # Build alias lookup: alias surface form → canonical skill name (lowercased)
    alias_lookup: dict[str, str] = {}
    for canonical, variants in _ALIASES.items():
        for v in variants:
            alias_lookup[_normalize(v)] = canonical

    for skill in db_skills:
        skill_id: str = skill["id"]
        skill_name: str = skill["name"]
        canonical = _normalize(skill_name)

        # --- Layer 1: exact word-boundary match ---
        if _word_boundary_present(canonical, normalized_cv):
            results.append(MatchedSkill(id=skill_id, name=skill_name, score=1.0, match_type="exact"))
            continue

        # --- Layer 2: alias match ---
        alias_hit = False
        if canonical in _ALIASES:
            for alias in _ALIASES[canonical]:
                if _word_boundary_present(alias, normalized_cv):
                    results.append(MatchedSkill(id=skill_id, name=skill_name, score=0.95, match_type="alias"))
                    alias_hit = True
                    break
        if alias_hit:
            continue

        # --- Layer 3: fuzzy match on sliding n-gram windows of CV tokens ---
        # Split CV into overlapping n-grams up to len(skill_name words) to
        # avoid matching single short tokens against long skill names.
        skill_word_count = len(canonical.split())
        tokens = normalized_cv.split()
        best_ratio = 0.0
        for i in range(len(tokens)):
            window = " ".join(tokens[i : i + skill_word_count + 1])
            ratio = fuzz.ratio(canonical, window) / 100.0
            if ratio > best_ratio:
                best_ratio = ratio

        if best_ratio >= 0.85:
            results.append(MatchedSkill(id=skill_id, name=skill_name, score=round(best_ratio, 3), match_type="fuzzy"))

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
