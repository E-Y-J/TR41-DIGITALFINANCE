# =============================================================================
# Digital Finance Tracker - Transaction Routes
# PURPOSE: Transaction API routes for CRUD operations
# =============================================================================
"""
Transaction Routes Module

This module provides API endpoints for transaction operations:
- GET    /api/transactions       - List user's transactions (paginated)
- GET    /api/transactions/:id   - Get single transaction
- POST   /api/transactions       - Create new transaction
- PATCH  /api/transactions/:id   - Update transaction
- DELETE /api/transactions/:id   - Delete transaction
- GET    /api/transactions/summary - Get transaction summary

All endpoints require authentication via @requires_auth decorator.

Usage:
    # Register blueprint in app factory
    from app.api.routes.transactions import bp as transactions_bp
    app.register_blueprint(transactions_bp, url_prefix="/api/transactions")

Response Format:
    {
        "success": true,
        "data": {...},
        "message": "Optional message",
        "meta": {...}  // For paginated responses
    }
"""

import logging
from flask import Blueprint, request, g

from app.auth.decorators import requires_auth
from app.auth.user_sync import sync_user_from_claims
from app.services.transaction_service import TransactionService
from app.schemas.transaction_schema import transaction_schema, transaction_list_schema
from app.utils.errors import ValidationError
from app.utils.helpers import success_response, parse_uuid


# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# BLUEPRINT SETUP
# =============================================================================

bp = Blueprint("transactions", __name__)


# =============================================================================
# TRANSACTION LIST & CREATE
# =============================================================================


