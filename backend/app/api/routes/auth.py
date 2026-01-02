# =============================================================================
# Digital Finance Tracker - Auth Routes
# PURPOSE: Auth0 authentication endpoints for the backend
# =============================================================================
"""
Auth Routes Module

This module provides authentication-related API endpoints.

IMPORTANT: Auth0 Authentication Flow
------------------------------------
This application uses Auth0 for authentication. The login/register flow is:

1. Frontend redirects user to Auth0 Universal Login
2. User authenticates with Auth0 (email/password, social login, etc.)
3. Auth0 redirects back to frontend with authorization code
4. Frontend exchanges code for tokens (access_token, id_token)
5. Frontend stores tokens and sends access_token to backend API
6. Backend validates tokens using @requires_auth decorator

The backend does NOT:
- Handle login/register forms directly
- Store passwords (Auth0 handles this)
- Issue tokens (Auth0 issues JWTs)

The backend DOES:
- Validate Auth0 JWTs on protected routes
- Sync Auth0 user data to local database
- Provide user info endpoint

Endpoints:
- POST /api/auth/callback    - Sync user after Auth0 login (frontend calls this)
- GET  /api/auth/me          - Get current authenticated user info
- POST /api/auth/logout      - Client-side logout instructions
- GET  /api/auth/status      - Check authentication status

Usage:
    # Register blueprint in app factory
    from app.api.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
"""

import logging
from flask import Blueprint, g, jsonify, request

from app.auth.decorators import requires_auth, optional_auth
from app.auth.user_sync import sync_user_from_claims
from app.schemas.user_schema import user_schema
from app.core.config import get_config


# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# BLUEPRINT SETUP
# =============================================================================

bp = Blueprint("auth", __name__)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def success_response(data=None, message="Success", status_code=200):
    """Create a standardized success response."""
    response = {
        "success": True,
        "message": message,
    }
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code


def error_response(message="Error", code="ERROR", status_code=400, details=None):
    """Create a standardized error response."""
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
    if details:
        response["error"]["details"] = details
    return jsonify(response), status_code


# =============================================================================
# AUTH CALLBACK ENDPOINT
# =============================================================================


@bp.route("/callback", methods=["POST"])
@requires_auth
def auth_callback():
    """
    Sync user after successful Auth0 authentication.

    This endpoint should be called by the frontend after successful
    Auth0 login to ensure the user is synced to our local database.

    The @requires_auth decorator validates the access token and
    populates g.current_user with Auth0 claims.

    Returns:
        200: User synced successfully with user data
        401: Invalid or missing token

    Example Request:
        POST /api/auth/callback
        Authorization: Bearer <access_token>

    Example Response:
        {
            "success": true,
            "data": {
                "id": "uuid-string",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_new_user": false
            },
            "message": "User synced successfully"
        }

    Notes:
        - Frontend should call this after receiving tokens from Auth0
        - Creates local user record on first login
        - Updates user data if Auth0 profile changed
    """
    # Check if user exists before sync
    from app.models.user import User

    auth0_id = g.current_user.get("sub")
    existing_user = User.get_by_auth0_id(auth0_id) if auth0_id else None
    is_new_user = existing_user is None

    # Sync user from Auth0 claims to local database
    user = sync_user_from_claims(g.current_user)

    # Serialize user data
    user_data = user_schema.dump(user)
    user_data["is_new_user"] = is_new_user

    message = "Welcome! Account created." if is_new_user else "User synced successfully"

    logger.info(f"Auth callback for user: {user.auth0_id}, new: {is_new_user}")

    return success_response(data=user_data, message=message)


# =============================================================================
# GET CURRENT USER
# =============================================================================


