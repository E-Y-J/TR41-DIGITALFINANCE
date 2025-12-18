# =============================================================================
# Digital Finance Tracker - User Model
# PURPOSE: User database model for storing Auth0 user data locally
# =============================================================================
"""
User Model Module

This module defines the User model for the local database:
- Stores Auth0 user data for local reference
- Links to other models (transactions, budgets, etc.)
- Provides user preferences and settings storage

Database Table: users
Primary Key: id (UUID)
Unique Constraint: auth0_id

Usage:
    from app.models.user import User

    # Find user by Auth0 ID
    user = User.query.filter_by(auth0_id="auth0|123").first()

    # Create new user
    user = User(
        auth0_id="auth0|123",
        email="user@example.com",
        name="John Doe"
    )
    db.session.add(user)
    db.session.commit()

Notes:
    - auth0_id is the unique identifier from Auth0 (sub claim)
    - Email may not be verified - check email_verified flag
    - User preferences are stored as JSON in settings column
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.extensions import db


# =============================================================================
# USER MODEL
# =============================================================================


class User(db.Model):
    """
    User model representing an authenticated user.

    This model stores Auth0 user information locally for:
    - Linking to other database tables
    - Storing user preferences
    - Quick access without Auth0 API calls

    Attributes:
        id: Primary key UUID
        auth0_id: Auth0 user identifier (sub claim)
        email: User's email address
        email_verified: Whether email is verified in Auth0
        name: Display name
        nickname: Short nickname
        picture: Profile picture URL
        settings: JSON object for user preferences
        is_active: Whether user account is active
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login: Last login timestamp

    Example:
        >>> user = User(
        ...     auth0_id="auth0|507f1f77bcf86cd799439011",
        ...     email="user@example.com",
        ...     name="John Doe"
        ... )
        >>> db.session.add(user)
        >>> db.session.commit()
    """

    __tablename__ = "users"

    # =========================================================================
    # PRIMARY KEY
    # =========================================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Primary key UUID"
    )

    # =========================================================================
    # AUTH0 FIELDS
    # =========================================================================

    auth0_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
        doc="Auth0 user ID (sub claim)",
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True, index=True, doc="User email address"
    )

    email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, doc="Whether email is verified in Auth0"
    )

    # =========================================================================
    # PROFILE FIELDS
    # =========================================================================

    name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, doc="User's display name"
    )

    nickname: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, doc="Short nickname"
    )

    picture: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, doc="Profile picture URL"
    )

    # =========================================================================
    # SETTINGS & PREFERENCES
    # =========================================================================

    settings: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, default=dict, nullable=False, doc="User preferences and settings as JSON"
    )

    # =========================================================================
    # STATUS FIELDS
    # =========================================================================

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, doc="Whether user account is active"
    )

    # =========================================================================
    # TIMESTAMPS
    # =========================================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Account creation timestamp",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Last update timestamp",
    )

    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, doc="Last login timestamp"
    )

    # =========================================================================
    # RELATIONSHIPS (to be added as models are created)
    # =========================================================================

    # transactions = relationship("Transaction", back_populates="user")
    # budgets = relationship("Budget", back_populates="user")
    # categories = relationship("Category", back_populates="user")

    # =========================================================================
    # METHODS
    # =========================================================================

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User {self.email or self.auth0_id}>"

    def to_dict(self, include_settings: bool = False) -> Dict[str, Any]:
        """
        Convert user to dictionary for API response.

        Args:
            include_settings: Whether to include user settings

        Returns:
            Dictionary representation of user

        Example:
            >>> user.to_dict()
            {
                "id": "...",
                "email": "user@example.com",
                "name": "John Doe",
                ...
            }
        """
        data = {
            "id": str(self.id),
            "auth0_id": self.auth0_id,
            "email": self.email,
            "email_verified": self.email_verified,
            "name": self.name,
            "nickname": self.nickname,
            "picture": self.picture,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

        if include_settings:
            data["settings"] = self.settings

        return data

    def update_from_claims(self, claims: Dict[str, Any]) -> bool:
        """
        Update user data from Auth0 token claims.

        Args:
            claims: Dictionary of Auth0 token claims

        Returns:
            True if any fields were updated, False otherwise

        Example:
            >>> claims = validate_token(token)
            >>> changed = user.update_from_claims(claims)
            >>> if changed:
            ...     db.session.commit()
        """
        updated = False

        # Map claims to user fields
        claim_mappings = {
            "email": "email",
            "email_verified": "email_verified",
            "name": "name",
            "nickname": "nickname",
            "picture": "picture",
        }

        for claim_key, field_name in claim_mappings.items():
            claim_value = claims.get(claim_key)
            if claim_value is not None:
                current_value = getattr(self, field_name)
                if current_value != claim_value:
                    setattr(self, field_name, claim_value)
                    updated = True

        return updated

    def update_last_login(self) -> None:
        """Update last_login to current time."""
        self.last_login = datetime.now(timezone.utc)

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a user setting value.

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default

        Example:
            >>> currency = user.get_setting("currency", "USD")
        """
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a user setting value.

        Args:
            key: Setting key
            value: Value to set

        Example:
            >>> user.set_setting("currency", "EUR")
            >>> db.session.commit()
        """
        # Create a new dict to trigger SQLAlchemy change detection
        new_settings = dict(self.settings)
        new_settings[key] = value
        self.settings = new_settings

    # =========================================================================
    # CLASS METHODS
    # =========================================================================

    @classmethod
    def get_by_auth0_id(cls, auth0_id: str) -> Optional["User"]:
        """
        Find user by Auth0 ID.

        Args:
            auth0_id: Auth0 user ID (sub claim)

        Returns:
            User instance or None if not found

        Example:
            >>> user = User.get_by_auth0_id("auth0|123")
        """
        return cls.query.filter_by(auth0_id=auth0_id).first()

    @classmethod
    def get_by_email(cls, email: str) -> Optional["User"]:
        """
        Find user by email address.

        Args:
            email: User email address

        Returns:
            User instance or None if not found

        Example:
            >>> user = User.get_by_email("user@example.com")
        """
        return cls.query.filter_by(email=email).first()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "User",
]
