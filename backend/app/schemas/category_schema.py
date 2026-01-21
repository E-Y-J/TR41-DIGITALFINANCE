# =============================================================================
# Digital Finance Tracker - Category Schemas
# PURPOSE: Marshmallow schemas for Category validation and serialization
# =============================================================================
"""
Category Schema Module

This module provides Marshmallow schemas for Category data:
- Serialization of Category objects for API responses
- Minimal validation (categories are read-only for users)

Categories are system-managed, so no create/update schemas needed.

Usage:
    from app.schemas.category_schema import CategorySchema, category_schema

    # Serialize single category
    data = category_schema.dump(category)

    # Serialize list of categories
    data = category_list_schema.dump(categories)

Schema Types:
    - CategorySchema: Full category data (for responses)
    - CategoryListSchema: For serializing lists
"""

from marshmallow import fields

from app.schemas.base import BaseSchema


# =============================================================================
# CATEGORY SCHEMA (FULL)
# =============================================================================


class CategorySchema(BaseSchema):
    """
    Full category schema for API responses.

    Used when returning category data to frontend.
    Categories are read-only for users.

    Example Response:
        {
            "id": "uuid-string",
            "name": "Food & Dining",
            "description": "Restaurants, groceries, fast food...",
            "category_type": "expense",
            "display_order": 1
        }
    """

    # Identity fields
    id = fields.UUID(dump_only=True, metadata={"description": "Category ID"})

    # Category fields
    name = fields.String(
        dump_only=True,
        metadata={"description": "Category name"},
    )

    description = fields.String(
        dump_only=True,
        allow_none=True,
        metadata={"description": "Category description"},
    )

    category_type = fields.Method(
        "get_category_type",
        dump_only=True,
        metadata={"description": "Category type: income, expense, or both"},
    )

    def get_category_type(self, obj):
        """Extract the enum value as a string."""
        if hasattr(obj.category_type, "value"):
            return obj.category_type.value
        return str(obj.category_type)

    is_system = fields.Boolean(
        dump_only=True,
        metadata={"description": "Whether this is a system category"},
    )

    display_order = fields.Integer(
        dump_only=True,
        metadata={"description": "Display order for frontend"},
    )


# =============================================================================
# CATEGORY RESPONSE SCHEMA
# =============================================================================


class CategoryResponseSchema(BaseSchema):
    """
    Schema for category API responses.

    Wraps category data in standard response format.

    Example:
        {
            "success": true,
            "data": {...category...},
            "message": "Category retrieved"
        }
    """

    success = fields.Boolean(dump_only=True)
    message = fields.String(dump_only=True)
    data = fields.Nested(CategorySchema, dump_only=True)


class CategoryListResponseSchema(BaseSchema):
    """
    Schema for category list API responses.

    Example:
        {
            "success": true,
            "data": [...categories...],
            "message": "Categories retrieved"
        }
    """

    success = fields.Boolean(dump_only=True)
    message = fields.String(dump_only=True)
    data = fields.List(fields.Nested(CategorySchema), dump_only=True)


# =============================================================================
# SCHEMA INSTANCES
# =============================================================================

# Singleton instances for reuse
category_schema = CategorySchema()
category_list_schema = CategorySchema(many=True)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Schema classes
    "CategorySchema",
    "CategoryResponseSchema",
    "CategoryListResponseSchema",
    # Schema instances
    "category_schema",
    "category_list_schema",
]
