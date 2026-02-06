# =============================================================================
# Digital Finance Tracker - Loan Generator
# PURPOSE: Generate loan records for testing loan tracking features
# =============================================================================
"""
Loan Generator

Generates loan records for testing:
- Car loan tracking
- Student loan tracking
- Personal loan tracking
- Loan payment analysis
- Debt management features

Enables testing of:
- Loan balance calculations
- Payment tracking
- Loan status queries via AI chat
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from tools.data_generators.base import BaseGenerator

if TYPE_CHECKING:
    from app.core.extensions import db


class LoanGenerator(BaseGenerator):
    """
    Generator for loan records.

    Creates realistic loan scenarios with varying balances and terms.
    """

    def generate(self, db_session) -> int:
        """
        Generate loan records.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            Number of loans created
        """
        from app.models.loan import Loan, LoanStatus

        # Get Financial Services category (required for loans)
        fin_category = self.get_category("Financial Services")
        if not fin_category:
            self.stdout_write("   WARNING: Financial Services category not found", indent=3)
            return 0

        count = 0
        today = date.today()

        # Loan templates matching actual model fields
        loan_templates = [
            {
                "name": "Toyota Camry Auto Loan",
                "original_amount": 28500.00,
                "remaining_amount": 18750.00,
                "start_months_ago": 24,
                "term_months": 72,
            },
            {
                "name": "Federal Student Loan",
                "original_amount": 45000.00,
                "remaining_amount": 32150.00,
                "start_months_ago": 48,
                "term_months": 120,
            },
            {
                "name": "Personal Loan - Home Improvement",
                "original_amount": 15000.00,
                "remaining_amount": 8200.00,
                "start_months_ago": 18,
                "term_months": 48,
            },
        ]

        for template in loan_templates:
            # Calculate dates
            start_date = today - timedelta(days=template["start_months_ago"] * 30)
            end_date = start_date + timedelta(days=template["term_months"] * 30)

            loan = Loan(
                user_id=self.user.id,
                category_id=fin_category.id,
                name=template["name"],
                original_amount=Decimal(str(template["original_amount"])),
                remaining_amount=Decimal(str(template["remaining_amount"])),
                start_date=start_date,
                end_date=end_date,
                status=LoanStatus.OPEN,
            )
            db_session.add(loan)
            count += 1

        # Add one paid-off loan in history
        paid_off_start = today - timedelta(days=18 * 30)
        paid_off_end = today - timedelta(days=6 * 30)

        paid_off_loan = Loan(
            user_id=self.user.id,
            category_id=fin_category.id,
            name="Best Buy Credit Card",
            original_amount=Decimal("1899.00"),
            remaining_amount=Decimal("0.00"),
            start_date=paid_off_start,
            end_date=paid_off_end,
            status=LoanStatus.CLOSED,
        )
        db_session.add(paid_off_loan)
        count += 1

        self.stdout_write(f"   Created {count} loans (1 paid off)", indent=3)
        return count
