# =============================================================================
# Digital Finance Tracker - Loan Model
# PURPOSE: Store user loan data (MVP)
# =============================================================================

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import CheckConstraint, String, Date, DateTime, Numeric, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.extensions import db
from app.models.enums import LoanStatus

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.budget import Budget
    from app.models.category import Category


class Loan(db.Model):
    """
    Loan model representing a user's loan or debt obligation.

    MVP Scope:
        - Tracks original and remaining balance
        - Supports active vs closed loans
        - Categorized under Financial Services by default (service layer assigns default)
    """

    __tablename__ = "loans"

    __table_args__ = (
        CheckConstraint(
            "original_amount >= 0",
            name="ck_loan_original_amount_positive",
        ),
        CheckConstraint(
            "remaining_amount >= 0",
            name="ck_loan_remaining_amount_positive",
        ),
        CheckConstraint(
            "remaining_amount <= original_amount",
            name="ck_loan_remaining_lte_original",
        ),
    )
    
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
    # FOREIGN KEYS
    # =========================================================================

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Owner of the loan",
    )

    budget_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("budgets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Optional budget association",
    )

    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id"),
        nullable=False,
        index=True,
        doc="Loan category (default: Financial Services)",
    )

    # =========================================================================
    # LOAN FIELDS
    # =========================================================================

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Loan name (e.g. Car Loan, Student Loan)",
    )

    original_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        doc="Original loan amount",
    )

    remaining_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        doc="Remaining loan balance",
    )

    start_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        doc="Loan start date",
    )

    end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        doc="Loan payoff/closure date",
    )

    status: Mapped[LoanStatus] = mapped_column(
        Enum(
            LoanStatus,
            name="loan_status_enum",
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
            validate_strings=True,
        ),
        default=LoanStatus.OPEN,
        nullable=False,
        index=True,
        doc="Loan status: open or closed",
    )

    # =========================================================================
    # TIMESTAMPS
    # =========================================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================

    user: Mapped["User"] = relationship(
        "User",
        backref="loans",
    )

    budget: Mapped[Optional["Budget"]] = relationship(
        "Budget",
        backref="loans",
    )

    category: Mapped["Category"] = relationship(
        "Category",
        backref="loans",
    )

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def progress_percentage(self) -> int:
        """
        Percentage of loan paid off.

        Used by frontend progress ring.

        Safe calculation: prevents negative values or >100%.
        """
        if self.original_amount == 0:
            return 0

        paid = max(self.original_amount - self.remaining_amount, Decimal("0"))
        percentage = (paid / self.original_amount) * 100
        return min(round(percentage), 100)

    # =========================================================================
    # REPRESENTATION
    # =========================================================================

    def __repr__(self) -> str:
        return f"<Loan {self.name} ({self.status.value}) id={self.id}>"
