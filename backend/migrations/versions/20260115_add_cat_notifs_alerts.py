"""Add categories, notifications, and alerts tables - AI Foundation

AI FOUNDATION MIGRATION - Categorization, Notifications & Alerts

This migration adds:
1. Categories table - 11 pre-defined spending categories
2. Notifications table - 6 notification types
3. Alerts table - Financial anomaly alerts (foundation)
4. Updates to transactions table:
   - category_id (FK to categories)
   - ai_confidence (Float)
   - ai_source (Enum: huggingface, gemini, user, keyword)
   - is_user_override (Boolean)
   - original_category_id (FK to categories)

IMPORTANT:
- Categories are seeded after table creation
- Existing transactions keep their legacy 'category' string field
- New transactions should use category_id (FK)
- Alerts are foundation for anomaly detection (detection logic added later)

Revision ID: add_categories_notifications_alerts
Revises: 0ef6d8b45cc5
Create Date: 2026-01-07

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
# In add_categories_notifications_alerts.py
revision = 'add_cat_notifs_alerts'  # <=32 chars
down_revision = '748571261c46'      # points to previous migration
branch_labels = None
depends_on = None


# =============================================================================
# DEFAULT CATEGORIES DATA
# =============================================================================
# These match the DEFAULT_CATEGORIES in app/models/category.py

DEFAULT_CATEGORIES = [
    {
        "id": str(uuid.uuid4()),
        "name": "Food & Dining",
        "description": "Restaurants, groceries, food delivery, coffee shops",
        "category_type": "expense",
        "icon": "utensils",
        "color": "#FF6B6B",
        "display_order": 1,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Transportation",
        "description": "Gas, public transit, ride-sharing, car maintenance",
        "category_type": "expense",
        "icon": "car",
        "color": "#4ECDC4",
        "display_order": 2,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Shopping & Retail",
        "description": "Clothing, electronics, home goods, online shopping",
        "category_type": "expense",
        "icon": "shopping-bag",
        "color": "#45B7D1",
        "display_order": 3,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Entertainment & Recreation",
        "description": "Movies, games, subscriptions, hobbies, sports",
        "category_type": "expense",
        "icon": "gamepad",
        "color": "#96CEB4",
        "display_order": 4,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Healthcare & Medical",
        "description": "Doctor visits, pharmacy, insurance, fitness",
        "category_type": "expense",
        "icon": "heartbeat",
        "color": "#FF8C94",
        "display_order": 5,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Utilities & Services",
        "description": "Electricity, water, internet, phone, rent",
        "category_type": "expense",
        "icon": "bolt",
        "color": "#FFD93D",
        "display_order": 6,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Financial Services",
        "description": "Bank fees, investments, loans, transfers",
        "category_type": "both",
        "icon": "piggy-bank",
        "color": "#6BCB77",
        "display_order": 7,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Income",
        "description": "Salary, freelance, investments, refunds",
        "category_type": "income",
        "icon": "wallet",
        "color": "#4D96FF",
        "display_order": 8,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Government & Legal",
        "description": "Taxes, fees, fines, legal services",
        "category_type": "both",
        "icon": "landmark",
        "color": "#9B59B6",
        "display_order": 9,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Charity & Donations",
        "description": "Charitable giving, donations, tips",
        "category_type": "expense",
        "icon": "hand-holding-heart",
        "color": "#E91E63",
        "display_order": 10,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Unknown",
        "description": "Uncategorized transactions (AI confidence too low)",
        "category_type": "both",
        "icon": "question",
        "color": "#95A5A6",
        "display_order": 99,
    },
]


def upgrade():
    # =========================================================================
    # 1. CREATE CATEGORIES TABLE
    # =========================================================================
    op.create_table(
        "categories",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "category_type",
            sa.Enum(
                "INCOME",
                "EXPENSE",
                "BOTH",
                name="category_type_enum",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("icon", sa.String(length=50), nullable=True),
        sa.Column("color", sa.String(length=7), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for categories
    with op.batch_alter_table("categories", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_categories_name"), ["name"], unique=True)
        batch_op.create_index(
            batch_op.f("ix_categories_category_type"), ["category_type"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_categories_is_active"), ["is_active"], unique=False
        )

    # =========================================================================
    # 2. CREATE NOTIFICATIONS TABLE
    # =========================================================================
    op.create_table(
        "notifications",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "notification_type",
            sa.Enum(
                "DEFAULT",
                "NEW_TRANSACTION",
                "DELETED_TRANSACTION",
                "EDITED_PROFILE",
                "WEEKLY_SUMMARY_READY",
                "CATEGORY_UPDATED",
                name="notification_type_enum",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "UNREAD",
                "READ",
                name="notification_status_enum",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for notifications
    with op.batch_alter_table("notifications", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_notifications_user_id"), ["user_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_notifications_status"), ["status"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_notifications_notification_type"),
            ["notification_type"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_notifications_created_at"), ["created_at"], unique=False
        )
        # Composite index for common query: user's unread notifications
        batch_op.create_index(
            "idx_notification_user_status", ["user_id", "status"], unique=False
        )

    # =========================================================================
    # 3. CREATE ALERTS TABLE (Foundation for anomaly detection)
    # =========================================================================
    op.create_table(
        "alerts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("transaction_id", sa.UUID(), nullable=True),
        sa.Column("category_id", sa.UUID(), nullable=True),
        sa.Column(
            "alert_type",
            sa.Enum(
                "HIGH_SPENDING",
                "LARGE_TRANSACTION",
                "UNUSUAL_CATEGORY",
                "BUDGET_WARNING",
                "BUDGET_EXCEEDED",
                name="alert_type_enum",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.Enum(
                "LOW",
                "MEDIUM",
                "HIGH",
                "CRITICAL",
                name="alert_severity_enum",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_dismissed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dismissed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["transaction_id"], ["transactions.id"], ondelete="SET NULL"
        ),
        # Note: category_id FK added after categories table exists
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for alerts
    with op.batch_alter_table("alerts", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_alerts_user_id"), ["user_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_alerts_alert_type"), ["alert_type"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_alerts_severity"), ["severity"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_alerts_is_dismissed"), ["is_dismissed"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_alerts_created_at"), ["created_at"], unique=False
        )
        # Composite index for common query: user's active alerts
        batch_op.create_index(
            "idx_alert_user_dismissed", ["user_id", "is_dismissed"], unique=False
        )

    # Add category_id FK after categories table exists
    with op.batch_alter_table("alerts", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "fk_alerts_category_id",
            "categories",
            ["category_id"],
            ["id"],
            ondelete="SET NULL",
        )

    # =========================================================================
    # 4. UPDATE TRANSACTIONS TABLE
    # =========================================================================
    # Add new columns for AI categorization

    with op.batch_alter_table("transactions", schema=None) as batch_op:
        # Category foreign key (nullable for backward compatibility)
        batch_op.add_column(sa.Column("category_id", sa.UUID(), nullable=True))

        # AI confidence score (0.0 to 1.0)
        batch_op.add_column(sa.Column("ai_confidence", sa.Float(), nullable=True))

        # AI source enum
        batch_op.add_column(
            sa.Column(
                "ai_source",
                sa.Enum(
                    "KEYWORD",
                    "HUGGINGFACE",
                    "GEMINI",
                    "USER",
                    name="ai_source_enum",
                    native_enum=False,
                ),
                nullable=True,
            )
        )

        # User override flag
        batch_op.add_column(
            sa.Column(
                "is_user_override", sa.Boolean(), nullable=False, server_default="false"
            )
        )

        # Original category (before user override)
        batch_op.add_column(sa.Column("original_category_id", sa.UUID(), nullable=True))

        # Add foreign key constraints
        batch_op.create_foreign_key(
            "fk_transactions_category_id",
            "categories",
            ["category_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_foreign_key(
            "fk_transactions_original_category_id",
            "categories",
            ["original_category_id"],
            ["id"],
            ondelete="SET NULL",
        )

        # Create indexes for new columns
        batch_op.create_index(
            batch_op.f("ix_transactions_category_id"), ["category_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_transactions_ai_source"), ["ai_source"], unique=False
        )
        batch_op.create_index(
            "idx_transaction_user_category_id",
            ["user_id", "category_id"],
            unique=False,
        )

    # =========================================================================
    # 5. SEED DEFAULT CATEGORIES
    # =========================================================================
    # Insert the 11 default categories

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    categories_table = sa.table(
        "categories",
        sa.column("id", sa.UUID()),
        sa.column("name", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("category_type", sa.String()),
        sa.column("icon", sa.String()),
        sa.column("color", sa.String()),
        sa.column("display_order", sa.Integer()),
        sa.column("is_active", sa.Boolean()),
        sa.column("created_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
    )

    op.bulk_insert(
        categories_table,
        [
            {
                "id": cat["id"],
                "name": cat["name"],
                "description": cat["description"],
                "category_type": cat["category_type"].upper(),
                "icon": cat["icon"],
                "color": cat["color"],
                "display_order": cat["display_order"],
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            }
            for cat in DEFAULT_CATEGORIES
        ],
    )


def downgrade():
    # =========================================================================
    # 1. REMOVE TRANSACTION COLUMNS AND CONSTRAINTS
    # =========================================================================
    with op.batch_alter_table("transactions", schema=None) as batch_op:
        # Drop indexes first
        batch_op.drop_index("idx_transaction_user_category_id")
        batch_op.drop_index(batch_op.f("ix_transactions_ai_source"))
        batch_op.drop_index(batch_op.f("ix_transactions_category_id"))

        # Drop foreign keys
        batch_op.drop_constraint(
            "fk_transactions_original_category_id", type_="foreignkey"
        )
        batch_op.drop_constraint("fk_transactions_category_id", type_="foreignkey")

        # Drop columns
        batch_op.drop_column("original_category_id")
        batch_op.drop_column("is_user_override")
        batch_op.drop_column("ai_source")
        batch_op.drop_column("ai_confidence")
        batch_op.drop_column("category_id")

    # =========================================================================
    # 2. DROP ALERTS TABLE
    # =========================================================================
    with op.batch_alter_table("alerts", schema=None) as batch_op:
        batch_op.drop_constraint("fk_alerts_category_id", type_="foreignkey")
        batch_op.drop_index("idx_alert_user_dismissed")
        batch_op.drop_index(batch_op.f("ix_alerts_created_at"))
        batch_op.drop_index(batch_op.f("ix_alerts_is_dismissed"))
        batch_op.drop_index(batch_op.f("ix_alerts_severity"))
        batch_op.drop_index(batch_op.f("ix_alerts_alert_type"))
        batch_op.drop_index(batch_op.f("ix_alerts_user_id"))

    op.drop_table("alerts")

    # =========================================================================
    # 3. DROP NOTIFICATIONS TABLE
    # =========================================================================
    with op.batch_alter_table("notifications", schema=None) as batch_op:
        batch_op.drop_index("idx_notification_user_status")
        batch_op.drop_index(batch_op.f("ix_notifications_created_at"))
        batch_op.drop_index(batch_op.f("ix_notifications_notification_type"))
        batch_op.drop_index(batch_op.f("ix_notifications_status"))
        batch_op.drop_index(batch_op.f("ix_notifications_user_id"))

    op.drop_table("notifications")

    # =========================================================================
    # 4. DROP CATEGORIES TABLE
    # =========================================================================
    with op.batch_alter_table("categories", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_categories_is_active"))
        batch_op.drop_index(batch_op.f("ix_categories_category_type"))
        batch_op.drop_index(batch_op.f("ix_categories_name"))

    op.drop_table("categories")

    # =========================================================================
    # 5. DROP ENUMS
    # =========================================================================
    # Note: SQLAlchemy non-native enums don't need explicit dropping
    # But if using native enums, uncomment:
    # op.execute("DROP TYPE IF EXISTS category_type_enum")
    # op.execute("DROP TYPE IF EXISTS notification_type_enum")
    # op.execute("DROP TYPE IF EXISTS notification_status_enum")
    # op.execute("DROP TYPE IF EXISTS ai_source_enum")
    # op.execute("DROP TYPE IF EXISTS alert_type_enum")
    # op.execute("DROP TYPE IF EXISTS alert_severity_enum")
