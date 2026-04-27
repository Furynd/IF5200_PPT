import os
import logging
import jwt
from typing import Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Skema otorisasi Bearer Token untuk Swagger UI
security = HTTPBearer()

# Dapatkan dari Supabase Dashboard -> Settings -> API -> JWT Secret
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "super_secret_jwt_key_untuk_dev_lokal")
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_JWKS_URL = (
    f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json" if SUPABASE_URL else ""
)

_jwks_client: jwt.PyJWKClient | None = None


def _decode_hs256(token: str) -> dict:
    return jwt.decode(
        token,
        SUPABASE_JWT_SECRET,
        algorithms=["HS256"],
        audience="authenticated",
    )


def _decode_jwks(token: str) -> dict:
    if not SUPABASE_JWKS_URL:
        raise jwt.PyJWTError("SUPABASE_URL belum dikonfigurasi")

    global _jwks_client
    if _jwks_client is None:
        _jwks_client = jwt.PyJWKClient(SUPABASE_JWKS_URL)

    signing_key = _jwks_client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256", "ES256", "EdDSA"],
        audience="authenticated",
    )

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency untuk memverifikasi JWT dari Supabase.
    Akan mengembalikan user_id (UUID) jika token valid.
    """
    token = credentials.credentials
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "")

        # New Supabase projects can use asymmetric keys. Keep HS256 for legacy projects.
        decoders: list[Callable[[str], dict]]
        if alg == "HS256":
            decoders = [_decode_hs256, _decode_jwks]
        else:
            decoders = [_decode_jwks, _decode_hs256]

        payload = None
        last_error: Exception | None = None
        for decode_token in decoders:
            try:
                payload = decode_token(token)
                break
            except Exception as exc:  # noqa: BLE001
                last_error = exc

        if payload is None and os.getenv("ENVIRONMENT", "development") != "production":
            try:
                payload = jwt.decode(token, options={"verify_signature": False, "verify_aud": False})
                logger.warning("Using unsigned Supabase JWT fallback in non-production mode")
            except Exception as exc:  # noqa: BLE001
                last_error = exc

        if payload is None:
            raise jwt.PyJWTError(str(last_error) if last_error else "Invalid token")
        
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