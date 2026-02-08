# =============================================================================
# Digital Finance Tracker - Alert Generator
# PURPOSE: Generate financial alert records for testing anomaly detection
# =============================================================================
"""
Alert Generator

Generates financial alert records for testing:
- High spending alerts
- Large transaction alerts
- Unusual category alerts
- Budget warning alerts
- Budget exceeded alerts

Enables testing of:
- Alert display and management
- Alert severity levels
- Alert dismissal
- Alert-triggered actions
"""

from typing import List, Tuple, TYPE_CHECKING

from tools.data_generators.base import BaseGenerator

if TYPE_CHECKING:
    from app.core.extensions import db


class AlertGenerator(BaseGenerator):
    """
    Generator for financial alert records.

    Creates alerts matching the anomaly transactions and budget patterns.
    """

    def generate(self, db_session) -> int:
        """
        Generate alert records.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            Number of alerts created
        """
        from app.models.alert import Alert
        from app.models.enums import AlertType, AlertSeverity

        count = 0
        max_days = min(self.months_back * 30, 90)  # Max 90 days of alerts

        # Large transaction alerts
        large_tx_alerts = [
            ("Large Transaction Detected", "$2,450.00 at Louis Vuitton exceeds typical spending by 15x",
             AlertSeverity.HIGH, 3, "Shopping & Retail", {"amount": 2450.00, "typical": 163.00}),
            ("Large Transaction Detected", "$8,500.00 at Rolex is significantly above average",
             AlertSeverity.CRITICAL, 45, "Shopping & Retail", {"amount": 8500.00, "typical": 163.00}),
            ("Large Transaction", "$1,250.00 Emergency Room charge detected",
             AlertSeverity.MEDIUM, 20, "Healthcare & Medical", {"amount": 1250.00}),
            ("Large Purchase Alert", "$3,500.00 furniture purchase exceeds monthly average",
             AlertSeverity.MEDIUM, 180, "Shopping & Retail", {"amount": 3500.00}),
            ("Large Transaction", "$4,200.00 vacation package booked",
             AlertSeverity.MEDIUM, 200, "Entertainment & Recreation", {"amount": 4200.00}),
        ]

        for title, msg, severity, days_ago, cat_name, data in large_tx_alerts:
            if days_ago > max_days:
                continue

            category = self.get_category(cat_name)
            created_at = self.get_date_days_ago(days_ago)
            is_dismissed = days_ago > 14  # Older alerts are dismissed

            alert = Alert(
                user_id=self.user.id,
                alert_type=AlertType.LARGE_TRANSACTION,
                severity=severity,
                title=title,
                message=msg,
                is_dismissed=is_dismissed,
                dismissed_at=created_at if is_dismissed else None,
                category_id=category.id if category else None,
                data=data,
                created_at=created_at,
            )
            db_session.add(alert)
            count += 1

        # High spending alerts
        high_spending_alerts = [
            ("High Spending Alert", "Food & Dining spending is 34% above your 3-month average",
             AlertSeverity.MEDIUM, 7, "Food & Dining", {"current": 687, "average": 512, "increase_pct": 34}),
            ("Category Spike", "Entertainment spending increased 85% this week",
             AlertSeverity.LOW, 14, "Entertainment & Recreation", {"current": 245, "average": 132}),
            ("Unusual Spending", "Shopping expenses are 2x your typical monthly amount",
             AlertSeverity.MEDIUM, 21, "Shopping & Retail", {"current": 912, "typical": 456}),
            ("High Spending", "Transportation costs spiked due to rideshare usage",
             AlertSeverity.LOW, 28, "Transportation", {"uber_rides": 12, "typical": 4}),
        ]

        for title, msg, severity, days_ago, cat_name, data in high_spending_alerts:
            if days_ago > max_days:
                continue

            category = self.get_category(cat_name)
            created_at = self.get_date_days_ago(days_ago)
            is_dismissed = days_ago > 10

            alert = Alert(
                user_id=self.user.id,
                alert_type=AlertType.HIGH_SPENDING,
                severity=severity,
                title=title,
                message=msg,
                is_dismissed=is_dismissed,
                dismissed_at=created_at if is_dismissed else None,
                category_id=category.id if category else None,
                data=data,
                created_at=created_at,
            )
            db_session.add(alert)
            count += 1

        # Unusual category alerts
        unusual_alerts = [
            ("Unusual Purchase", "First transaction at 'Bail Bonds' - please verify",
             AlertSeverity.HIGH, 100, "Financial Services", {"merchant": "Bail Bonds Inc", "first_time": True}),
            ("New Merchant Category", "First purchase in Government & Legal category",
             AlertSeverity.LOW, 45, "Government & Legal", {"first_time_category": True}),
            ("Late Night Activity", "Multiple transactions after midnight detected",
             AlertSeverity.MEDIUM, 8, None, {"time": "2:30 AM", "count": 2}),
            ("Multiple Same-Day", "4 gas station charges on the same day - road trip?",
             AlertSeverity.LOW, 15, "Transportation", {"count": 4, "total": 213.00}),
        ]

        for title, msg, severity, days_ago, cat_name, data in unusual_alerts:
            if days_ago > max_days:
                continue

            category = self.get_category(cat_name) if cat_name else None
            created_at = self.get_date_days_ago(days_ago)
            is_dismissed = days_ago > 20

            alert = Alert(
                user_id=self.user.id,
                alert_type=AlertType.UNUSUAL_CATEGORY,
                severity=severity,
                title=title,
                message=msg,
                is_dismissed=is_dismissed,
                dismissed_at=created_at if is_dismissed else None,
                category_id=category.id if category else None,
                data=data,
                created_at=created_at,
            )
            db_session.add(alert)
            count += 1

        # Budget warning alerts (approaching limit)
        budget_warnings = [
            ("Budget Warning", "Food & Dining is at 85% of monthly budget ($510 of $600)",
             AlertSeverity.MEDIUM, 5, "Food & Dining", {"spent": 510, "budget": 600, "pct": 85}),
            ("Budget Warning", "Shopping approaching limit - $380 of $400 used",
             AlertSeverity.LOW, 8, "Shopping & Retail", {"spent": 380, "budget": 400, "pct": 95}),
            ("Weekly Budget Alert", "Entertainment at 90% of weekly budget",
             AlertSeverity.LOW, 3, "Entertainment & Recreation", {"spent": 72, "budget": 80, "pct": 90}),
        ]

        for title, msg, severity, days_ago, cat_name, data in budget_warnings:
            if days_ago > max_days:
                continue

            category = self.get_category(cat_name)
            created_at = self.get_date_days_ago(days_ago)

            alert = Alert(
                user_id=self.user.id,
                alert_type=AlertType.BUDGET_WARNING,
                severity=severity,
                title=title,
                message=msg,
                is_dismissed=False,
                category_id=category.id if category else None,
                data=data,
                created_at=created_at,
            )
            db_session.add(alert)
            count += 1

        # Budget exceeded alerts
        budget_exceeded = [
            ("Budget Exceeded", "Food & Dining exceeded by $87 (114% of budget)",
             AlertSeverity.HIGH, 2, "Food & Dining", {"spent": 687, "budget": 600, "over": 87}),
            ("Budget Exceeded", "Shopping over by $23 this month",
             AlertSeverity.MEDIUM, 4, "Shopping & Retail", {"spent": 423, "budget": 400, "over": 23}),
            ("Weekly Budget Exceeded", "Entertainment weekly budget exceeded",
             AlertSeverity.LOW, 1, "Entertainment & Recreation", {"spent": 95, "budget": 80, "over": 15}),
        ]

        for title, msg, severity, days_ago, cat_name, data in budget_exceeded:
            if days_ago > max_days:
                continue

            category = self.get_category(cat_name)
            created_at = self.get_date_days_ago(days_ago)

            alert = Alert(
                user_id=self.user.id,
                alert_type=AlertType.BUDGET_EXCEEDED,
                severity=severity,
                title=title,
                message=msg,
                is_dismissed=False,
                category_id=category.id if category else None,
                data=data,
                created_at=created_at,
            )
            db_session.add(alert)
            count += 1

        self.stdout_write(f"   Created {count} alerts", indent=3)
        return count
