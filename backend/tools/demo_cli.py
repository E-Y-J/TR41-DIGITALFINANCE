#!/usr/bin/env python
# =============================================================================
# Digital Finance Tracker - AI Demo CLI
# PURPOSE: Interactive CLI to demonstrate AI capabilities for project demo
# =============================================================================
"""
AI Demo CLI

An interactive command-line interface to showcase the AI features of the
Digital Finance Tracker. Perfect for demos and presentations.

Features Demonstrated:
    1. Transaction Categorization (HuggingFace → Gemini → Keyword)
    2. Natural Language Chat (Add, Edit, Delete transactions)
    3. Spending Queries ("How much did I spend on food?")
    4. Intent Classification (MiniLM-based)
    5. Guardrails (Finance-only scope enforcement)

Usage:
    # Inside Docker container:
    docker exec -it flask_backend python tools/demo_cli.py

    # Or locally (with venv activated):
    python tools/demo_cli.py

Demo Commands:
    - Type natural language queries
    - "demo" - Run automated demo scenarios
    - "test" - Quick AI component test
    - "help" - Show available commands
    - "quit" - Exit the CLI
"""

import os
import sys
from pathlib import Path
from uuid import uuid4
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Colors for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def print_header(text: str):
    """Print a styled header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}\n")


def print_subheader(text: str):
    """Print a styled subheader."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}--- {text} ---{Colors.END}")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")


def print_ai_response(text: str):
    """Print AI response in a styled box."""
    print(f"\n{Colors.CYAN}┌{'─' * 58}┐{Colors.END}")
    # Word wrap the response
    words = text.split()
    line = ""
    for word in words:
        if len(line) + len(word) + 1 <= 56:
            line += (" " if line else "") + word
        else:
            print(
                f"{Colors.CYAN}│{Colors.END} {line.ljust(56)} {Colors.CYAN}│{Colors.END}"
            )
            line = word
    if line:
        print(f"{Colors.CYAN}│{Colors.END} {line.ljust(56)} {Colors.CYAN}│{Colors.END}")
    print(f"{Colors.CYAN}└{'─' * 58}┘{Colors.END}\n")


