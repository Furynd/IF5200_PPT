import os
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.schema import User

router = APIRouter(prefix="/auth", tags=["Autentikasi & Profil"])

# ==========================================
# 1. ENDPOINT DEV-ONLY (MOCK LOGIN)
# ==========================================
@router.post("/dev-login")
def dev_login(email: str):
    """
    HANYA UNTUK DEVELOPMENT LOKAL.
    Digunakan oleh Dev B (Frontend) untuk bypass Supabase Cloud saat koding di localhost.
    """
    # PENGAMAN MUTLAK: Pastikan endpoint ini mati saat di-deploy ke Railway/Production
    if os.getenv("ENVIRONMENT") == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Forbidden: Dev endpoint is disabled in production."
        )

    # Gunakan UUID statis untuk testing, atau generate baru
    fake_uuid = "123e4567-e89b-12d3-a456-426614174000" 
    
    payload = {
        "aud": "authenticated",
        "sub": fake_uuid,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    
    secret = os.getenv("SUPABASE_JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="SUPABASE_JWT_SECRET tidak disetel di .env")

    token = jwt.encode(payload, secret, algorithm="HS256")
    return {"access_token": token, "user": {"id": fake_uuid, "email": email}}


# ==========================================
# 2. ENDPOINT PRODUKSI (SYNC & ME)
# ==========================================
class UserSyncRequest(BaseModel):
    email: str

@router.post("/sync")
def sync_user_profile(
    user_data: UserSyncRequest, 
    db: Session = Depends(get_db), 
    user_id: str = Depends(get_current_user_id)
):
    """
    Menyimpan profil user ke database lokal setelah berhasil login.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        new_user = User(id=user_id, email=user_data.email)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "Profil lokal berhasil dibuat", "user": new_user}
        
    return {"message": "Profil lokal sudah ada", "user": user}

@router.get("/me")
def get_my_profile(
    db: Session = Depends(get_db), 
    user_id: str = Depends(get_current_user_id)
):
    """
    Mengambil data profil. Wajib melampirkan Bearer Token.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Profil tidak ditemukan")
    
    return user