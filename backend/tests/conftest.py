# =============================================================================
# Digital Finance Tracker - Test Configuration
# PURPOSE: Pytest fixtures for unit and integration tests
# =============================================================================
"""
Test Configuration Module

This module provides shared fixtures for all tests:
- app: Flask application in testing mode
- _db: Database setup/teardown per test session
- db_session: Clean database session per test
- client: Flask test client
- user: Test user matching decorator's testing shortcut
- auth_client: Client + user tuple for authenticated tests

Notes:
    - FLASK_ENV='testing' bypasses Auth0 JWT validation in decorators
    - Test user auth0_id must match decorator's testing shortcut (test|user123)

WARNING:
    When running tests via 'docker compose exec backend pytest', tables are
    dropped after tests complete. This affects the shared dev database.
    Run 'flask db upgrade' after Docker tests to restore tables.
"""

import os
import uuid

import pytest

from app import create_app
from app.core.extensions import db
from app.models.user import User, AccountStatus, UserRole


@pytest.fixture(scope="session")
def app():
    """
    Create the Flask app in testing mode.
    FLASK_ENV='testing' causes requires_auth to bypass JWT.
    """
    os.environ["FLASK_ENV"] = "testing"

    app = create_app("testing")
    app.config["TESTING"] = True

    with app.app_context():
        yield app


@pytest.fixture(scope="session")
def _db(app):
    """
    Create/drop all tables once per session on the test DB.

    WARNING: This fixture drops ALL tables after tests complete.
    When running in Docker, this affects the shared dev database.
    Run 'flask db upgrade' after Docker tests to restore tables.

    Lifecycle:
        1. Drop existing tables (clean slate)
        2. Create all tables from models
        3. Run tests
        4. Drop all tables (cleanup)
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield db
        db.drop_all()


@pytest.fixture(autouse=True)
def db_session(_db):
    """
    Provide a clean session per test: rollback & expunge.
    """
    yield db.session
    db.session.rollback()
    db.session.expunge_all()


@pytest.fixture
def client(app):
    """
    Flask test client.
    """
    return app.test_client()


@pytest.fixture
def user(db_session):
    """
    Create a test user that satisfies User model constraints.
    Uses auth0_id = "test|user123" to match the testing shortcut in decorators.
    """
    # Check if user already exists (from previous test)
    existing = User.query.filter_by(auth0_id="test|user123").first()
    if existing:
        return existing

    u = User(
        auth0_id="test|user123",  # Must match decorator's testing shortcut
        email=f"test-{uuid.uuid4()}@example.com",
        first_name="Test",
        last_name="User",
        nickname="tester",
        account_status=AccountStatus.ACTIVE,
        role=UserRole.USER,
    )
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def auth_client(client, user):
    """
    For tests, just return (client, user).
    Auth is bypassed in requires_auth when FLASK_ENV='testing',
    and loan routes fall back to User.query.first().
    """
    return client, user
