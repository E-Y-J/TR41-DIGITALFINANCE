# =============================================================================
# Digital Finance Tracker - Categories Routes
# PURPOSE: Category API routes for retrieving and managing categories
# =============================================================================
"""
Categories Routes Module

AI Foundation - Categorization Support

This module provides API endpoints for category operations:
- GET    /api/categories       - Get all categories (system + user's custom)
- POST   /api/categories       - Create a custom category
- GET    /api/categories/<id>  - Get category by ID
- PUT    /api/categories/<id>  - Update a custom category
- DELETE /api/categories/<id>  - Delete a custom category

System categories (11 default) are read-only. Users can create custom
categories that integrate with the AI learning system.

The 11 default system categories are:
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

Custom Category + AI Integration:
    - AI always predicts system categories first
    - User can override to custom category
    - User Learning records the mapping
    - Future transactions auto-categorize to custom category

Usage:
    # Register blueprint in app factory
    from app.api.routes.categories import bp as categories_bp
    app.register_blueprint(categories_bp, url_prefix="/api/categories")
"""

import logging
from flask import Blueprint, request, g

from app.auth.decorators import requires_auth
from app.auth.user_sync import sync_user_from_claims
from app.services.category_service import CategoryService
from app.schemas.category_schema import (
    category_schema,
    category_list_schema,
    category_create_schema,
    category_update_schema,
)
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
    Get all categories available to the user (system + custom).

    Returns system categories plus user's custom categories.

    Query Parameters:
        type (str, optional): Filter by category type (income, expense, both)
        custom_only (bool, optional): Return only user's custom categories

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
                    "is_system": true,
                    "is_custom": false,
                    "icon": "utensils",
                    "color": "#FF6B6B"
                },
                {
                    "id": "uuid",
                    "name": "Pet Expenses",
                    "description": "Pet food, vet, grooming",
                    "category_type": "expense",
                    "is_system": false,
                    "is_custom": true,
                    "icon": "paw",
                    "color": "#8B5CF6"
                }
            ],
            "message": "Categories retrieved successfully"
        }
    """
    user = sync_user_from_claims(g.current_user, g.access_token)

    # Check if only custom categories requested
    custom_only = request.args.get("custom_only", "").lower() == "true"

    if custom_only:
        categories = CategoryService.get_user_custom_categories(user.id)
    else:
        # Get optional type filter
        type_filter = request.args.get("type", "").lower()

        if type_filter:
            try:
                category_type = CategoryType(type_filter)
                # Get all categories for user, then filter by type
                all_categories = CategoryService.get_for_user(user.id)
                categories = [
                    c
                    for c in all_categories
                    if c.category_type == category_type
                    or c.category_type == CategoryType.BOTH
                ]
            except ValueError:
                raise ValidationError(
                    f"Invalid category type: {type_filter}. "
                    f"Must be one of: income, expense, both"
                )
        else:
            categories = CategoryService.get_for_user(user.id)

    return success_response(
        data=category_list_schema.dump(categories),
        message="Categories retrieved successfully",
    )


# =============================================================================
# CREATE CUSTOM CATEGORY
# =============================================================================


@bp.route("", methods=["POST"])
@requires_auth
def create_category():
    """
    Create a custom category.

    Users can create their own categories for personalized tracking.
    Custom categories integrate with the AI learning system.

    Request Body:
        name (str, required): Category name (2-100 characters)
        description (str, optional): Category description
        category_type (str, optional): "income", "expense", or "both" (default: expense)
        icon (str, optional): Icon name for frontend
        color (str, optional): Hex color code (e.g., #FF6B6B)

    Returns:
        201: Category created successfully
        400: Validation error
        409: Category name already exists

    Example Request:
        {
            "name": "Pet Expenses",
            "description": "Pet food, vet visits, grooming",
            "category_type": "expense",
            "color": "#8B5CF6"
        }
    """
    user = sync_user_from_claims(g.current_user, g.access_token)
    data = request.get_json() or {}

    # Validate input
    errors = category_create_schema.validate(data)
    if errors:
        raise ValidationError("Validation failed", details=errors)

    validated = category_create_schema.load(data)

    # Convert category_type string to enum
    category_type = CategoryType(validated.get("category_type", "expense"))

    # Create the category
    category = CategoryService.create_custom_category(
        user_id=user.id,
        name=validated["name"],
        description=validated.get("description"),
        category_type=category_type,
        icon=validated.get("icon"),
        color=validated.get("color"),
    )

    return {
        "success": True,
        "data": category.to_dict(),
        "message": "Category created successfully",
    }, 201


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
                "is_system": true,
                "is_custom": false,
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


# =============================================================================
# UPDATE CUSTOM CATEGORY
# =============================================================================


@bp.route("/<category_id>", methods=["PUT"])
@requires_auth
def update_category(category_id: str):
    """
    Update a custom category.

    Only custom categories (user-created) can be updated.
    System categories cannot be modified.

    Path Parameters:
        category_id: Category UUID

    Request Body (all optional):
        name (str): New category name
        description (str): New description
        category_type (str): "income", "expense", or "both"
        icon (str): Icon name
        color (str): Hex color code

    Returns:
        200: Category updated successfully
        400: Validation error
        403: Cannot modify system category
        404: Category not found
        409: Name conflict

    Example Request:
        {
            "name": "Pet Care",
            "color": "#10B981"
        }
    """
    user = sync_user_from_claims(g.current_user, g.access_token)
    uuid_obj = parse_uuid(category_id, "category_id")
    data = request.get_json() or {}

    # Validate input
    errors = category_update_schema.validate(data)
    if errors:
        raise ValidationError("Validation failed", details=errors)

    validated = category_update_schema.load(data)

    # Convert category_type if provided
    if "category_type" in validated and validated["category_type"]:
        validated["category_type"] = CategoryType(validated["category_type"])

    # Update the category
    category = CategoryService.update_custom_category(
        category_id=uuid_obj,
        user_id=user.id,
        **validated,
    )

    return {
        "success": True,
        "data": category.to_dict(),
        "message": "Category updated successfully",
    }, 200


# =============================================================================
# DELETE CUSTOM CATEGORY
# =============================================================================


@bp.route("/<category_id>", methods=["DELETE"])
@requires_auth
def delete_category(category_id: str):
    """
    Delete a custom category.

    Only custom categories (user-created) can be deleted.
    System categories cannot be deleted.

    Transactions using this category will be reassigned to:
    - The category specified in reassign_to, OR
    - The "Unknown" category (default)

    Path Parameters:
        category_id: Category UUID

    Query Parameters:
        reassign_to (uuid, optional): Category to reassign transactions to

    Returns:
        200: Category deleted successfully
        400: Validation error
        403: Cannot delete system category
        404: Category not found

    Example Response:
        {
            "success": true,
            "message": "Category deleted successfully"
        }
    """
    user = sync_user_from_claims(g.current_user, g.access_token)
    uuid_obj = parse_uuid(category_id, "category_id")

    # Optional reassignment target
    reassign_to = request.args.get("reassign_to")
    reassign_uuid = parse_uuid(reassign_to, "reassign_to") if reassign_to else None

    # Delete the category
    CategoryService.delete_custom_category(
        category_id=uuid_obj,
        user_id=user.id,
        reassign_to=reassign_uuid,
    )

    return {
        "success": True,
        "message": "Category deleted successfully",
    }, 200
