#!/usr/bin/env python3
"""
Classes controlling the CLI command to populate the database with dummy data.
Run with: python tools/populate_db.py --users 10
"""

# MARK: Imports
import sys
import os
import random
import uuid
import json
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
            "--users", 
            type=int, 
            default=10, 
            help="Number of random users to create"
        )
        parser.add_argument(
            "--transactions",
            type=int,
            default=25,
            help="Number of transaction objects to create"
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
            
            created_count = 0
            used_emails = set()

            for _ in range(num_users):
                user_data = self.make_fake_user_data(used_emails)
                self.create_user_in_db(user_data)
                created_count += 1
                
            for _ in range(num_transactions):
                pass

            # MARK: Populate Specific Data
            self.stdout_write("Creating specific dev users...")
            self.create_specific_users(used_emails)
            created_count += 2

            try:
                db.session.commit()
                self.stdout_write(
                    f"Successfully created {created_count} users total.", 
                )
            except Exception as e:
                db.session.rollback()
                self.stdout_write(f"Database commit failed: {e}")

    # MARK: Helper Methods
    def clear_data(self):
        """
        Wipes existing data to prevent duplicate key errors.
        """
        self.stdout_write("Clearing existing user data...")
        try:
            num_deleted = db.session.query(User).delete()
            db.session.commit()
            self.stdout_write(f"   - Deleted {num_deleted} existing users.")
        except Exception as e:
            db.session.rollback()
            self.stdout_write(f"   - Error clearing data: {e}")

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
        
        created_at = self.fake.date_time_between(start_date="-2y", end_date="now", tzinfo=timezone.utc)
        updated_at = self.fake.date_time_between(start_date=created_at, end_date="now", tzinfo=timezone.utc)

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
                "timezone": random.choice(["UTC", "America/Los_Angeles", "Europe/London"]),
                "theme": random.choice(["light", "dark"]),
                "notifications": {"reminders": bool(random.getrandbits(1))},
            },
            "created_at": created_at,
            "updated_at": updated_at,
            "last_login": None,
        }

    def create_specific_users(self, used_emails: set):
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
                "role": "user"
            },
            {
                "auth0_id": "google-oauth2|104977996918702131537",
                "email": "joeyvigil109329@gmail.com",
                "first_name": "Joseph",
                "last_name": "Vigil",
                "nickname": "arielr",
                "account_status": "active",
                "role": "user"
            }
        ]

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
            self.create_user_in_db(full_data)

    def create_user_in_db(self, data: dict):
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
            last_login=data["last_login"]
        )
        db.session.add(user)

    def stdout_write(self, message):
        """
        Helper to print to console in BLUE all the time.
        """
        blue = "\033[94m"   # Blue
        reset = "\033[0m"   # Reset
        
        print(f"{blue}{message}{reset}")

if __name__ == "__main__":
    cmd = Command()
    parser = ArgumentParser(description=cmd.help)
    cmd.add_arguments(parser)
    args = parser.parse_args()
    cmd.handle(args)