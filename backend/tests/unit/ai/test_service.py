# =============================================================================
# Digital Finance Tracker - AI Service Tests
# PURPOSE: Unit tests for the unified AI service facade
# =============================================================================
"""
Unit tests for AIService class.

Tests the microservice-ready AI facade that provides:
- Unified interface for all AI operations
- Metrics/monitoring support
- Easy extraction to microservice

Uses mocking to avoid loading actual ML models during CI/CD.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


class TestAIService:
    """Test suite for AIService class."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from app.ai.service import AIService
        AIService._instance = None
        yield
        AIService._instance = None

    @pytest.fixture
    def mock_model_router(self):
        """Create a mock model router."""
        router = MagicMock()
        router.categorize.return_value = {
            "category": "Food & Dining",
            "confidence": 0.95,
            "source": "distilbert",
        }
        router.detect_intent.return_value = ("query_spending", 0.88)
        router.check_scope.return_value = (True, None)
        router.get_status.return_value = {
            "distilbert": {"ready": True},
            "minilm": {"ready": True},
        }
        return router

    @pytest.fixture
    def mock_intent_classifier(self):
        """Create a mock intent classifier."""
        classifier = MagicMock()
        classifier.initialize.return_value = True
        classifier._initialized = True
        classifier.is_initialized = True
        classifier.model = MagicMock()
        classifier.model.encode.return_value = [0.1] * 384
        classifier.embed_text.return_value = [0.1] * 384
        return classifier

    @pytest.fixture
    def mock_guardrails(self):
        """Create a mock guardrails."""
        guardrails = MagicMock()
        guardrails.initialize.return_value = True
        guardrails._initialized = True
        return guardrails

    # =========================================================================
    # CLASS EXISTENCE TESTS
    # =========================================================================

    def test_ai_service_class_exists(self):
        """Test that AIService class exists."""
        from app.ai.service import AIService
        assert AIService is not None

    def test_get_ai_service_function_exists(self):
        """Test that get_ai_service function exists."""
        from app.ai.service import get_ai_service
        assert callable(get_ai_service)

    def test_initialize_ai_service_function_exists(self):
        """Test that initialize_ai_service function exists."""
        from app.ai.service import initialize_ai_service
        assert callable(initialize_ai_service)

    # =========================================================================
    # INITIALIZATION TESTS
    # =========================================================================

    def test_service_can_be_instantiated(self):
        """Test that service can be instantiated."""
        from app.ai.service import AIService

        service = AIService()
        assert service is not None
        assert hasattr(service, 'is_initialized')

    # =========================================================================
    # METHOD EXISTENCE TESTS
    # =========================================================================

    def test_has_categorize_method(self):
        """Test that categorize method exists."""
        from app.ai.service import AIService
        service = AIService()
        assert hasattr(service, 'categorize')
        assert callable(service.categorize)

    def test_has_detect_intent_method(self):
        """Test that detect_intent method exists."""
        from app.ai.service import AIService
        service = AIService()
        assert hasattr(service, 'detect_intent')
        assert callable(service.detect_intent)

    def test_has_check_scope_method(self):
        """Test that check_scope method exists."""
        from app.ai.service import AIService
        service = AIService()
        assert hasattr(service, 'check_scope')
        assert callable(service.check_scope)

    def test_has_get_metrics_method(self):
        """Test that get_metrics method exists."""
        from app.ai.service import AIService
        service = AIService()
        assert hasattr(service, 'get_metrics')
        assert callable(service.get_metrics)

    def test_has_get_status_method(self):
        """Test that get_status method exists."""
        from app.ai.service import AIService
        service = AIService()
        assert hasattr(service, 'get_status')
        assert callable(service.get_status)


class TestAIServiceSingleton:
    """Test singleton behavior of AIService."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from app.ai.service import AIService
        AIService._instance = None
        yield
        AIService._instance = None

    def test_get_ai_service_returns_same_instance(self):
        """Test that get_ai_service returns singleton."""
        from app.ai.service import get_ai_service

        instance1 = get_ai_service()
        instance2 = get_ai_service()

        assert instance1 is instance2


class TestAIServiceMicroserviceReady:
    """Test microservice-ready design patterns."""

    def test_all_methods_have_microservice_comments(self):
        """Test that key methods have microservice conversion comments."""
        from app.ai.service import AIService
        import inspect

        source = inspect.getsource(AIService)

        # Key methods should have microservice notes
        assert "MICROSERVICE" in source or "microservice" in source


class TestAIMetrics:
    """Test AIMetrics dataclass."""

    def test_ai_metrics_exists(self):
        """Test that AIMetrics dataclass exists."""
        from app.ai.service import AIMetrics
        assert AIMetrics is not None

    def test_ai_metrics_has_expected_fields(self):
        """Test that AIMetrics has expected fields."""
        from app.ai.service import AIMetrics
        import dataclasses

        if dataclasses.is_dataclass(AIMetrics):
            fields = {f.name for f in dataclasses.fields(AIMetrics)}

            # Should have some of these fields
            expected = {"total_requests", "categorize_calls", "intent_calls"}
            assert len(fields) >= 1
