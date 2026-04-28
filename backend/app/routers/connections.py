"""
Connection discovery and recommendation endpoints.

AUTH NOTE (temporary):
  user_id is accepted as a query param for demo purposes.
  When Dev A completes JWT auth, replace the `user_id: str` query param
  with `current_user_id: str = Depends(auth.get_current_user_id)` and
  remove the default value.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from neo4j import AsyncDriver

from app.db.neo4j import get_neo4j_driver
from app.services import recommendation, company_graph, user_graph

router = APIRouter()

DEMO_USER_ID = "user-001"


class NetworkStatsResponse(BaseModel):
    connections: int
    companies: int
    referrals_sent: int


@router.get("/user/network-stats", response_model=NetworkStatsResponse)
async def network_stats(
    user_id: str = Query(default=DEMO_USER_ID),
    driver: AsyncDriver = Depends(get_neo4j_driver),
):
    return await recommendation.get_network_stats(driver, user_id)


@router.get("/connections")
async def all_connections(
    user_id: str = Query(default=DEMO_USER_ID),
    max_hops: int = Query(default=2, ge=1, le=2),
    driver: AsyncDriver = Depends(get_neo4j_driver),
):
    seeker = await recommendation.get_seeker_profile(driver, user_id)
    if seeker is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found in graph")

    raw = await recommendation.get_all_connections(driver, user_id, max_hops)
    ranked = recommendation.rank_connections(seeker, raw)
    return {"connections": ranked}


@router.get("/connections/at-company/{company_id}")
async def connections_at_company(
    company_id: str,
    user_id: str = Query(default=DEMO_USER_ID),
    max_hops: int = Query(default=2, ge=1, le=2),
    driver: AsyncDriver = Depends(get_neo4j_driver),
):
    seeker = await recommendation.get_seeker_profile(driver, user_id)
    if seeker is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found in graph")

    company, connections = await _fetch_both(driver, user_id, company_id, max_hops, seeker)

    if company is None:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")

    return {
        "company": company,
        "connections": connections,
    }


async def _fetch_both(driver, user_id, company_id, max_hops, seeker):
    import asyncio
    company_task = recommendation.get_network_stats  # placeholder — run both concurrently
    co, raw = await asyncio.gather(
        company_graph.get_company(driver, company_id),
        recommendation.get_connections_at_company(driver, user_id, company_id, max_hops),
    )
    ranked = recommendation.rank_connections(seeker, raw)
    return co, ranked


class AddConnectionRequest(BaseModel):
    target_user_id: str


@router.post("/connections")
async def add_connection(
    request: AddConnectionRequest,
    user_id: str = Query(default=DEMO_USER_ID),
    driver: AsyncDriver = Depends(get_neo4j_driver),
):
    """Create a CONNECTED_TO relationship between two users."""
    success = await user_graph.create_connection(driver, user_id, request.target_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User or target user not found")
    return {"status": "ok", "message": "Connection created"}
