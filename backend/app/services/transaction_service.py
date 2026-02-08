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

from datetime import datetime
import logging
from typing import Dict, Any, Optional, Tuple, List
from uuid import UUID
from decimal import Decimal
from dateutil.relativedelta import relativedelta

from sqlalchemy import and_, desc, cast, Date, func

from app.core.extensions import db
from app.models.transaction import Transaction
from app.models.user import User
from app.models.enums import TransactionType
from app.schemas.transaction_schema import (
    transaction_create_schema,
    transaction_update_schema,
)
from app.models.category import Category

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
        transaction = db.session.get(Transaction, transaction_id)

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
        category_id: Optional[UUID] = None,
        category_name: Optional[str] = None,
        merchant_name: Optional[str] = None,
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
            category_id: Filter by category UUID
            category_name: Filter by category name (will be resolved)
            merchant_name: Filter by merchant name
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
            ...     category_name='Food'
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

        if category_id:
            query = query.filter(Transaction.category_id == category_id)

        elif category_name:
            from app.services.category_service import CategoryService

            name = category_name.strip()

            if name:
                # Try to find existing category by name
                category = CategoryService.get_by_name(name)
                if category:
                    query = query.filter(Transaction.category_id == category.id)
                else:
                    # Unknown category name - no results for this filter
                    query = query.filter(False)

        if start_date:
            # Cast the string date column to date type for proper comparison
            # This handles both "YYYY-MM-DD" and "YYYY-MM-DD HH:MM:SS..." formats
            query = query.filter(cast(Transaction.date, Date) >= start_date)

        if end_date:
            # Cast the string date column to date type for proper comparison
            query = query.filter(cast(Transaction.date, Date) <= end_date)

        if merchant_name:
            query = query.filter(Transaction.merchant_name.ilike(f"%{merchant_name}%"))

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
        Create a new transaction for a user with auto-categorization.

        Includes auto-categorization via keyword matching.
        If merchant_name is provided and no category_id is given,
        the system will attempt to auto-categorize the transaction.

        CATEGORIZATION FLOW:
        1. If category_id provided -> use that category
        2. Else if merchant_name provided -> auto-categorize via keywords
        3. If no match -> assign "Unknown" category

        Args:
            user: User instance (owner)
            data: Transaction data from request

        Returns:
            Created Transaction instance with category assigned

        Raises:
            ValidationError: If data fails validation
            InternalError: If database operation fails

        Example:
            >>> # Auto-categorized by keyword
            >>> transaction = TransactionService.create_transaction(user, {
            ...     "amount": "50.00",
            ...     "transaction_type": "expense",
            ...     "date": "2025-12-19",
            ...     "merchant_name": "Starbucks Coffee"
            ... })
            >>> print(transaction.category_rel.name)  # "Food & Dining"
        """
        # Import here to avoid circular imports
        from app.services.category_service import CategoryService
        from app.models.enums import AISource

        # Validate input
        errors = transaction_create_schema.validate(data)
        if errors:
            raise ValidationError("Invalid transaction data", details=errors)

        # Load validated data
        validated = transaction_create_schema.load(data)

        try:
            # Convert transaction_type string to enum
            tx_type = TransactionType(validated["transaction_type"].lower())

            # =================================================================
            # Auto-categorization
            # =================================================================
            category_id = validated.get("category_id")
            category_name = validated.get("category")  # Legacy field (string name)
            ai_confidence = None
            ai_source = None

            if category_id:
                # User explicitly provided category_id - use it
                ai_source = AISource.USER
                ai_confidence = 1.0
            elif category_name:
                # User provided category name string - resolve to category_id
                # This handles frontend sending category: "Food & Dining" etc.
                resolved_category = CategoryService.get_by_name(category_name)
                if resolved_category:
                    category_id = resolved_category.id
                    ai_source = AISource.USER
                    ai_confidence = 1.0
                    logger.info(
                        f"Resolved category name '{category_name}' to ID {category_id}"
                    )
                else:
                    logger.warning(
                        f"Category name '{category_name}' not found, "
                        f"falling back to auto-categorization"
                    )

            # Only auto-categorize if no explicit category was provided
            if not category_id and validated.get("merchant_name"):
                # Try auto-categorization by keyword
                category, confidence, source = CategoryService.auto_categorize(
                    validated["merchant_name"]
                )
                category_id = category.id
                ai_confidence = confidence

                # Map source string to enum
                if source == "keyword":
                    ai_source = AISource.KEYWORD
                elif source == "huggingface":
                    ai_source = AISource.HUGGINGFACE
                elif source == "gemini":
                    ai_source = AISource.GEMINI
                # else: source == "unknown", ai_source stays None

            # Create transaction with auto-categorization data
            transaction = Transaction(
                user_id=user.id,
                amount=Decimal(str(validated["amount"])),
                transaction_type=tx_type,
                date=validated["date"],
                merchant_name=validated.get("merchant_name"),
                # Legacy 'category' field intentionally not set here anymore
                # AI categorization fields
                category_id=category_id,
                ai_confidence=ai_confidence,
                ai_source=ai_source,
            )

            db.session.add(transaction)
            db.session.commit()

            logger.info(
                f"Created transaction {transaction.id} for user {user.id}, "
                f"category_id={category_id}, source={ai_source}"
            )

            # =================================================================
            # Check and trigger budget alerts for EXPENSE transactions
            # =================================================================
            if tx_type == TransactionType.EXPENSE and category_id:
                try:
                    from app.services.budget_service import BudgetService

                    alerts = BudgetService.check_and_trigger_budget_alerts(
                        user.id, category_id
                    )
                    if alerts:
                        logger.info(
                            f"Budget alert(s) triggered for user {user.id}: "
                            f"{[a['type'] for a in alerts]}"
                        )
                except Exception as alert_error:
                    # Don't fail transaction creation if alert fails
                    logger.warning(f"Failed to check budget alerts: {alert_error}")

            # =================================================================
            # Check for anomalies (large transactions, unusual spending, etc.)
            # =================================================================
            if tx_type == TransactionType.EXPENSE:
                try:
                    from app.ai.anomaly_detector import get_detector

                    detector = get_detector()
                    anomalies = detector.check_transaction(
                        user_id=user.id,
                        transaction=transaction,
                        create_alerts=True,  # Auto-create Alert records
                    )
                    if anomalies:
                        logger.info(
                            f"Anomaly alert(s) triggered for user {user.id}: "
                            f"{[a['type'] for a in anomalies]}"
                        )
                except Exception as anomaly_error:
                    # Don't fail transaction creation if anomaly check fails
                    logger.warning(f"Failed to check anomalies: {anomaly_error}")

            # =================================================================
            # Index transaction for RAG (semantic search)
            # =================================================================
            if (
                tx_type == TransactionType.EXPENSE
                and category_id
                and validated.get("merchant_name")
            ):
                try:
                    from app.ai.rag import get_rag_engine
                    from app.models.category import Category

                    category = db.session.get(Category, category_id)
                    if category:
                        rag_engine = get_rag_engine()
                        rag_engine.index_transaction(
                            user_id=user.id,
                            transaction_id=transaction.id,
                            merchant_name=validated["merchant_name"],
                            category_name=category.name,
                            amount=float(transaction.amount),
                        )
                except Exception as rag_error:
                    # Don't fail transaction creation if RAG indexing fails
                    logger.warning(f"Failed to index for RAG: {rag_error}")

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

            # Legacy 'category' field intentionally not updated anymore

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

        # Apply date filters - cast string date to date type for proper comparison
        if start_date:
            query = query.filter(cast(Transaction.date, Date) >= start_date)
        if end_date:
            query = query.filter(cast(Transaction.date, Date) <= end_date)

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
    # TRANSACTION CATEGORY BREAKDOWN 
    # =============================================================================

    @classmethod
    def get_category_breakdown(
        cls,
        user: User,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        join_conditions = [
            Transaction.category_id == Category.id,
            Transaction.user_id == user.id,
            Transaction.transaction_type == TransactionType.EXPENSE
        ]
        
        if start_date:
            join_conditions.append(cast(Transaction.date, Date) >= start_date)
        if end_date:
            join_conditions.append(cast(Transaction.date, Date) <= end_date)

        query = db.session.query(
            Category.name.label("category_name"),
            func.coalesce(func.sum(Transaction.amount), 0).label("total_amount")
        ).outerjoin(
            Transaction, 
            and_(*join_conditions) 
        )
        
        results = query.group_by(Category.name).all()

        return [
            {"category": name, "total": str(total)} 
            for name, total in results
        ]
    # =============================================================================
    # TRANSACTION MONTHLY TREND 
    # =============================================================================

    @classmethod
    def get_monthly_trend(
        cls,
        user: User,
        start_date: str,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        from sqlalchemy import func, cast, Date
        from app.models.category import Category

        # 1. Setup Dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        # Present month (today)
        now_dt = datetime.now()

        # Calculate 12 months from start
        limit_dt = start_dt + relativedelta(months=12)

        # Use whichever is sooner: 12 months in the future OR the present month
        effective_end_dt = min(limit_dt, now_dt)

        # Convert back to strings for the SQL query
        sql_start = start_dt.strftime("%Y-%m-%d")
        sql_end = effective_end_dt.strftime("%Y-%m-%d")

        db_date = cast(Transaction.date, Date)
        month_group = func.date_trunc("month", db_date)

        # 2. SQL Query
        query = (
            db.session.query(
                month_group.label("month"), func.sum(Transaction.amount).label("total")
            )
            .join(Category, Transaction.category_id == Category.id)
            .filter(
                Transaction.user_id == user.id,
                Transaction.transaction_type == TransactionType.EXPENSE,
            )
        )

        if category:
            query = query.filter(Category.name == category)

        # Use our calculated 12-month-or-now range
        query = query.filter(db_date >= sql_start, db_date <= sql_end)
        results = query.group_by(month_group).order_by(month_group).all()

        # 3. Map results and Fill Gaps
        db_data = {row.month.strftime("%Y-%m"): row.total for row in results}
        final_trend = []
        current_dt = datetime(start_dt.year, start_dt.month, 1)

        # Comparison logic for the loop
        while current_dt <= effective_end_dt:
            key = current_dt.strftime("%Y-%m")
            final_trend.append(
                {
                    "month": key,
                    "month_label": current_dt.strftime("%b %Y"),
                    "total": str(db_data.get(key, 0)),
                }
            )
            # Standard library month increment
            if current_dt.month == 12:
                current_dt = datetime(current_dt.year + 1, 1, 1)
            else:
                current_dt = datetime(current_dt.year, current_dt.month + 1, 1)

        return final_trend

    # =========================================================================
    # CATEGORY OVERRIDE
    # =========================================================================

    @classmethod
    def update_category(
        cls,
        user: User,
        transaction_id: UUID,
        category_id: UUID,
    ) -> Transaction:
        """
        Update a transaction's category (user override).

        Allows users to manually correct AI-assigned categories.
        Stores the original category for analytics purposes.
        Records correction for AI learning to improve future predictions.

        WHAT HAPPENS:
        1. Store current category as original_category_id (if not already overridden)
        2. Set new category_id
        3. Set is_user_override = True
        4. Set ai_source = USER
        5. Record correction in UserLearning table for AI improvement

        Args:
            user: User instance (owner)
            transaction_id: Transaction's UUID
            category_id: New category UUID to assign

        Returns:
            Updated Transaction instance

        Raises:
            NotFoundError: If transaction or category not found
            ForbiddenError: If transaction doesn't belong to user

        Example:
            >>> updated = TransactionService.update_category(
            ...     user, tx_id, food_category_id
            ... )
            >>> print(updated.category_rel.name)  # "Food & Dining"
            >>> print(updated.is_user_override)   # True
        """
        from app.services.category_service import CategoryService
        from app.models.enums import AISource

        # Get transaction (validates ownership)
        transaction = cls.get_user_transaction(user, transaction_id)

        # Validate category exists
        new_category = CategoryService.get_by_id(category_id)

        try:
            # Store original category if this is first override
            if not transaction.is_user_override and transaction.category_id:
                transaction.original_category_id = transaction.category_id

            # Update category
            transaction.category_id = new_category.id
            transaction.is_user_override = True
            transaction.ai_source = AISource.USER
            transaction.ai_confidence = 1.0  # User is 100% confident

            db.session.commit()

            # Record correction for AI learning (Sprint 3 DB persistence)
            # This helps improve future predictions for this merchant
            if transaction.merchant_name:
                try:
                    from app.ai.user_learning import get_learning_engine

                    # Get original category name for learning
                    original_cat_name = None
                    if transaction.original_category_id:
                        original_cat = CategoryService.get_by_id(
                            transaction.original_category_id
                        )
                        original_cat_name = original_cat.name if original_cat else None

                    engine = get_learning_engine()
                    engine.record_correction(
                        user_id=user.id,
                        merchant_name=transaction.merchant_name,
                        correct_category=new_category.name,
                        original_category=original_cat_name,
                        original_source=str(transaction.ai_source.value)
                        if transaction.ai_source
                        else None,
                    )
                    logger.debug(
                        f"Recorded learning: {transaction.merchant_name} → {new_category.name}"
                    )
                except Exception as e:
                    # Don't fail the update if learning fails
                    logger.warning(f"Failed to record learning: {e}")

            logger.info(
                f"User {user.id} overrode category for transaction {transaction_id} "
                f"to {new_category.name}"
            )
            return transaction

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update category: {e}", exc_info=True)
            raise InternalError("Failed to update category")


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "TransactionService",
]