def run_quick_test(app):
    """Run a quick AI component test."""
    print_header("AI Component Quick Test")

    with app.app_context():
        results = {}

        # Test 1: Gemini Client
        print_subheader("1. Gemini API Client")
        try:
            from app.ai.gemini_client import get_gemini_client

            gemini = get_gemini_client()
            success = gemini.initialize()
            if success:
                print_success(f"Gemini initialized successfully")
                result = gemini.categorize_transaction("Starbucks Coffee", amount=5.50)
                if result.get("error"):
                    print_error(f"API Error: {result['error']}")
                else:
                    cat = result.get("category", "Unknown")
                    conf = result.get("confidence", 0)
                    print_success(
                        f"Test categorization: Starbucks → {cat} ({conf:.0%})"
                    )
                results["gemini"] = True
            else:
                print_error("Gemini initialization failed")
                results["gemini"] = False
        except Exception as e:
            print_error(f"Error: {e}")
            results["gemini"] = False

        # Test 2: Intent Classifier (MiniLM)
        print_subheader("2. Intent Classifier (MiniLM)")
        try:
            from app.ai.intent_classifier import get_intent_classifier

            classifier = get_intent_classifier()
            success = classifier.initialize()
            if success:
                print_success("MiniLM model loaded successfully")
                test_queries = [
                    ("Add $50 for lunch", "add_transaction"),
                    ("Show my spending", "show_transactions"),
                    ("Delete last transaction", "delete_transaction"),
                ]
                for query, expected in test_queries:
                    intent, conf = classifier.classify(query)
                    status = "✓" if expected in intent else "~"
                    print(f"  {status} '{query}' → {intent} ({conf:.0%})")
                results["intent_classifier"] = True
            else:
                print_error("Intent classifier initialization failed")
                results["intent_classifier"] = False
        except Exception as e:
            print_error(f"Error: {e}")
            results["intent_classifier"] = False

        # Test 3: Guardrails
        print_subheader("3. Guardrails (Scope Enforcement)")
        try:
            from app.ai.guardrails import get_guardrails

            guardrails = get_guardrails()
            guardrails.initialize()

            test_cases = [
                ("How much did I spend on food?", True),
                ("Add $25 for coffee", True),
                ("How do I make bread?", False),
                ("What's the weather today?", False),
            ]
            for query, expected_valid in test_cases:
                is_valid, msg = guardrails.check_scope(query)
                status = "✓" if is_valid == expected_valid else "✗"
                result_str = "IN SCOPE" if is_valid else "OUT OF SCOPE"
                print(f"  {status} '{query[:35]}...' → {result_str}")
            print_success("Guardrails working correctly")
            results["guardrails"] = True
        except Exception as e:
            print_error(f"Error: {e}")
            results["guardrails"] = False

        # Test 4: AI Orchestrator
        print_subheader("4. AI Orchestrator (Tiered Categorization)")
        try:
            from app.ai.orchestrator import get_orchestrator

            orchestrator = get_orchestrator()
            status = orchestrator.initialize()

            hf_status = "✓" if status.get("huggingface") else "✗"
            gm_status = "✓" if status.get("gemini") else "✗"
            kw_status = "✓" if status.get("keyword") else "✗"

            print(
                f"  {hf_status} HuggingFace Model: {'Ready' if status.get('huggingface') else 'Not available'}"
            )
            print(
                f"  {gm_status} Gemini Fallback: {'Ready' if status.get('gemini') else 'Not available'}"
            )
            print(
                f"  {kw_status} Keyword Matching: {'Ready' if status.get('keyword') else 'Not available'}"
            )

            test_merchants = ["McDonald's", "Shell Gas Station", "Netflix"]
            for merchant in test_merchants:
                result = orchestrator.categorize(merchant)
                cat = result["category"]
                src = result["source"]
                conf = result["confidence"]
                print(f"  → {merchant:20} = {cat:15} ({src}, {conf:.0%})")

            results["orchestrator"] = True
            print_success("Orchestrator working correctly")
        except Exception as e:
            print_error(f"Error: {e}")
            results["orchestrator"] = False

        # Test 5: Chat Handler
        print_subheader("5. Chat Handler (Natural Language)")
        try:
            from app.ai.chat_handler import get_chat_handler

            handler = get_chat_handler()
            handler.initialize()
            print_success("Chat handler initialized")
            results["chat_handler"] = True
        except Exception as e:
            print_error(f"Error: {e}")
            results["chat_handler"] = False

        # Summary
        print_subheader("Test Summary")
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        for component, status in results.items():
            icon = "✓" if status else "✗"
            color = Colors.GREEN if status else Colors.RED
            print(f"  {color}{icon} {component.replace('_', ' ').title()}{Colors.END}")

        print(f"\n{Colors.BOLD}Result: {passed}/{total} components working{Colors.END}")

        return results


def run_demo_scenarios(app, handler, user_id):
    """Run automated demo scenarios."""
    print_header("Automated Demo Scenarios")

    scenarios = [
        {
            "title": "1. Adding a Transaction via Natural Language",
            "messages": [
                "Add $45.50 for dinner at Olive Garden",
            ],
            "explanation": "The AI parses the natural language, extracts amount, merchant, and auto-categorizes it.",
        },
        {
            "title": "2. Querying Spending",
            "messages": [
                "How much did I spend on food this month?",
            ],
            "explanation": "The AI understands the query intent and would search transactions by category.",
        },
        {
            "title": "3. Transaction Categorization",
            "messages": [
                "What category is Uber?",
            ],
            "explanation": "The AI uses the categorization pipeline to identify the category.",
        },
        {
            "title": "4. Scope Enforcement (Guardrails)",
            "messages": [
                "How do I make pasta?",
            ],
            "explanation": "The AI politely redirects off-topic questions back to finance.",
        },
        {
            "title": "5. Budget Status Check",
            "messages": [
                "Am I over budget this month?",
            ],
            "explanation": "The AI understands budget-related queries.",
        },
        {
            "title": "6. Help Request",
            "messages": [
                "What can you help me with?",
            ],
            "explanation": "The AI provides guidance on available features.",
        },
    ]

    with app.app_context():
        for scenario in scenarios:
            print_subheader(scenario["title"])
            print_info(scenario["explanation"])
            print()

            for message in scenario["messages"]:
                print(f"{Colors.BOLD}You:{Colors.END} {message}")
                time.sleep(0.5)  # Dramatic pause

                try:
                    response = handler.process_message(user_id, message)
                    ai_response = response.get("response", "No response generated")
                    intent = response.get("intent", "unknown")
                    requires_confirm = response.get("requires_confirmation", False)

                    print(f"{Colors.BOLD}AI ({intent}):{Colors.END}")
                    print_ai_response(ai_response)

                    if requires_confirm:
                        print_info("This action requires user confirmation (yes/no)")

                except Exception as e:
                    print_error(f"Error: {e}")

            input(
                f"\n{Colors.YELLOW}Press Enter to continue to next scenario...{Colors.END}"
            )


