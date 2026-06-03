from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.neo4j import get_neo4j_driver
from app.core.security import get_current_user_id
from app.models.schema import User
from app.user_profile_repositories import UserProfileSyncRepository
from app.services.user_graph import (
    get_user_with_company,
    set_user_company,
    clear_user_company,
)

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    company_id: str | None = None
    job_title: str | None = None
    full_name: str | None = None
    phone_number: str | None = None
    is_open_to_refer: bool | None = None


def _public_user_dict(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "linkedin_id": user.linkedin_id,
        "is_admin": user.is_admin,
        "is_open_to_refer": user.is_open_to_refer,
        "referral_quota": user.referral_quota,
        "created_at": user.created_at,
        "cv_filename": user.cv_filename,
        "cv_url": user.cv_url,
    }


@router.get("/user/profile")
async def get_user_profile(
    db: Session = Depends(get_db),
    driver = Depends(get_neo4j_driver),
    user_id: str = Depends(get_current_user_id),
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Profil tidak ditemukan")

    graph = await get_user_with_company(driver, user_id)
    company = graph.get("company") if graph else None
    job_title = graph.get("job_title") if graph else None

    result = _public_user_dict(db_user)
    result["company"] = company
    result["job_title"] = job_title
    return result


@router.put("/user/profile")
async def update_user_profile(
    payload: UpdateProfileRequest,
    db: Session = Depends(get_db),
    driver = Depends(get_neo4j_driver),
    user_id: str = Depends(get_current_user_id),
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Profil tidak ditemukan")

    # Update Postgres fields if provided
    if payload.full_name is not None:
        db_user.full_name = payload.full_name.strip() or None
    if payload.phone_number is not None:
        db_user.phone_number = payload.phone_number.strip() or None
    if payload.is_open_to_refer is not None:
        db_user.is_open_to_refer = bool(payload.is_open_to_refer)

    db.commit()
    db.refresh(db_user)

    # Handle company/job in Neo4j
    company = None
    job_title = None
    if payload.company_id is None:
        # explicit null means clear current company
        await clear_user_company(driver, user_id)
    else:
        # set_user_company expects a company_id; if empty string treat as clear
        if payload.company_id == "":
            await clear_user_company(driver, user_id)
        else:
            res = await set_user_company(driver, user_id, payload.company_id, payload.job_title)
            if res is None:
                raise HTTPException(status_code=404, detail="Company not found")
            company = res.get("company")
            job_title = res.get("job_title")

    # Sync base user node/profile in Neo4j from current Postgres state.
    sync_repo = UserProfileSyncRepository(db, driver)
    await sync_repo.upsert_from_auth(
        user_id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        phone_number=db_user.phone_number,
    )

    # Refresh graph state if we didn't get company/job from set_user_company
    if company is None and job_title is None:
        graph = await get_user_with_company(driver, user_id)
        company = graph.get("company") if graph else None
        job_title = graph.get("job_title") if graph else None

    result = _public_user_dict(db_user)
    result["company"] = company
    result["job_title"] = job_title
    return result
