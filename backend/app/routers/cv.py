"""
CV skill extraction endpoint.

POST /api/cv/extract-skills
    - Accepts plain text (JSON body) or a PDF file upload (multipart).
    - Fetches current Skill nodes from Neo4j at request time — no hardcoded list.
    - Returns matched skills with score and match_type.
"""

import io
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from neo4j import AsyncDriver

from app.db.neo4j import get_neo4j_driver
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.schema import User
from app.services.skill_extractor import (
    MatchedSkill,
    extract_and_store_user_skills,
    extract_skills,
    fetch_skills,
)
from app.services.referral_delivery import upload_user_cv_to_supabase
from sqlalchemy.orm import Session

router = APIRouter()

_MAX_TEXT_BYTES = 500_000  # ~500 KB plain text cap


class CVTextRequest(BaseModel):
    cv_text: str


class ExtractSkillsResponse(BaseModel):
    matched_count: int
    skills: list[MatchedSkill]


def _extract_pdf_text_from_raw(raw: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader
        except ImportError as exc:
            raise HTTPException(status_code=503, detail="PDF parsing dependency is not installed") from exc

    reader = PdfReader(io.BytesIO(raw))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _is_pdf_upload(file: UploadFile) -> bool:
    filename = (file.filename or "").lower()
    return file.content_type in ("application/pdf", "application/octet-stream") or filename.endswith(".pdf")


@router.post("/cv/extract-skills", response_model=ExtractSkillsResponse)
async def extract_skills_from_text(
    body: CVTextRequest,
    driver: AsyncDriver = Depends(get_neo4j_driver),
):
    """Extract skills from plain CV text."""
    if not body.cv_text.strip():
        raise HTTPException(status_code=422, detail="cv_text must not be empty")

    db_skills = await fetch_skills(driver)
    matched = extract_skills(body.cv_text, db_skills)
    return ExtractSkillsResponse(matched_count=len(matched), skills=matched)


@router.post("/cv/extract-skills/pdf", response_model=ExtractSkillsResponse)
async def extract_skills_from_pdf(
    file: UploadFile = File(...),
    driver: AsyncDriver = Depends(get_neo4j_driver),
):
    """Extract skills from an uploaded PDF CV."""
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Only PDF files are accepted")

    raw = await file.read()
    if len(raw) > _MAX_TEXT_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 500 KB)")

    try:
        cv_text = _extract_pdf_text_from_raw(raw)
    except Exception:
        raise HTTPException(status_code=422, detail="Could not parse PDF")

    if not cv_text.strip():
        raise HTTPException(status_code=422, detail="No extractable text found in PDF")

    db_skills = await fetch_skills(driver)
    matched = extract_skills(cv_text, db_skills)
    return ExtractSkillsResponse(matched_count=len(matched), skills=matched)


@router.post("/cv/upload")
async def upload_user_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    driver: AsyncDriver = Depends(get_neo4j_driver),
    user_id: str = Depends(get_current_user_id),
):
    # Upload to Supabase Storage
    object_path, public_url, size_bytes = upload_user_cv_to_supabase(file, user_id=user_id)

    # Persist to users table
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.cv_filename = object_path
    user.cv_url = public_url
    user.cv_uploaded_at = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)

    if _is_pdf_upload(file):
        try:
            file.file.seek(0)
            raw = file.file.read()
            if raw:
                cv_text = _extract_pdf_text_from_raw(raw)
                if cv_text.strip():
                    await extract_and_store_user_skills(driver, user_id, cv_text)
        except Exception:
            pass

    return {
        "filename": object_path,
        "url": public_url,
        "size_bytes": size_bytes,
        "uploaded_at": user.cv_uploaded_at.isoformat() if user.cv_uploaded_at else None,
    }


@router.get("/cv/user")
def get_my_cv(db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.cv_filename:
        return None
    return {
        "filename": user.cv_filename,
        "url": user.cv_url,
        "uploaded_at": user.cv_uploaded_at.isoformat() if user.cv_uploaded_at else None,
    }
