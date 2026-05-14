"""add documents column

Revision ID: a8b9c0d1e2f3
Revises: 76f7a8b9c0d1
Create Date: 2026-05-14 12:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a8b9c0d1e2f3'
down_revision: Union[str, Sequence[str], None] = '76f7a8b9c0d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add documents column to properties table
    op.add_column('properties', sa.Column('documents', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=True))

def downgrade() -> None:
    op.drop_column('properties', 'documents')
