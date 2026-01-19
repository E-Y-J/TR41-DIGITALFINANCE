#!/usr/bin/env python3
"""
Generate realistic seed users (JSON) for frontend testing.

Usage:
  python backend/tools/generate_seed_users.py --count 100 --out ../fixtures/seed_users.json
"""
import argparse
import json
import random
import uuid
from datetime import datetime

from faker import Faker


def make_user(fake: Faker, used_emails: set):
    first = fake.first_name()
    last = fake.last_name()
    
    # Generate a unique email
    while True:
        email = fake.safe_email()
        if email not in used_emails:
            used_emails.add(email)
            break

    # created_at is random in the past 2 years
    created_at = fake.date_time_between(start_date='-2y', end_date='now')
    # updated_at is between created_at and now
    now = datetime.utcnow()
    updated_at = fake.date_time_between(start_date=created_at, end_date=now)

    return {
        "id": str(uuid.uuid4()),
        "auth0_id": str(uuid.uuid4()),        
        "email": email,
        "email_verified": False,
        "first_name": first,
        "last_name": last,
        "nickname": fake.user_name(),
        "picture": None,
        "account_status": "pending",
        "role": "USER",
        "salary_amount": "0.00",
        "settings": {
            "currency": random.choice(["USD", "EUR", "GBP", "AUD"]),
            "timezone": random.choice(["UTC", "America/Los_Angeles", "Europe/London"]),
            "theme": random.choice(["light", "dark"]),
            "notifications": {"reminders": bool(random.getrandbits(1))}
        },
        "created_at": created_at.isoformat(),
        "updated_at": updated_at.isoformat(),
        "last_login": None
    }

def generate(count, seed=None):
    fake = Faker()
    if seed is not None:
        fake.seed_instance(seed)
        random.seed(seed)
    
    used_emails = set()
    users = [make_user(fake, used_emails) for _ in range(count)]

    jae_user = {
        "id": str(uuid.uuid4()),
        "auth0_id": "google-oauth2|110513262768393412869",
        "email": "jaeyseo0922@gmail.com",
        "email_verified": False,
        "first_name": "Jae",
        "last_name": "Seo",
        "nickname": fake.user_name(),
        "picture": None,
        "account_status": "pending",
        "role": "USER",
        "salary_amount": "0.00",
        "settings": {
            "currency": random.choice(["USD", "EUR", "GBP", "AUD"]),
            "timezone": random.choice(["UTC", "America/Los_Angeles", "Europe/London"]),
            "theme": random.choice(["light", "dark"]),
            "notifications": {"reminders": bool(random.getrandbits(1))}
        },
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "last_login": None
    }

    ariel_user = {
        "id": str(uuid.uuid4()),
        "auth0_id": "google-oauth2|110513262768393412869",
        "email": "jaeyseo0922@gmail.com",
        "email_verified": False,
        "first_name": "Ariel",
        "last_name": "Resendiz",
        "nickname": fake.user_name(),
        "picture": None,
        "account_status": "active",
        "role": "USER",
        "salary_amount": "0.00",
        "settings": {
            "currency": random.choice(["USD", "EUR", "GBP", "AUD"]),
            "timezone": random.choice(["UTC", "America/Los_Angeles", "Europe/London"]),
            "theme": random.choice(["light", "dark"]),
            "notifications": {"reminders": bool(random.getrandbits(1))}
        },
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "last_login": None
    }
  
  
#     "email": "joeyvigil109329@gmail.com",
  
# : "https://dev-y4aqxr6uv6uiqqc6.us.auth0.com/",
  
# : "google-oauth2|104977996918702131537",
    joseph_user ={ }

    users.append(jae_user)

    return {"generated_at": datetime.utcnow().isoformat() + "Z", "users": users}

def main():
    parser = argparse.ArgumentParser(description="Generate seed users JSON for frontend testing.")
    parser.add_argument("--count", "-c", type=int, default=100, help="Number of users to generate")
    parser.add_argument("--out", "-o", type=str, default="../fixtures/seed_users.json", help="Output JSON path")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible output")
    args = parser.parse_args()

    payload = generate(count=args.count, seed=args.seed)

    import os
    outdir = os.path.dirname(args.out) or "."
    os.makedirs(outdir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    print(f"Wrote {len(payload['users'])} users to {args.out}")


if __name__ == "__main__":
    main()