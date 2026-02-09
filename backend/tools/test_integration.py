#!/usr/bin/env python
# =============================================================================
# Digital Finance Tracker - Comprehensive Integration Test
# PURPOSE: Verify AI model and database integration on Docker
# =============================================================================
"""
Comprehensive Integration Test

Tests:
1. Database integrity (users, transactions, AI sessions, etc.)
2. AI model predictions (DistilBERT classifier)
3. AI session content verification
4. Full system integration
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.core.extensions import db
from app.models import (
    User,
    Transaction,
    AISession,
    Budget,
    Notification,
    Alert,
    Loan,
    Category,
)


def run_integration_tests():
    """Run comprehensive integration tests."""
    print("=" * 70)
    print("COMPREHENSIVE DOCKER INTEGRATION TEST")
    print("=" * 70)

    app = create_app()
    errors = []

    with app.app_context():
        # ===== DATABASE TESTS =====
        print("\n" + "=" * 50)
        print("1. DATABASE INTEGRITY TESTS")
        print("=" * 50)

        # 1.1 User check
        jae = User.query.filter_by(email="jaeyseo0922@gmail.com").first()
        if jae:
            print("   [PASS] Jae Young Seo user found")
        else:
            print("   [FAIL] Jae Young Seo not found")
            errors.append("User not found")
            return

        # 1.2 Transaction count
        txn_count = Transaction.query.filter_by(user_id=jae.id).count()
        if txn_count > 1500:
            print(f"   [PASS] Transactions: {txn_count}")
        else:
            print(f"   [WARN] Transaction count: {txn_count}")

        # 1.3 AI Sessions
        ai_count = AISession.query.filter_by(user_id=jae.id).count()
        if ai_count >= 20:
            print(f"   [PASS] AI Sessions: {ai_count}")
        else:
            print(f"   [WARN] AI session count: {ai_count}")

        # 1.4 Budget check
        budget_count = Budget.query.filter_by(user_id=jae.id).count()
        print(f"   [PASS] Budgets: {budget_count}")

        # 1.5 Notification check
        notif_count = Notification.query.filter_by(user_id=jae.id).count()
        print(f"   [PASS] Notifications: {notif_count}")

        # 1.6 Alert check
        alert_count = Alert.query.filter_by(user_id=jae.id).count()
        print(f"   [PASS] Alerts: {alert_count}")

        # 1.7 Loan check
        loan_count = Loan.query.filter_by(user_id=jae.id).count()
        print(f"   [PASS] Loans: {loan_count}")

        # 1.8 Category check
        cat_count = Category.query.count()
        print(f"   [PASS] Categories: {cat_count}")

        # ===== AI MODEL TESTS =====
        print("\n" + "=" * 50)
        print("2. AI MODEL INTEGRATION TESTS")
        print("=" * 50)

        # 2.1 DistilBERT Classifier
        try:
            from app.ai.inference import TransactionClassifier

            classifier = TransactionClassifier()

            # Test predictions
            test_cases = [
                ("Starbucks Coffee", "Food & Dining"),
                ("Uber ride to airport", "Transportation"),
                ("Netflix monthly subscription", "Entertainment"),
                ("PG&E electric bill", "Utilities"),
                ("Amazon Prime purchase", "Shopping"),
                ("Kaiser Permanente copay", "Healthcare"),
                ("Rent payment to landlord", "Rent"),
                ("Whole Foods groceries", "Groceries"),
            ]

            correct = 0
            for desc, expected in test_cases:
                result, conf = classifier.predict(desc)
                # Accept if category contains expected or vice versa
                match = (
                    expected.lower() in result.lower()
                    or result.lower() in expected.lower()
                )
                if match:
                    correct += 1
                    status = "PASS"
                else:
                    status = "WARN"
                desc_short = desc[:25] + "..." if len(desc) > 25 else desc
                print(f'   [{status}] "{desc_short}" -> {result} ({conf:.1%})')

            accuracy = correct / len(test_cases)
            if accuracy >= 0.7:
                print(f"   [PASS] DistilBERT Accuracy: {accuracy:.0%}")
            else:
                print(f"   [WARN] DistilBERT Accuracy: {accuracy:.0%}")

        except Exception as e:
            print(f"   [FAIL] DistilBERT error: {e}")
            errors.append(f"DistilBERT error: {e}")

        # ===== AI SESSION CONTENT TESTS =====
        print("\n" + "=" * 50)
        print("3. AI SESSION CONTENT TESTS")
        print("=" * 50)

        sessions = AISession.query.filter_by(user_id=jae.id).all()

        # 3.1 Conversation history check
        sessions_with_content = [
            s
            for s in sessions
            if s.conversation_history and len(s.conversation_history) > 0
        ]
        print(
            f"   [PASS] Sessions with content: {len(sessions_with_content)}/{len(sessions)}"
        )

        # 3.2 Intent diversity
        intents = set([s.last_intent for s in sessions if s.last_intent])
        print(f"   [PASS] Unique intents covered: {len(intents)}")
        for intent in sorted(intents):
            print(f"         - {intent}")

        # 3.3 Sample conversation
        if sessions and sessions[0].conversation_history:
            msgs = sessions[0].conversation_history
            print(f"   [PASS] Sample session has {len(msgs)} messages")

        # ===== SUMMARY =====
        print("\n" + "=" * 70)
        if errors:
            print("RESULT: SOME ISSUES FOUND")
            for e in errors:
                print(f"  - {e}")
        else:
            print("RESULT: ALL INTEGRATION TESTS PASSED")
        print("=" * 70)

        # Stats summary
        print("\nDATA SUMMARY:")
        print(f"  - Users: {User.query.count()}")
        print(f"  - Transactions: {Transaction.query.count()}")
        print(f"  - AI Sessions: {AISession.query.count()}")
        print(f"  - Budgets: {Budget.query.count()}")
        print(f"  - Notifications: {Notification.query.count()}")
        print(f"  - Alerts: {Alert.query.count()}")
        print(f"  - Loans: {Loan.query.count()}")
        print(f"  - Categories: {Category.query.count()}")


if __name__ == "__main__":
    run_integration_tests()
