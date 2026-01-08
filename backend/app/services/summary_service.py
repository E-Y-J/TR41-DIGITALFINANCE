# =============================================================================
# Digital Finance Tracker - Summary Service
# PURPOSE: Spending summary service for AI-powered financial insights
# =============================================================================
"""
Summary Service Module

AI FOUNDATION - Spending Summary

This module provides the service layer for spending summary operations:
- Daily/Weekly/Monthly/Yearly/YTD spending summaries
- Category-based spending breakdowns
- Spending trends and analytics

Usage:
    from app.services.summary_service import SummaryService

    # Get weekly spending summary
    summary = SummaryService.get_spending_summary(user_id, "weekly")

    # Get category breakdown for a period
    breakdown = SummaryService.get_category_breakdown(user_id, "monthly")

Design Principles:
    - Stateless class methods for all operations
    - Efficient database queries with aggregations
    - Caching-ready structure (can add Flask-Caching later)
    - Consistent response format across all periods
"""

import logging
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID
from decimal import Decimal

from sqlalchemy import func, desc

from app.core.extensions import db
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.enums import TransactionType
from app.utils.errors import ValidationError
from app.utils.helpers import get_date_range_for_period


# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

VALID_PERIODS = ["daily", "weekly", "monthly", "yearly", "ytd"]


# =============================================================================
# SUMMARY SERVICE CLASS
# =============================================================================


