"""Add budgets table for user spending limits

BUDGET SYSTEM MIGRATION

This migration adds:
1. Budgets table - User-defined spending limits
   - Supports TOTAL budget (overall spending limit)
   - Supports CATEGORY budget (per-category limit)
   - Tracks surplus from previous periods

AI FOUNDATION:
    Budget data enables AI features:
    - BUDGET_WARNING alerts at 70% threshold
    - BUDGET_EXCEEDED alerts when limit reached
    - Spending pattern analysis vs user-defined limits
    - Personalized budget recommendations

BUDGET SPECIFICATIONS:
    - Period options: WEEKLY or MONTHLY
    - Warning threshold: Fixed at 70%
    - No carry over: Budgets reset each period
    - Surplus tracking: Records savings from previous period
    - Soft limit: Warning only, no transaction blocking

Revision ID: add_budgets_table
Revises: add_categories_notifications_alerts
Create Date: 2026-01-15

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "add_budgets_table"
down_revision = "add_categories_notifications_alerts"
branch_labels = None
depends_on = None


def upgrade():
    # =========================================================================
    # CREATE BUDGETS TABLE
    # =========================================================================
    op.create_table(
        "budgets",
        # Primary key
        sa.Column("id", sa.UUID(), nullable=False),
        # Foreign keys
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("category_id", sa.UUID(), nullable=True),  # NULL for total budget
        # Budget configuration
        sa.Column(
            "budget_type",
            sa.Enum("TOTAL", "CATEGORY", name="budget_type_enum", native_enum=False),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "period",
            sa.Enum("WEEKLY", "MONTHLY", name="budget_period_enum", native_enum=False),
            nullable=False,
        ),
        # Surplus tracking
        sa.Column(
            "last_period_surplus",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column("last_period_end", sa.DateTime(timezone=True), nullable=True),
        # Status
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            ondelete="CASCADE",
        ),
        # Unique constraint: One budget per user per category per period
        sa.UniqueConstraint(
            "user_id",
            "category_id",
            "period",
            name="uq_budget_user_category_period",
        ),
    )

    # Create indexes for budgets
    with op.batch_alter_table("budgets", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_budgets_user_id"), ["user_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_budgets_category_id"), ["category_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_budgets_budget_type"), ["budget_type"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_budgets_period"), ["period"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_budgets_is_active"), ["is_active"], unique=False
        )


def downgrade():
    # Drop indexes first
    with op.batch_alter_table("budgets", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_budgets_is_active"))
        batch_op.drop_index(batch_op.f("ix_budgets_period"))
        batch_op.drop_index(batch_op.f("ix_budgets_budget_type"))
        batch_op.drop_index(batch_op.f("ix_budgets_category_id"))
        batch_op.drop_index(batch_op.f("ix_budgets_user_id"))

    # Drop table
    op.drop_table("budgets")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS budget_type_enum")
    op.execute("DROP TYPE IF EXISTS budget_period_enum")
