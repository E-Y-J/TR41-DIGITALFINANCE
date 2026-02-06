# =============================================================================
# Digital Finance Tracker - Recurring Transactions Generator
# PURPOSE: Generate subscription and recurring bill transactions
# =============================================================================
"""
Recurring Transactions Generator

Generates predictable recurring payment patterns for testing:
- Streaming subscriptions (Netflix, Spotify, etc.)
- Utility bills (with realistic variance)
- Insurance premiums
- Rent payments
- Credit card payments

These create consistent monthly patterns for:
- Recurring transaction detection testing
- Budget forecasting
- Bill reminder features
"""

from decimal import Decimal
from typing import List, Tuple, TYPE_CHECKING

from tools.data_generators.base import BaseGenerator

if TYPE_CHECKING:
    from app.models.transaction import Transaction
    from app.core.extensions import db


class RecurringGenerator(BaseGenerator):
    """
    Generator for recurring transactions (subscriptions and bills).

    Creates monthly recurring payments on specific days of the month,
    going back N months for historical patterns.
    """

    # Template format: (merchant, category, amount, day_of_month, months_back)
    TEMPLATES: List[Tuple[str, str, float, int, int]] = [
        # Streaming subscriptions (fixed amounts)
        ("Netflix", "Entertainment & Recreation", 15.99, 5, 12),
        ("Spotify Premium", "Entertainment & Recreation", 10.99, 8, 12),
        ("Disney+", "Entertainment & Recreation", 13.99, 12, 10),
        ("YouTube Premium", "Entertainment & Recreation", 13.99, 15, 8),
        ("HBO Max", "Entertainment & Recreation", 15.99, 18, 6),
        ("Apple Music", "Entertainment & Recreation", 10.99, 22, 12),
        # Memberships
        ("Amazon Prime", "Shopping & Retail", 14.99, 20, 12),
        ("Costco Membership", "Shopping & Retail", 10.00, 25, 12),  # ~$120/year
        ("Planet Fitness", "Healthcare & Medical", 24.99, 1, 10),
        # Utilities (amounts vary)
        ("PG&E Electric", "Utilities & Services", 127.50, 3, 12),
        ("Comcast Xfinity", "Utilities & Services", 89.99, 7, 12),
        ("AT&T Wireless", "Utilities & Services", 95.00, 10, 12),
        ("Water Utility", "Utilities & Services", 45.00, 15, 12),
        ("Trash & Recycling", "Utilities & Services", 35.00, 20, 12),
        # Insurance
        ("Kaiser Health Insurance", "Healthcare & Medical", 350.00, 1, 12),
        ("Car Insurance - Geico", "Financial Services", 145.00, 18, 12),
        ("Renters Insurance", "Financial Services", 25.00, 5, 12),
        # Housing
        ("Rent Payment", "Utilities & Services", 1850.00, 1, 12),
        # Financial
        ("Chase Credit Card", "Financial Services", 500.00, 25, 12),
        ("Student Loan Payment", "Financial Services", 285.00, 15, 12),
    ]

    # Categories that should have variable amounts (utilities)
    VARIABLE_CATEGORIES = {"Utilities & Services"}
    VARIABLE_MERCHANTS = {"PG&E Electric", "Water Utility"}  # Exclude fixed-rate ones

    def generate(self, db_session) -> int:
        """
        Generate recurring transactions.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            Number of transactions created
        """
        from app.models.transaction import Transaction, AISource

        count = 0

        for merchant, cat_name, amount, day, months in self.TEMPLATES:
            # Limit to configured months_back
            actual_months = min(months, self.months_back)

            category = self.get_category(cat_name)
            if not category:
                continue

            for m in range(actual_months):
                tx_date = self.get_monthly_date(m, day)
                if not tx_date:
                    continue

                # Add variation for variable merchants
                final_amount = amount
                if merchant in self.VARIABLE_MERCHANTS:
                    final_amount = float(self.vary_amount(amount, 0.20))

                transaction = Transaction(
                    user_id=self.user.id,
                    amount=Decimal(str(final_amount)),
                    transaction_type="expense",
                    date=tx_date.strftime("%Y-%m-%d"),
                    merchant_name=merchant,
                    category_id=category.id,
                    ai_confidence=0.98,
                    ai_source=AISource.KEYWORD.value,
                    is_user_override=False,
                )
                db_session.add(transaction)
                count += 1

        self.stdout_write(f"   Created {count} recurring transactions", indent=3)
        return count
