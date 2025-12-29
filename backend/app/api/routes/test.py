# =============================================================================
# Digital Finance Tracker - Test Routes
# PURPOSE: Simple test endpoint for frontend-backend connection verification
# =============================================================================
"""
Test Routes Module

This module provides a simple test endpoint for frontend integration testing.

Purpose:
- Verify frontend can reach the backend API
- Confirm CORS is working correctly
- Validate HTTP client (Axios) configuration
- Test authentication header attachment

Endpoint:
- GET /api/test - Simple connection test (no auth required)

Usage:
    # Register blueprint in app factory
    from app.api.routes.test import bp as test_bp
    app.register_blueprint(test_bp, url_prefix="/api")

Frontend Usage:
    // Using Axios
    const response = await apiClient.get("/test");
    console.log(response.data.message); // "Hello from backend!"
"""

import logging
from flask import Blueprint, jsonify


# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# BLUEPRINT SETUP
# =============================================================================

bp = Blueprint("test", __name__)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def success_response(data=None, message="Success", status_code=200):
    """
    Create a standardized success response.

    Args:
        data: Optional data payload to include in response
        message: Success message string
        status_code: HTTP status code (default 200)

    Returns:
        Tuple of (JSON response, status_code)
    """
    response = {
        "success": True,
        "message": message,
    }
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code


# =============================================================================
# TEST ENDPOINTS
# =============================================================================


@bp.route("/test", methods=["GET"])
def test_connection():
    """
    Simple test endpoint for frontend-backend connection verification.

    This endpoint requires NO authentication and is meant for:
    - Testing API connectivity
    - Verifying CORS configuration
    - Validating HTTP client setup

    Returns:
        200: JSON response with test message

    Response Format:
        {
            "success": true,
            "message": "Hello from backend!",
            "data": {
                "status": "connected",
                "api_version": "1.0.0",
                "service": "digital-finance-api"
            }
        }

    Example:
        # NOTE: Port 8000 matches frontend's apiClient baseURL
        curl http://localhost:8000/api/test

        Response:
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
    logger.info("Test endpoint called - connection verified")

    return success_response(
        data={
            "status": "connected",
            "api_version": "1.0.0",
            "service": "digital-finance-api",
        },
        message="Hello from backend!",
    )
