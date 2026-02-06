# =============================================================================
# Digital Finance Tracker - Base Data Generator
# PURPOSE: Base class with common utilities for all data generators
# =============================================================================
"""
Base Generator Module

Provides the foundation for all data generators with:
- Common utilities for date/time manipulation
- Transaction creation helpers
- Console output formatting
- Category mapping utilities
"""

import random
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category
    from app.models.transaction import Transaction


class BaseGenerator:
    """
    Base class for data generators.

    Provides common utilities used by all specialized generators.

    Attributes:
        user: User model instance to generate data for
        categories: List of Category model instances
        cat_map: Dictionary mapping category names to Category objects
        now: Current datetime (UTC)
        months_back: Number of months of historical data to generate

    Example:
        class MyGenerator(BaseGenerator):
            def generate(self):
                # Use self.create_transaction() and other helpers
                pass
    """

    def __init__(
        self,
        user: "User",
        categories: List["Category"],
        months_back: int = 12,
    ):
        """
        Initialize the base generator.

        Args:
            user: User to generate data for
            categories: List of available categories
            months_back: Months of historical data (default 12)
        """
        self.user = user
        self.categories = categories
        self.cat_map = {cat.name: cat for cat in categories}
        self.now = datetime.now(timezone.utc)
        self.months_back = months_back
        self._created_count = 0

    # =========================================================================
    # DATE UTILITIES
    # =========================================================================

    def get_date_months_ago(self, months: int) -> datetime:
        """Get a datetime N months in the past."""
        return self.now - timedelta(days=30 * months)

    def get_date_days_ago(self, days: int) -> datetime:
        """Get a datetime N days in the past."""
        return self.now - timedelta(days=days)

    def get_random_date_in_range(
        self, start_days_ago: int, end_days_ago: int = 0
    ) -> datetime:
        """Get a random datetime within a range of days ago."""
        days_ago = random.randint(end_days_ago, start_days_ago)
        return self.get_date_days_ago(days_ago)

    def get_monthly_date(self, months_ago: int, day: int) -> Optional[datetime]:
        """
        Get a specific day of a month N months ago.

        Args:
            months_ago: Number of months in the past
            day: Day of month (1-28 recommended for safety)

        Returns:
            datetime or None if date would be in future
        """
        target_month = self.get_date_months_ago(months_ago)
        try:
            result = target_month.replace(day=min(day, 28))
            return result if result <= self.now else None
        except ValueError:
            return target_month.replace(day=28)

    def is_weekend(self, dt: datetime) -> bool:
        """Check if a datetime falls on a weekend."""
        return dt.weekday() >= 5

    # =========================================================================
    # AMOUNT UTILITIES
    # =========================================================================

    def random_amount(
        self,
        min_amt: float,
        max_amt: float,
        precision: int = 2,
    ) -> Decimal:
        """
        Generate a random amount between min and max.

        Args:
            min_amt: Minimum amount
            max_amt: Maximum amount
            precision: Decimal places (default 2)

        Returns:
            Decimal amount
        """
        if min_amt == max_amt:
            return Decimal(str(min_amt))
        amount = round(random.uniform(min_amt, max_amt), precision)
        return Decimal(str(amount))

    def vary_amount(
        self,
        base_amount: float,
        variance_pct: float = 0.15,
    ) -> Decimal:
        """
        Add variance to a base amount (for realistic bill variations).

        Args:
            base_amount: Base amount
            variance_pct: Percentage variance (0.15 = ±15%)

        Returns:
            Decimal with variance applied
        """
        multiplier = random.uniform(1 - variance_pct, 1 + variance_pct)
        return Decimal(str(round(base_amount * multiplier, 2)))

    # =========================================================================
    # CATEGORY UTILITIES
    # =========================================================================

    def get_category(self, name: str) -> Optional["Category"]:
        """Get a category by name, or None if not found."""
        return self.cat_map.get(name)

    def get_random_category(self) -> "Category":
        """Get a random category."""
        return random.choice(self.categories)

    # =========================================================================
    # TRANSACTION CREATION
    # =========================================================================

    def create_transaction_dict(
        self,
        amount: Decimal,
        transaction_type: str,
        date: datetime,
        merchant_name: str,
        category_name: str,
        ai_source: Optional[str] = None,
        ai_confidence: Optional[float] = None,
        is_user_override: bool = False,
        original_category_name: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a transaction dictionary for batch creation.

        Args:
            amount: Transaction amount
            transaction_type: 'expense' or 'income'
            date: Transaction date
            merchant_name: Merchant name
            category_name: Category name
            ai_source: AI source value (keyword, huggingface, gemini, user)
            ai_confidence: AI confidence score (0.0-1.0)
            is_user_override: Whether user overrode AI
            original_category_name: Original category if overridden

        Returns:
            Dictionary with transaction fields, or None if category not found
        """
        category = self.get_category(category_name)
        if not category:
            return None

        original_category_id = None
        if original_category_name:
            original_category = self.get_category(original_category_name)
            original_category_id = original_category.id if original_category else None

        return {
            "user_id": self.user.id,
            "amount": amount,
            "transaction_type": transaction_type,
            "date": date.strftime("%Y-%m-%d"),
            "merchant_name": merchant_name,
            "category_id": category.id,
            "ai_source": ai_source,
            "ai_confidence": ai_confidence,
            "is_user_override": is_user_override,
            "original_category_id": original_category_id,
        }

    # =========================================================================
    # OUTPUT UTILITIES
    # =========================================================================

    def stdout_write(self, message: str, indent: int = 0) -> None:
        """
        Print a colored message to console.

        Args:
            message: Message to print
            indent: Number of spaces to indent
        """
        blue = "\033[94m"
        reset = "\033[0m"
        prefix = " " * indent
        print(f"{blue}{prefix}{message}{reset}")

    def increment_count(self, n: int = 1) -> None:
        """Increment the created item counter."""
        self._created_count += n

    def get_count(self) -> int:
        """Get the current created item count."""
        return self._created_count

    def reset_count(self) -> None:
        """Reset the created item counter."""
        self._created_count = 0

    # =========================================================================
    # ABSTRACT METHOD
    # =========================================================================

    def generate(self) -> int:
        """
        Generate data. Override in subclasses.

        Returns:
            Number of items created
        """
        raise NotImplementedError("Subclasses must implement generate()")
