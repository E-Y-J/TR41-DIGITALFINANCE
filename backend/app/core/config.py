# =============================================================================
# Digital Finance Tracker - Configuration
# PURPOSE: Application configuration management with environment validation
# =============================================================================
"""
Configuration Module

This module handles all application configuration including:
- Environment variable loading and validation
- Auth0 configuration
- Database configuration
- Redis/Cache configuration
- Different config classes for Dev/Test/Production

Usage:
    from app.core.config import get_config
    config = get_config()
"""

import os
from typing import Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv


# =============================================================================
# LOAD ENVIRONMENT VARIABLES
# =============================================================================
# Load .env file before any config classes access os.getenv()
# This must happen before any configuration is read
load_dotenv()


# =============================================================================
# CONFIGURATION CLASSES
# =============================================================================


@dataclass
class Auth0Config:
    """
    Auth0 configuration settings.

    Attributes:
        domain: Auth0 tenant domain (e.g., 'your-tenant.auth0.com')
        api_audience: API identifier configured in Auth0
        algorithms: JWT signing algorithms (default: RS256)
        issuer: Token issuer URL (auto-generated from domain)

    Notes:
        - These values come from Auth0 Dashboard
        - Frontend must use same audience to get valid access tokens
    """

    domain: str
    api_audience: str
    client_id: str = ""
    algorithms: list = field(default_factory=lambda: ["RS256"])

    @property
    def issuer(self) -> str:
        """Generate issuer URL from domain."""
        return f"https://{self.domain}/"

    @property
    def jwks_url(self) -> str:
        """Generate JWKS URL for public key fetching."""
        return f"https://{self.domain}/.well-known/jwks.json"

    def validate(self) -> None:
        """
        Validate Auth0 configuration.

        Raises:
            ValueError: If required configuration is missing
        """
        if not self.domain:
            raise ValueError("AUTH0_DOMAIN is required")
        if not self.api_audience:
            raise ValueError("AUTH0_API_AUDIENCE is required")
        if not self.domain.endswith(".auth0.com") and "." not in self.domain:
            raise ValueError(
                f"AUTH0_DOMAIN appears invalid: {self.domain}. "
                "Expected format: your-tenant.auth0.com"
            )


@dataclass
class DatabaseConfig:
    """
    Database configuration settings.

    Attributes:
        url: Full database connection URL
        echo: Whether to log SQL queries (dev only)
        pool_size: Connection pool size
        pool_recycle: Seconds before connection recycling
    """

    url: str
    echo: bool = False
    pool_size: int = 5
    pool_recycle: int = 3600

    def validate(self) -> None:
        """Validate database configuration."""
        if not self.url:
            raise ValueError("DATABASE_URL is required")


@dataclass
class RedisConfig:
    """
    Redis configuration for caching and rate limiting.

    Attributes:
        url: Redis connection URL
        enabled: Whether Redis is enabled
    """

    url: str = "redis://localhost:6379/0"
    enabled: bool = True

    @property
    def is_configured(self) -> bool:
        """Check if Redis is properly configured."""
        return bool(self.url) and self.enabled


@dataclass
class CORSConfig:
    """
    CORS configuration settings.

    Attributes:
        origins: Allowed origins (frontend URLs)
        methods: Allowed HTTP methods
        allow_headers: Allowed request headers
    """

    origins: list = field(default_factory=lambda: ["http://localhost:5173"])
    methods: list = field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    allow_headers: list = field(
        default_factory=lambda: ["Content-Type", "Authorization"]
    )


# =============================================================================
# MAIN CONFIGURATION CLASS
# =============================================================================


