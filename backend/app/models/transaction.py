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

from sqlalchemy import String, DateTime, Numeric, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.extensions import db
from app.models.enums import TransactionType

if TYPE_CHECKING:
    from app.models.user import User


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
        Enum(TransactionType, name="transaction_type_enum", native_enum=False),
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

    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Transaction category",
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
        # Composite index for user + category queries
        db.Index("idx_transaction_user_category", "user_id", "category"),
    )

    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================

    # Many Transactions belong to one User (N:1 relationship)
    user: Mapped["User"] = relationship(
        "User",
        back_populates="transactions",
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
        """
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "amount": str(self.amount),
            "transaction_type": self.transaction_type.value,
            "date": self.date,
            "merchant_name": self.merchant_name,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

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
