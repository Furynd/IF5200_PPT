import os
import uuid
import jwt
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.db.neo4j import get_neo4j_driver
from app.core.security import get_current_user_id
from app.models.schema import User
from app.services.user_graph import create_user_node

router = APIRouter(prefix="/auth", tags=["Autentikasi & Profil"])
logger = logging.getLogger(__name__)


class DevLoginRequest(BaseModel):
    email: EmailStr
    password: str


class DevRegisterRequest(BaseModel):
    email: EmailStr
    full_name: str | None = None
    password: str
    phone_number: str | None = None


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _hash_password(password: str) -> str:
    # Dev-only hashing so password is never stored as plain text.
    pepper = os.getenv("DEV_AUTH_PASSWORD_PEPPER", "referly-dev-pepper")
    return hashlib.sha256(f"{pepper}:{password}".encode("utf-8")).hexdigest()


def _verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    return hmac.compare_digest(_hash_password(password), password_hash)


def _public_user(user: User) -> dict:
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
    }

# ==========================================
# 1. ENDPOINT DEV-ONLY (MOCK LOGIN)
# ==========================================
@router.post("/dev-login")
def dev_login(request_data: DevLoginRequest, db: Session = Depends(get_db)):
    """
    HANYA UNTUK DEVELOPMENT LOKAL.
    Digunakan oleh frontend dev untuk bypass Supabase Cloud saat koding di localhost.
    """
    # 1. PENGAMAN PRODUKSI
    if os.getenv("ENVIRONMENT") == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Forbidden: Dev endpoint is disabled in production."
        )

    # Cari user di database lokal
    user = db.query(User).filter(User.email == request_data.email).first()
    if not user or not _verify_password(request_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    
    # Gunakan UUID asli dari database lokal
    token_payload = {
        "aud": "authenticated",
        "sub": user.id, 
        "email": request_data.email,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    
    secret = os.getenv("SUPABASE_JWT_SECRET")
    token = jwt.encode(token_payload, secret, algorithm="HS256")
    return {"access_token": token, "user": _public_user(user)}

@router.post("/dev-register")
async def dev_register(
    request_data: DevRegisterRequest,
    db: Session = Depends(get_db),
    driver = Depends(get_neo4j_driver),
):
    """
    HANYA UNTUK DEVELOPMENT LOKAL.
    Menyimulasikan proses registrasi Supabase. 
    Akan membuat user baru di database lokal dan mengembalikan JWT.
    """
    # 1. PENGAMAN PRODUKSI
    if os.getenv("ENVIRONMENT") == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Forbidden: Dev endpoint is disabled in production."
        )

    # 2. Cek apakah email sudah terdaftar di DB lokal
    existing_user = db.query(User).filter(User.email == request_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    # 3. Buat UUID acak (meniru ID yang biasanya di-generate oleh Supabase Auth)
    new_uuid = str(uuid.uuid4())

    # 4. Simpan ke database PostgreSQL lokal
    new_user = User(
        id=new_uuid,
        email=request_data.email,
        password_hash=_hash_password(request_data.password),
        full_name=_clean_optional_text(request_data.full_name),
        phone_number=_clean_optional_text(request_data.phone_number),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    try:
        await create_user_node(
            driver,
            user_id=new_uuid,
            full_name=new_user.full_name or "",
            phone_number=new_user.phone_number or "",
        )
    except Exception as exc:
        logger.warning("Neo4j user node sync failed for %s: %s", new_uuid, exc)

    # 5. Terbitkan (Mint) JWT
    token_payload = {
        "aud": "authenticated",
        "sub": new_uuid,
        "email": request_data.email,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    
    secret = os.getenv("SUPABASE_JWT_SECRET")
    token = jwt.encode(token_payload, secret, algorithm="HS256")
    
    return {
        "message": "Registrasi lokal berhasil",
        "access_token": token, 
        "user": _public_user(new_user)
    }

# ==========================================
# 2. ENDPOINT PRODUKSI (SYNC & ME)
# ==========================================
class UserSyncRequest(BaseModel):
    email: str
    full_name: str | None = None
    phone_number: str | None = None

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
        new_user = User(
            id=user_id,
            email=user_data.email,
            full_name=_clean_optional_text(user_data.full_name),
            phone_number=_clean_optional_text(user_data.phone_number),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "Profil lokal berhasil dibuat", "user": _public_user(new_user)}

    if user_data.full_name is not None:
        user.full_name = _clean_optional_text(user_data.full_name)
    if user_data.phone_number is not None:
        user.phone_number = _clean_optional_text(user_data.phone_number)
    if user.email != user_data.email:
        user.email = user_data.email

    db.commit()
    db.refresh(user)
        
    return {"message": "Profil lokal sudah ada", "user": _public_user(user)}

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
    
    return _public_user(user)