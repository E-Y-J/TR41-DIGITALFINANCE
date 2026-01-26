# =============================================================================
# Digital Finance Tracker - Guardrails
# PURPOSE: Enforce finance-only scope for AI interactions
# =============================================================================
"""
Guardrails Module

Implements scope enforcement to ensure AI only handles finance-related requests.
Based on Elijah's PM requirements for restricting functionality.

Why Guardrails?
    - Users may ask off-topic questions ("How do I make bread?")
    - AI should politely redirect to finance topics
    - Prevents abuse and maintains focus

Implementation:
    1. Keyword-based detection (fast, rule-based)
    2. Semantic similarity to finance topics (MiniLM-based)
    3. Combined score determines if request is in-scope

Usage:
    from app.ai.guardrails import Guardrails, get_guardrails

    guardrails = get_guardrails()
    is_valid, message = guardrails.check_scope("How do I make bread?")
    # (False, "I can only help with finance tracking...")

    is_valid, message = guardrails.check_scope("How much did I spend?")
    # (True, None)

Notes:
    - Uses MiniLM for semantic understanding (if available)
    - Falls back to keyword-only if MiniLM not initialized
    - Custom logic as Guardrails.ai is not available (per Elijah's note)
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
import threading

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

# Minimum similarity score to consider request finance-related
SEMANTIC_THRESHOLD = 0.55

# Keyword-based threshold (ratio of finance keywords found)
KEYWORD_THRESHOLD = 0.1


# =============================================================================
# FINANCE VOCABULARY
# =============================================================================

# Keywords that indicate finance-related requests
FINANCE_KEYWORDS = [
    # Money & amounts
    "spend", "spent", "spending", "expense", "cost", "price", "amount",
    "dollar", "money", "cash", "payment", "paid", "pay",
    "$",  # Dollar sign
    # Transactions
    "transaction", "purchase", "buy", "bought", "sale", "transfer",
    "deposit", "withdrawal", "refund", "charge",
    # Categories
    "category", "categorize", "categorization", "classify",
    "food", "dining", "grocery", "restaurant",
    "transport", "uber", "lyft", "gas", "fuel",
    "shopping", "retail", "amazon", "store",
    "entertainment", "netflix", "spotify", "movie",
    "utility", "bill", "electric", "water", "internet",
    "medical", "health", "pharmacy", "doctor",
    "income", "salary", "paycheck", "wage",
    # Budgeting
    "budget", "limit", "goal", "savings", "save",
    "over budget", "under budget", "remaining",
    # Analytics
    "summary", "summarize", "total", "average", "breakdown",
    "insight", "pattern", "trend", "analyze", "analysis",
    # Actions
    "add", "create", "edit", "update", "delete", "remove",
    "show", "list", "view", "display", "get",
]

# Semantic topics for similarity matching
FINANCE_TOPICS = [
    "tracking personal spending and expenses",
    "managing household budget and savings",
    "categorizing financial transactions",
    "analyzing spending patterns by category",
    "adding expenses and income records",
    "viewing transaction history and summaries",
    "setting and monitoring budget goals",
    "understanding where money is going",
]

# Response when request is out of scope
OUT_OF_SCOPE_RESPONSES = [
    "I can only help with finance tracking. Try asking about your spending, "
    "transactions, or budget!",
    "That's outside my area of expertise. I'm here to help you track your "
    "finances. Need help with transactions or budgets?",
    "I'm focused on helping you manage your money. Would you like to see your "
    "spending summary or add a transaction?",
]


# =============================================================================
# GUARDRAILS CLASS
# =============================================================================


class Guardrails:
    """
    Enforces finance-only scope for AI interactions.

    Combines keyword matching and semantic similarity to determine
    if a user's request is within the finance tracking domain.

    Attributes:
        intent_classifier: Optional MiniLM classifier for semantic matching
        topic_embeddings: Pre-computed embeddings for finance topics

    Example:
        >>> guardrails = Guardrails()
        >>> in_scope, msg = guardrails.check_scope("What's the weather?")
        >>> print(in_scope, msg)
        False "I can only help with finance tracking..."
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_done = False
        return cls._instance

    def __init__(self):
        """Initialize guardrails."""
        if self._init_done:
            return

        self.intent_classifier = None
        self.topic_embeddings = None
        self.is_initialized = False
        self._response_index = 0
        self._init_done = True
        logger.debug("Guardrails instance created")

    def initialize(self) -> bool:
        """
        Initialize semantic matching (optional).

        Falls back to keyword-only if MiniLM not available or disabled.
        """
        if self.is_initialized:
            return True

        # Check if guardrails is disabled via config
        try:
            from app.core.config import get_config
            config = get_config()
            if hasattr(config, 'AI_GUARDRAILS_ENABLED') and not config.AI_GUARDRAILS_ENABLED:
                logger.info("Guardrails disabled via AI_GUARDRAILS_ENABLED=0")
                self.is_initialized = True
                return True
        except Exception:
            pass  # Config not available, continue with normal init

        try:
            # Try to use intent classifier for semantic matching
            from app.ai.intent_classifier import get_intent_classifier

            self.intent_classifier = get_intent_classifier()

            # Pre-compute topic embeddings
            if self.intent_classifier.is_initialized and not self.intent_classifier._use_fallback:
                import numpy as np

                embeddings = self.intent_classifier.embed_batch(FINANCE_TOPICS)
                self.topic_embeddings = np.mean(embeddings, axis=0)
                logger.info("Guardrails initialized with semantic matching")
            else:
                logger.info("Guardrails initialized with keyword-only matching")

            self.is_initialized = True
            return True

        except ImportError:
            logger.info("MiniLM not available, using keyword-only guardrails")
            self.is_initialized = True
            return True
        except RuntimeError:
            # embed_batch raises RuntimeError when using fallback
            logger.info("Intent classifier in fallback mode, using keyword-only guardrails")
            self.is_initialized = True
            return True
        except Exception as e:
            logger.warning(f"Guardrails semantic init failed, using keywords: {e}")
            self.is_initialized = True
            return True

    def check_scope(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Check if request is within finance scope.

        Args:
            text: User's input message

        Returns:
            Tuple of (is_in_scope, error_message)
            - If in scope: (True, None)
            - If out of scope: (False, "redirect message")

        Example:
            >>> in_scope, msg = guardrails.check_scope("make me a sandwich")
            >>> if not in_scope:
            ...     return {"response": msg}
        """
        if not self.is_initialized:
            self.initialize()

        text_lower = text.lower()

        # Step 1: Keyword check (fast)
        keyword_score = self._keyword_score(text_lower)
        if keyword_score >= KEYWORD_THRESHOLD:
            logger.debug(f"In scope (keyword): '{text[:50]}...' score={keyword_score:.2f}")
            return True, None

        # Step 2: Semantic check (if available)
        if self.topic_embeddings is not None:
            try:
                semantic_score = self._semantic_score(text)
                if semantic_score >= SEMANTIC_THRESHOLD:
                    logger.debug(
                        f"In scope (semantic): '{text[:50]}...' score={semantic_score:.2f}"
                    )
                    return True, None
            except Exception as e:
                logger.warning(f"Semantic check failed: {e}")

        # Out of scope
        logger.info(f"Out of scope: '{text[:50]}...'")
        return False, self._get_out_of_scope_response()

    def _keyword_score(self, text_lower: str) -> float:
        """Calculate keyword-based finance relevance score."""
        words = set(re.findall(r"\w+", text_lower))

        # Also check for dollar sign
        if "$" in text_lower:
            words.add("$")

        # Count matching keywords
        matches = sum(1 for kw in FINANCE_KEYWORDS if kw in text_lower)

        # Normalize by text length (avoid division by zero)
        word_count = max(len(words), 1)
        return matches / word_count

    def _semantic_score(self, text: str) -> float:
        """Calculate semantic similarity to finance topics."""
        import numpy as np

        # Embed user text
        text_embedding = self.intent_classifier.embed_text(text)

        # Cosine similarity to mean topic embedding
        norm_text = np.linalg.norm(text_embedding)
        norm_topic = np.linalg.norm(self.topic_embeddings)

        if norm_text == 0 or norm_topic == 0:
            return 0.0

        similarity = np.dot(text_embedding, self.topic_embeddings) / (
            norm_text * norm_topic
        )
        return float(similarity)

    def _get_out_of_scope_response(self) -> str:
        """Get a varied out-of-scope response."""
        response = OUT_OF_SCOPE_RESPONSES[self._response_index]
        self._response_index = (self._response_index + 1) % len(OUT_OF_SCOPE_RESPONSES)
        return response

    def get_info(self) -> Dict[str, Any]:
        """Get guardrails status and configuration."""
        return {
            "is_initialized": self.is_initialized,
            "has_semantic": self.topic_embeddings is not None,
            "keyword_threshold": KEYWORD_THRESHOLD,
            "semantic_threshold": SEMANTIC_THRESHOLD,
            "num_keywords": len(FINANCE_KEYWORDS),
            "num_topics": len(FINANCE_TOPICS),
        }


# =============================================================================
# SINGLETON ACCESSOR
# =============================================================================

_guardrails: Optional[Guardrails] = None


def get_guardrails() -> Guardrails:
    """Get the guardrails singleton."""
    global _guardrails
    if _guardrails is None:
        _guardrails = Guardrails()
    return _guardrails


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================


def is_finance_related(text: str) -> bool:
    """
    Quick check if text is finance-related.

    Convenience function that returns just boolean.

    Args:
        text: User's input message

    Returns:
        True if finance-related, False otherwise
    """
    guardrails = get_guardrails()
    in_scope, _ = guardrails.check_scope(text)
    return in_scope


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "Guardrails",
    "get_guardrails",
    "is_finance_related",
    "FINANCE_KEYWORDS",
    "FINANCE_TOPICS",
]
