# =============================================================================
# Security Middleware - Header Management
# =============================================================================
"""
Security middleware for Flask application.

Adds security headers to all responses:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block

Note: Server header removal is handled by custom Werkzeug request handler in run.py
"""

from flask import Flask
import logging

logger = logging.getLogger(__name__)


def init_security_middleware(app: Flask) -> None:
    """
    Initialize security headers using Flask's after_request decorator.

    Args:
        app: Flask application instance
    """

    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")
        return response

    logger.info("Security headers middleware initialized")
