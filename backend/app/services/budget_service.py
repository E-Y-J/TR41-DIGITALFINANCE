# =============================================================================
# Digital Finance Tracker - Budget Service
# PURPOSE: Business logic for budget operations
# =============================================================================
"""
Budget Service Module

This module provides business logic for budget management:
- Create/update/delete budgets
- Calculate spending vs budget
- Check warning thresholds
- Track surplus from previous periods

AI Foundation:
    Budget data is used by the AI system to:
    - Generate BUDGET_WARNING alerts at 70% threshold
    - Generate BUDGET_EXCEEDED alerts when limit reached
    - Analyze spending patterns vs user-defined limits
    - Provide personalized budget recommendations

Usage:
    from app.services import BudgetService

    # Get user's budgets with spending info
    budgets = BudgetService.get_budgets_with_spending(user_id)

    # Create a new budget
    budget = BudgetService.create_budget(user_id, data)

    # Check if budget warning should be triggered
    should_warn = BudgetService.check_budget_warning(user_id, category_id)
"""

import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, List, Tuple
from calendar import monthrange

from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
import logging

from app.core.extensions import db
from app.models.budget import Budget, WARNING_THRESHOLD
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.enums import BudgetType, BudgetPeriod, TransactionType
from app.utils.errors import (
    NotFoundError,
    ValidationError,
    ConflictError,
    InternalError,
)

logger = logging.getLogger(__name__)


# =============================================================================
# BUDGET SERVICE
# =============================================================================


