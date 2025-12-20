# =============================================================================
# Digital Finance Tracker - Marshmallow Validation Schemas
# PURPOSE: Export all validation schemas for easy imports
# =============================================================================
"""
Schemas Package

This package contains all Marshmallow validation schemas.

Usage:
    from app.schemas import UserSchema, UserUpdateSchema
    from app.schemas import TransactionSchema, TransactionCreateSchema
    from app.schemas import BaseSchema  # For custom schemas
"""

# Import base schema from centralized location
from app.schemas.base import BaseSchema, validate_not_blank, validate_no_spaces

# Import user schemas
from app.schemas.user_schema import (
    UserSchema,
    UserPublicSchema,
    UserUpdateSchema,
    UserSettingsSchema,
    UserSettingsUpdateSchema,
    UserResponseSchema,
    user_schema,
    user_public_schema,
    user_update_schema,
    user_settings_schema,
    user_settings_update_schema,
)

# Import transaction schemas
from app.schemas.transaction_schema import (
    TransactionSchema,
    TransactionCreateSchema,
    TransactionUpdateSchema,
    TransactionResponseSchema,
    TransactionListResponseSchema,
    transaction_schema,
    transaction_create_schema,
    transaction_update_schema,
)

__all__ = [
    # Base schema and validators (from base.py)
    "BaseSchema",
    "validate_not_blank",
    "validate_no_spaces",
    # User schemas
    "UserSchema",
    "UserPublicSchema",
    "UserUpdateSchema",
    "UserSettingsSchema",
    "UserSettingsUpdateSchema",
    "UserResponseSchema",
    "user_schema",
    "user_public_schema",
    "user_update_schema",
    "user_settings_schema",
    "user_settings_update_schema",
    # Transaction schemas
    "TransactionSchema",
    "TransactionCreateSchema",
    "TransactionUpdateSchema",
    "TransactionResponseSchema",
    "TransactionListResponseSchema",
    "transaction_schema",
    "transaction_create_schema",
    "transaction_update_schema",
]