@bp.route("/me", methods=["GET"])
@requires_auth
def get_me():
    """
    Get current authenticated user information.

    Similar to /api/users/me but focused on auth context.
    Includes Auth0-specific fields.

    Returns:
        200: Current user information
        401: Not authenticated

    Example Request:
        GET /api/auth/me
        Authorization: Bearer <access_token>

    Example Response:
        {
            "success": true,
            "data": {
                "id": "uuid-string",
                "auth0_id": "auth0|123...",
                "email": "user@example.com",
                "email_verified": true,
                "first_name": "John",
                "last_name": "Doe",
                "account_status": "active",
                "role": "user"
            },
            "message": "Authenticated"
        }
    """
    # Sync/get user
    user = sync_user_from_claims(g.current_user)

    # Build response with auth-relevant fields
    data = {
        "id": str(user.id),
        "auth0_id": user.auth0_id,
        "email": user.email,
        "email_verified": user.email_verified,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.full_name,
        "account_status": user.account_status.value,
        "role": user.role.value,
        "picture": user.picture,
    }

    return success_response(data=data, message="Authenticated")


# =============================================================================
# LOGOUT INSTRUCTIONS
# =============================================================================


@bp.route("/logout", methods=["POST"])
@optional_auth
def logout():
    """
    Logout endpoint - provides client-side logout instructions.

    Since Auth0 handles authentication, logout is primarily client-side:
    1. Clear tokens from client storage
    2. Optionally redirect to Auth0 logout endpoint

    This endpoint confirms logout action and provides Auth0 logout URL.

    Returns:
        200: Logout instructions

    Example Request:
        POST /api/auth/logout
        Authorization: Bearer <access_token>  (optional)

    Example Response:
        {
            "success": true,
            "data": {
                "auth0_logout_url": "https://your-tenant.auth0.com/v2/logout?...",
                "instructions": [
                    "Clear access_token from storage",
                    "Clear id_token from storage",
                    "Redirect to auth0_logout_url (optional)"
                ]
            },
            "message": "Logout instructions"
        }

    Notes:
        - Backend doesn't maintain session state (stateless JWT)
        - Client must clear tokens from local/session storage
        - Auth0 logout URL clears Auth0 session cookies
    """
    config = get_config()

    # Build Auth0 logout URL
    auth0_domain = config.auth0.domain
    client_id = config.auth0.client_id
    return_to = request.args.get("return_to", request.host_url)

    auth0_logout_url = (
        f"https://{auth0_domain}/v2/logout?"
        f"client_id={client_id}&returnTo={return_to}"
    )

    data = {
        "auth0_logout_url": auth0_logout_url,
        "instructions": [
            "Clear access_token from storage",
            "Clear id_token from storage",
            "Clear user data from state",
            "Redirect to auth0_logout_url to clear Auth0 session (optional)",
        ],
    }

    # Log if user was authenticated
    if g.get("current_user"):
        auth0_id = g.current_user.get("sub", "unknown")
        logger.info(f"Logout request from user: {auth0_id}")

    return success_response(data=data, message="Logout instructions")


# =============================================================================
# AUTH STATUS CHECK
# =============================================================================


@bp.route("/status", methods=["GET"])
@optional_auth
def auth_status():
    """
    Check authentication status.

    Returns whether the request has a valid auth token.
    Useful for frontend to check auth state on app load.

    Returns:
        200: Auth status (authenticated or not)

    Example Request (authenticated):
        GET /api/auth/status
        Authorization: Bearer <valid_token>

    Example Response (authenticated):
        {
            "success": true,
            "data": {
                "authenticated": true,
                "user_id": "uuid-string",
                "auth0_id": "auth0|123..."
            },
            "message": "Authenticated"
        }

    Example Response (not authenticated):
        {
            "success": true,
            "data": {
                "authenticated": false
            },
            "message": "Not authenticated"
        }
    """
    if g.get("current_user"):
        # User is authenticated
        user = sync_user_from_claims(g.current_user)

        data = {
            "authenticated": True,
            "user_id": str(user.id),
            "auth0_id": user.auth0_id,
            "email": user.email,
            "account_status": user.account_status.value,
        }

        return success_response(data=data, message="Authenticated")
    else:
        # Not authenticated
        return success_response(
            data={"authenticated": False}, message="Not authenticated"
        )


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "bp",
]
