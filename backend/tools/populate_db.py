#!/usr/bin/env python3
"""
Classes controlling the CLI command to populate the database with dummy data.
Run with: python tools/populate_db.py --users 10 --transactions 50
"""

# MARK: Imports
import sys
import random
import uuid
from pathlib import Path
from datetime import datetime, timezone
from argparse import ArgumentParser

from faker import Faker

# MARK: Flask Setup & Pathing
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.append(str(backend_dir))

try:
    from app import create_app
    from app.core.extensions import db
    from app.models.user import User
    from app.models.category import Category
    from app.models.transaction import Transaction, TransactionType, AISource
except ImportError as e:
    print(f"Error importing Flask app: {e}")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)


# MARK: Command Class
class Command:
    """
    The populate_db CLI command for populating the database when starting the backend.
    """

    help = "Populate the database with dummy data"

    def __init__(self):
        self.fake = Faker()
        self.app = create_app()

    # MARK: Arguments
    def add_arguments(self, parser: ArgumentParser) -> None:
        """
        Add arguments into the parser.
        """
        parser.add_argument(
            "--users", type=int, default=10, help="Number of random users to create"
        )
        parser.add_argument(
            "--transactions",
            type=int,
            default=25,
            help="Number of transaction objects to create",
        )

    def handle(self, args) -> None:
        """
        Handle the execution of the command.
        """
        num_users = args.users
        num_transactions = args.transactions

        with self.app.app_context():
            # MARK: Clear Data
            self.clear_data()

            # MARK: Populate Random Data
            self.stdout_write(f"Creating {num_users} random users...")

            # Seed categories FIRST (required for transactions)
            Category.seed_defaults()
            categories = Category.query.all()

            if not categories:
                raise RuntimeError(
                    "No categories found after seed_defaults(). "
                    "Check Category.seed_defaults()."
                )

            created_count = 0
            used_emails = set()
            users = []

            # MARK: Create Random Users
            for _ in range(num_users):
                user_data = self.make_fake_user_data(used_emails)
                user = self.create_user_in_db(user_data)
                users.append(user)
                created_count += 1

            # MARK: Populate Specific Data
            self.stdout_write("Creating specific dev users...")
            specific_users = self.create_specific_users(used_emails)
            created_count += len(specific_users)

            db.session.commit()
            self.stdout_write(f"Successfully created {created_count} users total.")

            # MARK: Create Transactions
            self.stdout_write(f"Creating {num_transactions} transactions...")
            for _ in range(num_transactions):
                transaction = self.make_fake_transaction(users, categories)
                db.session.add(transaction)

            for _ in range(15):
                transaction = self.make_fake_transaction(specific_users, categories)
                db.session.add(transaction)

            try:
                db.session.commit()
                self.stdout_write(
                    f"Successfully created {num_transactions} transactions."
                )
            except Exception as e:
                db.session.rollback()
                self.stdout_write(f"Transaction commit failed: {e}")

    # -------------------- Helper Methods --------------------

    # MARK: Helper Methods
    def clear_data(self):
        """
        Wipes existing data to prevent duplicate key errors.
        """
        with self.app.app_context():
            # Transactions first (FKs)
            self.stdout_write("Clearing existing transaction data...")
            try:
                db.session.query(Transaction).delete()
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                self.stdout_write(f"   - Error clearing transactions: {e}")

            # Categories next
            self.stdout_write("Clearing existing category data...")
            try:
                db.session.query(Category).delete()
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                self.stdout_write(f"   - Error clearing categories: {e}")

            # Users last
            self.stdout_write("Clearing existing user data...")
            try:
                db.session.query(User).delete()
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                self.stdout_write(f"   - Error clearing users: {e}")

    def make_fake_user_data(self, used_emails: set) -> dict:
        """
        Generate a dictionary of realistic user data using Faker.
        """
        first = self.fake.first_name()
        last = self.fake.last_name()

        while True:
            email = self.fake.unique.safe_email()
            if email not in used_emails:
                used_emails.add(email)
                break

        created_at = self.fake.date_time_between(
            start_date="-2y", end_date="now", tzinfo=timezone.utc
        )
        updated_at = self.fake.date_time_between(
            start_date=created_at, end_date="now", tzinfo=timezone.utc
        )

        return {
            "id": str(uuid.uuid4()),
            "auth0_id": f"auth0|{uuid.uuid4()}",
            "email": email,
            "email_verified": False,
            "first_name": first,
            "last_name": last,
            "nickname": self.fake.user_name(),
            "account_status": "active",
            "role": "user",
            "salary_amount": "0.00",
            "settings": {
                "currency": random.choice(["USD", "EUR", "GBP", "AUD"]),
                "timezone": random.choice(
                    ["UTC", "America/Los_Angeles", "Europe/London"]
                ),
                "theme": random.choice(["light", "dark"]),
                "notifications": {"reminders": bool(random.getrandbits(1))},
            },
            "created_at": created_at,
            "updated_at": updated_at,
            "last_login": None,
        }

    def create_specific_users(self, used_emails: set) -> list[User]:
        """
        Create the hardcoded users required for development.
        """
        specific_users = [
            {
                "auth0_id": "google-oauth2|110513262768393412869",
                "email": "jaeyseo0922@gmail.com",
                "first_name": "Jae",
                "last_name": "Seo",
                "nickname": "jaeseo",
                "account_status": "active",
                "role": "user",
            },
            {
                "auth0_id": "google-oauth2|115671326262146450498",
                "email": "resendiz.ariel6@gmail.com",
                "first_name": "Ariel",
                "last_name": "Resendiz",
                "nickname": "arielr",
                "account_status": "active",
                "role": "user"
            },
        ]
        created_users = []

        for u_data in specific_users:
            if u_data["email"] in used_emails:
                continue

            used_emails.add(u_data["email"])

            full_data = {
                **u_data,
                "id": str(uuid.uuid4()),
                "email_verified": False,
                "salary_amount": "0.00",
                "settings": {
                    "currency": "USD",
                    "timezone": "America/Los_Angeles",
                    "theme": "dark",
                    "notifications": {"reminders": True},
                },
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "last_login": None,
            }

            user = self.create_user_in_db(full_data)
            created_users.append(user)

        return created_users

    def create_user_in_db(self, data: dict) -> User:
        """
        Instantiate the User model and add it to the session.
        """
        user = User(
            id=data["id"],
            auth0_id=data["auth0_id"],
            email=data["email"],
            email_verified=data["email_verified"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            nickname=data.get("nickname"),
            account_status=data["account_status"],
            role=data["role"],
            salary_amount=data["salary_amount"],
            settings=data["settings"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            last_login=data["last_login"],
        )
        db.session.add(user)
        return user

    def make_fake_transaction(
        self, users: list[User], categories: list[Category]
    ) -> Transaction:
        user = random.choice(users)

        # Pick transaction type first, then match category to type
        tx_type = random.choice(list(TransactionType))

        # Filter categories that match the transaction type
        # BOTH categories work for any transaction type
        matching_categories = [
            cat
            for cat in categories
            if cat.category_type.value == tx_type.value
            or cat.category_type.value == "both"
        ]

        # Fallback to any category if no match (shouldn't happen)
        if not matching_categories:
            matching_categories = categories

        category = random.choice(matching_categories)

        amount = round(random.uniform(5.0, 500.0), 2)
        date = self.fake.date_time_between(
            start_date="-1y", end_date="now", tzinfo=timezone.utc
        )

        ai_override = bool(random.getrandbits(1))
        ai_source = None if ai_override else random.choice(list(AISource))
        original_category = None if ai_override else random.choice(categories)

        return Transaction(
            user_id=user.id,
            amount=amount,
            transaction_type=tx_type.value,
            date=date,
            merchant_name=self.fake.company(),
            category_id=category.id,
            ai_confidence=(random.uniform(0.5, 1.0) if not ai_override else None),
            ai_source=ai_source.value if ai_source else None,
            is_user_override=ai_override,
            original_category_id=(original_category.id if original_category else None),
        )

    def stdout_write(self, message):
        """
        Helper to print to console in BLUE all the time.
        """
        blue = "\033[94m"  # Blue
        reset = "\033[0m"  # Reset

        print(f"{blue}{message}{reset}")


if __name__ == "__main__":
    cmd = Command()
    parser = ArgumentParser(description=cmd.help)
    cmd.add_arguments(parser)
    args = parser.parse_args()
    cmd.handle(args)
