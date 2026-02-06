# =============================================================================
# Digital Finance Tracker - Income Generator
# PURPOSE: Generate salary, freelance, and refund income transactions
# =============================================================================
"""
Income Generator

Generates realistic income patterns for testing:
- Bi-weekly salary deposits (1st and 15th of month)
- Irregular freelance income
- Refunds and cashback rewards
- Peer-to-peer transfers (Venmo/Zelle)

These patterns enable testing of:
- Income tracking and analysis
- Net savings calculations
- Cash flow projections
"""

import random
from decimal import Decimal
from typing import List, Tuple, TYPE_CHECKING

from tools.data_generators.base import BaseGenerator

if TYPE_CHECKING:
    from app.core.extensions import db


class IncomeGenerator(BaseGenerator):
    """
    Generator for income transactions.

    Creates salary patterns on paydays, plus irregular freelance
    and refund income.
    """

    # Base salary per paycheck (2x per month)
    BASE_SALARY = 3250.00
    SALARY_VARIANCE = 0.08  # ±8% for overtime, etc.

    # Freelance payment days (days ago)
    FREELANCE_DAYS = [15, 45, 78, 92, 120, 145, 160, 185, 210, 275, 320, 350]

    # Refund/cashback data: (merchant, amount, days_ago)
    REFUNDS: List[Tuple[str, float, int]] = [
        ("Amazon Refund", 45.99, 8),
        ("Target Return", 67.50, 25),
        ("Chase Cashback Reward", 125.00, 32),
        ("Discover Cashback", 85.50, 60),
        ("Capital One Rewards", 67.25, 95),
        ("Venmo - Friend Payment", 35.00, 5),
        ("Venmo - Dinner Split", 28.50, 12),
        ("Venmo - Utilities Split", 42.00, 38),
        ("Zelle - Roommate Utilities", 95.00, 2),
        ("Zelle - Birthday Gift", 50.00, 45),
        ("PayPal Transfer", 120.00, 78),
        ("Tax Refund - State", 485.00, 280),
        ("Tax Refund - Federal", 1250.00, 285),
        ("Warranty Reimbursement", 89.99, 150),
    ]

    # Freelance clients
    FREELANCE_CLIENTS = [
        "Upwork",
        "Fiverr",
        "Direct Client - WebDev",
        "Consulting LLC",
        "Freelance Design Co",
        "Contract Work - ABC Corp",
    ]

    def generate(self, db_session) -> int:
        """
        Generate income transactions.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            Number of transactions created
        """
        from app.models.transaction import Transaction, AISource

        income_category = self.get_category("Income")
        if not income_category:
            self.stdout_write("   WARNING: Income category not found", indent=3)
            return 0

        count = 0

        # =====================================================================
        # SALARY DEPOSITS (1st and 15th of each month)
        # =====================================================================
        for m in range(self.months_back):
            # Payday 1: 1st of month
            payday1 = self.get_monthly_date(m, 1)
            if payday1:
                salary = self.BASE_SALARY * random.uniform(
                    1 - self.SALARY_VARIANCE, 1 + self.SALARY_VARIANCE
                )
                transaction = Transaction(
                    user_id=self.user.id,
                    amount=Decimal(str(round(salary, 2))),
                    transaction_type="income",
                    date=payday1.strftime("%Y-%m-%d"),
                    merchant_name="TechCorp Inc. - Payroll",
                    category_id=income_category.id,
                    ai_confidence=0.99,
                    ai_source=AISource.KEYWORD.value,
                    is_user_override=False,
                )
                db_session.add(transaction)
                count += 1

            # Payday 2: 15th of month
            payday2 = self.get_monthly_date(m, 15)
            if payday2:
                salary = self.BASE_SALARY * random.uniform(
                    1 - self.SALARY_VARIANCE, 1 + self.SALARY_VARIANCE
                )
                transaction = Transaction(
                    user_id=self.user.id,
                    amount=Decimal(str(round(salary, 2))),
                    transaction_type="income",
                    date=payday2.strftime("%Y-%m-%d"),
                    merchant_name="TechCorp Inc. - Payroll",
                    category_id=income_category.id,
                    ai_confidence=0.99,
                    ai_source=AISource.KEYWORD.value,
                    is_user_override=False,
                )
                db_session.add(transaction)
                count += 1

        # =====================================================================
        # FREELANCE INCOME (irregular)
        # =====================================================================
        max_days = self.months_back * 30
        for days_ago in self.FREELANCE_DAYS:
            if days_ago > max_days:
                continue

            tx_date = self.get_date_days_ago(days_ago)
            amount = round(random.uniform(150, 850), 2)
            client = random.choice(self.FREELANCE_CLIENTS)

            transaction = Transaction(
                user_id=self.user.id,
                amount=Decimal(str(amount)),
                transaction_type="income",
                date=tx_date.strftime("%Y-%m-%d"),
                merchant_name=client,
                category_id=income_category.id,
                ai_confidence=0.95,
                ai_source=AISource.GEMINI.value,
                is_user_override=False,
            )
            db_session.add(transaction)
            count += 1

        # =====================================================================
        # REFUNDS AND CASHBACK
        # =====================================================================
        max_days = self.months_back * 30
        for merchant, amount, days_ago in self.REFUNDS:
            if days_ago > max_days:
                continue

            tx_date = self.get_date_days_ago(days_ago)
            transaction = Transaction(
                user_id=self.user.id,
                amount=Decimal(str(amount)),
                transaction_type="income",
                date=tx_date.strftime("%Y-%m-%d"),
                merchant_name=merchant,
                category_id=income_category.id,
                ai_confidence=0.92,
                ai_source=AISource.GEMINI.value,
                is_user_override=False,
            )
            db_session.add(transaction)
            count += 1

        self.stdout_write(f"   Created {count} income transactions", indent=3)
        return count
