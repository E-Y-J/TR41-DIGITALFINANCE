# =============================================================================
# Digital Finance Tracker - Foundation Integration Tests
# PURPOSE: Test Categories, Notifications, Alerts, Summary endpoints
# =============================================================================
"""
Foundation Integration Tests

Tests for the core API endpoints (Sprint 1/2 features):
- Categories: GET /api/categories, GET /api/categories/<id>
- Notifications: POST /api/notifications/read-all
- Alerts: PATCH /api/alerts/<id>/dismiss

Testing Strategy:
    - FLASK_ENV='testing' bypasses Auth0 authentication
    - Tests verify endpoint registration and basic behavior
    - Uses fixtures from tests/conftest.py (app, client, db_session)

Note:
    These tests focus on endpoint availability rather than full business
    logic since auth is bypassed in testing mode.
"""

import pytest


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
    # ENDPOINT AVAILABILITY - Verify endpoints are registered
    # =========================================================================

    def test_categories_endpoint_available(self, client, user):
        """Test GET /api/categories is registered."""
        # Note: user fixture ensures test user exists with email
        response = client.get("/api/categories")
        assert response.status_code == 200

    def test_category_by_id_returns_404_for_invalid(self, client):
        """Test GET /api/categories/<id> returns 404 for non-existent category."""
        response = client.get("/api/categories/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404


class TestCategoryRoutes:
    """Test category-specific routing."""

    def test_categories_endpoint_exists(self, client, user):
        """Verify categories endpoint is registered and returns data."""
        # Note: user fixture ensures test user exists with email
        response = client.get("/api/categories")
        assert response.status_code == 200


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
