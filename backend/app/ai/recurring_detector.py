# =============================================================================
# Digital Finance Tracker - Recurring Transaction Detector
# PURPOSE: Detect subscription patterns, predict bills, alert on missed payments
# =============================================================================
"""
Recurring Transaction Detector Module

This module provides intelligent detection of recurring transactions:
1. DETECT: Identify subscription patterns (same merchant, similar amounts, regular intervals)
2. PREDICT: Forecast upcoming bills based on detected patterns
3. ALERT: Notify when expected payments are missed

Components:
    - RecurringPattern: Data class for detected patterns
    - RecurringDetector: Main detection engine
    - Pattern detection algorithms for various intervals (weekly, monthly, yearly)

How it works:
    1. Analyzes transaction history for patterns (same merchant, regular intervals)
    2. Groups transactions by merchant and identifies recurring amounts
    3. Calculates typical interval (weekly, bi-weekly, monthly, etc.)
    4. Predicts next occurrence and flags missed payments

Usage:
    from app.ai.recurring_detector import get_recurring_detector

    detector = get_recurring_detector()

    # Detect recurring patterns for a user
    patterns = detector.detect_patterns(user_id)

    # Get predicted upcoming bills
    upcoming = detector.get_upcoming_bills(user_id, days_ahead=30)

    # Check for missed payments
    missed = detector.check_missed_payments(user_id)
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal
from collections import defaultdict
import threading
from statistics import mean, stdev

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

# Minimum transactions to detect a pattern
MIN_TRANSACTIONS_FOR_PATTERN = 2

# Maximum amount variance to consider "same amount" (percentage)
AMOUNT_VARIANCE_THRESHOLD = 0.15  # 15%

# Maximum days variance to consider "regular interval"
INTERVAL_VARIANCE_DAYS = 5

# Supported recurring intervals (in days)
INTERVAL_WEEKLY = 7
INTERVAL_BIWEEKLY = 14
INTERVAL_MONTHLY = 30
INTERVAL_QUARTERLY = 90
INTERVAL_YEARLY = 365

# Tolerance for interval matching (days)
INTERVAL_TOLERANCE = {
    INTERVAL_WEEKLY: 2,
    INTERVAL_BIWEEKLY: 3,
    INTERVAL_MONTHLY: 5,
    INTERVAL_QUARTERLY: 10,
    INTERVAL_YEARLY: 15,
}

# Minimum confidence to consider a valid pattern
MIN_PATTERN_CONFIDENCE = 0.6

# Days to look back for pattern detection
LOOKBACK_DAYS = 365

# Days grace period before considering a payment "missed"
MISSED_PAYMENT_GRACE_DAYS = 7


# =============================================================================
# ENUMS & DATA CLASSES
# =============================================================================


class RecurrenceInterval(Enum):
    """Recurring transaction intervals."""
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    IRREGULAR = "irregular"


class PatternStatus(Enum):
    """Status of a recurring pattern."""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class RecurringPattern:
    """
    Represents a detected recurring transaction pattern.

    Attributes:
        merchant_name: Name of the merchant
        category_name: Category of the transactions
        category_id: UUID of the category
        average_amount: Typical transaction amount
        interval: Detected recurrence interval
        interval_days: Interval in days
        confidence: Confidence score (0-1)
        last_occurrence: Date of last transaction
        next_expected: Predicted next transaction date
        transaction_count: Number of transactions in pattern
        status: Current status of the pattern
    """
    merchant_name: str
    category_name: str
    category_id: Optional[str]
    average_amount: float
    interval: RecurrenceInterval
    interval_days: int
    confidence: float
    last_occurrence: datetime
    next_expected: datetime
    transaction_count: int
    status: PatternStatus = PatternStatus.ACTIVE
    amount_variance: float = 0.0
    transaction_ids: List[str] = None

    def __post_init__(self):
        if self.transaction_ids is None:
            self.transaction_ids = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "merchant_name": self.merchant_name,
            "category_name": self.category_name,
            "category_id": self.category_id,
            "average_amount": round(self.average_amount, 2),
            "interval": self.interval.value,
            "interval_days": self.interval_days,
            "confidence": round(self.confidence, 2),
            "last_occurrence": self.last_occurrence.isoformat(),
            "next_expected": self.next_expected.isoformat(),
            "transaction_count": self.transaction_count,
            "status": self.status.value,
            "amount_variance": round(self.amount_variance, 4),
            "is_overdue": self.is_overdue(),
            "days_until_next": self.days_until_next(),
        }

    def is_overdue(self) -> bool:
        """Check if expected payment is overdue."""
        now = datetime.now(timezone.utc)
        grace_period = timedelta(days=MISSED_PAYMENT_GRACE_DAYS)
        return now > (self.next_expected + grace_period)

    def days_until_next(self) -> int:
        """Days until next expected payment (negative if overdue)."""
        now = datetime.now(timezone.utc)
        delta = self.next_expected - now
        return delta.days


# =============================================================================
# RECURRING DETECTOR
# =============================================================================


class RecurringDetector:
    """
    Detects recurring transaction patterns.

    Analyzes transaction history to identify:
    - Subscriptions (Netflix, Spotify, etc.)
    - Regular bills (rent, utilities, insurance)
    - Recurring purchases (weekly groceries, etc.)

    Thread-safe singleton pattern ensures single instance.

    Example:
        >>> detector = get_recurring_detector()
        >>> patterns = detector.detect_patterns(user_id)
        >>> for p in patterns:
        ...     print(f"{p.merchant_name}: {p.interval.value} - ${p.average_amount:.2f}")
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
        if getattr(self, "_initialized", False):
            return

        self.is_initialized = False
        self._pattern_cache: Dict[str, Tuple[List[RecurringPattern], datetime]] = {}
        self._cache_ttl_minutes = 30

        self._initialized = True

    def initialize(self) -> bool:
        """Initialize the detector."""
        self.is_initialized = True
        logger.info("Recurring transaction detector initialized")
        return True

    def detect_patterns(
        self,
        user_id: UUID,
        lookback_days: int = LOOKBACK_DAYS,
        force_refresh: bool = False,
    ) -> List[RecurringPattern]:
        """
        Detect recurring transaction patterns for a user.

        Args:
            user_id: User's UUID
            lookback_days: Days of history to analyze
            force_refresh: Force recalculation (ignore cache)

        Returns:
            List of detected recurring patterns

        Example:
            >>> patterns = detector.detect_patterns(user_id)
            >>> patterns[0].merchant_name
            "Netflix"
        """
        # Check cache
        cache_key = str(user_id)
        if not force_refresh and cache_key in self._pattern_cache:
            patterns, cached_at = self._pattern_cache[cache_key]
            if datetime.now(timezone.utc) - cached_at < timedelta(minutes=self._cache_ttl_minutes):
                return patterns

        try:
            from app.models.transaction import Transaction
            from app.models.category import Category
            from app.models.enums import TransactionType
            from sqlalchemy import and_

            # Get expense transactions from lookback period
            cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
            cutoff_str = cutoff.strftime("%Y-%m-%d")

            transactions = Transaction.query.filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == TransactionType.EXPENSE,
                    Transaction.merchant_name.isnot(None),
                    Transaction.date >= cutoff_str,
                )
            ).order_by(Transaction.date).all()

            if not transactions:
                return []

            # Group by merchant (normalized)
            merchant_groups = self._group_by_merchant(transactions)

            # Detect patterns for each merchant group
            patterns = []
            for merchant_name, txs in merchant_groups.items():
                pattern = self._analyze_merchant_pattern(merchant_name, txs)
                if pattern and pattern.confidence >= MIN_PATTERN_CONFIDENCE:
                    patterns.append(pattern)

            # Sort by confidence descending
            patterns.sort(key=lambda p: p.confidence, reverse=True)

            # Cache results
            self._pattern_cache[cache_key] = (patterns, datetime.now(timezone.utc))

            logger.info(f"Detected {len(patterns)} recurring patterns for user {user_id}")
            return patterns

        except Exception as e:
            logger.error(f"Pattern detection failed for user {user_id}: {e}", exc_info=True)
            return []

    def _group_by_merchant(
        self,
        transactions: List[Any],
    ) -> Dict[str, List[Any]]:
        """Group transactions by normalized merchant name."""
        groups = defaultdict(list)

        for tx in transactions:
            if tx.merchant_name:
                # Normalize: lowercase, strip whitespace
                normalized = tx.merchant_name.lower().strip()
                groups[normalized].append(tx)

        return dict(groups)

    def _analyze_merchant_pattern(
        self,
        merchant_name: str,
        transactions: List[Any],
    ) -> Optional[RecurringPattern]:
        """
        Analyze transactions for a single merchant to detect patterns.

        Args:
            merchant_name: Normalized merchant name
            transactions: List of transactions for this merchant

        Returns:
            RecurringPattern if pattern detected, None otherwise
        """
        if len(transactions) < MIN_TRANSACTIONS_FOR_PATTERN:
            return None

        # Extract amounts and dates
        amounts = [float(tx.amount) for tx in transactions]
        dates = []
        for tx in transactions:
            if isinstance(tx.date, str):
                dates.append(datetime.strptime(tx.date, "%Y-%m-%d").replace(tzinfo=timezone.utc))
            else:
                dates.append(tx.date if tx.date.tzinfo else tx.date.replace(tzinfo=timezone.utc))

        # Sort by date
        date_amount_pairs = sorted(zip(dates, amounts, transactions), key=lambda x: x[0])
        dates = [d for d, _, _ in date_amount_pairs]
        amounts = [a for _, a, _ in date_amount_pairs]
        sorted_transactions = [t for _, _, t in date_amount_pairs]

        # Check amount consistency
        avg_amount = mean(amounts)
        if len(amounts) > 1:
            amount_variance = stdev(amounts) / avg_amount if avg_amount > 0 else 0
        else:
            amount_variance = 0

        if amount_variance > AMOUNT_VARIANCE_THRESHOLD:
            # Amounts too variable for recurring pattern
            return None

        # Calculate intervals between transactions
        intervals = []
        for i in range(1, len(dates)):
            delta = (dates[i] - dates[i-1]).days
            if delta > 0:  # Skip same-day transactions
                intervals.append(delta)

        if not intervals:
            return None

        # Detect interval pattern
        avg_interval = mean(intervals)
        interval_type, interval_days, interval_confidence = self._detect_interval_type(intervals)

        if interval_type == RecurrenceInterval.IRREGULAR:
            return None

        # Calculate next expected date
        last_date = dates[-1]
        next_expected = last_date + timedelta(days=interval_days)

        # Get category info
        category_name = "Unknown"
        category_id = None
        if sorted_transactions[0].category_id:
            try:
                from app.models.category import Category
                from app.core.extensions import db
                category = db.session.get(Category, sorted_transactions[0].category_id)
                if category:
                    category_name = category.name
                    category_id = str(sorted_transactions[0].category_id)
            except Exception:
                pass

        # Calculate overall confidence
        # Higher confidence if: more transactions, consistent amounts, regular intervals
        tx_count_factor = min(len(transactions) / 6, 1.0)  # Max at 6+ transactions
        amount_consistency = 1.0 - amount_variance
        confidence = (tx_count_factor * 0.3 + amount_consistency * 0.3 + interval_confidence * 0.4)

        return RecurringPattern(
            merchant_name=transactions[0].merchant_name,  # Use original name
            category_name=category_name,
            category_id=category_id,
            average_amount=avg_amount,
            interval=interval_type,
            interval_days=interval_days,
            confidence=confidence,
            last_occurrence=last_date,
            next_expected=next_expected,
            transaction_count=len(transactions),
            amount_variance=amount_variance,
            transaction_ids=[str(tx.id) for tx in sorted_transactions],
        )

    def _detect_interval_type(
        self,
        intervals: List[int],
    ) -> Tuple[RecurrenceInterval, int, float]:
        """
        Detect the recurring interval type from a list of intervals.

        Args:
            intervals: List of intervals between transactions (in days)

        Returns:
            Tuple of (RecurrenceInterval, average_days, confidence)
        """
        if not intervals:
            return RecurrenceInterval.IRREGULAR, 0, 0.0

        avg_interval = mean(intervals)
        if len(intervals) > 1:
            interval_variance = stdev(intervals)
        else:
            interval_variance = 0

        # Check against known intervals
        best_match = RecurrenceInterval.IRREGULAR
        best_interval = int(avg_interval)
        best_confidence = 0.0

        for target_days, tolerance in INTERVAL_TOLERANCE.items():
            # Check if average interval matches this pattern
            if abs(avg_interval - target_days) <= tolerance:
                # Check consistency
                matches = sum(1 for i in intervals if abs(i - target_days) <= tolerance)
                match_rate = matches / len(intervals)

                if match_rate > best_confidence:
                    if target_days == INTERVAL_WEEKLY:
                        best_match = RecurrenceInterval.WEEKLY
                    elif target_days == INTERVAL_BIWEEKLY:
                        best_match = RecurrenceInterval.BIWEEKLY
                    elif target_days == INTERVAL_MONTHLY:
                        best_match = RecurrenceInterval.MONTHLY
                    elif target_days == INTERVAL_QUARTERLY:
                        best_match = RecurrenceInterval.QUARTERLY
                    elif target_days == INTERVAL_YEARLY:
                        best_match = RecurrenceInterval.YEARLY

                    best_interval = target_days
                    best_confidence = match_rate

        return best_match, best_interval, best_confidence

    def get_upcoming_bills(
        self,
        user_id: UUID,
        days_ahead: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Get predicted upcoming bills.

        Args:
            user_id: User's UUID
            days_ahead: Days to look ahead

        Returns:
            List of upcoming bill predictions

        Example:
            >>> upcoming = detector.get_upcoming_bills(user_id, days_ahead=14)
            >>> upcoming[0]
            {"merchant": "Netflix", "amount": 15.99, "expected_date": "2026-02-01", "days_until": 5}
        """
        patterns = self.detect_patterns(user_id)
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(days=days_ahead)

        upcoming = []
        for pattern in patterns:
            if pattern.status == PatternStatus.ACTIVE and pattern.next_expected <= cutoff:
                upcoming.append({
                    "merchant_name": pattern.merchant_name,
                    "category_name": pattern.category_name,
                    "expected_amount": round(pattern.average_amount, 2),
                    "expected_date": pattern.next_expected.strftime("%Y-%m-%d"),
                    "days_until": pattern.days_until_next(),
                    "interval": pattern.interval.value,
                    "confidence": round(pattern.confidence, 2),
                    "is_overdue": pattern.is_overdue(),
                })

        # Sort by expected date
        upcoming.sort(key=lambda x: x["expected_date"])

        return upcoming

    def check_missed_payments(
        self,
        user_id: UUID,
    ) -> List[Dict[str, Any]]:
        """
        Check for missed recurring payments.

        Args:
            user_id: User's UUID

        Returns:
            List of potentially missed payments

        Example:
            >>> missed = detector.check_missed_payments(user_id)
            >>> missed[0]
            {"merchant": "Spotify", "expected_date": "2026-01-15", "days_overdue": 5}
        """
        patterns = self.detect_patterns(user_id)

        missed = []
        for pattern in patterns:
            if pattern.status == PatternStatus.ACTIVE and pattern.is_overdue():
                missed.append({
                    "merchant_name": pattern.merchant_name,
                    "category_name": pattern.category_name,
                    "expected_amount": round(pattern.average_amount, 2),
                    "expected_date": pattern.next_expected.strftime("%Y-%m-%d"),
                    "days_overdue": abs(pattern.days_until_next()),
                    "interval": pattern.interval.value,
                    "confidence": round(pattern.confidence, 2),
                })

        # Sort by days overdue (most overdue first)
        missed.sort(key=lambda x: x["days_overdue"], reverse=True)

        return missed

    def get_monthly_recurring_total(
        self,
        user_id: UUID,
    ) -> Dict[str, Any]:
        """
        Calculate total monthly recurring expenses.

        Args:
            user_id: User's UUID

        Returns:
            Dictionary with monthly recurring totals

        Example:
            >>> totals = detector.get_monthly_recurring_total(user_id)
            >>> totals
            {"monthly_total": 150.00, "pattern_count": 5, "by_category": {...}}
        """
        patterns = self.detect_patterns(user_id)

        monthly_total = 0.0
        by_category: Dict[str, float] = defaultdict(float)

        for pattern in patterns:
            if pattern.status != PatternStatus.ACTIVE:
                continue

            # Normalize to monthly amount
            if pattern.interval == RecurrenceInterval.WEEKLY:
                monthly_amount = pattern.average_amount * 4.33
            elif pattern.interval == RecurrenceInterval.BIWEEKLY:
                monthly_amount = pattern.average_amount * 2.17
            elif pattern.interval == RecurrenceInterval.MONTHLY:
                monthly_amount = pattern.average_amount
            elif pattern.interval == RecurrenceInterval.QUARTERLY:
                monthly_amount = pattern.average_amount / 3
            elif pattern.interval == RecurrenceInterval.YEARLY:
                monthly_amount = pattern.average_amount / 12
            else:
                continue

            monthly_total += monthly_amount
            by_category[pattern.category_name] += monthly_amount

        return {
            "monthly_total": round(monthly_total, 2),
            "yearly_projected": round(monthly_total * 12, 2),
            "pattern_count": len([p for p in patterns if p.status == PatternStatus.ACTIVE]),
            "by_category": {k: round(v, 2) for k, v in sorted(by_category.items(), key=lambda x: x[1], reverse=True)},
        }

    def get_pattern_summary(
        self,
        user_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get summary of recurring patterns for a user.

        Args:
            user_id: User's UUID

        Returns:
            Summary dictionary with patterns grouped by interval
        """
        patterns = self.detect_patterns(user_id)

        summary = {
            "total_patterns": len(patterns),
            "by_interval": defaultdict(list),
            "upcoming_week": [],
            "overdue": [],
        }

        now = datetime.now(timezone.utc)
        week_ahead = now + timedelta(days=7)

        for pattern in patterns:
            pattern_dict = pattern.to_dict()

            # Group by interval
            summary["by_interval"][pattern.interval.value].append(pattern_dict)

            # Check if upcoming this week
            if pattern.next_expected <= week_ahead and not pattern.is_overdue():
                summary["upcoming_week"].append(pattern_dict)

            # Check if overdue
            if pattern.is_overdue():
                summary["overdue"].append(pattern_dict)

        # Convert defaultdict to regular dict
        summary["by_interval"] = dict(summary["by_interval"])

        return summary

    def clear_cache(self, user_id: Optional[UUID] = None) -> None:
        """
        Clear pattern cache.

        Args:
            user_id: Specific user to clear (None = clear all)
        """
        if user_id:
            cache_key = str(user_id)
            if cache_key in self._pattern_cache:
                del self._pattern_cache[cache_key]
        else:
            self._pattern_cache.clear()


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_recurring_detector: Optional[RecurringDetector] = None


def get_recurring_detector() -> RecurringDetector:
    """
    Get the singleton RecurringDetector instance.

    Returns:
        RecurringDetector instance

    Example:
        >>> detector = get_recurring_detector()
        >>> patterns = detector.detect_patterns(user_id)
    """
    global _recurring_detector

    if _recurring_detector is None:
        _recurring_detector = RecurringDetector()
        _recurring_detector.initialize()

    return _recurring_detector


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "RecurringDetector",
    "get_recurring_detector",
    "RecurringPattern",
    "RecurrenceInterval",
    "PatternStatus",
    "MIN_TRANSACTIONS_FOR_PATTERN",
    "MIN_PATTERN_CONFIDENCE",
]
