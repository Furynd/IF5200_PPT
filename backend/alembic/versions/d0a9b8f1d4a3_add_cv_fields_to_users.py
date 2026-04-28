"""add_cv_fields_to_users

Revision ID: d0a9b8f1d4a3
Revises: 8f3e0c1a7d2b
Create Date: 2026-04-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0a9b8f1d4a3'
down_revision: Union[str, Sequence[str], None] = '8f3e0c1a7d2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('cv_filename', sa.String(), nullable=True))
    op.add_column('users', sa.Column('cv_url', sa.String(), nullable=True))
    op.add_column('users', sa.Column('cv_uploaded_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'cv_uploaded_at')
    op.drop_column('users', 'cv_url')
    op.drop_column('users', 'cv_filename')
