# tests/unit/test_loan_schema.py
from uuid import uuid4
from decimal import Decimal

import pytest
from marshmallow import ValidationError

from app.schemas.loan_schema import loan_create_schema, loan_update_schema
from app.models.enums import LoanStatus


def _base_create_payload(**overrides):
    data = {
        "name": "Car Loan",
        "original_amount": "10000.00",
        "remaining_amount": "10000.00",
        "category_id": str(uuid4()),
        # budget_id omitted by default
    }
    data.update(overrides)
    return data


# -----------------------------------------------------------------------------
# LoanCreateSchema tests
# -----------------------------------------------------------------------------


def test_loan_create_requires_category_id():
    payload = _base_create_payload()
    payload.pop("category_id")

    with pytest.raises(ValidationError) as exc:
        loan_create_schema.load(payload)

    errors = exc.value.messages
    assert "category_id" in errors


def test_loan_create_allows_missing_budget_id():
    payload = _base_create_payload()
    result = loan_create_schema.load(payload)

    # budget_id may not be present in result; either way it's optional
    assert "budget_id" not in result or result["budget_id"] is None


def test_loan_create_allows_null_budget_id():
    payload = _base_create_payload(budget_id=None)
    result = loan_create_schema.load(payload)

    assert result["budget_id"] is None


def test_loan_create_status_defaults_to_open():
    payload = _base_create_payload()
    result = loan_create_schema.load(payload)

    assert result["status"] == LoanStatus.OPEN.value


# -----------------------------------------------------------------------------
# LoanUpdateSchema tests
# -----------------------------------------------------------------------------


def test_loan_update_cannot_close_with_positive_balance():
    payload = {
        "status": LoanStatus.CLOSED.value,
        "remaining_amount": "100.00",
    }

    with pytest.raises(ValidationError) as exc:
        loan_update_schema.load(payload)

    errors = exc.value.messages
    assert "status" in errors


def test_loan_update_can_close_with_zero_balance():
    payload = {
        "status": LoanStatus.CLOSED.value,
        "remaining_amount": "0.00",
    }

    result = loan_update_schema.load(payload)

    assert result["status"] == LoanStatus.CLOSED.value
    assert result["remaining_amount"] == Decimal("0.00")
