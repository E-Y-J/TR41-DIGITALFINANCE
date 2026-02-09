# =============================================================================
# Digital Finance Tracker - User Schemas
# PURPOSE: Marshmallow schemas for User validation and serialization
# =============================================================================
"""
User Schema Module

This module provides Marshmallow schemas for User data:
- Validation of incoming request data
- Serialization of User objects for API responses
- Nested schema support for related data

Usage:
    from app.schemas.user_schema import UserSchema, UserUpdateSchema

    # Serialize user for response
    schema = UserSchema()
    data = schema.dump(user)

    # Validate update request
    update_schema = UserUpdateSchema()
    validated = update_schema.load(request.json)

Schema Types:
    - UserSchema: Full user data (for responses)
    - UserPublicSchema: Limited public data
    - UserUpdateSchema: Allowed update fields
    - UserSettingsSchema: User preferences
"""

from typing import Optional
from marshmallow import fields, validate, validates

from app.schemas.base import BaseSchema, validate_not_blank

# =============================================================================
# USER SETTINGS SCHEMA
# =============================================================================


class UserSettingsSchema(BaseSchema):
    """
    Schema for user settings/preferences.

    Fields:
        currency: Preferred currency code (3 letters)
        timezone: User's timezone
        notifications: Notification preferences
        theme: UI theme preference

    Example:
        >>> settings = {
        ...     "currency": "USD",
        ...     "timezone": "America/New_York",
        ...     "notifications": {"email": True},
        ...     "theme": "dark"
        ... }
    """

    currency = fields.String(
        validate=validate.Length(equal=3),
        load_default="USD",
        metadata={"description": "Currency code (e.g., USD, EUR)"},
    )

    timezone = fields.String(
        load_default="UTC", metadata={"description": "User timezone"}
    )

    notifications = fields.Dict(
        keys=fields.String(),
        values=fields.Boolean(),
        load_default=dict,
        metadata={"description": "Notification preferences"},
    )

    theme = fields.String(
        validate=validate.OneOf(["light", "dark", "system"]),
        load_default="system",
        metadata={"description": "UI theme preference"},
    )


# =============================================================================
# USER SCHEMA (FULL)
# =============================================================================


class UserSchema(BaseSchema):
    """
    Full user schema for API responses.

    Includes all user fields except sensitive data.
    Used for responses to authenticated requests.

    Example Response:
        {
            "id": "uuid-string",
            "email": "user@example.com",
            "email_verified": "false"
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "account_status": "active",
            "role": "user",
            "salary_amount": "5000.00",
            "created_at": "2024-01-01T00:00:00Z",
            "settings": {...}
        }
    """

    # Identity fields
    id = fields.UUID(dump_only=True, metadata={"description": "User ID"})

    auth0_id = fields.String(
        dump_only=True, metadata={"description": "Auth0 user identifier"}
    )

    # Profile fields (per ERD: first_name, last_name)
    email = fields.Email(dump_only=True, metadata={"description": "User email address"})

    email_verified = fields.Boolean(
        dump_only=True, metadata={"description": "User's email verified status"}
    )

    first_name = fields.String(
        dump_only=True, metadata={"description": "User's first name"}
    )

    last_name = fields.String(
        dump_only=True, metadata={"description": "User's last name"}
    )

    nickname = fields.String(
        dump_only=True,
        allow_none=True,
        metadata={"description": "User's optional nickname/display name"},
    )

    full_name = fields.String(
        dump_only=True, metadata={"description": "User's full name (computed)"}
    )

    # Status & Role fields (per ERD)
    account_status = fields.Method(
        "get_account_status",
        dump_only=True,
        metadata={"description": "Account status: pending, active, or suspended"},
    )

    def get_account_status(self, obj):
        """Extract enum value as string."""
        if hasattr(obj.account_status, "value"):
            return obj.account_status.value
        return str(obj.account_status) if obj.account_status else None

    role = fields.Method(
        "get_role",
        dump_only=True,
        metadata={"description": "User role: user or admin"},
    )

    def get_role(self, obj):
        """Extract enum value as string."""
        if hasattr(obj.role, "value"):
            return obj.role.value
        return str(obj.role) if obj.role else None

    # Financial fields (per ERD)
    salary_amount = fields.Decimal(
        dump_only=True,
        as_string=True,
        metadata={"description": "User's salary amount"},
    )

    # Timestamps
    created_at = fields.DateTime(
        dump_only=True, format="iso", metadata={"description": "Account creation date"}
    )

    updated_at = fields.DateTime(
        dump_only=True, format="iso", metadata={"description": "Last update date"}
    )

    last_login = fields.DateTime(
        dump_only=True,
        format="iso",
        allow_none=True,
        metadata={"description": "Last login timestamp"},
    )

    # Nested settings
    settings = fields.Nested(
        UserSettingsSchema, dump_only=True, metadata={"description": "User preferences"}
    )


