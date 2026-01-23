# =============================================================================
# Digital Finance Tracker - User Learning Module
# PURPOSE: Learn from user corrections to improve categorization accuracy
# =============================================================================
"""
User Learning Module

This module enables the AI system to learn from user corrections:
- Track when users change AI-assigned categories
- Build per-user merchant → category mappings
- Prioritize learned mappings over generic AI predictions

Learning Flow:
    1. AI categorizes transaction as "Shopping & Retail"
    2. User corrects it to "Food & Dining"
    3. System stores: (user_id, "merchant_name") → "Food & Dining"
    4. Next time same merchant appears, system uses learned category

Storage Options:
    - Current: In-memory cache (lost on restart)
    - Future: Database table (persistent)
    - Future: Redis cache (fast + persistent)

Usage:
    from app.ai.user_learning import UserLearningEngine, get_learning_engine

    engine = get_learning_engine()

    # Record a user correction
    engine.record_correction(user_id, "Local Coffee Shop", "Food & Dining")

    # Get learned category for a merchant
    category = engine.get_learned_category(user_id, "Local Coffee Shop")
    # Returns: "Food & Dining" or None if not learned

Notes:
    - Learning is per-user (personalized)
    - System also tracks global patterns across all users
    - High-confidence global patterns can become new keywords
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from uuid import UUID
from datetime import datetime, timezone
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

# Minimum corrections before considering a global pattern
GLOBAL_PATTERN_THRESHOLD = 5

# Confidence boost for learned categories
LEARNED_CONFIDENCE = 0.95


# =============================================================================
# USER LEARNING ENGINE
# =============================================================================


class UserLearningEngine:
    """
    Learns from user corrections to improve categorization.

    Implements two levels of learning:
    1. User-specific: Personal merchant → category mappings
    2. Global: Aggregate patterns across all users

    Attributes:
        user_mappings: Dict of user_id → {merchant → category}
        global_counts: Dict of merchant → {category → count}
        correction_history: List of all corrections for analysis

    Example:
        >>> engine = UserLearningEngine()
        >>> engine.record_correction(user_id, "Local Shop", "Food & Dining")
        >>> category = engine.get_learned_category(user_id, "Local Shop")
        >>> print(category)  # "Food & Dining"
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
        """Initialize the learning engine."""
        if self._initialized:
            return

        # User-specific learned mappings
        # Structure: {user_id: {normalized_merchant: category_name}}
        self._user_mappings: Dict[UUID, Dict[str, str]] = defaultdict(dict)

        # Global correction counts across all users
        # Structure: {normalized_merchant: {category_name: count}}
        self._global_counts: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        # Full correction history for analysis
        self._correction_history: List[Dict[str, Any]] = []

        # Statistics
        self._stats = {
            "total_corrections": 0,
            "unique_merchants": 0,
            "users_with_corrections": set(),
        }

        self._initialized = True
        logger.info("User Learning Engine initialized")

    def record_correction(
        self,
        user_id: UUID,
        merchant_name: str,
        correct_category: str,
        original_category: Optional[str] = None,
        original_source: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record a user's category correction for learning.

        Called when a user changes the AI-assigned category of a transaction.
        Updates both user-specific and global learning data.

        Args:
            user_id: User making the correction
            merchant_name: Merchant name from transaction
            correct_category: The category user selected
            original_category: What AI originally predicted (for analysis)
            original_source: Where original prediction came from

        Returns:
            Dictionary with learning update details

        Example:
            >>> engine.record_correction(
            ...     user_id=uuid,
            ...     merchant_name="Local Coffee Co",
            ...     correct_category="Food & Dining",
            ...     original_category="Shopping & Retail",
            ...     original_source="huggingface"
            ... )
        """
        # Normalize merchant name for consistent matching
        normalized = self._normalize_merchant(merchant_name)

        # Update user-specific mapping
        self._user_mappings[user_id][normalized] = correct_category

        # Update global counts
        self._global_counts[normalized][correct_category] += 1

        # Record in history
        correction_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": str(user_id),
            "merchant_name": merchant_name,
            "normalized_merchant": normalized,
            "correct_category": correct_category,
            "original_category": original_category,
            "original_source": original_source,
        }
        self._correction_history.append(correction_record)

        # Update stats
        self._stats["total_corrections"] += 1
        self._stats["users_with_corrections"].add(str(user_id))
        self._stats["unique_merchants"] = len(self._global_counts)

        logger.info(
            f"Learned: '{merchant_name}' → {correct_category} "
            f"(user: {str(user_id)[:8]}..., was: {original_category})"
        )

        return {
            "learned": True,
            "merchant": merchant_name,
            "category": correct_category,
            "is_new_merchant": normalized not in self._global_counts,
            "global_count": self._global_counts[normalized][correct_category],
        }

    def get_learned_category(
        self,
        user_id: UUID,
        merchant_name: str,
    ) -> Optional[Tuple[str, float, str]]:
        """
        Get learned category for a merchant.

        First checks user-specific mappings, then falls back to global patterns.

        Args:
            user_id: User to check mappings for
            merchant_name: Merchant name to look up

        Returns:
            Tuple of (category_name, confidence, source) or None if not learned

        Example:
            >>> result = engine.get_learned_category(user_id, "Local Shop")
            >>> if result:
            ...     category, confidence, source = result
            ...     print(f"{category} ({source})")  # "Food & Dining (user_learned)"
        """
        normalized = self._normalize_merchant(merchant_name)

        # Check user-specific mapping first (highest priority)
        if user_id in self._user_mappings:
            if normalized in self._user_mappings[user_id]:
                category = self._user_mappings[user_id][normalized]
                return (category, LEARNED_CONFIDENCE, "user_learned")

        # Check global patterns
        if normalized in self._global_counts:
            category_counts = self._global_counts[normalized]
            if category_counts:
                # Get most common category
                most_common = max(category_counts.items(), key=lambda x: x[1])
                category, count = most_common

                # Only use if enough corrections
                if count >= GLOBAL_PATTERN_THRESHOLD:
                    # Confidence scales with number of corrections
                    confidence = min(0.85, 0.5 + (count * 0.05))
                    return (category, confidence, "global_learned")

        return None

    def get_suggestions(
        self,
        merchant_name: str,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Get category suggestions based on global learning.

        Useful for presenting options to users for ambiguous merchants.

        Args:
            merchant_name: Merchant to get suggestions for
            limit: Maximum number of suggestions

        Returns:
            List of suggestion dictionaries sorted by frequency
        """
        normalized = self._normalize_merchant(merchant_name)

        if normalized not in self._global_counts:
            return []

        category_counts = self._global_counts[normalized]
        sorted_categories = sorted(
            category_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return [
            {
                "category": cat,
                "count": count,
                "percentage": round(count / sum(category_counts.values()) * 100, 1),
            }
            for cat, count in sorted_categories[:limit]
        ]

    def get_user_learned_merchants(self, user_id: UUID) -> Dict[str, str]:
        """Get all learned merchant → category mappings for a user."""
        return dict(self._user_mappings.get(user_id, {}))

    def get_stats(self) -> Dict[str, Any]:
        """Get learning engine statistics."""
        return {
            "total_corrections": self._stats["total_corrections"],
            "unique_merchants_learned": self._stats["unique_merchants"],
            "users_with_corrections": len(self._stats["users_with_corrections"]),
            "global_patterns": len(
                [
                    m
                    for m, counts in self._global_counts.items()
                    if max(counts.values(), default=0) >= GLOBAL_PATTERN_THRESHOLD
                ]
            ),
        }

    def get_correction_history(
        self,
        user_id: Optional[UUID] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get correction history, optionally filtered by user."""
        history = self._correction_history

        if user_id:
            history = [h for h in history if h["user_id"] == str(user_id)]

        return history[-limit:]

    def suggest_new_keywords(self) -> List[Dict[str, Any]]:
        """
        Suggest new keywords to add to KEYWORD_CATEGORY_MAP.

        Analyzes global patterns to find merchants that should become keywords.

        Returns:
            List of suggested keyword additions
        """
        suggestions = []

        for merchant, category_counts in self._global_counts.items():
            if not category_counts:
                continue

            most_common = max(category_counts.items(), key=lambda x: x[1])
            category, count = most_common

            if count >= GLOBAL_PATTERN_THRESHOLD:
                total_for_merchant = sum(category_counts.values())
                agreement_rate = count / total_for_merchant

                # Suggest if high agreement
                if agreement_rate >= 0.8:
                    suggestions.append(
                        {
                            "keyword": merchant,
                            "category": category,
                            "count": count,
                            "agreement_rate": round(agreement_rate * 100, 1),
                            "reason": f"{count} users categorized as {category}",
                        }
                    )

        return sorted(suggestions, key=lambda x: x["count"], reverse=True)

    def _normalize_merchant(self, merchant_name: str) -> str:
        """
        Normalize merchant name for consistent matching.

        Removes common variations to improve matching:
        - Lowercase
        - Remove special characters
        - Remove common suffixes (#1234, store numbers)
        """
        import re

        if not merchant_name:
            return ""

        # Lowercase
        normalized = merchant_name.lower().strip()

        # Remove store numbers (#1234, Store 567, etc.)
        normalized = re.sub(r"#\d+", "", normalized)
        normalized = re.sub(r"store\s*\d+", "", normalized)
        normalized = re.sub(r"\s+\d+$", "", normalized)

        # Remove special characters except spaces
        normalized = re.sub(r"[^\w\s]", "", normalized)

        # Collapse multiple spaces
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

    def clear_user_data(self, user_id: UUID):
        """Clear all learned data for a specific user."""
        if user_id in self._user_mappings:
            del self._user_mappings[user_id]

        self._correction_history = [
            h for h in self._correction_history if h["user_id"] != str(user_id)
        ]

        self._stats["users_with_corrections"].discard(str(user_id))
        logger.info(f"Cleared learning data for user {user_id}")


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_learning_engine: Optional[UserLearningEngine] = None


def get_learning_engine() -> UserLearningEngine:
    """
    Get the singleton UserLearningEngine instance.

    Returns:
        UserLearningEngine instance
    """
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = UserLearningEngine()
    return _learning_engine


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "UserLearningEngine",
    "get_learning_engine",
    "LEARNED_CONFIDENCE",
    "GLOBAL_PATTERN_THRESHOLD",
]