@bp.route("", methods=["GET"])
@requires_auth
def list_transactions():
    """
    Get paginated list of user's transactions.

    Query Parameters:
        page (int): Page number, default 1
        per_page (int): Items per page, default 20, max 100
        transaction_type (str): Filter by 'income' or 'expense'
        category_id (str): Filter by category UUID
        category_name (str): Filter by category name (will be resolved to ID)
        merchant_name (str): Filter by merchant name
        start_date (str): Filter by start date (YYYY-MM-DD)
        end_date (str): Filter by end date (YYYY-MM-DD)
        sort_by (str): Sort field ('date', 'amount', 'created_at')
        sort_order (str): 'asc' or 'desc'

    Returns:
        200: Paginated list of transactions

    Example Request:
        GET /api/transactions?page=1&per_page=20&transaction_type=expense

    Example Response:
        {
            "success": true,
            "data": [
                {
                    "id": "uuid-string",
                    "amount": "50.00",
                    "transaction_type": "expense",
                    "date": "2025-12-19",
                    "merchant_name": "Grocery Store",
                    "category": "Food"
                },
                ...
            ],
            "meta": {
                "page": 1,
                "per_page": 20,
                "total": 150,
                "total_pages": 8
            },
            "message": "Transactions retrieved successfully"
        }
    """
    # Get current user
    user = sync_user_from_claims(g.current_user)

    # Parse query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    transaction_type = request.args.get("transaction_type")

    raw_category_id = request.args.get("category_id")
    category_id = parse_uuid(raw_category_id, "category_id") if raw_category_id else None

    # category name filter (e.g. "Government & Legal")
    category_name = request.args.get("category")

    merchant_query = request.args.get("merchant_name")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    sort_by = request.args.get("sort_by", "date")
    sort_order = request.args.get("sort_order", "desc")

    # Get transactions
    transactions, meta = TransactionService.get_user_transactions(
        user=user,
        page=page,
        per_page=per_page,
        transaction_type=transaction_type,
        category_id=category_id,
        category_name=category_name,
        merchant_name=merchant_query,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    # Serialize response
    data = transaction_list_schema.dump(transactions)

    return success_response(
        data=data, message="Transactions retrieved successfully", meta=meta
    )


@bp.route("", methods=["POST"])
@requires_auth
def create_transaction():
    """
    Create a new transaction.

    Request Body:
        amount (str/number): Transaction amount (required)
        transaction_type (str): 'income' or 'expense' (required)
        date (str): Transaction date YYYY-MM-DD (required)
        merchant_name (str): Merchant/source name (optional)
        category (str): Category name (optional)

    Returns:
        201: Created transaction
        400: Invalid request body
        422: Validation error

    Example Request:
        POST /api/transactions
        Authorization: Bearer <access_token>
        Content-Type: application/json

        {
            "amount": "50.00",
            "transaction_type": "expense",
            "date": "2025-12-19",
            "merchant_name": "Grocery Store",
            "category": "Food"
        }

    Example Response:
        {
            "success": true,
            "data": {
                "id": "uuid-string",
                "amount": "50.00",
                "transaction_type": "expense",
                ...
            },
            "message": "Transaction created successfully"
        }
    """
    # Get request data
    data = request.get_json()

    if not data:
        raise ValidationError("Request body required")

    # Get current user
    user = sync_user_from_claims(g.current_user)

    # Create transaction
    transaction = TransactionService.create_transaction(user, data)

    # Serialize response
    response_data = transaction_schema.dump(transaction)

    return success_response(
        data=response_data, message="Transaction created successfully", status_code=201
    )


# =============================================================================
# TRANSACTION DETAIL OPERATIONS
# =============================================================================


@bp.route("/<transaction_id>", methods=["GET"])
@requires_auth
def get_transaction(transaction_id: str):
    """
    Get a single transaction by ID.

    Path Parameters:
        transaction_id: Transaction UUID

    Returns:
        200: Transaction details
        403: Access denied
        404: Transaction not found

    Example Request:
        GET /api/transactions/123e4567-e89b-12d3-a456-426614174000

    Example Response:
        {
            "success": true,
            "data": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "amount": "50.00",
                "transaction_type": "expense",
                "date": "2025-12-19",
                "merchant_name": "Grocery Store",
                "category": "Food",
                "created_at": "2025-12-19T10:30:00Z",
                "updated_at": "2025-12-19T10:30:00Z"
            },
            "message": "Transaction retrieved successfully"
        }
    """
    # Parse UUID
    tx_id = parse_uuid(transaction_id)

    # Get current user
    user = sync_user_from_claims(g.current_user)

    # Get transaction (validates ownership)
    transaction = TransactionService.get_user_transaction(user, tx_id)

    # Serialize response
    response_data = transaction_schema.dump(transaction)

    return success_response(
        data=response_data, message="Transaction retrieved successfully"
    )


@bp.route("/<transaction_id>", methods=["PATCH"])
@requires_auth
def update_transaction(transaction_id: str):
    """
    Update a transaction.

    Path Parameters:
        transaction_id: Transaction UUID

    Request Body (all optional):
        amount (str/number): New amount
        transaction_type (str): 'income' or 'expense'
        date (str): New date YYYY-MM-DD
        merchant_name (str): New merchant name
        category (str): New category

    Returns:
        200: Updated transaction
        400: Invalid request body
        403: Access denied
        404: Transaction not found
        422: Validation error

    Example Request:
        PATCH /api/transactions/123e4567-e89b-12d3-a456-426614174000
        Authorization: Bearer <access_token>
        Content-Type: application/json

        {
            "amount": "75.00",
            "category": "Dining"
        }

    Example Response:
        {
            "success": true,
            "data": {...updated transaction...},
            "message": "Transaction updated successfully"
        }
    """
    # Parse UUID
    tx_id = parse_uuid(transaction_id)

    # Get request data
    data = request.get_json()

    if not data:
        raise ValidationError("Request body required")

    # Get current user
    user = sync_user_from_claims(g.current_user)

    # Update transaction
    transaction = TransactionService.update_transaction(user, tx_id, data)

    # Serialize response
    response_data = transaction_schema.dump(transaction)

    return success_response(
        data=response_data, message="Transaction updated successfully"
    )


@bp.route("/<transaction_id>", methods=["DELETE"])
@requires_auth
def delete_transaction(transaction_id: str):
    """
    Delete a transaction.

    Path Parameters:
        transaction_id: Transaction UUID

    Returns:
        200: Deletion confirmed
        403: Access denied
        404: Transaction not found

    Example Request:
        DELETE /api/transactions/123e4567-e89b-12d3-a456-426614174000
        Authorization: Bearer <access_token>

    Example Response:
        {
            "success": true,
            "message": "Transaction deleted successfully"
        }
    """
    # Parse UUID
    tx_id = parse_uuid(transaction_id)

    # Get current user
    user = sync_user_from_claims(g.current_user)

    # Delete transaction
    TransactionService.delete_transaction(user, tx_id)

    return success_response(message="Transaction deleted successfully")


# =============================================================================
# TRANSACTION SUMMARY
# =============================================================================


@bp.route("/summary", methods=["GET"])
@requires_auth
def get_summary():
    """
    Get transaction summary for current user.

    Query Parameters:
        start_date (str): Filter by start date (YYYY-MM-DD)
        end_date (str): Filter by end date (YYYY-MM-DD)

    Returns:
        200: Transaction summary

    Example Request:
        GET /api/transactions/summary?start_date=2025-12-01&end_date=2025-12-31

    Example Response:
        {
            "success": true,
            "data": {
                "total_income": "5000.00",
                "total_expense": "3500.00",
                "net_balance": "1500.00",
                "income_count": 5,
                "expense_count": 25
            },
            "message": "Summary retrieved successfully"
        }
    """
    user = sync_user_from_claims(g.current_user)

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    summary = TransactionService.get_user_summary(
        user=user, start_date=start_date, end_date=end_date
    )
    
    category_totals = TransactionService.get_category_breakdown(
        user=user, start_date=start_date, end_date=end_date
    )

    serialized_summary = {
        "total_income": str(summary["total_income"]),
        "total_expense": str(summary["total_expense"]),
        "net_balance": str(summary["net_balance"]),
        "income_count": summary["income_count"],
        "expense_count": summary["expense_count"],
        "categories": category_totals
    }

    return success_response(
        data=serialized_summary, message="Summary retrieved successfully"
    )
    
    
# =============================================================================
# MONTHLY TREND 
# =============================================================================

@bp.route("/trend", methods=["GET"])
@requires_auth
def get_monthly_trend():
    """
    Get month-by-month expense totals for a line chart.
    """
    user = sync_user_from_claims(g.current_user)
    start_date = request.args.get("start_date")
    category = request.args.get("category") 

    
    trend_data = TransactionService.get_monthly_trend(
        user=user, 
        start_date=start_date, 
        category=category
    )
    
    return success_response(
        data=trend_data, 
        message="Monthly trend retrieved successfully"
    )


# =============================================================================
# CATEGORY OVERRIDE (User Manual Override)
# =============================================================================


@bp.route("/<transaction_id>/category", methods=["PATCH"])
@requires_auth
def update_category(transaction_id: str):
    """
    Update a transaction's category (user override).

    AI Foundation:
    Allows users to manually correct AI-assigned categories.
    The original AI-assigned category is preserved for analytics.

    Path Parameters:
        transaction_id: Transaction UUID

    Request Body:
        {
            "category_id": "uuid-of-new-category"
        }

    Returns:
        200: Updated transaction
        400: Invalid UUID or missing category_id
        403: Transaction doesn't belong to user
        404: Transaction or category not found

    Example Request:
        PATCH /api/transactions/abc123/category
        {
            "category_id": "food-dining-uuid"
        }

    Example Response:
        {
            "success": true,
            "data": {
                "id": "abc123",
                "category_id": "food-dining-uuid",
                "category": {
                    "id": "food-dining-uuid",
                    "name": "Food & Dining"
                },
                "is_user_override": true,
                "ai_source": "user",
                ...
            },
            "message": "Category updated successfully"
        }
    """
    # Parse and validate transaction UUID
    tx_id = parse_uuid(transaction_id, "transaction_id")

    # Get current user
    user = sync_user_from_claims(g.current_user)

    # Get request body
    data = request.get_json() or {}

    # Validate category_id is provided
    if "category_id" not in data:
        raise ValidationError("category_id is required")

    # Parse and validate category UUID
    category_id = parse_uuid(data["category_id"], "category_id")

    # Update category
    transaction = TransactionService.update_category(user, tx_id, category_id)

    return success_response(
        data=transaction_schema.dump(transaction),
        message="Category updated successfully",
    )


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "bp",
]
