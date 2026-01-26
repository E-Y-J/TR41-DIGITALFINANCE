# =============================================================================
# Digital Finance Tracker - AI Orchestrator
# PURPOSE: Coordinate tiered AI categorization (HuggingFace → Gemini → Unknown)
# =============================================================================
"""
AI Orchestrator Module

This module coordinates the AI categorization pipeline:
1. Try HuggingFace model (local, free, fast)
2. If confidence < 70%, try Gemini API (cloud, free tier)
3. If confidence < 50%, mark as Unknown (requires user clarification)

Confidence Thresholds:
    - HUGGINGFACE_THRESHOLD (70%): Below this, fallback to Gemini
    - UNKNOWN_THRESHOLD (50%): Below this, mark as Unknown

Usage:
    from app.ai.orchestrator import AIOrchestrator, get_orchestrator

    # Get singleton instance
    orchestrator = get_orchestrator()

    # Categorize a transaction
    result = orchestrator.categorize("McDonald's #1234")
    # {
    #     "category": "Food & Dining",
    #     "category_id": "uuid-string",
    #     "confidence": 0.95,
    #     "source": "huggingface",
    #     "needs_clarification": False
    # }

Notes:
    - Thread-safe for concurrent requests
    - Graceful degradation if AI services unavailable
    - Falls back to keyword matching if all AI fails
"""

import logging
from typing import Dict, Any, Optional, Tuple
from uuid import UUID
import threading

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIDENCE THRESHOLDS
# =============================================================================

HUGGINGFACE_THRESHOLD = 0.70  # Below this, try Gemini
UNKNOWN_THRESHOLD = 0.50  # Below this, mark as Unknown


# =============================================================================
# AI ORCHESTRATOR CLASS
# =============================================================================


