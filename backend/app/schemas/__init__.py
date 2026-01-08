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
    from app.schemas import CategorySchema, category_schema
    from app.schemas import NotificationSchema, notification_schema
    from app.schemas import BaseSchema  # For custom schemas

AI Foundation Additions:
    - CategorySchema for category serialization
    - NotificationSchema for notification serialization
    - AlertSchema for alert serialization
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
    transaction_list_schema,
)

# Import category schemas (AI Foundation)
from app.schemas.category_schema import (
    CategorySchema,
    CategoryResponseSchema,
    CategoryListResponseSchema,
    category_schema,
    category_list_schema,
)

# Import notification schemas (AI Foundation)
from app.schemas.notification_schema import (
    NotificationSchema,
    NotificationStatusUpdateSchema,
    NotificationResponseSchema,
    NotificationListResponseSchema,
    notification_schema,
    notification_list_schema,
    notification_status_update_schema,
)

# Import alert schemas (Foundation for anomaly detection)
from app.schemas.alert_schema import (
    AlertSchema,
    AlertDismissSchema,
    AlertCreateSchema,
    AlertResponseSchema,
    AlertListResponseSchema,
    alert_schema,
    alert_list_schema,
    alert_dismiss_schema,
    alert_create_schema,
)

__all__ = [
    # =========================================================================
    # Base schema and validators (from base.py)
    # =========================================================================
    "BaseSchema",
    "validate_not_blank",
    "validate_no_spaces",
    # =========================================================================
    # User schemas
    # =========================================================================
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
    # =========================================================================
    # Transaction schemas
    # =========================================================================
    "TransactionSchema",
    "TransactionCreateSchema",
    "TransactionUpdateSchema",
    "TransactionResponseSchema",
    "TransactionListResponseSchema",
    "transaction_schema",
    "transaction_create_schema",
    "transaction_update_schema",
    "transaction_list_schema",
    # =========================================================================
    # Category schemas (AI Foundation)
    # =========================================================================
    "CategorySchema",
    "CategoryResponseSchema",
    "CategoryListResponseSchema",
    "category_schema",
    "category_list_schema",
    # =========================================================================
    # Notification schemas (AI Foundation)
    # =========================================================================
    "NotificationSchema",
    "NotificationStatusUpdateSchema",
    "NotificationResponseSchema",
    "NotificationListResponseSchema",
    "notification_schema",
    "notification_list_schema",
    "notification_status_update_schema",
    # =========================================================================
    # Alert schemas (Foundation for anomaly detection)
    # =========================================================================
    "AlertSchema",
    "AlertDismissSchema",
    "AlertCreateSchema",
    "AlertResponseSchema",
    "AlertListResponseSchema",
    "alert_schema",
    "alert_list_schema",
    "alert_dismiss_schema",
    "alert_create_schema",
]
