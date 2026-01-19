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

Relationship:
    - One User can have many Transactions (1:N)
    - Auth0 handles sensitive personal data (address, DOB, etc.)

Usage:
    from app.models.user import User

    # Find user by Auth0 ID
    user = User.query.filter_by(auth0_id="auth0|123").first()

    # Create new user
    user = User(
        auth0_id="auth0|123",
        email="user@example.com",
        first_name="John",
        last_name="Doe"
    )
    db.session.add(user)
    db.session.commit()

Notes:
    - auth0_id is the unique identifier from Auth0 (sub claim)
    - Email verification is managed by Auth0, not stored locally
    - User preferences are stored as JSON in settings column
    - Personal data (address, DOB) managed by Auth0, not stored locally
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Dict, Any, TYPE_CHECKING

from sqlalchemy import String, DateTime, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.extensions import db
from app.models.enums import AccountStatus, UserRole

if TYPE_CHECKING:
    from app.models.transaction import Transaction
    from app.models.notification import Notification
    from app.models.alert import Alert
    from app.models.budget import Budget

# =============================================================================
# USER MODEL
# =============================================================================


class User(db.Model):
    """
    User model representing an authenticated user.

    This model stores Auth0 user information locally for:
    - Linking to other database tables (transactions, etc.)
    - Storing user preferences and app-specific data
    - Quick access without Auth0 API calls

    Note: Sensitive personal data (address, DOB, etc.) is managed by Auth0,
    not stored locally. This reduces risk and simplifies our schema.

    Attributes:
        id: Primary key UUID
        auth0_id: Auth0 user identifier (sub claim)
        email: User's email address
        first_name: User's first name (per ERD)
        last_name: User's last name (per ERD)
        account_status: Account status (pending, active, suspended)
        role: User role (user, admin)
        salary_amount: User's salary for budgeting features
        settings: JSON object for user preferences
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login: Last login timestamp

    Relationships:
        transactions: One-to-Many relationship with Transaction model

    Example:
        >>> user = User(
        ...     auth0_id="auth0|507f1f77bcf86cd799439011",
        ...     email="user@example.com",
        ...     first_name="John",
        ...     last_name="Doe"
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

    # =========================================================================
    # PROFILE FIELDS (per ERD)
    # =========================================================================

    first_name: Mapped[str] = mapped_column(
        String(255), nullable=False, doc="User's first name"
    )

    last_name: Mapped[str] = mapped_column(
        String(255), nullable=False, doc="User's last name"
    )

    nickname: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, doc="User's optional nickname/display name"
    )

    # =========================================================================
    # SETTINGS & PREFERENCES
    # =========================================================================

    settings: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, default=dict, nullable=False, doc="User preferences and settings as JSON"
    )

    # =========================================================================
    # STATUS & ROLE FIELDS (per ERD)
    # =========================================================================

    account_status: Mapped[AccountStatus] = mapped_column(
        Enum(
            AccountStatus,
            name="account_status_enum",
            native_enum=False,
            values_callable=lambda obj: [
                e.value for e in obj
            ],  # map to lowercase values
            validate_strings=True,
        ),
        default=AccountStatus.PENDING,
        nullable=False,
        index=True,
        doc="Account status: pending, active, suspended, or deactivated",
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role_enum",
            native_enum=False,
            values_callable=lambda obj: [
                e.value for e in obj
            ],  # map to lowercase values
            validate_strings=True,
        ),
        default=UserRole.USER,
        nullable=False,
        index=True,
        doc="User role: user or admin",
    )

    # =========================================================================
    # FINANCIAL FIELDS (per ERD)
    # =========================================================================

    salary_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
        doc="User's salary amount for budgeting features",
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
    # RELATIONSHIPS
    # =========================================================================

    # One User can have many Transactions (1:N relationship)
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # One User can have many Notifications (1:N relationship)
    # For notification system
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # One User can have many Alerts (1:N relationship)
    # For anomaly detection alerts
    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # One User can have many Budgets (1:N relationship)
    # For spending limit management
    budgets: Mapped[list["Budget"]] = relationship(
        "Budget",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def full_name(self) -> str:
        """
        Return user's full name (first_name + last_name).

        Returns:
            Combined first and last name with space between
        """
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_active(self) -> bool:
        """
        Check if user account is active.

        Returns:
            True if account_status is ACTIVE, False otherwise
        """
        return self.account_status == AccountStatus.ACTIVE

    @property
    def is_deactivated(self) -> bool:
        """
        Check if user account is deactivated.

        Returns:
            True if account_status is DEACTIVATED, False otherwise
        """
        return self.account_status == AccountStatus.DEACTIVATED

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
            "first_name": self.first_name,
            "last_name": self.last_name,
            "nickname": self.nickname,
            "full_name": self.full_name,
            "account_status": self.account_status.value,
            "role": self.role.value,
            "salary_amount": str(self.salary_amount),
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
        # Note: Auth0 provides 'given_name' and 'family_name' for first/last name
        # 'nickname' is also provided by Auth0
        claim_mappings = {
            "email": "email",
            "given_name": "first_name",
            "family_name": "last_name",
            "nickname": "nickname",
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
