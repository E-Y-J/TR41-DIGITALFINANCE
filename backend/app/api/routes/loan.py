# =============================================================================
# Digital Finance Tracker - Loan Routes
# PURPOSE: CRUD API endpoints for managing user loans
# =============================================================================

import logging
from uuid import UUID
from marshmallow import ValidationError as MarshmallowValidationError
from flask import Blueprint, request, g

from app.auth.decorators import requires_auth
from app.auth.user_sync import sync_user_from_claims
from app.schemas.loan_schema import (
    loan_schema,
    loan_list_schema,
    loan_create_schema,
    loan_update_schema,
)
from app.services.loan_service import LoanService
from app.utils.errors import ValidationError
from app.utils.helpers import success_response

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
    Retrieve all loans for the current user with pagination and filtering.
    """
    user = sync_user_from_claims(g.current_user, g.access_token)

    status_filter = request.args.get("status", "all")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    loans_data = LoanService.get_paginated(
        user_id=user.id, 
        status_filter=None if status_filter == "all" else status_filter,
        page=page,
        per_page=per_page
    )
    

    return success_response(
        data={
            "items": loan_list_schema.dump(loans_data.items),
            "total": loans_data.total,
            "pages": loans_data.pages,
            "current_page": loans_data.page
        },
        message="Loans retrieved successfully",
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
    user = sync_user_from_claims(g.current_user, g.access_token)

    try:
        loan_uuid = UUID(loan_id)
    except ValueError:
        raise ValidationError("Invalid loan_id UUID format")

    loan = LoanService.get_by_id(user.id, loan_uuid)

    return success_response(
        data=loan_schema.dump(loan),
        message="Loan retrieved successfully",
    )


# =============================================================================
# CREATE NEW LOAN
# =============================================================================


@bp.route("", methods=["POST"])
@requires_auth
def create_loan():
    """
    Create a new loan for the current user.
    """
    user = sync_user_from_claims(g.current_user, g.access_token)

    data = request.get_json(silent=True)
    if data is None:
        raise ValidationError("Request body required")

    try:
        validated_data = loan_create_schema.load(data)
    except MarshmallowValidationError as err:
        raise ValidationError("Invalid loan data", details=err.messages)

    loan = LoanService.create(user.id, validated_data)

    return success_response(
        data=loan_schema.dump(loan),
        message="Loan created successfully",
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
    """
    user = sync_user_from_claims(g.current_user, g.access_token)

    data = request.get_json(silent=True)
    if data is None:
        raise ValidationError("Request body required")

    try:
        loan_uuid = UUID(loan_id)
    except ValueError:
        raise ValidationError("Invalid loan_id UUID format")

    try:
        validated_data = loan_update_schema.load(data)
    except MarshmallowValidationError as err:
        raise ValidationError("Invalid loan data", details=err.messages)

    updated_loan = LoanService.update(user.id, loan_uuid, validated_data)

    return success_response(
        data=loan_schema.dump(updated_loan),
        message="Loan updated successfully",
    )


# =============================================================================
# DELETE LOAN
# =============================================================================


@bp.route("/<loan_id>", methods=["DELETE"])
@requires_auth
def delete_loan(loan_id: str):
    """
    Delete a loan for the current user.
    """
    user = sync_user_from_claims(g.current_user, g.access_token)

    try:
        loan_uuid = UUID(loan_id)
    except ValueError:
        raise ValidationError("Invalid loan_id UUID format")

    LoanService.delete(user.id, loan_uuid)

    return success_response(message="Loan deleted successfully")