def interactive_chat(app, handler, user_id):
    """Run interactive chat session."""
    print_header("Interactive AI Chat")
    print_info("Type your message to chat with the AI")
    print_info("Commands: 'demo', 'test', 'help', 'clear', 'quit'")
    print()

    with app.app_context():
        while True:
            try:
                user_input = input(f"{Colors.BOLD}You: {Colors.END}").strip()

                if not user_input:
                    continue

                if user_input.lower() == "quit":
                    print_info("Goodbye! Thanks for the demo.")
                    break

                if user_input.lower() == "help":
                    print_subheader("Available Commands")
                    print("  demo  - Run automated demo scenarios")
                    print("  test  - Quick AI component test")
                    print("  clear - Clear conversation history")
                    print("  quit  - Exit the CLI")
                    print("\n  Or just type naturally:")
                    print("  - 'Add $50 for lunch at Subway'")
                    print("  - 'How much did I spend on food?'")
                    print("  - 'What category is Uber?'")
                    print("  - 'Show my transactions this week'")
                    continue

                if user_input.lower() == "demo":
                    run_demo_scenarios(app, handler, user_id)
                    continue

                if user_input.lower() == "test":
                    run_quick_test(app)
                    continue

                if user_input.lower() == "clear":
                    # Create new session
                    user_id = uuid4()
                    print_success("Conversation cleared, new session started")
                    continue

                # Process message through AI
                start_time = time.time()
                response = handler.process_message(user_id, user_input)
                elapsed_ms = (time.time() - start_time) * 1000

                # Extract response data
                ai_response = response.get(
                    "response", "I couldn't process that request."
                )
                intent = response.get("intent", "unknown")
                requires_confirm = response.get("requires_confirmation", False)
                parsed_data = response.get("parsed_data", {})

                # Display response
                print(
                    f"\n{Colors.BOLD}AI ({intent}):{Colors.END} {Colors.CYAN}[{elapsed_ms:.0f}ms]{Colors.END}"
                )
                print_ai_response(ai_response)

                if requires_confirm:
                    print_info("Type 'yes' to confirm or 'no' to cancel")

                if parsed_data:
                    print(f"{Colors.YELLOW}Parsed Data:{Colors.END}")
                    for key, value in parsed_data.items():
                        if key != "_db_id":
                            print(f"  • {key}: {value}")
                    print()

            except KeyboardInterrupt:
                print("\n")
                print_info("Use 'quit' to exit properly")
            except Exception as e:
                print_error(f"Error: {e}")


