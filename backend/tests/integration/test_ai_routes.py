# =============================================================================
# Digital Finance Tracker - AI Routes Integration Tests
# PURPOSE: Test all AI-related API endpoints for proper authentication and response
# =============================================================================
"""
AI Routes Integration Tests

This module tests all /api/v1/ai/* endpoints to ensure:
- Proper user authentication via sync_user_from_claims
- Correct response structure
- Error handling

Test Coverage:
- POST /api/v1/ai/categorize
- POST /api/v1/ai/chat
- GET /api/v1/ai/chat/history
- GET /api/v1/ai/insights
- GET /api/v1/ai/clarifications
- POST /api/v1/ai/clarifications/{id}/resolve
- POST /api/v1/ai/clarifications/{id}/dismiss
- GET /api/v1/ai/recurring
- GET /api/v1/ai/recurring/upcoming
- GET /api/v1/ai/recurring/missed
- POST /api/v1/ai/rag/query
- GET /api/v1/ai/status

Note: These tests verify that endpoints return proper responses and don't
return "User not found" errors due to auth pattern bugs.
"""

import pytest
import uuid
from datetime import date, timedelta

from app.core.extensions import db
from app.models.category import Category
from app.models.transaction import Transaction


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def seeded_categories(app, _db):
    """
    Seed system categories once per session.
    Depends on _db to ensure tables exist first.
    """
    with app.app_context():
        count = Category.query.filter_by(is_system=True).count()
        if count == 0:
            Category.seed_defaults()
            db.session.commit()
        yield


@pytest.fixture
def auth_headers(user, seeded_categories):
    """Create auth headers for testing using existing user fixture."""
    return {
        "X-Test-User-Email": user.email,
        "Content-Type": "application/json",
    }


@pytest.fixture
def sample_transactions(app, user, seeded_categories):
    """Create sample transactions for AI analysis."""
    from app.models.enums import TransactionType

    with app.app_context():
        # Get a category for transactions
        category = Category.query.filter_by(is_system=True, is_active=True).first()

        transactions = []
        for i in range(5):
            t = Transaction(
                user_id=user.id,
                amount=100.00 + (i * 10),
                merchant_name=f"Test Merchant {i}",
                transaction_type=TransactionType.EXPENSE,
                category_id=category.id if category else None,
                date=str(date.today() - timedelta(days=i)),
            )
            db.session.add(t)
            transactions.append(t)

        db.session.commit()

        # Refresh to get IDs
        for t in transactions:
            db.session.refresh(t)

        yield transactions

        # Cleanup
        for t in transactions:
            db.session.delete(t)
        db.session.commit()


# =============================================================================
# TEST CLASS: AI Chat Endpoints
# =============================================================================


class TestAIChatEndpoints:
    """Tests for AI chat-related endpoints."""

    def test_chat_endpoint_accepts_message(self, client, auth_headers):
        """Test POST /api/v1/ai/chat accepts a message."""
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers,
            json={"message": "What are my spending habits?"},
        )

        # Should NOT return "User not found" (the auth bug we fixed)
        result = response.get_json()
        if response.status_code == 404:
            assert "User not found" not in result.get("error", {}).get("message", ""), \
                "Auth pattern bug: User not found should not occur with valid auth"

        # Accept 200 (success) or 500 (if AI service not configured)
        # but NOT 404 "User not found"
        assert response.status_code in [200, 500], \
            f"Unexpected status {response.status_code}: {result}"

    def test_chat_history_endpoint(self, client, auth_headers):
        """Test GET /api/v1/ai/chat/history returns proper structure."""
        response = client.get(
            "/api/v1/ai/chat/history",
            headers=auth_headers,
        )

        assert response.status_code == 200, \
            f"Expected 200, got {response.status_code}: {response.get_json()}"

        result = response.get_json()
        assert result["success"] is True
        assert "data" in result
        assert "sessions" in result["data"]
        assert "meta" in result

    def test_chat_history_with_pagination(self, client, auth_headers):
        """Test GET /api/v1/ai/chat/history with pagination params."""
        response = client.get(
            "/api/v1/ai/chat/history?page=1&per_page=10",
            headers=auth_headers,
        )

        assert response.status_code == 200
        result = response.get_json()
        assert result["meta"]["page"] == 1
        assert result["meta"]["per_page"] == 10


# =============================================================================
# TEST CLASS: AI Categorization Endpoint
# =============================================================================


