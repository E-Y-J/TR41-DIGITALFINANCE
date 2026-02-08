# =============================================================================
# Digital Finance Tracker - Clarification Flow
# PURPOSE: Handle low-confidence AI categorizations with user prompts
# =============================================================================
"""
Clarification Flow Module

This module handles scenarios where AI confidence is low and user input is needed:
- Transaction categorization clarification
- Ambiguous command interpretation
- User preference learning

The clarification flow:
1. AI detects low confidence (<50%)
2. System creates a pending clarification request
3. User sees notification/prompt in app
4. User selects the correct option
5. System learns from user feedback

Usage:
    from app.ai.clarification import ClarificationManager, get_clarification_manager

    # Get manager
    manager = get_clarification_manager()

    # Create clarification request
    request = manager.create_request(
        user_id=user_id,
        request_type="category",
        transaction_id=tx.id,
        alternatives=[
            {"category": "Food & Dining", "confidence": 0.45},
            {"category": "Shopping", "confidence": 0.35},
        ]
    )

    # User responds
    manager.resolve_request(request_id, user_choice="Food & Dining")

Notes:
    - Clarifications expire after 24 hours
    - User responses are used to improve future categorization
    - Integrates with notification system for in-app alerts
"""

import logging
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta
from enum import Enum
import threading

logger = logging.getLogger(__name__)


# =============================================================================
# CLARIFICATION TYPES
# =============================================================================


class ClarificationType(str, Enum):
    """Types of clarification requests."""

    CATEGORY = "category"  # Transaction category unclear
    AMOUNT = "amount"  # Amount seems unusual
    MERCHANT = "merchant"  # Merchant name unclear
    DUPLICATE = "duplicate"  # Possible duplicate transaction
    BUDGET = "budget"  # Budget category assignment


class ClarificationStatus(str, Enum):
    """Status of clarification requests."""

    PENDING = "pending"  # Waiting for user response
    RESOLVED = "resolved"  # User has responded
    EXPIRED = "expired"  # No response within timeout
    DISMISSED = "dismissed"  # User dismissed without responding


# =============================================================================
# CLARIFICATION REQUEST
# =============================================================================


class ClarificationRequest:
    """
    Represents a clarification request to the user.

    Attributes:
        id: Unique request ID
        user_id: User who should respond
        request_type: Type of clarification needed
        transaction_id: Related transaction (if applicable)
        alternatives: List of options for user to choose
        status: Current status of request
        created_at: When request was created
        resolved_at: When user responded (if resolved)
        user_choice: What user selected (if resolved)
    """

    def __init__(
        self,
        user_id: UUID,
        request_type: ClarificationType,
        alternatives: List[Dict[str, Any]],
        transaction_id: Optional[UUID] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.id = uuid4()
        self.user_id = user_id
        self.request_type = request_type
        self.transaction_id = transaction_id
        self.alternatives = alternatives
        self.context = context or {}
        self.status = ClarificationStatus.PENDING
        self.created_at = datetime.now(timezone.utc)
        self.resolved_at: Optional[datetime] = None
        self.user_choice: Optional[str] = None
        self.expires_at = self.created_at + timedelta(hours=24)

    def is_expired(self) -> bool:
        """Check if request has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    def resolve(self, choice: str):
        """Mark request as resolved with user's choice."""
        self.status = ClarificationStatus.RESOLVED
        self.user_choice = choice
        self.resolved_at = datetime.now(timezone.utc)

    def dismiss(self):
        """Mark request as dismissed."""
        self.status = ClarificationStatus.DISMISSED
        self.resolved_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "type": self.request_type.value,
            "transaction_id": str(self.transaction_id) if self.transaction_id else None,
            "alternatives": self.alternatives,
            "context": self.context,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "user_choice": self.user_choice,
        }


# =============================================================================
# CLARIFICATION MANAGER
# =============================================================================


