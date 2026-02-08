# =============================================================================
# Digital Finance Tracker - Anomaly Generator
# PURPOSE: Generate unusual transactions for anomaly detection testing
# =============================================================================
"""
Anomaly Generator

Generates unusual and edge-case transactions for testing:
- Unusually large purchases (luxury items)
- Duplicate transactions (same amount, same day)
- Late-night transactions
- Multiple same-category same-day
- Micro-transactions
- Round number patterns
- Suspicious patterns

These enable comprehensive anomaly detection testing.
"""

import random
from decimal import Decimal
from typing import List, Tuple, TYPE_CHECKING

from tools.data_generators.base import BaseGenerator

if TYPE_CHECKING:
    from app.core.extensions import db


class AnomalyGenerator(BaseGenerator):
    """
    Generator for anomaly detection test cases.

    Creates unusual transaction patterns that should trigger
    anomaly detection algorithms.
    """

    # Anomaly templates: (merchant, category, amount, days_ago, notes, anomaly_type)
    ANOMALIES: List[Tuple[str, str, float, int, str, str]] = [
        # Unusual luxury purchases (high value)
        ("Louis Vuitton", "Shopping & Retail", 2450.00, 3, "Unusual luxury purchase", "luxury"),
        ("Rolex Authorized Dealer", "Shopping & Retail", 8500.00, 45, "High-value watch", "luxury"),
        ("Tiffany & Co", "Shopping & Retail", 1850.00, 68, "Jewelry purchase", "luxury"),
        ("Gucci", "Shopping & Retail", 1200.00, 92, "Designer purchase", "luxury"),
        ("Tesla Service", "Transportation", 2800.00, 120, "Car service", "luxury"),

        # Medical emergencies
        ("Emergency Room Visit", "Healthcare & Medical", 1250.00, 20, "Medical emergency", "medical"),
        ("Urgent Care Clinic", "Healthcare & Medical", 450.00, 55, "Urgent visit", "medical"),
        ("Ambulance Service", "Healthcare & Medical", 890.00, 88, "Emergency transport", "medical"),

        # Duplicate transactions (same merchant, same day, same amount)
        ("Starbucks", "Food & Dining", 5.75, 5, "Morning coffee", "duplicate"),
        ("Starbucks", "Food & Dining", 5.75, 5, "Duplicate? Same amount same day", "duplicate"),
        ("Amazon", "Shopping & Retail", 29.99, 12, "First purchase", "duplicate"),
        ("Amazon", "Shopping & Retail", 29.99, 12, "Duplicate same-day", "duplicate"),

        # Late night transactions (suspiciously timed)
        ("7-Eleven", "Food & Dining", 18.00, 8, "Late night - 2:30 AM", "late_night"),
        ("Uber", "Transportation", 65.00, 8, "Late night ride home - 3 AM", "late_night"),
        ("Gas Station", "Transportation", 42.00, 22, "Late night fuel - 1 AM", "late_night"),
        ("ATM Withdrawal", "Financial Services", 200.00, 15, "Late night ATM - 2 AM", "late_night"),

        # Legal/unusual category
        ("Bail Bonds Inc", "Financial Services", 5000.00, 100, "Legal situation", "legal"),
        ("Law Office - Retainer", "Financial Services", 2500.00, 140, "Legal fees", "legal"),
        ("Court Filing Fee", "Government & Legal", 350.00, 155, "Court costs", "legal"),

        # Multiple gas stations same day (road trip or suspicious)
        ("Shell", "Transportation", 55.00, 15, "First fill up", "multiple_same_day"),
        ("Chevron", "Transportation", 58.00, 15, "Second fill - same day", "multiple_same_day"),
        ("76 Station", "Transportation", 52.00, 15, "Third gas station same day", "multiple_same_day"),
        ("Arco", "Transportation", 48.00, 15, "Fourth gas same day", "multiple_same_day"),

        # Micro-transactions (subscription charges, in-app)
        ("App Store", "Entertainment & Recreation", 0.99, 25, "Tiny purchase", "micro"),
        ("Google Play", "Entertainment & Recreation", 0.99, 30, "Micro-transaction", "micro"),
        ("In-App Purchase", "Entertainment & Recreation", 1.99, 35, "Mobile game", "micro"),
        ("Patreon", "Entertainment & Recreation", 1.00, 40, "Subscription", "micro"),

        # Round number patterns (potentially suspicious)
        ("Cash Withdrawal", "Financial Services", 500.00, 40, "ATM - round amount", "round"),
        ("Wire Transfer Out", "Financial Services", 2000.00, 55, "Large round transfer", "round"),
        ("Zelle Transfer", "Financial Services", 1000.00, 70, "Round transfer", "round"),
        ("Venmo Transfer", "Financial Services", 500.00, 85, "Round P2P", "round"),
        ("Cash Deposit", "Income", 3000.00, 100, "Round deposit", "round"),

        # Foreign transactions
        ("Currency Exchange", "Financial Services", 200.00, 130, "Foreign currency", "foreign"),
        ("International ATM", "Financial Services", 300.00, 135, "Overseas withdrawal", "foreign"),
        ("Hotel - Paris", "Entertainment & Recreation", 450.00, 138, "Travel expense", "foreign"),
        ("Restaurant - Tokyo", "Food & Dining", 85.00, 142, "International dining", "foreign"),

        # Subscription traps (free trial conversions)
        ("Mystery Box Subscription", "Shopping & Retail", 49.99, 28, "Forgot to cancel?", "subscription"),
        ("Premium Membership", "Entertainment & Recreation", 99.99, 35, "Auto-renewed", "subscription"),
        ("VIP Access Monthly", "Entertainment & Recreation", 29.99, 42, "Recurring charge", "subscription"),

        # Very high single transactions
        ("Furniture Store", "Shopping & Retail", 3500.00, 180, "Major furniture purchase", "high_value"),
        ("Vacation Package", "Entertainment & Recreation", 4200.00, 200, "Travel booking", "high_value"),
        ("Appliance Store", "Shopping & Retail", 2100.00, 220, "Appliance purchase", "high_value"),
    ]

    def generate(self, db_session) -> int:
        """
        Generate anomaly transactions.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            Number of transactions created
        """
        from app.models.transaction import Transaction, AISource

        count = 0
        max_days = self.months_back * 30

        for merchant, cat_name, amount, days_ago, notes, anomaly_type in self.ANOMALIES:
            if days_ago > max_days:
                continue

            category = self.get_category(cat_name)
            if not category:
                # Try alternative category
                if cat_name == "Government & Legal":
                    category = self.get_category("Financial Services")
                if not category:
                    continue

            tx_date = self.get_date_days_ago(days_ago)

            # Determine transaction type
            tx_type = "income" if "deposit" in notes.lower() else "expense"

            # Lower confidence for unusual transactions
            confidence = 0.65 if anomaly_type in ["luxury", "legal", "foreign"] else 0.75

            transaction = Transaction(
                user_id=self.user.id,
                amount=Decimal(str(amount)),
                transaction_type=tx_type,
                date=tx_date.strftime("%Y-%m-%d"),
                merchant_name=merchant,
                category_id=category.id,
                ai_confidence=confidence,
                ai_source=AISource.GEMINI.value,
                is_user_override=False,
            )
            db_session.add(transaction)
            count += 1

        self.stdout_write(f"   Created {count} anomaly transactions", indent=3)
        return count


