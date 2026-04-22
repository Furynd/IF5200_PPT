"""compatibility_shim

Revision ID: b37e9b85722c
Revises: 626d698eb693
Create Date: 2026-04-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b37e9b85722c'
down_revision: Union[str, Sequence[str], None] = '626d698eb693'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass