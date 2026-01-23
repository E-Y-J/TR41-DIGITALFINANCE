# =============================================================================
# Digital Finance Tracker - AI Service Facade
# PURPOSE: Clean interface for AI operations - Microservice-ready design
# =============================================================================
"""
AI Service Facade

This module provides a clean, unified interface for all AI operations.
Designed for easy extraction into a separate microservice in the future.

MICROSERVICE-READY DESIGN:
    This facade abstracts all AI functionality behind simple function calls.
    To convert to microservice later:
    1. Deploy AI models in separate container
    2. Replace these functions with HTTP/gRPC calls
    3. No changes needed in calling code (services, routes)

Current Implementation (Embedded):
    - Direct function calls to AI modules
    - Models loaded in Flask process memory
    - ~1.5GB RAM for all models

Future Implementation (Microservice):
    - HTTP calls to AI service: http://ai-service:8001/api/v1/...
    - AI service has its own Docker container
    - Flask app uses minimal memory

Usage:
    from app.ai.service import AIService

    # Get singleton
    ai = AIService.get_instance()

    # Categorize transaction
    result = ai.categorize("Starbucks")

    # Detect intent
    intent, conf = ai.detect_intent("show my spending")

    # Check scope
    in_scope, msg = ai.check_scope("how do I make bread?")

Metrics:
    All operations are timed and logged for monitoring.
    Prometheus metrics available via get_metrics().
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# =============================================================================
# METRICS (Simple Implementation - Prometheus-ready)
# =============================================================================


@dataclass
class AIMetrics:
    """
    AI performance metrics.

    Designed to be exported to Prometheus in the future.
    Currently stored in memory.
    """

    # Counters
    categorize_count: int = 0
    intent_count: int = 0
    scope_check_count: int = 0
    embed_count: int = 0

    # Latency tracking (in milliseconds)
    categorize_latency_sum: float = 0.0
    intent_latency_sum: float = 0.0
    scope_check_latency_sum: float = 0.0

    # Error counts
    categorize_errors: int = 0
    intent_errors: int = 0

    # Model status
    models_loaded: bool = False
    load_time_ms: float = 0.0
    last_used: Optional[datetime] = None

    def record_categorize(self, latency_ms: float, error: bool = False):
        """Record a categorize operation."""
        self.categorize_count += 1
        self.categorize_latency_sum += latency_ms
        if error:
            self.categorize_errors += 1
        self.last_used = datetime.now(timezone.utc)

    def record_intent(self, latency_ms: float, error: bool = False):
        """Record an intent detection operation."""
        self.intent_count += 1
        self.intent_latency_sum += latency_ms
        if error:
            self.intent_errors += 1
        self.last_used = datetime.now(timezone.utc)

    def record_scope_check(self, latency_ms: float):
        """Record a scope check operation."""
        self.scope_check_count += 1
        self.scope_check_latency_sum += latency_ms
        self.last_used = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Export metrics as dictionary (Prometheus-ready format)."""
        return {
            "counters": {
                "categorize_total": self.categorize_count,
                "intent_total": self.intent_count,
                "scope_check_total": self.scope_check_count,
                "embed_total": self.embed_count,
                "categorize_errors_total": self.categorize_errors,
                "intent_errors_total": self.intent_errors,
            },
            "latency": {
                "categorize_avg_ms": (
                    self.categorize_latency_sum / self.categorize_count
                    if self.categorize_count > 0
                    else 0
                ),
                "intent_avg_ms": (
                    self.intent_latency_sum / self.intent_count
                    if self.intent_count > 0
                    else 0
                ),
                "scope_check_avg_ms": (
                    self.scope_check_latency_sum / self.scope_check_count
                    if self.scope_check_count > 0
                    else 0
                ),
            },
            "status": {
                "models_loaded": self.models_loaded,
                "load_time_ms": self.load_time_ms,
                "last_used": (
                    self.last_used.isoformat() if self.last_used else None
                ),
            },
        }


# =============================================================================
# AI SERVICE FACADE
# =============================================================================


