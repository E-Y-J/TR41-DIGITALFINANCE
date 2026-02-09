# =============================================================================
# Digital Finance Tracker - Intent Classifier
# PURPOSE: MiniLM-based intent detection for natural language commands
# =============================================================================
"""
Intent Classifier Module

Uses sentence-transformers/multi-qa-MiniLM-L6-cos-v1 for semantic similarity
based intent classification. This model excels at understanding user queries
and matching them to predefined intents.

Model Info:
    - Name: multi-qa-MiniLM-L6-cos-v1
    - Size: ~80MB
    - Output: 384-dimensional embeddings
    - Training: 215M+ question-answer pairs
    - GPU: Not required

How It Works:
    1. Pre-compute embeddings for all intent examples
    2. When user sends message, embed their text
    3. Find most similar intent using cosine similarity
    4. Return intent with confidence score

Usage:
    from app.ai.intent_classifier import IntentClassifier, get_intent_classifier

    classifier = get_intent_classifier()
    intent, confidence = classifier.classify("show my spending last month")
    # ("summarize_transactions", 0.89)

Supported Intents (Elijah's Requirements):
    - summarize_transactions: "Summarize my transactions"
    - show_transactions: "Show me all my transactions"
    - add_transaction: "Add $50 for lunch"
    - edit_transaction: "Change my last transaction"
    - delete_transaction: "Delete my last transaction"
    - query_spending: "How much did I spend on food?"
    - categorize_help: "What category is Uber?"
    - budget_status: "Am I over budget?"

Notes:
    - Thread-safe singleton pattern
    - Lazy loading (model loaded on first use)
    - Works with guardrails.py for scope enforcement
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import threading
import numpy as np

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

MODEL_NAME = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
CONFIDENCE_THRESHOLD = 0.70  # Below this, intent is uncertain


# =============================================================================
# INTENT DEFINITIONS
# =============================================================================
# Each intent has example phrases that represent it.
# The classifier embeds these examples and compares user input to them.

INTENT_EXAMPLES = {
    "summarize_transactions": [
        "summarize my transactions",
        "show me a summary",
        "give me an overview of my spending",
        "what's my spending summary",
        "how much did I spend",
        "spending overview",
        "transaction summary",
        "show spending breakdown",
    ],
    "show_transactions": [
        "show me all my transactions",
        "list my transactions",
        "show my recent transactions",
        "what are my transactions",
        "display transactions",
        "view my transactions",
        "get my transaction history",
    ],
    "add_transaction": [
        "add a transaction",
        "add expense",
        "log a purchase",
        "I bought something",
        "record spending",
        "add new expense",
        "I spent money on",
        "log expense",
        "create transaction",
    ],
    "edit_transaction": [
        "edit my transaction",
        "change my last transaction",
        "update transaction",
        "modify transaction",
        "fix my transaction",
        "correct the amount",
        "change the category",
    ],
    "delete_transaction": [
        "delete my transaction",
        "remove transaction",
        "delete my last transaction",
        "cancel transaction",
        "remove expense",
        "delete the expense",
    ],
    "query_spending": [
        "how much did I spend on",
        "what did I spend on food",
        "spending on transportation",
        "how much for groceries",
        "category spending",
        "spending by category",
        "total spent on",
    ],
    "categorize_help": [
        "what category is",
        "which category for",
        "how do I categorize",
        "category for Uber",
        "what category should I use",
        "help me categorize",
    ],
    "budget_status": [
        "am I over budget",
        "budget status",
        "how is my budget",
        "check my budget",
        "am I within budget",
        "budget remaining",
        "how much budget left",
    ],
    "get_insights": [
        "spending insights",
        "analyze my spending",
        "spending patterns",
        "unusual spending",
        "spending analysis",
        "financial insights",
    ],
    "help": [
        "help",
        "what can you do",
        "how do I use this",
        "commands",
        "what are my options",
        "show me what you can do",
    ],
}


# =============================================================================
# INTENT CLASSIFIER CLASS
# =============================================================================


class IntentClassifier:
    """
    Semantic similarity-based intent classifier using MiniLM.

    Uses sentence embeddings to match user input to predefined intents.
    More robust than keyword matching - understands meaning, not just words.

    Attributes:
        model: SentenceTransformer model instance
        intent_embeddings: Pre-computed embeddings for intent examples
        is_initialized: Whether model is loaded

    Example:
        >>> classifier = IntentClassifier()
        >>> classifier.initialize()
        >>> intent, conf = classifier.classify("show my spending")
        >>> print(f"{intent}: {conf:.2f}")
        summarize_transactions: 0.87
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern for memory efficiency."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_done = False
        return cls._instance

    def __init__(self):
        """Initialize classifier (model loaded lazily)."""
        if self._init_done:
            return

        self.model = None
        self.intent_embeddings: Dict[str, np.ndarray] = {}
        self.is_initialized = False
        self._use_fallback = False  # True when sentence-transformers unavailable
        self._init_done = True
        logger.debug("IntentClassifier instance created (not yet initialized)")

    def initialize(self) -> bool:
        """
        Load MiniLM model and pre-compute intent embeddings.

        Returns:
            True if initialization successful, False if fallback mode

        Notes:
            If sentence-transformers is not installed, falls back to
            keyword-based matching (lower accuracy but works).
        """
        if self.is_initialized:
            return True

        # Check if intent classifier is disabled via config
        try:
            from app.core.config import get_config

            config = get_config()
            if (
                hasattr(config, "AI_INTENT_CLASSIFIER_ENABLED")
                and not config.AI_INTENT_CLASSIFIER_ENABLED
            ):
                logger.info(
                    "Intent classifier disabled via AI_INTENT_CLASSIFIER_ENABLED=0"
                )
                self.is_initialized = True
                self._use_fallback = True
                return True
        except Exception:
            pass  # Config not available, continue with normal init

        try:
            logger.info(f"Loading intent classifier model: {MODEL_NAME}")

            # Import here to allow graceful failure if not installed
            from sentence_transformers import SentenceTransformer

            # Load model
            self.model = SentenceTransformer(MODEL_NAME)

            # Pre-compute embeddings for all intent examples
            logger.info("Pre-computing intent embeddings...")
            for intent, examples in INTENT_EXAMPLES.items():
                embeddings = self.model.encode(examples, convert_to_numpy=True)
                # Store mean embedding for each intent
                self.intent_embeddings[intent] = np.mean(embeddings, axis=0)

            self.is_initialized = True
            self._use_fallback = False
            logger.info(
                f"Intent classifier initialized with {len(INTENT_EXAMPLES)} intents"
            )
            return True

        except ImportError as e:
            logger.warning(
                "sentence-transformers not installed. "
                "Using keyword-based fallback for intent detection. "
                "For better accuracy, run: pip install sentence-transformers"
            )
            self.is_initialized = True
            self._use_fallback = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize intent classifier: {e}", exc_info=True)
            # Still mark as initialized to avoid repeated failures
            self.is_initialized = True
            self._use_fallback = True
            return False

    def classify(self, text: str) -> Tuple[str, float]:
        """
        Classify user text into an intent.

        Args:
            text: User's input message

        Returns:
            Tuple of (intent_name, confidence_score)
            confidence_score is 0.0 to 1.0

        Example:
            >>> intent, conf = classifier.classify("how much did I spend")
            >>> print(intent, conf)
            query_spending 0.85
        """
        if not self.is_initialized:
            self.initialize()

        # Use keyword-based fallback if model unavailable
        if self._use_fallback:
            return self._classify_by_keywords(text)

        try:
            # Embed user input
            user_embedding = self.model.encode(text, convert_to_numpy=True)

            # Find most similar intent
            best_intent = None
            best_score = -1.0

            for intent, intent_emb in self.intent_embeddings.items():
                # Cosine similarity
                similarity = self._cosine_similarity(user_embedding, intent_emb)
                if similarity > best_score:
                    best_score = similarity
                    best_intent = intent

            # Convert similarity to confidence (0-1 range)
            confidence = max(0.0, min(1.0, best_score))

            logger.debug(
                f"Intent classification: '{text}' → {best_intent} ({confidence:.2f})"
            )

            return best_intent, confidence

        except Exception as e:
            logger.error(f"Intent classification error: {e}", exc_info=True)
            return "general_chat", 0.0

    def classify_with_alternatives(
        self, text: str, top_k: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Get top-k intent predictions with confidence scores.

        Useful when primary intent is uncertain and user needs options.

        Args:
            text: User's input message
            top_k: Number of top intents to return

        Returns:
            List of (intent_name, confidence_score) tuples, sorted by confidence
        """
        if not self.is_initialized:
            self.initialize()

        # Use keyword fallback if model unavailable
        if self._use_fallback:
            primary = self._classify_by_keywords(text)
            return [primary]  # Fallback only returns single result

        try:
            user_embedding = self.model.encode(text, convert_to_numpy=True)

            scores = []
            for intent, intent_emb in self.intent_embeddings.items():
                similarity = self._cosine_similarity(user_embedding, intent_emb)
                confidence = max(0.0, min(1.0, similarity))
                scores.append((intent, confidence))

            # Sort by confidence descending
            scores.sort(key=lambda x: x[1], reverse=True)

            return scores[:top_k]

        except Exception as e:
            logger.error(f"Intent classification error: {e}", exc_info=True)
            return [("general_chat", 0.0)]

    def embed_text(self, text: str) -> np.ndarray:
        """
        Get embedding vector for text.

        Useful for RAG, similarity search, and other embedding-based tasks.

        Args:
            text: Text to embed

        Returns:
            384-dimensional numpy array

        Raises:
            RuntimeError: If using fallback mode (model not available)
        """
        if not self.is_initialized:
            self.initialize()

        if self._use_fallback:
            raise RuntimeError(
                "embed_text requires sentence-transformers. "
                "Install with: pip install sentence-transformers"
            )

        return self.model.encode(text, convert_to_numpy=True)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Get embedding vectors for multiple texts.

        More efficient than calling embed_text multiple times.

        Args:
            texts: List of texts to embed

        Returns:
            2D numpy array of shape (len(texts), 384)

        Raises:
            RuntimeError: If using fallback mode (model not available)
        """
        if not self.is_initialized:
            self.initialize()

        if self._use_fallback:
            raise RuntimeError(
                "embed_batch requires sentence-transformers. "
                "Install with: pip install sentence-transformers"
            )

        return self.model.encode(texts, convert_to_numpy=True)

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.

        Uses sentence_transformers.util.cos_sim for efficiency when available.
        """
        try:
            from app.ai.utils import cos_sim

            return cos_sim(a, b)
        except ImportError:
            # Fallback to manual computation
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return float(np.dot(a, b) / (norm_a * norm_b))

    def _classify_by_keywords(self, text: str) -> Tuple[str, float]:
        """
        Keyword-based fallback when MiniLM model is unavailable.

        Less accurate than semantic matching but works without dependencies.

        Args:
            text: User's input message

        Returns:
            Tuple of (intent_name, confidence_score)
        """
        text_lower = text.lower()

        # Keyword patterns for each intent (ordered by specificity)
        keyword_patterns = {
            "add_transaction": [
                "add",
                "spent",
                "paid",
                "bought",
                "purchase",
                "expense",
                "received",
                "earned",
                "income",
                "got paid",
                "deposit",
            ],
            "categorize_transaction": [
                "categorize",
                "category",
                "classify",
                "what type",
                "label",
            ],
            "set_budget": ["budget", "limit", "spending limit", "set limit", "cap"],
            "summarize_transactions": [
                "summary",
                "summarize",
                "overview",
                "report",
                "total",
                "spending",
                "how much",
                "spent this",
                "show my",
            ],
            "get_insights": [
                "insight",
                "analyze",
                "pattern",
                "trend",
                "habit",
                "advice",
                "suggest",
                "recommend",
                "tips",
            ],
            "help": ["help", "what can you", "how do i", "guide", "tutorial"],
        }

        # Check each pattern
        best_intent = "general_chat"
        best_score = 0

        for intent, keywords in keyword_patterns.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > best_score:
                best_score = matches
                best_intent = intent

        # Confidence based on keyword matches (lower than semantic matching)
        confidence = min(0.7, 0.3 + (best_score * 0.15))

        logger.debug(
            f"Keyword fallback: '{text}' → {best_intent} "
            f"({best_score} matches, {confidence:.2f} conf)"
        )

        return best_intent, confidence

    def get_info(self) -> Dict[str, Any]:
        """Get classifier status and info."""
        return {
            "model": MODEL_NAME if not self._use_fallback else "keyword_fallback",
            "is_initialized": self.is_initialized,
            "using_fallback": self._use_fallback,
            "num_intents": len(INTENT_EXAMPLES),
            "intents": list(INTENT_EXAMPLES.keys()),
            "confidence_threshold": CONFIDENCE_THRESHOLD,
        }


# =============================================================================
# SINGLETON ACCESSOR
# =============================================================================

_classifier: Optional[IntentClassifier] = None


def get_intent_classifier() -> IntentClassifier:
    """Get the intent classifier singleton."""
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier()
    return _classifier


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "IntentClassifier",
    "get_intent_classifier",
    "INTENT_EXAMPLES",
    "CONFIDENCE_THRESHOLD",
]
