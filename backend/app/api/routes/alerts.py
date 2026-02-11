# =============================================================================
# Digital Finance Tracker - Alert Routes
# PURPOSE: API endpoints for financial anomaly alerts
# =============================================================================
"""
Alert Routes Blueprint (Foundation)

This module provides API endpoints for Alert operations:
- GET /api/alerts - List user's alerts (paginated)
- GET /api/alerts/count - Get active alert count
- PATCH /api/alerts/:id/dismiss - Dismiss single alert
- PATCH /api/alerts/dismiss-all - Dismiss all alerts

AI Foundation:
    Foundation endpoints for alert management. Alerts are currently
    created manually or via service layer. Automatic alert generation
    (anomaly detection) will be added with AI integration.

All routes require authentication via @requires_auth decorator.

Usage:
    GET /api/alerts?page=1&per_page=20&include_dismissed=false
    GET /api/alerts/count
    PATCH /api/alerts/123e4567-e89b-12d3-a456-426614174000/dismiss
    PATCH /api/alerts/dismiss-all
"""

import logging

from flask import Blueprint, request, g

from app.auth.decorators import requires_auth
from app.auth.user_sync import sync_user_from_claims
from app.schemas.alert_schema import (
    alert_schema,
    alert_list_schema,
)
from app.services.alert_service import AlertService
from app.models.enums import AlertType, AlertSeverity
from app.utils.errors import BadRequestError
from app.utils.helpers import success_response, parse_uuid

# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# BLUEPRINT CONFIGURATION
# =============================================================================

alerts_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")


# =============================================================================
# ALERT ENDPOINTS
# =============================================================================


@alerts_bp.route("", methods=["GET"])
@requires_auth
def get_alerts():
    """
    Get paginated list of user's alerts.

    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 20, max: 100)
        include_dismissed (bool): Include dismissed alerts (default: false)
        type (str): Filter by alert type (optional)
        severity (str): Filter by severity (optional)

    Returns:
        {
            "success": true,
            "data": [...],
            "meta": {
                "page": 1,
                "per_page": 20,
                "total": 5,
                "total_pages": 1
            }
        }

    Requires:
        Authentication via Auth0
    """
    user = sync_user_from_claims(g.current_user, g.access_token)

    # Parse query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    include_dismissed = request.args.get("include_dismissed", "false").lower() == "true"

    # Parse optional type filter
    alert_type = None
    type_param = request.args.get("type")
    if type_param:
        try:
            alert_type = AlertType(type_param)
        except ValueError:
            valid_types = [t.value for t in AlertType]
            raise BadRequestError(f"Invalid alert type. Valid types: {valid_types}")

    # Parse optional severity filter
    severity = None
    severity_param = request.args.get("severity")
    if severity_param:
        try:
            severity = AlertSeverity(severity_param)
        except ValueError:
            valid_severities = [s.value for s in AlertSeverity]
            raise BadRequestError(f"Invalid severity. Valid values: {valid_severities}")

    # Get alerts
    alerts, meta = AlertService.get_user_alerts(
        user_id=user.id,
        page=page,
        per_page=per_page,
        include_dismissed=include_dismissed,
        alert_type=alert_type,
        severity=severity,
    )

    logger.info(f"User {user.id} retrieved {len(alerts)} alerts")

    return success_response(
        data=alert_list_schema.dump(alerts),
        message="Alerts retrieved successfully",
        meta=meta,
    )


@alerts_bp.route("/count", methods=["GET"])
@requires_auth
def get_alert_count():
    """
    Get count of active (undismissed) alerts.

    Returns:
        {
            "success": true,
            "data": {
                "active_count": 5
            }
        }

    Requires:
        Authentication via Auth0

    Notes:
        Useful for showing badge count in UI.
    """
    user = sync_user_from_claims(g.current_user, g.access_token)

    count = AlertService.get_active_count(user.id)

    logger.debug(f"User {user.id} has {count} active alerts")

    return success_response(
        data={"active_count": count},
        message="Active alert count retrieved successfully",
    )


@alerts_bp.route("/<alert_id>/dismiss", methods=["PATCH"])
@requires_auth
def dismiss_alert(alert_id: str):
    """
    Dismiss a specific alert.

    Path Parameters:
        alert_id (str): Alert UUID

    Returns:
        {
            "success": true,
            "data": { ... alert ... },
            "message": "Alert dismissed"
        }

    Requires:
        Authentication via Auth0
        User must own the alert

    Raises:
        400: Invalid UUID format
        403: Alert doesn't belong to user
        404: Alert not found
    """
    user = sync_user_from_claims(g.current_user, g.access_token)

    # Parse and validate UUID
    alert_uuid = parse_uuid(alert_id, "alert_id")

    # Dismiss the alert
    alert = AlertService.dismiss(user.id, alert_uuid)

    logger.info(f"User {user.id} dismissed alert {alert_id}")

    return success_response(
        data=alert_schema.dump(alert),
        message="Alert dismissed",
    )


@alerts_bp.route("/dismiss-all", methods=["PATCH"])
@requires_auth
def dismiss_all_alerts():
    """
    Dismiss all active alerts for the user.

    Returns:
        {
            "success": true,
            "data": {
                "dismissed_count": 5
            },
            "message": "5 alerts dismissed"
        }

    Requires:
        Authentication via Auth0
    """
    user = sync_user_from_claims(g.current_user, g.access_token)

    # Dismiss all alerts
    count = AlertService.dismiss_all(user.id)

    logger.info(f"User {user.id} dismissed {count} alerts")

    return success_response(
        data={"dismissed_count": count},
        message=f"{count} alert{'s' if count != 1 else ''} dismissed",
    )


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "alerts_bp",
]
