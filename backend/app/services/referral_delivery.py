from __future__ import annotations

import json
import mimetypes
import os
import re
import smtplib
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from email.message import EmailMessage
from email.utils import formataddr

from fastapi import HTTPException, UploadFile
from datetime import datetime


@dataclass(frozen=True)
class SupabaseStorageConfig:
    url: str
    service_role_key: str
    bucket: str


@dataclass(frozen=True)
class FonnteConfig:
    api_key: str
    sender: str | None


@dataclass(frozen=True)
class EmailConfig:
    host: str
    port: int
    username: str | None
    password: str | None
    from_email: str
    from_name: str | None
    use_tls: bool


_PHONE_KEEP_DIGITS = re.compile(r"\D+")


def _clean_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def get_supabase_storage_config() -> SupabaseStorageConfig:
    url = _clean_env("SUPABASE_URL").rstrip("/")
    service_role_key = _clean_env("SUPABASE_SERVICE_ROLE_KEY")
    bucket = _clean_env("SUPABASE_STORAGE_BUCKET", "referral-cv")

    if not url or not service_role_key:
        raise HTTPException(
            status_code=503,
            detail="Supabase Storage belum dikonfigurasi. Set SUPABASE_URL dan SUPABASE_SERVICE_ROLE_KEY.",
        )

    return SupabaseStorageConfig(url=url, service_role_key=service_role_key, bucket=bucket)


def get_fonnte_config() -> FonnteConfig:
    api_key = _clean_env("FONNTE_API_KEY")
    sender = _clean_env("FONNTE_SENDER") or None

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Fonnte belum dikonfigurasi. Set FONNTE_API_KEY.",
        )

    return FonnteConfig(api_key=api_key, sender=sender)


def get_email_config() -> EmailConfig:
    host = _clean_env("SMTP_HOST")
    from_email = _clean_env("SMTP_FROM_EMAIL")

    if not host or not from_email:
        raise HTTPException(
            status_code=503,
            detail="Fallback email belum dikonfigurasi. Set SMTP_HOST dan SMTP_FROM_EMAIL.",
        )

    port_raw = _clean_env("SMTP_PORT", "587")
    try:
        port = int(port_raw)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail="SMTP_PORT harus berupa angka.") from exc

    username = _clean_env("SMTP_USERNAME") or None
    password = _clean_env("SMTP_PASSWORD") or None
    from_name = _clean_env("SMTP_FROM_NAME") or None
    use_tls = _clean_env("SMTP_USE_TLS", "true").lower() not in {"0", "false", "no"}

    return EmailConfig(
        host=host,
        port=port,
        username=username,
        password=password,
        from_email=from_email,
        from_name=from_name,
        use_tls=use_tls,
    )


def normalize_phone_number(phone_number: str) -> str:
    digits = _PHONE_KEEP_DIGITS.sub("", phone_number or "")
    if not digits:
        return ""

    if digits.startswith("0"):
        return f"62{digits[1:]}"
    if digits.startswith("8"):
        return f"62{digits}"
    return digits


def _safe_filename(filename: str | None) -> str:
    if not filename:
        return "cv.pdf"
    name = Path(filename).name.strip()
    return name or "cv.pdf"


