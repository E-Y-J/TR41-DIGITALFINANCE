# =============================================================================
# Digital Finance Tracker - SQLAlchemy Database Models
# PURPOSE: Export all database models for easy imports
# =============================================================================
"""
Models Package

This package contains all SQLAlchemy database models.

Usage:
    from app.models import User, Transaction
    from app.models import AccountStatus, UserRole, TransactionType
    from app.models import Budget, BudgetType, BudgetPeriod

AI Foundation Additions:
    - Category model for transaction categorization
    - Notification model for user notifications
    - Alert model for financial anomaly alerts (foundation)
    - Budget model for user spending limits
    - New enums: CategoryType, NotificationStatus, NotificationType, AISource
    - Alert enums: AlertType, AlertSeverity
    - Budget enums: BudgetType, BudgetPeriod
"""

# Import enums from centralized location
from app.models.enums import (
    # User enums
    AccountStatus,
    UserRole,
    # Transaction enums
    TransactionType,
    # Category enums
    CategoryType,
    # Notification enums
    NotificationStatus,
    NotificationType,
    # AI enums
    AISource,
    # Alert enums (Foundation)
    AlertType,
    AlertSeverity,
    # Budget enums
    BudgetType,
    BudgetPeriod,
)

# Import models
from app.models.user import User
from app.models.transaction import Transaction
from app.models.loan import Loan

# AI Foundation models
from app.models.category import Category
from app.models.notification import Notification
from app.models.alert import Alert
from app.models.budget import Budget

__all__ = [
    # =========================================================================
    # Enums (from enums.py)
    # =========================================================================
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
    # =========================================================================
    # Models
    # =========================================================================
    "User",
    "Transaction",
    # AI Foundation models
    "Category",
    "Notification",
    "Alert",
    "Budget",
    "Loan",
]
