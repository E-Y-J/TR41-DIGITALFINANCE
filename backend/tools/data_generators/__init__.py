# =============================================================================
# Digital Finance Tracker - Data Generators Package
# PURPOSE: Modular test data generation system for comprehensive testing
# =============================================================================
"""
Data Generators Package

This package provides a modular system for generating comprehensive test data.
Each generator handles a specific domain of data.

Generators:
    - BaseGenerator: Common utilities and configuration
    - RecurringGenerator: Subscriptions and recurring bills
    - IncomeGenerator: Salary, freelance, refunds
    - DailySpendingGenerator: Daily transaction patterns
    - AnomalyGenerator: Anomaly detection test cases
    - AISessionGenerator: AI chat session conversations
    - BudgetGenerator: Budget limits and tracking
    - NotificationGenerator: User notifications
    - AlertGenerator: Financial alerts
    - LoanGenerator: Loan data

Usage:
    from tools.data_generators import JaeDataGenerator

    generator = JaeDataGenerator(user, categories)
    generator.generate_all()
"""

from tools.data_generators.base import BaseGenerator
from tools.data_generators.jae_generator import JaeDataGenerator

__all__ = [
    "BaseGenerator",
    "JaeDataGenerator",
]
