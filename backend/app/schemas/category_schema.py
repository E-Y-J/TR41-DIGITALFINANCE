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

from marshmallow import fields, validate

from app.schemas.base import BaseSchema


# =============================================================================
# CATEGORY SCHEMA (FULL)
# =============================================================================


class CategorySchema(BaseSchema):
    """
    Full category schema for API responses.

    Used when returning category data to frontend.
    System categories are read-only; custom categories can be modified.

    Example Response:
        {
            "id": "uuid-string",
            "name": "Food & Dining",
            "description": "Restaurants, groceries, fast food...",
            "category_type": "expense",
            "is_system": true,
            "is_custom": false,
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

    is_custom = fields.Method(
        "get_is_custom",
        dump_only=True,
        metadata={"description": "Whether this is a user-created custom category"},
    )

    def get_is_custom(self, obj):
        """Check if category is user-created."""
        return obj.user_id is not None

    user_id = fields.UUID(
        dump_only=True,
        allow_none=True,
        metadata={"description": "Owner user ID (null for system categories)"},
    )

    display_order = fields.Integer(
        dump_only=True,
        metadata={"description": "Display order for frontend"},
    )

    icon = fields.String(
        dump_only=True,
        allow_none=True,
        metadata={"description": "Icon name for frontend display"},
    )

    color = fields.String(
        dump_only=True,
        allow_none=True,
        metadata={"description": "Hex color code (e.g., #FF6B6B)"},
    )


# =============================================================================
# CATEGORY CREATE/UPDATE SCHEMAS
# =============================================================================


class CategoryCreateSchema(BaseSchema):
    """
    Schema for creating a custom category.

    Request Body Example:
        {
            "name": "Pet Expenses",
            "description": "Pet food, vet visits, grooming",
            "category_type": "expense",
            "icon": "paw",
            "color": "#8B5CF6"
        }
    """

    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100),
        metadata={"description": "Category name (2-100 characters)"},
    )

    description = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=500),
        metadata={"description": "Category description (optional)"},
    )

    category_type = fields.String(
        required=False,
        load_default="expense",
        validate=validate.OneOf(["income", "expense", "both"]),
        metadata={"description": "Category type: income, expense, or both"},
    )

    icon = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50),
        metadata={"description": "Icon name for frontend display"},
    )

    color = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Regexp(r"^#[0-9A-Fa-f]{6}$", error="Must be a valid hex color (e.g., #FF6B6B)"),
        metadata={"description": "Hex color code (e.g., #FF6B6B)"},
    )


class CategoryUpdateSchema(BaseSchema):
    """
    Schema for updating a custom category.

    All fields are optional - only provided fields will be updated.

    Request Body Example:
        {
            "name": "Pet Care",
            "color": "#10B981"
        }
    """

    name = fields.String(
        required=False,
        validate=validate.Length(min=2, max=100),
        metadata={"description": "Category name (2-100 characters)"},
    )

    description = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=500),
        metadata={"description": "Category description"},
    )

    category_type = fields.String(
        required=False,
        validate=validate.OneOf(["income", "expense", "both"]),
        metadata={"description": "Category type: income, expense, or both"},
    )

    icon = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50),
        metadata={"description": "Icon name for frontend display"},
    )

    color = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Regexp(r"^#[0-9A-Fa-f]{6}$", error="Must be a valid hex color (e.g., #FF6B6B)"),
        metadata={"description": "Hex color code (e.g., #FF6B6B)"},
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
category_create_schema = CategoryCreateSchema()
category_update_schema = CategoryUpdateSchema()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Schema classes
    "CategorySchema",
    "CategoryCreateSchema",
    "CategoryUpdateSchema",
    "CategoryResponseSchema",
    "CategoryListResponseSchema",
    # Schema instances
    "category_schema",
    "category_list_schema",
    "category_create_schema",
    "category_update_schema",
]
