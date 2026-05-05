import io
import json
from types import SimpleNamespace

import pytest

from backend.app.services import referral_delivery


class DummyUploadFile:
    def __init__(self, filename, content_type, data):
        self.filename = filename
        self.content_type = content_type
        self.file = io.BytesIO(data)


def test_normalize_phone_number_handles_indonesian_formats():
    assert referral_delivery.normalize_phone_number("0812-345-678") == "62812345678"
    assert referral_delivery.normalize_phone_number("+62812345678") == "62812345678"
    assert referral_delivery.normalize_phone_number("") == ""


def test_build_referral_message_includes_cv_link_and_note():
    message = referral_delivery.build_referral_message(
        requester_name="Alice",
        referee_name="Budi",
        company_name="PT Contoh",
        cv_url="https://example.com/cv.pdf",
        message="Mohon bantuannya ya",
    )

    assert "Alice" in message
    assert "Budi" in message
    assert "PT Contoh" in message
    assert "https://example.com/cv.pdf" in message
    assert "Mohon bantuannya ya" in message


def test_send_fonnte_message_serializes_payload(monkeypatch):
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps({"status": True, "message": "sent"}).encode("utf-8")

    def fake_urlopen(request, timeout=30):
        captured["url"] = request.full_url
        captured["body"] = request.data.decode("utf-8")
        captured["headers"] = dict(request.headers)
        return FakeResponse()

    monkeypatch.setenv("FONNTE_API_KEY", "test-key")
    monkeypatch.setenv("FONNTE_SENDER", "Referly")
    monkeypatch.setattr(referral_delivery.urllib.request, "urlopen", fake_urlopen)

    result = referral_delivery.send_fonnte_message("62812345678", "Halo")

    assert captured["url"] == "https://api.fonnte.com/send"
    assert "target=62812345678" in captured["body"]
    assert "message=Halo" in captured["body"]
    assert "sender=Referly" in captured["body"]
    assert result["status"] is True


def test_upload_cv_to_supabase_builds_expected_object_path(monkeypatch):
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"{}"

    def fake_urlopen(request, timeout=30):
        captured["url"] = request.full_url
        captured["body"] = request.data
        captured["headers"] = dict(request.headers)
        return FakeResponse()

    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key")
    monkeypatch.setenv("SUPABASE_STORAGE_BUCKET", "referral-cv")
    monkeypatch.setattr(referral_delivery.urllib.request, "urlopen", fake_urlopen)

    upload = DummyUploadFile("CV Final.pdf", "application/pdf", b"pdf-bytes")
    object_path, public_url = referral_delivery.upload_cv_to_supabase(
        upload,
        requester_id="requester-1",
        referee_id="referee-1",
        company_id="company-1",
    )

    assert object_path.startswith("referrals/requester-1/company-1/referee-1/")
    assert public_url == "https://example.supabase.co/storage/v1/object/public/referral-cv/" + object_path.replace(" ", "%20")
    assert captured["url"].startswith("https://example.supabase.co/storage/v1/object/referral-cv/")
    assert captured["headers"]["Authorization"] == "Bearer service-role-key"


def test_send_email_message_serializes_smtp_payload(monkeypatch):
    captured = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout=30):
            captured["host"] = host
            captured["port"] = port
            captured["timeout"] = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def starttls(self):
            captured["starttls"] = True

        def login(self, username, password):
            captured["login"] = (username, password)

        def send_message(self, message):
            captured["to"] = message["To"]
            captured["from"] = message["From"]
            captured["subject"] = message["Subject"]
            captured["body"] = message.get_content()

    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USERNAME", "mailer@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "noreply@example.com")
    monkeypatch.setenv("SMTP_FROM_NAME", "Referly")
    monkeypatch.setenv("SMTP_USE_TLS", "true")
    monkeypatch.setattr(referral_delivery.smtplib, "SMTP", FakeSMTP)

    result = referral_delivery.send_email_message(
        "referee@example.com",
        subject="Referral untuk PT Contoh",
        message="Halo",
    )

    assert captured["host"] == "smtp.example.com"
    assert captured["port"] == 587
    assert captured["starttls"] is True
    assert captured["login"] == ("mailer@example.com", "secret")
    assert captured["to"] == "referee@example.com"
    assert captured["from"] == "Referly <noreply@example.com>"
    assert captured["subject"] == "Referral untuk PT Contoh"
    assert "Halo" in captured["body"]
    assert result["channel"] == "email"


def test_send_referral_message_falls_back_to_email_when_phone_is_empty(monkeypatch):
    captured = {}

    def fake_send_email_message(target_email, subject, message):
        captured["channel"] = "email"
        captured["target"] = target_email
        captured["subject"] = subject
        captured["message"] = message
        return {"status": True}

    def fake_send_fonnte_message(*args, **kwargs):
        raise AssertionError("WhatsApp path should not be used when phone number is empty")

    monkeypatch.setattr(referral_delivery, "send_email_message", fake_send_email_message)
    monkeypatch.setattr(referral_delivery, "send_fonnte_message", fake_send_fonnte_message)

    result = referral_delivery.send_referral_message(
        referee_phone_number=None,
        referee_email="ref@example.com",
        subject="Referral untuk PT Contoh",
        message="referral body",
    )

    assert captured["channel"] == "email"
    assert captured["target"] == "ref@example.com"
    assert captured["subject"] == "Referral untuk PT Contoh"
    assert result["channel"] == "email"
    assert result["target"] == "ref@example.com"
