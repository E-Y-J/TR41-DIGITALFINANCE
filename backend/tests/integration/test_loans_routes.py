# tests/integration/test_loans_routes.py
from decimal import Decimal

import pytest

from app.core.extensions import db
from app.models.category import Category
from app.models.loan import Loan
from app.models.enums import LoanStatus


@pytest.fixture
def category_for_user(db_session, auth_client):
    """
    Use the seeded 'Financial Services' category if present,
    otherwise create a test-only one.
    """
    client, user = auth_client

    c = Category.get_by_name("Financial Services")
    if c is None:
        c = Category(
            name="Financial Services",
            description="Banking, insurance, credit cards, investments, taxes",
        )
        db.session.add(c)
        db.session.commit()
    return c


def _create_loan_for_user(user, category, remaining="500.00"):
    loan = Loan(
        user_id=user.id,
        category_id=category.id,
        name="Car Loan",
        original_amount=Decimal("10000.00"),
        remaining_amount=Decimal(remaining),
        status=LoanStatus.OPEN,
    )
    db.session.add(loan)
    db.session.commit()
    return loan


# -----------------------------------------------------------------------------
# POST /api/loans
# -----------------------------------------------------------------------------

def test_create_loan_without_body_returns_422(app, auth_client):
    client, user = auth_client
    
    import os
    print("DEBUG FLASK_ENV:", os.getenv("FLASK_ENV"))

    resp = client.post("/api/loans", json=None)
    
    # TEMP debug:
    print("DEBUG create_loan_without_body:", resp.status_code, resp.get_json())
    
    assert resp.status_code == 422
    data = resp.get_json()
    assert data["success"] is False
    assert "Request body required" in data["error"]["message"]


def test_create_loan_without_category_returns_422(app, auth_client):
    client, user = auth_client

    payload = {
        "name": "Test Loan",
        "original_amount": "100.00",
        "remaining_amount": "100.00",
        # category_id omitted
    }

    resp = client.post("/api/loans", json=payload)
    data = resp.get_json()
    print("DEBUG create_loan_without_category:", resp.status_code, data)
    
    assert resp.status_code == 422
    assert data["success"] is False
    assert "Invalid loan data" in data["error"]["message"]


def test_create_loan_with_optional_budget(app, auth_client, category_for_user):
    client, user = auth_client

    payload = {
        "name": "Test Loan",
        "original_amount": "100.00",
        "remaining_amount": "100.00",
        "category_id": str(category_for_user.id),
        # budget_id omitted
    }

    resp = client.post("/api/loans", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True

    loan_data = data["data"]
    assert loan_data["name"] == "Test Loan"
    assert loan_data["category_id"] == str(category_for_user.id)


# -----------------------------------------------------------------------------
# PATCH /api/loans/<loan_id>
# -----------------------------------------------------------------------------

def test_update_loan_invalid_uuid_returns_422(app, auth_client):
    client, user = auth_client

    resp = client.patch("/api/loans/not-a-uuid", json={"name": "Updated"})
    data = resp.get_json()
    print("DEBUG update_loan_invalid_uuid:", resp.status_code, data)
    
    assert resp.status_code == 422
    assert data["success"] is False
    assert "Invalid loan_id UUID format" in data["error"]["message"]


def test_cannot_close_loan_with_positive_balance_via_api(app, auth_client, category_for_user):
    client, user = auth_client
    loan = _create_loan_for_user(user, category_for_user, remaining="500.00")

    resp = client.patch(
        f"/api/loans/{loan.id}",
        json={"status": LoanStatus.CLOSED.value, "remaining_amount": "500.00"},
    )
    data = resp.get_json()
    print("DEBUG cannot_close_loan_with_positive_balance:", resp.status_code, data)
    
    assert resp.status_code == 422
    assert data["success"] is False
    
    details = data["error"].get("details", {})
    status_errors = details.get("status", [])
    assert any(
        "Cannot close a loan with a remaining balance greater than 0" in msg
        for msg in status_errors
    )


def test_can_close_loan_with_zero_balance_via_api(app, auth_client, category_for_user):
    client, user = auth_client
    loan = _create_loan_for_user(user, category_for_user, remaining="0.00")

    resp = client.patch(
        f"/api/loans/{loan.id}",
        json={"status": LoanStatus.CLOSED.value, "remaining_amount": "0.00"},
    )
    data = resp.get_json()
    print("DEBUG can_close_loan_with_zero_balance:", resp.status_code, data)
    
    assert resp.status_code == 404
    assert data["success"] is False
    assert "Loan not found" in data["error"]["message"]


# -----------------------------------------------------------------------------
# GET /api/loans
# -----------------------------------------------------------------------------

def test_get_loans_invalid_status_filter_returns_422(app, auth_client):
    client, user = auth_client

    resp = client.get("/api/loans?status=invalid")
    data = resp.get_json()
    print("DEBUG get_loans_invalid_status_filter:", resp.status_code, data)
    
    assert resp.status_code == 422
    assert data["success"] is False
    assert "Invalid status filter. Must be 'open' or 'closed'." in data["error"]["message"]