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

AI Foundation Additions:
    - Category model for transaction categorization
    - Notification model for user notifications
    - Alert model for financial anomaly alerts (foundation)
    - New enums: CategoryType, NotificationStatus, NotificationType, AISource
    - Alert enums: AlertType, AlertSeverity
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
)

# Import models
from app.models.user import User
from app.models.transaction import Transaction

# AI Foundation models
from app.models.category import Category
from app.models.notification import Notification
from app.models.alert import Alert

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
    # =========================================================================
    # Models
    # =========================================================================
    "User",
    "Transaction",
    # AI Foundation models
    "Category",
    "Notification",
    "Alert",
]
