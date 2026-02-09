# =============================================================================
# Middleware Package
# =============================================================================
"""
Middleware components for Flask application.

Contains WSGI middleware for cross-cutting concerns like security headers.
"""

__all__ = ["init_security_middleware"]

from app.middleware.security import init_security_middleware
