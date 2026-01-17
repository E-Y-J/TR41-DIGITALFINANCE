# =============================================================================
# Digital Finance Tracker - Notification Service
# PURPOSE: Notification service layer for business logic operations
# =============================================================================
"""
Notification Service Module

AI FOUNDATION - Notifications System

This module provides the service layer for Notification operations:
- Create notifications for various events
- Get user notifications with pagination
- Mark notifications as read (single or all)
- Delete notifications
- Get unread count

Notification Types (6 core types):
    - default: General notifications
    - new_transaction: Transaction created
    - deleted_transaction: Transaction deleted
    - edited_profile: Profile updated
    - weekly_summary_ready: Weekly spending summary generated
    - category_updated: Transaction category changed

Usage:
    from app.services.notification_service import NotificationService

    # Create notification
    notification = NotificationService.create(user_id, type, message)

    # Get user notifications
    notifications, meta = NotificationService.get_user_notifications(user_id)

    # Mark as read
    NotificationService.mark_as_read(notification_id)

Design Principles:
    - Stateless class methods for all operations
    - All database commits happen here (not in routes)
    - Pagination for list operations
    - Exception-based error handling
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from uuid import UUID

from sqlalchemy import desc

from app.core.extensions import db
from app.models.notification import Notification
from app.models.enums import NotificationStatus, NotificationType
from app.utils.errors import NotFoundError, ForbiddenError, InternalError


# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# NOTIFICATION SERVICE CLASS
# =============================================================================


class NotificationService:
    """
    Service class for Notification operations.

    All methods are class methods (no instance needed).
    Handles creation, reading, updating, and deleting of notifications.

    Example:
        >>> notification = NotificationService.create_for_new_transaction(
        ...     user_id, transaction
        ... )
        >>> notifications, meta = NotificationService.get_user_notifications(user_id)
    """

    # =========================================================================
    # CREATE OPERATIONS
    # =========================================================================

    @classmethod
    def create(
        cls,
        user_id: UUID,
        notification_type: NotificationType,
        message: str,
        title: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        """
        Create a new notification.

        Args:
            user_id: User's UUID who will receive the notification
            notification_type: NotificationType enum value
            message: Notification message content
            title: Optional notification title
            data: Optional JSON metadata

        Returns:
            Created Notification instance

        Example:
            >>> notification = NotificationService.create(
            ...     user_id=user.id,
            ...     notification_type=NotificationType.NEW_TRANSACTION,
            ...     message="New expense: $50.00 for Coffee",
            ...     title="New Transaction",
            ...     data={"transaction_id": str(tx.id)}
            ... )
        """
        try:
            notification = Notification(
                user_id=user_id,
                notification_type=notification_type,
                message=message,
                data=data or {},
            )

            db.session.add(notification)
            db.session.commit()

            logger.info(
                f"Created notification for user {user_id}: {notification_type.value}"
            )
            return notification

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create notification: {e}", exc_info=True)
            raise InternalError("Failed to create notification")

    @classmethod
    def create_for_new_transaction(
        cls,
        user_id: UUID,
        transaction_amount: float,
        transaction_category: str,
        transaction_id: UUID,
    ) -> Notification:
        """
        Create a notification for a new transaction.

        Args:
            user_id: User's UUID
            transaction_amount: Transaction amount
            transaction_category: Transaction category name
            transaction_id: Transaction UUID for reference

        Returns:
            Created Notification instance
        """
        return cls.create(
            user_id=user_id,
            notification_type=NotificationType.NEW_TRANSACTION,
            title="New Transaction",
            message=f"New transaction: ${abs(transaction_amount):.2f} in {transaction_category}",
            data={"transaction_id": str(transaction_id)},
        )

    @classmethod
    def create_for_deleted_transaction(
        cls,
        user_id: UUID,
        transaction_amount: float,
        transaction_category: str,
    ) -> Notification:
        """
        Create a notification for a deleted transaction.

        Args:
            user_id: User's UUID
            transaction_amount: Deleted transaction amount
            transaction_category: Deleted transaction category

        Returns:
            Created Notification instance
        """
        return cls.create(
            user_id=user_id,
            notification_type=NotificationType.DELETED_TRANSACTION,
            title="Transaction Deleted",
            message=f"Transaction deleted: ${abs(transaction_amount):.2f} in {transaction_category}",
        )

    @classmethod
    def create_for_profile_update(cls, user_id: UUID) -> Notification:
        """
        Create a notification for profile update.

        Args:
            user_id: User's UUID

        Returns:
            Created Notification instance
        """
        return cls.create(
            user_id=user_id,
            notification_type=NotificationType.EDITED_PROFILE,
            title="Profile Updated",
            message="Your profile has been updated successfully.",
        )

    @classmethod
    def create_for_weekly_summary(
        cls,
        user_id: UUID,
        summary_data: Dict[str, Any],
    ) -> Notification:
        """
        Create a notification when weekly summary is ready.

        Args:
            user_id: User's UUID
            summary_data: Summary data to include in notification

        Returns:
            Created Notification instance
        """
        total_spent = summary_data.get("total_spent", 0)
        return cls.create(
            user_id=user_id,
            notification_type=NotificationType.WEEKLY_SUMMARY_READY,
            title="Weekly Summary Ready",
            message=f"Your weekly spending summary is ready. Total: ${total_spent:.2f}",
            data=summary_data,
        )

    @classmethod
    def create_for_category_update(
        cls,
        user_id: UUID,
        transaction_id: UUID,
        old_category: str,
        new_category: str,
    ) -> Notification:
        """
        Create a notification when transaction category is updated.

        Args:
            user_id: User's UUID
            transaction_id: Transaction UUID
            old_category: Previous category name
            new_category: New category name

        Returns:
            Created Notification instance
        """
        return cls.create(
            user_id=user_id,
            notification_type=NotificationType.CATEGORY_UPDATED,
            title="Category Updated",
            message=f"Transaction category changed from '{old_category}' to '{new_category}'",
            data={
                "transaction_id": str(transaction_id),
                "old_category": old_category,
                "new_category": new_category,
            },
        )

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    @classmethod
    def get_by_id(cls, notification_id: UUID) -> Notification:
        """
        Get notification by primary key ID.

        Args:
            notification_id: Notification's UUID primary key

        Returns:
            Notification instance

        Raises:
            NotFoundError: If notification not found

        Example:
            >>> notification = NotificationService.get_by_id(uuid.UUID("..."))
        """
        notification = Notification.query.get(notification_id)

        if notification is None:
            logger.debug(f"Notification not found by ID: {notification_id}")
            raise NotFoundError("Notification not found")

        return notification

    @classmethod
    def get_user_notification(
        cls,
        user_id: UUID,
        notification_id: UUID,
    ) -> Notification:
        """
        Get a specific notification belonging to a user.

        Args:
            user_id: User's UUID (owner)
            notification_id: Notification's UUID

        Returns:
            Notification instance

        Raises:
            NotFoundError: If notification not found
            ForbiddenError: If notification doesn't belong to user

        Example:
            >>> notification = NotificationService.get_user_notification(
            ...     user_id, notif_id
            ... )
        """
        notification = cls.get_by_id(notification_id)

        if notification.user_id != user_id:
            logger.warning(
                f"User {user_id} attempted to access notification {notification_id}"
            )
            raise ForbiddenError("You don't have access to this notification")

        return notification

    @classmethod
    def get_user_notifications(
        cls,
        user_id: UUID,
        page: int = 1,
        per_page: int = 20,
        status: Optional[NotificationStatus] = None,
        notification_type: Optional[NotificationType] = None,
    ) -> Tuple[List[Notification], Dict[str, Any]]:
        """
        Get paginated list of user's notifications.

        Args:
            user_id: User's UUID
            page: Page number (1-indexed)
            per_page: Items per page (max 100)
            status: Filter by status (UNREAD, READ)
            notification_type: Filter by type

        Returns:
            Tuple of (list of notifications, pagination metadata)

        Example:
            >>> notifications, meta = NotificationService.get_user_notifications(
            ...     user_id,
            ...     page=1,
            ...     per_page=20,
            ...     status=NotificationStatus.UNREAD
            ... )
        """
        # Ensure per_page doesn't exceed maximum
        per_page = min(per_page, 100)

        # Build base query - ordered by newest first
        query = Notification.query.filter(Notification.user_id == user_id).order_by(
            desc(Notification.created_at)
        )

        # Apply filters
        if status:
            query = query.filter(Notification.status == status)

        if notification_type:
            query = query.filter(Notification.notification_type == notification_type)

        # Execute paginated query
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # Build metadata
        meta = {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }

        logger.debug(
            f"Retrieved {len(pagination.items)} notifications for user {user_id}"
        )
        return pagination.items, meta

    @classmethod
    def get_unread_count(cls, user_id: UUID) -> int:
        """
        Get count of unread notifications for a user.

        Args:
            user_id: User's UUID

        Returns:
            Number of unread notifications

        Example:
            >>> unread_count = NotificationService.get_unread_count(user_id)
            >>> print(f"You have {unread_count} unread notifications")
        """
        return Notification.get_unread_count(user_id)

    # =========================================================================
    # UPDATE OPERATIONS
    # =========================================================================

    @classmethod
    def mark_as_read(cls, user_id: UUID, notification_id: UUID) -> Notification:
        """
        Mark a specific notification as read.

        Args:
            user_id: User's UUID (for ownership verification)
            notification_id: Notification's UUID

        Returns:
            Updated Notification instance

        Raises:
            NotFoundError: If notification not found
            ForbiddenError: If notification doesn't belong to user

        Example:
            >>> notification = NotificationService.mark_as_read(user_id, notif_id)
        """
        notification = cls.get_user_notification(user_id, notification_id)
        notification.mark_as_read()
        db.session.commit()

        logger.info(f"Marked notification {notification_id} as read")
        return notification

    @classmethod
    def mark_all_as_read(cls, user_id: UUID) -> int:
        """
        Mark all unread notifications for a user as read.

        Args:
            user_id: User's UUID

        Returns:
            Number of notifications marked as read

        Example:
            >>> count = NotificationService.mark_all_as_read(user_id)
            >>> print(f"Marked {count} notifications as read")
        """
        count = Notification.mark_all_as_read(user_id)
        db.session.commit()
        logger.info(f"Marked {count} notifications as read for user {user_id}")
        return count

    # =========================================================================
    # DELETE OPERATIONS
    # =========================================================================

    @classmethod
    def delete(cls, user_id: UUID, notification_id: UUID) -> bool:
        """
        Delete a specific notification.

        Args:
            user_id: User's UUID (for ownership verification)
            notification_id: Notification's UUID

        Returns:
            True if deleted successfully

        Raises:
            NotFoundError: If notification not found
            ForbiddenError: If notification doesn't belong to user

        Example:
            >>> NotificationService.delete(user_id, notif_id)
        """
        notification = cls.get_user_notification(user_id, notification_id)

        db.session.delete(notification)
        db.session.commit()

        logger.info(f"Deleted notification {notification_id}")
        return True

    @classmethod
    def delete_all_read(cls, user_id: UUID) -> int:
        """
        Delete all read notifications for a user.

        Args:
            user_id: User's UUID

        Returns:
            Number of notifications deleted

        Example:
            >>> count = NotificationService.delete_all_read(user_id)
            >>> print(f"Deleted {count} read notifications")
        """
        result = Notification.query.filter(
            Notification.user_id == user_id,
            Notification.status == NotificationStatus.READ,
        ).delete()

        db.session.commit()

        logger.info(f"Deleted {result} read notifications for user {user_id}")
        return result
