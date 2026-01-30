# =============================================================================
# Digital Finance Tracker - Model Router
# PURPOSE: Route requests to the appropriate AI model
# =============================================================================
"""
Model Router Module

Central router that directs requests to the appropriate AI model based on task:
- DistilBERT: Transaction categorization (fine-tuned model)
- MiniLM: Intent detection, semantic search, embeddings
- Gemini: Fallback, complex chat, entity extraction

Why Model Router?
    - Clean separation of concerns
    - Easy to add/swap models
    - Consistent interface for all AI tasks
    - Memory-efficient model loading

Usage:
    from app.ai.model_router import ModelRouter, get_model_router

    router = get_model_router()

    # Categorize a transaction
    result = router.categorize("Starbucks Coffee")
    # {"category": "Food & Dining", "confidence": 0.95, "source": "distilbert"}

    # Detect intent from user message
    intent, conf = router.detect_intent("show my spending")
    # ("summarize_transactions", 0.87)

    # Get text embedding for RAG
    embedding = router.embed("lunch at subway")
    # numpy array of shape (384,)

Architecture:
    ┌──────────────────────────────────────────────────────────┐
    │                      MODEL ROUTER                        │
    ├──────────────────────────────────────────────────────────┤
    │                                                          │
    │  categorize() ──────────► DistilBERT (fine-tuned)       │
    │                              ↓ (if <70%)                │
    │                           Gemini (fallback)             │
    │                                                          │
    │  detect_intent() ───────► MiniLM (semantic matching)    │
    │                                                          │
    │  embed() ───────────────► MiniLM (384-dim vectors)      │
    │                                                          │
    │  extract_entities() ────► Gemini (NLP parsing)          │
    │                                                          │
    │  chat() ────────────────► Gemini (conversation)         │
    │                                                          │
    └──────────────────────────────────────────────────────────┘
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
import threading
import numpy as np

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

# Confidence thresholds
CATEGORIZATION_THRESHOLD = 0.99  # Below this, use Gemini fallback
INTENT_THRESHOLD = 0.70  # Below this, intent is uncertain


# =============================================================================
# MODEL ROUTER CLASS
# =============================================================================


class ModelRouter:
    """
    Routes AI requests to appropriate models.

    Provides a unified interface for all AI operations while internally
    routing to specialized models for each task.

    Models:
        - categorizer: DistilBERT for transaction categorization
        - intent_classifier: MiniLM for intent detection
        - gemini: Gemini API for fallback and complex tasks

    Attributes:
        categorizer: Transaction categorization model
        intent_classifier: Intent detection model
        gemini: Gemini API client
        guardrails: Scope enforcement
        is_initialized: Whether all models are ready

    Example:
        >>> router = ModelRouter()
        >>> router.initialize()
        >>> result = router.categorize("Shell Gas Station")
        >>> print(result["category"], result["source"])
        Transportation distilbert
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
        """Initialize router (models loaded lazily)."""
        if self._init_done:
            return

        self.categorizer = None
        self.intent_classifier = None
        self.gemini = None
        self.guardrails = None
        self.is_initialized = False
        self._init_done = True
        logger.debug("ModelRouter instance created")

    def initialize(self, preload_models: bool = True) -> bool:
        """
        Initialize all AI models.

        Args:
            preload_models: If True, load models into memory immediately.
                           If False, load on first use (lazy loading).

        Returns:
            True if initialization successful
        """
        if self.is_initialized:
            return True

        try:
            logger.info("Initializing ModelRouter...")

            # Import components
            from app.ai.categorizer import get_categorizer
            from app.ai.intent_classifier import get_intent_classifier
            from app.ai.gemini_client import get_gemini_client
            from app.ai.guardrails import get_guardrails

            self.categorizer = get_categorizer()
            self.intent_classifier = get_intent_classifier()
            self.gemini = get_gemini_client()
            self.guardrails = get_guardrails()

            if preload_models:
                # Preload intent classifier (lighter, used more often)
                logger.info("Preloading MiniLM intent classifier...")
                self.intent_classifier.initialize()

                # Preload categorizer (uses load_model, not initialize)
                logger.info("Preloading DistilBERT categorizer...")
                self.categorizer.load_model()

                # Initialize Gemini client
                logger.info("Initializing Gemini client...")
                self.gemini.initialize()

                # Initialize guardrails
                logger.info("Initializing guardrails...")
                self.guardrails.initialize()

            self.is_initialized = True
            logger.info("ModelRouter initialized successfully")
            return True

        except Exception as e:
            logger.error(f"ModelRouter initialization failed: {e}", exc_info=True)
            return False

    # =========================================================================
    # CATEGORIZATION (DistilBERT → Gemini fallback)
    # =========================================================================

    def categorize(
        self,
        merchant_name: str,
        amount: Optional[float] = None,
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Categorize a transaction using DistilBERT with Gemini fallback.

        Args:
            merchant_name: Merchant/payee name
            amount: Transaction amount (optional, helps with context)
            user_id: User ID for personalized predictions (optional)

        Returns:
            Dictionary with category, confidence, source, needs_clarification

        Returns:
            Dictionary with:
                - category: Category name
                - category_id: Category UUID
                - confidence: 0.0 to 1.0
                - source: "distilbert" | "gemini" | "keyword"
                - needs_clarification: True if confidence < 50%
        """
        if not self.is_initialized:
            self.initialize()

        try:
            # Try DistilBERT first
            result = self.categorizer.predict(merchant_name)

            if result["confidence"] >= CATEGORIZATION_THRESHOLD:
                result["source"] = "distilbert"
                return result

            # Fall back to Gemini if low confidence
            logger.debug(
                f"DistilBERT confidence low ({result['confidence']:.2f}), "
                f"falling back to Gemini"
            )

            gemini_result = self.gemini.categorize_transaction(
                merchant_name=merchant_name,
                amount=amount,
            )

            if gemini_result["confidence"] >= result["confidence"]:
                gemini_result["source"] = "gemini"
                return gemini_result

            # Return DistilBERT result if still better
            result["source"] = "distilbert"
            return result

        except Exception as e:
            logger.error(f"Categorization failed: {e}", exc_info=True)
            return {
                "category": "Unknown",
                "category_id": None,
                "confidence": 0.0,
                "source": "error",
                "needs_clarification": True,
                "error": str(e),
            }

    # =========================================================================
    # INTENT DETECTION (MiniLM)
    # =========================================================================

    def detect_intent(self, text: str) -> Tuple[str, float]:
        """
        Detect user intent from natural language.

        Uses MiniLM semantic similarity for robust intent matching.

        Args:
            text: User's input message

        Returns:
            Tuple of (intent_name, confidence_score)

        Intents:
            - summarize_transactions
            - show_transactions
            - add_transaction
            - edit_transaction
            - delete_transaction
            - query_spending
            - categorize_help
            - budget_status
            - help
        """
        if not self.is_initialized:
            self.initialize()

        return self.intent_classifier.classify(text)

    def detect_intent_with_alternatives(
        self, text: str, top_k: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Get top-k intent predictions.

        Useful when primary intent is uncertain.

        Args:
            text: User's input message
            top_k: Number of alternatives to return

        Returns:
            List of (intent, confidence) tuples
        """
        if not self.is_initialized:
            self.initialize()

        return self.intent_classifier.classify_with_alternatives(text, top_k)

    # =========================================================================
    # EMBEDDINGS (MiniLM)
    # =========================================================================

    def embed(self, text: str) -> np.ndarray:
        """
        Get embedding vector for text.

        Used for RAG, similarity search, semantic matching.

        Args:
            text: Text to embed

        Returns:
            384-dimensional numpy array
        """
        if not self.is_initialized:
            self.initialize()

        return self.intent_classifier.embed_text(text)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Get embeddings for multiple texts.

        More efficient than calling embed() multiple times.

        Args:
            texts: List of texts to embed

        Returns:
            2D numpy array of shape (len(texts), 384)
        """
        if not self.is_initialized:
            self.initialize()

        return self.intent_classifier.embed_batch(texts)

    # =========================================================================
    # ENTITY EXTRACTION (Gemini)
    # =========================================================================

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract transaction entities from natural language.

        Uses Gemini for complex NLP parsing.

        Args:
            text: User's input (e.g., "Add $50 for lunch at Subway yesterday")

        Returns:
            Dictionary with extracted entities:
                - amount: Decimal amount
                - merchant: Merchant name
                - category: Category suggestion
                - date: Parsed date
                - description: Any description
                - is_expense: True for expense, False for income
        """
        if not self.is_initialized:
            self.initialize()

        return self.gemini.extract_transaction_entities(text)

    # =========================================================================
    # SCOPE CHECK (Guardrails)
    # =========================================================================

    def check_scope(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Check if request is within finance scope.

        Args:
            text: User's input message

        Returns:
            Tuple of (is_in_scope, error_message_if_not)
        """
        if not self.is_initialized:
            self.initialize()

        return self.guardrails.check_scope(text)

    # =========================================================================
    # CHAT (Gemini)
    # =========================================================================

    def chat(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate chat response using Gemini.

        Args:
            message: User's message
            context: Optional context (user data, conversation history)

        Returns:
            AI-generated response string
        """
        if not self.is_initialized:
            self.initialize()

        return self.gemini.chat(message, context)

    # =========================================================================
    # STATUS
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get status of all models."""
        status = {
            "is_initialized": self.is_initialized,
            "models": {},
        }

        if self.categorizer:
            try:
                status["models"]["categorizer"] = self.categorizer.get_info()
            except Exception as e:
                status["models"]["categorizer"] = {"error": str(e)}

        if self.intent_classifier:
            try:
                status["models"]["intent_classifier"] = self.intent_classifier.get_info()
            except Exception as e:
                status["models"]["intent_classifier"] = {"error": str(e)}

        if self.gemini:
            try:
                status["models"]["gemini"] = self.gemini.get_status()
            except Exception as e:
                status["models"]["gemini"] = {"error": str(e)}

        if self.guardrails:
            try:
                status["models"]["guardrails"] = self.guardrails.get_info()
            except Exception as e:
                status["models"]["guardrails"] = {"error": str(e)}

        return status


# =============================================================================
# SINGLETON ACCESSOR
# =============================================================================

_router: Optional[ModelRouter] = None


def get_model_router() -> ModelRouter:
    """Get the model router singleton."""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "ModelRouter",
    "get_model_router",
    "CATEGORIZATION_THRESHOLD",
    "INTENT_THRESHOLD",
]
