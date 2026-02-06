# =============================================================================
# Digital Finance Tracker - Jae Data Generator (Orchestrator)
# PURPOSE: Coordinate all data generators for Jae Young Seo's test account
# =============================================================================
"""
Jae Data Generator - Master Orchestrator

This module coordinates all individual data generators to populate
Jae Young Seo's test account with comprehensive, realistic financial data.

Target Data Volume (12 months):
- Recurring transactions: ~240 (20 templates × 12 months)
- Income transactions: ~50+ (salary + freelance + refunds)
- Daily spending: ~1,200+ (12 months × avg 3.5/day)
- Anomalies: ~50+ test cases
- Government & Legal: ~14 transactions
- User overrides: 12 transactions
- AI Sessions: 15 conversations
- Budgets: 13 records
- Notifications: 50+ records
- Alerts: 20+ records
- Loans: 4 records

Total: ~1,600+ transactions with complete financial context
"""

import sys
from datetime import datetime, timezone
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

from tools.data_generators.recurring import RecurringGenerator
from tools.data_generators.income import IncomeGenerator
from tools.data_generators.daily_spending import DailySpendingGenerator
from tools.data_generators.anomalies import (
    AnomalyGenerator,
    UserOverrideGenerator,
    GovernmentLegalGenerator,
)
from tools.data_generators.ai_sessions import AISessionGenerator
from tools.data_generators.budgets import BudgetGenerator
from tools.data_generators.notifications import NotificationGenerator
from tools.data_generators.alerts import AlertGenerator
from tools.data_generators.loans import LoanGenerator


class JaeDataGenerator:
    """
    Master orchestrator for generating comprehensive test data.

    Coordinates all specialized generators to create a complete,
    realistic financial profile for testing the entire application.

    Usage:
        from tools.data_generators import JaeDataGenerator

        generator = JaeDataGenerator(
            user=user,
            categories=categories,
            months_back=12,
        )
        results = generator.generate_all(db.session)
    """

    # Constants for Jae Young Seo's account
    JAE_AUTH0_ID = "google-oauth2|110513262768393412869"
    JAE_EMAIL = "jaeyseo0922@gmail.com"

    def __init__(
        self,
        user: "User",
        categories: list,
        months_back: int = 12,
    ):
        """
        Initialize the orchestrator.

        Args:
            user: The User model instance
            categories: List of Category model instances
            months_back: Number of months of data to generate (default 12)
        """
        self.user = user
        self.categories = categories
        self.months_back = months_back

        # Track results
        self.results: Dict[str, int] = {}
        self._start_time: Optional[datetime] = None

    def _stdout_write(self, message: str) -> None:
        """Write message to stdout with flush."""
        sys.stdout.write(message + "\n")
        sys.stdout.flush()

    def generate_all(self, db_session) -> Dict[str, int]:
        """
        Generate all data types using specialized generators.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            Dictionary with counts for each data type
        """
        self._start_time = datetime.now(timezone.utc)

        self._stdout_write("\n" + "=" * 60)
        self._stdout_write("📊 JaeDataGenerator - Comprehensive Test Data")
        self._stdout_write("=" * 60)
        self._stdout_write(f"User: {self.user.email}")
        self._stdout_write(f"Months of data: {self.months_back}")
        self._stdout_write("-" * 60)

        # Generator configuration with execution order
        generators = [
            ("Recurring Transactions", RecurringGenerator),
            ("Income & Refunds", IncomeGenerator),
            ("Daily Spending", DailySpendingGenerator),
            ("Anomalies", AnomalyGenerator),
            ("User Overrides", UserOverrideGenerator),
            ("Government & Legal", GovernmentLegalGenerator),
            ("AI Chat Sessions", AISessionGenerator),
            ("Budgets", BudgetGenerator),
            ("Notifications", NotificationGenerator),
            ("Alerts", AlertGenerator),
            ("Loans", LoanGenerator),
        ]

        total_transactions = 0
        total_records = 0

        for name, generator_class in generators:
            self._stdout_write(f"\n📦 {name}...")

            try:
                generator = generator_class(
                    user=self.user,
                    categories=self.categories,
                    months_back=self.months_back,
                )
                count = generator.generate(db_session)
                self.results[name] = count
                total_records += count

                # Track transaction counts separately
                if name in [
                    "Recurring Transactions",
                    "Income & Refunds",
                    "Daily Spending",
                    "Anomalies",
                    "User Overrides",
                    "Government & Legal",
                ]:
                    total_transactions += count

            except Exception as e:
                self._stdout_write(f"   ❌ Error: {e}")
                self.results[name] = 0

        # Commit all changes
        self._stdout_write("\n💾 Committing to database...")
        db_session.commit()

        # Print summary
        self._print_summary(total_transactions, total_records)

        return self.results

    def _print_summary(self, total_transactions: int, total_records: int) -> None:
        """Print a summary of generated data."""
        end_time = datetime.now(timezone.utc)
        duration = (end_time - self._start_time).total_seconds()

        self._stdout_write("\n" + "=" * 60)
        self._stdout_write("✅ DATA GENERATION COMPLETE")
        self._stdout_write("=" * 60)

        self._stdout_write("\n📊 Summary by Type:")
        for name, count in self.results.items():
            self._stdout_write(f"   • {name}: {count}")

        self._stdout_write("\n📈 Totals:")
        self._stdout_write(f"   • Transactions: {total_transactions}")
        self._stdout_write(f"   • All Records: {total_records}")
        self._stdout_write(f"   • Duration: {duration:.2f}s")

        self._stdout_write("\n" + "=" * 60)

    @classmethod
    def is_jae_user(cls, user: "User") -> bool:
        """
        Check if the given user is Jae Young Seo.

        Args:
            user: User model instance

        Returns:
            True if user matches Jae's auth0_id or email
        """
        return (
            user.auth0_id == cls.JAE_AUTH0_ID
            or user.email == cls.JAE_EMAIL
        )

    @classmethod
    def get_jae_user(cls, db_session) -> Optional["User"]:
        """
        Retrieve Jae's user record from database.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            User instance or None if not found
        """
        from app.models.user import User

        return User.query.filter(
            (User.auth0_id == cls.JAE_AUTH0_ID) | (User.email == cls.JAE_EMAIL)
        ).first()
