"""Merge custom_cats and picture_url branches

Revision ID: 45e7cdb613bc
Revises: 20260203_custom_cats, 20260210_add_picture_url
Create Date: 2026-02-11 22:17:44.952641

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45e7cdb613bc'
down_revision = ('20260203_custom_cats', '20260210_add_picture_url')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
