# =============================================================================
# Digital Finance Tracker - Daily Spending Generator
# PURPOSE: Generate daily transaction patterns with weighted frequency
# =============================================================================
"""
Daily Spending Generator

Generates realistic daily spending patterns for testing:
- High-frequency merchants (coffee, fast food)
- Medium-frequency (groceries, restaurants)
- Low-frequency (electronics, luxury)
- Weekend vs weekday patterns

Uses weighted random selection for realistic distribution.
"""

import random
from decimal import Decimal
from typing import List, Tuple, TYPE_CHECKING

from tools.data_generators.base import BaseGenerator

if TYPE_CHECKING:
    from app.core.extensions import db


class DailySpendingGenerator(BaseGenerator):
    """
    Generator for daily spending transactions.

    Creates realistic spending patterns across all expense categories
    with weighted frequency distribution.
    """

    # Template format: (merchant, category, min_amt, max_amt, frequency_weight)
    # Higher weight = more frequent transactions
    TEMPLATES: List[Tuple[str, str, float, float, int]] = [
        # Coffee & Quick Bites (high frequency)
        ("Starbucks", "Food & Dining", 4.50, 8.95, 40),
        ("Peet's Coffee", "Food & Dining", 5.25, 9.50, 18),
        ("Blue Bottle Coffee", "Food & Dining", 5.50, 10.00, 10),
        ("7-Eleven", "Food & Dining", 2.50, 15.00, 15),
        ("Circle K", "Food & Dining", 3.00, 12.00, 8),
        # Fast Food (medium-high frequency)
        ("Chipotle", "Food & Dining", 10.50, 16.00, 25),
        ("Panda Express", "Food & Dining", 9.50, 14.00, 15),
        ("Subway", "Food & Dining", 8.00, 13.00, 12),
        ("In-N-Out Burger", "Food & Dining", 7.50, 15.00, 12),
        ("McDonald's", "Food & Dining", 5.00, 14.00, 15),
        ("Taco Bell", "Food & Dining", 6.00, 14.00, 10),
        ("Chick-fil-A", "Food & Dining", 8.00, 16.00, 12),
        ("Five Guys", "Food & Dining", 12.00, 22.00, 8),
        ("Wendy's", "Food & Dining", 6.00, 13.00, 8),
        # Food Delivery (weekend-heavy, higher amounts)
        ("DoorDash", "Food & Dining", 18.00, 65.00, 20),
        ("UberEats", "Food & Dining", 20.00, 70.00, 18),
        ("Grubhub", "Food & Dining", 22.00, 55.00, 12),
        ("Instacart", "Food & Dining", 45.00, 150.00, 10),
        # Groceries (weekly patterns)
        ("Trader Joe's", "Food & Dining", 45.00, 130.00, 25),
        ("Safeway", "Food & Dining", 35.00, 110.00, 20),
        ("Whole Foods", "Food & Dining", 50.00, 180.00, 15),
        ("Costco", "Food & Dining", 80.00, 300.00, 10),
        ("Sprouts", "Food & Dining", 30.00, 85.00, 8),
        ("Lucky Supermarket", "Food & Dining", 25.00, 75.00, 6),
        # Transportation - Gas (weekly)
        ("Shell", "Transportation", 35.00, 70.00, 20),
        ("Chevron", "Transportation", 38.00, 72.00, 18),
        ("76 Station", "Transportation", 32.00, 65.00, 10),
        ("Costco Gas", "Transportation", 40.00, 80.00, 8),
        ("Arco", "Transportation", 30.00, 60.00, 8),
        # Transportation - Rideshare (variable)
        ("Uber", "Transportation", 12.00, 55.00, 25),
        ("Lyft", "Transportation", 10.00, 50.00, 20),
        # Transportation - Public Transit
        ("BART", "Transportation", 4.50, 12.00, 30),
        ("Muni", "Transportation", 2.50, 5.00, 20),
        ("Clipper Card Reload", "Transportation", 20.00, 60.00, 8),
        ("Caltrain", "Transportation", 6.00, 15.00, 8),
        # Transportation - Parking
        ("Parking Meter", "Transportation", 2.00, 10.00, 18),
        ("Parking Garage", "Transportation", 15.00, 35.00, 8),
        ("SFO Parking", "Transportation", 25.00, 55.00, 3),
        # Shopping - General
        ("Amazon", "Shopping & Retail", 8.99, 280.00, 35),
        ("Target", "Shopping & Retail", 15.00, 150.00, 22),
        ("Walmart", "Shopping & Retail", 20.00, 120.00, 15),
        ("Walgreens", "Healthcare & Medical", 6.00, 45.00, 12),
        ("CVS Pharmacy", "Healthcare & Medical", 8.00, 55.00, 15),
        # Shopping - Specialty
        ("Best Buy", "Shopping & Retail", 25.00, 500.00, 6),
        ("Apple Store", "Shopping & Retail", 29.00, 350.00, 4),
        ("Home Depot", "Shopping & Retail", 15.00, 220.00, 8),
        ("Lowe's", "Shopping & Retail", 18.00, 180.00, 6),
        ("IKEA", "Shopping & Retail", 35.00, 400.00, 4),
        ("Bed Bath & Beyond", "Shopping & Retail", 25.00, 120.00, 4),
        ("TJ Maxx", "Shopping & Retail", 20.00, 85.00, 8),
        ("Ross", "Shopping & Retail", 15.00, 65.00, 6),
        ("Nordstrom Rack", "Shopping & Retail", 30.00, 150.00, 5),
        # Entertainment - Digital
        ("Steam", "Entertainment & Recreation", 9.99, 69.99, 8),
        ("PlayStation Store", "Entertainment & Recreation", 9.99, 79.99, 5),
        ("Nintendo eShop", "Entertainment & Recreation", 9.99, 59.99, 4),
        ("Xbox Store", "Entertainment & Recreation", 9.99, 69.99, 4),
        ("App Store", "Entertainment & Recreation", 0.99, 14.99, 12),
        ("Google Play", "Entertainment & Recreation", 0.99, 12.99, 10),
        # Entertainment - Outings
        ("AMC Theatres", "Entertainment & Recreation", 15.00, 50.00, 10),
        ("Regal Cinemas", "Entertainment & Recreation", 14.00, 45.00, 6),
        ("Dave & Buster's", "Entertainment & Recreation", 35.00, 95.00, 5),
        ("Escape Room SF", "Entertainment & Recreation", 35.00, 50.00, 3),
        ("Bowling Alley", "Entertainment & Recreation", 20.00, 45.00, 4),
        ("Mini Golf", "Entertainment & Recreation", 12.00, 28.00, 3),
        # Entertainment - Events
        ("Ticketmaster", "Entertainment & Recreation", 50.00, 300.00, 5),
        ("StubHub", "Entertainment & Recreation", 60.00, 400.00, 3),
        ("Eventbrite", "Entertainment & Recreation", 15.00, 75.00, 4),
        # Dining Out (weekends)
        ("The Cheesecake Factory", "Food & Dining", 45.00, 110.00, 8),
        ("Olive Garden", "Food & Dining", 35.00, 85.00, 6),
        ("Applebee's", "Food & Dining", 28.00, 65.00, 5),
        ("Red Lobster", "Food & Dining", 40.00, 95.00, 4),
        ("Local Sushi Restaurant", "Food & Dining", 40.00, 100.00, 10),
        ("Thai Basil", "Food & Dining", 25.00, 60.00, 8),
        ("Indian Cuisine", "Food & Dining", 30.00, 65.00, 6),
        ("Mexican Restaurant", "Food & Dining", 25.00, 55.00, 8),
        ("Local Pizza Place", "Food & Dining", 18.00, 45.00, 10),
        # Bars & Alcohol
        ("Local Bar", "Entertainment & Recreation", 25.00, 75.00, 8),
        ("Brewery Tour", "Entertainment & Recreation", 30.00, 70.00, 4),
        ("Wine Bar", "Entertainment & Recreation", 35.00, 85.00, 4),
        ("BevMo", "Food & Dining", 20.00, 80.00, 5),
        ("Total Wine", "Food & Dining", 25.00, 100.00, 4),
    ]

    # Weekend-heavy merchants (more frequent on Sat/Sun)
    WEEKEND_MERCHANTS = {
        "DoorDash", "UberEats", "Grubhub", "The Cheesecake Factory",
        "Olive Garden", "Local Sushi Restaurant", "AMC Theatres",
        "Dave & Buster's", "Local Bar", "Brewery Tour", "Wine Bar",
        "Ticketmaster", "StubHub", "Escape Room SF",
    }

    def generate(self, db_session) -> int:
        """
        Generate daily spending transactions.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            Number of transactions created
        """
        from app.models.transaction import Transaction, AISource

        count = 0
        days_to_generate = self.months_back * 30

        # Pre-calculate weights
        weights = [t[4] for t in self.TEMPLATES]

        for days_ago in range(days_to_generate):
            tx_date = self.get_date_days_ago(days_ago)
            is_weekend = self.is_weekend(tx_date)

            # Determine number of transactions for this day
            # More transactions on weekends
            base_count = random.randint(2, 5)
            if is_weekend:
                base_count += random.randint(1, 4)

            # Select transactions using weighted random choice
            selected = random.choices(self.TEMPLATES, weights=weights, k=base_count)

            for merchant, cat_name, min_amt, max_amt, _ in selected:
                category = self.get_category(cat_name)
                if not category:
                    continue

                # Skip some weekend-heavy merchants on weekdays
                if not is_weekend and merchant in self.WEEKEND_MERCHANTS:
                    if random.random() < 0.6:  # 60% chance to skip
                        continue

                amount = self.random_amount(min_amt, max_amt)

                # Determine AI source with realistic distribution
                source_roll = random.random()
                if source_roll < 0.55:
                    ai_source = AISource.KEYWORD
                    ai_confidence = round(random.uniform(0.90, 0.99), 2)
                elif source_roll < 0.85:
                    ai_source = AISource.HUGGINGFACE
                    ai_confidence = round(random.uniform(0.78, 0.95), 2)
                else:
                    ai_source = AISource.GEMINI
                    ai_confidence = round(random.uniform(0.72, 0.92), 2)

                # 8% are user overrides
                is_user_override = random.random() < 0.08
                if is_user_override:
                    ai_source = AISource.USER
                    ai_confidence = 1.0

                transaction = Transaction(
                    user_id=self.user.id,
                    amount=amount,
                    transaction_type="expense",
                    date=tx_date.strftime("%Y-%m-%d"),
                    merchant_name=merchant,
                    category_id=category.id,
                    ai_confidence=ai_confidence,
                    ai_source=ai_source.value,
                    is_user_override=is_user_override,
                )
                db_session.add(transaction)
                count += 1

        self.stdout_write(f"   Created {count} daily spending transactions", indent=3)
        return count
