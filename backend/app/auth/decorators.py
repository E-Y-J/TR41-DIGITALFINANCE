# =============================================================================
# Digital Finance Tracker - Auth Decorators
# PURPOSE: Authentication decorators for protecting Flask routes
# =============================================================================
"""
Authentication Decorators Module

This module provides decorators for protecting Flask routes:
- @requires_auth: Validates JWT token and injects user info into g
- @optional_auth: Same as above but doesn't fail if no token

Usage:
    from app.auth.decorators import requires_auth, optional_auth

    @bp.route('/protected')
    @requires_auth
    def protected_route():
        # g.current_user contains Auth0 claims
        user_id = g.current_user.get("sub")
        return {"user_id": user_id}

    @bp.route('/public')
    @optional_auth
    def public_route():
        # g.current_user is None if not authenticated
        if g.current_user:
            return {"message": "Hello, authenticated user!"}
        return {"message": "Hello, guest!"}

Flask g Context:
    After @requires_auth, the following are available:
    - g.current_user: Dict with all token claims
    - g.auth0_id: User's Auth0 ID (sub claim)
    - g.access_token: The raw access token string
"""

import logging
from functools import wraps
from typing import Callable, Optional, TypeVar, Any
import os
from flask import request, g

from app.auth.auth0 import (
    get_token_from_header,
    validate_token,
    get_user_id_from_claims,
)
from app.utils.errors import UnauthorizedError

# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# TYPE HINTS
# =============================================================================

F = TypeVar("F", bound=Callable[..., Any])


# =============================================================================
# CORE DECORATOR
# =============================================================================


def requires_auth(f: F) -> F:
    """
    Decorator that requires a valid Auth0 JWT token.

    This decorator:
    1. Extracts Bearer token from Authorization header
    2. Validates the token against Auth0
    3. Stores claims in Flask's g context
    4. Proceeds to the route handler

    After decoration, the following are available in the route:
    - g.current_user: Dict containing all token claims
    - g.auth0_id: User's Auth0 ID (sub claim)
    - g.access_token: The raw access token

    Args:
        f: The route function to wrap

    Returns:
        Wrapped function that validates auth before execution

    Raises:
        UnauthorizedError: If token is missing or invalid

    Example:
        >>> @bp.route('/api/users/me')
        ... @requires_auth
        ... def get_me():
        ...     return {"user_id": g.auth0_id}
    """

    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        # TESTING SHORTCUT: bypass real auth in unit/integration tests
        # FLASK_ENV is set to "testing" in tests/conftest.py
        if os.getenv("FLASK_ENV") == "testing":
            logger.warning("requires_auth: TESTING shortcut active, bypassing Auth0")
            # Set mock values for tests that expect them
            if not hasattr(g, "auth0_id"):
                g.auth0_id = "test|user123"
            if not hasattr(g, "current_user"):
                g.current_user = {"sub": g.auth0_id}
            if not hasattr(g, "access_token"):
                g.access_token = "test_token"
            return f(*args, **kwargs)

        # DEV IMPERSONATION (skip Auth0)
        is_dev = os.getenv("FLASK_ENV") == "development"
        dev_impersonation = os.getenv("DEV_IMPERSONATION", "").lower() == "true"

        if not is_dev and request.headers.get("X-Dev-Auth0-Id"):
            logger.critical(
                "SECURITY: Dev impersonation header used outside development"
            )
            raise UnauthorizedError("Invalid authentication method")

        # ℹ️ Header present but feature disabled (dev only)
        if is_dev and request.headers.get("X-Dev-Auth0-Id") and not dev_impersonation:
            logger.info(
                "Dev impersonation header ignored because DEV_IMPERSONATION is not enabled"
            )

        # DEV IMPERSONATION (dev-only, explicit opt-in)
        if is_dev and dev_impersonation:
            dev_auth0_id = request.headers.get("X-Dev-Auth0-Id")
            if dev_auth0_id and dev_auth0_id.strip():
                g.auth0_id = dev_auth0_id.strip()
                g.current_user = {"sub": dev_auth0_id.strip()}
                g.access_token = None
                logger.warning(
                    f"[DEV ONLY] impersonation active for auth0_id={dev_auth0_id.strip()}"
                )
                return f(*args, **kwargs)
        try:
            # Extract token from header
            auth_header = request.headers.get("Authorization")
            token = get_token_from_header(auth_header)

            # Validate token and get claims
            claims = validate_token(token)

            # Store in Flask g context for route access
            g.current_user = claims
            g.auth0_id = get_user_id_from_claims(claims)
            g.access_token = token

            logger.debug(f"Authenticated request from user: {g.auth0_id}")

        except UnauthorizedError:
            # Re-raise auth errors as-is
            raise
        except Exception as e:
            # Log unexpected errors but return generic message
            logger.error(f"Unexpected auth error: {e}", exc_info=True)
            raise UnauthorizedError("Authentication failed")

        return f(*args, **kwargs)

    return decorated  # type: ignore


# =============================================================================
# OPTIONAL AUTH DECORATOR
# =============================================================================


def optional_auth(f: F) -> F:
    """
    Decorator that optionally validates Auth0 JWT token.

    Unlike @requires_auth, this decorator:
    - Does NOT fail if no token is provided
    - Sets g.current_user to None if unauthenticated
    - Still validates token if one is provided

    Use for routes that work for both guests and authenticated users.

    Args:
        f: The route function to wrap

    Returns:
        Wrapped function that optionally validates auth

    Example:
        >>> @bp.route('/api/dashboard')
        ... @optional_auth
        ... def dashboard():
        ...     if g.current_user:
        ...         return {"personalized": True}
        ...     return {"personalized": False}
    """

    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        # Initialize as unauthenticated
        g.current_user = None
        g.auth0_id = None
        g.access_token = None

        auth_header = request.headers.get("Authorization")

        if auth_header:
            try:
                token = get_token_from_header(auth_header)
                claims = validate_token(token)

                g.current_user = claims
                g.auth0_id = get_user_id_from_claims(claims)
                g.access_token = token

                logger.debug(f"Optional auth: authenticated as {g.auth0_id}")

            except Exception as e:
                # Log but don't fail - user will be treated as guest
                logger.debug(f"Optional auth: token validation failed: {e}")

        return f(*args, **kwargs)

    return decorated  # type: ignore


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_current_user() -> Optional[dict]:
    """
    Get the current authenticated user from Flask g context.

    Returns:
        Dict with user claims if authenticated, None otherwise

    Example:
        >>> user = get_current_user()
        >>> if user:
        ...     print(f"Hello, {user.get('email')}")
    """
    return getattr(g, "current_user", None)


def get_current_auth0_id() -> Optional[str]:
    """
    Get the current user's Auth0 ID from Flask g context.

    Returns:
        Auth0 ID string if authenticated, None otherwise

    Example:
        >>> auth0_id = get_current_auth0_id()
        >>> if auth0_id:
        ...     user = User.query.filter_by(auth0_id=auth0_id).first()
    """
    return getattr(g, "auth0_id", None)


def is_authenticated() -> bool:
    """
    Check if the current request is authenticated.

    Returns:
        True if request has valid authentication, False otherwise

    Example:
        >>> if is_authenticated():
        ...     return get_personalized_data()
        >>> return get_public_data()
    """
    return get_current_user() is not None


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "requires_auth",
    "optional_auth",
    "get_current_user",
    "get_current_auth0_id",
    "is_authenticated",
]
