import io

import pytest

from app.routers import cv


class DummyUploadFile:
    def __init__(self, filename: str, content_type: str, data: bytes):
        self.filename = filename
        self.content_type = content_type
        self.file = io.BytesIO(data)


class DummyUser:
    def __init__(self, user_id: str):
        self.id = user_id
        self.cv_filename = None
        self.cv_url = None
        self.cv_uploaded_at = None


class DummyQuery:
    def __init__(self, user: DummyUser):
        self._user = user

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self._user


class DummyDB:
    def __init__(self, user: DummyUser):
        self._user = user

    def query(self, _model):
        return DummyQuery(self._user)

    def add(self, _obj):
        return None

    def commit(self):
        return None

    def refresh(self, _obj):
        return None


@pytest.mark.asyncio
async def test_upload_user_cv_extracts_and_stores_skills(monkeypatch):
    user = DummyUser("user-123")
    db = DummyDB(user)
    upload = DummyUploadFile("resume.pdf", "application/pdf", b"pdf-bytes")
    captured = {}

    def fake_upload(file, *, user_id):
        assert user_id == "user-123"
        assert file.file.read() == b"pdf-bytes"
        file.file.seek(0)
        return "users/user-123/resume.pdf", "https://example.test/resume.pdf", 9

    async def fake_extract_and_store_user_skills(driver, user_id, cv_text):
        captured["driver"] = driver
        captured["user_id"] = user_id
        captured["cv_text"] = cv_text
        return []

    monkeypatch.setattr(cv, "upload_user_cv_to_supabase", fake_upload)
    monkeypatch.setattr(cv, "_is_pdf_upload", lambda _file: True)
    monkeypatch.setattr(cv, "_extract_pdf_text_from_raw", lambda _raw: "Python\nFastAPI\nNeo4j")
    monkeypatch.setattr(cv, "extract_and_store_user_skills", fake_extract_and_store_user_skills)

    result = await cv.upload_user_cv(
        file=upload,
        db=db,
        driver=object(),
        user_id="user-123",
    )

    assert result["filename"] == "users/user-123/resume.pdf"
    assert result["url"] == "https://example.test/resume.pdf"
    assert result["size_bytes"] == 9
    assert captured["user_id"] == "user-123"
    assert captured["cv_text"] == "Python\nFastAPI\nNeo4j"