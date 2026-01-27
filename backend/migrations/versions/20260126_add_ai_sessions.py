# =============================================================================
# Digital Finance Tracker - AI Session Tables Migration
# PURPOSE: Add tables for AI session management (replaces in-memory storage)
# =============================================================================
"""
Add AI session tables: ai_sessions, pending_actions, user_learnings

Revision ID: 20260126_add_ai_sessions
Revises: b2c3d4e5_add_budgets
Create Date: 2026-01-26

These tables replace in-memory storage to prevent data loss on restart:
- ai_sessions: Chat conversation state per user
- pending_actions: Actions awaiting user confirmation
- user_learnings: Merchant → category corrections for personalized AI
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260126_add_ai_sessions"
down_revision = "b2c3d4e5_add_budgets"
branch_labels = None
depends_on = None


def upgrade():
    """Create AI session tables."""

    # ==========================================================================
    # AI SESSIONS TABLE
    # ==========================================================================
    op.create_table(
        "ai_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "conversation_history",
            postgresql.JSONB,
            nullable=False,
            server_default="[]",
        ),
        sa.Column("last_intent", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now() + interval '30 minutes'"),
        ),
    )

    # Indexes for ai_sessions
    op.create_index(
        "idx_ai_sessions_user_active",
        "ai_sessions",
        ["user_id", "is_active"],
    )
    op.create_index(
        "idx_ai_sessions_expires",
        "ai_sessions",
        ["expires_at"],
    )

    # ==========================================================================
    # PENDING ACTIONS TABLE
    # ==========================================================================
    op.create_table(
        "pending_actions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai_sessions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column(
            "action_data",
            postgresql.JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now() + interval '24 hours'"),
        ),
    )

    # Indexes for pending_actions
    op.create_index(
        "idx_pending_actions_user_status",
        "pending_actions",
        ["user_id", "status"],
    )
    op.create_index(
        "idx_pending_actions_expires",
        "pending_actions",
        ["expires_at"],
    )

    # ==========================================================================
    # USER LEARNINGS TABLE
    # ==========================================================================
    op.create_table(
        "user_learnings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("merchant_normalized", sa.String(255), nullable=False),
        sa.Column("category_name", sa.String(100), nullable=False),
        sa.Column("correction_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("original_category", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Unique index for user+merchant lookup
    op.create_index(
        "idx_user_learnings_lookup",
        "user_learnings",
        ["user_id", "merchant_normalized"],
        unique=True,
    )


def downgrade():
    """Remove AI session tables."""

    # Drop indexes first
    op.drop_index("idx_user_learnings_lookup", table_name="user_learnings")
    op.drop_index("idx_pending_actions_expires", table_name="pending_actions")
    op.drop_index("idx_pending_actions_user_status", table_name="pending_actions")
    op.drop_index("idx_ai_sessions_expires", table_name="ai_sessions")
    op.drop_index("idx_ai_sessions_user_active", table_name="ai_sessions")

    # Drop tables
    op.drop_table("user_learnings")
    op.drop_table("pending_actions")
    op.drop_table("ai_sessions")
