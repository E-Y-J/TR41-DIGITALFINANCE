# app/services/loan_service.py

from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime, date
from typing import List, Dict, Any, Optional

from app.utils.errors import NotFoundError, ValidationError
from app.models.enums import LoanStatus


class LoanService:
    """
    Service layer for loan-related business logic.

    Stub implementation for testing / development.
    Fully aligned with Loan model and LoanSchema including optional dates and timestamps.
    """

    # -------------------------------------------------------------------------
    # GET ALL LOANS
    # -------------------------------------------------------------------------
    @staticmethod
    def get_all(user_id: UUID, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve all loans for a user, optionally filtered by status."""
        valid_statuses = [s.value for s in LoanStatus]
        if status_filter and status_filter not in valid_statuses:
            raise ValidationError(f"Invalid status filter: {status_filter}")

        # TODO: Replace with DB query
        sample_loan = LoanService._sample_loan(user_id)

        if status_filter and sample_loan["status"] != status_filter:
            return []

        return [sample_loan]

    # -------------------------------------------------------------------------
    # GET SINGLE LOAN
    # -------------------------------------------------------------------------
    @staticmethod
    def get_by_id(user_id: UUID, loan_id: UUID) -> Dict[str, Any]:
        """Retrieve a single loan by ID."""
        if not loan_id:
            raise NotFoundError("Loan not found")

        # TODO: Replace with DB lookup
        sample_loan = LoanService._sample_loan(user_id, loan_id)
        return sample_loan

    # -------------------------------------------------------------------------
    # CREATE LOAN
    # -------------------------------------------------------------------------
    @staticmethod
    def create(user_id: UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new loan for the user."""
        original_amount = Decimal(data["original_amount"])
        remaining_amount = Decimal(data["remaining_amount"])
        status = data.get("status", LoanStatus.OPEN.value)

        # Validate status
        if status not in [s.value for s in LoanStatus]:
            raise ValidationError(f"Invalid loan status: {status}")

        progress = LoanService.compute_progress(original_amount, remaining_amount)

        return {
            "id": uuid4(),
            "user_id": user_id,
            "name": data["name"],
            "original_amount": original_amount,
            "remaining_amount": remaining_amount,
            "category_id": data["category_id"],
            "budget_id": data.get("budget_id"),
            "status": status,
            "progress_percentage": progress,
            "user_name": "John Doe",
            "category_name": "Default Category",
            "budget_name": None,
            "start_date": data.get("start_date"),  # Optional
            "end_date": data.get("end_date"),      # Optional
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

    # -------------------------------------------------------------------------
    # UPDATE LOAN
    # -------------------------------------------------------------------------
    @staticmethod
    def update(user_id: UUID, loan_id: UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing loan."""
        if not loan_id:
            raise NotFoundError("Loan not found")

        # Assume existing values for stub
        existing_loan = LoanService._sample_loan(user_id, loan_id)

        # Validate status if provided
        status = data.get("status", existing_loan["status"])
        if status not in [s.value for s in LoanStatus]:
            raise ValidationError(f"Invalid loan status: {status}")

        # Update fields if provided
        original_amount = Decimal(data.get("original_amount", existing_loan["original_amount"]))
        remaining_amount = Decimal(data.get("remaining_amount", existing_loan["remaining_amount"]))
        progress = LoanService.compute_progress(original_amount, remaining_amount)

        return {
            "id": loan_id,
            "user_id": user_id,
            "name": data.get("name", existing_loan["name"]),
            "original_amount": original_amount,
            "remaining_amount": remaining_amount,
            "category_id": data.get("category_id", existing_loan["category_id"]),
            "budget_id": data.get("budget_id", existing_loan["budget_id"]),
            "status": status,
            "progress_percentage": progress,
            "user_name": existing_loan["user_name"],
            "category_name": existing_loan["category_name"],
            "budget_name": existing_loan["budget_name"],
            "start_date": data.get("start_date", existing_loan["start_date"]),
            "end_date": data.get("end_date", existing_loan["end_date"]),
            "created_at": existing_loan["created_at"],
            "updated_at": datetime.utcnow(),
        }

    # -------------------------------------------------------------------------
    # DELETE LOAN
    # -------------------------------------------------------------------------
    @staticmethod
    def delete(user_id: UUID, loan_id: UUID) -> None:
        """Delete (or soft-delete) a loan."""
        if not loan_id:
            raise NotFoundError("Loan not found")
        # TODO: Implement DB delete
        return None

    # -------------------------------------------------------------------------
    # HELPER METHODS
    # -------------------------------------------------------------------------
    @staticmethod
    def compute_progress(original: Decimal, remaining: Decimal) -> float:
        """Compute progress percentage for a loan."""
        if original <= 0:
            return 0.0
        return float(((original - remaining) / original) * 100)

    @staticmethod
    def _sample_loan(user_id: UUID, loan_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Generate a sample loan dict with all schema fields populated."""
        original_amount = Decimal("1000.00")
        remaining_amount = Decimal("800.00")
        loan_id = loan_id or uuid4()
        progress = LoanService.compute_progress(original_amount, remaining_amount)

        return {
            "id": loan_id,
            "user_id": user_id,
            "name": "Sample Loan",
            "original_amount": original_amount,
            "remaining_amount": remaining_amount,
            "category_id": uuid4(),
            "budget_id": None,
            "status": LoanStatus.OPEN.value,
            "progress_percentage": progress,
            "user_name": "John Doe",
            "category_name": "Default Category",
            "budget_name": None,
            "start_date": None,
            "end_date": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