class Config:
    """
    Base configuration class.

    All configuration is loaded from environment variables.
    Use get_config() to get the appropriate config for your environment.

    Attributes:
        ENV: Current environment (development/testing/production)
        DEBUG: Debug mode flag
        SECRET_KEY: Flask secret key for session signing
        auth0: Auth0 configuration object
        database: Database configuration object
        redis: Redis configuration object
        cors: CORS configuration object

    Example:
        >>> config = get_config()
        >>> print(config.auth0.domain)
        'your-tenant.auth0.com'
    """

    # Environment
    ENV: str = os.getenv("FLASK_ENV", "development")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "0") == "1"
    TESTING: bool = False

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # Auth0
    auth0: Auth0Config = None

    # Database
    database: DatabaseConfig = None

    # Redis
    redis: RedisConfig = None

    # CORS
    cors: CORSConfig = None

    # Rate Limiting
    RATELIMIT_ENABLED: bool = True
    RATELIMIT_DEFAULT: str = "100/hour"
    RATELIMIT_STORAGE_URL: Optional[str] = None

    # AI Configuration
    AI_MODEL_PATH: str = os.getenv("AI_MODEL_PATH", "app/ai/model_store/")
    AI_CONFIDENCE_THRESHOLD: float = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.7"))

    # AI Model Enable/Disable Flags (for performance tuning or cost control)
    AI_INTENT_CLASSIFIER_ENABLED: bool = os.getenv("AI_INTENT_CLASSIFIER_ENABLED", "1") == "1"
    AI_CATEGORIZER_ENABLED: bool = os.getenv("AI_CATEGORIZER_ENABLED", "1") == "1"
    AI_GUARDRAILS_ENABLED: bool = os.getenv("AI_GUARDRAILS_ENABLED", "1") == "1"
    AI_GEMINI_ENABLED: bool = os.getenv("AI_GEMINI_ENABLED", "1") == "1"

    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # =============================================================================
    # FLASK-SQLALCHEMY COMPATIBILITY
    # These properties expose config values in the format Flask extensions expect
    # =============================================================================

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Database URI for Flask-SQLAlchemy compatibility."""
        return self.database.url if self.database else ""

    @property
    def SQLALCHEMY_ECHO(self) -> bool:
        """SQL echo setting for Flask-SQLAlchemy compatibility."""
        return self.database.echo if self.database else False

    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self) -> dict:
        """Engine options for Flask-SQLAlchemy compatibility."""
        if not self.database:
            return {}
        return {
            "pool_size": self.database.pool_size,
            "pool_recycle": self.database.pool_recycle,
        }

    def __init__(self):
        """Initialize configuration from environment variables."""
        self._load_auth0_config()
        self._load_database_config()
        self._load_redis_config()
        self._load_cors_config()

    def _load_auth0_config(self) -> None:
        """Load Auth0 configuration from environment."""
        algorithms_str = os.getenv("AUTH0_ALGORITHMS", "RS256")
        algorithms = [a.strip() for a in algorithms_str.split(",")]

        self.auth0 = Auth0Config(
            domain=os.getenv("AUTH0_DOMAIN", ""),
            api_audience=os.getenv("AUTH0_API_AUDIENCE", ""),
            client_id=os.getenv("AUTH0_CLIENT_ID", ""),
            algorithms=algorithms,
        )

    def _load_database_config(self) -> None:
        """Load database configuration from environment."""
        self.database = DatabaseConfig(
            url=os.getenv("DATABASE_URL", ""),
            echo=self.DEBUG,
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
        )

    def _load_redis_config(self) -> None:
        """Load Redis configuration from environment."""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis = RedisConfig(url=redis_url, enabled=bool(redis_url))
        self.RATELIMIT_STORAGE_URL = redis_url if self.redis.enabled else None

    def _load_cors_config(self) -> None:
        """Load CORS configuration from environment."""
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        origins = [origin.strip() for origin in frontend_url.split(",")]

        self.cors = CORSConfig(origins=origins)

    def validate(self) -> None:
        """
        Validate all configuration.

        Raises:
            ValueError: If any required configuration is missing or invalid
        """
        if (
            self.SECRET_KEY == "dev-secret-key-change-in-production"
            and self.ENV == "production"
        ):
            raise ValueError("SECRET_KEY must be set in production")

        self.auth0.validate()
        self.database.validate()

    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary (for debugging).

        Returns:
            Dictionary representation of config (secrets masked)
        """
        return {
            "ENV": self.ENV,
            "DEBUG": self.DEBUG,
            "AUTH0_DOMAIN": self.auth0.domain,
            "AUTH0_API_AUDIENCE": self.auth0.api_audience,
            "DATABASE_URL": self._mask_url(self.database.url),
            "REDIS_ENABLED": self.redis.enabled,
            "CORS_ORIGINS": self.cors.origins,
        }

    @staticmethod
    def _mask_url(url: str) -> str:
        """Mask sensitive parts of URLs for logging."""
        if not url:
            return ""
        if "@" in url:
            # Mask password in database URLs
            parts = url.split("@")
            return f"***@{parts[-1]}"
        return url


class DevelopmentConfig(Config):
    """Development configuration with debug enabled."""

    ENV = "development"
    DEBUG = True

    def validate(self) -> None:
        """Skip strict validation in development."""
        # Allow missing Auth0 config in development for initial setup
        if self.database.url:
            pass  # Database is optional in early development


class TestingConfig(Config):
    """Testing configuration with test database."""

    ENV = "testing"
    TESTING = True
    DEBUG = True

    def __init__(self):
        """Initialize with test-specific settings."""
        super().__init__()
        # Use SQLite for tests if no test database URL provided
        if not self.database.url:
            self.database = DatabaseConfig(url="sqlite:///:memory:", echo=False)

    def validate(self) -> None:
        """Skip validation in testing."""
        pass


class ProductionConfig(Config):
    """Production configuration with strict validation."""

    ENV = "production"
    DEBUG = False

    def __init__(self):
        """Initialize with production settings."""
        super().__init__()
        # Stricter rate limiting in production
        self.RATELIMIT_DEFAULT = "60/hour"

    def validate(self) -> None:
        """Strict validation for production."""
        super().validate()

        if not self.redis.enabled:
            raise ValueError("Redis is required in production for rate limiting")


# =============================================================================
# CONFIGURATION FACTORY
# =============================================================================

# Configuration mapping
CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

# Cached config instance
_config_instance: Optional[Config] = None


def get_config(config_name: Optional[str] = None) -> Config:
    """
    Get configuration for current environment.

    Uses module-level caching to ensure single instance (singleton pattern).

    Args:
        config_name: Optional environment name override

    Returns:
        Config: Configuration object for current environment

    Example:
        >>> config = get_config()
        >>> config.auth0.domain
        'your-tenant.auth0.com'
    """
    global _config_instance

    # If config_name is provided, create a new instance (for testing)
    if config_name:
        config_class = CONFIG_MAP.get(config_name, DevelopmentConfig)
        return config_class()

    # Use cached instance for default config
    if _config_instance is None:
        env = os.getenv("FLASK_ENV", "development")
        config_class = CONFIG_MAP.get(env, DevelopmentConfig)
        _config_instance = config_class()

    return _config_instance


def validate_config() -> None:
    """
    Validate current configuration.

    Call this at application startup to fail fast on misconfigurations.

    Raises:
        ValueError: If configuration is invalid
    """
    config = get_config()
    config.validate()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "Config",
    "DevelopmentConfig",
    "TestingConfig",
    "ProductionConfig",
    "Auth0Config",
    "DatabaseConfig",
    "RedisConfig",
    "CORSConfig",
    "get_config",
    "validate_config",
]
