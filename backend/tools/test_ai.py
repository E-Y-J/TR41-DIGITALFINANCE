#!/usr/bin/env python
# =============================================================================
# Digital Finance Tracker - AI Integration Test
# PURPOSE: Test the AI categorization system
# =============================================================================
"""
AI Integration Test Script

Tests all AI components within Flask app context:
- Gemini API client
- AI Orchestrator (tiered categorization)
- Keyword matching
- Chat handler

Usage:
    python tools/test_ai.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_ai():
    """Test all AI components."""
    print("=" * 60)
    print("Digital Finance Tracker - AI Integration Test")
    print("=" * 60)

    # Create Flask app context
    from app import create_app

    app = create_app("development")

    with app.app_context():
        # Test 1: Gemini Client
        print("\n[1/4] Testing Gemini Client...")
        try:
            from app.ai.gemini_client import get_gemini_client

            gemini = get_gemini_client()
            success = gemini.initialize()
            print(f"   Gemini initialized: {success}")

            if success:
                # Test categorization
                result = gemini.categorize_transaction("Starbucks Coffee", amount=5.50)
                cat = result.get("category", "Unknown")
                conf = result.get("confidence", 0)
                err = result.get("error", None)
                if err:
                    print(f"   Categorization error: {err}")
                else:
                    print(f"   Test: Starbucks -> {cat} ({conf:.0%})")
        except Exception as e:
            print(f"   Error: {e}")

        # Test 2: Keyword Matching (via CategoryService)
        print("\n[2/4] Testing Keyword Matching...")
        try:
            from app.services.category_service import CategoryService

            test_merchants = [
                ("Shell Gas Station", "Transportation"),
                ("McDonald's", "Food & Dining"),
                ("Netflix", "Entertainment"),
                ("Amazon", "Shopping"),
                ("Verizon Wireless", "Utilities"),
            ]

            for merchant, expected in test_merchants:
                category, conf = CategoryService.categorize_by_keyword(merchant)
                result = category.name if category else "No match"
                status = "✓" if expected in result else "✗"
                print(f"   {status} {merchant:25} -> {result}")
        except Exception as e:
            print(f"   Error: {e}")

        # Test 3: AI Orchestrator
        print("\n[3/4] Testing AI Orchestrator...")
        try:
            from app.ai.orchestrator import get_orchestrator

            orchestrator = get_orchestrator()
            status = orchestrator.initialize()

            print(f"   HuggingFace available: {status.get('huggingface', False)}")
            print(f"   Gemini available: {status.get('gemini', False)}")
            print(f"   Keyword available: {status.get('keyword', True)}")

            # Test with merchants that should use keyword matching
            test_cases = [
                "Walmart Grocery",
                "Uber Ride",
                "City Water Bill",
            ]

            for merchant in test_cases:
                result = orchestrator.categorize(merchant)
                cat = result["category"]
                src = result["source"]
                conf = result["confidence"]
                print(f"   {merchant:25} -> {cat:20} ({src}, {conf:.0%})")
        except Exception as e:
            print(f"   Error: {e}")

        # Test 4: Chat Handler
        print("\n[4/4] Testing Chat Handler...")
        try:
            from app.ai.chat_handler import get_chat_handler
            from uuid import uuid4

            handler = get_chat_handler()
            handler.initialize()
            print(f"   Chat handler initialized: {handler.is_initialized}")

            # Test parsing (without actually creating transactions)
            test_user_id = uuid4()
            test_messages = [
                "Add $50 for lunch at Subway",
                "How much did I spend this month?",
                "help",
            ]

            for msg in test_messages:
                result = handler.process_message(test_user_id, msg)
                intent = result.get("intent", "unknown")
                requires_confirm = result.get("requires_confirmation", False)
                print(
                    f"   '{msg[:30]}...' -> intent: {intent}, confirm: {requires_confirm}"
                )
        except Exception as e:
            print(f"   Error: {e}")

    print("\n" + "=" * 60)
    print("AI Integration Test Complete!")
    print("=" * 60)
    print("\nNote: If Gemini shows quota errors, wait a few minutes")
    print("      or check your API key at https://aistudio.google.com/apikey")


if __name__ == "__main__":
    test_ai()
