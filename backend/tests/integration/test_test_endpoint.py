# =============================================================================
# Digital Finance Tracker - Test Endpoint Tests
# PURPOSE: Integration tests for the /api/test endpoint
# =============================================================================
"""
Test Endpoint Integration Tests

This module tests the /api/test endpoint used for frontend-backend
connection verification.

Tests:
    - test_endpoint_returns_success: Verify 200 status and correct response format
    - test_endpoint_response_structure: Verify all expected fields are present
    - test_endpoint_no_auth_required: Verify endpoint works without authentication
"""

import pytest

# Note: Uses fixtures from tests/conftest.py (app, client, db_session)


# =============================================================================
# TEST CASES
# =============================================================================


class TestTestEndpoint:
    """Tests for GET /api/test endpoint."""

    def test_endpoint_returns_success(self, client):
        """
        Test that /api/test returns 200 status code.

        Expected:
            - Status code: 200
            - Response contains 'success': True
        """
        response = client.get("/api/test")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_endpoint_response_structure(self, client):
        """
        Test that response has all expected fields.

        Expected response structure:
        {
            "success": true,
            "message": "Hello from backend!",
            "data": {
                "status": "connected",
                "api_version": "1.0.0",
                "service": "digital-finance-api"
            }
        }
        """
        response = client.get("/api/test")
        data = response.get_json()

        # Check top-level fields
        assert "success" in data
        assert "message" in data
        assert "data" in data

        # Check message content
        assert data["message"] == "Hello from backend!"

        # Check data fields
        assert data["data"]["status"] == "connected"
        assert data["data"]["api_version"] == "1.0.0"
        assert data["data"]["service"] == "digital-finance-api"

    def test_endpoint_no_auth_required(self, client):
        """
        Test that endpoint works without authentication header.

        This endpoint is specifically designed to NOT require auth
        so frontend can test connectivity before implementing auth.
        """
        # Make request without any Authorization header
        response = client.get("/api/test")

        # Should succeed without auth
        assert response.status_code == 200
        assert response.get_json()["success"] is True

    def test_endpoint_returns_json(self, client):
        """
        Test that response content type is JSON.

        Expected:
            - Content-Type header contains 'application/json'
        """
        response = client.get("/api/test")

        assert response.content_type == "application/json"

    def test_endpoint_method_not_allowed(self, client):
        """
        Test that POST, PUT, DELETE return 405 Method Not Allowed.

        Only GET method should be allowed.
        """
        # POST should fail
        response = client.post("/api/test")
        assert response.status_code == 405

        # PUT should fail
        response = client.put("/api/test")
        assert response.status_code == 405

        # DELETE should fail
        response = client.delete("/api/test")
        assert response.status_code == 405
