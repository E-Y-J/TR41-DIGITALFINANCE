# =============================================================================
# Digital Finance Tracker - Budget Generator
# PURPOSE: Generate budget records for testing budget tracking features
# =============================================================================
"""
Budget Generator

Generates budget records for testing:
- Category budgets (per-category limits)
- Total budget (overall spending limit)
- Weekly and monthly periods
- Various budget amounts matching spending patterns

Enables testing of:
- Budget creation and management
- Budget alert triggers
- Budget progress tracking
- Budget vs actual spending analysis
"""

from decimal import Decimal
from typing import List, Tuple, TYPE_CHECKING

from tools.data_generators.base import BaseGenerator

if TYPE_CHECKING:
    from app.core.extensions import db


class BudgetGenerator(BaseGenerator):
    """
    Generator for budget records.

    Creates realistic budgets that align with generated spending patterns.
    """

    # Category budget templates: (category_name, monthly_amount, weekly_amount, period)
    # Only one budget per category per period is allowed
    MONTHLY_BUDGETS: List[Tuple[str, float]] = [
        ("Food & Dining", 650.00),
        ("Transportation", 400.00),
        ("Shopping & Retail", 450.00),
        ("Entertainment & Recreation", 350.00),
        ("Utilities & Services", 2300.00),
        ("Healthcare & Medical", 450.00),
        ("Financial Services", 750.00),
        ("Government & Legal", 200.00),
    ]

    WEEKLY_BUDGETS: List[Tuple[str, float]] = [
        ("Food & Dining", 150.00),
        ("Entertainment & Recreation", 80.00),
        ("Shopping & Retail", 100.00),
    ]

    # Total budget (overall spending limit)
    TOTAL_MONTHLY_BUDGET = 4500.00
    TOTAL_WEEKLY_BUDGET = 1000.00

    def generate(self, db_session) -> int:
        """
        Generate budget records.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            Number of budgets created
        """
        from app.models.budget import Budget
        from app.models.enums import BudgetType, BudgetPeriod

        count = 0

        # Create monthly category budgets
        for cat_name, amount in self.MONTHLY_BUDGETS:
            category = self.get_category(cat_name)
            if not category:
                continue

            budget = Budget(
                user_id=self.user.id,
                category_id=category.id,
                budget_type=BudgetType.CATEGORY,
                amount=Decimal(str(amount)),
                period=BudgetPeriod.MONTHLY,
                last_period_surplus=Decimal("0.00"),
                is_active=True,
            )
            db_session.add(budget)
            count += 1

        # Create weekly category budgets
        for cat_name, amount in self.WEEKLY_BUDGETS:
            category = self.get_category(cat_name)
            if not category:
                continue

            budget = Budget(
                user_id=self.user.id,
                category_id=category.id,
                budget_type=BudgetType.CATEGORY,
                amount=Decimal(str(amount)),
                period=BudgetPeriod.WEEKLY,
                last_period_surplus=Decimal("0.00"),
                is_active=True,
            )
            db_session.add(budget)
            count += 1

        # Create total monthly budget
        total_monthly = Budget(
            user_id=self.user.id,
            category_id=None,  # NULL for total budget
            budget_type=BudgetType.TOTAL,
            amount=Decimal(str(self.TOTAL_MONTHLY_BUDGET)),
            period=BudgetPeriod.MONTHLY,
            last_period_surplus=Decimal("250.00"),  # Some surplus from last month
            is_active=True,
        )
        db_session.add(total_monthly)
        count += 1

        # Create total weekly budget
        total_weekly = Budget(
            user_id=self.user.id,
            category_id=None,
            budget_type=BudgetType.TOTAL,
            amount=Decimal(str(self.TOTAL_WEEKLY_BUDGET)),
            period=BudgetPeriod.WEEKLY,
            last_period_surplus=Decimal("50.00"),
            is_active=True,
        )
        db_session.add(total_weekly)
        count += 1

        self.stdout_write(f"   Created {count} budgets", indent=3)
        return count
