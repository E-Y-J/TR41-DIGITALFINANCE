# =============================================================================
# Digital Finance Tracker - Notification Generator
# PURPOSE: Generate notification history for testing notification features
# =============================================================================
"""
Notification Generator

Generates notification records for testing:
- Transaction notifications (created, deleted)
- Weekly summary notifications
- Category update notifications
- Profile edit notifications
- AI clarification requests

Enables testing of:
- Notification display
- Read/unread status
- Notification filtering
- Notification dismissal
"""

import random
from datetime import timedelta
from typing import List, Dict, Any, TYPE_CHECKING

from tools.data_generators.base import BaseGenerator

if TYPE_CHECKING:
    from app.core.extensions import db


class NotificationGenerator(BaseGenerator):
    """
    Generator for notification records.

    Creates realistic notification history matching transaction patterns.
    """

    def generate(self, db_session) -> int:
        """
        Generate notification records.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            Number of notifications created
        """
        from app.models.notification import Notification
        from app.models.enums import NotificationType, NotificationStatus

        count = 0
        max_days = min(self.months_back * 30, 90)  # Max 90 days of notifications

        # New transaction notifications (most common)
        new_tx_notifications = [
            ("New transaction: -$45.00 at Target", 1, "expense"),
            ("New transaction: -$8.50 at Starbucks", 2, "expense"),
            ("New transaction: -$125.00 at Amazon", 3, "expense"),
            ("New transaction: +$3,250.00 from TechCorp Inc.", 1, "income"),
            ("New transaction: -$65.00 at Shell", 4, "expense"),
            ("New transaction: -$35.00 at Uber", 5, "expense"),
            ("New transaction: -$89.00 at Trader Joe's", 6, "expense"),
            ("New transaction: +$285.00 from Upwork", 8, "income"),
            ("New transaction: -$15.99 at Netflix", 5, "expense"),
            ("New transaction: -$250.00 at Best Buy", 10, "expense"),
            ("New transaction: -$1,850.00 for Rent", 1, "expense"),
            ("New transaction: -$127.50 at PG&E", 3, "expense"),
            ("New transaction: +$50.00 from Venmo", 12, "income"),
            ("New transaction: -$45.00 at DoorDash", 7, "expense"),
            ("New transaction: -$15.00 at Parking", 8, "expense"),
            ("New transaction: +$3,280.00 from TechCorp Inc.", 15, "income"),
            ("New transaction: -$95.00 at AT&T", 10, "expense"),
            ("New transaction: -$24.99 at Planet Fitness", 1, "expense"),
            ("New transaction: -$350.00 at Kaiser", 1, "expense"),
            ("New transaction: -$145.00 for Car Insurance", 18, "expense"),
        ]

        for msg, days_ago, tx_type in new_tx_notifications:
            if days_ago > max_days:
                continue

            created_at = self.get_date_days_ago(days_ago)
            # Older notifications are read, newer ones may be unread
            status = NotificationStatus.READ if days_ago > 3 else (
                NotificationStatus.UNREAD if random.random() < 0.4 else NotificationStatus.READ
            )

            notification = Notification(
                user_id=self.user.id,
                notification_type=NotificationType.NEW_TRANSACTION,
                status=status,
                title="Transaction Added",
                message=msg,
                data={"transaction_type": tx_type},
                created_at=created_at,
            )
            db_session.add(notification)
            count += 1

        # Weekly summary notifications
        for week in range(min(12, self.months_back * 4)):
            days_ago = (week + 1) * 7
            if days_ago > max_days:
                continue

            created_at = self.get_date_days_ago(days_ago)
            week_num = self.months_back * 4 - week

            notification = Notification(
                user_id=self.user.id,
                notification_type=NotificationType.WEEKLY_SUMMARY_READY,
                status=NotificationStatus.READ,
                title="Weekly Summary Ready",
                message=f"Your week {week_num} spending summary is ready. You spent $842.50 across 35 transactions.",
                data={"week_number": week_num, "total_spent": 842.50},
                created_at=created_at,
            )
            db_session.add(notification)
            count += 1

        # Category updated notifications (AI re-categorization)
        category_updates = [
            ("AI categorized 'Amazon Business' as Utilities & Services", 5),
            ("AI updated 'Apple Store' from Shopping to Entertainment", 12),
            ("'Costco Gas' recategorized to Transportation", 18),
            ("AI matched 'Local Restaurant' to Food & Dining", 25),
            ("'Insurance Payment' categorized as Financial Services", 32),
        ]

        for msg, days_ago in category_updates:
            if days_ago > max_days:
                continue

            created_at = self.get_date_days_ago(days_ago)

            notification = Notification(
                user_id=self.user.id,
                notification_type=NotificationType.CATEGORY_UPDATED,
                status=NotificationStatus.READ,
                title="Category Updated",
                message=msg,
                data={"auto_categorized": True},
                created_at=created_at,
            )
            db_session.add(notification)
            count += 1

        # Profile edit notifications
        profile_edits = [
            ("Your email preferences have been updated", 15),
            ("Notification settings saved successfully", 28),
            ("Profile picture updated", 45),
            ("Display name changed to 'Jae'", 60),
        ]

        for msg, days_ago in profile_edits:
            if days_ago > max_days:
                continue

            created_at = self.get_date_days_ago(days_ago)

            notification = Notification(
                user_id=self.user.id,
                notification_type=NotificationType.EDITED_PROFILE,
                status=NotificationStatus.READ,
                title="Profile Updated",
                message=msg,
                data={},
                created_at=created_at,
            )
            db_session.add(notification)
            count += 1

        # AI clarification requests
        clarifications = [
            ("Is 'AMZ*Services' an Amazon subscription or purchase?", 8),
            ("Should 'PAYPAL*' transactions be categorized as the underlying merchant?", 22),
            ("I noticed 3 similar charges - are these duplicates?", 35),
        ]

        for msg, days_ago in clarifications:
            if days_ago > max_days:
                continue

            created_at = self.get_date_days_ago(days_ago)
            status = NotificationStatus.UNREAD if days_ago < 10 else NotificationStatus.READ

            notification = Notification(
                user_id=self.user.id,
                notification_type=NotificationType.AI_CLARIFICATION,
                status=status,
                title="Clarification Needed",
                message=msg,
                data={"requires_response": True},
                created_at=created_at,
            )
            db_session.add(notification)
            count += 1

        # Deleted transaction notifications
        deleted_notifications = [
            ("Transaction deleted: -$25.00 at duplicate charge", 10),
            ("Transaction deleted: -$0.00 at test transaction", 20),
        ]

        for msg, days_ago in deleted_notifications:
            if days_ago > max_days:
                continue

            created_at = self.get_date_days_ago(days_ago)

            notification = Notification(
                user_id=self.user.id,
                notification_type=NotificationType.DELETED_TRANSACTION,
                status=NotificationStatus.READ,
                title="Transaction Deleted",
                message=msg,
                data={},
                created_at=created_at,
            )
            db_session.add(notification)
            count += 1

        self.stdout_write(f"   Created {count} notifications", indent=3)
        return count