class SummaryService:
    """
    Service class for spending summary operations.

    All methods are class methods (no instance needed).
    Provides aggregated spending data across different time periods.

    Supported periods:
        - daily: Current day
        - weekly: Last 7 days
        - monthly: Current calendar month
        - yearly: Current calendar year
        - ytd: Year-to-date (Jan 1 to today)

    Example:
        >>> summary = SummaryService.get_spending_summary(user_id, "weekly")
        >>> print(f"Total spent: ${summary['total_expense']:.2f}")
    """

    # =========================================================================
    # MAIN SUMMARY METHODS
    # =========================================================================

    @classmethod
    def get_spending_summary(
        cls,
        user_id: UUID,
        period: str = "weekly",
    ) -> Dict[str, Any]:
        """
        Get comprehensive spending summary for a period.

        Args:
            user_id: User's UUID
            period: Time period (daily, weekly, monthly, yearly, ytd)

        Returns:
            Dictionary containing:
                - period: Requested period name
                - start_date: Period start date
                - end_date: Period end date
                - total_income: Total income amount
                - total_expense: Total expense amount (positive)
                - net: Income - Expense
                - transaction_count: Number of transactions
                - category_breakdown: List of spending by category
                - top_categories: Top 5 spending categories

        Raises:
            ValidationError: If period is invalid

        Example:
            >>> summary = SummaryService.get_spending_summary(
            ...     user_id, "monthly"
            ... )
            >>> for cat in summary["category_breakdown"]:
            ...     print(f"{cat['name']}: ${cat['amount']:.2f}")
        """
        # Validate period
        if period.lower() not in VALID_PERIODS:
            raise ValidationError(
                f"Invalid period: {period}. Must be one of: {', '.join(VALID_PERIODS)}"
            )

        period = period.lower()

        # Get date range
        start_date, end_date = get_date_range_for_period(period)

        # Get totals
        totals = cls._get_period_totals(user_id, start_date, end_date)

        # Get category breakdown
        category_breakdown = cls._get_category_breakdown(user_id, start_date, end_date)

        # Get transaction count
        transaction_count = cls._get_transaction_count(user_id, start_date, end_date)

        # Build response
        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_income": float(totals["income"]),
            "total_expense": float(totals["expense"]),
            "net": float(totals["income"] - totals["expense"]),
            "transaction_count": transaction_count,
            "category_breakdown": category_breakdown,
            "top_categories": category_breakdown[:5] if category_breakdown else [],
        }

    @classmethod
    def get_category_breakdown(
        cls,
        user_id: UUID,
        period: str = "weekly",
        transaction_type: Optional[TransactionType] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get detailed category breakdown for a period.

        Args:
            user_id: User's UUID
            period: Time period (daily, weekly, monthly, yearly, ytd)
            transaction_type: Optional filter by INCOME or EXPENSE

        Returns:
            List of dictionaries containing:
                - category_id: Category UUID
                - name: Category name
                - amount: Total amount (absolute value)
                - percentage: Percentage of total
                - transaction_count: Number of transactions

        Example:
            >>> breakdown = SummaryService.get_category_breakdown(
            ...     user_id, "monthly", TransactionType.EXPENSE
            ... )
        """
        # Validate period
        if period.lower() not in VALID_PERIODS:
            raise ValidationError(
                f"Invalid period: {period}. Must be one of: {', '.join(VALID_PERIODS)}"
            )

        start_date, end_date = get_date_range_for_period(period.lower())

        return cls._get_category_breakdown(
            user_id, start_date, end_date, transaction_type
        )

    @classmethod
    def get_spending_trends(
        cls,
        user_id: UUID,
        period: str = "monthly",
        num_periods: int = 6,
    ) -> List[Dict[str, Any]]:
        """
        Get spending trends over multiple periods.

        Args:
            user_id: User's UUID
            period: Period type (weekly, monthly)
            num_periods: Number of periods to return (max 12)

        Returns:
            List of period summaries, oldest first

        Example:
            >>> trends = SummaryService.get_spending_trends(
            ...     user_id, "monthly", num_periods=6
            ... )
            >>> for t in trends:
            ...     print(f"{t['period_label']}: ${t['total_expense']:.2f}")
        """
        # PERFORMANCE NOTE: For large datasets with many transactions,
        # consider adding Flask-Caching to cache trend results:
        #   @cache.memoize(timeout=300)
        # This would cache results for 5 minutes per user/period combo.
        # See: https://flask-caching.readthedocs.io/

        num_periods = min(num_periods, 12)  # Max 12 periods

        trends = []
        today = date.today()

        for i in range(num_periods - 1, -1, -1):  # Oldest to newest
            if period == "weekly":
                # Go back i weeks
                week_start = today - timedelta(weeks=i, days=today.weekday())
                week_end = week_start + timedelta(days=6)
                period_start = week_start
                period_end = min(week_end, today)
                period_label = f"Week of {week_start.strftime('%b %d')}"
            elif period == "monthly":
                # Go back i months
                month_offset = i
                target_month = today.month - month_offset
                target_year = today.year
                while target_month <= 0:
                    target_month += 12
                    target_year -= 1
                period_start = date(target_year, target_month, 1)
                # Get last day of month
                if target_month == 12:
                    period_end = date(target_year + 1, 1, 1) - timedelta(days=1)
                else:
                    period_end = date(target_year, target_month + 1, 1) - timedelta(
                        days=1
                    )
                period_end = min(period_end, today)
                period_label = period_start.strftime("%b %Y")
            else:
                raise ValidationError(
                    "Trends only support 'weekly' or 'monthly' periods"
                )

            totals = cls._get_period_totals(user_id, period_start, period_end)

            trends.append(
                {
                    "period_start": period_start.isoformat(),
                    "period_end": period_end.isoformat(),
                    "period_label": period_label,
                    "total_income": float(totals["income"]),
                    "total_expense": float(totals["expense"]),
                    "net": float(totals["income"] - totals["expense"]),
                }
            )

        return trends

    # =========================================================================
    # INTERNAL HELPER METHODS
    # =========================================================================

    @classmethod
    def _get_period_totals(
        cls,
        user_id: UUID,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Decimal]:
        """
        Get income and expense totals for a date range.

        Args:
            user_id: User's UUID
            start_date: Period start date
            end_date: Period end date

        Returns:
            Dictionary with 'income' and 'expense' Decimal values
        """
        # Query for income total
        income_result = (
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.INCOME,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
            )
            .scalar()
        )

        # Query for expense total (stored as negative, so we use abs)
        expense_result = (
            db.session.query(func.coalesce(func.sum(func.abs(Transaction.amount)), 0))
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.EXPENSE,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
            )
            .scalar()
        )

        return {
            "income": Decimal(str(income_result or 0)),
            "expense": Decimal(str(expense_result or 0)),
        }

    @classmethod
    def _get_category_breakdown(
        cls,
        user_id: UUID,
        start_date: date,
        end_date: date,
        transaction_type: Optional[TransactionType] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get spending breakdown by category for a date range.

        Args:
            user_id: User's UUID
            start_date: Period start date
            end_date: Period end date
            transaction_type: Optional filter (defaults to EXPENSE only)

        Returns:
            List of category breakdown dictionaries, sorted by amount desc
        """
        # Default to expense breakdown
        if transaction_type is None:
            transaction_type = TransactionType.EXPENSE

        # Query with category join
        # Note: category_id might be null for old transactions
        query = (
            db.session.query(
                Transaction.category_id,
                Category.name.label("category_name"),
                func.sum(func.abs(Transaction.amount)).label("total_amount"),
                func.count(Transaction.id).label("transaction_count"),
            )
            .outerjoin(Category, Transaction.category_id == Category.id)
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == transaction_type,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
            )
            .group_by(
                Transaction.category_id,
                Category.name,
            )
            .order_by(desc("total_amount"))
        )

        results = query.all()

        # Calculate total for percentages
        total = sum(r.total_amount or 0 for r in results)

        breakdown = []
        for r in results:
            amount = float(r.total_amount or 0)
            percentage = (amount / float(total) * 100) if total > 0 else 0

            breakdown.append(
                {
                    "category_id": str(r.category_id) if r.category_id else None,
                    "name": r.category_name or "Uncategorized",
                    "amount": amount,
                    "percentage": round(percentage, 2),
                    "transaction_count": r.transaction_count,
                }
            )

        return breakdown

    @classmethod
    def _get_transaction_count(
        cls,
        user_id: UUID,
        start_date: date,
        end_date: date,
    ) -> int:
        """
        Get transaction count for a date range.

        Args:
            user_id: User's UUID
            start_date: Period start date
            end_date: Period end date

        Returns:
            Number of transactions
        """
        return Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        ).count()

    # =========================================================================
    # COMPARISON METHODS
    # =========================================================================

    @classmethod
    def get_period_comparison(
        cls,
        user_id: UUID,
        period: str = "weekly",
    ) -> Dict[str, Any]:
        """
        Compare current period with previous period.

        Args:
            user_id: User's UUID
            period: Time period (weekly, monthly)

        Returns:
            Dictionary with current, previous, and change data

        Example:
            >>> comparison = SummaryService.get_period_comparison(
            ...     user_id, "monthly"
            ... )
            >>> print(f"Change: {comparison['expense_change_percent']:.1f}%")
        """
        current = cls.get_spending_summary(user_id, period)

        # Get previous period dates
        today = date.today()
        if period == "weekly":
            prev_end = today - timedelta(days=7)
            prev_start = prev_end - timedelta(days=6)
        elif period == "monthly":
            # Previous month
            first_of_month = date(today.year, today.month, 1)
            prev_end = first_of_month - timedelta(days=1)
            prev_start = date(prev_end.year, prev_end.month, 1)
        else:
            raise ValidationError("Comparison only supports 'weekly' or 'monthly'")

        prev_totals = cls._get_period_totals(user_id, prev_start, prev_end)

        # Calculate changes
        current_expense = current["total_expense"]
        prev_expense = float(prev_totals["expense"])

        if prev_expense > 0:
            expense_change = ((current_expense - prev_expense) / prev_expense) * 100
        else:
            expense_change = 100 if current_expense > 0 else 0

        return {
            "current_period": {
                "start_date": current["start_date"],
                "end_date": current["end_date"],
                "total_expense": current_expense,
                "total_income": current["total_income"],
            },
            "previous_period": {
                "start_date": prev_start.isoformat(),
                "end_date": prev_end.isoformat(),
                "total_expense": prev_expense,
                "total_income": float(prev_totals["income"]),
            },
            "expense_change": round(current_expense - prev_expense, 2),
            "expense_change_percent": round(expense_change, 2),
            "trend": "up"
            if expense_change > 0
            else "down"
            if expense_change < 0
            else "flat",
        }
