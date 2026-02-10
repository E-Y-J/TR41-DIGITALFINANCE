# =============================================================================
# Digital Finance Tracker - Alert Schema
# PURPOSE: Marshmallow schemas for Alert serialization
# =============================================================================
"""
Alert Schema Module (Foundation)

This module provides Marshmallow schemas for Alert serialization:
- AlertSchema: Full alert serialization
- AlertResponseSchema: API response wrapper
- AlertListResponseSchema: Paginated list response

Foundation for anomaly detection alerts.
Schemas ready; detection logic will be added with AI integration.

Usage:
    from app.schemas.alert_schema import alert_schema, alert_list_schema

    # Serialize single alert
    data = alert_schema.dump(alert)

    # Serialize list of alerts
    data = alert_list_schema.dump(alerts)
"""

from marshmallow import fields, validate

from app.schemas.base import BaseSchema
from app.models.enums import AlertType, AlertSeverity

# =============================================================================
# ALERT SCHEMAS
# =============================================================================


class AlertSchema(BaseSchema):
    """
    Schema for Alert model serialization.

    Handles conversion between Alert model and JSON.

    Fields:
        id: Alert UUID
        user_id: Owner's UUID
        alert_type: Type of alert
        severity: Alert severity level
        title: Short title
        message: Detailed message
        is_dismissed: Whether dismissed
        dismissed_at: When dismissed
        transaction_id: Related transaction (optional)
        category_id: Related category (optional)
        data: Extra metadata
        created_at: Creation timestamp
    """

    id = fields.UUID(dump_only=True)
    user_id = fields.UUID(dump_only=True)

    alert_type = fields.Method(
        "get_alert_type",
        dump_only=True,
        metadata={"description": "Type of alert"},
    )

    def get_alert_type(self, obj):
        """Extract enum value as string."""
        if hasattr(obj.alert_type, "value"):
            return obj.alert_type.value
        return str(obj.alert_type) if obj.alert_type else None

    severity = fields.Method(
        "get_severity",
        dump_only=True,
        metadata={"description": "Alert severity level"},
    )

    def get_severity(self, obj):
        """Extract enum value as string."""
        if hasattr(obj.severity, "value"):
            return obj.severity.value
        return str(obj.severity) if obj.severity else None

    title = fields.String(
        dump_only=True,
        metadata={"description": "Short alert title"},
    )
    message = fields.String(
        dump_only=True,
        metadata={"description": "Detailed alert message"},
    )

    is_dismissed = fields.Boolean(
        dump_only=True,
        metadata={"description": "Whether alert has been dismissed"},
    )
    dismissed_at = fields.DateTime(
        dump_only=True,
        allow_none=True,
        metadata={"description": "When alert was dismissed"},
    )

    transaction_id = fields.UUID(
        dump_only=True,
        allow_none=True,
        metadata={"description": "Related transaction UUID"},
    )
    category_id = fields.UUID(
        dump_only=True,
        allow_none=True,
        metadata={"description": "Related category UUID"},
    )

    data = fields.Dict(
        dump_only=True,
        metadata={"description": "Additional alert data"},
    )

    created_at = fields.DateTime(
        dump_only=True,
        metadata={"description": "When alert was created"},
    )

    # Optional: Include related objects
    category = fields.Nested(
        "CategorySchema",
        dump_only=True,
        attribute="category_rel",
        metadata={"description": "Related category details"},
    )

    class Meta:
        """Schema metadata."""

        pass


class AlertDismissSchema(BaseSchema):
    """
    Schema for dismissing an alert.

    Used for PATCH /alerts/:id/dismiss request validation.
    Currently no fields needed - just marks as dismissed.
    Could add 'reason' field in future if needed.
    """

    reason = fields.String(
        load_only=True,
        required=False,
        allow_none=True,
        validate=validate.Length(max=500),
        metadata={"description": "Optional reason for dismissing"},
    )


class AlertCreateSchema(BaseSchema):
    """
    Schema for creating an alert (internal use).

    Used by services to create alerts programmatically.
    Not exposed via API - alerts are created by the system.

    Example:
        >>> data = alert_create_schema.load({
        ...     "alert_type": "high_spending",
        ...     "severity": "medium",
        ...     "title": "High Spending Alert",
        ...     "message": "You spent 2x your usual amount in Food & Dining"
        ... })
    """

    alert_type = fields.String(
        required=True,
        validate=validate.OneOf([t.value for t in AlertType]),
        metadata={"description": "Alert type"},
    )
    severity = fields.String(
        required=False,
        validate=validate.OneOf([s.value for s in AlertSeverity]),
        load_default="medium",
        metadata={"description": "Alert severity"},
    )
    title = fields.String(
        required=True,
        validate=validate.Length(min=1, max=255),
        metadata={"description": "Alert title"},
    )
    message = fields.String(
        required=True,
        validate=validate.Length(min=1, max=2000),
        metadata={"description": "Alert message"},
    )
    transaction_id = fields.UUID(
        required=False,
        allow_none=True,
        metadata={"description": "Related transaction UUID"},
    )
    category_id = fields.UUID(
        required=False,
        allow_none=True,
        metadata={"description": "Related category UUID"},
    )
    data = fields.Dict(
        required=False,
        load_default=dict,
        metadata={"description": "Additional data"},
    )


# =============================================================================
# RESPONSE WRAPPER SCHEMAS
# =============================================================================


class AlertResponseSchema(BaseSchema):
    """Standard API response wrapper for single alert."""

    success = fields.Boolean(dump_default=True)
    message = fields.String()
    data = fields.Nested(AlertSchema)


class AlertListResponseSchema(BaseSchema):
    """Standard API response wrapper for alert list."""

    success = fields.Boolean(dump_default=True)
    message = fields.String()
    data = fields.List(fields.Nested(AlertSchema))
    meta = fields.Dict(metadata={"description": "Pagination metadata"})


# =============================================================================
# SCHEMA INSTANCES
# =============================================================================

# Reusable schema instances
alert_schema = AlertSchema()
alert_list_schema = AlertSchema(many=True)
alert_dismiss_schema = AlertDismissSchema()
alert_create_schema = AlertCreateSchema()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "AlertSchema",
    "AlertDismissSchema",
    "AlertCreateSchema",
    "AlertResponseSchema",
    "AlertListResponseSchema",
    "alert_schema",
    "alert_list_schema",
    "alert_dismiss_schema",
    "alert_create_schema",
]
