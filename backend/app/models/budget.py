# =============================================================================
# Digital Finance Tracker - Budget Model
# PURPOSE: Budget database model for user spending limits
# =============================================================================
"""
Budget Model Module

This module defines the Budget model for the local database:
- Stores user-defined spending budgets (per category or total)
- Supports weekly and monthly budget periods
- Tracks surplus from previous budget periods
- Foundation for AI spending analysis and alerts

Database Table: budgets
Primary Key: id (UUID)
Foreign Key: user_id (references users.id)
Foreign Key: category_id (optional, references categories.id)

BUDGET TYPES:
    - TOTAL: Overall spending limit (category_id is NULL)
    - CATEGORY: Limit for specific category (category_id required)

BUDGET PERIODS:
    - WEEKLY: Resets every week
    - MONTHLY: Resets every month

AI Foundation:
    Created to support AI spending analysis features:
    - Alert when spending reaches 70% of budget (warning)
    - Alert when budget is exceeded
    - Track historical savings for insights
    - Predict end-of-period spending patterns

Relationship:
    - Many Budgets belong to one User (N:1)
    - Budget may reference a Category (optional for TOTAL type)

Usage:
    from app.models import Budget, BudgetType, BudgetPeriod

    # Create total monthly budget
    total_budget = Budget(
        user_id=user.id,
        budget_type=BudgetType.TOTAL,
        amount=Decimal("2000.00"),
        period=BudgetPeriod.MONTHLY,
    )

    # Create category budget
    food_budget = Budget(
        user_id=user.id,
        category_id=food_category.id,
        budget_type=BudgetType.CATEGORY,
        amount=Decimal("300.00"),
        period=BudgetPeriod.MONTHLY,
    )

Notes:
    - WARNING_THRESHOLD is fixed at 70%
    - No carry over - budgets reset each period
    - last_period_surplus tracks savings from previous period
    - is_active allows pausing budgets without deleting
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Dict, Any, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Numeric, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.extensions import db
from app.models.enums import BudgetType, BudgetPeriod

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category


# =============================================================================
# CONSTANTS
# =============================================================================

# Fixed warning threshold - alert when spending reaches this percentage
WARNING_THRESHOLD = 70  # Alert at 70% of budget spent


# =============================================================================
# BUDGET MODEL
# =============================================================================


class Budget(db.Model):
    """
    Budget model representing a user's spending limit.

    This model stores budgets that can be:
    1. TOTAL - Overall spending limit (category_id is NULL)
    2. CATEGORY - Limit for a specific category

    Attributes:
        id: Primary key UUID
        user_id: Foreign key to User (owner of this budget)
        category_id: Foreign key to Category (NULL for total budget)
        budget_type: 'total' or 'category'
        amount: Budget limit amount
        period: 'weekly' or 'monthly'
        last_period_surplus: Amount saved from previous period
        is_active: Whether budget is active (can pause)
        created_at: Record creation timestamp
        updated_at: Record update timestamp

    Relationships:
        user: Many-to-One with User model
        category: Many-to-One with Category model (optional)

    Example:
        >>> budget = Budget.query.filter_by(
        ...     user_id=user.id,
        ...     budget_type=BudgetType.TOTAL
        ... ).first()
        >>> budget.to_dict()
        {
            "id": "uuid-string",
            "budget_type": "total",
            "amount": "2000.00",
            "period": "monthly",
            "warning_threshold": 70,
            "last_period_surplus": "150.00"
        }
    """

    __tablename__ = "budgets"

    # =========================================================================
    # TABLE CONSTRAINTS
    # =========================================================================

    __table_args__ = (
        # Unique constraint: One budget per user per category per period
        # For total budgets, category_id is NULL (handled by DB)
        UniqueConstraint(
            "user_id",
            "category_id",
            "period",
            name="uq_budget_user_category_period",
        ),
    )

    # =========================================================================
    # PRIMARY KEY
    # =========================================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Primary key UUID",
    )

    # =========================================================================
    # FOREIGN KEYS
    # =========================================================================

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="User who owns this budget",
    )

    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True,  # NULL for total budget
        index=True,
        doc="Category this budget applies to (NULL for total budget)",
    )

    # =========================================================================
    # BUDGET CONFIGURATION
    # =========================================================================

    budget_type: Mapped[BudgetType] = mapped_column(
        Enum(BudgetType, name="budget_type_enum", native_enum=False),
        nullable=False,
        index=True,
        doc="Budget type: 'total' or 'category'",
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        doc="Budget limit amount",
    )

    period: Mapped[BudgetPeriod] = mapped_column(
        Enum(BudgetPeriod, name="budget_period_enum", native_enum=False),
        nullable=False,
        default=BudgetPeriod.MONTHLY,
        index=True,
        doc="Budget reset period: 'weekly' or 'monthly'",
    )

    # =========================================================================
    # SURPLUS TRACKING
    # =========================================================================

    last_period_surplus: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        doc="Amount saved from previous budget period",
    )

    last_period_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the last period ended (for surplus calculation)",
    )

    # =========================================================================
    # STATUS
    # =========================================================================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        doc="Whether budget is active (can pause without deleting)",
    )

    # =========================================================================
    # TIMESTAMPS
    # =========================================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Record creation timestamp",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Record update timestamp",
    )

    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================

    # Many Budgets belong to one User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="budgets",
    )

    # Budget may belong to one Category (NULL for total budget)
    category: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="budgets",
    )

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def warning_threshold(self) -> int:
        """
        Get the warning threshold percentage.

        Returns:
            Fixed warning threshold (70%)
        """
        return WARNING_THRESHOLD

    @property
    def is_total_budget(self) -> bool:
        """
        Check if this is a total budget (not category-specific).

        Returns:
            True if this is a total budget, False otherwise
        """
        return self.budget_type == BudgetType.TOTAL

    @property
    def is_category_budget(self) -> bool:
        """
        Check if this is a category-specific budget.

        Returns:
            True if this is a category budget, False otherwise
        """
        return self.budget_type == BudgetType.CATEGORY

    # =========================================================================
    # METHODS
    # =========================================================================

    def __repr__(self) -> str:
        """String representation of Budget."""
        if self.is_total_budget:
            return f"<Budget TOTAL {self.amount} {self.period.value}>"
        return f"<Budget {self.category_id} {self.amount} {self.period.value}>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert budget to dictionary for API response.

        Returns:
            Dictionary representation of budget

        Example:
            >>> budget.to_dict()
            {
                "id": "uuid-string",
                "user_id": "user-uuid",
                "category_id": "category-uuid",
                "category_name": "Food & Dining",
                "budget_type": "category",
                "amount": "300.00",
                "period": "monthly",
                "warning_threshold": 70,
                "last_period_surplus": "50.00",
                "is_active": true,
                "created_at": "2026-01-15T10:00:00Z",
                "updated_at": "2026-01-15T10:00:00Z"
            }
        """
        result = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "category_id": str(self.category_id) if self.category_id else None,
            "budget_type": self.budget_type.value,
            "amount": str(self.amount),
            "period": self.period.value,
            "warning_threshold": self.warning_threshold,
            "last_period_surplus": str(self.last_period_surplus),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        # Include category name if available
        if self.category:
            result["category_name"] = self.category.name

        return result

    def update_surplus(self, spent_amount: Decimal) -> Decimal:
        """
        Calculate and update surplus from the ending period.

        This should be called when a budget period ends to record
        how much was saved.

        Args:
            spent_amount: Total amount spent during the period

        Returns:
            The surplus amount (budget - spent)

        Example:
            >>> budget.amount = Decimal("300.00")
            >>> surplus = budget.update_surplus(Decimal("250.00"))
            >>> surplus
            Decimal('50.00')
            >>> budget.last_period_surplus
            Decimal('50.00')
        """
        surplus = self.amount - spent_amount
        # Only record positive surplus (savings)
        self.last_period_surplus = max(surplus, Decimal("0.00"))
        self.last_period_end = datetime.now(timezone.utc)
        return self.last_period_surplus

    def check_warning(self, spent_amount: Decimal) -> bool:
        """
        Check if spending has reached the warning threshold.

        Args:
            spent_amount: Amount spent so far in current period

        Returns:
            True if spending >= 70% of budget, False otherwise

        Example:
            >>> budget.amount = Decimal("100.00")
            >>> budget.check_warning(Decimal("70.00"))
            True
            >>> budget.check_warning(Decimal("50.00"))
            False
        """
        if self.amount <= 0:
            return False
        percentage = (spent_amount / self.amount) * 100
        return percentage >= self.warning_threshold

    def check_exceeded(self, spent_amount: Decimal) -> bool:
        """
        Check if budget has been exceeded.

        Args:
            spent_amount: Amount spent so far in current period

        Returns:
            True if spending >= budget amount, False otherwise

        Example:
            >>> budget.amount = Decimal("100.00")
            >>> budget.check_exceeded(Decimal("100.00"))
            True
            >>> budget.check_exceeded(Decimal("99.99"))
            False
        """
        return spent_amount >= self.amount

    def get_percentage_used(self, spent_amount: Decimal) -> float:
        """
        Calculate percentage of budget used.

        Args:
            spent_amount: Amount spent so far in current period

        Returns:
            Percentage of budget used (0-100+)

        Example:
            >>> budget.amount = Decimal("100.00")
            >>> budget.get_percentage_used(Decimal("75.00"))
            75.0
        """
        if self.amount <= 0:
            return 0.0
        return float((spent_amount / self.amount) * 100)

    def get_remaining(self, spent_amount: Decimal) -> Decimal:
        """
        Calculate remaining budget.

        Args:
            spent_amount: Amount spent so far in current period

        Returns:
            Remaining budget (can be negative if exceeded)

        Example:
            >>> budget.amount = Decimal("100.00")
            >>> budget.get_remaining(Decimal("75.00"))
            Decimal('25.00')
        """
        return self.amount - spent_amount


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "Budget",
    "WARNING_THRESHOLD",
]
