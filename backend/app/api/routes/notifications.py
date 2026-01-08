# =============================================================================
# Digital Finance Tracker - Notifications Routes
# PURPOSE: Notification API routes for user notification management
# =============================================================================
"""
Notifications Routes Module

AI Foundation - User Notification System

This module provides API endpoints for notification operations:
- GET /api/notifications - Get user notifications (paginated)
- GET /api/notifications/unread-count - Get unread count
- PATCH /api/notifications/<id>/read - Mark notification as read
- PATCH /api/notifications/read-all - Mark all as read
- DELETE /api/notifications/<id> - Delete notification
- DELETE /api/notifications/read - Delete all read notifications

Notification Types (6 core types):
    - default: General notifications
    - new_transaction: Transaction created
    - deleted_transaction: Transaction deleted
    - edited_profile: Profile updated
    - weekly_summary_ready: Weekly spending summary generated
    - category_updated: Transaction category changed

Usage:
    # Register blueprint in app factory
    from app.api.routes.notifications import bp as notifications_bp
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
"""

import logging
from flask import Blueprint, request, g

from app.auth.decorators import requires_auth
from app.auth.user_sync import sync_user_from_claims
from app.services.notification_service import NotificationService
from app.schemas.notification_schema import (
    notification_schema,
    notification_list_schema,
)
from app.models.enums import NotificationStatus, NotificationType
from app.utils.helpers import success_response, parse_uuid, validate_pagination
from app.utils.errors import ValidationError


# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# BLUEPRINT SETUP
# =============================================================================

bp = Blueprint("notifications", __name__)


# =============================================================================
# GET ALL NOTIFICATIONS
# =============================================================================


@bp.route("", methods=["GET"])
@requires_auth
def get_notifications():
    """
    Get user's notifications with pagination.

    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 20, max: 100)
        status (str): Filter by status (unread, read)
        type (str): Filter by notification type

    Returns:
        200: List of notifications with pagination metadata

    Example Response:
        {
            "success": true,
            "data": [
                {
                    "id": "uuid",
                    "notification_type": "new_transaction",
                    "title": "New Transaction",
                    "message": "New expense: $50.00 for Coffee",
                    "status": "unread",
                    "created_at": "2024-01-15T10:30:00Z"
                },
                ...
            ],
            "meta": {
                "page": 1,
                "per_page": 20,
                "total": 45,
                "total_pages": 3
            },
            "message": "Notifications retrieved successfully"
        }
    """
    # Sync user from JWT claims
    user = sync_user_from_claims(g.jwt_claims)

    # Parse pagination
    page, per_page = validate_pagination(
        request.args.get("page", 1, type=int),
        request.args.get("per_page", 20, type=int),
    )

    # Parse optional filters
    status = None
    status_param = request.args.get("status", "").lower()
    if status_param:
        try:
            status = NotificationStatus(status_param)
        except ValueError:
            raise ValidationError(
                f"Invalid status: {status_param}. Must be 'unread' or 'read'"
            )

    notification_type = None
    type_param = request.args.get("type", "").lower()
    if type_param:
        try:
            notification_type = NotificationType(type_param)
        except ValueError:
            valid_types = [t.value for t in NotificationType]
            raise ValidationError(
                f"Invalid type: {type_param}. Must be one of: {', '.join(valid_types)}"
            )

    # Get notifications
    notifications, meta = NotificationService.get_user_notifications(
        user_id=user.id,
        page=page,
        per_page=per_page,
        status=status,
        notification_type=notification_type,
    )

    return success_response(
        data=notification_list_schema.dump(notifications),
        message="Notifications retrieved successfully",
        meta=meta,
    )


# =============================================================================
# GET UNREAD COUNT
# =============================================================================


@bp.route("/unread-count", methods=["GET"])
@requires_auth
def get_unread_count():
    """
    Get count of unread notifications.

    Returns:
        200: Unread count

    Example Response:
        {
            "success": true,
            "data": {
                "unread_count": 5
            },
            "message": "Unread count retrieved successfully"
        }
    """
    # Sync user from JWT claims
    user = sync_user_from_claims(g.jwt_claims)

    count = NotificationService.get_unread_count(user.id)

    return success_response(
        data={"unread_count": count},
        message="Unread count retrieved successfully",
    )


# =============================================================================
# MARK NOTIFICATION AS READ
# =============================================================================


@bp.route("/<notification_id>/read", methods=["PATCH"])
@requires_auth
def mark_as_read(notification_id: str):
    """
    Mark a specific notification as read.

    Path Parameters:
        notification_id: Notification UUID

    Returns:
        200: Updated notification
        400: Invalid UUID format
        403: Notification doesn't belong to user
        404: Notification not found

    Example Response:
        {
            "success": true,
            "data": {
                "id": "uuid",
                "status": "read",
                ...
            },
            "message": "Notification marked as read"
        }
    """
    # Sync user from JWT claims
    user = sync_user_from_claims(g.jwt_claims)

    # Parse and validate UUID
    uuid_obj = parse_uuid(notification_id, "notification_id")

    # Mark as read
    notification = NotificationService.mark_as_read(user.id, uuid_obj)

    return success_response(
        data=notification_schema.dump(notification),
        message="Notification marked as read",
    )


# =============================================================================
# MARK ALL AS READ
# =============================================================================


@bp.route("/read-all", methods=["PATCH"])
@requires_auth
def mark_all_as_read():
    """
    Mark all unread notifications as read.

    Returns:
        200: Count of notifications marked as read

    Example Response:
        {
            "success": true,
            "data": {
                "marked_count": 10
            },
            "message": "All notifications marked as read"
        }
    """
    # Sync user from JWT claims
    user = sync_user_from_claims(g.jwt_claims)

    count = NotificationService.mark_all_as_read(user.id)

    return success_response(
        data={"marked_count": count},
        message="All notifications marked as read",
    )


# =============================================================================
# DELETE NOTIFICATION
# =============================================================================


@bp.route("/<notification_id>", methods=["DELETE"])
@requires_auth
def delete_notification(notification_id: str):
    """
    Delete a specific notification.

    Path Parameters:
        notification_id: Notification UUID

    Returns:
        200: Success message
        400: Invalid UUID format
        403: Notification doesn't belong to user
        404: Notification not found

    Example Response:
        {
            "success": true,
            "message": "Notification deleted successfully"
        }
    """
    # Sync user from JWT claims
    user = sync_user_from_claims(g.jwt_claims)

    # Parse and validate UUID
    uuid_obj = parse_uuid(notification_id, "notification_id")

    # Delete notification
    NotificationService.delete(user.id, uuid_obj)

    return success_response(
        message="Notification deleted successfully",
    )


# =============================================================================
# DELETE ALL READ NOTIFICATIONS
# =============================================================================


@bp.route("/read", methods=["DELETE"])
@requires_auth
def delete_all_read():
    """
    Delete all read notifications.

    Returns:
        200: Count of notifications deleted

    Example Response:
        {
            "success": true,
            "data": {
                "deleted_count": 25
            },
            "message": "Read notifications deleted successfully"
        }
    """
    # Sync user from JWT claims
    user = sync_user_from_claims(g.jwt_claims)

    count = NotificationService.delete_all_read(user.id)

    return success_response(
        data={"deleted_count": count},
        message="Read notifications deleted successfully",
    )
