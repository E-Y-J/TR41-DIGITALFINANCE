# =============================================================================
# Digital Finance Tracker - Foundation Integration Tests
# PURPOSE: Test Categories, Notifications, Alerts, Summary endpoints
# =============================================================================

import pytest
from app import create_app


@pytest.fixture
def app():
    """Create and configure test application."""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestFoundationEndpoints:
    """Tests for Categories, Notifications, Alerts, Summary endpoints."""

    # =========================================================================
    # PUBLIC ENDPOINTS
    # =========================================================================

    def test_test_endpoint(self, client):
        """Test the public test endpoint."""
        response = client.get("/api/test")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    # =========================================================================
    # PROTECTED ENDPOINTS - Should return 401 without auth
    # =========================================================================

    def test_categories_requires_auth(self, client):
        """Test GET /api/categories requires authentication."""
        response = client.get("/api/categories")
        assert response.status_code == 401

    def test_category_by_id_requires_auth(self, client):
        """Test GET /api/categories/<id> requires authentication."""
        response = client.get("/api/categories/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 401

    def test_notifications_requires_auth(self, client):
        """Test GET /api/notifications requires authentication."""
        response = client.get("/api/notifications")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False

    def test_notifications_unread_count_requires_auth(self, client):
        """Test GET /api/notifications/unread-count requires authentication."""
        response = client.get("/api/notifications/unread-count")
        assert response.status_code == 401

    def test_notifications_read_all_requires_auth(self, client):
        """Test PATCH /api/notifications/read-all requires authentication."""
        response = client.patch("/api/notifications/read-all")
        assert response.status_code == 401

    def test_alerts_requires_auth(self, client):
        """Test GET /api/alerts requires authentication."""
        response = client.get("/api/alerts")
        assert response.status_code == 401

    def test_alerts_count_requires_auth(self, client):
        """Test GET /api/alerts/count requires authentication."""
        response = client.get("/api/alerts/count")
        assert response.status_code == 401

    def test_summary_weekly_requires_auth(self, client):
        """Test GET /api/summary/weekly requires authentication."""
        response = client.get("/api/summary/weekly")
        assert response.status_code == 401

    def test_summary_monthly_requires_auth(self, client):
        """Test GET /api/summary/monthly requires authentication."""
        response = client.get("/api/summary/monthly")
        assert response.status_code == 401

    def test_summary_category_requires_auth(self, client):
        """Test GET /api/summary/by-category requires authentication."""
        response = client.get("/api/summary/by-category")
        assert response.status_code == 401

    def test_transactions_requires_auth(self, client):
        """Test GET /api/transactions requires authentication."""
        response = client.get("/api/transactions")
        assert response.status_code == 401

    def test_users_me_requires_auth(self, client):
        """Test GET /api/users/me requires authentication."""
        response = client.get("/api/users/me")
        assert response.status_code == 401


class TestCategoryRoutes:
    """Test category-specific routing."""

    def test_categories_endpoint_exists(self, client):
        """Verify categories endpoint is registered (returns 401, not 404)."""
        response = client.get("/api/categories")
        # Should not be 404 (endpoint exists), returns 401 (needs auth)
        assert response.status_code == 401


class TestNotificationRoutes:
    """Test notification-specific routing."""

    def test_notification_read_all_method_not_allowed(self, client):
        """Test that GET is not allowed on read-all endpoint."""
        response = client.get("/api/notifications/read-all")
        assert response.status_code == 405  # Method Not Allowed


class TestAlertRoutes:
    """Test alert-specific routing."""

    def test_alert_dismiss_requires_patch(self, client):
        """Test that GET is not allowed on dismiss endpoint."""
        response = client.get(
            "/api/alerts/00000000-0000-0000-0000-000000000000/dismiss"
        )
        assert response.status_code == 405  # Method Not Allowed