class UserOverrideGenerator(BaseGenerator):
    """
    Generator for user override correction transactions.

    Creates transactions where AI miscategorized and user corrected,
    testing the category correction flow.
    """

    # Override templates: (merchant, original_cat, correct_cat, amount, days_ago)
    OVERRIDES: List[Tuple[str, str, str, float, int]] = [
        ("Amazon Business Services", "Shopping & Retail", "Utilities & Services", 89.99, 35),
        ("Apple One Subscription", "Shopping & Retail", "Entertainment & Recreation", 22.95, 28),
        ("Costco Gas", "Shopping & Retail", "Transportation", 48.00, 18),
        ("Doctor Office Copay", "Financial Services", "Healthcare & Medical", 25.00, 42),
        ("Insurance Premium", "Utilities & Services", "Financial Services", 175.00, 12),
        ("Spotify Gift Card", "Entertainment & Recreation", "Shopping & Retail", 30.00, 8),
        ("Netflix Subscription", "Shopping & Retail", "Entertainment & Recreation", 15.99, 5),
        ("Gym Equipment", "Healthcare & Medical", "Shopping & Retail", 245.00, 55),
        ("Home Office Supplies", "Shopping & Retail", "Utilities & Services", 89.00, 62),
        ("Car Wash Subscription", "Shopping & Retail", "Transportation", 19.99, 15),
        ("Pet Insurance", "Healthcare & Medical", "Financial Services", 45.00, 25),
        ("Magazine Subscription", "Entertainment & Recreation", "Shopping & Retail", 12.99, 38),
    ]

    def generate(self, db_session) -> int:
        """
        Generate user override transactions.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            Number of transactions created
        """
        from app.models.transaction import Transaction, AISource

        count = 0
        max_days = self.months_back * 30

        for merchant, original_cat, correct_cat, amount, days_ago in self.OVERRIDES:
            if days_ago > max_days:
                continue

            category = self.get_category(correct_cat)
            original_category = self.get_category(original_cat)
            if not category or not original_category:
                continue

            tx_date = self.get_date_days_ago(days_ago)

            transaction = Transaction(
                user_id=self.user.id,
                amount=Decimal(str(amount)),
                transaction_type="expense",
                date=tx_date.strftime("%Y-%m-%d"),
                merchant_name=merchant,
                category_id=category.id,
                ai_confidence=1.0,
                ai_source=AISource.USER.value,
                is_user_override=True,
                original_category_id=original_category.id,
            )
            db_session.add(transaction)
            count += 1

        self.stdout_write(f"   Created {count} user override transactions", indent=3)
        return count


