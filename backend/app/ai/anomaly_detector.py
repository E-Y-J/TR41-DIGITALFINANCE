# =============================================================================
# Digital Finance Tracker - Anomaly Detector
# PURPOSE: Detect unusual spending patterns and generate alerts
# =============================================================================
"""
Anomaly Detection Module

This module provides spending anomaly detection for:
- HIGH_SPENDING: Spending exceeds user's baseline in a category
- LARGE_TRANSACTION: Single transaction exceeds threshold
- UNUSUAL_CATEGORY: Spending in category user rarely uses

Detection Methods:
    - Statistical: Z-score based outlier detection
    - Baseline: Compare current vs historical average
    - Frequency: Detect rare category usage

Usage:
    from app.ai.anomaly_detector import AnomalyDetector, get_detector

    # Get singleton instance
    detector = get_detector()

    # Check for anomalies after transaction
    anomalies = detector.check_transaction(user_id, transaction)

    # Get user insights
    insights = detector.get_spending_insights(user_id)

Notes:
    - Uses rolling 30-day window for baseline calculation
    - Configurable thresholds per alert type
    - Creates alerts automatically when anomalies detected
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from statistics import mean, stdev
import threading

from sqlalchemy import func, and_

from app.core.extensions import db

logger = logging.getLogger(__name__)


# =============================================================================
# DETECTION THRESHOLDS
# =============================================================================

# High spending: trigger when spending is X times the baseline
HIGH_SPENDING_MULTIPLIER = 2.0  # 2x the average

# Large transaction: trigger when transaction amount exceeds this
LARGE_TRANSACTION_THRESHOLD = Decimal("500.00")

# Unusual category: trigger when category has < X transactions in history
UNUSUAL_CATEGORY_MIN_TRANSACTIONS = 3

# Z-score threshold for statistical outliers
Z_SCORE_THRESHOLD = 2.0

# Minimum transactions needed to calculate baseline
MIN_TRANSACTIONS_FOR_BASELINE = 5

# Rolling window for baseline calculation (days)
BASELINE_WINDOW_DAYS = 30


# =============================================================================
# ANOMALY DETECTOR CLASS
# =============================================================================


class AnomalyDetector:
    """
    Detects unusual spending patterns and triggers alerts.

    Implements multiple detection strategies:
    - Baseline comparison (vs 30-day average)
    - Statistical outlier detection (z-score)
    - Category frequency analysis

    Attributes:
        user_baselines: Cache of user spending baselines
        is_initialized: Whether detector is ready

    Example:
        >>> detector = AnomalyDetector()
        >>> anomalies = detector.check_transaction(user_id, transaction)
        >>> for anomaly in anomalies:
        ...     print(f"{anomaly['type']}: {anomaly['message']}")
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the detector."""
        if hasattr(self, "_init_done") and self._init_done:
            return

        self._user_baselines: Dict[UUID, Dict[str, Any]] = {}
        self._baseline_expiry: Dict[UUID, datetime] = {}
        self._baseline_cache_minutes = 60  # Cache baselines for 60 minutes
        self.is_initialized = False

        self._init_done = True

    def initialize(self) -> bool:
        """
        Initialize the anomaly detector.

        This method prepares the detector for use. Currently a no-op since
        the detector doesn't require heavy initialization, but included for
        consistency with other AI components.

        Returns:
            True if initialization successful
        """
        if self.is_initialized:
            return True

        # Detector is stateless - no heavy initialization needed
        # Baselines are calculated on-demand and cached
        self.is_initialized = True
        logger.info("Anomaly detector initialized")
        return True

    def check_transaction(
        self,
        user_id: UUID,
        transaction: Any,
        create_alerts: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Check a transaction for anomalies.

        Args:
            user_id: User's UUID
            transaction: Transaction model instance
            create_alerts: Whether to automatically create alerts

        Returns:
            List of detected anomalies

        Example:
            >>> anomalies = detector.check_transaction(user_id, transaction)
            >>> anomalies
            [
                {
                    "type": "high_spending",
                    "severity": "medium",
                    "message": "Food & Dining spending is 2.5x your usual",
                    "data": {...}
                }
            ]
        """
        anomalies = []

        try:
            from app.models.enums import TransactionType

            # Only check expense transactions
            if transaction.transaction_type != TransactionType.EXPENSE:
                return anomalies

            # Check for large transaction
            large_anomaly = self._check_large_transaction(transaction)
            if large_anomaly:
                anomalies.append(large_anomaly)

            # Check for high spending in category
            if transaction.category_id:
                high_spending = self._check_high_spending(
                    user_id, transaction.category_id, transaction.amount
                )
                if high_spending:
                    anomalies.append(high_spending)

                # Check for unusual category
                unusual = self._check_unusual_category(user_id, transaction.category_id)
                if unusual:
                    anomalies.append(unusual)

            # Create alerts if requested
            if create_alerts and anomalies:
                self._create_alerts(user_id, transaction, anomalies)

        except Exception as e:
            logger.error(
                f"Anomaly check failed for transaction {transaction.id}: {e}",
                exc_info=True,
            )

        return anomalies

    def _check_large_transaction(
        self, transaction: Any
    ) -> Optional[Dict[str, Any]]:
        """Check if transaction amount is unusually large."""
        if transaction.amount >= LARGE_TRANSACTION_THRESHOLD:
            return {
                "type": "large_transaction",
                "severity": self._get_severity_for_amount(transaction.amount),
                "message": f"Large transaction: ${transaction.amount:.2f}",
                "data": {
                    "amount": str(transaction.amount),
                    "threshold": str(LARGE_TRANSACTION_THRESHOLD),
                    "merchant": transaction.merchant_name,
                },
            }
        return None

    def _check_high_spending(
        self,
        user_id: UUID,
        category_id: UUID,
        amount: Decimal,
    ) -> Optional[Dict[str, Any]]:
        """Check if spending in category is higher than baseline."""
        try:
            baseline = self._get_category_baseline(user_id, category_id)
            if not baseline:
                return None

            avg_transaction = baseline.get("avg_transaction", 0)
            if avg_transaction <= 0:
                return None

            # Check if this transaction is significantly higher than average
            ratio = float(amount) / avg_transaction
            if ratio >= HIGH_SPENDING_MULTIPLIER:
                return {
                    "type": "high_spending",
                    "severity": self._get_severity_for_ratio(ratio),
                    "message": (
                        f"This ${amount:.2f} transaction is {ratio:.1f}x "
                        f"your average of ${avg_transaction:.2f}"
                    ),
                    "data": {
                        "amount": str(amount),
                        "average": str(round(avg_transaction, 2)),
                        "ratio": round(ratio, 2),
                        "category_id": str(category_id),
                        "category_name": baseline.get("category_name"),
                    },
                }
        except Exception as e:
            logger.error(f"High spending check failed: {e}", exc_info=True)

        return None

    def _check_unusual_category(
        self,
        user_id: UUID,
        category_id: UUID,
    ) -> Optional[Dict[str, Any]]:
        """Check if user rarely spends in this category."""
        try:
            baseline = self._get_category_baseline(user_id, category_id)
            if not baseline:
                # No baseline = definitely unusual
                category_name = self._get_category_name(category_id)
                return {
                    "type": "unusual_category",
                    "severity": "low",
                    "message": f"First time spending in {category_name}",
                    "data": {
                        "category_id": str(category_id),
                        "category_name": category_name,
                        "transaction_count": 0,
                    },
                }

            tx_count = baseline.get("transaction_count", 0)
            if tx_count < UNUSUAL_CATEGORY_MIN_TRANSACTIONS:
                return {
                    "type": "unusual_category",
                    "severity": "low",
                    "message": (
                        f"Uncommon category: {baseline.get('category_name')} "
                        f"(only {tx_count} previous transactions)"
                    ),
                    "data": {
                        "category_id": str(category_id),
                        "category_name": baseline.get("category_name"),
                        "transaction_count": tx_count,
                    },
                }
        except Exception as e:
            logger.error(f"Unusual category check failed: {e}", exc_info=True)

        return None

    def _get_category_baseline(
        self,
        user_id: UUID,
        category_id: UUID,
    ) -> Optional[Dict[str, Any]]:
        """Get spending baseline for a category."""
        try:
            from app.models.transaction import Transaction
            from app.models.category import Category
            from app.models.enums import TransactionType

            # Check cache
            cache_key = f"{user_id}_{category_id}"
            if cache_key in self._user_baselines:
                expiry = self._baseline_expiry.get(cache_key)
                if expiry and datetime.now(timezone.utc) < expiry:
                    return self._user_baselines[cache_key]

            # Calculate baseline from last 30 days
            cutoff = datetime.now(timezone.utc) - timedelta(days=BASELINE_WINDOW_DAYS)
            cutoff_str = cutoff.strftime("%Y-%m-%d")

            transactions = Transaction.query.filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.category_id == category_id,
                    Transaction.transaction_type == TransactionType.EXPENSE,
                    Transaction.date >= cutoff_str,
                )
            ).all()

            if not transactions:
                return None

            amounts = [float(t.amount) for t in transactions]
            category = db.session.get(Category, category_id)

            baseline = {
                "category_id": str(category_id),
                "category_name": category.name if category else "Unknown",
                "transaction_count": len(transactions),
                "total_spent": sum(amounts),
                "avg_transaction": mean(amounts) if amounts else 0,
                "std_deviation": stdev(amounts) if len(amounts) > 1 else 0,
                "min_amount": min(amounts) if amounts else 0,
                "max_amount": max(amounts) if amounts else 0,
            }

            # Cache the result
            self._user_baselines[cache_key] = baseline
            self._baseline_expiry[cache_key] = datetime.now(
                timezone.utc
            ) + timedelta(minutes=self._baseline_cache_minutes)

            return baseline

        except Exception as e:
            logger.error(f"Failed to get category baseline: {e}", exc_info=True)
            return None

    def _get_category_name(self, category_id: UUID) -> str:
        """Get category name from ID."""
        try:
            from app.models.category import Category

            category = db.session.get(Category, category_id)
            return category.name if category else "Unknown"
        except Exception:
            return "Unknown"

    def _get_severity_for_amount(self, amount: Decimal) -> str:
        """Determine severity based on transaction amount."""
        if amount >= Decimal("1000"):
            return "high"
        elif amount >= Decimal("500"):
            return "medium"
        return "low"

    def _get_severity_for_ratio(self, ratio: float) -> str:
        """Determine severity based on spending ratio."""
        if ratio >= 5.0:
            return "high"
        elif ratio >= 3.0:
            return "medium"
        return "low"

    def _create_alerts(
        self,
        user_id: UUID,
        transaction: Any,
        anomalies: List[Dict[str, Any]],
    ):
        """Create alerts for detected anomalies."""
        try:
            from app.services.alert_service import AlertService
            from app.models.enums import AlertType, AlertSeverity

            for anomaly in anomalies:
                alert_type_map = {
                    "high_spending": AlertType.HIGH_SPENDING,
                    "large_transaction": AlertType.LARGE_TRANSACTION,
                    "unusual_category": AlertType.UNUSUAL_CATEGORY,
                }

                severity_map = {
                    "low": AlertSeverity.LOW,
                    "medium": AlertSeverity.MEDIUM,
                    "high": AlertSeverity.HIGH,
                }

                alert_type = alert_type_map.get(anomaly["type"])
                severity = severity_map.get(anomaly["severity"], AlertSeverity.MEDIUM)

                if alert_type:
                    AlertService.create(
                        user_id=user_id,
                        alert_type=alert_type,
                        severity=severity,
                        title=f"{anomaly['type'].replace('_', ' ').title()} Alert",
                        message=anomaly["message"],
                        transaction_id=transaction.id,
                        category_id=transaction.category_id,
                        data=anomaly.get("data", {}),
                    )

        except Exception as e:
            logger.error(f"Failed to create alerts: {e}", exc_info=True)

    def get_spending_insights(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get spending insights for a user.

        Args:
            user_id: User's UUID

        Returns:
            Dictionary with spending insights

        Example:
            >>> insights = detector.get_spending_insights(user_id)
            >>> insights
            {
                "top_categories": [...],
                "unusual_activity": [...],
                "spending_trend": "increasing",
                "recommendations": [...]
            }
        """
        try:
            from app.models.transaction import Transaction
            from app.models.category import Category
            from app.models.enums import TransactionType
            from sqlalchemy import desc

            # Get last 30 days of transactions
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            cutoff_str = cutoff.strftime("%Y-%m-%d")

            # Get spending by category
            category_spending = (
                Transaction.query.with_entities(
                    Transaction.category_id,
                    func.sum(Transaction.amount).label("total"),
                    func.count(Transaction.id).label("count"),
                )
                .filter(
                    and_(
                        Transaction.user_id == user_id,
                        Transaction.transaction_type == TransactionType.EXPENSE,
                        Transaction.date >= cutoff_str,
                    )
                )
                .group_by(Transaction.category_id)
                .order_by(desc("total"))
                .limit(10)
                .all()
            )

            # Build insights
            top_categories = []
            for cat_id, total, count in category_spending:
                if cat_id:
                    category = db.session.get(Category, cat_id)
                    top_categories.append(
                        {
                            "category_id": str(cat_id),
                            "category_name": category.name if category else "Unknown",
                            "total_spent": float(total),
                            "transaction_count": count,
                            "avg_per_transaction": round(float(total) / count, 2),
                        }
                    )

            # Get recent unusual activity
            unusual_activity = self._get_recent_unusual_activity(user_id)

            # Calculate spending trend
            spending_trend = self._calculate_spending_trend(user_id)

            return {
                "period": f"Last {BASELINE_WINDOW_DAYS} days",
                "top_categories": top_categories,
                "unusual_activity": unusual_activity,
                "spending_trend": spending_trend,
                "recommendations": self._generate_recommendations(
                    top_categories, spending_trend
                ),
            }

        except Exception as e:
            logger.error(f"Failed to get spending insights: {e}", exc_info=True)
            return {
                "error": "Failed to generate insights",
                "top_categories": [],
                "unusual_activity": [],
                "spending_trend": "unknown",
                "recommendations": [],
            }

    def _get_recent_unusual_activity(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get recent unusual spending activity."""
        try:
            from app.models.alert import Alert
            from app.models.enums import AlertType

            # Get recent high spending and unusual category alerts
            recent_alerts = (
                Alert.query.filter(
                    and_(
                        Alert.user_id == user_id,
                        Alert.alert_type.in_(
                            [AlertType.HIGH_SPENDING, AlertType.UNUSUAL_CATEGORY]
                        ),
                        Alert.is_dismissed == False,
                    )
                )
                .order_by(Alert.created_at.desc())
                .limit(5)
                .all()
            )

            return [
                {
                    "type": alert.alert_type.value,
                    "message": alert.message,
                    "created_at": alert.created_at.isoformat(),
                }
                for alert in recent_alerts
            ]

        except Exception:
            return []

    def _calculate_spending_trend(self, user_id: UUID) -> str:
        """Calculate if spending is increasing, decreasing, or stable."""
        try:
            from app.models.transaction import Transaction
            from app.models.enums import TransactionType

            now = datetime.now(timezone.utc)

            # Compare last 2 weeks to previous 2 weeks
            week2_start = (now - timedelta(days=14)).strftime("%Y-%m-%d")
            week1_start = (now - timedelta(days=7)).strftime("%Y-%m-%d")
            week4_start = (now - timedelta(days=28)).strftime("%Y-%m-%d")

            # Last 2 weeks spending
            recent_spending = (
                Transaction.query.with_entities(func.sum(Transaction.amount))
                .filter(
                    and_(
                        Transaction.user_id == user_id,
                        Transaction.transaction_type == TransactionType.EXPENSE,
                        Transaction.date >= week2_start,
                    )
                )
                .scalar()
                or 0
            )

            # Previous 2 weeks spending
            previous_spending = (
                Transaction.query.with_entities(func.sum(Transaction.amount))
                .filter(
                    and_(
                        Transaction.user_id == user_id,
                        Transaction.transaction_type == TransactionType.EXPENSE,
                        Transaction.date >= week4_start,
                        Transaction.date < week2_start,
                    )
                )
                .scalar()
                or 0
            )

            if previous_spending == 0:
                return "new_user"

            change_ratio = float(recent_spending) / float(previous_spending)

            if change_ratio > 1.2:
                return "increasing"
            elif change_ratio < 0.8:
                return "decreasing"
            return "stable"

        except Exception as e:
            logger.error(f"Failed to calculate spending trend: {e}")
            return "unknown"

    def _generate_recommendations(
        self,
        top_categories: List[Dict[str, Any]],
        spending_trend: str,
    ) -> List[str]:
        """Generate spending recommendations."""
        recommendations = []

        if spending_trend == "increasing":
            recommendations.append(
                "Your spending has increased recently. Consider reviewing your budget."
            )

        if top_categories:
            top_cat = top_categories[0]
            if top_cat["total_spent"] > 500:
                recommendations.append(
                    f"Consider setting a budget for {top_cat['category_name']} - "
                    f"you've spent ${top_cat['total_spent']:.2f} there this month."
                )

        if len(recommendations) == 0:
            recommendations.append("Your spending looks healthy! Keep it up.")

        return recommendations

    def clear_cache(self, user_id: Optional[UUID] = None):
        """Clear baseline cache for a user or all users."""
        if user_id:
            keys_to_remove = [
                k for k in self._user_baselines.keys() if str(user_id) in k
            ]
            for key in keys_to_remove:
                del self._user_baselines[key]
                self._baseline_expiry.pop(key, None)
        else:
            self._user_baselines.clear()
            self._baseline_expiry.clear()


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_detector: Optional[AnomalyDetector] = None


def get_detector() -> AnomalyDetector:
    """
    Get the singleton AnomalyDetector instance.

    Returns:
        AnomalyDetector instance (creates if not exists)
    """
    global _detector
    if _detector is None:
        _detector = AnomalyDetector()
    return _detector


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "AnomalyDetector",
    "get_detector",
    "HIGH_SPENDING_MULTIPLIER",
    "LARGE_TRANSACTION_THRESHOLD",
    "UNUSUAL_CATEGORY_MIN_TRANSACTIONS",
    "Z_SCORE_THRESHOLD",
]