# =============================================================================
# USER PUBLIC SCHEMA
# =============================================================================


class UserPublicSchema(BaseSchema):
    """
    Limited user schema for public/shared contexts.

    Only includes non-sensitive fields that can be shown to others.

    Example:
        Used when displaying transaction history to another user.
    """

    id = fields.UUID(dump_only=True, metadata={"description": "User ID"})

    first_name = fields.String(
        dump_only=True, metadata={"description": "User's first name"}
    )

    last_name = fields.String(
        dump_only=True, metadata={"description": "User's last name"}
    )


# =============================================================================
# USER UPDATE SCHEMA
# =============================================================================


class UserUpdateSchema(BaseSchema):
    """
    Schema for validating user update requests.

    Only allows updating specific fields.
    Auth0-managed fields (email, etc.) are not updatable here.

    Auto-Activation:
        When a user with 'pending' status provides first_name and last_name,
        their account_status will be automatically set to 'active'.

    Example Request:
        {
            "first_name": "John",
            "last_name": "Smith",
            "salary_amount": "5000.00",
            "settings": {
                "currency": "EUR"
            }
        }
    """

    first_name = fields.String(
        validate=[
            validate.Length(min=1, max=255),
        ],
        load_default=None,
        metadata={"description": "User's first name"},
    )

    last_name = fields.String(
        validate=[
            validate.Length(min=1, max=255),
        ],
        load_default=None,
        metadata={"description": "User's last name"},
    )

    nickname = fields.String(
        validate=[
            validate.Length(max=100),
        ],
        load_default=None,
        metadata={"description": "User's optional nickname/display name"},
    )

    salary_amount = fields.Decimal(
        places=2,
        as_string=True,
        validate=validate.Range(min=0),
        load_default=None,
        metadata={"description": "User's salary amount for budgeting"},
    )

    settings = fields.Nested(
        UserSettingsSchema,
        load_default=None,
        metadata={"description": "User preferences to update", "partial": True},
    )

    @validates("first_name")
    def validate_first_name(self, value: Optional[str]) -> None:
        """Validate first_name doesn't contain only whitespace."""
        if value is not None:
            validate_not_blank(value)

    @validates("last_name")
    def validate_last_name(self, value: Optional[str]) -> None:
        """Validate last_name doesn't contain only whitespace."""
        if value is not None:
            validate_not_blank(value)


# =============================================================================
# USER SETTINGS UPDATE SCHEMA
# =============================================================================


class UserSettingsUpdateSchema(BaseSchema):
    """
    Schema for updating individual settings.

    Allows partial updates to settings object.

    Example Request:
        {
            "currency": "EUR",
            "timezone": "Europe/London"
        }
    """

    currency = fields.String(
        validate=validate.Length(equal=3),
        load_default=None,
        metadata={"description": "Currency code"},
    )

    timezone = fields.String(
        load_default=None, metadata={"description": "User timezone"}
    )

    notifications = fields.Dict(
        keys=fields.String(),
        values=fields.Boolean(),
        load_default=None,
        metadata={"description": "Notification preferences"},
    )

    theme = fields.String(
        validate=validate.OneOf(["light", "dark", "system"]),
        load_default=None,
        metadata={"description": "UI theme preference"},
    )


# =============================================================================
# RESPONSE WRAPPER SCHEMAS
# =============================================================================


class UserResponseSchema(BaseSchema):
    """
    Standard API response wrapper for user data.

    Example:
        {
            "success": true,
            "data": { ...user data... },
            "message": "User retrieved successfully"
        }
    """

    success = fields.Boolean(
        dump_default=True, metadata={"description": "Request success status"}
    )

    data = fields.Nested(UserSchema, metadata={"description": "User data"})

    message = fields.String(
        dump_default="Success", metadata={"description": "Response message"}
    )


# =============================================================================
# SCHEMA INSTANCES (for convenience)
# =============================================================================

# Pre-instantiated schemas for common use
user_schema = UserSchema()
user_public_schema = UserPublicSchema()
user_update_schema = UserUpdateSchema()
user_settings_schema = UserSettingsSchema()
user_settings_update_schema = UserSettingsUpdateSchema()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Schema classes
    "BaseSchema",
    "UserSchema",
    "UserPublicSchema",
    "UserUpdateSchema",
    "UserSettingsSchema",
    "UserSettingsUpdateSchema",
    "UserResponseSchema",
    # Pre-instantiated schemas
    "user_schema",
    "user_public_schema",
    "user_update_schema",
    "user_settings_schema",
    "user_settings_update_schema",
]
