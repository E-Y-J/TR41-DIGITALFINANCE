# =============================================================================
# Digital Finance Tracker - Intent Classifier Tests
# PURPOSE: Unit tests for MiniLM-based intent detection
# =============================================================================
"""
Unit tests for IntentClassifier.

Tests focus on the configuration and structure that can be tested without
loading actual ML models. For integration tests with real model,
see tests/integration/ai/.
"""

import pytest
from unittest.mock import MagicMock


class TestIntentClassifier:
    """Test suite for IntentClassifier class."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        import app.ai.intent_classifier as classifier_module
        from app.ai.intent_classifier import IntentClassifier
        classifier_module._classifier = None
        IntentClassifier._instance = None
        yield
        classifier_module._classifier = None
        IntentClassifier._instance = None

    # =========================================================================
    # CLASS EXISTENCE TESTS
    # =========================================================================

    def test_intent_classifier_class_exists(self):
        """Test that IntentClassifier class exists."""
        from app.ai.intent_classifier import IntentClassifier
        assert IntentClassifier is not None

    def test_get_intent_classifier_function_exists(self):
        """Test that get_intent_classifier function exists."""
        from app.ai.intent_classifier import get_intent_classifier
        assert callable(get_intent_classifier)

    # =========================================================================
    # INTENT DEFINITIONS TESTS
    # =========================================================================

    def test_intent_examples_defined(self):
        """Test that INTENT_EXAMPLES constant is defined."""
        from app.ai.intent_classifier import INTENT_EXAMPLES

        assert INTENT_EXAMPLES is not None
        assert len(INTENT_EXAMPLES) > 0

    def test_all_intents_have_examples(self):
        """Test that all intents have example phrases."""
        from app.ai.intent_classifier import INTENT_EXAMPLES

        for intent, examples in INTENT_EXAMPLES.items():
            assert isinstance(intent, str)
            assert len(examples) >= 1, f"Intent '{intent}' needs examples"

    def test_required_intents_exist(self):
        """Test that required intents are defined."""
        from app.ai.intent_classifier import INTENT_EXAMPLES

        required = [
            "summarize_transactions",
            "add_transaction",
            "query_spending",
        ]

        for intent in required:
            assert intent in INTENT_EXAMPLES, f"Missing required intent: {intent}"

    # =========================================================================
    # METHOD EXISTENCE TESTS
    # =========================================================================

    def test_has_classify_method_exists(self):
        """Test that classify method exists."""
        from app.ai.intent_classifier import IntentClassifier

        classifier = IntentClassifier()
        assert hasattr(classifier, 'classify')
        assert callable(classifier.classify)

    def test_has_classify_with_alternatives_method(self):
        """Test that classify_with_alternatives method exists."""
        from app.ai.intent_classifier import IntentClassifier

        classifier = IntentClassifier()
        assert hasattr(classifier, 'classify_with_alternatives')
        assert callable(classifier.classify_with_alternatives)

    def test_has_initialize_method(self):
        """Test that initialize method exists."""
        from app.ai.intent_classifier import IntentClassifier

        classifier = IntentClassifier()
        assert hasattr(classifier, 'initialize')
        assert callable(classifier.initialize)


class TestIntentClassifierSingleton:
    """Test singleton behavior of IntentClassifier."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        import app.ai.intent_classifier as classifier_module
        from app.ai.intent_classifier import IntentClassifier
        classifier_module._classifier = None
        IntentClassifier._instance = None
        yield
        classifier_module._classifier = None
        IntentClassifier._instance = None

    def test_get_intent_classifier_returns_same_instance(self):
        """Test that get_intent_classifier returns singleton."""
        from app.ai.intent_classifier import get_intent_classifier

        instance1 = get_intent_classifier()
        instance2 = get_intent_classifier()

        assert instance1 is instance2


class TestIntentExamples:
    """Test intent examples are well-formed."""

    def test_examples_are_strings(self):
        """Test that all examples are non-empty strings."""
        from app.ai.intent_classifier import INTENT_EXAMPLES

        for intent, examples in INTENT_EXAMPLES.items():
            for example in examples:
                assert isinstance(example, str), \
                    f"Example for '{intent}' should be string"
                assert len(example) > 0, \
                    f"Example for '{intent}' should not be empty"

    def test_examples_are_natural_language(self):
        """Test that examples look like natural language."""
        from app.ai.intent_classifier import INTENT_EXAMPLES

        for intent, examples in INTENT_EXAMPLES.items():
            for example in examples:
                # Should have reasonable length
                assert len(example) >= 3, \
                    f"Example '{example}' for '{intent}' too short"


class TestIntentClassifierConfiguration:
    """Test configuration constants."""

    def test_model_name_defined(self):
        """Test that model name is defined."""
        from app.ai.intent_classifier import MODEL_NAME

        assert MODEL_NAME is not None
        assert isinstance(MODEL_NAME, str)
        assert len(MODEL_NAME) > 0

    def test_confidence_threshold_defined(self):
        """Test that confidence threshold is defined."""
        from app.ai.intent_classifier import CONFIDENCE_THRESHOLD

        assert CONFIDENCE_THRESHOLD is not None
        assert 0.0 < CONFIDENCE_THRESHOLD < 1.0
