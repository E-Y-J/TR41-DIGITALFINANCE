# =============================================================================
# Digital Finance Tracker - Transaction Model
# PURPOSE: Transaction database model for storing user financial transactions
# =============================================================================
"""
Transaction Model Module

This module defines the Transaction model for the local database:
- Stores user income and expense transactions
- Links to User model via foreign key
- Supports categorization and merchant tracking

Database Table: transactions
Primary Key: id (UUID)
Foreign Key: user_id (references users.id)

Relationship:
    - Many Transactions belong to one User (N:1)
    - A user can have zero or many transactions
    - Every transaction MUST belong to exactly one user

Usage:
    from app.models import Transaction, TransactionType

    # Create new transaction
    transaction = Transaction(
        user_id=user.id,
        amount=Decimal("50.00"),
        transaction_type=TransactionType.EXPENSE,
        date="2024-01-15",
        merchant_name="Coffee Shop",
        category="Food & Dining"
    )
    db.session.add(transaction)
    db.session.commit()

Notes:
    - amount is stored as Decimal for financial precision
    - transaction_type is either 'income' or 'expense'
    - date is stored as string (VARCHAR) per ERD specification
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Dict, Any, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Numeric, Float, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.extensions import db
from app.models.enums import TransactionType, AISource

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category


# =============================================================================
# TRANSACTION MODEL
# =============================================================================


class Transaction(db.Model):
    """
    Transaction model representing a financial transaction.

    This model stores individual income/expense transactions for users.
    Each transaction must belong to exactly one user (enforced by NOT NULL FK).

    Attributes:
        id: Primary key UUID
        user_id: Foreign key to users table (required)
        amount: Transaction amount (required)
        transaction_type: Income or expense (required)
        date: Transaction date as string (required)
        merchant_name: Name of merchant/payee (optional)
        category: Transaction category (optional)
        created_at: Record creation timestamp
        updated_at: Record update timestamp

    Relationships:
        user: Many-to-One relationship with User model

    Example:
        >>> transaction = Transaction(
        ...     user_id=user.id,
        ...     amount=Decimal("125.50"),
        ...     transaction_type=TransactionType.EXPENSE,
        ...     date="2024-01-15",
        ...     merchant_name="Amazon",
        ...     category="Shopping"
        ... )
        >>> db.session.add(transaction)
        >>> db.session.commit()
    """

    __tablename__ = "transactions"

    # =========================================================================
    # PRIMARY KEY
    # =========================================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Primary key UUID",
    )

    # =========================================================================
    # FOREIGN KEY
    # =========================================================================

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to users table",
    )

    # =========================================================================
    # TRANSACTION FIELDS (per ERD)
    # =========================================================================

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        doc="Transaction amount",
    )

    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(
            TransactionType,
            name="transaction_type_enum",
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
            validate_strings=True,
        ),
        nullable=False,
        index=True,
        doc="Transaction type: income or expense",
    )

    date: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Transaction date (stored as string per ERD)",
    )

    merchant_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Name of merchant or payee",
    )

    # -------------------------------------------------------------------------
    # LEGACY FIELD - Keep for backward compatibility during migration
    # This field is deprecated in favor of category_id foreign key
    # Will be removed in future migration after data migration complete
    # -------------------------------------------------------------------------
    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="[DEPRECATED] Transaction category string - use category_id instead",
    )

    # =========================================================================
    # AI CATEGORIZATION FIELDS
    # =========================================================================
    # These fields support the AI categorization feature:
    # - category_id: Links to categories table
    # - ai_confidence: AI's confidence score (0.0 to 1.0)
    # - ai_source: Which AI system assigned the category
    # - is_user_override: Did user manually override AI's suggestion?
    # - original_category_id: What AI originally suggested (before override)
    # =========================================================================

    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Foreign key to categories table",
    )

    ai_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="AI confidence score (0.0 to 1.0). NULL if user-assigned.",
    )

    ai_source: Mapped[Optional[AISource]] = mapped_column(
        Enum(
            AISource,
            name="ai_source_enum",
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
            validate_strings=True,
        ),
        nullable=True,
        index=True,
        doc="Source of categorization: huggingface, gemini, or user",
    )

    is_user_override: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="True if user manually overrode AI's category suggestion",
    )

    original_category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        doc="AI's original suggestion before user override",
    )

    # =========================================================================
    # TIMESTAMPS
    # =========================================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Record creation timestamp",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Record update timestamp",
    )

    # =========================================================================
    # INDEXES (for common query patterns)
    # =========================================================================

    __table_args__ = (
        # Composite index for user + date queries (e.g., monthly reports)
        db.Index("idx_transaction_user_date", "user_id", "date"),
        # Composite index for user + category queries (legacy)
        db.Index("idx_transaction_user_category", "user_id", "category"),
        # Composite index for user + category_id queries
        db.Index("idx_transaction_user_category_id", "user_id", "category_id"),
        # Composite index for user + ai_source queries
        db.Index("idx_transaction_user_ai_source", "user_id", "ai_source"),
    )

    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================

    # Many Transactions belong to one User (N:1 relationship)
    user: Mapped["User"] = relationship(
        "User",
        back_populates="transactions",
    )

    # Many Transactions belong to one Category (N:1 relationship)
    # Links to categories table for AI categorization
    category_rel: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="transactions",
        foreign_keys=[category_id],
    )

    # Original category before user override (N:1 relationship)
    # Tracks what AI originally suggested
    original_category_rel: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="original_transactions",
        foreign_keys=[original_category_id],
    )

    # =========================================================================
    # METHODS
    # =========================================================================

    def __repr__(self) -> str:
        """String representation of Transaction."""
        return f"<Transaction {self.transaction_type.value}: {self.amount}>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert transaction to dictionary for API response.

        Returns:
            Dictionary representation of transaction

        Example:
            >>> transaction.to_dict()
            {
                "id": "uuid-string",
                "user_id": "uuid-string",
                "amount": "125.50",
                "transaction_type": "expense",
                ...
            }

        Includes:
            Added category object with id/name, ai_confidence, ai_source,
            is_user_override, and original_category fields.
        """
        result = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "amount": str(self.amount),
            "transaction_type": self.transaction_type.value,
            "date": self.date,
            "merchant_name": self.merchant_name,
            # Legacy category string (deprecated)
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            # AI categorization fields
            "category_id": str(self.category_id) if self.category_id else None,
            "ai_confidence": self.ai_confidence,
            "ai_source": self.ai_source.value if self.ai_source else None,
            "is_user_override": self.is_user_override,
            "original_category_id": (
                str(self.original_category_id) if self.original_category_id else None
            ),
        }

        # Include category object if relationship is loaded
        if self.category_rel:
            result["category_obj"] = {
                "id": str(self.category_rel.id),
                "name": self.category_rel.name,
            }
        else:
            result["category_obj"] = None

        return result

    # =========================================================================
    # CLASS METHODS
    # =========================================================================

    @classmethod
    def get_by_user_id(cls, user_id: uuid.UUID) -> list["Transaction"]:
        """
        Find all transactions for a user.

        Args:
            user_id: User UUID

        Returns:
            List of Transaction instances

        Example:
            >>> transactions = Transaction.get_by_user_id(user.id)
        """
        return cls.query.filter_by(user_id=user_id).order_by(cls.date.desc()).all()

    @classmethod
    def get_by_user_and_type(
        cls, user_id: uuid.UUID, transaction_type: TransactionType
    ) -> list["Transaction"]:
        """
        Find transactions for a user filtered by type.

        Args:
            user_id: User UUID
            transaction_type: TransactionType.INCOME or TransactionType.EXPENSE

        Returns:
            List of Transaction instances

        Example:
            >>> expenses = Transaction.get_by_user_and_type(
            ...     user.id, TransactionType.EXPENSE
            ... )
        """
        return (
            cls.query.filter_by(user_id=user_id, transaction_type=transaction_type)
            .order_by(cls.date.desc())
            .all()
        )


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "Transaction",
]
