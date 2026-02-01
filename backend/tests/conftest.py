# tests/conftest.py
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
    """
    u = User(
        auth0_id=f"test-auth0-{uuid.uuid4()}",
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