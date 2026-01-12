# =============================================================================
# Digital Finance Tracker - Base Schema
# PURPOSE: Shared base schema and common validators for Marshmallow schemas
# =============================================================================
"""
Base Schema Module

This module provides the base schema configuration and common validators
used across all Marshmallow schemas in the application.

Centralizing base schema provides:
- Consistent configuration across all schemas
- Reusable validation functions
- Single place to modify schema behavior

Usage:
    from app.schemas.base import BaseSchema, validate_not_blank

    class MySchema(BaseSchema):
        name = fields.String(validate=validate_not_blank)
"""

from typing import Optional
from marshmallow import Schema, ValidationError, EXCLUDE


# =============================================================================
# COMMON VALIDATORS
# =============================================================================


def validate_not_blank(value: Optional[str]) -> None:
    """
    Validate that a string is not empty or whitespace only.

    Args:
        value: String value to validate

    Raises:
        ValidationError: If value is empty or whitespace only

    Example:
        >>> validate_not_blank("  ")  # Raises ValidationError
        >>> validate_not_blank("hello")  # Passes
    """
    if value is not None and not value.strip():
        raise ValidationError("Field cannot be empty or whitespace only")


def validate_no_spaces(value: Optional[str]) -> None:
    """
    Validate that a string contains no spaces.

    Args:
        value: String value to validate

    Raises:
        ValidationError: If value contains spaces

    Example:
        >>> validate_no_spaces("hello world")  # Raises ValidationError
        >>> validate_no_spaces("hello_world")  # Passes
    """
    if value is not None and " " in value:
        raise ValidationError("Field cannot contain spaces")


# =============================================================================
# BASE SCHEMA
# =============================================================================


class BaseSchema(Schema):
    """
    Base schema with common configuration.

    All application schemas should inherit from this class to ensure
    consistent behavior across the application.

    Configuration:
        - ordered: Returns ordered dict to maintain field order in responses
        - unknown: EXCLUDE - ignores unknown fields during deserialization

    Example:
        >>> class UserSchema(BaseSchema):
        ...     name = fields.String()
        ...     email = fields.Email()
    """

    class Meta:
        # Don't raise on unknown fields during load (ignore them)
        unknown = EXCLUDE


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "BaseSchema",
    "validate_not_blank",
    "validate_no_spaces",
]
