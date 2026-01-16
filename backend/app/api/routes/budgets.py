# =============================================================================
# Digital Finance Tracker - Budget Routes
# PURPOSE: API endpoints for budget management
# =============================================================================
"""
Budget Routes Module

This module defines API endpoints for budget management:
- GET /api/budgets - List user's budgets with spending info
- POST /api/budgets - Create a new budget
- GET /api/budgets/<id> - Get specific budget
- PUT /api/budgets/<id> - Update a budget
- DELETE /api/budgets/<id> - Delete a budget
- GET /api/budgets/status - Get budget status summary

All endpoints require authentication.

Usage:
    from app.api.routes import budgets_bp
    app.register_blueprint(budgets_bp)
"""

from flask import Blueprint, request, g

from app.auth.decorators import requires_auth
from app.services.budget_service import BudgetService
from app.schemas.budget_schema import (
    budget_create_schema,
    budget_update_schema,
)
from app.utils.errors import ValidationError


# =============================================================================
# BLUEPRINT SETUP
# =============================================================================

bp = Blueprint("budgets", __name__, url_prefix="/api/budgets")


# =============================================================================
# BUDGET ENDPOINTS
# =============================================================================


@bp.route("", methods=["GET"])
@requires_auth
def get_budgets():
    """
    Get all budgets for the authenticated user.

    Returns budgets with current spending information including:
    - Amount spent in current period
    - Remaining budget
    - Percentage used
    - Warning/exceeded status

    Query Parameters:
        active_only (bool): If true, only return active budgets (default: true)

    Returns:
        200: List of budgets with spending data
        401: Not authenticated

    Example Response:
        {
            "success": true,
            "data": [
                {
                    "id": "uuid",
                    "budget_type": "total",
                    "amount": "2000.00",
                    "period": "monthly",
                    "spent": "1400.00",
                    "remaining": "600.00",
                    "percentage_used": 70.0,
                    "is_warning": true,
                    "is_exceeded": false,
                    "last_period_surplus": "150.00"
                },
                {
                    "id": "uuid",
                    "budget_type": "category",
                    "category_id": "uuid",
                    "category_name": "Food & Dining",
                    "amount": "300.00",
                    "spent": "245.00",
                    "remaining": "55.00",
                    "percentage_used": 81.7,
                    "is_warning": true,
                    "is_exceeded": false
                }
            ],
            "message": "Budgets retrieved successfully",
            "meta": {
                "total": 2,
                "active": 2,
                "warning_count": 2,
                "exceeded_count": 0
            }
        }
    """
    user_id = g.current_user.id
    active_only = request.args.get("active_only", "true").lower() == "true"

    budgets = BudgetService.get_budgets_with_spending(user_id, active_only)

    # Calculate meta information
    warning_count = sum(1 for b in budgets if b.get("is_warning"))
    exceeded_count = sum(1 for b in budgets if b.get("is_exceeded"))

    return {
        "success": True,
        "data": budgets,
        "message": "Budgets retrieved successfully",
        "meta": {
            "total": len(budgets),
            "active": sum(1 for b in budgets if b.get("is_active")),
            "warning_count": warning_count,
            "exceeded_count": exceeded_count,
        },
    }, 200


@bp.route("", methods=["POST"])
@requires_auth
def create_budget():
    """
    Create a new budget.

    Request Body:
        budget_type (str): "total" or "category" (required)
        category_id (uuid): Category UUID (required for category type)
        amount (str): Budget limit amount (required)
        period (str): "weekly" or "monthly" (required)
        is_active (bool): Whether budget is active (default: true)

    Returns:
        201: Budget created successfully
        400: Validation error
        401: Not authenticated
        409: Budget already exists for this category/period

    Example Request (Total Budget):
        {
            "budget_type": "total",
            "amount": "2000.00",
            "period": "monthly"
        }

    Example Request (Category Budget):
        {
            "budget_type": "category",
            "category_id": "uuid-string",
            "amount": "300.00",
            "period": "monthly"
        }
    """
    user_id = g.current_user.id
    data = request.get_json() or {}

    # Validate input
    errors = budget_create_schema.validate(data)
    if errors:
        raise ValidationError("Validation failed", details=errors)

    # Load validated data
    validated_data = budget_create_schema.load(data)

    # Create budget
    budget = BudgetService.create_budget(user_id, validated_data)

    return {
        "success": True,
        "data": budget.to_dict(),
        "message": "Budget created successfully",
    }, 201


@bp.route("/<uuid:budget_id>", methods=["GET"])
@requires_auth
def get_budget(budget_id):
    """
    Get a specific budget by ID.

    Path Parameters:
        budget_id (uuid): Budget's UUID

    Returns:
        200: Budget with spending data
        401: Not authenticated
        404: Budget not found

    Example Response:
        {
            "success": true,
            "data": {
                "id": "uuid",
                "budget_type": "category",
                "category_name": "Food & Dining",
                "amount": "300.00",
                "spent": "210.00",
                "remaining": "90.00",
                "percentage_used": 70.0,
                "is_warning": true,
                "is_exceeded": false
            },
            "message": "Budget retrieved successfully"
        }
    """
    user_id = g.current_user.id

    budget = BudgetService.get_budget_by_id(budget_id, user_id)

    # Get spending info
    status = BudgetService.check_budget_status(
        user_id,
        category_id=budget.category_id if budget.category_id else None,
    )

    # Merge budget data with spending status
    budget_dict = budget.to_dict()
    budget_dict.update(
        {
            "spent": status.get("spent"),
            "remaining": status.get("remaining"),
            "percentage_used": status.get("percentage_used"),
            "is_warning": status.get("is_warning"),
            "is_exceeded": status.get("is_exceeded"),
        }
    )

    return {
        "success": True,
        "data": budget_dict,
        "message": "Budget retrieved successfully",
    }, 200


