# =============================================================================
# Digital Finance Tracker - Transaction Schemas
# PURPOSE: Marshmallow schemas for Transaction validation and serialization
# =============================================================================
"""
Transaction Schema Module

This module provides Marshmallow schemas for Transaction data:
- Validation of incoming request data
- Serialization of Transaction objects for API responses
- Create and update schemas with proper validation

Usage:
    from app.schemas.transaction_schema import (
        TransactionSchema,
        TransactionCreateSchema,
        TransactionUpdateSchema
    )

    # Serialize transaction for response
    schema = TransactionSchema()
    data = schema.dump(transaction)

    # Validate create request
    create_schema = TransactionCreateSchema()
    validated = create_schema.load(request.json)

Schema Types:
    - TransactionSchema: Full transaction data (for responses)
    - TransactionCreateSchema: Fields for creating new transaction
    - TransactionUpdateSchema: Allowed update fields
"""

from decimal import Decimal
from typing import Optional
from marshmallow import fields, validate, validates, ValidationError

from app.schemas.base import BaseSchema


# =============================================================================
# TRANSACTION SCHEMA (FULL)
# =============================================================================


class TransactionSchema(BaseSchema):
    """
    Full transaction schema for API responses.

    Includes all transaction fields.
    Used for responses to authenticated requests.

    AI Categorization Fields:
        Added category_id, ai_confidence, ai_source, is_user_override
        to support intelligent transaction categorization.

    Example Response:
        {
            "id": "uuid-string",
            "user_id": "uuid-string",
            "amount": "125.50",
            "transaction_type": "expense",
            "date": "2024-01-15",
            "merchant_name": "Amazon",
            "category": "Shopping",
            "category_id": "category-uuid",
            "category_obj": {"id": "...", "name": "Shopping & Retail"},
            "ai_confidence": 0.95,
            "ai_source": "huggingface",
            "is_user_override": false,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    """

    # Identity fields
    id = fields.UUID(dump_only=True, metadata={"description": "Transaction ID"})

    user_id = fields.UUID(dump_only=True, metadata={"description": "User ID"})

    # Transaction fields
    amount = fields.Decimal(
        dump_only=True,
        as_string=True,
        metadata={"description": "Transaction amount"},
    )

    transaction_type = fields.Method(
        "get_transaction_type",
        dump_only=True,
        metadata={"description": "Transaction type: income or expense"},
    )

    def get_transaction_type(self, obj):
        """Extract enum value as string."""
        if hasattr(obj.transaction_type, "value"):
            return obj.transaction_type.value
        return str(obj.transaction_type) if obj.transaction_type else None

    date = fields.String(
        dump_only=True,
        metadata={"description": "Transaction date"},
    )

    merchant_name = fields.String(
        dump_only=True,
        allow_none=True,
        metadata={"description": "Merchant or payee name"},
    )

    # Legacy category field (deprecated, kept for backward compatibility)
    category = fields.String(
        dump_only=True,
        allow_none=True,
        metadata={"description": "[DEPRECATED] Transaction category string"},
    )

    # =========================================================================
    # AI CATEGORIZATION FIELDS
    # =========================================================================

    category_id = fields.UUID(
        dump_only=True,
        allow_none=True,
        metadata={"description": "Category ID (foreign key to categories table)"},
    )

    category_name = fields.Method(
        "get_category_name",
        dump_only=True,
        metadata={"description": "Category name (e.g., 'Food & Dining')"},
    )

    def get_category_name(self, obj):
        """Get the category name from the relationship."""
        if hasattr(obj, "category_rel") and obj.category_rel:
            return obj.category_rel.name
        return None

    category_obj = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        dump_only=True,
        allow_none=True,
        metadata={"description": "Category object with id and name"},
    )

    ai_confidence = fields.Float(
        dump_only=True,
        allow_none=True,
        metadata={"description": "AI confidence score (0.0 to 1.0)"},
    )

    ai_source = fields.Method(
        "get_ai_source",
        dump_only=True,
        metadata={"description": "Source: huggingface, gemini, or user"},
    )

    def get_ai_source(self, obj):
        """Extract enum value as string."""
        if obj.ai_source is None:
            return None
        if hasattr(obj.ai_source, "value"):
            return obj.ai_source.value
        return str(obj.ai_source)

    is_user_override = fields.Boolean(
        dump_only=True,
        metadata={"description": "True if user overrode AI's category"},
    )

    original_category_id = fields.UUID(
        dump_only=True,
        allow_none=True,
        metadata={"description": "AI's original category suggestion (before override)"},
    )

    # Timestamps
    created_at = fields.DateTime(
        dump_only=True,
        format="iso",
        metadata={"description": "Record creation date"},
    )

    updated_at = fields.DateTime(
        dump_only=True,
        format="iso",
        metadata={"description": "Record update date"},
    )


# =============================================================================
# TRANSACTION CREATE SCHEMA
# =============================================================================


