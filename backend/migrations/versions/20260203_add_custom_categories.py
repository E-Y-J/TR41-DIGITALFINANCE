# =============================================================================
# Digital Finance Tracker - Add Custom Categories Migration
# PURPOSE: Add user_id column to categories table for custom user categories
# =============================================================================
"""Add user_id to categories for custom categories support

Revision ID: 20260203_add_custom_categories
Revises: b7c67e304714
Create Date: 2026-02-03

This migration adds:
- user_id column to categories table (nullable, references users)
- Updates unique constraint to allow same name per user
- Removes global unique constraint on name

Custom categories allow users to create their own categories that
integrate with the AI learning system.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '20260203_custom_cats'
down_revision = 'b7c67e304714'
branch_labels = None
depends_on = None


def upgrade():
    """Add user_id column and update constraints."""
    # Add user_id column (nullable for system categories)
    op.add_column(
        'categories',
        sa.Column(
            'user_id',
            postgresql.UUID(as_uuid=True),
            nullable=True,
        )
    )

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_categories_user_id',
        'categories',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Drop the old unique index on name
    # The actual index is named 'ix_categories_name' based on DB schema
    op.drop_index('ix_categories_name', table_name='categories')

    # Create new unique constraint: name + user_id
    # This allows same name for different users, but unique per user
    op.create_unique_constraint(
        'uq_category_name_per_user',
        'categories',
        ['name', 'user_id']
    )

    # Create index on user_id for faster lookups
    op.create_index(
        'idx_categories_user_id',
        'categories',
        ['user_id'],
        unique=False
    )


def downgrade():
    """Remove user_id column and restore original constraints."""
    # Drop the new constraint
    op.drop_constraint('uq_category_name_per_user', 'categories', type_='unique')

    # Drop the index
    op.drop_index('idx_categories_user_id', table_name='categories')

    # Drop the foreign key
    op.drop_constraint('fk_categories_user_id', 'categories', type_='foreignkey')

    # Drop the user_id column
    op.drop_column('categories', 'user_id')

    # Restore original unique index on name
    op.create_index(
        'ix_categories_name',
        'categories',
        ['name'],
        unique=True
    )
