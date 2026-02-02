# =============================================================================
# Digital Finance Tracker - Auth Decorator Unit Tests
# PURPOSE: Unit tests for authentication decorators
# =============================================================================
"""
Auth Decorator Unit Tests

Tests for the @requires_auth and @optional_auth decorators:
- Valid token authentication flow
- Dev impersonation mode (enabled/disabled)
- Production security (no dev headers allowed)
- Invalid token handling
- Optional auth fallback behavior
- Helper functions (get_current_user, is_authenticated)

Testing Strategy:
    - Set FLASK_ENV='production' to bypass testing shortcut and test
      actual auth flow with mocked Auth0 functions
    - Reset to 'testing' after each test to restore normal behavior

Note:
    The decorators have a testing shortcut when FLASK_ENV='testing'
    that bypasses all auth. To test the actual auth flow, we
    temporarily set FLASK_ENV='production' and mock the Auth0 calls.
"""
import os
import pytest
from flask import Flask, g, request
from unittest.mock import patch
from app.auth.decorators import (
    requires_auth,
    optional_auth,
    get_current_user,
    get_current_auth0_id,
    is_authenticated,
    UnauthorizedError,
)

# -------------------------------
# Flask test app
# -------------------------------
app = Flask(__name__)

@pytest.fixture
def client():
    with app.test_request_context():
        yield

# -------------------------------
# Mock helpers
# -------------------------------
def fake_validate_token(token):
    if token == "bad":
        raise UnauthorizedError("Invalid token")
    return {"sub": "auth0|123"}

def fake_get_user_id_from_claims(claims):
    return claims["sub"]

def fake_get_token_from_header(auth_header):
    if not auth_header:
        raise UnauthorizedError("No auth header")
    return auth_header.split(" ")[1]  # simple Bearer split

# -------------------------------
# requires_auth tests
# -------------------------------

@patch("app.auth.decorators.validate_token", side_effect=fake_validate_token)
@patch("app.auth.decorators.get_user_id_from_claims", side_effect=fake_get_user_id_from_claims)
@patch("app.auth.decorators.get_token_from_header", side_effect=fake_get_token_from_header)
def test_requires_auth_valid_token(mock_token, mock_get_id, mock_validate, client):
    # Set to production to bypass testing shortcut and test actual auth flow with mocks
    os.environ["FLASK_ENV"] = "production"

    @requires_auth
    def route():
        return g.auth0_id

    request.headers = {"Authorization": "Bearer good"}
    assert route() == "auth0|123"
    assert g.current_user["sub"] == "auth0|123"
    assert g.access_token == "good"

    # Reset to testing after test
    os.environ["FLASK_ENV"] = "testing"

def test_requires_auth_dev_impersonation_enabled(client):
    os.environ["FLASK_ENV"] = "development"
    os.environ["DEV_IMPERSONATION"] = "true"

    @requires_auth
    def route():
        return g.auth0_id

    request.headers = {"X-Dev-Auth0-Id": "dev|456"}
    assert route() == "dev|456"
    assert g.current_user["sub"] == "dev|456"
    assert g.access_token is None

def test_requires_auth_dev_impersonation_disabled(client):
    os.environ["FLASK_ENV"] = "development"
    os.environ["DEV_IMPERSONATION"] = "false"

    @requires_auth
    def route():
        return "ok"

    # Provide a dummy Authorization header so the token path does not fail
    request.headers = {"X-Dev-Auth0-Id": "dev|456", "Authorization": "Bearer good"}

    with patch("app.auth.decorators.get_token_from_header", side_effect=fake_get_token_from_header):
        with patch("app.auth.decorators.validate_token", side_effect=fake_validate_token):
            with patch("app.auth.decorators.get_user_id_from_claims", side_effect=fake_get_user_id_from_claims):
                result = route()

    # Dev header ignored, normal token path sets g.auth0_id
    assert g.auth0_id == "auth0|123"
    assert result == "ok"

def test_requires_auth_dev_header_in_production(client):
    os.environ["FLASK_ENV"] = "production"
    os.environ["DEV_IMPERSONATION"] = "true"

    @requires_auth
    def route():
        return "ok"

    request.headers = {"X-Dev-Auth0-Id": "dev|456"}
    with pytest.raises(UnauthorizedError):
        route()

def test_requires_auth_invalid_token(client):
    os.environ["FLASK_ENV"] = "production"

    @requires_auth
    def route():
        return "ok"

    request.headers = {"Authorization": "Bearer bad"}
    with patch("app.auth.decorators.validate_token", side_effect=fake_validate_token):
        with patch("app.auth.decorators.get_token_from_header", side_effect=fake_get_token_from_header):
            with pytest.raises(UnauthorizedError):
                route()

# -------------------------------
# optional_auth tests
# -------------------------------

@patch("app.auth.decorators.validate_token", side_effect=fake_validate_token)
@patch("app.auth.decorators.get_user_id_from_claims", side_effect=fake_get_user_id_from_claims)
@patch("app.auth.decorators.get_token_from_header", side_effect=fake_get_token_from_header)
def test_optional_auth_no_token(mock_token, mock_get_id, mock_validate, client):
    @optional_auth
    def route():
        return get_current_auth0_id()

    request.headers = {}
    assert route() is None
    assert g.current_user is None

@patch("app.auth.decorators.validate_token", side_effect=fake_validate_token)
@patch("app.auth.decorators.get_user_id_from_claims", side_effect=fake_get_user_id_from_claims)
@patch("app.auth.decorators.get_token_from_header", side_effect=fake_get_token_from_header)
def test_optional_auth_valid_token(mock_token, mock_get_id, mock_validate, client):
    @optional_auth
    def route():
        return get_current_auth0_id()

    request.headers = {"Authorization": "Bearer good"}
    assert route() == "auth0|123"
    assert g.current_user["sub"] == "auth0|123"

@patch("app.auth.decorators.validate_token", side_effect=lambda t: (_ for _ in ()).throw(Exception("fail")))
@patch("app.auth.decorators.get_token_from_header", side_effect=fake_get_token_from_header)
def test_optional_auth_invalid_token(mock_token, mock_validate, client):
    @optional_auth
    def route():
        return get_current_auth0_id()

    request.headers = {"Authorization": "Bearer bad"}
    # Should not raise, just logs
    assert route() is None
    assert g.current_user is None

# -------------------------------
# helper function tests
# -------------------------------

def test_helper_functions(client):
    g.current_user = {"sub": "auth0|123"}
    g.auth0_id = "auth0|123"
    assert get_current_user() == {"sub": "auth0|123"}
    assert get_current_auth0_id() == "auth0|123"
    assert is_authenticated() is True

    g.current_user = None
    g.auth0_id = None
    assert get_current_user() is None
    assert get_current_auth0_id() is None
    assert is_authenticated() is False
