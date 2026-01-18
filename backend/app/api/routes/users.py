# =============================================================================
# Digital Finance Tracker - User Routes
# PURPOSE: User API routes for authenticated user operations
# =============================================================================
"""
User Routes Module

This module provides API endpoints for user operations:
- GET /api/users/me - Get current user profile
- PATCH /api/users/me - Update current user profile
- GET /api/users/me/settings - Get user settings
- PATCH /api/users/me/settings - Update user settings

All endpoints require authentication via @requires_auth decorator.

Usage:
    # Register blueprint in app factory
    from app.api.routes.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix="/api/users")

Response Format:
    {
        "success": true,
        "data": {...},
        "message": "Optional message"
    }
"""

import logging
from flask import Blueprint, request, g

from app.auth.decorators import requires_auth
from app.auth.user_sync import sync_user_from_claims
from app.services.user_service import UserService
from app.schemas.user_schema import user_schema
from app.utils.errors import ValidationError
from app.utils.helpers import success_response


# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# BLUEPRINT SETUP
# =============================================================================

bp = Blueprint("users", __name__)


# =============================================================================
# USER PROFILE ENDPOINTS
# =============================================================================


@bp.route("/me", methods=["GET"])
@requires_auth
def get_current_user():
    """
    Get current authenticated user's profile.

    Returns:
        200: User profile data
        401: Unauthorized (no/invalid token)
        404: User not found in local database

    Example Request:
        GET /api/users/me
        Authorization: Bearer <access_token>

    Example Response:
        {
            "success": true,
            "data": {
                "id": "uuid-string",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                ...
            },
            "message": "User retrieved successfully"
        }
    """
    # Sync user from Auth0 claims (creates if first login)
    user = sync_user_from_claims(g.current_user)

    # Serialize user data
    data = user_schema.dump(user)

    return success_response(data=data, message="User retrieved successfully")


@bp.route("/me", methods=["PATCH"])
@requires_auth
def update_current_user():
    """
    Update current authenticated user's profile.

    Allowed Fields:
        - first_name: User's first name
        - last_name: User's last name
        - nickname: User's optional nickname/display name
        - salary_amount: User's salary for budgeting
        - settings: User preferences (partial update)

    Returns:
        200: Updated user profile
        400: Invalid request body
        401: Unauthorized
        422: Validation error

    Example Request:
        PATCH /api/users/me
        Authorization: Bearer <access_token>
        Content-Type: application/json

        {
            "first_name": "John",
            "last_name": "Doe",
            "nickname": "JohnD",
            "salary_amount": "5000.00"
        }

    Example Response:
        {
            "success": true,
            "data": {...updated user...},
            "message": "Profile updated successfully"
        }
    """
    # Get request data
    data = request.get_json()

    if not data:
        raise ValidationError("Request body required")

    # Get/sync current user
    user = sync_user_from_claims(g.current_user)

    # Update profile via service
    updated_user = UserService.update_profile(user, data)

    # Serialize response
    response_data = user_schema.dump(updated_user)

    return success_response(data=response_data, message="Profile updated successfully")


# =============================================================================
# USER SETTINGS ENDPOINTS
# =============================================================================


@bp.route("/me/settings", methods=["GET"])
@requires_auth
def get_user_settings():
    """
    Get current user's settings/preferences.

    Returns:
        200: User settings object
        401: Unauthorized

    Example Request:
        GET /api/users/me/settings
        Authorization: Bearer <access_token>

    Example Response:
        {
            "success": true,
            "data": {
                "currency": "USD",
                "timezone": "America/New_York",
                "notifications": {"email": true},
                "theme": "dark"
            },
            "message": "Settings retrieved successfully"
        }
    """
    # Get/sync current user
    user = sync_user_from_claims(g.current_user)

    return success_response(
        data=user.settings, message="Settings retrieved successfully"
    )


@bp.route("/me/settings", methods=["PATCH"])
@requires_auth
def update_user_settings():
    """
    Update current user's settings/preferences.

    Partial update - only provided fields are updated.

    Allowed Fields:
        - currency: 3-letter currency code
        - timezone: Timezone string
        - notifications: Notification preferences dict
        - theme: "light", "dark", or "system"

    Returns:
        200: Updated settings
        400: Invalid request body
        401: Unauthorized
        422: Validation error

    Example Request:
        PATCH /api/users/me/settings
        Authorization: Bearer <access_token>
        Content-Type: application/json

        {
            "currency": "EUR",
            "theme": "dark"
        }

    Example Response:
        {
            "success": true,
            "data": {...merged settings...},
            "message": "Settings updated successfully"
        }
    """
    # Get request data
    data = request.get_json()

    if not data:
        raise ValidationError("Request body required")

    # Get/sync current user
    user = sync_user_from_claims(g.current_user)

    # Update settings via service
    updated_user = UserService.update_settings(user, data)

    return success_response(
        data=updated_user.settings, message="Settings updated successfully"
    )


# =============================================================================
# ACCOUNT MANAGEMENT ENDPOINTS
# =============================================================================


@bp.route("/me/deactivate", methods=["POST"])
@requires_auth
def deactivate_account():
    """
    Deactivate current user's account.

    This is a soft delete - user data is preserved.
    User can contact support to reactivate.

    Returns:
        200: Account deactivated
        401: Unauthorized

    Example Request:
        POST /api/users/me/deactivate
        Authorization: Bearer <access_token>

    Example Response:
        {
            "success": true,
            "message": "Account deactivated successfully"
        }
    """
    # Get/sync current user
    user = sync_user_from_claims(g.current_user)

    # Deactivate via service
    UserService.deactivate_user(user)

    logger.info(f"User deactivated: {user.auth0_id}")

    return success_response(message="Account deactivated successfully")


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "bp",
]