class GovernmentLegalGenerator(BaseGenerator):
    """
    Generator for Government & Legal transactions.

    Creates transactions in the often-empty Government & Legal category.
    """

    # Government/Legal templates: (merchant, amount, days_ago, notes)
    TEMPLATES: List[Tuple[str, float, int, str]] = [
        ("DMV Registration", 250.00, 45, "Annual vehicle registration"),
        ("DMV License Renewal", 45.00, 180, "Driver license renewal"),
        ("Parking Ticket - SF", 85.00, 22, "Street parking violation"),
        ("Parking Ticket - Oakland", 65.00, 88, "Expired meter"),
        ("Court Filing Fee", 45.00, 90, "Small claims court"),
        ("Passport Renewal", 130.00, 120, "US Passport renewal"),
        ("Property Tax", 1250.00, 75, "Annual property tax"),
        ("Property Tax Q2", 1250.00, 165, "Q2 property tax"),
        ("State Income Tax", 850.00, 280, "State tax payment"),
        ("Federal Income Tax", 1500.00, 285, "Federal tax payment"),
        ("Jury Duty Parking", 25.00, 200, "Jury service expenses"),
        ("Building Permit", 450.00, 250, "Home improvement permit"),
        ("Business License", 175.00, 300, "Annual business license"),
        ("TSA PreCheck", 85.00, 340, "Travel convenience"),
    ]

    def generate(self, db_session) -> int:
        """
        Generate Government & Legal transactions.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            Number of transactions created
        """
        from app.models.transaction import Transaction, AISource

        category = self.get_category("Government & Legal")
        if not category:
            self.stdout_write("   WARNING: Government & Legal category not found", indent=3)
            return 0

        count = 0
        max_days = self.months_back * 30

        for merchant, amount, days_ago, notes in self.TEMPLATES:
            if days_ago > max_days:
                continue

            tx_date = self.get_date_days_ago(days_ago)

            transaction = Transaction(
                user_id=self.user.id,
                amount=Decimal(str(amount)),
                transaction_type="expense",
                date=tx_date.strftime("%Y-%m-%d"),
                merchant_name=merchant,
                category_id=category.id,
                ai_confidence=0.88,
                ai_source=AISource.GEMINI.value,
                is_user_override=False,
            )
            db_session.add(transaction)
            count += 1

        self.stdout_write(f"   Created {count} Government & Legal transactions", indent=3)
        return count
