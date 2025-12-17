# =============================================================================
# Digital Finance Tracker - Custom Exceptions
# PURPOSE: Custom exception classes for consistent error handling
# =============================================================================
"""
Custom Exceptions Module

This module provides enterprise-standard exception classes that:
- Map to proper HTTP status codes
- Include error codes for client-side handling
- Support detailed error information
- Enable consistent error responses across the API

Usage:
    from app.utils.errors import NotFoundError, ValidationError
    
    # Raise in service/route:
    raise NotFoundError("User not found", details={"user_id": user_id})
    
    # Error handler will format response automatically

Error Response Format:
    {
        "success": false,
        "error": {
            "code": "NOT_FOUND",
            "message": "User not found",
            "details": {"user_id": "123"}
        }
    }
"""

from typing import Optional, Dict, Any
from http import HTTPStatus


# =============================================================================
# BASE EXCEPTION
# =============================================================================

class AppException(Exception):
    """
    Base exception for all application errors.
    
    All custom exceptions should inherit from this class.
    
    Attributes:
        message: Human-readable error message
        status_code: HTTP status code (default: 500)
        error_code: Machine-readable error code (e.g., "VALIDATION_ERROR")
        details: Additional error details (field errors, context, etc.)
    
    Example:
        >>> raise AppException(
        ...     message="Something went wrong",
        ...     status_code=500,
        ...     error_code="INTERNAL_ERROR",
        ...     details={"trace_id": "abc123"}
        ... )
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for JSON response.
        
        Returns:
            Dictionary with error information
        """
        response = {
            "success": False,
            "error": {
                "code": self.error_code,
                "message": self.message,
            }
        }
        
        if self.details:
            response["error"]["details"] = self.details
        
        return response
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r}, status_code={self.status_code})"


# =============================================================================
# CLIENT ERRORS (4xx)
# =============================================================================

class BadRequestError(AppException):
    """
    400 Bad Request - Invalid request syntax or parameters.
    
    Use when the request cannot be processed due to client error.
    
    Example:
        >>> raise BadRequestError("Invalid date format", details={"field": "date"})
    """
    
    def __init__(
        self,
        message: str = "Bad request",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_code="BAD_REQUEST",
            details=details
        )


class UnauthorizedError(AppException):
    """
    401 Unauthorized - Authentication required or failed.
    
    Use when:
    - No authentication token provided
    - Token is invalid or expired
    - Authentication failed
    
    Example:
        >>> raise UnauthorizedError("Token expired")
    """
    
    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            details=details
        )


class ForbiddenError(AppException):
    """
    403 Forbidden - User lacks permission for this action.
    
    Use when user is authenticated but doesn't have permission.
    
    Example:
        >>> raise ForbiddenError("Admin access required")
    """
    
    def __init__(
        self,
        message: str = "Permission denied",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.FORBIDDEN,
            error_code="FORBIDDEN",
            details=details
        )


class NotFoundError(AppException):
    """
    404 Not Found - Resource does not exist.
    
    Use when the requested resource cannot be found.
    
    Example:
        >>> raise NotFoundError("Transaction not found", details={"id": "txn_123"})
    """
    
    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.NOT_FOUND,
            error_code="NOT_FOUND",
            details=details
        )


class ConflictError(AppException):
    """
    409 Conflict - Resource already exists or state conflict.
    
    Use when:
    - Trying to create a resource that already exists
    - Concurrent modification detected
    
    Example:
        >>> raise ConflictError("Email already registered")
    """
    
    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.CONFLICT,
            error_code="CONFLICT",
            details=details
        )


class ValidationError(AppException):
    """
    422 Unprocessable Entity - Validation failed.
    
    Use when input data fails validation.
    
    Example:
        >>> raise ValidationError(
        ...     "Validation failed",
        ...     details={
        ...         "email": ["Invalid email format"],
        ...         "amount": ["Must be positive number"]
        ...     }
        ... )
    """
    
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )


class RateLimitError(AppException):
    """
    429 Too Many Requests - Rate limit exceeded.
    
    Use when user exceeds API rate limits.
    
    Example:
        >>> raise RateLimitError("Rate limit exceeded. Try again in 60 seconds.")
    """
    
    def __init__(
        self,
        message: str = "Too many requests",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )


# =============================================================================
# SERVER ERRORS (5xx)
# =============================================================================

class InternalError(AppException):
    """
    500 Internal Server Error - Unexpected server error.
    
    Use when an unexpected error occurs.
    Log the actual error, return generic message to client.
    
    Example:
        >>> raise InternalError("An unexpected error occurred")
    """
    
    def __init__(
        self,
        message: str = "An unexpected error occurred",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            details=details
        )


class ServiceUnavailableError(AppException):
    """
    503 Service Unavailable - Service temporarily unavailable.
    
    Use when:
    - Database is down
    - External service is unreachable
    - Maintenance mode
    
    Example:
        >>> raise ServiceUnavailableError("Database connection failed")
    """
    
    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            error_code="SERVICE_UNAVAILABLE",
            details=details
        )


# =============================================================================
# AUTH-SPECIFIC ERRORS
# =============================================================================

class TokenError(UnauthorizedError):
    """
    Token validation error - extends UnauthorizedError.
    
    Use for specific token issues.
    
    Example:
        >>> raise TokenError("Token has expired")
    """
    
    def __init__(
        self,
        message: str = "Invalid token",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message=message, details=details)
        self.error_code = "TOKEN_ERROR"


class TokenExpiredError(TokenError):
    """Token has expired."""
    
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message=message)
        self.error_code = "TOKEN_EXPIRED"


class TokenInvalidError(TokenError):
    """Token is malformed or invalid."""
    
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message=message)
        self.error_code = "TOKEN_INVALID"


class InsufficientScopeError(ForbiddenError):
    """
    User lacks required scope/permission.
    
    Example:
        >>> raise InsufficientScopeError(
        ...     "Missing required scope",
        ...     details={"required": "admin:read", "provided": ["user:read"]}
        ... )
    """
    
    def __init__(
        self,
        message: str = "Insufficient scope",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message=message, details=details)
        self.error_code = "INSUFFICIENT_SCOPE"


# =============================================================================
# ERROR RESPONSE HELPER
# =============================================================================

def format_error_response(error: Exception) -> Dict[str, Any]:
    """
    Format any exception into standard error response.
    
    Args:
        error: Exception to format
    
    Returns:
        Dictionary with standardized error format
    
    Example:
        >>> try:
        ...     raise ValueError("oops")
        ... except Exception as e:
        ...     response = format_error_response(e)
    """
    if isinstance(error, AppException):
        return error.to_dict()
    
    # Handle unknown exceptions
    return {
        "success": False,
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
        }
    }


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Base
    "AppException",
    # Client errors
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "RateLimitError",
    # Server errors
    "InternalError",
    "ServiceUnavailableError",
    # Auth errors
    "TokenError",
    "TokenExpiredError",
    "TokenInvalidError",
    "InsufficientScopeError",
    # Helpers
    "format_error_response",
]
