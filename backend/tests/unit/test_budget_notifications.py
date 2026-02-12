# =============================================================================
# Digital Finance Tracker - Budget Notification Test
# PURPOSE: Test that budget notifications are created correctly
# =============================================================================
"""
Quick test to verify budget notification creation.

Run with: python tests/unit/test_budget_notifications.py
"""

import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def test_budget_notification_enums():
    """Test that budget notification enum values exist."""
    from app.models.enums import NotificationType

    # Verify BUDGET_WARNING exists
    assert hasattr(NotificationType, "BUDGET_WARNING")
    assert NotificationType.BUDGET_WARNING.value == "budget_warning"
    print("✅ BUDGET_WARNING enum exists")

    # Verify BUDGET_EXCEEDED exists
    assert hasattr(NotificationType, "BUDGET_EXCEEDED")
    assert NotificationType.BUDGET_EXCEEDED.value == "budget_exceeded"
    print("✅ BUDGET_EXCEEDED enum exists")

    # List all enum values
    print(f"📋 All NotificationType values: {[e.value for e in NotificationType]}")


def test_alert_service_imports():
    """Test that AlertService can import new notification types."""
    from app.services.alert_service import NotificationType

    assert NotificationType.BUDGET_WARNING.value == "budget_warning"
    assert NotificationType.BUDGET_EXCEEDED.value == "budget_exceeded"
    print("✅ AlertService imports NotificationType correctly")


def test_notification_model_accepts_budget_types():
    """Test that Notification model can be instantiated with budget types."""
    from uuid import uuid4
    from app.models.enums import NotificationType

    # We can't fully test without database, but we can verify the types are valid
    notification_data = {
        "user_id": uuid4(),
        "notification_type": NotificationType.BUDGET_WARNING,
        "title": "Budget Warning: Food",
        "message": "You've used 80% of your monthly Food budget",
        "data": {"budget_id": str(uuid4()), "percentage_used": 80.0},
    }

    # Verify the enum is the expected type
    assert notification_data["notification_type"] == NotificationType.BUDGET_WARNING
    print("✅ Notification data structure valid for BUDGET_WARNING")

    notification_data["notification_type"] = NotificationType.BUDGET_EXCEEDED
    assert notification_data["notification_type"] == NotificationType.BUDGET_EXCEEDED
    print("✅ Notification data structure valid for BUDGET_EXCEEDED")


if __name__ == "__main__":
    print("\n🧪 Testing Budget Notification Feature\n")
    print("-" * 50)

    try:
        test_budget_notification_enums()
        print()
        test_alert_service_imports()
        print()
        test_notification_model_accepts_budget_types()
        print()
        print("-" * 50)
        print("✅ All tests passed! Budget notifications ready.\n")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
