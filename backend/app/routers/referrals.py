from fastapi import APIRouter, Depends, Form, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from neo4j import AsyncDriver

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.db.neo4j import get_neo4j_driver
from app.models.schema import Company, ReferralRequest, User
from app.services.referral_delivery import build_referral_message, send_referral_message, normalize_phone_number
from app.services import company_graph

router = APIRouter()


class ReferralSendResponse(BaseModel):
    referral_id: str
    status: str
    message_channel: str
    cv_url: str
    target_contact: str
    delivery_response: dict


@router.post("/referrals", response_model=ReferralSendResponse)
async def send_referral(
    company_id: str = Form(...),
    referee_user_id: str = Form(...),
    message: str | None = Form(default=None),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    driver: AsyncDriver = Depends(get_neo4j_driver),
):
    requester = db.query(User).filter(User.id == user_id).first()
    if requester is None:
        raise HTTPException(status_code=404, detail="Requester not found")

    referee = db.query(User).filter(User.id == referee_user_id).first()
    if referee is None:
        raise HTTPException(status_code=404, detail="Referee not found")

    if not referee.is_open_to_refer:
        raise HTTPException(status_code=400, detail="Referee is not open to referrals")

    # Try PostgreSQL first, then fall back to Neo4j
    company = db.query(Company).filter(Company.id == company_id).first()
    company_name = None
    
    if company is None:
        # Company not in PostgreSQL, try Neo4j
        neo4j_company = await company_graph.get_company(driver, company_id)
        if neo4j_company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        company_name = neo4j_company["name"]
        # Create company in PostgreSQL for future referrals
        company = Company(id=company_id, name=neo4j_company["name"], industry=neo4j_company.get("industry"))
        db.add(company)
        db.commit()
        db.refresh(company)
    else:
        company_name = company.name

    normalized_phone = normalize_phone_number(referee.phone_number or "")
    referee_email = (referee.email or "").strip()
    if not normalized_phone and not referee_email:
        raise HTTPException(status_code=400, detail="Referee phone number and email are not available")

    cv_url = (requester.cv_url or "").strip()
    if not cv_url:
        raise HTTPException(
            status_code=400,
            detail="CV belum diunggah di profil. Silakan upload CV di halaman profile terlebih dahulu.",
        )

    referral_message = build_referral_message(
        requester_name=requester.full_name or requester.email,
        referee_name=referee.full_name or referee.email,
        company_name=company_name,
        cv_url=cv_url,
        message=message,
    )

    delivery = send_referral_message(
        referee_phone_number=normalized_phone,
        referee_email=referee_email,
        subject=f"Referral untuk {company_name}",
        message=referral_message,
    )
    message_channel = delivery["channel"]
    target_contact = delivery["target"]
    delivery_response = delivery["response"]

    referral = ReferralRequest(
        requester_id=requester.id,
        referee_id=referee.id,
        company_id=company.id if company else None,
        status="sent",
        message_channel=message_channel,
    )
    db.add(referral)
    db.commit()
    db.refresh(referral)

    return ReferralSendResponse(
        referral_id=referral.id,
        status=referral.status,
        message_channel=referral.message_channel,
        cv_url=cv_url,
        target_contact=target_contact,
        delivery_response=delivery_response,
    )
