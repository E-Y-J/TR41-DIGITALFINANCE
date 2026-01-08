# =============================================================================
# Digital Finance Tracker - Categories Routes
# PURPOSE: Category API routes for retrieving spending categories
# =============================================================================
"""
Categories Routes Module

AI Foundation - Categorization Support

This module provides API endpoints for category operations:
- GET /api/categories - Get all categories
- GET /api/categories/<id> - Get category by ID

Categories are pre-defined (seeded) and mostly read-only.
Users cannot create custom categories in the current implementation.

The 11 default categories are:
    - Food & Dining (EXPENSE)
    - Transportation (EXPENSE)
    - Shopping & Retail (EXPENSE)
    - Entertainment & Recreation (EXPENSE)
    - Healthcare & Medical (EXPENSE)
    - Utilities & Services (EXPENSE)
    - Financial Services (BOTH)
    - Income (INCOME)
    - Government & Legal (BOTH)
    - Charity & Donations (EXPENSE)
    - Unknown (BOTH) - Used when AI confidence is too low

Usage:
    # Register blueprint in app factory
    from app.api.routes.categories import bp as categories_bp
    app.register_blueprint(categories_bp, url_prefix="/api/categories")
"""

import logging
from flask import Blueprint, request

from app.auth.decorators import requires_auth
from app.services.category_service import CategoryService
from app.schemas.category_schema import category_schema, category_list_schema
from app.models.enums import CategoryType
from app.utils.helpers import success_response, parse_uuid
from app.utils.errors import ValidationError


# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# BLUEPRINT SETUP
# =============================================================================

bp = Blueprint("categories", __name__)


# =============================================================================
# GET ALL CATEGORIES
# =============================================================================


@bp.route("", methods=["GET"])
@requires_auth
def get_categories():
    """
    Get all categories.

    Query Parameters:
        type (str, optional): Filter by category type (income, expense, both)

    Returns:
        200: List of categories
        400: Invalid type parameter

    Example Response:
        {
            "success": true,
            "data": [
                {
                    "id": "uuid",
                    "name": "Food & Dining",
                    "description": "...",
                    "category_type": "expense",
                    "icon": "utensils",
                    "color": "#FF6B6B"
                },
                ...
            ],
            "message": "Categories retrieved successfully"
        }
    """
    # Get optional type filter
    type_filter = request.args.get("type", "").lower()

    if type_filter:
        try:
            category_type = CategoryType(type_filter)
            categories = CategoryService.get_by_type(category_type)
        except ValueError:
            raise ValidationError(
                f"Invalid category type: {type_filter}. "
                f"Must be one of: income, expense, both"
            )
    else:
        categories = CategoryService.get_all()

    return success_response(
        data=category_list_schema.dump(categories),
        message="Categories retrieved successfully",
    )


# =============================================================================
# GET CATEGORY BY ID
# =============================================================================


@bp.route("/<category_id>", methods=["GET"])
@requires_auth
def get_category(category_id: str):
    """
    Get a specific category by ID.

    Path Parameters:
        category_id: Category UUID

    Returns:
        200: Category details
        400: Invalid UUID format
        404: Category not found

    Example Response:
        {
            "success": true,
            "data": {
                "id": "uuid",
                "name": "Food & Dining",
                "description": "Restaurants, groceries, food delivery",
                "category_type": "expense",
                "icon": "utensils",
                "color": "#FF6B6B"
            },
            "message": "Category retrieved successfully"
        }
    """
    # Parse and validate UUID
    uuid_obj = parse_uuid(category_id, "category_id")

    # Get category
    category = CategoryService.get_by_id(uuid_obj)

    return success_response(
        data=category_schema.dump(category),
        message="Category retrieved successfully",
    )
