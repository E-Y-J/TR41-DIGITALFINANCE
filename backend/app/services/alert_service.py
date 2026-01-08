# =============================================================================
# Digital Finance Tracker - Alert Service
# PURPOSE: Alert service layer for financial anomaly alerts
# =============================================================================
"""
Alert Service Module (Foundation)

This module provides the service layer for Alert operations:
- Create alerts (for system/AI use)
- Get user alerts with pagination
- Dismiss alerts (single or all)
- Get active alert count

Foundation for anomaly detection. The model and service are ready;
detection logic (calculating baselines, detecting anomalies) will be
added when AI is integrated.

CURRENT CAPABILITIES:
    - Store and retrieve alerts
    - Dismiss alerts
    - Count active alerts

FUTURE CAPABILITIES (when AI is added):
    - Detect high spending vs baseline
    - Detect large transactions
    - Detect unusual category patterns

Usage:
    from app.services.alert_service import AlertService

    # Create alert (typically called by detection system)
    alert = AlertService.create_high_spending_alert(
        user_id, category_id, amount, baseline
    )

    # Get user's active alerts
    alerts, meta = AlertService.get_user_alerts(user_id)

    # Dismiss alert
    AlertService.dismiss(user_id, alert_id)

Design Principles:
    - Stateless class methods for all operations
    - All database commits happen here (not in routes)
    - Pagination for list operations
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from uuid import UUID
from decimal import Decimal

from sqlalchemy import desc, not_

from app.core.extensions import db
from app.models.alert import Alert
from app.models.enums import AlertType, AlertSeverity
from app.utils.errors import NotFoundError, ForbiddenError, InternalError


# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# ALERT SERVICE CLASS
# =============================================================================


class AlertService:
    """
    Service class for Alert operations.

    All methods are class methods (no instance needed).
    Handles creation, reading, and dismissing of alerts.

    ALERT TYPES:
        - HIGH_SPENDING: Spending exceeds baseline in a category
        - LARGE_TRANSACTION: Single transaction exceeds threshold
        - UNUSUAL_CATEGORY: Spending in unusual category for user
        - BUDGET_WARNING: Approaching budget limit
        - BUDGET_EXCEEDED: Budget exceeded

    Example:
        >>> alert = AlertService.create(
        ...     user_id, AlertType.HIGH_SPENDING, AlertSeverity.MEDIUM,
        ...     "High Spending", "You spent 2x your usual amount"
        ... )
        >>> alerts, meta = AlertService.get_user_alerts(user_id)
    """

    # =========================================================================
    # CREATE OPERATIONS
    # =========================================================================

    @classmethod
    def create(
        cls,
        user_id: UUID,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        transaction_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Alert:
        """
        Create a new alert.

        Args:
            user_id: User's UUID
            alert_type: AlertType enum value
            severity: AlertSeverity enum value
            title: Short alert title
            message: Detailed alert message
            transaction_id: Optional related transaction UUID
            category_id: Optional related category UUID
            data: Optional metadata (baseline, threshold, etc.)

        Returns:
            Created Alert instance

        Example:
            >>> alert = AlertService.create(
            ...     user_id=user.id,
            ...     alert_type=AlertType.LARGE_TRANSACTION,
            ...     severity=AlertSeverity.MEDIUM,
            ...     title="Large Transaction",
            ...     message="$500 spent at Amazon",
            ...     transaction_id=transaction.id,
            ...     data={"amount": 500, "threshold": 200}
            ... )
        """
        try:
            alert = Alert(
                user_id=user_id,
                alert_type=alert_type,
                severity=severity,
                title=title,
                message=message,
                transaction_id=transaction_id,
                category_id=category_id,
                data=data or {},
            )

            db.session.add(alert)
            db.session.commit()

            logger.info(
                f"Created alert for user {user_id}: {alert_type.value} ({severity.value})"
            )
            return alert

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create alert: {e}", exc_info=True)
            raise InternalError("Failed to create alert")

    @classmethod
    def create_high_spending_alert(
        cls,
        user_id: UUID,
        category_id: UUID,
        category_name: str,
        current_amount: Decimal,
        baseline_amount: Decimal,
        multiplier: float = 2.0,
    ) -> Alert:
        """
        Create a high spending alert for a category.

        Used when user's spending in a category exceeds their baseline.

        Args:
            user_id: User's UUID
            category_id: Category UUID
            category_name: Category name for message
            current_amount: Current period spending
            baseline_amount: Baseline (average) spending
            multiplier: How many times over baseline (e.g., 2.0 = 2x)

        Returns:
            Created Alert instance

        Example:
            >>> alert = AlertService.create_high_spending_alert(
            ...     user.id, food_cat.id, "Food & Dining",
            ...     Decimal("500.00"), Decimal("200.00"), 2.5
            ... )
        """
        severity = AlertSeverity.MEDIUM
        if multiplier >= 3.0:
            severity = AlertSeverity.HIGH
        elif multiplier >= 5.0:
            severity = AlertSeverity.CRITICAL

        return cls.create(
            user_id=user_id,
            alert_type=AlertType.HIGH_SPENDING,
            severity=severity,
            title=f"High Spending: {category_name}",
            message=(
                f"Your spending in {category_name} is {multiplier:.1f}x your usual. "
                f"Current: ${float(current_amount):.2f}, Baseline: ${float(baseline_amount):.2f}"
            ),
            category_id=category_id,
            data={
                "current_amount": float(current_amount),
                "baseline_amount": float(baseline_amount),
                "multiplier": multiplier,
            },
        )

    @classmethod
    def create_large_transaction_alert(
        cls,
        user_id: UUID,
        transaction_id: UUID,
        amount: Decimal,
        merchant_name: str,
        threshold: Decimal,
    ) -> Alert:
        """
        Create a large transaction alert.

        Used when a single transaction exceeds user's threshold.

        Args:
            user_id: User's UUID
            transaction_id: Transaction UUID
            amount: Transaction amount
            merchant_name: Merchant name
            threshold: User's threshold setting

        Returns:
            Created Alert instance
        """
        severity = AlertSeverity.MEDIUM
        if float(amount) >= float(threshold) * 2:
            severity = AlertSeverity.HIGH
        if float(amount) >= float(threshold) * 5:
            severity = AlertSeverity.CRITICAL

        return cls.create(
            user_id=user_id,
            alert_type=AlertType.LARGE_TRANSACTION,
            severity=severity,
            title="Large Transaction Detected",
            message=(
                f"${float(amount):.2f} spent at {merchant_name or 'Unknown'} "
                f"exceeds your ${float(threshold):.2f} threshold"
            ),
            transaction_id=transaction_id,
            data={
                "amount": float(amount),
                "threshold": float(threshold),
                "merchant_name": merchant_name,
            },
        )

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    @classmethod
    def get_by_id(cls, alert_id: UUID) -> Alert:
        """
        Get alert by primary key ID.

        Args:
            alert_id: Alert's UUID primary key

        Returns:
            Alert instance

        Raises:
            NotFoundError: If alert not found
        """
        alert = Alert.query.get(alert_id)

        if alert is None:
            logger.debug(f"Alert not found by ID: {alert_id}")
            raise NotFoundError("Alert not found")

        return alert

    @classmethod
    def get_user_alert(cls, user_id: UUID, alert_id: UUID) -> Alert:
        """
        Get a specific alert belonging to a user.

        Args:
            user_id: User's UUID (owner)
            alert_id: Alert's UUID

        Returns:
            Alert instance

        Raises:
            NotFoundError: If alert not found
            ForbiddenError: If alert doesn't belong to user
        """
        alert = cls.get_by_id(alert_id)

        if alert.user_id != user_id:
            logger.warning(f"User {user_id} attempted to access alert {alert_id}")
            raise ForbiddenError("You don't have access to this alert")

        return alert

    @classmethod
    def get_user_alerts(
        cls,
        user_id: UUID,
        page: int = 1,
        per_page: int = 20,
        include_dismissed: bool = False,
        alert_type: Optional[AlertType] = None,
        severity: Optional[AlertSeverity] = None,
    ) -> Tuple[List[Alert], Dict[str, Any]]:
        """
        Get paginated list of user's alerts.

        Args:
            user_id: User's UUID
            page: Page number (1-indexed)
            per_page: Items per page (max 100)
            include_dismissed: Include dismissed alerts (default: False)
            alert_type: Filter by alert type
            severity: Filter by severity

        Returns:
            Tuple of (list of alerts, pagination metadata)

        Example:
            >>> alerts, meta = AlertService.get_user_alerts(
            ...     user_id,
            ...     page=1,
            ...     per_page=20,
            ...     include_dismissed=False
            ... )
        """
        per_page = min(per_page, 100)

        # Build query - ordered by newest first
        query = Alert.query.filter(Alert.user_id == user_id).order_by(
            desc(Alert.created_at)
        )

        # Filter dismissed
        if not include_dismissed:
            query = query.filter(not_(Alert.is_dismissed))

        # Apply filters
        if alert_type:
            query = query.filter(Alert.alert_type == alert_type)

        if severity:
            query = query.filter(Alert.severity == severity)

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

        logger.debug(f"Retrieved {len(pagination.items)} alerts for user {user_id}")
        return pagination.items, meta

    @classmethod
    def get_active_count(cls, user_id: UUID) -> int:
        """
        Get count of active (undismissed) alerts for a user.

        Args:
            user_id: User's UUID

        Returns:
            Number of active alerts
        """
        return Alert.get_active_count(user_id)

    # =========================================================================
    # UPDATE OPERATIONS
    # =========================================================================

    @classmethod
    def dismiss(cls, user_id: UUID, alert_id: UUID) -> Alert:
        """
        Dismiss a specific alert.

        Args:
            user_id: User's UUID (for ownership verification)
            alert_id: Alert's UUID

        Returns:
            Updated Alert instance

        Raises:
            NotFoundError: If alert not found
            ForbiddenError: If alert doesn't belong to user
        """
        alert = cls.get_user_alert(user_id, alert_id)
        alert.dismiss()
        db.session.commit()

        logger.info(f"Dismissed alert {alert_id} for user {user_id}")
        return alert

    @classmethod
    def dismiss_all(cls, user_id: UUID) -> int:
        """
        Dismiss all active alerts for a user.

        Args:
            user_id: User's UUID

        Returns:
            Number of alerts dismissed
        """
        count = Alert.dismiss_all(user_id)
        logger.info(f"Dismissed {count} alerts for user {user_id}")
        return count


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "AlertService",
]
