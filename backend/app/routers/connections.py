"""
Connection discovery and recommendation endpoints.

AUTH NOTE (temporary):
  user_id is accepted as a query param for demo purposes.
  When Dev A completes JWT auth, replace the `user_id: str` query param
  with `current_user_id: str = Depends(auth.get_current_user_id)` and
  remove the default value.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from neo4j import AsyncDriver
from sqlalchemy.orm import Session

from app.db.neo4j import get_neo4j_driver
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.schema import ConnectionRequest, User
from app.services import recommendation, company_graph, connection_service, user_graph

router = APIRouter()


class NetworkStatsResponse(BaseModel):
    connections: int
    companies: int
    referrals_sent: int


@router.get("/user/network-stats", response_model=NetworkStatsResponse)
async def network_stats(
    user_id: str = Depends(get_current_user_id),
    driver: AsyncDriver = Depends(get_neo4j_driver),
):
    return await recommendation.get_network_stats(driver, user_id)


@router.get("/connections")
async def all_connections(
    user_id: str = Depends(get_current_user_id),
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
    user_id: str = Depends(get_current_user_id),
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
    co, raw = await asyncio.gather(
        company_graph.get_company(driver, company_id),
        recommendation.get_connections_at_company(driver, user_id, company_id, max_hops),
    )
    ranked = recommendation.rank_connections(seeker, raw)
    return co, ranked
# ---------------------------------------------------------------------------
# Connection request endpoints (two-way add friend)
# ---------------------------------------------------------------------------

class ConnectionRequestResponse(BaseModel):
    id: str
    from_user_id: str
    to_user_id: str
    status: str
    created_at: datetime
    responded_at: datetime | None = None


class AddConnectionRequest(BaseModel):
    target_user_id: str


@router.post("/connections/request/{target_user_id}", response_model=ConnectionRequestResponse)
async def send_connection_request(
    target_user_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    driver: AsyncDriver = Depends(get_neo4j_driver),
):
    if user_id == target_user_id:
        raise HTTPException(status_code=400, detail="Cannot send a connection request to yourself")

    target = db.query(User).filter(User.id == target_user_id).first()
    if target is None:
        raise HTTPException(status_code=404, detail="Target user not found")

    already_connected = await connection_service.are_connected(driver, user_id, target_user_id)
    if already_connected:
        raise HTTPException(status_code=409, detail="Users are already connected")

    existing = (
        db.query(ConnectionRequest)
        .filter(
            ConnectionRequest.from_user_id == user_id,
            ConnectionRequest.to_user_id == target_user_id,
            ConnectionRequest.status == "pending",
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Connection request already pending")

    req = ConnectionRequest(from_user_id=user_id, to_user_id=target_user_id)
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.post("/connections/request/{request_id}/accept", response_model=ConnectionRequestResponse)
async def accept_connection_request(
    request_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    driver: AsyncDriver = Depends(get_neo4j_driver),
):
    req = db.query(ConnectionRequest).filter(ConnectionRequest.id == request_id).first()
    if req is None:
        raise HTTPException(status_code=404, detail="Connection request not found")
    if req.to_user_id != user_id:
        raise HTTPException(status_code=403, detail="Only the recipient can accept this request")
    if req.status != "pending":
        raise HTTPException(status_code=409, detail=f"Request is already {req.status}")

    created = await connection_service.create_connected_to(driver, req.from_user_id, req.to_user_id)
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create connection in graph — check that both users exist in Neo4j")

    req.status = "accepted"
    req.responded_at = datetime.utcnow()
    db.commit()
    db.refresh(req)
    return req


@router.post("/connections/request/{request_id}/decline", response_model=ConnectionRequestResponse)
async def decline_connection_request(
    request_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    req = db.query(ConnectionRequest).filter(ConnectionRequest.id == request_id).first()
    if req is None:
        raise HTTPException(status_code=404, detail="Connection request not found")
    if req.to_user_id != user_id:
        raise HTTPException(status_code=403, detail="Only the recipient can decline this request")
    if req.status != "pending":
        raise HTTPException(status_code=409, detail=f"Request is already {req.status}")

    req.status = "declined"
    req.responded_at = datetime.utcnow()
    db.commit()
    db.refresh(req)
    return req


@router.get("/connections/requests/incoming")
async def list_incoming_requests(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    reqs = (
        db.query(ConnectionRequest)
        .filter(
            ConnectionRequest.to_user_id == user_id,
            ConnectionRequest.status == "pending",
        )
        .order_by(ConnectionRequest.created_at.desc())
        .all()
    )
    return {"requests": [
        {
            "id": r.id,
            "from_user_id": r.from_user_id,
            "created_at": r.created_at,
        }
        for r in reqs
    ]}


@router.get("/connections/requests/outgoing")
async def list_outgoing_requests(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    reqs = (
        db.query(ConnectionRequest)
        .filter(
            ConnectionRequest.from_user_id == user_id,
            ConnectionRequest.status == "pending",
        )
        .order_by(ConnectionRequest.created_at.desc())
        .all()
    )
    return {"requests": [
        {
            "id": r.id,
            "to_user_id": r.to_user_id,
            "created_at": r.created_at,
        }
        for r in reqs
    ]}
