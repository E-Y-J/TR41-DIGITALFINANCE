# =============================================================================
# Digital Finance Tracker - Auth0 Integration
# PURPOSE: Auth0 JWT token validation and JWKS management
# =============================================================================
"""
Auth0 Token Validation Module

This module provides secure JWT token validation for Auth0:
- Fetches and caches JWKS (JSON Web Key Set) from Auth0
- Validates access tokens with proper signature verification
- Extracts user claims from validated tokens
- Provides thread-safe JWKS caching with automatic refresh

Usage:
    from app.auth.auth0 import validate_token, get_token_claims
    
    # In a route:
    token = get_token_from_header()
    claims = validate_token(token)
    user_id = claims.get("sub")

Security Notes:
    - JWKS is cached and refreshed when keys rotate
    - All validation errors return generic messages to clients
    - Detailed errors are logged for debugging
"""

import logging
from typing import Dict, Any, Optional
from urllib.request import urlopen
from functools import lru_cache
import json

from jose import jwt, JWTError, ExpiredSignatureError

from app.core.config import get_config
from app.utils.errors import (
    TokenError,
    TokenExpiredError,
    TokenInvalidError,
    UnauthorizedError,
)


# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# JWKS MANAGEMENT
# =============================================================================

class JWKSClient:
    """
    Client for fetching and caching Auth0 JSON Web Key Set (JWKS).
    
    This class manages the public keys used to verify JWT signatures.
    Keys are cached to minimize API calls and refreshed when needed.
    
    Attributes:
        jwks_uri: URL to fetch JWKS from Auth0
        _jwks: Cached JWKS data
        
    Example:
        >>> client = JWKSClient("https://tenant.auth0.com/.well-known/jwks.json")
        >>> jwks = client.get_jwks()
        >>> signing_key = client.get_signing_key("key-id-123")
    """
    
    def __init__(self, jwks_uri: str):
        """
        Initialize JWKS client.
        
        Args:
            jwks_uri: Full URL to Auth0 JWKS endpoint
        """
        self.jwks_uri = jwks_uri
        self._jwks: Optional[Dict[str, Any]] = None
    
    def get_jwks(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Fetch JWKS from Auth0, using cache when available.
        
        Args:
            force_refresh: If True, bypass cache and fetch fresh JWKS
        
        Returns:
            JWKS data containing public keys
        
        Raises:
            TokenError: If JWKS cannot be fetched
        """
        if self._jwks is None or force_refresh:
            try:
                logger.debug(f"Fetching JWKS from {self.jwks_uri}")
                with urlopen(self.jwks_uri, timeout=10) as response:
                    self._jwks = json.loads(response.read().decode())
                logger.info("JWKS fetched successfully")
            except Exception as e:
                logger.error(f"Failed to fetch JWKS: {e}")
                raise TokenError("Unable to verify token at this time")
        
        return self._jwks
    
    def get_signing_key(self, kid: str) -> Optional[Dict[str, Any]]:
        """
        Get the signing key matching the given key ID.
        
        Args:
            kid: Key ID from JWT header
        
        Returns:
            Matching key from JWKS, or None if not found
        
        Notes:
            If key is not found, JWKS is refreshed once in case of rotation.
        """
        jwks = self.get_jwks()
        
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return key
        
        # Key not found - try refreshing JWKS (might have rotated)
        logger.info(f"Key {kid} not found, refreshing JWKS")
        jwks = self.get_jwks(force_refresh=True)
        
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return key
        
        return None
    
    def clear_cache(self) -> None:
        """Clear cached JWKS data."""
        self._jwks = None
        logger.debug("JWKS cache cleared")


# =============================================================================
# JWKS CLIENT SINGLETON
# =============================================================================

@lru_cache(maxsize=1)
def get_jwks_client() -> JWKSClient:
    """
    Get the singleton JWKS client instance.
    
    Returns:
        Configured JWKSClient instance
    
    Notes:
        Uses LRU cache to ensure only one instance exists.
        Call get_jwks_client.cache_clear() to reset if needed.
    """
    config = get_config()
    jwks_uri = f"https://{config.auth0.domain}/.well-known/jwks.json"
    return JWKSClient(jwks_uri)


# =============================================================================
# TOKEN EXTRACTION
# =============================================================================

def get_token_from_header(auth_header: Optional[str]) -> str:
    """
    Extract Bearer token from Authorization header.
    
    Args:
        auth_header: Authorization header value (e.g., "Bearer eyJ...")
    
    Returns:
        The token string without "Bearer " prefix
    
    Raises:
        UnauthorizedError: If header is missing or malformed
    
    Example:
        >>> token = get_token_from_header("Bearer eyJhbGc...")
        >>> print(token[:10])
        'eyJhbGc...'
    """
    if not auth_header:
        raise UnauthorizedError("Authorization header missing")
    
    parts = auth_header.split()
    
    if len(parts) != 2:
        raise UnauthorizedError("Invalid Authorization header format")
    
    scheme, token = parts
    
    if scheme.lower() != "bearer":
        raise UnauthorizedError("Authorization scheme must be Bearer")
    
    return token


# =============================================================================
# TOKEN VALIDATION
# =============================================================================

def validate_token(token: str) -> Dict[str, Any]:
    """
    Validate an Auth0 JWT access token and return its claims.
    
    This function:
    1. Decodes the token header to get the key ID
    2. Fetches the matching public key from JWKS
    3. Verifies the signature and standard claims
    4. Returns the validated payload
    
    Args:
        token: JWT access token string
    
    Returns:
        Dictionary of validated token claims (sub, email, etc.)
    
    Raises:
        TokenExpiredError: If token has expired
        TokenInvalidError: If token signature is invalid
        TokenError: For other validation failures
    
    Example:
        >>> claims = validate_token("eyJhbGciOiJSUzI1NiIs...")
        >>> print(claims["sub"])
        'auth0|123456'
    
    Security Notes:
        - Always verify the token before trusting claims
        - The `sub` claim is the unique user identifier
        - Tokens should be validated on every request
    """
    config = get_config()
    
    # Get unverified header to find key ID
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError as e:
        logger.warning(f"Failed to decode token header: {e}")
        raise TokenInvalidError("Invalid token format")
    
    # Get the signing key
    kid = unverified_header.get("kid")
    if not kid:
        raise TokenInvalidError("Token missing key ID")
    
    jwks_client = get_jwks_client()
    signing_key = jwks_client.get_signing_key(kid)
    
    if not signing_key:
        logger.warning(f"Signing key not found: {kid}")
        raise TokenInvalidError("Token signing key not found")
    
    # Validate the token
    try:
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=config.auth0.api_audience,
            issuer=f"https://{config.auth0.domain}/"
        )
        
        logger.debug(f"Token validated for user: {payload.get('sub')}")
        return payload
        
    except ExpiredSignatureError:
        logger.info("Token has expired")
        raise TokenExpiredError()
    except JWTError as e:
        logger.warning(f"Token validation failed: {e}")
        raise TokenInvalidError("Token validation failed")


def get_token_claims(token: str) -> Dict[str, Any]:
    """
    Convenience alias for validate_token.
    
    Args:
        token: JWT access token string
    
    Returns:
        Dictionary of validated token claims
    
    Raises:
        TokenError: If validation fails
    """
    return validate_token(token)


# =============================================================================
# TOKEN CLAIM HELPERS
# =============================================================================

def get_user_id_from_claims(claims: Dict[str, Any]) -> str:
    """
    Extract the user ID from validated token claims.
    
    Args:
        claims: Validated token claims dictionary
    
    Returns:
        The Auth0 user ID (sub claim)
    
    Raises:
        TokenError: If sub claim is missing
    
    Example:
        >>> claims = validate_token(token)
        >>> user_id = get_user_id_from_claims(claims)
        >>> print(user_id)
        'auth0|507f1f77bcf86cd799439011'
    """
    user_id = claims.get("sub")
    if not user_id:
        raise TokenError("Token missing user ID")
    return user_id


def get_email_from_claims(claims: Dict[str, Any]) -> Optional[str]:
    """
    Extract email from validated token claims.
    
    Args:
        claims: Validated token claims dictionary
    
    Returns:
        Email address if present, None otherwise
    
    Notes:
        Email may not be present in access tokens by default.
        Configure Auth0 to include email in access token claims.
    """
    return claims.get("email")


def get_email_verified(claims: Dict[str, Any]) -> bool:
    """
    Check if user's email is verified.
    
    Args:
        claims: Validated token claims dictionary
    
    Returns:
        True if email is verified, False otherwise
    """
    return claims.get("email_verified", False)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "JWKSClient",
    "get_jwks_client",
    "get_token_from_header",
    "validate_token",
    "get_token_claims",
    "get_user_id_from_claims",
    "get_email_from_claims",
    "get_email_verified",
]
