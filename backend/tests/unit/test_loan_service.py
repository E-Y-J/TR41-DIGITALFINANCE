# tests/unit/test_loan_service.py
import uuid
from decimal import Decimal

import pytest

from app.core.extensions import db
from app.models.user import User, AccountStatus, UserRole
from app.models.category import Category, CategoryType
from app.models.budget import Budget, BudgetType, BudgetPeriod
from app.models.loan import Loan
from app.models.enums import LoanStatus
from app.services.loan_service import LoanService
from app.utils.errors import ValidationError


@pytest.fixture
def service_user(db_session):
    """
    User fixture for service-layer tests.
    Must satisfy NOT NULL + UNIQUE constraints on User.
    """
    u = User(
        auth0_id=f"service-auth0-{uuid.uuid4()}",
        email=f"service-{uuid.uuid4()}@example.com",
        first_name="Service",
        last_name="User",
        nickname="service_tester",
        account_status=AccountStatus.ACTIVE,
        role=UserRole.USER,
    )
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def service_category(db_session):
    """
    Category fixture for service-layer tests.

    Category has:
    - name: unique
    - category_type: NOT NULL
    """
    c = Category(
        name=f"Test Category {uuid.uuid4()}",
        description="Test category for loan service tests",
        category_type=CategoryType.EXPENSE,
        is_system=False,
        display_order=999,
    )
    db.session.add(c)
    db.session.commit()
    return c


@pytest.fixture
def service_budget(db_session, service_user, service_category):
    """
    Budget fixture matching Budget model:
    - user_id: required
    - category_id: optional; we use it
    - budget_type: CATEGORY
    - amount: NOT NULL
    - period: MONTHLY
    """
    b = Budget(
        user_id=service_user.id,
        category_id=service_category.id,
        budget_type=BudgetType.CATEGORY,
        amount=Decimal("1000.00"),
        period=BudgetPeriod.MONTHLY,
        is_active=True,
    )
    db.session.add(b)
    db.session.commit()
    return b


def test_create_loan_requires_category_id(db_session, service_user):
    data = {
        "name": "Car Loan",
        "original_amount": "10000.00",
        "remaining_amount": "10000.00",
        # category_id omitted
    }

    with pytest.raises(ValidationError) as exc:
        LoanService.create(service_user.id, data)

    assert "Invalid loan data" in str(exc.value)


def test_create_loan_allows_missing_budget_id(
    db_session, service_user, service_category
):
    data = {
        "name": "Car Loan",
        "original_amount": "10000.00",
        "remaining_amount": "10000.00",
        "category_id": service_category.id,
        # budget_id omitted
    }

    loan = LoanService.create(service_user.id, data)

    assert isinstance(loan, Loan)
    assert loan.user_id == service_user.id
    assert loan.category_id == service_category.id
    assert loan.budget_id is None
    assert loan.status == LoanStatus.OPEN


def test_create_loan_with_budget(
    db_session, service_user, service_category, service_budget
):
    data = {
        "name": "Car Loan",
        "original_amount": "10000.00",
        "remaining_amount": "10000.00",
        "category_id": service_category.id,
        "budget_id": service_budget.id,
        "status": LoanStatus.CLOSED.value,
    }

    loan = LoanService.create(service_user.id, data)

    assert loan.budget_id == service_budget.id
    # LoanService converts string to LoanStatus enum
    assert loan.status == LoanStatus.CLOSED
    # We do NOT assert on loan.budget_name because Budget has no 'name' column.


def test_update_cannot_close_with_positive_remaining(
    db_session, service_user, service_category
):
    loan = Loan(
        user_id=service_user.id,
        category_id=service_category.id,
        name="Car Loan",
        original_amount=Decimal("10000.00"),
        remaining_amount=Decimal("500.00"),
        status=LoanStatus.OPEN,
    )
    db.session.add(loan)
    db.session.commit()

    with pytest.raises(ValidationError):
        LoanService.update(
            service_user.id,
            loan.id,
            {"status": LoanStatus.CLOSED.value, "remaining_amount": "500.00"},
        )


def test_update_can_close_with_zero_remaining(
    db_session, service_user, service_category
):
    loan = Loan(
        user_id=service_user.id,
        category_id=service_category.id,
        name="Car Loan",
        original_amount=Decimal("10000.00"),
        remaining_amount=Decimal("0.00"),
        status=LoanStatus.OPEN,
    )
    db.session.add(loan)
    db.session.commit()

    updated = LoanService.update(
        service_user.id,
        loan.id,
        {"status": LoanStatus.CLOSED.value, "remaining_amount": "0.00"},
    )

    assert updated.status == LoanStatus.CLOSED
    assert updated.remaining_amount == Decimal("0.00")
