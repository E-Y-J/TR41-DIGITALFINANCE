#!/usr/bin/env python3
# =============================================================================
# Digital Finance Tracker - Single User Data Population
# PURPOSE: Populate comprehensive mock data for a specific user without clearing
#          the entire database. Useful for testing individual accounts.
# =============================================================================
"""
Single User Data Population Script

Usage:
    python tools/populate_user.py --email "suryadizhang.swe@gmail.com"
    python tools/populate_user.py --email "suryadizhang.swe@gmail.com" --months 6
    python tools/populate_user.py --email "suryadizhang.swe@gmail.com" --clear-first

This script:
1. Finds or creates the user by email
2. Optionally clears existing data for that user only
3. Populates comprehensive test data using JaeDataGenerator

Data Created (per month of data):
- ~20 recurring transactions (subscriptions, bills)
- ~4+ income transactions (salary, freelance, refunds)
- ~100+ daily spending transactions
- ~4+ anomaly test cases
- ~1 government & legal transaction
- 1 user override correction
- 1-2 AI chat sessions
- 1 budget per category
- 4+ notifications
- 2+ alerts
"""

import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone
from argparse import ArgumentParser

# Flask Setup & Pathing
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.append(str(backend_dir))

try:
    from app import create_app
    from app.core.extensions import db
    from app.models.user import User
    from app.models.ai_session import AISession
    from app.models.category import Category
    from app.models.transaction import Transaction
    from app.models.loan import Loan
    from app.models.notification import Notification
    from app.models.budget import Budget
except ImportError as e:
    print(f"Error importing Flask app: {e}")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

# ANSI Colors
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def stdout_write(message: str, color: str = BLUE) -> None:
    """Print colored message to stdout."""
    print(f"{color}{message}{RESET}")


def clear_user_data(user_id: str) -> dict:
    """
    Clear all data associated with a specific user.
    Returns dict with counts of deleted records.
    """
    counts = {}

    # Order matters due to foreign keys
    models = [
        ("AI Sessions", AISession),
        ("Transactions", Transaction),
        ("Loans", Loan),
        ("Budgets", Budget),
        ("Notifications", Notification),
    ]

    for name, model in models:
        try:
            count = model.query.filter_by(user_id=user_id).delete()
            counts[name] = count
            stdout_write(f"   Deleted {count} {name}")
        except Exception as e:
            stdout_write(f"   Error deleting {name}: {e}", RED)
            counts[name] = 0

    db.session.commit()
    return counts


def find_or_create_user(email: str, auth0_id: str = None) -> User:
    """
    Find existing user or create a new one.
    """
    user = User.query.filter_by(email=email).first()
    if user:
        stdout_write(f"Found existing user: {user.email} (ID: {user.id})", GREEN)
        return user

    # Create new user
    stdout_write(f"Creating new user: {email}", YELLOW)

    # Generate auth0_id if not provided
    if not auth0_id:
        auth0_id = f"manual|{uuid.uuid4()}"

    # Parse name from email if possible
    name_part = email.split("@")[0]
    parts = name_part.replace(".", " ").replace("_", " ").split()
    first_name = parts[0].capitalize() if parts else "Test"
    last_name = parts[-1].capitalize() if len(parts) > 1 else "User"

    user = User(
        id=str(uuid.uuid4()),
        auth0_id=auth0_id,
        email=email,
        email_verified=False,
        first_name=first_name,
        last_name=last_name,
        nickname=name_part,
        account_status="active",
        role="user",
        salary_amount="0.00",
        settings={
            "currency": "USD",
            "timezone": "America/Los_Angeles",
            "theme": "dark",
            "notifications": {"reminders": True},
        },
        created_at=datetime(2025, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime.now(timezone.utc),
        last_login=None,
    )
    db.session.add(user)
    db.session.commit()
    stdout_write(f"Created user: {user.email} (ID: {user.id})", GREEN)
    return user


def populate_user_data(user: User, categories: list, months_back: int = 12) -> dict:
    """
    Populate comprehensive test data for a user.
    """
    from tools.data_generators import JaeDataGenerator

    stdout_write("\n" + "=" * 60)
    stdout_write(f"Populating data for: {user.email}")
    stdout_write(f"Months of data: {months_back}")
    stdout_write("=" * 60)

    generator = JaeDataGenerator(
        user=user,
        categories=categories,
        months_back=months_back,
    )

    results = generator.generate_all(db.session)
    return results


def main():
    parser = ArgumentParser(description="Populate mock data for a specific user")
    parser.add_argument(
        "--email",
        required=True,
        help="User email address to populate data for",
    )
    parser.add_argument(
        "--auth0-id",
        help="Auth0 ID for new user (optional, auto-generated if not provided)",
    )
    parser.add_argument(
        "--months",
        type=int,
        default=12,
        help="Number of months of historical data to generate (default: 12)",
    )
    parser.add_argument(
        "--clear-first",
        action="store_true",
        help="Clear existing data for this user before populating",
    )

    args = parser.parse_args()

    app = create_app()

    with app.app_context():
        stdout_write("\n" + "=" * 60)
        stdout_write("📊 Single User Data Population Script")
        stdout_write("=" * 60)

        # Ensure categories exist
        Category.seed_defaults()
        categories = Category.query.all()
        if not categories:
            stdout_write("ERROR: No categories found!", RED)
            sys.exit(1)
        stdout_write(f"Found {len(categories)} categories")

        # Find or create user
        user = find_or_create_user(args.email, args.auth0_id)

        # Clear existing data if requested
        if args.clear_first:
            stdout_write("\n🗑️  Clearing existing data...")
            clear_user_data(user.id)

        # Populate data
        populate_user_data(user, categories, args.months)

        stdout_write("\n✅ Data population complete!", GREEN)
        stdout_write(f"User: {user.email}")
        stdout_write(f"User ID: {user.id}")


if __name__ == "__main__":
    main()
