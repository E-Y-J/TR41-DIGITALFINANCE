# =============================================================================
# Digital Finance Tracker - AI Module
# PURPOSE: AI-powered features for transaction categorization and insights
# =============================================================================
"""
AI Module Package

This package provides AI-powered features for the Digital Finance Tracker:

Multi-Model Architecture (Sprint 2/3):
    - DistilBERT: Transaction categorization (fine-tuned model)
    - MiniLM: Intent detection, semantic search, embeddings
    - Gemini: Fallback categorization, complex chat, entity extraction

Components:
    - model_router: Routes requests to appropriate model
    - intent_classifier: MiniLM-based intent detection (NEW)
    - guardrails: Finance scope enforcement (NEW)
    - categorizer: HuggingFace DistilBERT for transaction categorization
    - gemini_client: Google Gemini API client for fallback & chat
    - orchestrator: Tiered AI categorization flow
    - anomaly_detector: Spending pattern analysis
    - chat_handler: NLP command parsing for CRUD operations
    - clarification: User clarification flow for low-confidence cases
    - rag: RAG foundation for personalized predictions

Usage:
    from app.ai import initialize_ai, get_model_router

    # Initialize at app startup
    initialize_ai()

    # Use model router for all AI tasks
    router = get_model_router()

    # Categorize transaction
    result = router.categorize("Starbucks Coffee")

    # Detect intent
    intent, confidence = router.detect_intent("show my spending")

    # Check scope
    in_scope, msg = router.check_scope("How do I make bread?")

Models:
    1. DistilBERT (fine-tuned)
       - Purpose: Transaction categorization
       - Size: ~250MB
       - GPU: Not required

    2. MiniLM (sentence-transformers/multi-qa-MiniLM-L6-cos-v1)
       - Purpose: Intent detection, semantic search, RAG embeddings
       - Size: ~80MB
       - GPU: Not required

    3. Gemini (gemini-2.0-flash-lite)
       - Purpose: Fallback, entity extraction, complex chat
       - Free tier: 15 req/min, 1000/day

See: docs/AI_ARCHITECTURE.md for full documentation.

Notes:
    - All services use singleton pattern
    - Thread-safe initialization
    - Lazy loading for memory efficiency
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# =============================================================================
# LAZY IMPORTS
# =============================================================================


def get_ai_service():
    """
    Get the AI service facade (RECOMMENDED entry point).

    The AIService provides a clean, unified interface for all AI operations.
    Designed for easy extraction into a microservice.

    Example:
        >>> ai = get_ai_service()
        >>> ai.initialize()  # Preload models (or call at app startup)
        >>> result = ai.categorize("Starbucks")
        >>> intent, conf = ai.detect_intent("show my spending")
    """
    from app.ai.service import get_ai_service

    return get_ai_service()


def get_model_router():
    """Get the model router singleton (recommended entry point)."""
    from app.ai.model_router import get_model_router

    return get_model_router()


def get_intent_classifier():
    """Get the MiniLM intent classifier singleton."""
    from app.ai.intent_classifier import get_intent_classifier

    return get_intent_classifier()


def get_guardrails():
    """Get the guardrails singleton for scope enforcement."""
    from app.ai.guardrails import get_guardrails

    return get_guardrails()


def get_categorizer():
    """Get the HuggingFace categorizer singleton."""
    from app.ai.categorizer import get_categorizer

    return get_categorizer()


def get_gemini_client():
    """Get the Gemini API client singleton."""
    from app.ai.gemini_client import get_gemini_client

    return get_gemini_client()


def get_orchestrator():
    """Get the AI orchestrator singleton."""
    from app.ai.orchestrator import get_orchestrator

    return get_orchestrator()


def get_detector():
    """Get the anomaly detector singleton."""
    from app.ai.anomaly_detector import get_detector

    return get_detector()


def get_chat_handler():
    """Get the chat handler singleton."""
    from app.ai.chat_handler import get_chat_handler

    return get_chat_handler()


def get_clarification_manager():
    """Get the clarification manager singleton."""
    from app.ai.clarification import get_clarification_manager

    return get_clarification_manager()


def get_learning_engine():
    """Get the user learning engine singleton."""
    from app.ai.user_learning import get_learning_engine

    return get_learning_engine()


def get_rag_engine():
    """Get the RAG engine singleton (foundation only - not fully implemented)."""
    from app.ai.rag import get_rag_engine

    return get_rag_engine()


# =============================================================================
# CLASS EXPORTS (for type hints)
# =============================================================================

# Lazy class imports - only loaded when accessed
def __getattr__(name):
    """Lazy import for classes (avoids loading models at import time)."""
    if name == "AIService":
        from app.ai.service import AIService
        return AIService
    elif name == "ModelRouter":
        from app.ai.model_router import ModelRouter
        return ModelRouter
    elif name == "IntentClassifier":
        from app.ai.intent_classifier import IntentClassifier
        return IntentClassifier
    elif name == "Guardrails":
        from app.ai.guardrails import Guardrails
        return Guardrails
    elif name == "TransactionCategorizer":
        from app.ai.categorizer import TransactionCategorizer
        return TransactionCategorizer
    elif name == "TransactionClassifier":
        from app.ai.inference import TransactionClassifier
        return TransactionClassifier
    raise AttributeError(f"module 'app.ai' has no attribute '{name}'")


# =============================================================================
# INITIALIZATION
# =============================================================================


def initialize_ai(download_model: bool = False) -> bool:
    """
    Initialize all AI components.

    Should be called at application startup for optimal performance.
    Initializes components lazily - heavy models aren't loaded until needed.

    Args:
        download_model: Whether to download HuggingFace model if not present

    Returns:
        True if initialization successful, False otherwise

    Example:
        >>> from app.ai import initialize_ai
        >>> success = initialize_ai()
        >>> print("AI ready!" if success else "AI init failed")
    """
    try:
        logger.info("Initializing AI components...")

        # Initialize orchestrator (which initializes other components)
        orchestrator = get_orchestrator()
        orchestrator.initialize()

        # Initialize chat handler
        chat = get_chat_handler()
        chat.initialize()

        # Initialize anomaly detector
        detector = get_detector()
        detector.initialize()

        logger.info("AI components initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize AI components: {e}", exc_info=True)
        return False


def get_ai_status() -> dict:
    """
    Get status of all AI components.

    Returns:
        Dictionary with status of each component

    Example:
        >>> status = get_ai_status()
        >>> print(status["orchestrator"]["is_ready"])
    """
    status = {}

    try:
        from app.ai.orchestrator import get_orchestrator

        orchestrator = get_orchestrator()
        status["orchestrator"] = orchestrator.get_info()
    except Exception as e:
        status["orchestrator"] = {"error": str(e)}

    try:
        from app.ai.gemini_client import get_gemini_client

        gemini = get_gemini_client()
        status["gemini"] = gemini.get_status()
    except Exception as e:
        status["gemini"] = {"error": str(e)}

    try:
        from app.ai.chat_handler import get_chat_handler

        chat = get_chat_handler()
        status["chat"] = {"is_initialized": chat.is_initialized}
    except Exception as e:
        status["chat"] = {"error": str(e)}

    try:
        from app.ai.anomaly_detector import get_detector

        detector = get_detector()
        status["anomaly_detector"] = {"is_initialized": detector.is_initialized}
    except Exception as e:
        status["anomaly_detector"] = {"error": str(e)}

    try:
        from app.ai.clarification import get_clarification_manager

        manager = get_clarification_manager()
        status["clarifications"] = manager.get_stats()
    except Exception as e:
        status["clarifications"] = {"error": str(e)}

    try:
        from app.ai.user_learning import get_learning_engine

        engine = get_learning_engine()
        status["user_learning"] = engine.get_stats()
    except Exception as e:
        status["user_learning"] = {"error": str(e)}

    try:
        from app.ai.rag import get_rag_engine

        rag = get_rag_engine()
        status["rag"] = rag.get_stats()
    except Exception as e:
        status["rag"] = {"error": str(e)}

    return status


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # NEW: Unified AI Service (RECOMMENDED entry point)
    "get_ai_service",  # Microservice-ready facade with metrics
    "AIService",  # For type hints
    # NEW: Multi-model architecture (Sprint 2/3)
    "get_model_router",  # Main entry point for all AI tasks
    "get_intent_classifier",  # MiniLM intent detection
    "get_guardrails",  # Finance scope enforcement
    "ModelRouter",  # For type hints
    "IntentClassifier",  # For type hints
    "Guardrails",  # For type hints
    # Existing: Getters for singletons
    "get_categorizer",
    "get_gemini_client",
    "get_orchestrator",
    "get_detector",
    "get_chat_handler",
    "get_clarification_manager",
    "get_learning_engine",
    "get_rag_engine",
    # Initialization
    "initialize_ai",
    "get_ai_status",
]