class BudgetService:
    """
    Service class for budget operations.

    Provides static methods for:
    - CRUD operations on budgets
    - Spending calculations
    - Warning/exceeded checks
    - Surplus tracking

    All methods are static for easy testing and use without instantiation.
    """

    # =========================================================================
    # PERIOD CALCULATION HELPERS
    # =========================================================================

    @staticmethod
    def get_current_period_dates(period: BudgetPeriod) -> Tuple[datetime, datetime]:
        """
        Get start and end dates for the current budget period.

        Args:
            period: Budget period (WEEKLY or MONTHLY)

        Returns:
            Tuple of (start_date, end_date) as datetime objects

        Example:
            >>> start, end = BudgetService.get_current_period_dates(BudgetPeriod.MONTHLY)
            >>> # If today is Jan 15, 2026:
            >>> # start = Jan 1, 2026 00:00:00
            >>> # end = Jan 31, 2026 23:59:59
        """
        now = datetime.now(timezone.utc)

        if period == BudgetPeriod.WEEKLY:
            # Week starts on Monday
            days_since_monday = now.weekday()
            start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
                days=days_since_monday
            )
            end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        else:  # MONTHLY
            # Month starts on 1st
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            _, last_day = monthrange(now.year, now.month)
            end = now.replace(
                day=last_day, hour=23, minute=59, second=59, microsecond=0
            )

        return start, end

    # =========================================================================
    # SPENDING CALCULATIONS
    # =========================================================================

    @staticmethod
    def calculate_category_spending(
        user_id: uuid.UUID,
        category_id: uuid.UUID,
        period: BudgetPeriod,
    ) -> Decimal:
        """
        Calculate total spending for a category in the current period.

        Args:
            user_id: User's UUID
            category_id: Category's UUID
            period: Budget period (WEEKLY or MONTHLY)

        Returns:
            Total amount spent in the category for the period

        Example:
            >>> spent = BudgetService.calculate_category_spending(
            ...     user_id, food_category_id, BudgetPeriod.MONTHLY
            ... )
            >>> spent
            Decimal('245.50')
        """
        start, end = BudgetService.get_current_period_dates(period)

        # Convert to string format since Transaction.date is stored as string (YYYY-MM-DD)
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")

        result = (
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.category_id == category_id,
                    Transaction.transaction_type == TransactionType.EXPENSE,
                    Transaction.date >= start_str,
                    Transaction.date <= end_str,
                )
            )
            .scalar()
        )

        return Decimal(str(result))

    @staticmethod
    def calculate_total_spending(
        user_id: uuid.UUID,
        period: BudgetPeriod,
    ) -> Decimal:
        """
        Calculate total spending (all categories) in the current period.

        Args:
            user_id: User's UUID
            period: Budget period (WEEKLY or MONTHLY)

        Returns:
            Total amount spent across all categories for the period

        Example:
            >>> spent = BudgetService.calculate_total_spending(
            ...     user_id, BudgetPeriod.MONTHLY
            ... )
            >>> spent
            Decimal('1250.00')
        """
        start, end = BudgetService.get_current_period_dates(period)

        # Convert to string format since Transaction.date is stored as string (YYYY-MM-DD)
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")

        result = (
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == TransactionType.EXPENSE,
                    Transaction.date >= start_str,
                    Transaction.date <= end_str,
                )
            )
            .scalar()
        )

        return Decimal(str(result))

    # =========================================================================
    # CRUD OPERATIONS
    # =========================================================================

    @staticmethod
    def get_budget_by_id(budget_id: uuid.UUID, user_id: uuid.UUID) -> Budget:
        """
        Get a specific budget by ID.

        Args:
            budget_id: Budget's UUID
            user_id: User's UUID (for ownership verification)

        Returns:
            Budget model instance

        Raises:
            NotFoundError: If budget not found or doesn't belong to user
        """
        budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()

        if not budget:
            raise NotFoundError("Budget not found")

        return budget

    @staticmethod
    def get_user_budgets(
        user_id: uuid.UUID,
        active_only: bool = True,
    ) -> List[Budget]:
        """
        Get all budgets for a user.

        Args:
            user_id: User's UUID
            active_only: If True, only return active budgets

        Returns:
            List of Budget model instances
        """
        query = Budget.query.filter_by(user_id=user_id)

        if active_only:
            query = query.filter_by(is_active=True)

        return query.order_by(Budget.budget_type, Budget.created_at).all()

    @staticmethod
    def get_budgets_with_spending(
        user_id: uuid.UUID,
        active_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get all budgets for a user with current spending information.

        This is the main method for dashboard budget display.
        Includes spent amount, remaining, percentage, and warning status.

        Args:
            user_id: User's UUID
            active_only: If True, only return active budgets

        Returns:
            List of budget dictionaries with spending data

        Example:
            >>> budgets = BudgetService.get_budgets_with_spending(user_id)
            >>> budgets[0]
            {
                "id": "uuid",
                "budget_type": "category",
                "category_name": "Food & Dining",
                "amount": "300.00",
                "spent": "210.00",
                "remaining": "90.00",
                "percentage_used": 70.0,
                "is_warning": True,
                "is_exceeded": False,
                ...
            }
        """
        budgets = BudgetService.get_user_budgets(user_id, active_only)
        result = []

        for budget in budgets:
            # Calculate spending based on budget type
            if budget.budget_type == BudgetType.TOTAL:
                spent = BudgetService.calculate_total_spending(user_id, budget.period)
            else:
                spent = BudgetService.calculate_category_spending(
                    user_id, budget.category_id, budget.period
                )

            # Build response dictionary
            budget_dict = budget.to_dict()
            budget_dict["spent"] = str(spent)
            budget_dict["remaining"] = str(budget.get_remaining(spent))
            budget_dict["percentage_used"] = round(budget.get_percentage_used(spent), 1)
            budget_dict["is_warning"] = budget.check_warning(spent)
            budget_dict["is_exceeded"] = budget.check_exceeded(spent)

            result.append(budget_dict)

        return result

    @staticmethod
    def create_budget(user_id: uuid.UUID, data: Dict[str, Any]) -> Budget:
        """
        Create a new budget for a user.

        Args:
            user_id: User's UUID
            data: Validated budget data from schema

        Returns:
            Created Budget model instance

        Raises:
            ValidationError: If category doesn't exist
            ConflictError: If budget already exists for this category/period
        """
        budget_type = BudgetType(data["budget_type"])
        period = BudgetPeriod(data["period"])
        category_id = data.get("category_id")

        # Validate category exists for category budgets
        if budget_type == BudgetType.CATEGORY:
            category = Category.query.get(category_id)
            if not category:
                raise ValidationError("Category not found")

        # Check for existing budget (unique constraint)
        existing = Budget.query.filter_by(
            user_id=user_id,
            category_id=category_id,
            period=period,
        ).first()

        if existing:
            if budget_type == BudgetType.TOTAL:
                raise ConflictError(f"A {period.value} total budget already exists")
            else:
                raise ConflictError(
                    f"A {period.value} budget for this category already exists"
                )

        # Create budget with proper error handling
        try:
            budget = Budget(
                user_id=user_id,
                category_id=category_id,
                budget_type=budget_type,
                amount=Decimal(str(data["amount"])),
                period=period,
                is_active=data.get("is_active", True),
            )

            db.session.add(budget)
            db.session.commit()

            logger.info(f"Created {budget_type.value} budget for user {user_id}")
            return budget

        except IntegrityError:
            db.session.rollback()
            logger.warning(f"Budget conflict for user {user_id}, period {period.value}")
            raise ConflictError("A budget with this configuration already exists")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create budget: {e}", exc_info=True)
            raise InternalError("Failed to create budget")

    @staticmethod
    def update_budget(
        budget_id: uuid.UUID,
        user_id: uuid.UUID,
        data: Dict[str, Any],
    ) -> Budget:
        """
        Update an existing budget.

        Cannot change budget_type or category_id after creation.

        Args:
            budget_id: Budget's UUID
            user_id: User's UUID (for ownership verification)
            data: Validated update data from schema

        Returns:
            Updated Budget model instance

        Raises:
            NotFoundError: If budget not found
        """
        budget = BudgetService.get_budget_by_id(budget_id, user_id)

        # Update allowed fields
        if "amount" in data:
            budget.amount = Decimal(str(data["amount"]))
        if "period" in data:
            # Check if new period would create conflict
            new_period = BudgetPeriod(data["period"])
            existing = Budget.query.filter(
                and_(
                    Budget.user_id == user_id,
                    Budget.category_id == budget.category_id,
                    Budget.period == new_period,
                    Budget.id != budget_id,
                )
            ).first()
            if existing:
                raise ConflictError(
                    f"A {new_period.value} budget already exists for this configuration"
                )
            budget.period = new_period
        if "is_active" in data:
            budget.is_active = data["is_active"]

        try:
            db.session.commit()
            logger.info(f"Updated budget {budget_id}")
            return budget
        except IntegrityError:
            db.session.rollback()
            logger.warning(f"Budget update conflict for budget {budget_id}")
            raise ConflictError("A budget with this configuration already exists")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update budget: {e}", exc_info=True)
            raise InternalError("Failed to update budget")

    @staticmethod
    def delete_budget(budget_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Delete a budget.

        Args:
            budget_id: Budget's UUID
            user_id: User's UUID (for ownership verification)

        Returns:
            True if deleted successfully

        Raises:
            NotFoundError: If budget not found
        """
        budget = BudgetService.get_budget_by_id(budget_id, user_id)
        try:
            db.session.delete(budget)
            db.session.commit()
            logger.info(f"Deleted budget {budget_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete budget: {e}", exc_info=True)
            raise InternalError("Failed to delete budget")

    # =========================================================================
    # WARNING & ALERT CHECKS
    # =========================================================================

    @staticmethod
    def check_budget_status(
        user_id: uuid.UUID,
        category_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """
        Check budget status for a category or total spending.

        Used by AI/alert system to determine if warnings should be triggered.

        Args:
            user_id: User's UUID
            category_id: Category UUID (None for total budget check)

        Returns:
            Dictionary with budget status information

        Example:
            >>> status = BudgetService.check_budget_status(user_id, food_category_id)
            >>> status
            {
                "has_budget": True,
                "budget_amount": "300.00",
                "spent": "220.00",
                "remaining": "80.00",
                "percentage_used": 73.3,
                "is_warning": True,
                "is_exceeded": False,
                "warning_threshold": 70
            }
        """
        # Find the relevant budget
        if category_id:
            budget = Budget.query.filter_by(
                user_id=user_id,
                category_id=category_id,
                is_active=True,
            ).first()
        else:
            budget = Budget.query.filter_by(
                user_id=user_id,
                budget_type=BudgetType.TOTAL,
                is_active=True,
            ).first()

        if not budget:
            return {
                "has_budget": False,
                "budget_amount": None,
                "spent": None,
                "remaining": None,
                "percentage_used": None,
                "is_warning": False,
                "is_exceeded": False,
                "warning_threshold": WARNING_THRESHOLD,
            }

        # Calculate spending
        if budget.budget_type == BudgetType.TOTAL:
            spent = BudgetService.calculate_total_spending(user_id, budget.period)
        else:
            spent = BudgetService.calculate_category_spending(
                user_id, budget.category_id, budget.period
            )

        return {
            "has_budget": True,
            "budget_id": str(budget.id),
            "budget_amount": str(budget.amount),
            "period": budget.period.value,
            "spent": str(spent),
            "remaining": str(budget.get_remaining(spent)),
            "percentage_used": round(budget.get_percentage_used(spent), 1),
            "is_warning": budget.check_warning(spent),
            "is_exceeded": budget.check_exceeded(spent),
            "warning_threshold": WARNING_THRESHOLD,
            "last_period_surplus": str(budget.last_period_surplus),
        }

    @staticmethod
    def get_budgets_needing_warning(user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """
        Get all budgets that have reached warning threshold.

        Used by alert service to generate BUDGET_WARNING alerts.

        Args:
            user_id: User's UUID

        Returns:
            List of budget status dictionaries for budgets at/above 70%
        """
        budgets = BudgetService.get_budgets_with_spending(user_id, active_only=True)
        return [b for b in budgets if b["is_warning"] and not b["is_exceeded"]]

    @staticmethod
    def get_exceeded_budgets(user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """
        Get all budgets that have been exceeded.

        Used by alert service to generate BUDGET_EXCEEDED alerts.

        Args:
            user_id: User's UUID

        Returns:
            List of budget status dictionaries for exceeded budgets
        """
        budgets = BudgetService.get_budgets_with_spending(user_id, active_only=True)
        return [b for b in budgets if b["is_exceeded"]]

    # =========================================================================
    # SURPLUS MANAGEMENT
    # =========================================================================

    @staticmethod
    def record_period_surplus(budget_id: uuid.UUID, user_id: uuid.UUID) -> Decimal:
        """
        Record surplus from the ending budget period.

        Should be called when a budget period ends to track savings.
        This is typically called by a scheduled task.

        Args:
            budget_id: Budget's UUID
            user_id: User's UUID

        Returns:
            The surplus amount recorded

        Example:
            >>> surplus = BudgetService.record_period_surplus(budget_id, user_id)
            >>> surplus
            Decimal('50.00')  # User saved $50 from their budget
        """
        budget = BudgetService.get_budget_by_id(budget_id, user_id)

        # Calculate what was spent in the period
        if budget.budget_type == BudgetType.TOTAL:
            spent = BudgetService.calculate_total_spending(user_id, budget.period)
        else:
            spent = BudgetService.calculate_category_spending(
                user_id, budget.category_id, budget.period
            )

        # Record the surplus
        surplus = budget.update_surplus(spent)
        db.session.commit()

        return surplus

    # =========================================================================
    # ALERT TRIGGER METHODS
    # =========================================================================

    @staticmethod
    def check_and_trigger_budget_alerts(
        user_id: uuid.UUID,
        category_id: Optional[uuid.UUID] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Check budget status and trigger alerts if thresholds are crossed.

        This should be called after a transaction is created/updated.
        Creates BUDGET_WARNING at 70% and BUDGET_EXCEEDED at 100%.

        Args:
            user_id: User's UUID
            category_id: Category UUID to check (also checks total budget)

        Returns:
            Dictionary with alert info if alert was created, None otherwise

        Example:
            >>> # Call after creating a transaction
            >>> alert_info = BudgetService.check_and_trigger_budget_alerts(
            ...     user_id, transaction.category_id
            ... )
            >>> if alert_info:
            ...     print(f"Alert triggered: {alert_info['title']}")
        """
        from app.services.alert_service import AlertService

        alerts_created = []

        # Check category budget if category_id provided
        if category_id:
            category_alert = BudgetService._check_single_budget_alert(
                user_id, category_id, AlertService
            )
            if category_alert:
                alerts_created.append(category_alert)

        # Also check total budget
        total_alert = BudgetService._check_single_budget_alert(
            user_id,
            None,
            AlertService,  # None = total budget
        )
        if total_alert:
            alerts_created.append(total_alert)

        return alerts_created if alerts_created else None

    @staticmethod
    def _check_single_budget_alert(
        user_id: uuid.UUID,
        category_id: Optional[uuid.UUID],
        AlertService,
    ) -> Optional[Dict[str, Any]]:
        """
        Check a single budget and create alert if needed.

        Internal helper method.
        """
        from app.models.enums import AlertType

        # Get budget status
        status = BudgetService.check_budget_status(user_id, category_id)

        if not status.get("has_budget"):
            return None

        budget_id = uuid.UUID(status["budget_id"])
        is_warning = status["is_warning"]
        is_exceeded = status["is_exceeded"]

        # Determine category name
        category_name = None
        if category_id:
            from app.models.category import Category

            category = Category.query.get(category_id)
            if category:
                category_name = category.name

        # Check if EXCEEDED (100%+) - higher priority
        if is_exceeded:
            # Check if we already have an active exceeded alert
            if not AlertService.has_recent_budget_alert(
                user_id, budget_id, AlertType.BUDGET_EXCEEDED
            ):
                alert = AlertService.create_budget_exceeded_alert(
                    user_id=user_id,
                    budget_id=budget_id,
                    category_id=category_id,
                    category_name=category_name,
                    budget_amount=Decimal(status["budget_amount"]),
                    spent_amount=Decimal(status["spent"]),
                    percentage_used=status["percentage_used"],
                    period=status["period"],
                )
                return {
                    "alert_id": str(alert.id),
                    "type": "budget_exceeded",
                    "title": alert.title,
                    "message": alert.message,
                }

        # Check if WARNING (70-99%)
        elif is_warning:
            # Check if we already have an active warning alert
            if not AlertService.has_recent_budget_alert(
                user_id, budget_id, AlertType.BUDGET_WARNING
            ):
                alert = AlertService.create_budget_warning_alert(
                    user_id=user_id,
                    budget_id=budget_id,
                    category_id=category_id,
                    category_name=category_name,
                    budget_amount=Decimal(status["budget_amount"]),
                    spent_amount=Decimal(status["spent"]),
                    percentage_used=status["percentage_used"],
                    period=status["period"],
                )
                return {
                    "alert_id": str(alert.id),
                    "type": "budget_warning",
                    "title": alert.title,
                    "message": alert.message,
                }

        return None


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "BudgetService",
]