class AIOrchestrator:
    """
    Orchestrates AI categorization with tiered fallback.

    Flow:
        1. Keyword matching (instant, rule-based)
        2. HuggingFace model (local AI)
        3. Gemini API (cloud AI fallback)
        4. Unknown (needs user clarification)

    Attributes:
        categorizer: HuggingFace model instance
        gemini: Gemini API client instance
        is_initialized: Whether services are initialized

    Example:
        >>> orchestrator = AIOrchestrator()
        >>> orchestrator.initialize()
        >>> result = orchestrator.categorize("Shell Gas Station")
        >>> print(f"{result['category']} ({result['source']})")
        Transportation (huggingface)
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
        """Initialize the orchestrator."""
        if hasattr(self, "_init_done") and self._init_done:
            return

        self.categorizer = None
        self.gemini = None
        self.is_initialized = False
        self._category_cache: Dict[str, UUID] = {}  # name -> id mapping

        self._init_done = True

    def initialize(self) -> Dict[str, bool]:
        """
        Initialize all AI services.

        Returns:
            Dictionary with initialization status for each service

        Example:
            >>> status = orchestrator.initialize()
            >>> status
            {"huggingface": True, "gemini": True, "keyword": True}
        """
        if self.is_initialized:
            return self._get_status()

        results = {
            "huggingface": False,
            "gemini": False,
            "keyword": True,  # Always available
        }

        # Initialize HuggingFace categorizer
        try:
            from app.ai.categorizer import get_categorizer

            self.categorizer = get_categorizer()
            if self.categorizer.is_model_available():
                results["huggingface"] = self.categorizer.load_model()
            else:
                logger.warning(
                    "HuggingFace model not found in model_store. "
                    "Run: python -m app.ai.download_model"
                )
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace: {e}", exc_info=True)

        # Initialize Gemini client
        try:
            from app.ai.gemini_client import get_gemini_client

            self.gemini = get_gemini_client()
            results["gemini"] = self.gemini.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}", exc_info=True)

        # Load category cache
        self._load_category_cache()

        self.is_initialized = True
        logger.info(f"AI Orchestrator initialized: {results}")

        return results

    def _load_category_cache(self):
        """Load category name to ID mapping from database."""
        try:
            from app.models.category import Category

            categories = Category.query.all()
            self._category_cache = {cat.name: cat.id for cat in categories}
            logger.info(f"Loaded {len(self._category_cache)} categories into cache")
        except Exception as e:
            logger.error(f"Failed to load category cache: {e}", exc_info=True)

    def _get_category_id(self, category_name: str) -> Optional[UUID]:
        """Get category ID from name."""
        if not self._category_cache:
            self._load_category_cache()
        return self._category_cache.get(category_name)

    def categorize(
        self,
        merchant_name: str,
        amount: Optional[float] = None,
        description: Optional[str] = None,
        transaction_type: Optional[str] = None,
        user_id: Optional[UUID] = None,
        skip_keyword: bool = False,
        skip_learned: bool = False,
    ) -> Dict[str, Any]:
        """
        Categorize a transaction using the tiered AI approach.

        Categorization Flow (in order of priority):
        1. User Learned: Check if user has corrected this merchant before
        2. Keyword Match: Fast rule-based matching
        3. HuggingFace: Local zero-shot classification
        4. Gemini: Cloud API fallback
        5. Unknown: Low confidence, needs user clarification

        Args:
            merchant_name: Name of the merchant/payee
            amount: Transaction amount (helps with context)
            description: Additional description
            transaction_type: "income" or "expense"
            user_id: User's UUID (for personalized learning)
            skip_keyword: Skip keyword matching (for testing AI)
            skip_learned: Skip user learned mappings (for testing AI)

        Returns:
            Dictionary with categorization result:
            {
                "category": "Food & Dining",
                "category_id": "uuid-string" or None,
                "confidence": 0.95,
                "source": "user_learned" | "keyword" | "huggingface" | "gemini" | "unknown",
                "needs_clarification": False,
                "alternatives": []  # Top alternatives if uncertain
            }

        Example:
            >>> result = orchestrator.categorize("AMZN Mktp US", amount=50.00)
            >>> result
            {
                "category": "Shopping & Retail",
                "category_id": "...",
                "confidence": 0.92,
                "source": "huggingface",
                "needs_clarification": False
            }
        """
        if not self.is_initialized:
            self.initialize()

        # Prepare result structure
        result = {
            "category": "Unknown",
            "category_id": None,
            "confidence": 0.0,
            "source": "unknown",
            "needs_clarification": True,
            "alternatives": [],
            "reasoning": None,
        }

        # Step 0: Check user-learned mappings (highest priority)
        if user_id and not skip_learned:
            learned_result = self._try_user_learned(user_id, merchant_name)
            if learned_result and learned_result["confidence"] >= 0.9:
                return learned_result

        # Step 1: Try keyword matching (fastest)
        if not skip_keyword:
            keyword_result = self._try_keyword_matching(merchant_name)
            if keyword_result["confidence"] >= 1.0:
                return keyword_result

        # Step 2: Try HuggingFace model
        hf_result = self._try_huggingface(merchant_name)
        if hf_result and hf_result["confidence"] >= HUGGINGFACE_THRESHOLD:
            return hf_result

        # Step 3: Try Gemini if HuggingFace confidence is low
        if hf_result and hf_result["confidence"] >= UNKNOWN_THRESHOLD:
            # HuggingFace gave a decent answer, use it but note lower confidence
            return hf_result

        gemini_result = self._try_gemini(
            merchant_name, amount, description, transaction_type
        )
        if gemini_result and gemini_result["confidence"] >= UNKNOWN_THRESHOLD:
            return gemini_result

        # Step 4: Return best available result or Unknown
        # Prefer HuggingFace result even with low confidence
        if hf_result and hf_result["confidence"] > 0:
            hf_result["needs_clarification"] = True
            # Get alternatives for user to choose
            hf_result["alternatives"] = self._get_alternatives(merchant_name)
            return hf_result

        if gemini_result and gemini_result["confidence"] > 0:
            gemini_result["needs_clarification"] = True
            gemini_result["alternatives"] = self._get_alternatives(merchant_name)
            return gemini_result

        # Complete failure - mark as Unknown
        result["category_id"] = self._get_category_id("Unknown")
        result["alternatives"] = self._get_all_categories()
        return result

    def _try_user_learned(
        self, user_id: UUID, merchant_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check user-learned merchant mappings.

        This checks if the user has previously corrected a similar merchant,
        giving priority to personalized learning over generic AI.
        """
        try:
            from app.ai.user_learning import get_learning_engine

            engine = get_learning_engine()
            learned = engine.get_learned_category(user_id, merchant_name)

            if learned:
                category_name, confidence, source = learned
                return {
                    "category": category_name,
                    "category_id": self._get_category_id(category_name),
                    "confidence": confidence,
                    "source": source,  # "user_learned" or "global_learned"
                    "needs_clarification": False,
                    "alternatives": [],
                    "reasoning": "Learned from your previous categorizations",
                }
        except Exception as e:
            logger.error(f"User learning lookup failed: {e}", exc_info=True)

        return None

    def record_user_correction(
        self,
        user_id: UUID,
        merchant_name: str,
        correct_category: str,
        original_category: Optional[str] = None,
        original_source: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record a user's category correction for learning.

        Call this when a user changes the AI-assigned category.

        Args:
            user_id: User making the correction
            merchant_name: Merchant name from transaction
            correct_category: The category user selected
            original_category: What AI originally predicted
            original_source: Where original prediction came from

        Returns:
            Dictionary with learning update details
        """
        try:
            from app.ai.user_learning import get_learning_engine

            engine = get_learning_engine()
            return engine.record_correction(
                user_id=user_id,
                merchant_name=merchant_name,
                correct_category=correct_category,
                original_category=original_category,
                original_source=original_source,
            )
        except Exception as e:
            logger.error(f"Failed to record correction: {e}", exc_info=True)
            return {"learned": False, "error": str(e)}

    def _try_keyword_matching(self, merchant_name: str) -> Dict[str, Any]:
        """Try keyword-based categorization."""
        try:
            from app.services.category_service import CategoryService

            category, confidence = CategoryService.categorize_by_keyword(merchant_name)
            if category:
                return {
                    "category": category.name,
                    "category_id": category.id,
                    "confidence": confidence,
                    "source": "keyword",
                    "needs_clarification": False,
                    "alternatives": [],
                    "reasoning": "Matched by keyword",
                }
        except Exception as e:
            logger.error(f"Keyword matching failed: {e}", exc_info=True)

        return {"confidence": 0.0}

    def _try_huggingface(self, merchant_name: str) -> Optional[Dict[str, Any]]:
        """Try HuggingFace model categorization."""
        if not self.categorizer or not self.categorizer.is_loaded:
            return None

        try:
            prediction = self.categorizer.predict(merchant_name)
            if "error" in prediction:
                return None

            category_name = prediction["category"]
            return {
                "category": category_name,
                "category_id": self._get_category_id(category_name),
                "confidence": prediction["confidence"],
                "source": "huggingface",
                "needs_clarification": prediction["confidence"] < UNKNOWN_THRESHOLD,
                "alternatives": [],
                "reasoning": f"HuggingFace model prediction",
            }
        except Exception as e:
            logger.error(f"HuggingFace prediction failed: {e}", exc_info=True)
            return None

    def _try_gemini(
        self,
        merchant_name: str,
        amount: Optional[float],
        description: Optional[str],
        transaction_type: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        """Try Gemini API categorization."""
        if not self.gemini or not self.gemini.is_initialized:
            return None

        try:
            prediction = self.gemini.categorize_transaction(
                merchant_name=merchant_name,
                amount=amount,
                description=description,
                transaction_type=transaction_type,
            )
            if "error" in prediction:
                return None

            category_name = prediction["category"]
            return {
                "category": category_name,
                "category_id": self._get_category_id(category_name),
                "confidence": prediction["confidence"],
                "source": "gemini",
                "needs_clarification": prediction["confidence"] < UNKNOWN_THRESHOLD,
                "alternatives": [],
                "reasoning": prediction.get("reasoning", "Gemini API prediction"),
            }
        except Exception as e:
            logger.error(f"Gemini prediction failed: {e}", exc_info=True)
            return None

    def _get_alternatives(self, merchant_name: str, k: int = 3) -> list:
        """Get alternative category suggestions."""
        if self.categorizer and self.categorizer.is_loaded:
            try:
                top_k = self.categorizer.get_top_k_predictions(merchant_name, k=k)
                return [
                    {
                        "category": p["category"],
                        "category_id": str(self._get_category_id(p["category"])),
                        "probability": p["probability"],
                    }
                    for p in top_k
                ]
            except Exception as e:
                logger.error(f"Failed to get alternatives: {e}")

        return self._get_all_categories()

    def _get_all_categories(self) -> list:
        """Get all available categories as options."""
        return [
            {"category": name, "category_id": str(cat_id)}
            for name, cat_id in self._category_cache.items()
            if name != "Unknown"
        ]

    def _get_status(self) -> Dict[str, bool]:
        """Get current service status."""
        return {
            "huggingface": bool(self.categorizer and self.categorizer.is_loaded),
            "gemini": bool(self.gemini and self.gemini.is_initialized),
            "keyword": True,
        }

    def get_info(self) -> Dict[str, Any]:
        """Get detailed orchestrator info."""
        info = {
            "is_initialized": self.is_initialized,
            "services": self._get_status(),
            "thresholds": {
                "huggingface_threshold": HUGGINGFACE_THRESHOLD,
                "unknown_threshold": UNKNOWN_THRESHOLD,
            },
            "categories_cached": len(self._category_cache),
        }

        if self.categorizer:
            info["huggingface_info"] = self.categorizer.get_model_info()

        if self.gemini:
            info["gemini_info"] = self.gemini.get_status()

        return info


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_orchestrator: Optional[AIOrchestrator] = None


def get_orchestrator() -> AIOrchestrator:
    """
    Get the singleton AIOrchestrator instance.

    Returns:
        AIOrchestrator instance (creates if not exists)
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AIOrchestrator()
    return _orchestrator


def initialize_ai() -> Dict[str, bool]:
    """
    Initialize all AI services.

    Should be called at application startup.

    Returns:
        Dictionary with initialization status for each service
    """
    orchestrator = get_orchestrator()
    return orchestrator.initialize()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "AIOrchestrator",
    "get_orchestrator",
    "initialize_ai",
    "HUGGINGFACE_THRESHOLD",
    "UNKNOWN_THRESHOLD",
]
