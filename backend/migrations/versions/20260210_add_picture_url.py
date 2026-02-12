# =============================================================================
# Digital Finance Tracker - Add Picture URL Migration
# PURPOSE: Add picture_url column to users table for Auth0 profile pictures
# =============================================================================
"""Add picture_url to users table

Revision ID: 20260210_add_picture_url
Revises: b7c67e304714
Create Date: 2026-02-10

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260210_add_picture_url"
down_revision = "b7c67e304714"
branch_labels = None
depends_on = None


def upgrade():
    """Add picture_url column to users table."""
    op.add_column("users", sa.Column("picture_url", sa.String(512), nullable=True))


def downgrade():
    """Remove picture_url column from users table."""
    op.drop_column("users", "picture_url")
