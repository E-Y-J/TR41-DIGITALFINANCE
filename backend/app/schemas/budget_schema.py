# =============================================================================
# Digital Finance Tracker - Budget Schema
# PURPOSE: Marshmallow schemas for budget validation and serialization
# =============================================================================
"""
Budget Schema Module

This module defines Marshmallow schemas for the Budget model:
- BudgetSchema: Full budget serialization
- BudgetCreateSchema: Validation for creating budgets
- BudgetUpdateSchema: Validation for updating budgets
- BudgetResponseSchema: Standard API response wrapper

Usage:
    from app.schemas import BudgetSchema, budget_schema

    # Serialize a budget
    result = budget_schema.dump(budget)

    # Validate create data
    errors = budget_create_schema.validate(request_data)

Notes:
    - amount must be positive
    - category_id required for CATEGORY type, NULL for TOTAL type
    - warning_threshold is fixed at 70% (not editable)
"""

from decimal import Decimal
from typing import Dict, Any

from marshmallow import (
    fields,
    validate,
    validates_schema,
    ValidationError,
    EXCLUDE,
)

from app.schemas.base import BaseSchema
from app.models.enums import BudgetType, BudgetPeriod

# =============================================================================
# BUDGET SCHEMAS
# =============================================================================


class BudgetSchema(BaseSchema):
    """
    Schema for serializing Budget model.

    Used for:
    - API responses (GET /api/budgets)
    - Full budget representation

    Fields:
        id: Budget UUID (read-only)
        user_id: User UUID (read-only)
        category_id: Category UUID (optional, NULL for total budget)
        category_name: Category name (read-only, computed)
        budget_type: 'total' or 'category'
        amount: Budget limit amount
        period: 'weekly' or 'monthly'
        warning_threshold: Alert threshold percentage (fixed 70%)
        last_period_surplus: Savings from previous period
        is_active: Whether budget is active
        created_at: Creation timestamp
        updated_at: Update timestamp
    """

    # Primary key
    id = fields.UUID(dump_only=True)

    # Foreign keys
    user_id = fields.UUID(dump_only=True)
    category_id = fields.UUID(allow_none=True)

    # Computed field
    category_name = fields.String(dump_only=True)

    # Budget configuration
    budget_type = fields.Method(
        "get_budget_type",
        dump_only=True,
        metadata={"description": "Budget type: total or category"},
    )

    def get_budget_type(self, obj):
        """Extract enum value as string."""
        if hasattr(obj.budget_type, "value"):
            return obj.budget_type.value
        return str(obj.budget_type) if obj.budget_type else None

    amount = fields.Decimal(places=2, as_string=True)

    period = fields.Method(
        "get_period",
        dump_only=True,
        metadata={"description": "Budget period: weekly or monthly"},
    )

    def get_period(self, obj):
        """Extract enum value as string."""
        if hasattr(obj.period, "value"):
            return obj.period.value
        return str(obj.period) if obj.period else None

    # Fixed threshold (read-only)
    warning_threshold = fields.Integer(dump_only=True)

    # Surplus tracking
    last_period_surplus = fields.Decimal(places=2, as_string=True, dump_only=True)

    # Status
    is_active = fields.Boolean()

    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class BudgetCreateSchema(BaseSchema):
    """
    Schema for creating a new budget.

    Validates:
    - budget_type is required ('total' or 'category')
    - amount is required and positive
    - period is required ('weekly' or 'monthly')
    - category_id is required for CATEGORY type, must be NULL for TOTAL type

    Example:
        {
            "budget_type": "category",
            "category_id": "uuid-string",
            "amount": "300.00",
            "period": "monthly"
        }
    """

    class Meta:
        """Schema configuration."""

        unknown = EXCLUDE

    budget_type = fields.String(
        required=True,
        validate=validate.OneOf([t.value for t in BudgetType]),
        error_messages={"required": "Budget type is required"},
    )

    category_id = fields.UUID(
        allow_none=True,
        load_default=None,
    )

    amount = fields.Decimal(
        required=True,
        places=2,
        as_string=True,
        validate=validate.Range(min=Decimal("0.01")),
        error_messages={
            "required": "Amount is required",
            "validator_failed": "Amount must be greater than 0",
        },
    )

    period = fields.String(
        required=True,
        validate=validate.OneOf([p.value for p in BudgetPeriod]),
        error_messages={"required": "Period is required"},
    )

    is_active = fields.Boolean(load_default=True)

    @validates_schema
    def validate_category_for_type(self, data: Dict[str, Any], **kwargs) -> None:
        """
        Validate category_id based on budget_type.

        Rules:
        - TOTAL budget: category_id must be NULL
        - CATEGORY budget: category_id is required

        Args:
            data: Validated data dictionary

        Raises:
            ValidationError: If validation fails
        """
        budget_type = data.get("budget_type")
        category_id = data.get("category_id")

        if budget_type == BudgetType.TOTAL.value:
            if category_id is not None:
                raise ValidationError(
                    "Total budget must not have a category_id",
                    field_name="category_id",
                )
        elif budget_type == BudgetType.CATEGORY.value:
            if category_id is None:
                raise ValidationError(
                    "Category budget requires a category_id",
                    field_name="category_id",
                )


