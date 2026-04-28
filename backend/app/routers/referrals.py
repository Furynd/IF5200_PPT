from fastapi import APIRouter, Depends, Form, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.schema import Company, ReferralRequest, User
from app.services.referral_delivery import (
    build_referral_message,
    normalize_phone_number,
    send_fonnte_message,
)

router = APIRouter()


class ReferralSendResponse(BaseModel):
    referral_id: str
    status: str
    message_channel: str
    cv_url: str
    target_phone_number: str
    fonnte_response: dict


@router.post("/referrals", response_model=ReferralSendResponse)
def send_referral(
    company_id: str = Form(...),
    referee_user_id: str = Form(...),
    message: str | None = Form(default=None),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    requester = db.query(User).filter(User.id == user_id).first()
    if requester is None:
        raise HTTPException(status_code=404, detail="Requester not found")

    referee = db.query(User).filter(User.id == referee_user_id).first()
    if referee is None:
        raise HTTPException(status_code=404, detail="Referee not found")

    if not referee.is_open_to_refer:
        raise HTTPException(status_code=400, detail="Referee is not open to referrals")

    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    normalized_phone = normalize_phone_number(referee.phone_number or "")
    if not normalized_phone:
        raise HTTPException(status_code=400, detail="Referee phone number is not available")

    cv_url = (requester.cv_url or "").strip()
    if not cv_url:
        raise HTTPException(
            status_code=400,
            detail="CV belum diunggah di profil. Silakan upload CV di halaman profile terlebih dahulu.",
        )

    referral_message = build_referral_message(
        requester_name=requester.full_name or requester.email,
        referee_name=referee.full_name or referee.email,
        company_name=company.name,
        cv_url=cv_url,
        message=message,
    )

    fonnte_response = send_fonnte_message(normalized_phone, referral_message)

    referral = ReferralRequest(
        requester_id=requester.id,
        referee_id=referee.id,
        company_id=company.id,
        status="sent",
        message_channel="whatsapp",
    )
    db.add(referral)
    db.commit()
    db.refresh(referral)

    return ReferralSendResponse(
        referral_id=referral.id,
        status=referral.status,
        message_channel=referral.message_channel,
        cv_url=cv_url,
        target_phone_number=normalized_phone,
        fonnte_response=fonnte_response,
    )