class TransactionCreateSchema(BaseSchema):
    """
    Schema for validating transaction create requests.

    Category Assignment:
        Added category_id field for explicit category assignment.
        When category_id is not provided, AI will auto-categorize.

    Example Request:
        {
            "amount": "125.50",
            "transaction_type": "expense",
            "date": "2024-01-15",
            "merchant_name": "Amazon",
            "category": "Shopping",
            "category_id": "uuid-string"  // Optional
        }
    """

    amount = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=Decimal("0.01")),
        metadata={"description": "Transaction amount (must be positive)"},
    )

    transaction_type = fields.String(
        required=True,
        validate=validate.OneOf(["income", "expense"]),
        metadata={"description": "Transaction type: income or expense"},
    )

    date = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50),
        metadata={"description": "Transaction date"},
    )

    merchant_name = fields.String(
        load_default=None,
        validate=validate.Length(max=255),
        metadata={"description": "Merchant or payee name"},
    )

    # Legacy category field (kept for backward compatibility)
    category = fields.String(
        load_default=None,
        validate=validate.Length(max=100),
        metadata={"description": "[DEPRECATED] Transaction category string"},
    )

    # Category ID for explicit category assignment
    category_id = fields.UUID(
        load_default=None,
        metadata={
            "description": "Category ID (optional, AI will assign if not provided)"
        },
    )

    @validates("amount")
    def validate_amount(self, value: Decimal) -> None:
        """Validate amount is positive and has reasonable precision."""
        if value <= 0:
            raise ValidationError("Amount must be greater than zero")
        # Check for reasonable precision (max 2 decimal places)
        if value.as_tuple().exponent < -2:
            raise ValidationError("Amount can have at most 2 decimal places")

    @validates("date")
    def validate_date(self, value: str) -> None:
        """Validate date is not empty."""
        if not value or not value.strip():
            raise ValidationError("Date cannot be empty")


# =============================================================================
# TRANSACTION UPDATE SCHEMA
# =============================================================================


class TransactionUpdateSchema(BaseSchema):
    """
    Schema for validating transaction update requests.

    All fields are optional - only provided fields will be updated.

    Example Request:
        {
            "amount": "150.00",
            "category": "Electronics"
        }
    """

    amount = fields.Decimal(
        load_default=None,
        as_string=True,
        validate=validate.Range(min=Decimal("0.01")),
        metadata={"description": "Transaction amount (must be positive)"},
    )

    transaction_type = fields.String(
        load_default=None,
        validate=validate.OneOf(["income", "expense"]),
        metadata={"description": "Transaction type: income or expense"},
    )

    date = fields.String(
        load_default=None,
        validate=validate.Length(min=1, max=50),
        metadata={"description": "Transaction date"},
    )

    merchant_name = fields.String(
        load_default=None,
        validate=validate.Length(max=255),
        metadata={"description": "Merchant or payee name"},
    )

    category = fields.String(
        load_default=None,
        validate=validate.Length(max=100),
        metadata={"description": "Transaction category"},
    )

    @validates("amount")
    def validate_amount(self, value: Optional[Decimal]) -> None:
        """Validate amount is positive and has reasonable precision."""
        if value is not None:
            if value <= 0:
                raise ValidationError("Amount must be greater than zero")
            if value.as_tuple().exponent < -2:
                raise ValidationError("Amount can have at most 2 decimal places")

    @validates("date")
    def validate_date(self, value: Optional[str]) -> None:
        """Validate date is not empty if provided."""
        if value is not None and not value.strip():
            raise ValidationError("Date cannot be empty")


# =============================================================================
# RESPONSE WRAPPER SCHEMAS
# =============================================================================


class TransactionResponseSchema(BaseSchema):
    """
    Standard API response wrapper for transaction data.

    Example:
        {
            "success": true,
            "data": { ...transaction data... },
            "message": "Transaction created successfully"
        }
    """

    success = fields.Boolean(
        dump_default=True,
        metadata={"description": "Request success status"},
    )

    data = fields.Nested(
        TransactionSchema,
        metadata={"description": "Transaction data"},
    )

    message = fields.String(
        dump_default="Success",
        metadata={"description": "Response message"},
    )


class TransactionListResponseSchema(BaseSchema):
    """
    Standard API response wrapper for transaction list.

    Example:
        {
            "success": true,
            "data": [ ...transactions... ],
            "meta": { "page": 1, "per_page": 20, "total": 100 },
            "message": "Transactions retrieved successfully"
        }
    """

    success = fields.Boolean(
        dump_default=True,
        metadata={"description": "Request success status"},
    )

    data = fields.List(
        fields.Nested(TransactionSchema),
        metadata={"description": "List of transactions"},
    )

    meta = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        metadata={"description": "Pagination metadata"},
    )

    message = fields.String(
        dump_default="Success",
        metadata={"description": "Response message"},
    )


# =============================================================================
# SCHEMA INSTANCES (for convenience)
# =============================================================================

# Pre-instantiated schemas for common use
transaction_schema = TransactionSchema()
transaction_create_schema = TransactionCreateSchema()
transaction_update_schema = TransactionUpdateSchema()
transaction_list_schema = TransactionSchema(many=True)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Schema classes
    "BaseSchema",
    "TransactionSchema",
    "TransactionCreateSchema",
    "TransactionUpdateSchema",
    "TransactionResponseSchema",
    "TransactionListResponseSchema",
    # Pre-instantiated schemas
    "transaction_schema",
    "transaction_create_schema",
    "transaction_update_schema",
    "transaction_list_schema",
]
