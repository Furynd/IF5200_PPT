"""add_connection_requests_table

Revision ID: f2a1c9d7b4e8
Revises: c1d4a9e21f30
Create Date: 2026-05-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2a1c9d7b4e8'
down_revision: Union[str, Sequence[str], None] = 'c1d4a9e21f30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'connection_requests',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('from_user_id', sa.String(), nullable=False),
        sa.Column('to_user_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('responded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['from_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['to_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_connection_requests_from_user_id', 'connection_requests', ['from_user_id'], unique=False)
    op.create_index('ix_connection_requests_to_user_id', 'connection_requests', ['to_user_id'], unique=False)
    op.create_index('ix_connection_requests_status', 'connection_requests', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_connection_requests_status', table_name='connection_requests')
    op.drop_index('ix_connection_requests_to_user_id', table_name='connection_requests')
    op.drop_index('ix_connection_requests_from_user_id', table_name='connection_requests')
    op.drop_table('connection_requests')