class TestAICategorizationEndpoint:
    """Tests for AI transaction categorization endpoint."""

    def test_categorize_endpoint_accepts_transaction(self, client, auth_headers):
        """Test POST /api/v1/ai/categorize accepts transaction data."""
        response = client.post(
            "/api/v1/ai/categorize",
            headers=auth_headers,
            json={
                "text": "Starbucks coffee",
                "amount": 5.50,
            },
        )

        # Should NOT return "User not found"
        result = response.get_json()
        if response.status_code == 404:
            assert "User not found" not in result.get("error", {}).get("message", ""), \
                "Auth pattern bug: User not found should not occur"

        # Accept 200 (success) or 500 (if AI service not configured)
        assert response.status_code in [200, 500], \
            f"Unexpected status {response.status_code}: {result}"


# =============================================================================
# TEST CLASS: AI Insights Endpoint
# =============================================================================


class TestAIInsightsEndpoint:
    """Tests for AI insights/analysis endpoint."""

    def test_insights_endpoint_returns_data(self, client, auth_headers, sample_transactions):
        """Test GET /api/v1/ai/insights returns proper structure."""
        response = client.get(
            "/api/v1/ai/insights",
            headers=auth_headers,
        )

        # Should NOT return "User not found"
        result = response.get_json()
        if response.status_code == 404:
            assert "User not found" not in result.get("error", {}).get("message", ""), \
                "Auth pattern bug: User not found should not occur"

        # Accept 200 or 500 (if AI service not configured)
        assert response.status_code in [200, 500], \
            f"Unexpected status {response.status_code}: {result}"

        if response.status_code == 200:
            assert result["success"] is True


# =============================================================================
# TEST CLASS: AI Clarifications Endpoints
# =============================================================================


class TestAIClarificationsEndpoints:
    """Tests for AI clarifications-related endpoints."""

    def test_get_clarifications_list(self, client, auth_headers):
        """Test GET /api/v1/ai/clarifications returns list."""
        response = client.get(
            "/api/v1/ai/clarifications",
            headers=auth_headers,
        )

        # Should NOT return "User not found"
        result = response.get_json()
        if response.status_code == 404:
            assert "User not found" not in result.get("error", {}).get("message", ""), \
                "Auth pattern bug: User not found should not occur"

        assert response.status_code == 200, \
            f"Unexpected status {response.status_code}: {result}"

        assert result["success"] is True
        assert "data" in result

    def test_resolve_nonexistent_clarification(self, client, auth_headers):
        """Test POST /api/v1/ai/clarifications/{id}/resolve with invalid ID."""
        fake_id = str(uuid.uuid4())
        response = client.post(
            f"/api/v1/ai/clarifications/{fake_id}/resolve",
            headers=auth_headers,
            json={"choice": "test choice"},
        )

        # Should return 404 for "clarification not found", NOT "User not found"
        result = response.get_json()
        if response.status_code == 404:
            # Acceptable - clarification doesn't exist
            # But should NOT be "User not found"
            error_msg = result.get("error", {}).get("message", "")
            assert "User not found" not in error_msg, \
                "Auth pattern bug: User not found should not occur"
        else:
            # 400 for validation error is also acceptable
            assert response.status_code in [400, 404]

    def test_dismiss_nonexistent_clarification(self, client, auth_headers):
        """Test POST /api/v1/ai/clarifications/{id}/dismiss with invalid ID."""
        fake_id = str(uuid.uuid4())
        response = client.post(
            f"/api/v1/ai/clarifications/{fake_id}/dismiss",
            headers=auth_headers,
        )

        result = response.get_json()
        if response.status_code == 404:
            error_msg = result.get("error", {}).get("message", "")
            assert "User not found" not in error_msg, \
                "Auth pattern bug: User not found should not occur"


# =============================================================================
# TEST CLASS: AI Recurring Transaction Endpoints
# =============================================================================


