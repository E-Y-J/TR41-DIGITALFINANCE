# =============================================================================
# Digital Finance Tracker - Transaction Service
# PURPOSE: Transaction service layer for business logic operations
# =============================================================================
"""
Transaction Service Module

This module provides the service layer for Transaction operations:
- CRUD operations for transactions
- Business logic separation from routes
- Data validation and transformation
- Pagination and filtering

Usage:
    from app.services.transaction_service import TransactionService

    # Get user's transactions
    transactions, meta = TransactionService.get_user_transactions(
        user_id=user.id,
        page=1,
        per_page=20
    )

    # Create transaction
    transaction = TransactionService.create_transaction(user, data)

Design Principles:
    - Stateless class methods for all operations
    - All database commits happen here (not in routes)
    - All exceptions are domain-specific (not generic)
    - Input validation via schemas before operations
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from uuid import UUID
from decimal import Decimal

from sqlalchemy import desc

from app.core.extensions import db
from app.models.transaction import Transaction
from app.models.user import User
from app.models.enums import TransactionType
from app.schemas.transaction_schema import (
    transaction_create_schema,
    transaction_update_schema,
)
from app.utils.errors import (
    NotFoundError,
    ValidationError,
    InternalError,
    ForbiddenError,
)


# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# TRANSACTION SERVICE CLASS
# =============================================================================


class TransactionService:
    """
    Service class for Transaction operations.

    All methods are class methods (no instance needed).
    Handles business logic, validation, and database operations.

    Example:
        >>> transactions, meta = TransactionService.get_user_transactions(user_id)
        >>> transaction = TransactionService.create_transaction(user, data)
    """

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    @classmethod
    def get_by_id(cls, transaction_id: UUID) -> Transaction:
        """
        Get transaction by primary key ID.

        Args:
            transaction_id: Transaction's UUID primary key

        Returns:
            Transaction instance

        Raises:
            NotFoundError: If transaction not found

        Example:
            >>> transaction = TransactionService.get_by_id(uuid.UUID("..."))
        """
        transaction = Transaction.query.get(transaction_id)

        if transaction is None:
            logger.debug(f"Transaction not found by ID: {transaction_id}")
            raise NotFoundError("Transaction not found")

        return transaction

    @classmethod
    def get_user_transaction(cls, user: User, transaction_id: UUID) -> Transaction:
        """
        Get a specific transaction belonging to a user.

        Args:
            user: User instance (owner)
            transaction_id: Transaction's UUID

        Returns:
            Transaction instance

        Raises:
            NotFoundError: If transaction not found
            ForbiddenError: If transaction doesn't belong to user

        Example:
            >>> transaction = TransactionService.get_user_transaction(user, tx_id)
        """
        transaction = cls.get_by_id(transaction_id)

        if transaction.user_id != user.id:
            logger.warning(
                f"User {user.id} attempted to access transaction {transaction_id}"
            )
            raise ForbiddenError("You don't have access to this transaction")

        return transaction

    @classmethod
    def get_user_transactions(
        cls,
        user: User,
        page: int = 1,
        per_page: int = 20,
        transaction_type: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        sort_by: str = "date",
        sort_order: str = "desc",
    ) -> Tuple[List[Transaction], Dict[str, Any]]:
        """
        Get paginated list of user's transactions with optional filters.

        Args:
            user: User instance
            page: Page number (1-indexed)
            per_page: Items per page (max 100)
            transaction_type: Filter by type ('income' or 'expense')
            category: Filter by category
            start_date: Filter transactions on or after this date (YYYY-MM-DD)
            end_date: Filter transactions on or before this date (YYYY-MM-DD)
            sort_by: Sort field ('date', 'amount', 'created_at')
            sort_order: Sort direction ('asc' or 'desc')

        Returns:
            Tuple of (list of transactions, pagination metadata)

        Example:
            >>> transactions, meta = TransactionService.get_user_transactions(
            ...     user,
            ...     page=1,
            ...     per_page=20,
            ...     transaction_type='expense',
            ...     category='Food'
            ... )
        """
        # Ensure per_page doesn't exceed maximum
        per_page = min(per_page, 100)

        # Build base query
        query = Transaction.query.filter(Transaction.user_id == user.id)

        # Apply filters
        if transaction_type:
            try:
                tx_type = TransactionType(transaction_type.lower())
                query = query.filter(Transaction.transaction_type == tx_type)
            except ValueError:
                raise ValidationError(
                    f"Invalid transaction_type: {transaction_type}. "
                    "Must be 'income' or 'expense'"
                )

        if category:
            query = query.filter(Transaction.category == category)

        if start_date:
            query = query.filter(Transaction.date >= start_date)

        if end_date:
            query = query.filter(Transaction.date <= end_date)

        # Apply sorting
        sort_column = getattr(Transaction, sort_by, Transaction.date)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)

        # Execute paginated query
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # Build metadata
        meta = {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }

        return pagination.items, meta

    # =========================================================================
    # CREATE OPERATIONS
    # =========================================================================

    @classmethod
    def create_transaction(cls, user: User, data: Dict[str, Any]) -> Transaction:
        """
        Create a new transaction for a user.

        Args:
            user: User instance (owner)
            data: Transaction data from request

        Returns:
            Created Transaction instance

        Raises:
            ValidationError: If data fails validation
            InternalError: If database operation fails

        Example:
            >>> transaction = TransactionService.create_transaction(user, {
            ...     "amount": "50.00",
            ...     "transaction_type": "expense",
            ...     "date": "2025-12-19",
            ...     "merchant_name": "Grocery Store",
            ...     "category": "Food"
            ... })
        """
        # Validate input
        errors = transaction_create_schema.validate(data)
        if errors:
            raise ValidationError("Invalid transaction data", details=errors)

        # Load validated data
        validated = transaction_create_schema.load(data)

        try:
            # Convert transaction_type string to enum
            tx_type = TransactionType(validated["transaction_type"].lower())

            # Create transaction
            transaction = Transaction(
                user_id=user.id,
                amount=Decimal(str(validated["amount"])),
                transaction_type=tx_type,
                date=validated["date"],
                merchant_name=validated.get("merchant_name"),
                category=validated.get("category"),
            )

            db.session.add(transaction)
            db.session.commit()

            logger.info(f"Created transaction {transaction.id} for user {user.id}")
            return transaction

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create transaction: {e}", exc_info=True)
            raise InternalError("Failed to create transaction")

    # =========================================================================
    # UPDATE OPERATIONS
    # =========================================================================

    @classmethod
    def update_transaction(
        cls, user: User, transaction_id: UUID, data: Dict[str, Any]
    ) -> Transaction:
        """
        Update an existing transaction.

        Args:
            user: User instance (owner)
            transaction_id: Transaction's UUID
            data: Fields to update

        Returns:
            Updated Transaction instance

        Raises:
            NotFoundError: If transaction not found
            ForbiddenError: If transaction doesn't belong to user
            ValidationError: If data fails validation
            InternalError: If database operation fails

        Example:
            >>> updated = TransactionService.update_transaction(user, tx_id, {
            ...     "amount": "75.00",
            ...     "category": "Dining"
            ... })
        """
        # Get transaction (validates ownership)
        transaction = cls.get_user_transaction(user, transaction_id)

        # Validate input
        errors = transaction_update_schema.validate(data)
        if errors:
            raise ValidationError("Invalid transaction data", details=errors)

        # Load validated data
        validated = transaction_update_schema.load(data)

        try:
            # Update fields if provided
            if validated.get("amount") is not None:
                transaction.amount = Decimal(str(validated["amount"]))

            if validated.get("transaction_type") is not None:
                transaction.transaction_type = TransactionType(
                    validated["transaction_type"].lower()
                )

            if validated.get("date") is not None:
                transaction.date = validated["date"]

            if "merchant_name" in validated:
                transaction.merchant_name = validated["merchant_name"]

            if "category" in validated:
                transaction.category = validated["category"]

            db.session.commit()

            logger.info(f"Updated transaction {transaction_id} for user {user.id}")
            return transaction

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update transaction: {e}", exc_info=True)
            raise InternalError("Failed to update transaction")

    # =========================================================================
    # DELETE OPERATIONS
    # =========================================================================

    @classmethod
    def delete_transaction(cls, user: User, transaction_id: UUID) -> None:
        """
        Delete a transaction.

        Args:
            user: User instance (owner)
            transaction_id: Transaction's UUID

        Raises:
            NotFoundError: If transaction not found
            ForbiddenError: If transaction doesn't belong to user
            InternalError: If database operation fails

        Example:
            >>> TransactionService.delete_transaction(user, tx_id)
        """
        # Get transaction (validates ownership)
        transaction = cls.get_user_transaction(user, transaction_id)

        try:
            db.session.delete(transaction)
            db.session.commit()

            logger.info(f"Deleted transaction {transaction_id} for user {user.id}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete transaction: {e}", exc_info=True)
            raise InternalError("Failed to delete transaction")

    # =========================================================================
    # AGGREGATION OPERATIONS
    # =========================================================================

    @classmethod
    def get_user_summary(
        cls,
        user: User,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get summary of user's transactions.

        Args:
            user: User instance
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Summary dict with totals and counts

        Example:
            >>> summary = TransactionService.get_user_summary(user)
            >>> print(summary["total_income"])
        """
        from sqlalchemy import func

        # Build base query
        query = db.session.query(
            Transaction.transaction_type,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count"),
        ).filter(Transaction.user_id == user.id)

        # Apply date filters
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)

        # Group by type
        results = query.group_by(Transaction.transaction_type).all()

        # Build summary
        summary = {
            "total_income": Decimal("0.00"),
            "total_expense": Decimal("0.00"),
            "income_count": 0,
            "expense_count": 0,
            "net_balance": Decimal("0.00"),
        }

        for tx_type, total, count in results:
            if tx_type == TransactionType.INCOME:
                summary["total_income"] = total or Decimal("0.00")
                summary["income_count"] = count
            elif tx_type == TransactionType.EXPENSE:
                summary["total_expense"] = total or Decimal("0.00")
                summary["expense_count"] = count

        summary["net_balance"] = summary["total_income"] - summary["total_expense"]

        return summary


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "TransactionService",
]