def upload_cv_to_supabase(
    file: UploadFile,
    *,
    requester_id: str,
    referee_id: str,
    company_id: str,
) -> tuple[str, str]:
    config = get_supabase_storage_config()

    raw = file.file.read()
    if not raw:
        raise HTTPException(status_code=422, detail="CV file is empty")

    safe_filename = _safe_filename(file.filename)
    object_path = (
        f"referrals/{requester_id}/{company_id}/{referee_id}/"
        f"{Path(safe_filename).stem}-{company_id[:8]}{Path(safe_filename).suffix or '.pdf'}"
    )
    quoted_path = urllib.parse.quote(object_path, safe="/-_.")

    content_type = file.content_type or mimetypes.guess_type(safe_filename)[0] or "application/octet-stream"
    upload_url = f"{config.url}/storage/v1/object/{config.bucket}/{quoted_path}?upsert=true"

    request = urllib.request.Request(
        upload_url,
        data=raw,
        method="POST",
        headers={
            "Authorization": f"Bearer {config.service_role_key}",
            "Content-Type": content_type,
            "x-upsert": "true",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response.read()
    except Exception as exc:  # pragma: no cover - surfaced as HTTP error for the caller
        raise HTTPException(
            status_code=502,
            detail=f"Gagal mengunggah CV ke Supabase Storage: {exc}",
        ) from exc

    public_url = f"{config.url}/storage/v1/object/public/{config.bucket}/{quoted_path}"
    return object_path, public_url


def upload_user_cv_to_supabase(
    file: UploadFile,
    *,
    user_id: str,
) -> tuple[str, str, int]:
    """Upload a user's CV to Supabase Storage and return (object_path, public_url, size_bytes)."""
    config = get_supabase_storage_config()

    # If UploadFile comes from FastAPI async path, it may not be read yet.
    try:
        raw = file.file.read()
    except Exception:
        # Fallback: try awaitable read not supported here
        raise HTTPException(status_code=422, detail="Could not read uploaded file")

    if not raw:
        raise HTTPException(status_code=422, detail="CV file is empty")

    safe_filename = _safe_filename(file.filename)
    object_path = f"users/{user_id}/{Path(safe_filename).stem}{Path(safe_filename).suffix or '.pdf'}"
    quoted_path = urllib.parse.quote(object_path, safe="/-_.")

    content_type = file.content_type or mimetypes.guess_type(safe_filename)[0] or "application/octet-stream"
    upload_url = f"{config.url}/storage/v1/object/{config.bucket}/{quoted_path}?upsert=true"

    request = urllib.request.Request(
        upload_url,
        data=raw,
        method="POST",
        headers={
            "Authorization": f"Bearer {config.service_role_key}",
            "Content-Type": content_type,
            "x-upsert": "true",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response.read()
    except Exception as exc:  # pragma: no cover - surfaced as HTTP error for the caller
        raise HTTPException(
            status_code=502,
            detail=f"Gagal mengunggah CV ke Supabase Storage: {exc}",
        ) from exc

    public_url = f"{config.url}/storage/v1/object/public/{config.bucket}/{quoted_path}"
    return object_path, public_url, len(raw)


def build_referral_message(
    *,
    requester_name: str,
    referee_name: str,
    company_name: str,
    cv_url: str,
    message: str | None = None,
) -> str:
    lines = [
        f"Halo {referee_name}, ada referral baru dari {requester_name} untuk {company_name}.",
        f"Link CV: {cv_url}",
    ]

    extra_message = (message or "").strip()
    if extra_message:
        lines.extend(["", "Catatan tambahan:", extra_message])

    lines.append("")
    lines.append("Dikirim lewat Referly.")
    return "\n".join(lines)


def send_fonnte_message(target_phone_number: str, message: str) -> dict[str, Any]:
    config = get_fonnte_config()
    payload: dict[str, str] = {
        "target": target_phone_number,
        "message": message,
    }
    if config.sender:
        payload["sender"] = config.sender

    encoded_payload = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(
        "https://api.fonnte.com/send",
        data=encoded_payload,
        method="POST",
        headers={
            "Authorization": config.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return {"raw": body}
    except Exception as exc:  # pragma: no cover - surfaced as HTTP error for the caller
        raise HTTPException(
            status_code=502,
            detail=f"Gagal mengirim pesan Fonnte: {exc}",
        ) from exc


def send_email_message(target_email: str, subject: str, message: str) -> dict[str, Any]:
    config = get_email_config()

    email_message = EmailMessage()
    email_message["To"] = target_email
    email_message["From"] = formataddr((config.from_name, config.from_email)) if config.from_name else config.from_email
    email_message["Subject"] = subject
    email_message.set_content(message)

    try:
        with smtplib.SMTP(config.host, config.port, timeout=30) as client:
            if config.use_tls:
                client.starttls()
            if config.username and config.password:
                client.login(config.username, config.password)
            client.send_message(email_message)
    except Exception as exc:  # pragma: no cover - surfaced as HTTP error for the caller
        raise HTTPException(
            status_code=502,
            detail=f"Gagal mengirim email referral: {exc}",
        ) from exc

    return {
        "status": True,
        "target": target_email,
        "subject": subject,
        "channel": "email",
    }


def send_referral_message(
    *,
    referee_phone_number: str | None,
    referee_email: str | None,
    subject: str,
    message: str,
) -> dict[str, Any]:
    normalized_phone = normalize_phone_number(referee_phone_number or "")
    normalized_email = (referee_email or "").strip()

    if normalized_phone:
        return {
            "channel": "whatsapp",
            "target": normalized_phone,
            "response": send_fonnte_message(normalized_phone, message),
        }

    if normalized_email:
        return {
            "channel": "email",
            "target": normalized_email,
            "response": send_email_message(normalized_email, subject=subject, message=message),
        }

    raise HTTPException(status_code=400, detail="Referee phone number and email are not available")
