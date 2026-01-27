# =============================================================================
# Digital Finance Tracker - Loan Service
# PURPOSE: Loan service layer for business logic operations
# =============================================================================
"""
Loan Service Module

Provides business logic, validation, DB operations, and computed fields for Loans.
"""

import logging
from decimal import Decimal
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
        - Progress computation
        - Soft-delete
        - Populating related names (user, category, budget)
    """

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    @classmethod
    def get_all(cls, user_id: UUID, status_filter: Optional[str] = None) -> List[Loan]:
        """Retrieve all non-deleted loans for a user, optionally filtered by status."""
        if status_filter and status_filter not in [s.value for s in LoanStatus]:
            raise ValidationError(f"Invalid status filter: {status_filter}")

        query = Loan.query.filter_by(user_id=user_id, is_deleted=False)
        if status_filter:
            query = query.filter_by(status=status_filter)

        loans = query.all()
        cls._populate_related_names(loans)
        return loans

    @classmethod
    def get_by_id(cls, user_id: UUID, loan_id: UUID) -> Loan:
        """Retrieve a single non-deleted loan by ID."""
        loan = Loan.query.filter_by(id=loan_id, user_id=user_id, is_deleted=False).first()
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
        """Create a new loan with computed progress and optional related fields."""
        errors = loan_create_schema.validate(data)
        if errors:
            raise ValidationError("Invalid loan data", details=errors)

        validated = loan_create_schema.load(data)

        status = validated.get("status", LoanStatus.OPEN.value)
        if status not in [s.value for s in LoanStatus]:
            raise ValidationError(f"Invalid loan status: {status}")

        progress = cls.compute_progress(
            Decimal(validated["original_amount"]),
            Decimal(validated["remaining_amount"]),
        )

        loan = Loan(
            user_id=user_id,
            name=validated["name"],
            original_amount=Decimal(validated["original_amount"]),
            remaining_amount=Decimal(validated["remaining_amount"]),
            category_id=validated["category_id"],
            budget_id=validated.get("budget_id"),
            status=status,
            progress_percentage=progress,
            start_date=validated.get("start_date"),
            end_date=validated.get("end_date"),
            is_deleted=False,
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

        errors = loan_update_schema.validate(data)
        if errors:
            raise ValidationError("Invalid loan update data", details=errors)

        validated = loan_update_schema.load(data)

        for field in ["name", "original_amount", "remaining_amount", "category_id",
                      "budget_id", "status", "start_date", "end_date"]:
            if field in validated:
                setattr(loan, field, validated[field])

        if "original_amount" in validated or "remaining_amount" in validated:
            loan.progress_percentage = cls.compute_progress(
                Decimal(loan.original_amount),
                Decimal(loan.remaining_amount),
            )

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
    # DELETE OPERATION (SOFT DELETE)
    # =========================================================================

    @classmethod
    def delete(cls, user_id: UUID, loan_id: UUID) -> None:
        """Soft-delete a loan by setting is_deleted=True."""
        loan = cls.get_by_id(user_id, loan_id)

        try:
            loan.is_deleted = True
            db.session.commit()
            logger.info(f"Soft-deleted loan {loan.id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to soft-delete loan: {e}", exc_info=True)
            raise InternalError("Failed to delete loan")

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    @staticmethod
    def compute_progress(original: Decimal, remaining: Decimal) -> float:
        """Compute loan progress percentage safely."""
        if original <= 0:
            return 0.0
        return float(((original - remaining) / original) * 100)

    @staticmethod
    def _populate_related_names(loans: List[Loan]) -> None:
        """Populate user_name, category_name, budget_name for a list of loans."""
        for loan in loans:
            loan.user_name = loan.user.name if loan.user else None
            loan.category_name = loan.category.name if loan.category else None
            loan.budget_name = loan.budget.name if loan.budget else None


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = ["LoanService"]
