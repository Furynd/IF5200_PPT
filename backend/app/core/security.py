import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

# Skema otorisasi Bearer Token untuk Swagger UI
security = HTTPBearer()

# Dapatkan dari Supabase Dashboard -> Settings -> API -> JWT Secret
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "super_secret_jwt_key_untuk_dev_lokal")

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency untuk memverifikasi JWT dari Supabase.
    Akan mengembalikan user_id (UUID) jika token valid.
    """
    token = credentials.credentials
    try:
        # Supabase secara default menggunakan algoritma HS256 dan audience "authenticated"
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        
        # 'sub' (subject) di dalam JWT Supabase berisi UUID user
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError("UUID tidak ditemukan di dalam token")
            
        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sudah kedaluwarsa"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kredensial tidak valid",
            headers={"WWW-Authenticate": "Bearer"},
        )