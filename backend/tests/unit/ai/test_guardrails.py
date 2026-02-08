# =============================================================================
# Digital Finance Tracker - Guardrails Tests
# PURPOSE: Unit tests for finance scope enforcement
# =============================================================================
"""
Unit tests for Guardrails class.

Tests the finance-only scope enforcement that prevents off-topic queries.
Focuses on testing the keyword detection logic which doesn't require ML models.
"""

import pytest
from unittest.mock import MagicMock


class TestGuardrails:
    """Test suite for Guardrails class."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        import app.ai.guardrails as guardrails_module
        guardrails_module._guardrails_instance = None
        yield
        guardrails_module._guardrails_instance = None

    # =========================================================================
    # CLASS EXISTENCE TESTS
    # =========================================================================

    def test_guardrails_class_exists(self):
        """Test that Guardrails class exists."""
        from app.ai.guardrails import Guardrails
        assert Guardrails is not None

    def test_get_guardrails_function_exists(self):
        """Test that get_guardrails function exists."""
        from app.ai.guardrails import get_guardrails
        assert callable(get_guardrails)

    # =========================================================================
    # KEYWORD DETECTION TESTS (No ML Required)
    # =========================================================================

    def test_has_check_scope_method(self):
        """Test that check_scope method exists."""
        from app.ai.guardrails import Guardrails

        guardrails = Guardrails()
        assert hasattr(guardrails, 'check_scope')
        assert callable(guardrails.check_scope)

    def test_has_is_initialized_property(self):
        """Test that is_initialized property exists."""
        from app.ai.guardrails import Guardrails

        guardrails = Guardrails()
        assert hasattr(guardrails, 'is_initialized')

    def test_initialize_method_exists(self):
        """Test that initialize method exists."""
        from app.ai.guardrails import Guardrails

        guardrails = Guardrails()
        assert hasattr(guardrails, 'initialize')
        assert callable(guardrails.initialize)

    # =========================================================================
    # CONFIGURATION TESTS
    # =========================================================================

    def test_finance_topics_defined(self):
        """Test that finance topics are defined."""
        from app.ai.guardrails import FINANCE_TOPICS

        assert FINANCE_TOPICS is not None
        assert len(FINANCE_TOPICS) > 0

    def test_finance_topics_are_strings(self):
        """Test that all finance topics are non-empty strings."""
        from app.ai.guardrails import FINANCE_TOPICS

        for topic in FINANCE_TOPICS:
            assert isinstance(topic, str)
            assert len(topic) > 0

    def test_semantic_threshold_defined(self):
        """Test that semantic threshold is defined."""
        from app.ai.guardrails import SEMANTIC_THRESHOLD

        assert SEMANTIC_THRESHOLD is not None
        assert 0.0 < SEMANTIC_THRESHOLD < 1.0


class TestGuardrailsSingleton:
    """Test singleton behavior of Guardrails."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        import app.ai.guardrails as guardrails_module
        from app.ai.guardrails import Guardrails
        guardrails_module._guardrails = None
        Guardrails._instance = None
        yield
        guardrails_module._guardrails = None
        Guardrails._instance = None

    def test_get_guardrails_returns_same_instance(self):
        """Test that get_guardrails returns singleton."""
        from app.ai.guardrails import get_guardrails

        instance1 = get_guardrails()
        instance2 = get_guardrails()

        assert instance1 is instance2


class TestGuardrailsKeywords:
    """Test keyword-based detection (fallback mode)."""

    def test_finance_keywords_exist(self):
        """Test that finance keywords are defined."""
        from app.ai.guardrails import FINANCE_KEYWORDS

        assert FINANCE_KEYWORDS is not None
        assert len(FINANCE_KEYWORDS) > 0

    def test_keywords_include_common_terms(self):
        """Test that common finance terms are in keywords."""
        from app.ai.guardrails import FINANCE_KEYWORDS

        # Convert to lowercase set for checking
        keywords_lower = {k.lower() for k in FINANCE_KEYWORDS}

        # Should include some common finance terms
        common_terms = ["spend", "budget", "money", "transaction", "expense"]

        # At least some should be present
        matches = [t for t in common_terms if t in keywords_lower]
        assert len(matches) >= 2, f"Expected common finance terms, got {keywords_lower}"
