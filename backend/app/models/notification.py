# =============================================================================
# Digital Finance Tracker - Notification Model
# PURPOSE: Notification database model for user notifications
# =============================================================================
"""
Notification Model Module

This module defines the Notification model for the local database:
- Stores user notifications
- Supports 6 core notification types
- Enables frontend notification system

Database Table: notifications
Primary Key: id (UUID)
Foreign Key: user_id (references users.id)

Notifications are created by backend when events occur:
- Transaction created/deleted
- Profile updated
- Weekly summary ready
- AI categorization changes

Relationship:
    - Many Notifications belong to one User (N:1)

Usage:
    from app.models import Notification, NotificationType, NotificationStatus

    # Create notification
    notification = Notification(
        user_id=user.id,
        type=NotificationType.NEW_TRANSACTION,
        message="New transaction: -$50.00 at Starbucks",
        data={"transaction_id": str(transaction.id)}
    )
    db.session.add(notification)
    db.session.commit()

    # Get unread notifications for user
    unread = Notification.query.filter_by(
        user_id=user.id,
        status=NotificationStatus.UNREAD
    ).all()

Notes:
    - status defaults to UNREAD
    - type defaults to DEFAULT
    - data stores extra context (transaction_id, etc.)
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, TYPE_CHECKING

from sqlalchemy import DateTime, Text, String, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.extensions import db
from app.models.enums import NotificationStatus, NotificationType

if TYPE_CHECKING:
    from app.models.user import User


# =============================================================================
# NOTIFICATION MODEL
# =============================================================================


class Notification(db.Model):
    """
    Notification model representing a user notification.

    This model stores notifications for users, triggered by various
    events in the application.

    Attributes:
        id: Primary key UUID
        user_id: Foreign key to users table (required)
        type: Notification type (default, new_transaction, etc.)
        status: Read status (unread, read)
        message: Notification message text
        data: JSON object with extra context (transaction_id, etc.)
        created_at: Notification creation timestamp

    Relationships:
        user: Many-to-One relationship with User model

    Notification Types (6 core):
        - DEFAULT: Generic/system notification
        - NEW_TRANSACTION: Transaction created
        - DELETED_TRANSACTION: Transaction deleted
        - EDITED_PROFILE: Profile updated
        - WEEKLY_SUMMARY_READY: Weekly AI summary available
        - CATEGORY_UPDATED: AI re-categorized a transaction

    Example:
        >>> notification = Notification(
        ...     user_id=user.id,
        ...     type=NotificationType.NEW_TRANSACTION,
        ...     message="New transaction: -$50.00 at Starbucks",
        ...     data={"transaction_id": "txn-uuid"}
        ... )
        >>> db.session.add(notification)
        >>> db.session.commit()
    """

    __tablename__ = "notifications"

    # =========================================================================
    # PRIMARY KEY
    # =========================================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Primary key UUID",
    )

    # =========================================================================
    # FOREIGN KEY
    # =========================================================================

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to users table",
    )

    # =========================================================================
    # NOTIFICATION FIELDS
    # =========================================================================

    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(
            NotificationType,
            name="notification_type_enum",
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
            validate_strings=True,
        ),
        nullable=False,
        default=NotificationType.DEFAULT,
        index=True,
        doc="Notification type",
    )

    status: Mapped[NotificationStatus] = mapped_column(
        Enum(
            NotificationStatus,
            name="notification_status_enum",
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
            validate_strings=True,
        ),
        nullable=False,
        default=NotificationStatus.UNREAD,
        index=True,
        doc="Notification read status",
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Notification title",
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Notification message",
    )

    data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=lambda: {},
        doc="Extra notification context (transaction_id, etc.)",
    )

    # =========================================================================
    # TIMESTAMPS
    # =========================================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        doc="Notification creation timestamp",
    )

    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When notification was read",
    )

    # =========================================================================
    # INDEXES
    # =========================================================================

    __table_args__ = (
        # Composite index for user + status queries (get unread notifications)
        db.Index("idx_notification_user_status", "user_id", "status"),
        # Composite index for user + notification_type queries
        db.Index("idx_notification_user_type", "user_id", "notification_type"),
        # Composite index for user + created_at (for sorting)
        db.Index("idx_notification_user_created", "user_id", "created_at"),
    )

    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================

    # Many Notifications belong to one User (N:1 relationship)
    user: Mapped["User"] = relationship(
        "User",
        back_populates="notifications",
    )

    # =========================================================================
    # METHODS
    # =========================================================================

    def __repr__(self) -> str:
        """String representation of Notification."""
        return f"<Notification {self.notification_type.value}: {self.message[:30]}...>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert notification to dictionary for API response.

        Returns:
            Dictionary representation of notification

        Example:
            >>> notification.to_dict()
            {
                "id": "uuid-string",
                "type": "new_transaction",
                "status": "unread",
                "message": "New transaction...",
                "data": {"transaction_id": "..."},
                "created_at": "2026-01-06T10:30:00Z"
            }
        """
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "type": self.notification_type.value,
            "status": self.status.value,
            "title": self.title,
            "message": self.message,
            "data": self.data or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None,
        }

    def mark_as_read(self) -> None:
        """
        Mark this notification as read.

        Example:
            >>> notification.mark_as_read()
            >>> db.session.commit()
        """
        self.status = NotificationStatus.READ

    # =========================================================================
    # CLASS METHODS
    # =========================================================================

    @classmethod
    def get_by_user_id(
        cls,
        user_id: uuid.UUID,
        status: Optional[NotificationStatus] = None,
        notification_type: Optional[NotificationType] = None,
    ) -> List["Notification"]:
        """
        Get notifications for a user with optional filters.

        Args:
            user_id: User UUID
            status: Optional filter by status (UNREAD, READ)
            notification_type: Optional filter by type

        Returns:
            List of Notification instances, ordered by created_at desc

        Example:
            >>> unread = Notification.get_by_user_id(
            ...     user.id,
            ...     status=NotificationStatus.UNREAD
            ... )
        """
        query = cls.query.filter_by(user_id=user_id)

        if status:
            query = query.filter(cls.status == status)

        if notification_type:
            query = query.filter(cls.notification_type == notification_type)

        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_unread_count(cls, user_id: uuid.UUID) -> int:
        """
        Get count of unread notifications for a user.

        Args:
            user_id: User UUID

        Returns:
            Count of unread notifications

        Example:
            >>> count = Notification.get_unread_count(user.id)
            >>> count
            5
        """
        return cls.query.filter_by(
            user_id=user_id, status=NotificationStatus.UNREAD
        ).count()

    @classmethod
    def mark_all_as_read(cls, user_id: uuid.UUID) -> int:
        """
        Mark all notifications as read for a user.

        Args:
            user_id: User UUID

        Returns:
            Number of notifications marked as read

        Example:
            >>> count = Notification.mark_all_as_read(user.id)
            >>> db.session.commit()
            >>> count
            5
        """
        result = cls.query.filter_by(
            user_id=user_id, status=NotificationStatus.UNREAD
        ).update({cls.status: NotificationStatus.READ})

        return result

    @classmethod
    def create_notification(
        cls,
        user_id: uuid.UUID,
        notification_type: NotificationType,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> "Notification":
        """
        Create a new notification.

        Factory method for creating notifications.

        Args:
            user_id: User UUID
            notification_type: Type of notification
            message: Notification message
            data: Optional extra context

        Returns:
            Created Notification instance (not committed)

        Example:
            >>> notification = Notification.create_notification(
            ...     user_id=user.id,
            ...     notification_type=NotificationType.NEW_TRANSACTION,
            ...     message="New transaction: -$50.00 at Starbucks",
            ...     data={"transaction_id": str(transaction.id)}
            ... )
            >>> db.session.add(notification)
            >>> db.session.commit()
        """
        return cls(
            user_id=user_id,
            type=notification_type,
            status=NotificationStatus.UNREAD,
            message=message,
            data=data or {},
        )


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "Notification",
]