def show_welcome():
    """Display welcome banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   💰 Digital Finance Tracker - AI Demo                  ║
    ║                                                          ║
    ║   Showcasing:                                            ║
    ║   • Natural Language Transaction Management              ║
    ║   • AI-Powered Categorization (HuggingFace + Gemini)    ║
    ║   • Intelligent Spending Queries                         ║
    ║   • Intent Classification (MiniLM)                       ║
    ║   • Finance-Only Scope Enforcement                       ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(f"{Colors.CYAN}{banner}{Colors.END}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Demo CLI for Digital Finance Tracker"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="interactive",
        choices=["interactive", "test", "demo", "health"],
        help="Command to run: test (quick test), demo (scenarios), health (API health)",
    )
    parser.add_argument(
        "--query", "-q", type=str, help="Single query to process (non-interactive)"
    )
    args = parser.parse_args()

    show_welcome()

    print_info("Initializing Flask application...")

    # Create Flask app context
    from app import create_app

    app = create_app("development")

    with app.app_context():
        # Handle health check
        if args.command == "health":
            print_header("AI System Health Check")
            from app.ai.service import get_ai_service

            service = get_ai_service()
            health = service.health_check()
            status = service.get_status()

            # Overall status
            status_color = (
                Colors.GREEN if health["status"] == "healthy" else Colors.YELLOW
            )
            print(
                f"\n{status_color}Overall Status: {health['status'].upper()}{Colors.END}"
            )
            print(f"Models Loaded: {health.get('models_loaded', 'Unknown')}")

            # Component details from models dict
            if "models" in status and "models" in status["models"]:
                models_info = status["models"]["models"]
                print(f"\n{Colors.CYAN}AI Components:{Colors.END}")
                for model_name, model_info in models_info.items():
                    if isinstance(model_info, dict):
                        available = model_info.get(
                            "available", model_info.get("initialized", True)
                        )
                        if "error" in model_info:
                            available = False
                    else:
                        available = bool(model_info)
                    icon = "✓" if available else "✗"
                    color = Colors.GREEN if available else Colors.RED
                    print(
                        f"  {color}{icon} {model_name}: {'Ready' if available else 'Not Available'}{Colors.END}"
                    )
            elif "models" in status:
                # Router status
                router_status = status["models"]
                print(f"\n{Colors.CYAN}AI Components:{Colors.END}")
                init = router_status.get("is_initialized", False)
                icon = "✓" if init else "✗"
                color = Colors.GREEN if init else Colors.RED
                print(
                    f"  {color}{icon} Router: {'Initialized' if init else 'Not Initialized'}{Colors.END}"
                )

                # Individual models from router
                if "models" in router_status:
                    for model_name, model_info in router_status["models"].items():
                        if isinstance(model_info, dict):
                            available = model_info.get(
                                "available", model_info.get("initialized", True)
                            )
                            if "error" in model_info:
                                available = False
                        else:
                            available = bool(model_info)
                        icon = "✓" if available else "✗"
                        color = Colors.GREEN if available else Colors.RED
                        print(
                            f"  {color}{icon} {model_name}: {'Ready' if available else 'Limited'}{Colors.END}"
                        )

            print()
            return

        # Initialize chat handler
        print_info("Loading AI models (this may take a moment)...")

        from app.ai.chat_handler import get_chat_handler

        handler = get_chat_handler()

        if not handler.initialize():
            print_error("Failed to initialize chat handler")
            print_info("Some AI features may not be available")

        print_success("AI system ready!")
        print()

        # Get or create demo user - use existing user from database to satisfy FK constraint
        from app.models import User

        demo_user = User.query.first()
        if demo_user:
            user_id = demo_user.id
            print_info(f"Demo user: {demo_user.email}")
        else:
            # Create a demo user if none exists
            from app.core.extensions import db

            user_id = uuid4()
            demo_user = User(
                id=user_id,
                auth0_id=f"demo|{str(user_id)[:8]}",
                email=f"demo-{str(user_id)[:8]}@example.com",
                name="Demo User",
            )
            db.session.add(demo_user)
            db.session.commit()
            print_info(f"Created demo user: {demo_user.email}")

        print_info(f"Session ID: {str(user_id)[:8]}...")

        # Handle non-interactive commands
        if args.command == "test":
            run_quick_test(app)
            return

        if args.command == "demo":
            run_demo_scenarios(app, handler, user_id)
            return

        # Handle single query
        if args.query:
            print(f"\n{Colors.BOLD}You:{Colors.END} {args.query}")
            response = handler.process_message(user_id, args.query)
            ai_response = response.get("response", "No response")
            intent = response.get("intent", "unknown")
            print(f"\n{Colors.BOLD}AI ({intent}):{Colors.END}")
            print_ai_response(ai_response)
            return

    # Start interactive session
    interactive_chat(app, handler, user_id)


if __name__ == "__main__":
    main()
