"""add_basic_profile_fields_to_users

Revision ID: 8f3e0c1a7d2b
Revises: b37e9b85722c
Create Date: 2026-04-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f3e0c1a7d2b'
down_revision: Union[str, Sequence[str], None] = 'b37e9b85722c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'phone_number')
    op.drop_column('users', 'full_name')