# =============================================================================
# Digital Finance Tracker - Application Factory
# PURPOSE: Flask application factory with configuration and initialization
# =============================================================================
"""
Application Factory Module

This module provides the Flask application factory pattern:
- Creates and configures Flask app instance
- Initializes extensions (database, cache, etc.)
- Registers blueprints for API routes
- Sets up error handlers for consistent responses
- Configures logging

Usage:
    from app import create_app

    # Create app with default config (based on FLASK_ENV)
    app = create_app()

    # Create app with specific config
    app = create_app("testing")

    # Run the app
    if __name__ == "__main__":
        app = create_app()
        app.run()

Configuration:
    The app loads configuration based on FLASK_ENV environment variable:
    - development: Debug mode, verbose logging
    - testing: Test database, no rate limiting
    - production: Optimized settings, minimal logging
"""

import logging
from typing import Optional

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from app.core.config import get_config
from app.core.extensions import init_extensions
from app.utils.errors import AppException


# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# APPLICATION FACTORY
# =============================================================================


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Create and configure the Flask application.

    This factory function:
    1. Creates Flask app instance
    2. Loads configuration
    3. Initializes extensions
    4. Registers blueprints
    5. Sets up error handlers
    6. Configures logging

    Args:
        config_name: Optional config name ("development", "testing", "production")
                    If None, uses FLASK_ENV environment variable

    Returns:
        Configured Flask application instance

    Example:
        >>> app = create_app()
        >>> # NOTE: Port 8000 to match frontend's expected API base URL
        >>> app.run(host="0.0.0.0", port=8000)

    Notes:
        - Always use this factory, don't create Flask() directly
        - For testing, pass config_name="testing"
    """
    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)

    # Store config for easy access
    app.config["CONFIG"] = config

    # ==========================================================================
    # FLASK-SQLALCHEMY CONFIGURATION
    # Explicitly set SQLAlchemy config because from_object() doesn't read @property
    # ==========================================================================
    if config.database:
        app.config["SQLALCHEMY_DATABASE_URI"] = config.database.url
        app.config["SQLALCHEMY_ECHO"] = config.database.echo
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_size": config.database.pool_size,
            "pool_recycle": config.database.pool_recycle,
        }

    # Configure logging
    _configure_logging(app)

    logger.info(f"Creating app with config: {config.__class__.__name__}")

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Register health check
    _register_health_check(app)

    # Initialize Swagger UI
    _init_swagger(app)

    logger.info("Application created successfully")

    return app


# =============================================================================
# BLUEPRINT REGISTRATION
# =============================================================================


def _register_blueprints(app: Flask) -> None:
    """
    Register all API blueprints.

    Args:
        app: Flask application instance

    Notes:
        Add new blueprints here as they're created.
    """
    # Auth routes
    from app.api.routes.auth import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # User routes
    from app.api.routes.users import bp as users_bp

    app.register_blueprint(users_bp, url_prefix="/api/users")

    # Transaction routes
    from app.api.routes.transactions import bp as transactions_bp

    app.register_blueprint(transactions_bp, url_prefix="/api/transactions")

    # Test routes (for frontend-backend connection verification)
    from app.api.routes.test import bp as test_bp

    app.register_blueprint(test_bp, url_prefix="/api")

    # =========================================================================
    # AI Foundation: Categories, Notifications, Alerts, Summary Routes
    # =========================================================================

    # Category routes (GET only - categories are pre-defined)
    from app.api.routes.categories import bp as categories_bp

    app.register_blueprint(categories_bp, url_prefix="/api/categories")

    # Notification routes (CRUD + mark read)
    from app.api.routes.notifications import bp as notifications_bp

    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")

    # Summary routes (spending analytics)
    from app.api.routes.summary import bp as summary_bp

    app.register_blueprint(summary_bp, url_prefix="/api/summary")

    # Alert routes (financial anomaly alerts - foundation)
    from app.api.routes.alerts import alerts_bp

    app.register_blueprint(alerts_bp)  # url_prefix already set in blueprint

    # Budget routes (spending limits management)
    from app.api.routes.budgets import bp as budgets_bp

    app.register_blueprint(budgets_bp)  # url_prefix already set in blueprint

    logger.debug(
        "Registered blueprints: auth, users, transactions, test, "
        "categories, notifications, summary, alerts, budgets"
    )


# =============================================================================
# SWAGGER INITIALIZATION
# =============================================================================


def _init_swagger(app: Flask) -> None:
    """
    Initialize Swagger UI for API documentation.

    Args:
        app: Flask application instance

    Notes:
        - Swagger UI: /api/docs
        - OpenAPI JSON: /api/docs/openapi.json
    """
    from app.api.swagger import init_swagger

    init_swagger(app)
    logger.debug("Swagger UI initialized at /api/docs")


# =============================================================================
# ERROR HANDLERS
# =============================================================================


def _register_error_handlers(app: Flask) -> None:
    """
    Register error handlers for consistent error responses.

    Args:
        app: Flask application instance

    Notes:
        All errors return JSON in standard format:
        {
            "success": false,
            "error": {
                "code": "ERROR_CODE",
                "message": "Human readable message",
                "details": {...}
            }
        }
    """

    @app.errorhandler(AppException)
    def handle_app_exception(error: AppException):
        """Handle custom application exceptions."""
        logger.warning(f"AppException: {error.error_code} - {error.message}")
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Handle Werkzeug HTTP exceptions."""
        logger.warning(f"HTTPException: {error.code} - {error.description}")
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": error.name.upper().replace(" ", "_"),
                    "message": error.description,
                },
            }
        ), error.code

    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception):
        """Handle unexpected exceptions."""
        # Log the full exception for debugging
        logger.error(f"Unhandled exception: {error}", exc_info=True)

        # Return generic error to client (don't expose internals)
        return jsonify(
            {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                },
            }
        ), 500

    logger.debug("Registered error handlers")


# =============================================================================
# HEALTH CHECK
# =============================================================================


def _register_health_check(app: Flask) -> None:
    """
    Register health check endpoint.

    Args:
        app: Flask application instance

    Notes:
        Used by load balancers and container orchestration.
    """

    @app.route("/health", methods=["GET"])
    def health_check():
        """
        Health check endpoint.

        Returns:
            200: Service is healthy
        """
        return jsonify(
            {
                "status": "healthy",
                "service": "digital-finance-api",
            }
        ), 200

    @app.route("/", methods=["GET"])
    def root():
        """
        Root endpoint with API info.

        Returns:
            200: API information
        """
        return jsonify(
            {
                "name": "Digital Finance Tracker API",
                "version": "1.0.0",
                "status": "running",
                "docs": "/api/docs",  # Future: Swagger/OpenAPI docs
            }
        ), 200


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================


def _configure_logging(app: Flask) -> None:
    """
    Configure application logging.

    Args:
        app: Flask application instance

    Notes:
        - Development: DEBUG level, verbose format
        - Production: INFO level, JSON format (for log aggregation)
    """
    config = app.config.get("CONFIG")

    # Determine log level
    if config and config.DEBUG:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    logger.debug(f"Logging configured at level: {logging.getLevelName(log_level)}")


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "create_app",
]
