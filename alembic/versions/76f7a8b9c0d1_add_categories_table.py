"""add_categories_table

Revision ID: 76f7a8b9c0d1
Revises: e2ad2876ced4
Create Date: 2026-05-13 17:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76f7a8b9c0d1'
down_revision: Union[str, Sequence[str], None] = 'e2ad2876ced4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'categories' not in tables:
        op.create_table('categories',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
        op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=True)
        
        # SEED: Transfer existing categories from properties table to new categories table
        if 'properties' in tables:
            print("Seeding categories from existing properties...")
            # Get distinct categories from properties
            res = conn.execute(sa.text("SELECT DISTINCT category FROM properties WHERE category IS NOT NULL"))
            categories = [row[0] for row in res if row[0]]
            
            for cat_name in categories:
                # Check if it already exists (safety)
                exists = conn.execute(sa.text("SELECT id FROM categories WHERE name = :name"), {"name": cat_name}).fetchone()
                if not exists:
                    conn.execute(sa.text("INSERT INTO categories (name) VALUES (:name)"), {"name": cat_name})


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')
