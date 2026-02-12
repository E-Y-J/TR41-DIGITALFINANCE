# =============================================================================
# Digital Finance Tracker - Flask Extensions
# PURPOSE: Flask extensions initialization and management
# =============================================================================
"""
Extensions Module

This module initializes all Flask extensions in a centralized location.
Extensions are created without app binding, then initialized in the app factory.

This pattern allows:
- Circular import prevention
- Easy testing with different configurations
- Clear separation of concerns

Usage:
    from app.core.extensions import db, cache, limiter

    # In app factory:
    def create_app():
        app = Flask(__name__)
        init_extensions(app)
        return app
"""

import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

# =============================================================================
# EXTENSION INSTANCES
# =============================================================================

# Database ORM
db = SQLAlchemy()

# Database migrations
migrate = Migrate()

# Caching (Redis or simple cache)
cache = Cache()


# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="memory://",  # Override in production with Redis
)

# CORS handling
cors = CORS()


# =============================================================================
# INITIALIZATION FUNCTION
# =============================================================================


def init_extensions(app) -> None:
    """
    Initialize all Flask extensions with the application.

    This function should be called in the application factory after
    the app is configured.

    Args:
        app: Flask application instance

    Example:
        >>> from flask import Flask
        >>> from app.core.extensions import init_extensions
        >>>
        >>> app = Flask(__name__)
        >>> app.config.from_object(config)
        >>> init_extensions(app)

    Notes:
        - Order of initialization matters for some extensions
        - Database must be initialized before migrations
        - Cache should be initialized before rate limiter in production
    """
    # Initialize SQLAlchemy
    db.init_app(app)

    # Initialize migrations (depends on db)
    migrate.init_app(app, db)

    # Initialize caching
    _init_cache(app)

    # Initialize rate limiter
    _init_limiter(app)

    # Initialize CORS
    _init_cors(app)

    # Initialize security middleware LAST (must be outermost WSGI layer)
    _init_security_middleware(app)


def _init_security_middleware(app):
    """Initialize security headers middleware as the final WSGI wrapper."""
    from app.middleware.security import init_security_middleware

    init_security_middleware(app)


def _init_cache(app) -> None:
    """
    Initialize caching with appropriate backend.

    Uses Redis in production, simple cache in development.

    Args:
        app: Flask application instance
    """
    from app.core.config import get_config

    config = get_config()

    if config.redis.enabled and config.redis.url:
        # Use Redis cache in production
        cache_config = {
            "CACHE_TYPE": "RedisCache",
            "CACHE_REDIS_URL": config.redis.url,
            "CACHE_DEFAULT_TIMEOUT": 300,  # 5 minutes
        }
    else:
        # Use simple in-memory cache for development
        cache_config = {
            "CACHE_TYPE": "SimpleCache",
            "CACHE_DEFAULT_TIMEOUT": 300,
        }

    app.config.update(cache_config)
    cache.init_app(app)


def _init_limiter(app) -> None:
    """
    Initialize rate limiter with appropriate storage.

    Uses Redis in production for distributed rate limiting.
    Falls back to memory storage if Redis is unavailable.

    Args:
        app: Flask application instance
    """
    from app.core.config import get_config
    import logging

    logger = logging.getLogger(__name__)
    config = get_config()

    if config.redis.enabled and config.redis.url:
        # Test Redis connection before using it
        try:
            import redis

            r = redis.from_url(config.redis.url)
            r.ping()
            # Redis is available, use it
            limiter._storage_uri = config.redis.url
            logger.info("Rate limiter using Redis storage")
        except Exception as e:
            # Redis not available, fall back to memory
            logger.warning(f"Redis unavailable for rate limiting, using memory: {e}")
            limiter._storage_uri = "memory://"
    else:
        limiter._storage_uri = "memory://"
        logger.info("Rate limiter using memory storage")

    # Apply rate limit settings from config
    app.config["RATELIMIT_ENABLED"] = config.RATELIMIT_ENABLED
    app.config["RATELIMIT_DEFAULT"] = config.RATELIMIT_DEFAULT

    limiter.init_app(app)

    # Exempt OPTIONS requests from rate limiting (CORS preflight)
    @limiter.request_filter
    def _skip_options_requests():
        from flask import request

        return request.method == "OPTIONS"


def _init_cors(app) -> None:
    """
    Initialize CORS with configuration.

    Allows frontend to make cross-origin requests to the API.

    Args:
        app: Flask application instance
    """
    from app.core.config import get_config

    config = get_config()

    # Dev-only header for impersonation
    allow_headers = config.cors.allow_headers
    if os.getenv("FLASK_ENV") == "development":
        allow_headers = [*allow_headers, "X-Dev-Auth0-Id"]

    cors.init_app(
        app,
        resources={r"/api/*": {"origins": config.cors.origins}},
        origins=config.cors.origins,
        methods=config.cors.methods,
        allow_headers=allow_headers,
        supports_credentials=True,
        expose_headers=["Content-Type", "Authorization"],
    )


# =============================================================================
# DATABASE UTILITIES
# =============================================================================


def reset_database(app) -> None:
    """
    Reset database (DROP ALL and recreate).

    WARNING: This deletes all data! Only use in development/testing.

    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.drop_all()
        db.create_all()


def create_tables(app) -> None:
    """
    Create all database tables.

    Use migrations for production, this is for quick development setup.

    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.create_all()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Extension instances
    "db",
    "migrate",
    "cache",
    "limiter",
    "cors",
    # Functions
    "init_extensions",
    "reset_database",
    "create_tables",
]
