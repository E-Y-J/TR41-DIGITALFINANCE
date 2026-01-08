# =============================================================================
# Digital Finance Tracker - Notification Schemas
# PURPOSE: Marshmallow schemas for Notification validation and serialization
# =============================================================================
"""
Notification Schema Module

This module provides Marshmallow schemas for Notification data:
- Serialization of Notification objects for API responses
- Validation for status update requests

Supports notification API endpoints for frontend team.

Usage:
    from app.schemas.notification_schema import (
        NotificationSchema,
        notification_schema,
        notification_list_schema
    )

    # Serialize single notification
    data = notification_schema.dump(notification)

    # Serialize list of notifications
    data = notification_list_schema.dump(notifications)

Schema Types:
    - NotificationSchema: Full notification data (for responses)
    - NotificationListResponseSchema: For paginated list responses
"""

from marshmallow import fields, validate

from app.schemas.base import BaseSchema


# =============================================================================
# NOTIFICATION SCHEMA (FULL)
# =============================================================================


class NotificationSchema(BaseSchema):
    """
    Full notification schema for API responses.

    Used when returning notification data to frontend.

    Example Response:
        {
            "id": "uuid-string",
            "type": "new_transaction",
            "status": "unread",
            "message": "New transaction: -$50.00 at Starbucks",
            "metadata": {"transaction_id": "txn-uuid"},
            "created_at": "2026-01-06T10:30:00Z"
        }
    """

    # Identity fields
    id = fields.UUID(dump_only=True, metadata={"description": "Notification ID"})

    user_id = fields.UUID(dump_only=True, metadata={"description": "User ID (owner)"})

    # Notification fields
    type = fields.String(
        dump_only=True,
        metadata={
            "description": "Notification type",
            "enum": [
                "default",
                "new_transaction",
                "deleted_transaction",
                "edited_profile",
                "weekly_summary_ready",
                "category_updated",
            ],
        },
    )

    status = fields.String(
        dump_only=True,
        metadata={"description": "Notification status: unread or read"},
    )

    message = fields.String(
        dump_only=True,
        metadata={"description": "Notification message"},
    )

    data = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        dump_only=True,
        metadata={"description": "Extra notification context"},
    )

    # Timestamps
    created_at = fields.DateTime(
        dump_only=True,
        format="iso",
        metadata={"description": "Notification creation date"},
    )


# =============================================================================
# NOTIFICATION UPDATE SCHEMA
# =============================================================================


class NotificationStatusUpdateSchema(BaseSchema):
    """
    Schema for updating notification status.

    Used when marking notifications as read.

    Example Request:
        {
            "status": "read"
        }
    """

    status = fields.String(
        required=True,
        validate=validate.OneOf(["read", "unread"]),
        metadata={"description": "New status: read or unread"},
    )


# =============================================================================
# NOTIFICATION RESPONSE SCHEMAS
# =============================================================================


class NotificationResponseSchema(BaseSchema):
    """
    Schema for single notification API responses.

    Example:
        {
            "success": true,
            "data": {...notification...},
            "message": "Notification retrieved"
        }
    """

    success = fields.Boolean(dump_only=True)
    message = fields.String(dump_only=True)
    data = fields.Nested(NotificationSchema, dump_only=True)


class NotificationListResponseSchema(BaseSchema):
    """
    Schema for notification list API responses with pagination.

    Example:
        {
            "success": true,
            "data": [...notifications...],
            "meta": {
                "page": 1,
                "per_page": 20,
                "total": 50,
                "total_pages": 3,
                "unread_count": 10
            },
            "message": "Notifications retrieved"
        }
    """

    success = fields.Boolean(dump_only=True)
    message = fields.String(dump_only=True)
    data = fields.List(fields.Nested(NotificationSchema), dump_only=True)
    meta = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        dump_only=True,
        metadata={"description": "Pagination metadata including unread_count"},
    )


# =============================================================================
# SCHEMA INSTANCES
# =============================================================================

# Singleton instances for reuse
notification_schema = NotificationSchema()
notification_list_schema = NotificationSchema(many=True)
notification_status_update_schema = NotificationStatusUpdateSchema()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Schema classes
    "NotificationSchema",
    "NotificationStatusUpdateSchema",
    "NotificationResponseSchema",
    "NotificationListResponseSchema",
    # Schema instances
    "notification_schema",
    "notification_list_schema",
    "notification_status_update_schema",
]
