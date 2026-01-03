"""Align account_status to lowercase and add 'deactivated'

Revision ID: 748571261c46
Revises: 0ef6d8b45cc5
Create Date: 2026-01-02 22:28:46.813452
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '748571261c46'
down_revision = '0ef6d8b45cc5'
branch_labels = None
depends_on = None

def upgrade():
    # Drop any existing CHECK constraint that references account_status
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

    # Normalize existing data to lowercase to satisfy the new constraint
    op.execute("""
    UPDATE users
    SET account_status = CASE account_status
        WHEN 'PENDING' THEN 'pending'
        WHEN 'ACTIVE' THEN 'active'
        WHEN 'SUSPENDED' THEN 'suspended'
        ELSE LOWER(account_status)
    END;
    """)

    # Add the new CHECK constraint with lowercase + 'deactivated'
    op.execute("""
    ALTER TABLE users
    ADD CONSTRAINT ck_users_account_status_enum
    CHECK (account_status IN ('pending','active','suspended','deactivated'));
    """)

def downgrade():
    # Drop the lowercase constraint
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS ck_users_account_status_enum;")

    # Convert values back to uppercase to match the original initial migration
    op.execute("""
    UPDATE users
    SET account_status = CASE account_status
        WHEN 'pending' THEN 'PENDING'
        WHEN 'active' THEN 'ACTIVE'
        WHEN 'suspended' THEN 'SUSPENDED'
        WHEN 'deactivated' THEN 'SUSPENDED' -- fallback (no 'DEACTIVATED' in original)
        ELSE UPPER(account_status)
    END;
    """)

    # Recreate the original CHECK constraint (uppercase values only)
    op.execute("""
    ALTER TABLE users
    ADD CONSTRAINT ck_users_account_status_enum
    CHECK (account_status IN ('PENDING','ACTIVE','SUSPENDED'));
    """)