#!/usr/bin/env python3
# =============================================================================
# Digital Finance Tracker - Data Generators Test Script
# PURPOSE: Test all data generators without database connection
# =============================================================================
"""
Comprehensive test for the modular data generator system.

Tests:
- All imports work correctly
- All generators can be instantiated
- All generators produce correct data structures
- Transaction counts are within expected ranges
- AI sessions have valid conversation formats
- All enums and models are correctly referenced
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from typing import List, Optional
import uuid

# Setup path
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))


# ==============================================================================
# MOCK CLASSES
# ==============================================================================

@dataclass
class MockCategory:
    """Mock Category model for testing."""
    id: str
    name: str
    category_type: str = "expense"

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class MockUser:
    """Mock User model for testing."""
    id: str
    email: str
    auth0_id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


class MockDBSession:
    """Mock database session that collects records."""

    def __init__(self):
        self.records = []
        self.committed = False

    def add(self, record):
        self.records.append(record)

    def commit(self):
        self.committed = True

    def get_records_by_type(self, type_name: str) -> List:
        return [r for r in self.records if type(r).__name__ == type_name]


# ==============================================================================
# TEST FUNCTIONS
# ==============================================================================

def create_mock_categories() -> List[MockCategory]:
    """Create mock categories matching the real system."""
    categories = [
        MockCategory(id=str(uuid.uuid4()), name="Food & Dining", category_type="expense"),
        MockCategory(id=str(uuid.uuid4()), name="Transportation", category_type="expense"),
        MockCategory(id=str(uuid.uuid4()), name="Shopping & Retail", category_type="expense"),
        MockCategory(id=str(uuid.uuid4()), name="Entertainment & Recreation", category_type="expense"),
        MockCategory(id=str(uuid.uuid4()), name="Utilities & Services", category_type="expense"),
        MockCategory(id=str(uuid.uuid4()), name="Healthcare & Medical", category_type="expense"),
        MockCategory(id=str(uuid.uuid4()), name="Financial Services", category_type="expense"),
        MockCategory(id=str(uuid.uuid4()), name="Government & Legal", category_type="expense"),
        MockCategory(id=str(uuid.uuid4()), name="Income", category_type="income"),
        MockCategory(id=str(uuid.uuid4()), name="Uncategorized", category_type="both"),
    ]
    return categories


def create_mock_user() -> MockUser:
    """Create mock user for Jae Young Seo."""
    return MockUser(
        id=str(uuid.uuid4()),
        email="jaeyseo0922@gmail.com",
        auth0_id="google-oauth2|110513262768393412869"
    )


def test_imports():
    """Test that all imports work correctly."""
    print("\n" + "=" * 60)
    print("TEST 1: Import Verification")
    print("=" * 60)

    try:
        from tools.data_generators import JaeDataGenerator, BaseGenerator
        print("✅ Package imports successful")

        from tools.data_generators.recurring import RecurringGenerator
        print("✅ RecurringGenerator imported")

        from tools.data_generators.income import IncomeGenerator
        print("✅ IncomeGenerator imported")

        from tools.data_generators.daily_spending import DailySpendingGenerator
        print("✅ DailySpendingGenerator imported")

        from tools.data_generators.anomalies import (
            AnomalyGenerator, UserOverrideGenerator, GovernmentLegalGenerator
        )
        print("✅ Anomaly generators imported")

        from tools.data_generators.ai_sessions import AISessionGenerator
        print("✅ AISessionGenerator imported")

        from tools.data_generators.budgets import BudgetGenerator
        print("✅ BudgetGenerator imported")

        from tools.data_generators.notifications import NotificationGenerator
        print("✅ NotificationGenerator imported")

        from tools.data_generators.alerts import AlertGenerator
        print("✅ AlertGenerator imported")

        from tools.data_generators.loans import LoanGenerator
        print("✅ LoanGenerator imported")

        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_base_generator():
    """Test BaseGenerator functionality."""
    print("\n" + "=" * 60)
    print("TEST 2: BaseGenerator Utilities")
    print("=" * 60)

    from tools.data_generators.base import BaseGenerator

    user = create_mock_user()
    categories = create_mock_categories()

    generator = BaseGenerator(user=user, categories=categories, months_back=12)

    # Test category lookup
    food_cat = generator.get_category("Food & Dining")
    assert food_cat is not None, "Food & Dining category not found"
    print(f"✅ Category lookup works: {food_cat.name}")

    # Test date generation
    date_30_days_ago = generator.get_date_days_ago(30)
    assert date_30_days_ago < datetime.now(timezone.utc), "Date should be in the past"
    print(f"✅ Date generation works: {date_30_days_ago.date()}")

    # Test random amount
    amount = generator.random_amount(10.0, 50.0)
    assert 10.0 <= amount <= 50.0, f"Amount {amount} out of range"
    print(f"✅ Random amount works: ${amount:.2f}")

    # Test transaction dict creation
    tx_date = generator.get_date_days_ago(5)
    tx_dict = generator.create_transaction_dict(
        amount=Decimal("25.50"),
        transaction_type="expense",
        date=tx_date,
        merchant_name="Test Merchant",
        category_name="Food & Dining",
    )
    assert tx_dict is not None, "Transaction dict creation failed"
    assert tx_dict["amount"] == Decimal("25.50"), "Amount conversion failed"
    assert tx_dict["merchant_name"] == "Test Merchant", "Merchant name wrong"
    print(f"✅ Transaction dict creation works")

    return True


def test_recurring_generator():
    """Test RecurringGenerator output."""
    print("\n" + "=" * 60)
    print("TEST 3: RecurringGenerator")
    print("=" * 60)

    from tools.data_generators.recurring import RecurringGenerator

    user = create_mock_user()
    categories = create_mock_categories()
    db_session = MockDBSession()

    generator = RecurringGenerator(user=user, categories=categories, months_back=12)
    count = generator.generate(db_session)

    print(f"   Generated {count} recurring transactions")

    # Should have 20 templates × ~12 months = ~200-240 transactions
    assert count >= 150, f"Expected at least 150 recurring transactions, got {count}"
    assert count <= 300, f"Expected at most 300 recurring transactions, got {count}"
    print(f"✅ Recurring count in expected range (150-300)")

    # Check transaction structure
    if db_session.records:
        tx = db_session.records[0]
        assert hasattr(tx, 'user_id'), "Transaction missing user_id"
        assert hasattr(tx, 'amount'), "Transaction missing amount"
        assert hasattr(tx, 'merchant_name'), "Transaction missing merchant_name"
        print(f"✅ Transaction structure valid")
        print(f"   Sample: {tx.merchant_name} - ${tx.amount}")

    return True


def test_income_generator():
    """Test IncomeGenerator output."""
    print("\n" + "=" * 60)
    print("TEST 4: IncomeGenerator")
    print("=" * 60)

    from tools.data_generators.income import IncomeGenerator

    user = create_mock_user()
    categories = create_mock_categories()
    db_session = MockDBSession()

    generator = IncomeGenerator(user=user, categories=categories, months_back=12)
    count = generator.generate(db_session)

    print(f"   Generated {count} income transactions")

    # Should have 24 salary + ~12 freelance + ~14 refunds = ~50 transactions
    assert count >= 40, f"Expected at least 40 income transactions, got {count}"
    assert count <= 70, f"Expected at most 70 income transactions, got {count}"
    print(f"✅ Income count in expected range (40-70)")

    # Check for salary transactions
    salary_txs = [r for r in db_session.records if "Payroll" in str(getattr(r, 'merchant_name', ''))]
    assert len(salary_txs) >= 20, f"Expected at least 20 salary transactions, got {len(salary_txs)}"
    print(f"✅ Salary transactions: {len(salary_txs)}")

    return True


def test_daily_spending_generator():
    """Test DailySpendingGenerator output."""
    print("\n" + "=" * 60)
    print("TEST 5: DailySpendingGenerator")
    print("=" * 60)

    from tools.data_generators.daily_spending import DailySpendingGenerator

    user = create_mock_user()
    categories = create_mock_categories()
    db_session = MockDBSession()

    generator = DailySpendingGenerator(user=user, categories=categories, months_back=12)
    count = generator.generate(db_session)

    print(f"   Generated {count} daily spending transactions")

    # Should have ~360 days × 3-4 per day = ~1000-1500 transactions
    assert count >= 800, f"Expected at least 800 daily transactions, got {count}"
    assert count <= 2000, f"Expected at most 2000 daily transactions, got {count}"
    print(f"✅ Daily spending count in expected range (800-2000)")

    # Check variety of merchants
    merchants = set(getattr(r, 'merchant_name', '') for r in db_session.records)
    assert len(merchants) >= 30, f"Expected at least 30 unique merchants, got {len(merchants)}"
    print(f"✅ Unique merchants: {len(merchants)}")

    return True


def test_anomaly_generators():
    """Test anomaly-related generators."""
    print("\n" + "=" * 60)
    print("TEST 6: Anomaly Generators")
    print("=" * 60)

    from tools.data_generators.anomalies import (
        AnomalyGenerator, UserOverrideGenerator, GovernmentLegalGenerator
    )

    user = create_mock_user()
    categories = create_mock_categories()

    # Test AnomalyGenerator
    db_session = MockDBSession()
    generator = AnomalyGenerator(user=user, categories=categories, months_back=12)
    anomaly_count = generator.generate(db_session)
    print(f"   Anomalies: {anomaly_count}")
    assert anomaly_count >= 30, f"Expected at least 30 anomalies, got {anomaly_count}"
    print(f"✅ AnomalyGenerator works")

    # Test UserOverrideGenerator
    db_session = MockDBSession()
    generator = UserOverrideGenerator(user=user, categories=categories, months_back=12)
    override_count = generator.generate(db_session)
    print(f"   User overrides: {override_count}")
    assert override_count >= 10, f"Expected at least 10 overrides, got {override_count}"
    print(f"✅ UserOverrideGenerator works")

    # Test GovernmentLegalGenerator
    db_session = MockDBSession()
    generator = GovernmentLegalGenerator(user=user, categories=categories, months_back=12)
    gov_count = generator.generate(db_session)
    print(f"   Government/Legal: {gov_count}")
    assert gov_count >= 10, f"Expected at least 10 gov transactions, got {gov_count}"
    print(f"✅ GovernmentLegalGenerator works")

    return True


def test_ai_session_generator():
    """Test AISessionGenerator output."""
    print("\n" + "=" * 60)
    print("TEST 7: AISessionGenerator")
    print("=" * 60)

    from tools.data_generators.ai_sessions import AISessionGenerator

    user = create_mock_user()
    categories = create_mock_categories()
    db_session = MockDBSession()

    generator = AISessionGenerator(user=user, categories=categories, months_back=12)
    count = generator.generate(db_session)

    print(f"   Generated {count} AI sessions")

    assert count >= 10, f"Expected at least 10 AI sessions, got {count}"
    assert count <= 20, f"Expected at most 20 AI sessions, got {count}"
    print(f"✅ AI session count in expected range (10-20)")

    # Check session structure
    if db_session.records:
        session = db_session.records[0]
        assert hasattr(session, 'conversation_history'), "Session missing conversation_history"
        assert hasattr(session, 'last_intent'), "Session missing last_intent"

        # Check conversation format
        history = session.conversation_history
        assert isinstance(history, list), "conversation_history should be a list"
        assert len(history) >= 2, "Should have at least one exchange"

        msg = history[0]
        assert "role" in msg, "Message missing role"
        assert "content" in msg, "Message missing content"
        print(f"✅ AI session structure valid")
        print(f"   Sample intent: {session.last_intent}")

    return True


def test_budget_generator():
    """Test BudgetGenerator output."""
    print("\n" + "=" * 60)
    print("TEST 8: BudgetGenerator")
    print("=" * 60)

    from tools.data_generators.budgets import BudgetGenerator

    user = create_mock_user()
    categories = create_mock_categories()
    db_session = MockDBSession()

    generator = BudgetGenerator(user=user, categories=categories, months_back=12)
    count = generator.generate(db_session)

    print(f"   Generated {count} budgets")

    assert count >= 10, f"Expected at least 10 budgets, got {count}"
    assert count <= 20, f"Expected at most 20 budgets, got {count}"
    print(f"✅ Budget count in expected range (10-20)")

    # Check budget structure
    if db_session.records:
        budget = db_session.records[0]
        assert hasattr(budget, 'amount'), "Budget missing amount"
        assert hasattr(budget, 'budget_type'), "Budget missing budget_type"
        assert hasattr(budget, 'period'), "Budget missing period"
        print(f"✅ Budget structure valid")

    return True


def test_notification_generator():
    """Test NotificationGenerator output."""
    print("\n" + "=" * 60)
    print("TEST 9: NotificationGenerator")
    print("=" * 60)

    from tools.data_generators.notifications import NotificationGenerator

    user = create_mock_user()
    categories = create_mock_categories()
    db_session = MockDBSession()

    generator = NotificationGenerator(user=user, categories=categories, months_back=12)
    count = generator.generate(db_session)

    print(f"   Generated {count} notifications")

    assert count >= 40, f"Expected at least 40 notifications, got {count}"
    assert count <= 80, f"Expected at most 80 notifications, got {count}"
    print(f"✅ Notification count in expected range (40-80)")

    # Check notification structure
    if db_session.records:
        notif = db_session.records[0]
        assert hasattr(notif, 'notification_type'), "Notification missing type"
        assert hasattr(notif, 'title'), "Notification missing title"
        assert hasattr(notif, 'message'), "Notification missing message"
        print(f"✅ Notification structure valid")

    return True


def test_alert_generator():
    """Test AlertGenerator output."""
    print("\n" + "=" * 60)
    print("TEST 10: AlertGenerator")
    print("=" * 60)

    from tools.data_generators.alerts import AlertGenerator

    user = create_mock_user()
    categories = create_mock_categories()
    db_session = MockDBSession()

    generator = AlertGenerator(user=user, categories=categories, months_back=12)
    count = generator.generate(db_session)

    print(f"   Generated {count} alerts")

    assert count >= 10, f"Expected at least 10 alerts, got {count}"
    assert count <= 30, f"Expected at most 30 alerts, got {count}"
    print(f"✅ Alert count in expected range (10-30)")

    # Check alert structure
    if db_session.records:
        alert = db_session.records[0]
        assert hasattr(alert, 'alert_type'), "Alert missing type"
        assert hasattr(alert, 'severity'), "Alert missing severity"
        assert hasattr(alert, 'title'), "Alert missing title"
        print(f"✅ Alert structure valid")

    return True


def test_loan_generator():
    """Test LoanGenerator output."""
    print("\n" + "=" * 60)
    print("TEST 11: LoanGenerator")
    print("=" * 60)

    from tools.data_generators.loans import LoanGenerator

    user = create_mock_user()
    categories = create_mock_categories()
    db_session = MockDBSession()

    generator = LoanGenerator(user=user, categories=categories, months_back=12)
    count = generator.generate(db_session)

    print(f"   Generated {count} loans")

    assert count >= 3, f"Expected at least 3 loans, got {count}"
    assert count <= 10, f"Expected at most 10 loans, got {count}"
    print(f"✅ Loan count in expected range (3-10)")

    # Check loan structure
    if db_session.records:
        loan = db_session.records[0]
        assert hasattr(loan, 'name'), "Loan missing name"
        assert hasattr(loan, 'original_amount'), "Loan missing original_amount"
        assert hasattr(loan, 'remaining_amount'), "Loan missing remaining_amount"
        print(f"✅ Loan structure valid")
        print(f"   Sample: {loan.name}")

    return True


def test_jae_generator_orchestration():
    """Test JaeDataGenerator orchestration."""
    print("\n" + "=" * 60)
    print("TEST 12: JaeDataGenerator Orchestration")
    print("=" * 60)

    from tools.data_generators import JaeDataGenerator

    user = create_mock_user()
    categories = create_mock_categories()
    db_session = MockDBSession()

    generator = JaeDataGenerator(user=user, categories=categories, months_back=12)
    results = generator.generate_all(db_session)

    print(f"\n   Results Summary:")
    for name, count in results.items():
        print(f"   • {name}: {count}")

    # Check total records
    total_records = sum(results.values())
    print(f"\n   Total records generated: {total_records}")

    assert total_records >= 1000, f"Expected at least 1000 total records, got {total_records}"
    print(f"✅ Total record count meets minimum (1000+)")

    # Verify all generators ran
    expected_generators = [
        "Recurring Transactions",
        "Income & Refunds",
        "Daily Spending",
        "Anomalies",
        "User Overrides",
        "Government & Legal",
        "AI Chat Sessions",
        "Budgets",
        "Notifications",
        "Alerts",
        "Loans",
    ]

    for gen_name in expected_generators:
        assert gen_name in results, f"Missing generator: {gen_name}"
        assert results[gen_name] > 0, f"Generator {gen_name} produced 0 records"

    print(f"✅ All {len(expected_generators)} generators executed successfully")

    return True


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🧪 DATA GENERATORS COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")

    tests = [
        ("Import Verification", test_imports),
        ("BaseGenerator Utilities", test_base_generator),
        ("RecurringGenerator", test_recurring_generator),
        ("IncomeGenerator", test_income_generator),
        ("DailySpendingGenerator", test_daily_spending_generator),
        ("Anomaly Generators", test_anomaly_generators),
        ("AISessionGenerator", test_ai_session_generator),
        ("BudgetGenerator", test_budget_generator),
        ("NotificationGenerator", test_notification_generator),
        ("AlertGenerator", test_alert_generator),
        ("LoanGenerator", test_loan_generator),
        ("JaeDataGenerator Orchestration", test_jae_generator_orchestration),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Final summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   Total: {len(tests)}")
    print("=" * 60)

    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("⚠️ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
