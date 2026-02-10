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
# CATEGORY ENUMS
# =============================================================================


class CategoryType(enum.Enum):
    """
    Category transaction type association.

    Indicates what type of transactions a category applies to.

    Values:
        INCOME: Category only for income transactions (e.g., Salary)
        EXPENSE: Category only for expense transactions (e.g., Food & Dining)
        BOTH: Category can be either (e.g., Unknown)

    AI Categorization:
        Used to match categories to transaction types.

    Example:
        >>> category.category_type = CategoryType.EXPENSE
        >>> category.category_type.value
        'expense'
    """

    INCOME = "income"
    EXPENSE = "expense"
    BOTH = "both"


# =============================================================================
# NOTIFICATION ENUMS
# =============================================================================


class NotificationStatus(enum.Enum):
    """
    Notification read status enumeration.

    Values:
        UNREAD: Notification has not been read
        READ: Notification has been read

    Notification System:
        Used to track which notifications user has seen.

    Example:
        >>> notification.status = NotificationStatus.UNREAD
        >>> notification.status.value
        'unread'
    """

    UNREAD = "unread"
    READ = "read"


class NotificationType(enum.Enum):
    """
    Notification type enumeration.

    Defines the notification types for the application.

    Values:
        DEFAULT: Generic/system notification
        NEW_TRANSACTION: Transaction created notification
        DELETED_TRANSACTION: Transaction deleted notification
        EDITED_PROFILE: Profile updated notification
        WEEKLY_SUMMARY_READY: Weekly AI summary available
        CATEGORY_UPDATED: AI re-categorized a transaction
        AI_CLARIFICATION: AI needs user clarification for categorization

    Notification System:
        Types requested by frontend team for notification UI.

    Example:
        >>> notification.type = NotificationType.NEW_TRANSACTION
        >>> notification.type.value
        'new_transaction'
    """

    DEFAULT = "default"
    NEW_TRANSACTION = "new_transaction"
    DELETED_TRANSACTION = "deleted_transaction"
    EDITED_PROFILE = "edited_profile"
    WEEKLY_SUMMARY_READY = "weekly_summary_ready"
    CATEGORY_UPDATED = "category_updated"
    AI_CLARIFICATION = "ai_clarification"


class AISource(enum.Enum):
    """
    AI categorization source enumeration.

    Tracks which system assigned the category to a transaction.

    Values:
        KEYWORD: Category assigned by keyword matching (rule-based)
        HUGGINGFACE: Category assigned by HuggingFace model
        GEMINI: Category assigned by Gemini API (fallback)
        USER: Category manually set by user (override)

    AI Categorization:
        KEYWORD is for rule-based matching (no AI needed).
        HUGGINGFACE/GEMINI track which AI model was used.
        USER indicates manual override by user.

    Example:
        >>> transaction.ai_source = AISource.KEYWORD
        >>> transaction.ai_source.value
        'keyword'
    """

    KEYWORD = "keyword"
    HUGGINGFACE = "huggingface"
    GEMINI = "gemini"
    USER = "user"


# =============================================================================
# ALERT ENUMS (Foundation)
# =============================================================================


class AlertType(enum.Enum):
    """
    Alert type enumeration.

    Defines types of financial alerts the system can generate.

    Values:
        HIGH_SPENDING: Spending exceeds baseline in a category
        LARGE_TRANSACTION: Single transaction exceeds threshold
        UNUSUAL_CATEGORY: Spending in unusual category for user
        BUDGET_WARNING: Approaching budget limit
        BUDGET_EXCEEDED: Budget exceeded

    Alert System:
        Foundation for anomaly detection. Detection logic in alert_service.

    Example:
        >>> alert.alert_type = AlertType.HIGH_SPENDING
        >>> alert.alert_type.value
        'high_spending'
    """

    HIGH_SPENDING = "high_spending"
    LARGE_TRANSACTION = "large_transaction"
    UNUSUAL_CATEGORY = "unusual_category"
    BUDGET_WARNING = "budget_warning"
    BUDGET_EXCEEDED = "budget_exceeded"


class AlertSeverity(enum.Enum):
    """
    Alert severity level enumeration.

    Indicates urgency/importance of an alert.

    Values:
        LOW: Informational, minor anomaly
        MEDIUM: Notable, should review
        HIGH: Significant, requires attention
        CRITICAL: Urgent, potential issue

    Alert System:
        Foundation for anomaly detection UI styling.

    Example:
        >>> alert.severity = AlertSeverity.MEDIUM
        >>> alert.severity.value
        'medium'
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# =============================================================================
# BUDGET ENUMS
# =============================================================================


class BudgetType(enum.Enum):
    """
    Budget type enumeration.

    Defines whether a budget applies to total spending or a specific category.

    Values:
        TOTAL: Overall spending limit (no specific category)
        CATEGORY: Limit for a specific spending category

    Budget System:
        - TOTAL budgets have category_id = NULL
        - CATEGORY budgets must have a valid category_id

    Example:
        >>> budget.budget_type = BudgetType.TOTAL
        >>> budget.budget_type.value
        'total'
    """

    TOTAL = "total"
    CATEGORY = "category"


class BudgetPeriod(enum.Enum):
    """
    Budget reset period enumeration.

    Defines how often a budget resets.

    Values:
        WEEKLY: Budget resets every week
        MONTHLY: Budget resets every month

    Budget System:
        - Weekly budgets reset on Monday
        - Monthly budgets reset on the 1st of each month
        - No carry over - unused budget does not roll over

    Example:
        >>> budget.period = BudgetPeriod.MONTHLY
        >>> budget.period.value
        'monthly'
    """

    WEEKLY = "weekly"
    MONTHLY = "monthly"


# =============================================================================
# LOAN ENUMS
# =============================================================================


class LoanStatus(enum.Enum):
    """
    Loan status enumeration (MVP).

    Values:
        OPEN: Loan is active and being paid
        CLOSED: Loan has been fully paid off
    """

    OPEN = "open"
    CLOSED = "closed"


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # User enums
    "AccountStatus",
    "UserRole",
    # Transaction enums
    "TransactionType",
    # Category enums
    "CategoryType",
    # Notification enums
    "NotificationStatus",
    "NotificationType",
    # AI enums
    "AISource",
    # Alert enums (Foundation)
    "AlertType",
    "AlertSeverity",
    # Budget enums
    "BudgetType",
    "BudgetPeriod",
    # Loan enums
    "LoanStatus",
]