class AIService:
    """
    Unified AI service facade - Microservice-ready design.

    This class provides a clean interface for all AI operations.
    Internally uses the model router, but this abstraction allows
    easy replacement with HTTP calls when extracting to microservice.

    Thread-safe singleton pattern.

    Attributes:
        router: ModelRouter instance (current implementation)
        metrics: AIMetrics for monitoring
        is_initialized: Whether models are loaded

    Example:
        >>> ai = AIService.get_instance()
        >>> ai.initialize()  # Preload all models
        >>> result = ai.categorize("Shell Gas")
        >>> print(result["category"])
        Transportation
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
        """Initialize service."""
        if self._init_done:
            return

        self.router = None
        self.metrics = AIMetrics()
        self.is_initialized = False
        self._init_done = True
        logger.debug("AIService instance created")

    @classmethod
    def get_instance(cls) -> "AIService":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self, preload: bool = True) -> bool:
        """
        Initialize AI service and optionally preload models.

        Args:
            preload: If True, load all models into memory now.
                    If False, models load on first use (lazy).

        Returns:
            True if initialization successful
        """
        if self.is_initialized:
            return True

        try:
            start_time = time.time()
            logger.info("Initializing AI service...")

            # Import and initialize model router
            from app.ai.model_router import get_model_router

            self.router = get_model_router()

            if preload:
                logger.info("Preloading AI models (this may take 10-15 seconds)...")
                self.router.initialize(preload_models=True)
                logger.info("AI models preloaded successfully")

            load_time = (time.time() - start_time) * 1000
            self.metrics.load_time_ms = load_time
            self.metrics.models_loaded = True
            self.is_initialized = True

            logger.info(f"AI service initialized in {load_time:.0f}ms")
            return True

        except Exception as e:
            logger.error(f"AI service initialization failed: {e}", exc_info=True)
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
        Categorize a transaction.

        MICROSERVICE NOTE:
            In microservice version, this becomes:
            response = requests.post(
                "http://ai-service:8001/api/v1/categorize",
                json={"merchant_name": merchant_name, "amount": amount}
            )
            return response.json()

        Args:
            merchant_name: Merchant/payee name
            amount: Transaction amount (optional)
            user_id: User ID for personalized predictions (optional)

        Returns:
            {
                "category": "Food & Dining",
                "category_id": "uuid-string",
                "confidence": 0.95,
                "source": "distilbert" | "gemini" | "keyword",
                "needs_clarification": False
            }
        """
        if not self.is_initialized:
            self.initialize()

        start_time = time.time()
        error = False

        try:
            result = self.router.categorize(merchant_name, amount, user_id)
            return result
        except Exception as e:
            error = True
            logger.error(f"Categorization failed: {e}", exc_info=True)
            return {
                "category": "Unknown",
                "category_id": None,
                "confidence": 0.0,
                "source": "error",
                "needs_clarification": True,
                "error": str(e),
            }
        finally:
            latency = (time.time() - start_time) * 1000
            self.metrics.record_categorize(latency, error)

    # =========================================================================
    # INTENT DETECTION (MiniLM)
    # =========================================================================

    def detect_intent(self, text: str) -> Tuple[str, float]:
        """
        Detect user intent from natural language.

        MICROSERVICE NOTE:
            In microservice version, this becomes:
            response = requests.post(
                "http://ai-service:8001/api/v1/intent",
                json={"text": text}
            )
            data = response.json()
            return (data["intent"], data["confidence"])

        Args:
            text: User's input message

        Returns:
            Tuple of (intent_name, confidence)
        """
        if not self.is_initialized:
            self.initialize()

        start_time = time.time()
        error = False

        try:
            intent, confidence = self.router.detect_intent(text)
            return intent, confidence
        except Exception as e:
            error = True
            logger.error(f"Intent detection failed: {e}", exc_info=True)
            return "general_chat", 0.0
        finally:
            latency = (time.time() - start_time) * 1000
            self.metrics.record_intent(latency, error)

    def detect_intent_with_alternatives(
        self, text: str, top_k: int = 3
    ) -> List[Tuple[str, float]]:
        """Get top-k intent predictions."""
        if not self.is_initialized:
            self.initialize()

        return self.router.detect_intent_with_alternatives(text, top_k)

    # =========================================================================
    # SCOPE CHECK (Guardrails)
    # =========================================================================

    def check_scope(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Check if request is within finance scope.

        MICROSERVICE NOTE:
            In microservice version, this becomes:
            response = requests.post(
                "http://ai-service:8001/api/v1/scope",
                json={"text": text}
            )
            data = response.json()
            return (data["in_scope"], data.get("message"))

        Args:
            text: User's input message

        Returns:
            Tuple of (is_in_scope, error_message_if_not)
        """
        if not self.is_initialized:
            self.initialize()

        start_time = time.time()

        try:
            result = self.router.check_scope(text)
            return result
        except Exception as e:
            logger.error(f"Scope check failed: {e}", exc_info=True)
            # Default to allowing (fail open for UX)
            return True, None
        finally:
            latency = (time.time() - start_time) * 1000
            self.metrics.record_scope_check(latency)

    # =========================================================================
    # EMBEDDINGS (MiniLM - for RAG)
    # =========================================================================

    def embed(self, text: str) -> List[float]:
        """
        Get embedding vector for text.

        Used for RAG, similarity search, etc.

        Args:
            text: Text to embed

        Returns:
            384-dimensional vector as list
        """
        if not self.is_initialized:
            self.initialize()

        self.metrics.embed_count += 1
        embedding = self.router.embed(text)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts."""
        if not self.is_initialized:
            self.initialize()

        self.metrics.embed_count += len(texts)
        embeddings = self.router.embed_batch(texts)
        return embeddings.tolist()

    # =========================================================================
    # ENTITY EXTRACTION (Gemini)
    # =========================================================================

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract transaction entities from natural language.

        Args:
            text: e.g., "Add $50 for lunch at Subway yesterday"

        Returns:
            {
                "amount": 50.0,
                "merchant": "Subway",
                "category": "Food & Dining",
                "date": "2026-01-21",
                "description": "lunch"
            }
        """
        if not self.is_initialized:
            self.initialize()

        return self.router.extract_entities(text)

    # =========================================================================
    # METRICS & STATUS
    # =========================================================================

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get AI service metrics.

        Prometheus-ready format for future integration.
        """
        return self.metrics.to_dict()

    def get_status(self) -> Dict[str, Any]:
        """Get detailed status of AI service."""
        status = {
            "service": "ai_service",
            "is_initialized": self.is_initialized,
            "metrics": self.get_metrics(),
        }

        if self.router:
            status["models"] = self.router.get_status()

        return status

    def health_check(self) -> Dict[str, Any]:
        """
        Health check for load balancers/k8s.

        Returns simple status for quick checks.
        """
        return {
            "status": "healthy" if self.is_initialized else "initializing",
            "models_loaded": self.metrics.models_loaded,
        }


# =============================================================================
# CONVENIENCE FUNCTIONS (Module-level access)
# =============================================================================


def get_ai_service() -> AIService:
    """Get the AI service singleton."""
    return AIService.get_instance()


def initialize_ai_service(preload: bool = True) -> bool:
    """Initialize AI service (call at app startup)."""
    return get_ai_service().initialize(preload=preload)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "AIService",
    "AIMetrics",
    "get_ai_service",
    "initialize_ai_service",
]
