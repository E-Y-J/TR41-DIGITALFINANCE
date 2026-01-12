# =============================================================================
# Digital Finance Tracker - Summary Routes
# PURPOSE: Spending summary API routes for financial analytics
# =============================================================================
"""
Summary Routes Module

AI Foundation - Spending Analytics

This module provides API endpoints for spending summary operations:
- GET /api/summary/<period> - Get spending summary for a period
- GET /api/summary/<period>/categories - Get category breakdown
- GET /api/summary/trends - Get spending trends over time
- GET /api/summary/compare/<period> - Compare with previous period

Supported Periods:
    - daily: Current day
    - weekly: Last 7 days
    - monthly: Current calendar month
    - yearly: Current calendar year
    - ytd: Year-to-date (Jan 1 to today)

Usage:
    # Register blueprint in app factory
    from app.api.routes.summary import bp as summary_bp
    app.register_blueprint(summary_bp, url_prefix="/api/summary")
"""

import logging
from flask import Blueprint, request, g

from app.auth.decorators import requires_auth
from app.auth.user_sync import sync_user_from_claims
from app.services.summary_service import SummaryService
from app.models.enums import TransactionType
from app.utils.helpers import success_response
from app.utils.errors import ValidationError


# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# BLUEPRINT SETUP
# =============================================================================

bp = Blueprint("summary", __name__)


# =============================================================================
# GET SPENDING SUMMARY
# =============================================================================


@bp.route("/<period>", methods=["GET"])
@requires_auth
def get_spending_summary(period: str):
    """
    Get comprehensive spending summary for a period.

    Path Parameters:
        period: Time period (daily, weekly, monthly, yearly, ytd)

    Returns:
        200: Spending summary with category breakdown
        400: Invalid period

    Example Response:
        {
            "success": true,
            "data": {
                "period": "weekly",
                "start_date": "2024-01-08",
                "end_date": "2024-01-14",
                "total_income": 5000.00,
                "total_expense": 1250.50,
                "net": 3749.50,
                "transaction_count": 23,
                "category_breakdown": [
                    {
                        "category_id": "uuid",
                        "name": "Food & Dining",
                        "amount": 350.00,
                        "percentage": 28.0,
                        "transaction_count": 12
                    },
                    ...
                ],
                "top_categories": [...]
            },
            "message": "Spending summary retrieved successfully"
        }
    """
    # Sync user from JWT claims
    user = sync_user_from_claims(g.jwt_claims)

    # Get summary
    summary = SummaryService.get_spending_summary(user.id, period)

    return success_response(
        data=summary,
        message="Spending summary retrieved successfully",
    )


# =============================================================================
# GET CATEGORY BREAKDOWN
# =============================================================================


@bp.route("/<period>/categories", methods=["GET"])
@requires_auth
def get_category_breakdown(period: str):
    """
    Get detailed category breakdown for a period.

    Path Parameters:
        period: Time period (daily, weekly, monthly, yearly, ytd)

    Query Parameters:
        type (str, optional): Filter by transaction type (income, expense)

    Returns:
        200: Category breakdown list
        400: Invalid period or type

    Example Response:
        {
            "success": true,
            "data": [
                {
                    "category_id": "uuid",
                    "name": "Food & Dining",
                    "amount": 350.00,
                    "percentage": 28.0,
                    "transaction_count": 12
                },
                ...
            ],
            "message": "Category breakdown retrieved successfully"
        }
    """
    # Sync user from JWT claims
    user = sync_user_from_claims(g.jwt_claims)

    # Parse optional type filter
    transaction_type = None
    type_param = request.args.get("type", "").lower()
    if type_param:
        try:
            transaction_type = TransactionType(type_param)
        except ValueError:
            raise ValidationError(
                f"Invalid type: {type_param}. Must be 'income' or 'expense'"
            )

    # Get breakdown
    breakdown = SummaryService.get_category_breakdown(user.id, period, transaction_type)

    return success_response(
        data=breakdown,
        message="Category breakdown retrieved successfully",
    )


# =============================================================================
# GET SPENDING TRENDS
# =============================================================================


@bp.route("/trends", methods=["GET"])
@requires_auth
def get_spending_trends():
    """
    Get spending trends over multiple periods.

    Query Parameters:
        period (str): Period type (weekly, monthly) - default: monthly
        num_periods (int): Number of periods to return (1-12) - default: 6

    Returns:
        200: List of period summaries
        400: Invalid parameters

    Example Response:
        {
            "success": true,
            "data": [
                {
                    "period_start": "2023-08-01",
                    "period_end": "2023-08-31",
                    "period_label": "Aug 2023",
                    "total_income": 5000.00,
                    "total_expense": 2500.00,
                    "net": 2500.00
                },
                ...
            ],
            "message": "Spending trends retrieved successfully"
        }
    """
    # Sync user from JWT claims
    user = sync_user_from_claims(g.jwt_claims)

    # Parse parameters - validation happens in service layer
    period = request.args.get("period", "monthly").lower()
    num_periods = request.args.get("num_periods", 6, type=int)
    num_periods = max(1, min(num_periods, 12))  # Clamp to 1-12

    # Get trends (service validates period)
    trends = SummaryService.get_spending_trends(user.id, period, num_periods)

    return success_response(
        data=trends,
        message="Spending trends retrieved successfully",
    )


# =============================================================================
# COMPARE WITH PREVIOUS PERIOD
# =============================================================================


@bp.route("/compare/<period>", methods=["GET"])
@requires_auth
def get_period_comparison(period: str):
    """
    Compare current period with previous period.

    Path Parameters:
        period: Period type (weekly, monthly)

    Returns:
        200: Comparison data with change metrics
        400: Invalid period

    Example Response:
        {
            "success": true,
            "data": {
                "current_period": {
                    "start_date": "2024-01-08",
                    "end_date": "2024-01-14",
                    "total_expense": 1250.50,
                    "total_income": 5000.00
                },
                "previous_period": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-07",
                    "total_expense": 1100.00,
                    "total_income": 4500.00
                },
                "expense_change": 150.50,
                "expense_change_percent": 13.68,
                "trend": "up"
            },
            "message": "Period comparison retrieved successfully"
        }
    """
    # Sync user from JWT claims
    user = sync_user_from_claims(g.jwt_claims)

    # Validate period
    if period.lower() not in ["weekly", "monthly"]:
        raise ValidationError(
            f"Invalid period: {period}. Comparison only supports 'weekly' or 'monthly'"
        )

    # Get comparison
    comparison = SummaryService.get_period_comparison(user.id, period)

    return success_response(
        data=comparison,
        message="Period comparison retrieved successfully",
    )
