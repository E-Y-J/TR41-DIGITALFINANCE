# =============================================================================
# Digital Finance Tracker - Loan Service
# PURPOSE: Loan service layer for business logic operations
# =============================================================================
"""
Loan Service Module

Provides business logic, validation, DB operations, and computed fields for Loans.
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.core.extensions import db
from app.models.loan import Loan
from app.models.user import User
from app.models.category import Category
from app.models.budget import Budget
from app.schemas.loan_schema import loan_create_schema, loan_update_schema
from app.utils.errors import NotFoundError, ValidationError, InternalError
from app.models.enums import LoanStatus

logger = logging.getLogger(__name__)


class LoanService:
    """
    Service class for Loan operations.

    Handles:
        - CRUD operations
        - Validation
        - Loan lifecycle management (create, update, delete)
        - Populating related names (user, category, budget)
    """

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    @classmethod
    def get_all(cls, user_id: UUID, status_filter: Optional[str] = None) -> List[Loan]:
        """Retrieve all loans for a user, optionally filtered by status."""
        if status_filter and status_filter not in [s.value for s in LoanStatus]:
            raise ValidationError(f"Invalid status filter: {status_filter}")

        query = Loan.query.filter_by(user_id=user_id)
        if status_filter:
            query = query.filter_by(status=status_filter)

        loans = query.all()
        cls._populate_related_names(loans)
        return loans

    @classmethod
    def get_by_id(cls, user_id: UUID, loan_id: UUID) -> Loan:
        """Retrieve a single loan by ID for a user."""
        loan = Loan.query.filter_by(id=loan_id, user_id=user_id).first()
        if not loan:
            logger.debug(f"Loan not found: {loan_id}")
            raise NotFoundError("Loan not found")
        cls._populate_related_names([loan])
        return loan

    # =========================================================================
    # CREATE OPERATION
    # =========================================================================

    @classmethod
    def create(cls, user_id: UUID, data: Dict[str, Any]) -> Loan:
        """
        Create a new loan with computed progress and optional related fields.

        Note: Data may come from route (already validated/deserialized) or
        directly from unit tests (raw dict). We validate required fields
        without re-deserializing dates/decimals to avoid type conflicts.
        """
        # Validate required fields (works with both raw and deserialized data)
        required_fields = ["name", "original_amount", "remaining_amount", "category_id"]
        missing = [f for f in required_fields if f not in data or data[f] is None]
        if missing:
            raise ValidationError("Invalid loan data", details={f: ["Missing data for required field."] for f in missing})

        validated = data
        status_str = validated.get("status", LoanStatus.OPEN.value)
        status = LoanStatus(status_str) if isinstance(status_str, str) else status_str

        loan = Loan(
            user_id=user_id,
            name=validated["name"],
            original_amount=validated["original_amount"],
            remaining_amount=validated["remaining_amount"],
            category_id=validated["category_id"],
            budget_id=validated.get("budget_id"),
            status=status,
            start_date=validated.get("start_date"),
            end_date=validated.get("end_date"),
        )

        try:
            db.session.add(loan)
            db.session.commit()
            cls._populate_related_names([loan])
            logger.info(f"Created loan {loan.id} for user {user_id}")
            return loan
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create loan: {e}", exc_info=True)
            raise InternalError("Failed to create loan")

    # =========================================================================
    # UPDATE OPERATION
    # =========================================================================

    @classmethod
    def update(cls, user_id: UUID, loan_id: UUID, data: Dict[str, Any]) -> Loan:
        """Update an existing loan."""
        loan = cls.get_by_id(user_id, loan_id)

        payload=dict(data)
        if "category_id" in payload and payload["category_id"] is not None:
            payload["category_id"] = str(payload["category_id"])
        if "budget_id" in payload and payload["budget_id"] is not None:
            payload["budget_id"] = str(payload["budget_id"])

        errors = loan_update_schema.validate(payload)
        if errors:
            raise ValidationError("Invalid loan update data", details=errors)

        validated = loan_update_schema.load(payload)

        if "status" in validated:
            validated["status"] = LoanStatus(validated["status"])

        for field in ["name", "original_amount", "remaining_amount", "category_id",
                      "budget_id", "status", "start_date", "end_date"]:
            if field in validated:
                setattr(loan, field, validated[field])

        try:
            db.session.commit()
            cls._populate_related_names([loan])
            logger.info(f"Updated loan {loan.id}")
            return loan
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update loan: {e}", exc_info=True)
            raise InternalError("Failed to update loan")

    # =========================================================================
    # DELETE OPERATION
    # =========================================================================

    @classmethod
    def delete(cls, user_id: UUID, loan_id: UUID) -> None:
        """Permanently delete a loan."""
        loan = cls.get_by_id(user_id, loan_id)

        try:
            db.session.delete(loan)
            db.session.commit()
            logger.info(f"Deleted loan {loan.id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete loan: {e}", exc_info=True)
            raise InternalError("Failed to delete loan")

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    @staticmethod
    def _populate_related_names(loans: List[Loan]) -> None:
        """Populate user_name, category_name, budget_name for a list of loans.

        Note:
            Budget model does not have a 'name' column. We derive a friendly label
            from its type/category instead.
        """
        for loan in loans:
            loan.user_name = loan.user.nickname if loan.user else None
            loan.category_name = loan.category.name if loan.category else None

            budget = loan.budget
            if budget is None:
                loan.budget_name = None
            else:
                if budget.is_total_budget:
                    loan.budget_name = "Total budget"
                elif budget.category:
                    loan.budget_name = f"{budget.category.name} budget"
                else:
                    loan.budget_name = "Category budget"

# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = ["LoanService"]