class BudgetUpdateSchema(BaseSchema):
    """
    Schema for updating an existing budget.

    All fields are optional - only provided fields will be updated.
    Cannot change budget_type or category_id after creation.

    Example:
        {
            "amount": "400.00",
            "period": "weekly",
            "is_active": false
        }
    """

    class Meta:
        """Schema configuration."""

        unknown = EXCLUDE

    amount = fields.Decimal(
        places=2,
        as_string=True,
        validate=validate.Range(min=Decimal("0.01")),
        error_messages={"validator_failed": "Amount must be greater than 0"},
    )

    period = fields.String(
        validate=validate.OneOf([p.value for p in BudgetPeriod]),
    )

    is_active = fields.Boolean()


class BudgetWithSpendingSchema(BaseSchema):
    """
    Schema for budget with current spending information.

    Used for dashboard and budget overview endpoints.
    Includes computed spending data.

    Fields:
        ... all BudgetSchema fields ...
        spent: Amount spent in current period
        remaining: Budget remaining
        percentage_used: Percentage of budget used
        is_warning: Whether spending has reached warning threshold
        is_exceeded: Whether budget has been exceeded
    """

    # Include all base budget fields
    id = fields.UUID(dump_only=True)
    user_id = fields.UUID(dump_only=True)
    category_id = fields.UUID(allow_none=True)
    category_name = fields.String(dump_only=True)
    budget_type = fields.String()
    amount = fields.Decimal(places=2, as_string=True)
    period = fields.String()
    warning_threshold = fields.Integer(dump_only=True)
    last_period_surplus = fields.Decimal(places=2, as_string=True, dump_only=True)
    is_active = fields.Boolean()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Computed spending fields
    spent = fields.Decimal(places=2, as_string=True, dump_only=True)
    remaining = fields.Decimal(places=2, as_string=True, dump_only=True)
    percentage_used = fields.Float(dump_only=True)
    is_warning = fields.Boolean(dump_only=True)
    is_exceeded = fields.Boolean(dump_only=True)


class BudgetResponseSchema(BaseSchema):
    """
    Standard API response wrapper for single budget.

    Example:
        {
            "success": true,
            "data": { ... budget ... },
            "message": "Budget created successfully"
        }
    """

    success = fields.Boolean(dump_only=True)
    data = fields.Nested(BudgetSchema, dump_only=True)
    message = fields.String(dump_only=True)


class BudgetListResponseSchema(BaseSchema):
    """
    Standard API response wrapper for budget list.

    Example:
        {
            "success": true,
            "data": [ ... budgets ... ],
            "message": "Budgets retrieved successfully",
            "meta": {
                "total": 5,
                "active": 4
            }
        }
    """

    success = fields.Boolean(dump_only=True)
    data = fields.List(fields.Nested(BudgetSchema), dump_only=True)
    message = fields.String(dump_only=True)
    meta = fields.Dict(dump_only=True)


# =============================================================================
# SCHEMA INSTANCES
# =============================================================================

# Single instances for reuse
budget_schema = BudgetSchema()
budget_create_schema = BudgetCreateSchema()
budget_update_schema = BudgetUpdateSchema()
budget_with_spending_schema = BudgetWithSpendingSchema()
budget_list_schema = BudgetSchema(many=True)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Schemas
    "BudgetSchema",
    "BudgetCreateSchema",
    "BudgetUpdateSchema",
    "BudgetWithSpendingSchema",
    "BudgetResponseSchema",
    "BudgetListResponseSchema",
    # Instances
    "budget_schema",
    "budget_create_schema",
    "budget_update_schema",
    "budget_with_spending_schema",
    "budget_list_schema",
]
