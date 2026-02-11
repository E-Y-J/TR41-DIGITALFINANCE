# =============================================================================
# Digital Finance Tracker - AI Categorizer
# PURPOSE: Business logic wrapper for transaction categorization
# =============================================================================
"""
AI Categorizer Module

This module provides the business logic wrapper around the raw inference engine.
It handles singleton pattern, confidence thresholds, batch processing, and
Gemini fallback integration.

Architecture:
    inference.py    → Raw DistilBERT model inference (Jae's domain)
    categorizer.py  → Business logic wrapper (this file)

Usage:
    from app.ai.categorizer import get_categorizer

    categorizer = get_categorizer()
    result = categorizer.predict("McDonald's #1234")
    # {"category": "Food & Dining", "confidence": 0.95}

Notes:
    - Wraps inference.py for raw model predictions
    - Singleton pattern ensures model loaded once
    - Applies confidence thresholds
    - Thread-safe for concurrent requests
"""

import os
import logging
from typing import Dict, Any, List, Optional
import threading

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

# Import centralized constants
try:
    from app.ai.constants import (
        SYSTEM_CATEGORIES,
        ConfidenceThresholds,
        CATEGORY_KEYWORDS,
    )

    CONFIDENCE_THRESHOLD = ConfidenceThresholds.CATEGORY_HIGH
except ImportError:
    # Fallback if constants.py not available
    CONFIDENCE_THRESHOLD = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.80"))
    SYSTEM_CATEGORIES = [
        "Charity & Donations",
        "Entertainment & Recreation",
        "Financial Services",
        "Food & Dining",
        "Government & Legal",
        "Healthcare & Medical",
        "Income",
        "Shopping & Retail",
        "Transportation",
        "Utilities & Services",
    ]
    CATEGORY_KEYWORDS = {}


# =============================================================================
# TRANSACTION CATEGORIZER CLASS
# =============================================================================


class TransactionCategorizer:
    """
    Business logic wrapper for transaction categorization.

    Wraps the raw inference engine (inference.py) and adds:
    - Singleton pattern
    - Confidence thresholds
    - Batch processing
    - Error handling
    - API contract consistency

    Example:
        >>> categorizer = TransactionCategorizer()
        >>> result = categorizer.predict("Starbucks Coffee")
        >>> print(f"{result['category']}: {result['confidence']:.2f}")
        Food & Dining: 0.96
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern - only one instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the categorizer."""
        if self._initialized:
            return

        self._classifier = None  # Raw inference engine
        self.is_loaded = False
        self._initialized = True

    @property
    def is_ready(self) -> bool:
        """
        Check if the categorizer is ready for inference.

        Returns:
            True if model is loaded and ready, False otherwise
        """
        return self.is_loaded and self._classifier is not None

    def load_model(self) -> bool:
        """
        Load the inference engine.

        Returns:
            True if model loaded successfully, False otherwise
        """
        if self.is_loaded:
            logger.info("Model already loaded, skipping...")
            return True

        try:
            from app.ai.inference import TransactionClassifier

            logger.info("Loading TransactionClassifier from inference.py...")
            self._classifier = TransactionClassifier()
            self.is_loaded = True
            logger.info("TransactionClassifier loaded successfully")
            return True

        except FileNotFoundError as e:
            logger.warning(f"Model files not found: {e}")
            return False
        except ImportError as e:
            logger.error(f"Import error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            return False

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict category for a single transaction.

        Args:
            text: Transaction description (merchant name, etc.)

        Returns:
            Dictionary with prediction results:
            {
                "category": "Food & Dining",
                "confidence": 0.95,
                "raw_label": "Food & Dining"
            }

        Example:
            >>> result = categorizer.predict("Amazon.com Purchase")
            >>> result["category"]
            "Shopping & Retail"
        """
        if not self.is_loaded:
            if not self.load_model():
                return {
                    "category": "Unknown",
                    "confidence": 0.0,
                    "error": "Model not loaded",
                }

        try:
            # Call raw inference
            label, confidence = self._classifier.predict(text)

            # Apply confidence threshold
            if confidence < CONFIDENCE_THRESHOLD:
                category = "Unknown"
            else:
                category = label

            return {
                "category": category,
                "confidence": round(confidence, 4),
                "raw_label": label,
            }

        except Exception as e:
            logger.error(f"Prediction failed for '{text}': {e}", exc_info=True)
            return {
                "category": "Unknown",
                "confidence": 0.0,
                "error": str(e),
            }

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Predict categories for multiple transactions.

        Args:
            texts: List of transaction descriptions

        Returns:
            List of prediction dictionaries

        Example:
            >>> results = categorizer.predict_batch(["Uber", "Netflix"])
            >>> [r["category"] for r in results]
            ["Transportation", "Entertainment & Recreation"]
        """
        if not self.is_loaded:
            if not self.load_model():
                return [
                    {"text": t, "category": "Unknown", "confidence": 0.0} for t in texts
                ]

        results = []
        for text in texts:
            result = self.predict(text)
            result["text"] = text
            results.append(result)

        return results

    def get_top_k_predictions(self, text: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Get top-k category predictions for uncertain cases.

        Args:
            text: Transaction description
            k: Number of top predictions to return

        Returns:
            List of top-k predictions sorted by probability
        """
        # For now, just return the single prediction
        # TODO: Extend inference.py to support top-k
        result = self.predict(text)
        return [
            {
                "category": result.get("raw_label", result["category"]),
                "probability": result["confidence"],
            }
        ]

    def is_model_available(self) -> bool:
        """Check if model can be loaded."""
        try:
            from pathlib import Path

            model_path = Path(__file__).parent / "transaction_classification_model"
            return model_path.exists()
        except Exception:
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "is_loaded": self.is_loaded,
            "model_type": "distilbert-sequence-classification",
            "inference_module": "inference.py",
            "confidence_threshold": CONFIDENCE_THRESHOLD,
            "categories": SYSTEM_CATEGORIES,
            "num_categories": len(SYSTEM_CATEGORIES),
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_categorizer: Optional[TransactionCategorizer] = None


def get_categorizer() -> TransactionCategorizer:
    """
    Get the singleton TransactionCategorizer instance.

    Returns:
        TransactionCategorizer instance (creates if not exists)

    Example:
        >>> from app.ai.categorizer import get_categorizer
        >>> categorizer = get_categorizer()
        >>> result = categorizer.predict("Starbucks")
    """
    global _categorizer
    if _categorizer is None:
        _categorizer = TransactionCategorizer()
    return _categorizer


def initialize_categorizer() -> bool:
    """
    Initialize the categorizer and load the model.

    Should be called at application startup.

    Returns:
        True if successful, False otherwise
    """
    categorizer = get_categorizer()
    return categorizer.load_model()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "TransactionCategorizer",
    "get_categorizer",
    "initialize_categorizer",
    "SYSTEM_CATEGORIES",
    "CONFIDENCE_THRESHOLD",
]
