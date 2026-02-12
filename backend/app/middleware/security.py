# =============================================================================
# Digital Finance Tracker - Security Middleware
# PURPOSE: Security headers management for all HTTP responses
# =============================================================================
"""
Security middleware for Flask application.

Adds comprehensive security headers to all responses:
- X-Content-Type-Options: nosniff (prevent MIME-sniffing)
- X-Frame-Options: DENY (prevent clickjacking)
- X-XSS-Protection: 1; mode=block (legacy XSS filter)
- Strict-Transport-Security: HSTS (force HTTPS)
- Referrer-Policy: strict-origin-when-cross-origin (referrer control)
- Permissions-Policy: restrict browser features
- Content-Security-Policy: CSP for API responses
- Cache-Control: prevent caching of sensitive responses

Also removes information-leaking headers:
- X-Powered-By
- Server (where possible)

References:
- OWASP Secure Headers: https://owasp.org/www-project-secure-headers/
- MDN Security Headers: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers

Note: Server header removal is also handled by custom Werkzeug request handler in run.py
"""

from flask import Flask, request
import logging
import os

logger = logging.getLogger(__name__)


def init_security_middleware(app: Flask) -> None:
    """
    Initialize security headers using Flask's after_request decorator.

    Args:
        app: Flask application instance

    Notes:
        - HSTS is only added for HTTPS requests or in production
        - Some headers use setdefault() to allow route-specific overrides
    """
    # Get environment for conditional headers
    is_production = os.getenv("FLASK_ENV", "development") == "production"

    @app.after_request
    def add_security_headers(response):
        """
        Add comprehensive security headers to all responses.

        Headers added:
        - X-Content-Type-Options: Prevents MIME-type sniffing
        - X-Frame-Options: Prevents clickjacking via iframes
        - X-XSS-Protection: Legacy XSS filter (for older browsers)
        - Strict-Transport-Security: Forces HTTPS connections
        - Referrer-Policy: Controls referrer information
        - Permissions-Policy: Restricts browser features
        - Content-Security-Policy: API-appropriate CSP
        - Cache-Control: Prevents caching of API responses

        Returns:
            Response object with security headers added
        """
        # =================================================================
        # BASIC SECURITY HEADERS (Always applied)
        # =================================================================
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")

        # =================================================================
        # HSTS - HTTP Strict Transport Security
        # Forces browsers to use HTTPS for future requests
        # Only add for HTTPS requests or production environment
        # =================================================================
        if request.is_secure or is_production:
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains; preload"
            )

        # =================================================================
        # REFERRER POLICY
        # Controls how much referrer information is sent
        # =================================================================
        response.headers.setdefault(
            "Referrer-Policy",
            "strict-origin-when-cross-origin"
        )

        # =================================================================
        # PERMISSIONS POLICY (formerly Feature-Policy)
        # Restricts which browser features can be used
        # =================================================================
        response.headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=(), payment=(), usb=()"
        )

        # =================================================================
        # CONTENT SECURITY POLICY (API-appropriate)
        # Restrictive CSP for API responses
        # =================================================================
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'none'; frame-ancestors 'none'"
        )

        # =================================================================
        # CACHE CONTROL for API responses
        # Prevent caching of sensitive data
        # =================================================================
        if request.path.startswith("/api/"):
            response.headers.setdefault(
                "Cache-Control",
                "no-store, no-cache, must-revalidate, private"
            )
            response.headers.setdefault("Pragma", "no-cache")
            response.headers.setdefault("Expires", "0")

        # =================================================================
        # REMOVE INFORMATION LEAKING HEADERS
        # Hide server technology stack from attackers
        # =================================================================
        # Remove X-Powered-By if present
        response.headers.pop("X-Powered-By", None)

        # Note: Server header is harder to remove in Flask/Werkzeug
        # It's handled in run.py via custom WSGIRequestHandler

        return response

    logger.info("Security headers middleware initialized (comprehensive)")