@bp.route("/<uuid:budget_id>", methods=["PUT"])
@requires_auth
def update_budget(budget_id):
    """
    Update an existing budget.

    Cannot change budget_type or category_id after creation.

    Path Parameters:
        budget_id (uuid): Budget's UUID

    Request Body (all optional):
        amount (str): New budget limit amount
        period (str): New period ("weekly" or "monthly")
        is_active (bool): Active status

    Returns:
        200: Budget updated successfully
        400: Validation error
        401: Not authenticated
        404: Budget not found
        409: Conflict with existing budget

    Example Request:
        {
            "amount": "400.00",
            "is_active": true
        }
    """
    user_id = g.current_user.id
    data = request.get_json() or {}

    # Validate input
    errors = budget_update_schema.validate(data)
    if errors:
        raise ValidationError("Validation failed", details=errors)

    # Load validated data
    validated_data = budget_update_schema.load(data)

    # Update budget
    budget = BudgetService.update_budget(budget_id, user_id, validated_data)

    return {
        "success": True,
        "data": budget.to_dict(),
        "message": "Budget updated successfully",
    }, 200


@bp.route("/<uuid:budget_id>", methods=["DELETE"])
@requires_auth
def delete_budget(budget_id):
    """
    Delete a budget.

    Path Parameters:
        budget_id (uuid): Budget's UUID

    Returns:
        200: Budget deleted successfully
        401: Not authenticated
        404: Budget not found

    Example Response:
        {
            "success": true,
            "message": "Budget deleted successfully"
        }
    """
    user_id = g.current_user.id

    BudgetService.delete_budget(budget_id, user_id)

    return {
        "success": True,
        "message": "Budget deleted successfully",
    }, 200


@bp.route("/status", methods=["GET"])
@requires_auth
def get_budget_status():
    """
    Get overall budget status summary for the user.

    Returns a summary including:
    - Total budget status (if set)
    - Category budgets at warning level
    - Exceeded budgets
    - Overall savings from last periods

    Returns:
        200: Budget status summary
        401: Not authenticated

    Example Response:
        {
            "success": true,
            "data": {
                "total_budget": {
                    "has_budget": true,
                    "amount": "2000.00",
                    "spent": "1400.00",
                    "remaining": "600.00",
                    "percentage_used": 70.0,
                    "is_warning": true
                },
                "category_budgets_count": 5,
                "warning_budgets": [
                    {"category_name": "Food & Dining", "percentage_used": 85.0}
                ],
                "exceeded_budgets": [],
                "total_surplus_last_period": "250.00"
            },
            "message": "Budget status retrieved successfully"
        }
    """
    user_id = g.current_user.id

    # Get total budget status
    total_status = BudgetService.check_budget_status(user_id, category_id=None)

    # Get all budgets with spending
    all_budgets = BudgetService.get_budgets_with_spending(user_id, active_only=True)

    # Filter category budgets
    category_budgets = [b for b in all_budgets if b.get("budget_type") == "category"]

    # Get warning and exceeded budgets
    warning_budgets = [
        {
            "category_name": b.get("category_name"),
            "percentage_used": b.get("percentage_used"),
            "remaining": b.get("remaining"),
        }
        for b in category_budgets
        if b.get("is_warning") and not b.get("is_exceeded")
    ]

    exceeded_budgets = [
        {
            "category_name": b.get("category_name"),
            "percentage_used": b.get("percentage_used"),
            "over_by": str(abs(float(b.get("remaining", 0)))),
        }
        for b in category_budgets
        if b.get("is_exceeded")
    ]

    # Calculate total surplus from last period
    from decimal import Decimal

    total_surplus = sum(Decimal(b.get("last_period_surplus", "0")) for b in all_budgets)

    return {
        "success": True,
        "data": {
            "total_budget": total_status if total_status.get("has_budget") else None,
            "category_budgets_count": len(category_budgets),
            "warning_budgets": warning_budgets,
            "exceeded_budgets": exceeded_budgets,
            "total_surplus_last_period": str(total_surplus),
        },
        "message": "Budget status retrieved successfully",
    }, 200


@bp.route("/category/<uuid:category_id>/status", methods=["GET"])
@requires_auth
def get_category_budget_status(category_id):
    """
    Get budget status for a specific category.

    Path Parameters:
        category_id (uuid): Category's UUID

    Returns:
        200: Category budget status
        401: Not authenticated

    Example Response:
        {
            "success": true,
            "data": {
                "has_budget": true,
                "budget_amount": "300.00",
                "spent": "210.00",
                "remaining": "90.00",
                "percentage_used": 70.0,
                "is_warning": true,
                "is_exceeded": false,
                "warning_threshold": 70,
                "last_period_surplus": "50.00"
            },
            "message": "Category budget status retrieved successfully"
        }
    """
    user_id = g.current_user.id

    status = BudgetService.check_budget_status(user_id, category_id=category_id)

    return {
        "success": True,
        "data": status,
        "message": "Category budget status retrieved successfully",
    }, 200


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = ["bp"]
