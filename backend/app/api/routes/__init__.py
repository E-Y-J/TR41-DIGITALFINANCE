# =============================================================================
# Digital Finance Tracker - API Route Blueprints
# PURPOSE: Export all route blueprints for registration
# =============================================================================
"""
Routes Package

This package contains all API route blueprints.

Usage:
    from app.api.routes import users_bp, transactions_bp

AI Foundation Routes:
    - categories_bp: Category endpoints (GET only)
    - notifications_bp: Notification CRUD endpoints
    - summary_bp: Spending summary and analytics endpoints
    - alerts_bp: Alert endpoints (list, dismiss)
"""

from app.api.routes.auth import bp as auth_bp
from app.api.routes.users import bp as users_bp
from app.api.routes.transactions import bp as transactions_bp
from app.api.routes.test import bp as test_bp

# AI Foundation: Categorization, Notifications & Analytics
from app.api.routes.categories import bp as categories_bp
from app.api.routes.notifications import bp as notifications_bp
from app.api.routes.summary import bp as summary_bp
from app.api.routes.alerts import alerts_bp
from app.api.routes.budgets import bp as budgets_bp

__all__ = [
    # Core routes
    "auth_bp",
    "users_bp",
    "transactions_bp",
    "test_bp",
    # AI Foundation routes
    "categories_bp",
    "notifications_bp",
    "summary_bp",
    "alerts_bp",
    "budgets_bp",
]
