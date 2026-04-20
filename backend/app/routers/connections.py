"""
Connection discovery and recommendation endpoints.

AUTH NOTE (temporary):
  user_id is accepted as a query param for demo purposes.
  When Dev A completes JWT auth, replace the `user_id: str` query param
  with `current_user_id: str = Depends(auth.get_current_user_id)` and
  remove the default value.

Endpoints:
  GET /api/user/network-stats?user_id=
  GET /api/connections/at-company/{company_id}?user_id=&max_hops=
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from neo4j import AsyncDriver

from app.db.neo4j import get_neo4j_driver
from app.services import recommendation

router = APIRouter()

DEMO_USER_ID = "user-001"


# ── Response models ────────────────────────────────────────────────────────────

class NetworkStatsResponse(BaseModel):
    connections: int
    companies: int
    referrals_sent: int


class SkillEntry(BaseModel):
    id: str
    name: str | None
    level: str | None


class ConnectionEntry(BaseModel):
    id: str
    full_name: str
    hops: int
    skills: list[SkillEntry]
    score: float
    score_method: str


class ConnectionsAtCompanyResponse(BaseModel):
    company_id: str
    total: int
    connections: list[ConnectionEntry]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/user/network-stats", response_model=NetworkStatsResponse)
async def network_stats(
    user_id: str = Query(default=DEMO_USER_ID, description="Replace with JWT dep when auth is ready"),
    driver: AsyncDriver = Depends(get_neo4j_driver),
):
    stats = await recommendation.get_network_stats(driver, user_id)
    return stats


@router.get(
    "/connections/at-company/{company_id}",
    response_model=ConnectionsAtCompanyResponse,
)
async def connections_at_company(
    company_id: str,
    user_id: str = Query(default=DEMO_USER_ID, description="Replace with JWT dep when auth is ready"),
    max_hops: int = Query(default=2, ge=1, le=2),
    driver: AsyncDriver = Depends(get_neo4j_driver),
):
    seeker = await recommendation.get_seeker_profile(driver, user_id)
    if seeker is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found in graph")

    connections = await recommendation.get_connections_at_company(
        driver, user_id, company_id, max_hops
    )
    ranked = recommendation.rank_connections(seeker, connections)

    return {
        "company_id": company_id,
        "total": len(ranked),
        "connections": ranked,
    }
