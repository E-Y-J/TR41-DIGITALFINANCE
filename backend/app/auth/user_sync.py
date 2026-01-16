# =============================================================================
# Digital Finance Tracker - User Sync
# PURPOSE: Synchronize Auth0 user data to local database
# =============================================================================
"""
User Sync Module

This module handles synchronization of Auth0 user data to the local database:
- Creates local user record on first login
- Updates user info from token claims
- Tracks last login timestamps

Usage:
    from app.auth.user_sync import sync_user_from_claims

    # In auth decorator or middleware:
    claims = validate_token(token)
    user = sync_user_from_claims(claims)
    # user is now a local database User object

Why Sync Users Locally?
    1. Link transactions/data to users with foreign keys
    2. Store user preferences and settings
    3. Enable queries without Auth0 API calls
    4. Support offline/cached user lookups
    5. Enable user activity tracking
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.core.extensions import db
from app.models.user import User
from app.utils.errors import InternalError


# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# SYNC FUNCTIONS
# =============================================================================


def sync_user_from_claims(claims: Dict[str, Any]) -> User:
    """
    Sync Auth0 token claims to local database user.

    This function:
    1. Extracts user info from token claims
    2. Creates new user if first login
    3. Updates existing user if info changed
    4. Updates last login timestamp

    Args:
        claims: Validated Auth0 token claims dictionary

    Returns:
        User instance (created or updated)

    Raises:
        InternalError: If sync fails due to database error

    Example:
        >>> claims = validate_token(token)
        >>> user = sync_user_from_claims(claims)
        >>> print(user.email)
        'user@example.com'

    Notes:
        - Call this after successful token validation
        - Database commit is performed automatically
        - Safe to call multiple times (idempotent)
    """
    auth0_id = claims.get("sub")

    if not auth0_id:
        logger.error("Token claims missing 'sub' field")
        raise InternalError("Invalid token claims")

    try:
        # Try to find existing user
        user = User.get_by_auth0_id(auth0_id)

        if user is None:
            # Create new user on first login
            user = _create_user_from_claims(claims)
            logger.info(f"Created new user: {auth0_id}")
        else:
            # Update existing user if claims changed
            if user.update_from_claims(claims):
                logger.debug(f"Updated user data: {auth0_id}")

            # Always update last login
            user.update_last_login()

        db.session.commit()
        return user

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to sync user {auth0_id}: {e}", exc_info=True)
        raise InternalError("Failed to sync user data")


def _parse_name_from_claims(claims: Dict[str, Any]) -> tuple[str, str]:
    """
    Parse first_name and last_name from Auth0 claims.

    Auth0 may provide 'name', 'given_name', 'family_name', or 'nickname'.
    We prioritize given_name/family_name, then split 'name' if available.

    Args:
        claims: Auth0 token claims

    Returns:
        Tuple of (first_name, last_name)
    """
    # Try explicit given_name/family_name first (standard OIDC claims)
    first_name = claims.get("given_name", "")
    last_name = claims.get("family_name", "")

    # If not available, try to split the 'name' claim
    if not first_name and not last_name:
        full_name = claims.get("name", "")
        if full_name:
            parts = full_name.strip().split(" ", 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""

    # Fallback to nickname or email prefix
    if not first_name:
        first_name = claims.get("nickname", "")
    if not first_name:
        email = claims.get("email", "")
        first_name = email.split("@")[0] if email else "User"

    return first_name, last_name


def _create_user_from_claims(claims: Dict[str, Any]) -> User:
    """
    Create a new User from Auth0 token claims.

    Args:
        claims: Validated Auth0 token claims

    Returns:
        New User instance (not yet committed)

    Notes:
        This is an internal function - use sync_user_from_claims instead.
        Auth0 name is parsed into first_name and last_name.
    """
    first_name, last_name = _parse_name_from_claims(claims)

    user = User(
        auth0_id=claims["sub"],
        email=claims.get("email"),
        first_name=first_name,
        last_name=last_name,
        last_login=datetime.now(timezone.utc),
        settings={
            "currency": "USD",  # Default currency
            "timezone": "UTC",  # Default timezone
        },
    )

    db.session.add(user)
    return user


# =============================================================================
# USER LOOKUP FUNCTIONS
# =============================================================================


def get_or_create_user(auth0_id: str, claims: Optional[Dict[str, Any]] = None) -> User:
    """
    Get existing user or create new one from claims.

    Args:
        auth0_id: Auth0 user ID (sub claim)
        claims: Optional token claims for creating new user

    Returns:
        User instance

    Raises:
        InternalError: If user not found and no claims provided

    Example:
        >>> user = get_or_create_user("auth0|123", claims)
    """
    user = User.get_by_auth0_id(auth0_id)

    if user is not None:
        return user

    if claims is None:
        raise InternalError("Cannot create user without claims")

    return sync_user_from_claims(claims)


def get_user_by_auth0_id(auth0_id: str) -> Optional[User]:
    """
    Get user by Auth0 ID without syncing.

    Args:
        auth0_id: Auth0 user ID (sub claim)

    Returns:
        User instance or None if not found

    Example:
        >>> user = get_user_by_auth0_id("auth0|123")
        >>> if user:
        ...     print(user.email)
    """
    return User.get_by_auth0_id(auth0_id)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "sync_user_from_claims",
    "get_or_create_user",
    "get_user_by_auth0_id",
]