class ClarificationManager:
    """
    Manages clarification requests and user responses.

    Handles the full lifecycle of clarification:
    - Creating new requests
    - Notifying users
    - Processing responses
    - Learning from feedback

    Attributes:
        pending_requests: Dictionary of pending requests by user
        resolved_requests: History of resolved requests (for learning)

    Example:
        >>> manager = ClarificationManager()
        >>> request = manager.create_request(
        ...     user_id,
        ...     ClarificationType.CATEGORY,
        ...     [{"category": "Food", "confidence": 0.4}]
        ... )
        >>> manager.resolve_request(request.id, "Food")
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
        """Initialize the clarification manager."""
        if self._initialized:
            return

        # Pending requests by user_id
        self._pending: Dict[UUID, List[ClarificationRequest]] = {}

        # Request lookup by ID
        self._requests: Dict[UUID, ClarificationRequest] = {}

        # Feedback history for learning (category -> user corrections)
        self._feedback: Dict[str, List[Dict[str, Any]]] = {}

        self._initialized = True

    def create_request(
        self,
        user_id: UUID,
        request_type: ClarificationType,
        alternatives: List[Dict[str, Any]],
        transaction_id: Optional[UUID] = None,
        context: Optional[Dict[str, Any]] = None,
        notify_user: bool = True,
    ) -> ClarificationRequest:
        """
        Create a new clarification request.

        Args:
            user_id: User who should respond
            request_type: Type of clarification needed
            alternatives: Options for user to choose from
            transaction_id: Related transaction (if any)
            context: Additional context for the request
            notify_user: Whether to create notification

        Returns:
            The created ClarificationRequest
        """
        # Clean up expired requests
        self._cleanup_expired()

        request = ClarificationRequest(
            user_id=user_id,
            request_type=request_type,
            alternatives=alternatives,
            transaction_id=transaction_id,
            context=context,
        )

        # Store request
        self._requests[request.id] = request

        if user_id not in self._pending:
            self._pending[user_id] = []
        self._pending[user_id].append(request)

        # Create notification
        if notify_user:
            self._create_notification(request)

        logger.info(
            f"Created clarification request {request.id} for user {user_id}: {request_type.value}"
        )

        return request

    def get_pending_requests(
        self,
        user_id: UUID,
        request_type: Optional[ClarificationType] = None,
    ) -> List[ClarificationRequest]:
        """
        Get pending clarification requests for a user.

        Args:
            user_id: User to get requests for
            request_type: Optional filter by type

        Returns:
            List of pending ClarificationRequests
        """
        self._cleanup_expired()

        requests = self._pending.get(user_id, [])

        # Filter by type if specified
        if request_type:
            requests = [r for r in requests if r.request_type == request_type]

        # Filter out expired
        requests = [r for r in requests if not r.is_expired()]

        return requests

    def get_request(self, request_id: UUID) -> Optional[ClarificationRequest]:
        """Get a specific request by ID."""
        return self._requests.get(request_id)

    def resolve_request(
        self,
        request_id: UUID,
        user_choice: str,
        apply_to_transaction: bool = True,
    ) -> Optional[ClarificationRequest]:
        """
        Resolve a clarification request with user's choice.

        Args:
            request_id: ID of the request to resolve
            user_choice: User's selected option
            apply_to_transaction: Whether to update the transaction

        Returns:
            The resolved request, or None if not found
        """
        request = self._requests.get(request_id)
        if not request:
            logger.warning(f"Clarification request {request_id} not found")
            return None

        if request.status != ClarificationStatus.PENDING:
            logger.warning(f"Request {request_id} is not pending: {request.status}")
            return request

        # Resolve the request
        request.resolve(user_choice)

        # Remove from pending
        if request.user_id in self._pending:
            self._pending[request.user_id] = [
                r for r in self._pending[request.user_id] if r.id != request_id
            ]

        # Apply to transaction if requested
        if apply_to_transaction and request.transaction_id:
            self._apply_to_transaction(request)

        # Record feedback for learning
        self._record_feedback(request)

        logger.info(f"Resolved clarification {request_id} with choice: {user_choice}")

        return request

    def dismiss_request(self, request_id: UUID) -> Optional[ClarificationRequest]:
        """
        Dismiss a clarification request without responding.

        Args:
            request_id: ID of the request to dismiss

        Returns:
            The dismissed request, or None if not found
        """
        request = self._requests.get(request_id)
        if not request:
            return None

        request.dismiss()

        # Remove from pending
        if request.user_id in self._pending:
            self._pending[request.user_id] = [
                r for r in self._pending[request.user_id] if r.id != request_id
            ]

        logger.info(f"Dismissed clarification {request_id}")

        return request

    def _cleanup_expired(self):
        """Clean up expired requests."""
        now = datetime.now(timezone.utc)

        expired_ids = []
        for request_id, request in self._requests.items():
            if request.is_expired() and request.status == ClarificationStatus.PENDING:
                request.status = ClarificationStatus.EXPIRED
                expired_ids.append(request_id)

        # Clean up pending lists
        for user_id in self._pending:
            self._pending[user_id] = [
                r
                for r in self._pending[user_id]
                if not r.is_expired() and r.status == ClarificationStatus.PENDING
            ]

    def _create_notification(self, request: ClarificationRequest):
        """Create an in-app notification for the clarification request."""
        try:
            from app.services.notification_service import NotificationService
            from app.models.enums import NotificationType

            # Build notification message
            if request.request_type == ClarificationType.CATEGORY:
                title = "Help me categorize a transaction"
                message = "I'm not sure how to categorize a recent transaction. Can you help?"
            elif request.request_type == ClarificationType.DUPLICATE:
                title = "Possible duplicate transaction"
                message = "I found what might be a duplicate transaction. Can you confirm?"
            else:
                title = "Clarification needed"
                message = "I need your input on something."

            NotificationService.create_notification(
                user_id=request.user_id,
                notification_type=NotificationType.AI_CLARIFICATION,
                title=title,
                message=message,
                data={
                    "clarification_id": str(request.id),
                    "type": request.request_type.value,
                    "alternatives": request.alternatives,
                },
            )

        except Exception as e:
            logger.error(f"Failed to create notification for clarification: {e}")

    def _apply_to_transaction(self, request: ClarificationRequest):
        """Apply the user's choice to the transaction."""
        try:
            from app.services.transaction_service import TransactionService
            from app.services.category_service import CategoryService

            if request.request_type == ClarificationType.CATEGORY:
                # Get the category by name
                category = CategoryService.get_by_name(request.user_choice)
                if category and request.transaction_id:
                    TransactionService.update_category(
                        user_id=request.user_id,
                        transaction_id=request.transaction_id,
                        category_id=category.id,
                        is_user_override=True,
                    )
                    logger.info(
                        f"Updated transaction {request.transaction_id} "
                        f"category to {request.user_choice}"
                    )

        except Exception as e:
            logger.error(f"Failed to apply clarification to transaction: {e}", exc_info=True)

    def _record_feedback(self, request: ClarificationRequest):
        """Record user feedback for future learning."""
        if request.request_type != ClarificationType.CATEGORY:
            return

        # Get the merchant/description from context
        merchant = request.context.get("merchant_name", "")
        description = request.context.get("description", "")

        key = f"{merchant}|{description}".lower()

        if key not in self._feedback:
            self._feedback[key] = []

        self._feedback[key].append(
            {
                "user_choice": request.user_choice,
                "alternatives": request.alternatives,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        # Keep only last 10 feedback items per key
        if len(self._feedback[key]) > 10:
            self._feedback[key] = self._feedback[key][-10:]

    def get_learned_category(
        self,
        merchant: str,
        description: Optional[str] = None,
    ) -> Optional[str]:
        """
        Get a learned category from previous user corrections.

        Args:
            merchant: Merchant name
            description: Transaction description

        Returns:
            Category name if learned, None otherwise
        """
        key = f"{merchant}|{description or ''}".lower()

        feedback_list = self._feedback.get(key, [])
        if not feedback_list:
            return None

        # Get most common user choice
        choices = [f["user_choice"] for f in feedback_list]
        if choices:
            # Return most frequent
            from collections import Counter

            most_common = Counter(choices).most_common(1)
            if most_common:
                return most_common[0][0]

        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get clarification statistics."""
        total_pending = sum(len(reqs) for reqs in self._pending.values())
        total_requests = len(self._requests)

        status_counts = {}
        for request in self._requests.values():
            status = request.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_pending": total_pending,
            "total_requests": total_requests,
            "by_status": status_counts,
            "feedback_entries": len(self._feedback),
            "users_with_pending": len(self._pending),
        }


# =============================================================================
# CLARIFICATION PROMPT BUILDER
# =============================================================================


class ClarificationPromptBuilder:
    """
    Builds user-friendly clarification prompts.

    Creates consistent, helpful prompts for different clarification scenarios.
    """

    @staticmethod
    def category_prompt(
        transaction_info: Dict[str, Any],
        alternatives: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Build a category clarification prompt.

        Args:
            transaction_info: Transaction details
            alternatives: Category alternatives with confidence

        Returns:
            Prompt data for UI display
        """
        merchant = transaction_info.get("merchant_name", "a transaction")
        amount = transaction_info.get("amount", "?")

        # Sort alternatives by confidence
        sorted_alts = sorted(
            alternatives, key=lambda x: x.get("confidence", 0), reverse=True
        )

        options = [
            {
                "label": alt.get("category"),
                "value": alt.get("category"),
                "confidence": alt.get("confidence", 0),
                "is_recommended": idx == 0,
            }
            for idx, alt in enumerate(sorted_alts[:5])
        ]

        return {
            "type": "category_clarification",
            "title": "Help me categorize this transaction",
            "message": f"How should I categorize the ${amount} transaction at {merchant}?",
            "options": options,
            "allow_custom": True,
            "context": transaction_info,
        }

    @staticmethod
    def duplicate_prompt(
        transaction: Dict[str, Any],
        possible_duplicate: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build a duplicate transaction prompt.

        Args:
            transaction: New transaction
            possible_duplicate: Potential duplicate

        Returns:
            Prompt data for UI display
        """
        return {
            "type": "duplicate_check",
            "title": "Is this a duplicate?",
            "message": "This transaction looks similar to an existing one.",
            "new_transaction": transaction,
            "existing_transaction": possible_duplicate,
            "options": [
                {"label": "Keep both", "value": "keep_both"},
                {"label": "It's a duplicate (delete new)", "value": "delete_new"},
                {"label": "It's a duplicate (delete old)", "value": "delete_old"},
            ],
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_clarification_manager: Optional[ClarificationManager] = None


def get_clarification_manager() -> ClarificationManager:
    """
    Get the singleton ClarificationManager instance.

    Returns:
        ClarificationManager instance
    """
    global _clarification_manager
    if _clarification_manager is None:
        _clarification_manager = ClarificationManager()
    return _clarification_manager


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def request_category_clarification(
    user_id: UUID,
    transaction_id: UUID,
    transaction_info: Dict[str, Any],
    alternatives: List[Dict[str, Any]],
) -> ClarificationRequest:
    """
    Convenience function to request category clarification.

    Args:
        user_id: User to ask
        transaction_id: Transaction needing clarification
        transaction_info: Transaction details for context
        alternatives: Category options

    Returns:
        Created ClarificationRequest
    """
    manager = get_clarification_manager()
    return manager.create_request(
        user_id=user_id,
        request_type=ClarificationType.CATEGORY,
        alternatives=alternatives,
        transaction_id=transaction_id,
        context=transaction_info,
    )


def check_learned_category(merchant: str) -> Optional[str]:
    """
    Check if we've learned a category for a merchant.

    Args:
        merchant: Merchant name

    Returns:
        Learned category name or None
    """
    manager = get_clarification_manager()
    return manager.get_learned_category(merchant)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "ClarificationManager",
    "ClarificationRequest",
    "ClarificationType",
    "ClarificationStatus",
    "ClarificationPromptBuilder",
    "get_clarification_manager",
    "request_category_clarification",
    "check_learned_category",
]
