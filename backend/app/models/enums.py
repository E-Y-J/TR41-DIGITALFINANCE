# =============================================================================
# Digital Finance Tracker - Database Enums
# PURPOSE: Shared enumeration types for database models
# =============================================================================
"""
Enums Module

This module defines all enumeration types used across database models.
Centralizing enums here provides:
- Single source of truth for enum values
- Easy reuse across models
- Simpler imports and maintenance

Usage:
    from app.models.enums import AccountStatus, UserRole, TransactionType

    # Check user status
    if user.account_status == AccountStatus.ACTIVE:
        allow_access()

    # Create transaction
    transaction = Transaction(
        transaction_type=TransactionType.EXPENSE,
        ...
    )
"""

import enum


# =============================================================================
# USER ENUMS
# =============================================================================


class AccountStatus(enum.Enum):
    """
    User account status enumeration.

    Values:
        PENDING: Account created but not fully activated
        ACTIVE: Account is active and in good standing
        SUSPENDED: Account has been suspended

    Example:
        >>> user.account_status = AccountStatus.ACTIVE
        >>> user.account_status.value
        'active'
    """

    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class UserRole(enum.Enum):
    """
    User role enumeration for access control.

    Values:
        USER: Regular user with standard permissions
        ADMIN: Administrator with elevated permissions

    Example:
        >>> if user.role == UserRole.ADMIN:
        ...     show_admin_panel()
    """

    USER = "user"
    ADMIN = "admin"


# =============================================================================
# TRANSACTION ENUMS
# =============================================================================


class TransactionType(enum.Enum):
    """
    Transaction type enumeration.

    Values:
        INCOME: Money received (salary, refunds, gifts, etc.)
        EXPENSE: Money spent (purchases, bills, etc.)

    Example:
        >>> transaction.transaction_type = TransactionType.INCOME
        >>> transaction.transaction_type.value
        'income'
    """

    INCOME = "income"
    EXPENSE = "expense"


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "AccountStatus",
    "UserRole",
    "TransactionType",
]
