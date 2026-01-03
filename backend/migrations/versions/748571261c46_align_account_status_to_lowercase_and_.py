"""Align account_status to lowercase and add 'deactivated' (with column widening)

Revision ID: 748571261c46
Revises: 0ef6d8b45cc5
Create Date: 2026-01-02 22:28:46.813452
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "748571261c46"
down_revision = "0ef6d8b45cc5"
branch_labels = None
depends_on = None


def upgrade():
    # 1) Drop any existing CHECK constraint that references account_status
    op.execute("""
    DO $$
    DECLARE
        constraint_name text;
    BEGIN
        SELECT c.conname INTO constraint_name
        FROM pg_constraint c
        JOIN pg_class t ON c.conrelid = t.oid
        WHERE t.relname = 'users'
          AND c.contype = 'c'
          AND pg_get_constraintdef(c.oid) LIKE '%account_status%';
        IF constraint_name IS NOT NULL THEN
            EXECUTE format('ALTER TABLE users DROP CONSTRAINT %I', constraint_name);
        END IF;
    END$$;
    """)

    # 2) Widen column to handle 'deactivated' (11 chars) with a bit of headroom
    op.execute("ALTER TABLE users ALTER COLUMN account_status TYPE VARCHAR(12);")

    # 3) Normalize existing data to lowercase to satisfy the new constraint
    op.execute("""
    UPDATE users
    SET account_status = CASE account_status
        WHEN 'PENDING' THEN 'pending'
        WHEN 'ACTIVE' THEN 'active'
        WHEN 'SUSPENDED' THEN 'suspended'
        ELSE LOWER(account_status)
    END;
    """)

    # 4) Add the new CHECK constraint with lowercase + 'deactivated'
    op.execute("""
    ALTER TABLE users
    ADD CONSTRAINT ck_users_account_status_enum
    CHECK (account_status IN ('pending','active','suspended','deactivated'));
    """)


def downgrade():
    # 1) Drop the lowercase constraint
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS ck_users_account_status_enum;")

    # 2) Convert values back to uppercase to match the original initial migration
    op.execute("""
    UPDATE users
    SET account_status = CASE account_status
        WHEN 'pending' THEN 'PENDING'
        WHEN 'active' THEN 'ACTIVE'
        WHEN 'suspended' THEN 'SUSPENDED'
        WHEN 'deactivated' THEN 'SUSPENDED' -- fallback in original schema
        ELSE UPPER(account_status)
    END;
    """)

    # 3) Narrow column back to original length (VARCHAR(9))
    op.execute("ALTER TABLE users ALTER COLUMN account_status TYPE VARCHAR(9);")

    # 4) Recreate the original CHECK constraint (uppercase values only)
    op.execute("""
    ALTER TABLE users
    ADD CONSTRAINT ck_users_account_status_enum
    CHECK (account_status IN ('PENDING','ACTIVE','SUSPENDED'));
    """)