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

from typing import Dict, Any, Optional
from marshmallow import Schema, fields, validate, post_load, validates, ValidationError, EXCLUDE


# =============================================================================
# BASE SCHEMA
# =============================================================================

class BaseSchema(Schema):
    """
    Base schema with common configuration.
    
    All schemas should inherit from this class.
    """
    
    class Meta:
        # Return ordered dict to maintain field order
        ordered = True
        # Don't raise on unknown fields during load (ignore them)
        unknown = EXCLUDE


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
        metadata={"description": "Currency code (e.g., USD, EUR)"}
    )
    
    timezone = fields.String(
        load_default="UTC",
        metadata={"description": "User timezone"}
    )
    
    notifications = fields.Dict(
        keys=fields.String(),
        values=fields.Boolean(),
        load_default=dict,
        metadata={"description": "Notification preferences"}
    )
    
    theme = fields.String(
        validate=validate.OneOf(["light", "dark", "system"]),
        load_default="system",
        metadata={"description": "UI theme preference"}
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
            "email_verified": true,
            "name": "John Doe",
            "nickname": "john",
            "picture": "https://...",
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z",
            "settings": {...}
        }
    """
    
    # Identity fields
    id = fields.UUID(
        dump_only=True,
        metadata={"description": "User ID"}
    )
    
    auth0_id = fields.String(
        dump_only=True,
        metadata={"description": "Auth0 user identifier"}
    )
    
    # Profile fields
    email = fields.Email(
        dump_only=True,
        metadata={"description": "User email address"}
    )
    
    email_verified = fields.Boolean(
        dump_only=True,
        metadata={"description": "Whether email is verified"}
    )
    
    name = fields.String(
        dump_only=True,
        metadata={"description": "Display name"}
    )
    
    nickname = fields.String(
        dump_only=True,
        metadata={"description": "Short nickname"}
    )
    
    picture = fields.Url(
        dump_only=True,
        allow_none=True,
        metadata={"description": "Profile picture URL"}
    )
    
    # Status fields
    is_active = fields.Boolean(
        dump_only=True,
        metadata={"description": "Account active status"}
    )
    
    # Timestamps
    created_at = fields.DateTime(
        dump_only=True,
        format="iso",
        metadata={"description": "Account creation date"}
    )
    
    updated_at = fields.DateTime(
        dump_only=True,
        format="iso",
        metadata={"description": "Last update date"}
    )
    
    last_login = fields.DateTime(
        dump_only=True,
        format="iso",
        allow_none=True,
        metadata={"description": "Last login timestamp"}
    )
    
    # Nested settings
    settings = fields.Nested(
        UserSettingsSchema,
        dump_only=True,
        metadata={"description": "User preferences"}
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
    
    id = fields.UUID(
        dump_only=True,
        metadata={"description": "User ID"}
    )
    
    name = fields.String(
        dump_only=True,
        metadata={"description": "Display name"}
    )
    
    nickname = fields.String(
        dump_only=True,
        metadata={"description": "Short nickname"}
    )
    
    picture = fields.Url(
        dump_only=True,
        allow_none=True,
        metadata={"description": "Profile picture URL"}
    )


# =============================================================================
# USER UPDATE SCHEMA
# =============================================================================

class UserUpdateSchema(BaseSchema):
    """
    Schema for validating user update requests.
    
    Only allows updating specific fields.
    Auth0-managed fields (email, etc.) are not updatable here.
    
    Example Request:
        {
            "name": "New Name",
            "nickname": "newnick",
            "settings": {
                "currency": "EUR"
            }
        }
    """
    
    name = fields.String(
        validate=[
            validate.Length(min=1, max=255),
        ],
        load_default=None,
        metadata={"description": "Display name"}
    )
    
    nickname = fields.String(
        validate=[
            validate.Length(min=1, max=100),
        ],
        load_default=None,
        metadata={"description": "Short nickname"}
    )
    
    settings = fields.Nested(
        UserSettingsSchema,
        partial=True,
        load_default=None,
        metadata={"description": "User preferences to update"}
    )
    
    @validates("name")
    def validate_name(self, value: Optional[str]) -> None:
        """Validate name doesn't contain only whitespace."""
        if value is not None and not value.strip():
            raise ValidationError("Name cannot be empty or whitespace only")
    
    @validates("nickname")
    def validate_nickname(self, value: Optional[str]) -> None:
        """Validate nickname format."""
        if value is not None:
            if not value.strip():
                raise ValidationError("Nickname cannot be empty or whitespace only")
            if " " in value:
                raise ValidationError("Nickname cannot contain spaces")


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
        metadata={"description": "Currency code"}
    )
    
    timezone = fields.String(
        load_default=None,
        metadata={"description": "User timezone"}
    )
    
    notifications = fields.Dict(
        keys=fields.String(),
        values=fields.Boolean(),
        load_default=None,
        metadata={"description": "Notification preferences"}
    )
    
    theme = fields.String(
        validate=validate.OneOf(["light", "dark", "system"]),
        load_default=None,
        metadata={"description": "UI theme preference"}
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
        dump_default=True,
        metadata={"description": "Request success status"}
    )
    
    data = fields.Nested(
        UserSchema,
        metadata={"description": "User data"}
    )
    
    message = fields.String(
        dump_default="Success",
        metadata={"description": "Response message"}
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