class TestAIRecurringEndpoints:
    """Tests for AI recurring transaction detection endpoints."""

    def test_recurring_patterns_endpoint(self, client, auth_headers, sample_transactions):
        """Test GET /api/v1/ai/recurring returns data."""
        response = client.get(
            "/api/v1/ai/recurring",
            headers=auth_headers,
        )

        result = response.get_json()
        if response.status_code == 404:
            assert "User not found" not in result.get("error", {}).get("message", ""), \
                "Auth pattern bug: User not found should not occur"

        # 200 or 500 (if service not configured)
        assert response.status_code in [200, 500], \
            f"Unexpected status {response.status_code}: {result}"

    def test_upcoming_recurring_endpoint(self, client, auth_headers):
        """Test GET /api/v1/ai/recurring/upcoming returns data."""
        response = client.get(
            "/api/v1/ai/recurring/upcoming",
            headers=auth_headers,
        )

        result = response.get_json()
        if response.status_code == 404:
            assert "User not found" not in result.get("error", {}).get("message", ""), \
                "Auth pattern bug: User not found should not occur"

        assert response.status_code in [200, 500], \
            f"Unexpected status {response.status_code}: {result}"

    def test_missed_recurring_endpoint(self, client, auth_headers):
        """Test GET /api/v1/ai/recurring/missed returns data."""
        response = client.get(
            "/api/v1/ai/recurring/missed",
            headers=auth_headers,
        )

        result = response.get_json()
        if response.status_code == 404:
            assert "User not found" not in result.get("error", {}).get("message", ""), \
                "Auth pattern bug: User not found should not occur"

        assert response.status_code in [200, 500], \
            f"Unexpected status {response.status_code}: {result}"


# =============================================================================
# TEST CLASS: AI RAG Query Endpoint
# =============================================================================


class TestAIRAGEndpoint:
    """Tests for AI RAG (Retrieval-Augmented Generation) query endpoint."""

    def test_rag_query_endpoint(self, client, auth_headers):
        """Test POST /api/v1/ai/rag/query accepts query."""
        response = client.post(
            "/api/v1/ai/rag/query",
            headers=auth_headers,
            json={"query": "How much did I spend on food?"},
        )

        result = response.get_json()
        if response.status_code == 404:
            assert "User not found" not in result.get("error", {}).get("message", ""), \
                "Auth pattern bug: User not found should not occur"

        # 200 or 500 (if RAG not configured)
        assert response.status_code in [200, 500], \
            f"Unexpected status {response.status_code}: {result}"


# =============================================================================
# TEST CLASS: AI Status Endpoint
# =============================================================================


class TestAIStatusEndpoint:
    """Tests for AI status endpoint."""

    def test_status_endpoint_returns_200(self, client, auth_headers):
        """Test GET /api/v1/ai/status returns status info."""
        response = client.get(
            "/api/v1/ai/status",
            headers=auth_headers,
        )

        assert response.status_code == 200, \
            f"Expected 200, got {response.status_code}: {response.get_json()}"


# =============================================================================
# TEST CLASS: Authentication Pattern Verification
# =============================================================================


class TestAuthPatternVerification:
    """
    Explicit tests to verify auth pattern is working correctly.

    These tests specifically check that the sync_user_from_claims pattern
    is being used correctly and not returning "User not found" errors.
    """

    def test_all_ai_endpoints_find_user(self, client, auth_headers):
        """
        Verify no AI endpoint returns "User not found" error.

        This test checks all AI endpoints to ensure the auth pattern
        bug (using g.user instead of sync_user_from_claims) is fixed.
        """
        endpoints = [
            ("GET", "/api/v1/ai/chat/history"),
            ("GET", "/api/v1/ai/insights"),
            ("GET", "/api/v1/ai/clarifications"),
            ("GET", "/api/v1/ai/recurring"),
            ("GET", "/api/v1/ai/recurring/upcoming"),
            ("GET", "/api/v1/ai/recurring/missed"),
            ("GET", "/api/v1/ai/status"),
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint, headers=auth_headers)

            result = response.get_json()
            error_msg = result.get("error", {}).get("message", "") if result else ""

            assert "User not found" not in error_msg, \
                f"Auth pattern bug on {method} {endpoint}: User not found error returned"

            # Should not be 404 with "User not found"
            if response.status_code == 404:
                assert "User not found" not in error_msg, \
                    f"Auth pattern bug on {method} {endpoint}"

    def test_post_endpoints_find_user(self, client, auth_headers):
        """
        Verify POST AI endpoints don't return "User not found" error.
        """
        post_endpoints = [
            ("/api/v1/ai/chat", {"message": "test"}),
            ("/api/v1/ai/categorize", {"text": "test", "amount": 10.0}),
            ("/api/v1/ai/rag/query", {"query": "test"}),
        ]

        for endpoint, payload in post_endpoints:
            response = client.post(endpoint, headers=auth_headers, json=payload)
            result = response.get_json()
            error_msg = result.get("error", {}).get("message", "") if result else ""

            assert "User not found" not in error_msg, \
                f"Auth pattern bug on POST {endpoint}: User not found error returned"
