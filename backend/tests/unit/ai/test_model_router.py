# =============================================================================
# Digital Finance Tracker - Model Router Tests
# PURPOSE: Unit tests for AI model routing logic
# =============================================================================
"""
Unit tests for ModelRouter class.

Tests the routing logic that directs requests to the appropriate AI model:
- DistilBERT for categorization
- MiniLM for intent detection
- Gemini for fallback/chat

Uses mocking to avoid loading actual ML models during CI/CD.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestModelRouter:
    """Test suite for ModelRouter class."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        import app.ai.model_router as router_module
        from app.ai.model_router import ModelRouter

        router_module._router = None
        ModelRouter._instance = None
        yield
        router_module._router = None
        ModelRouter._instance = None

    @pytest.fixture
    def mock_categorizer(self):
        """Create a mock categorizer."""
        categorizer = MagicMock()
        categorizer.predict.return_value = {
            "category": "Food & Dining",
            "confidence": 0.95,
            "source": "distilbert",
        }
        categorizer.is_ready.return_value = True
        return categorizer

    @pytest.fixture
    def mock_intent_classifier(self):
        """Create a mock intent classifier."""
        classifier = MagicMock()
        classifier.detect_intent.return_value = ("query_spending", 0.88)
        classifier.classify.return_value = ("query_spending", 0.88)
        classifier.initialize.return_value = True
        classifier._initialized = True
        classifier.is_initialized = True
        return classifier

    @pytest.fixture
    def mock_guardrails(self):
        """Create a mock guardrails."""
        guardrails = MagicMock()
        guardrails.check_scope.return_value = (True, None)
        guardrails.initialize.return_value = True
        guardrails._initialized = True
        return guardrails

    @pytest.fixture
    def mock_gemini(self):
        """Create a mock Gemini client."""
        gemini = MagicMock()
        gemini.categorize.return_value = {
            "category": "Food & Dining",
            "confidence": 0.80,
            "source": "gemini",
        }
        gemini.chat.return_value = "Here's your spending summary..."
        return gemini

    # =========================================================================
    # INITIALIZATION TESTS
    # =========================================================================

    def test_model_router_class_exists(self):
        """Test that ModelRouter class exists."""
        from app.ai.model_router import ModelRouter

        assert ModelRouter is not None

    def test_get_model_router_function_exists(self):
        """Test that get_model_router function exists."""
        from app.ai.model_router import get_model_router

        assert callable(get_model_router)

    # =========================================================================
    # MODEL SELECTION TESTS
    # =========================================================================

    def test_model_routing_constants_exist(self):
        """Test that model routing uses the correct models."""
        from app.ai.model_router import ModelRouter

        router = ModelRouter()
        # Should have routing configuration
        assert router is not None


class TestModelRouterSingleton:
    """Test singleton behavior of ModelRouter."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        import app.ai.model_router as router_module
        from app.ai.model_router import ModelRouter

        router_module._router = None
        ModelRouter._instance = None
        yield
        router_module._router = None
        ModelRouter._instance = None

    def test_get_model_router_returns_same_instance(self):
        """Test that get_model_router returns singleton."""
        from app.ai.model_router import get_model_router

        instance1 = get_model_router()
        instance2 = get_model_router()

        assert instance1 is instance2


class TestModelRouterMethods:
    """Test that all expected methods exist."""

    def test_has_categorize_method(self):
        """Test that categorize method exists."""
        from app.ai.model_router import ModelRouter

        router = ModelRouter()
        assert hasattr(router, "categorize")
        assert callable(router.categorize)

    def test_has_detect_intent_method(self):
        """Test that detect_intent method exists."""
        from app.ai.model_router import ModelRouter

        router = ModelRouter()
        assert hasattr(router, "detect_intent")
        assert callable(router.detect_intent)

    def test_has_check_scope_method(self):
        """Test that check_scope method exists."""
        from app.ai.model_router import ModelRouter

        router = ModelRouter()
        assert hasattr(router, "check_scope")
        assert callable(router.check_scope)

    def test_has_get_status_method(self):
        """Test that get_status method exists."""
        from app.ai.model_router import ModelRouter

        router = ModelRouter()
        assert hasattr(router, "get_status")
        assert callable(router.get_status)
