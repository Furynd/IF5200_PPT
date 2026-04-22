"""backfill_legacy_dev_password_hashes

Revision ID: c1d4a9e21f30
Revises: 8f3e0c1a7d2b
Create Date: 2026-04-22 00:00:00.000000

"""
from typing import Sequence, Union
import hashlib
import os

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d4a9e21f30'
down_revision: Union[str, Sequence[str], None] = '8f3e0c1a7d2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _hash_password(password: str) -> str:
    pepper = os.getenv("DEV_AUTH_PASSWORD_PEPPER", "referly-dev-pepper")
    return hashlib.sha256(f"{pepper}:{password}".encode("utf-8")).hexdigest()


def upgrade() -> None:
    """
    Backfill password_hash for legacy dev users that were created before
    password validation was introduced in /auth/dev-login.
    """
    bind = op.get_bind()
    default_password = os.getenv("DEV_LEGACY_BACKFILL_PASSWORD", "dev12345")
    hashed = _hash_password(default_password)

    bind.execute(
        sa.text(
            """
            UPDATE users
            SET password_hash = :hashed
            WHERE password_hash IS NULL OR password_hash = ''
            """
        ),
        {"hashed": hashed},
    )


def downgrade() -> None:
    # Best-effort rollback for rows that were backfilled with current env defaults.
    bind = op.get_bind()
    default_password = os.getenv("DEV_LEGACY_BACKFILL_PASSWORD", "dev12345")
    hashed = _hash_password(default_password)

    bind.execute(
        sa.text(
            """
            UPDATE users
            SET password_hash = NULL
            WHERE password_hash = :hashed
            """
        ),
        {"hashed": hashed},
    )