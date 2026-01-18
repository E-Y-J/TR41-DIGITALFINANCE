#!/usr/bin/env python3
"""
Seed the database from a fixtures JSON file.

Usage:
  # dry-run (no writes)
  python tools/seed_db.py --file fixtures/seed_users.json

  # commit (actually write)
  python tools/seed_db.py --file fixtures/seed_users.json --commit
"""

import os
import json
import argparse
from pathlib import Path
import sys

# Auto-load .env from backend/.env if present (optional)
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).resolve().parents[1] / ".env"  # backend/.env
    if env_path.exists():
        load_dotenv(env_path)
except Exception:
    pass


REQUIRED_FIELDS = [
    "id",
    "auth0_id",
    "email",
    "first_name",
    "last_name",
    "account_status",
    "role",
    "salary_amount",
    "created_at",
    "updated_at",
]


def load_fixture(path):
    with open(path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    if isinstance(payload, dict) and "users" in payload:
        return payload["users"]
    if isinstance(payload, list):
        return payload
    raise ValueError(
        "Unsupported fixture format: expected { 'users': [...] } or a list."
    )


def validate_users(users):
    """
    Dry-run validation to check that all required fields are present
    and not None for every user.
    """
    valid = True
    for i, u in enumerate(users):
        for field in REQUIRED_FIELDS:
            if field not in u or u[field] is None:
                print(f"[Validation Error] User {i} missing required field: '{field}'")
                valid = False
    if valid:
        print(f"Validation passed: all {len(users)} users have required fields.")
    else:
        print("Validation failed: some users are missing required fields.")
    return valid


def try_flask_insert(users, commit=False):
    from pathlib import Path

    # Add backend folder to sys.path so Python can find 'app'
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    try:
        from app import create_app
        from app.core.extensions import db
        from app.models.user import User
    except ImportError as e:
        print("Flask import failed:", e)
        return False

    try:
        app = create_app()
    except Exception as e:
        print("create_app() raised an exception:", e)
        return False

    # Dry-run validation
    if not validate_users(users):
        print("Flask insertion aborted due to validation errors.")
        return False

    try:
        with app.app_context():
            inserted = 0
            for u in users:
                row = {
                    "id": u.get("id"),
                    "auth0_id": u.get("auth0_id"),
                    "email": u.get("email"),
                    "first_name": u.get("first_name"),
                    "last_name": u.get("last_name"),
                    "nickname": u.get("nickname"),  # Optional field
                    "account_status": u.get("account_status", "pending"),
                    "role": u.get("role", "USER"),
                    "salary_amount": u.get("salary_amount", "0.00"),
                    "settings": u.get("settings", {}),
                    "created_at": u.get("created_at"),
                    "updated_at": u.get("updated_at"),
                    "last_login": u.get("last_login"),
                }

                try:
                    obj = User(**row)
                except TypeError:
                    obj = User()
                    for k, v in row.items():
                        try:
                            setattr(obj, k, v)
                        except Exception:
                            pass

                db.session.add(obj)
                inserted += 1

            if commit:
                db.session.commit()
                print(f"Flask: inserted {inserted} users (committed).")
            else:
                db.session.rollback()
                print(f"Flask: would insert {inserted} users (dry-run).")
            return True
    except Exception as e:
        print("Flask insertion failed:", e)
        return False


def fallback_sqlalchemy_insert(users, commit=False):
    import os
    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.exc import SQLAlchemyError

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("No DATABASE_URL found in environment for fallback SQLAlchemy insert.")
        return False

    engine = create_engine(db_url)
    metadata = MetaData()
    try:
        metadata.reflect(bind=engine)
    except TypeError:
        metadata.reflect(engine)

    if "users" not in metadata.tables:
        print("Fallback: 'users' table not found in the target database.")
        return False

    users_table = metadata.tables["users"]

    # Dry-run validation
    if not validate_users(users):
        print("Fallback insertion aborted due to validation errors.")
        return False

    conn = engine.connect()
    trans = conn.begin()
    try:
        inserted = 0
        for u in users:
            row = {
                "id": u.get("id"),
                "auth0_id": u.get("auth0_id"),
                "email": u.get("email"),
                "first_name": u.get("first_name"),
                "last_name": u.get("last_name"),
                "account_status": u.get("account_status", "pending"),
                "role": u.get("role", "USER"),
                "salary_amount": u.get("salary_amount", "0.00"),
                "settings": json.dumps(u.get("settings", {})),
                "created_at": u.get("created_at"),
                "updated_at": u.get("updated_at"),
                "last_login": u.get("last_login"),
            }
            conn.execute(users_table.insert().values(**row))
            inserted += 1

        if commit:
            trans.commit()
            print(f"Fallback: inserted {inserted} users (committed).")
        else:
            trans.rollback()
            print(f"Fallback: would insert {inserted} users (dry-run).")

        return True
    except SQLAlchemyError as e:
        trans.rollback()
        print("Fallback SQLAlchemy error:", e)
        return False
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Seed the database from a fixture JSON."
    )
    parser.add_argument("--file", "-f", required=True, help="Path to fixture JSON file")
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Actually commit the inserts (default: dry-run)",
    )
    args = parser.parse_args()

    fixture_path = args.file
    if not os.path.exists(fixture_path):
        print("Fixture file not found:", fixture_path)
        return 2

    try:
        users = load_fixture(fixture_path)
    except Exception as e:
        print("Failed to load fixture:", e)
        return 3

    print(f"Loaded {len(users)} users from {fixture_path}")

    ok = try_flask_insert(users, commit=args.commit)
    if ok:
        return 0

    ok2 = fallback_sqlalchemy_insert(users, commit=args.commit)
    if ok2:
        return 0

    print("Seeding failed via both Flask and fallback paths.")
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
