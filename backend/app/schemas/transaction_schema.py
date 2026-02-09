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

    PR #48 Fix: Null Handling (IMPORTANT FOR FRONTEND TEAM)
    =========================================================
    Problem: API was returning null values that broke frontend rendering.

    Solution: Use Method fields with fallback values. NO MORE NULLS in:
        - merchant_name: "Unnamed Transaction" (if null in DB)
        - category_id: Unknown category UUID (if null in DB)
        - category_name: "Unknown" (if null in DB)
        - category_obj: {"id": "...", "name": "Unknown"} (if null in DB)
        - ai_source: "pending" (uncategorized), "user" (override)
        - ai_confidence: 0.0 (uncategorized), 1.0 (user override)

    Fields that CAN be null (intentional):
        - original_category_id: null means user didn't override AI

    REMOVED from response (deprecated):
        - category: Legacy string column - use category_name instead

    Example Response:
        {
            "id": "uuid-string",
            "user_id": "uuid-string",
            "amount": "125.50",
            "transaction_type": "expense",
            "date": "2024-01-15",
            "merchant_name": "Amazon",
            "category_name": "Shopping & Retail",
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

    merchant_name = fields.Method(
        "get_merchant_name",
        dump_only=True,
        metadata={"description": "Merchant or payee name (never null)"},
    )

    def get_merchant_name(self, obj):
        """
        Get merchant name with fallback.

        PR #48 Fix: Returns 'Unnamed Transaction' instead of null.
        This ensures the frontend always has a displayable merchant name.
        """
        return obj.merchant_name or "Unnamed Transaction"

    # NOTE: Legacy `category` field removed - use `category_name` instead
    # The deprecated string column still exists in DB for historical data

    # =========================================================================
    # PR #48 FIX: AI CATEGORIZATION FIELDS (No Nulls in API Response)
    # =========================================================================
    #
    # WHY: Frontend was breaking when API returned null values.
    #
    # HOW: All fields below use Method fields with fallback values:
    #   - category_id     → Unknown category UUID (if uncategorized)
    #   - category_name   → "Unknown" (if uncategorized)
    #   - category_obj    → {"id": "...", "name": "Unknown"} (if uncategorized)
    #   - ai_source       → "pending" (uncategorized) or "user" (override)
    #   - ai_confidence   → 0.0 (uncategorized) or 1.0 (user override)
    #
    # INTENTIONALLY NULLABLE (needed by AI system):
    #   - original_category_id: null = user didn't override AI's prediction
    # =========================================================================

    category_id = fields.Method(
        "get_category_id",
        dump_only=True,
        metadata={"description": "Category ID (uses Unknown category as fallback)"},
    )

    def get_category_id(self, obj):
        """
        Get category ID with fallback to Unknown category.

        PR #48 Fix: Returns Unknown category ID instead of null.
        This ensures the frontend always has a valid category reference.
        """
        if obj.category_id:
            return str(obj.category_id)
        # Fallback to Unknown category
        from app.models.category import Category

        unknown_cat = Category.get_unknown_category()
        return str(unknown_cat.id) if unknown_cat else None

    category_name = fields.Method(
        "get_category_name",
        dump_only=True,
        metadata={"description": "Category name (e.g., 'Food & Dining')"},
    )

    def get_category_name(self, obj):
        """
        Get the category name from the relationship.

        PR #48 Fix: Falls back to "Unknown" category from database.
        This ensures the frontend always has a valid category name.
        """
        if hasattr(obj, "category_rel") and obj.category_rel:
            return obj.category_rel.name
        # Fallback to the "Unknown" category from database
        from app.models.category import Category

        unknown_cat = Category.get_unknown_category()
        return unknown_cat.name if unknown_cat else "Unknown"

    category_obj = fields.Method(
        "get_category_obj",
        dump_only=True,
        metadata={"description": "Category object with id and name (never null)"},
    )

    def get_category_obj(self, obj):
        """
        Get category object with fallback to Unknown category.

        PR #48 Fix: Returns Unknown category object instead of null.
        This ensures the frontend always has a valid category object.
        """
        if hasattr(obj, "category_rel") and obj.category_rel:
            return {
                "id": str(obj.category_rel.id),
                "name": obj.category_rel.name,
            }
        # Fallback to Unknown category
        from app.models.category import Category

        unknown_cat = Category.get_unknown_category()
        if unknown_cat:
            return {
                "id": str(unknown_cat.id),
                "name": unknown_cat.name,
            }
        return None

    ai_confidence = fields.Method(
        "get_ai_confidence",
        dump_only=True,
        metadata={"description": "AI confidence score (0.0 to 1.0, never null)"},
    )

    def get_ai_confidence(self, obj):
        """
        Get AI confidence with sensible defaults.

        PR #48 Fix: Never returns null.
        - User overrides: 1.0 (user is 100% confident in their choice)
        - AI categorized: actual confidence from model
        - Uncategorized: 0.0 (no confidence yet)
        """
        if getattr(obj, "is_user_override", False):
            return 1.0
        if obj.ai_confidence is not None:
            return obj.ai_confidence
        return 0.0  # Never return null

    ai_source = fields.Method(
        "get_ai_source",
        dump_only=True,
        metadata={"description": "Source: huggingface, gemini, user, or pending"},
    )

    def get_ai_source(self, obj):
        """
        Extract enum value as string, with sensible defaults.

        PR #48 Fix: Never returns null.
        - User overrides: "user" (human selected the category)
        - AI categorized: "huggingface" or "gemini" (model source)
        - Uncategorized: "pending" (awaiting AI categorization)
        """
        if getattr(obj, "is_user_override", False):
            return "user"
        if obj.ai_source is not None:
            if hasattr(obj.ai_source, "value"):
                return obj.ai_source.value
            return str(obj.ai_source)
        return "pending"  # Awaiting AI categorization

    is_user_override = fields.Boolean(
        dump_only=True,
        metadata={"description": "True if user overrode AI's category"},
    )

    original_category_id = fields.UUID(
        dump_only=True,
        allow_none=True,
        # INTENTIONALLY NULLABLE: null means no AI prediction was overridden
        metadata={
            "description": "AI's original category (null = no override occurred)"
        },
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
