# =============================================================================
# Digital Finance Tracker - Loan Routes
# PURPOSE: CRUD API endpoints for managing user loans
# =============================================================================

import logging
from flask import Blueprint, request, g
from uuid import UUID

from app.auth.decorators import requires_auth
from app.services.loan_service import LoanService
from app.schemas.loan_schema import (
    loan_schema,
    loan_list_schema,
    loan_create_schema,
    )
from app.utils.helpers import success_response
from app.utils.errors import ValidationError

# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# BLUEPRINT SETUP
# =============================================================================

bp = Blueprint("loans", __name__)

# =============================================================================
# GET ALL LOANS FOR CURRENT USER
# =============================================================================

@bp.route("", methods=["GET"])
@requires_auth
def get_loans():
    """
    Retrieve all loans for the current user.
    Optional query params:
        status: filter by loan status ("open" or "closed")

    Returns:
        200: List of loans
    """
    user = g.current_user
    status_filter = request.args.get("status")
    
    loans = LoanService.get_all(user.id, status_filter=status_filter)

    return success_response(
        data=loan_list_schema.dump(loans),
        message="Loans retrieved successfully"
    )


# =============================================================================
# GET SINGLE LOAN BY ID
# =============================================================================

@bp.route("/<loan_id>", methods=["GET"])
@requires_auth
def get_loan(loan_id: str):
    """
    Retrieve a single loan by ID for the current user.

    Returns:
        200: Loan object
        404: Loan not found or not owned by user
    """
    user = g.current_user

    try:
        loan_uuid = UUID(loan_id)
    except ValueError:
        raise ValidationError("Invalid loan_id UUID format")

    loan = LoanService.get_by_id(user.id, loan_uuid)

    return success_response(
        data=loan_schema.dump(loan),
        message="Loan retrieved successfully"
    )


# =============================================================================
# CREATE NEW LOAN
# =============================================================================

@bp.route("", methods=["POST"])
@requires_auth
def create_loan():
    """
    Create a new loan for the current user.

    Request body example:
    {
        "name": "Car Loan",
        "original_amount": "10000.00",
        "remaining_amount": "10000.00",
        "start_date": "2026-01-01",
        "end_date": null,
        "category_id": "uuid-of-financial-services",
        "budget_id": null
    }
    """
    user = g.current_user
    data = request.get_json()

    if not data:
        raise ValidationError("Request body required")

    validated_data = loan_create_schema.load(data)
    loan = LoanService.create(user.id, validated_data)

    return success_response(
        data=loan_schema.dump(loan),
        message="Loan created successfully"
    )


# =============================================================================
# UPDATE LOAN (PATCH)
# =============================================================================

@bp.route("/<loan_id>", methods=["PATCH"])
@requires_auth
def update_loan(loan_id: str):
    """
    Partial update of a loan for the current user.

    Only provided fields will be updated.
    Example:
    {
        "remaining_amount": "9000.00",
        "status": "closed"
    }
    """
    user = g.current_user
    data = request.get_json()

    if not data:
        raise ValidationError("Request body required")

    try:
        loan_uuid = UUID(loan_id)
    except ValueError:
        raise ValidationError("Invalid loan_id UUID format")

    updated_loan = LoanService.update(user.id, loan_uuid, data)

    return success_response(
        data=loan_schema.dump(updated_loan),
        message="Loan updated successfully"
    )


# =============================================================================
# DELETE LOAN (OPTIONAL)
# =============================================================================

@bp.route("/<loan_id>", methods=["DELETE"])
@requires_auth
def delete_loan(loan_id: str):
    """
    Soft-delete a loan (or remove entirely) for the current user.
    """
    user = g.current_user

    try:
        loan_uuid = UUID(loan_id)
    except ValueError:
        raise ValidationError("Invalid loan_id UUID format")

    LoanService.delete(user.id, loan_uuid)

    return success_response(message="Loan deleted successfully")
