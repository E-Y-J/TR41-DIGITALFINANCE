# =============================================================================
# Digital Finance Tracker - Business Logic Services
# PURPOSE: Export all service classes for easy imports
# =============================================================================
"""
Services Package

This package contains all business logic services.

Usage:
    from app.services import UserService, TransactionService

AI FOUNDATION ADDITIONS:
    - CategoryService: Category operations (mostly read-only)
    - NotificationService: Notification CRUD and status management
    - SummaryService: Spending summaries and analytics
    - AlertService: Financial anomaly alerts
"""

from app.services.user_service import UserService
from app.services.transaction_service import TransactionService

# AI Foundation: Categories, Notifications, Alerts, Summary
from app.services.category_service import CategoryService
from app.services.notification_service import NotificationService
from app.services.summary_service import SummaryService
from app.services.alert_service import AlertService
from app.services.budget_service import BudgetService

__all__ = [
    # Core services
    "UserService",
    "TransactionService",
    # AI Foundation services
    "CategoryService",
    "NotificationService",
    "SummaryService",
    "AlertService",
    "BudgetService",
]
