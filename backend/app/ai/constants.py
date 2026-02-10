# =============================================================================
# Digital Finance Tracker - AI Constants
# PURPOSE: Centralized constants for AI modules (categories, intents, thresholds)
# =============================================================================
"""
AI Constants Module

This module centralizes all constants used across AI modules:
- System categories for transaction categorization
- Intent types and examples for classification
- Confidence thresholds for routing decisions
- Keyword mappings for fast-path matching

Centralizing constants here provides:
- Single source of truth
- Easy updates across all modules
- Consistent behavior

Usage:
    from app.ai.constants import (
        SYSTEM_CATEGORIES,
        INTENT_EXAMPLES,
        CONFIDENCE_THRESHOLDS,
        CATEGORY_KEYWORDS,
    )

Notes:
    - Categories must match database Category table
    - Intent examples are used for MiniLM embedding similarity
    - Thresholds can be overridden via environment variables
"""

import os
from typing import Dict, List, Set

# =============================================================================
# SYSTEM CATEGORIES
# =============================================================================

# Master list of transaction categories
# Must stay in sync with database Category table seeded values (category.py)
# Source of truth: app/models/category.py → DEFAULT_CATEGORIES
SYSTEM_CATEGORIES: List[str] = [
    "Food & Dining",
    "Transportation",
    "Shopping & Retail",
    "Entertainment & Recreation",
    "Healthcare & Medical",
    "Utilities & Services",
    "Financial Services",
    "Income",
    "Government & Legal",
    "Charity & Donations",
    "Unknown",  # Fallback when AI confidence is below threshold
]

# Set version for fast lookup
VALID_CATEGORIES: Set[str] = set(SYSTEM_CATEGORIES)

# Default category when AI confidence is too low
DEFAULT_CATEGORY: str = "Unknown"


# =============================================================================
# CATEGORY KEYWORDS (Fast-Path Matching)
# =============================================================================

# Keywords mapped to categories for instant matching
# These bypass AI models entirely for speed
# Category names must match SYSTEM_CATEGORIES exactly
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Food & Dining": [
        "restaurant",
        "cafe",
        "coffee",
        "starbucks",
        "mcdonald",
        "burger",
        "pizza",
        "sushi",
        "doordash",
        "grubhub",
        "ubereats",
        "chipotle",
        "subway",
        "wendy",
        "taco",
        "diner",
        "bakery",
        "deli",
        "lunch",
        "dinner",
        "breakfast",
        "food",
        "eat",
        "meal",
        "snack",
        "grocery",
        "supermarket",
        "walmart",
        "target",
        "costco",
        "kroger",
        "safeway",
        "trader joe",
        "whole foods",
        "aldi",
        "publix",
    ],
    "Transportation": [
        "uber",
        "lyft",
        "taxi",
        "gas",
        "fuel",
        "shell",
        "chevron",
        "exxon",
        "bp",
        "parking",
        "toll",
        "metro",
        "bus",
        "train",
        "transit",
        "airline",
        "flight",
        "car",
        "auto",
        "vehicle",
        "rental",
        "hertz",
        "enterprise",
        "avis",
        "amtrak",
        "greyhound",
    ],
    "Shopping & Retail": [
        "amazon",
        "ebay",
        "etsy",
        "shop",
        "store",
        "mall",
        "retail",
        "clothing",
        "shoes",
        "fashion",
        "bestbuy",
        "electronics",
        "apple",
        "nike",
        "adidas",
        "nordstrom",
        "macys",
        "kohls",
        "jcpenney",
        "home depot",
        "lowes",
        "ikea",
        "wayfair",
        "purchase",
        "buy",
    ],
    "Entertainment & Recreation": [
        "movie",
        "cinema",
        "theater",
        "concert",
        "game",
        "gaming",
        "steam",
        "playstation",
        "xbox",
        "nintendo",
        "netflix",
        "hulu",
        "spotify",
        "music",
        "book",
        "kindle",
        "audible",
        "ticket",
        "event",
        "show",
        "amc",
        "regal",
        "fun",
        "hobby",
        "gym",
        "fitness",
        "sports",
    ],
    "Healthcare & Medical": [
        "doctor",
        "hospital",
        "clinic",
        "pharmacy",
        "cvs",
        "walgreens",
        "medicine",
        "prescription",
        "dental",
        "dentist",
        "vision",
        "optometry",
        "therapy",
        "health",
        "medical",
        "urgent care",
        "lab",
    ],
    "Utilities & Services": [
        "electric",
        "gas bill",
        "water",
        "internet",
        "cable",
        "phone",
        "mobile",
        "verizon",
        "att",
        "t-mobile",
        "sprint",
        "comcast",
        "xfinity",
        "utility",
        "bill",
        "rent",
        "mortgage",
        "subscription",
        "netflix",
        "spotify",
        "hulu",
        "disney",
    ],
    "Financial Services": [
        "bank",
        "credit card",
        "insurance",
        "investment",
        "tax",
        "interest",
        "fee",
        "atm",
        "transfer",
        "zelle",
        "venmo",
        "paypal",
        "cashapp",
        "wire",
        "checking",
        "savings",
        "loan",
    ],
    "Income": [
        "payroll",
        "salary",
        "wage",
        "direct deposit",
        "paycheck",
        "bonus",
        "commission",
        "dividend",
        "refund",
        "reimbursement",
        "income",
        "deposit",
        "payment received",
        "freelance",
    ],
    "Government & Legal": [
        "tax",
        "irs",
        "dmv",
        "license",
        "permit",
        "court",
        "legal",
        "attorney",
        "lawyer",
        "government",
        "state",
        "federal",
    ],
    "Charity & Donations": [
        "charity",
        "donation",
        "donate",
        "nonprofit",
        "church",
        "temple",
        "mosque",
        "synagogue",
        "religious",
        "red cross",
        "unicef",
    ],
}


# =============================================================================
# INTENT TYPES
# =============================================================================


class IntentType:
    """Intent type constants for chat commands."""

    CREATE_TRANSACTION = "create_transaction"
    EDIT_TRANSACTION = "edit_transaction"
    DELETE_TRANSACTION = "delete_transaction"
    QUERY_SPENDING = "query_spending"
    QUERY_TRANSACTIONS = "query_transactions"
    CATEGORIZE = "categorize"
    GENERAL_CHAT = "general_chat"
    CLARIFY_CATEGORY = "clarify_category"
    CONFIRM_ACTION = "confirm_action"
    CANCEL_ACTION = "cancel_action"
    BUDGET_STATUS = "budget_status"
    GET_INSIGHTS = "get_insights"
    HELP = "help"


# =============================================================================
# INTENT EXAMPLES (For MiniLM Similarity Matching)
# =============================================================================

# Example phrases for each intent type
# Used to compute embeddings for similarity-based classification
INTENT_EXAMPLES: Dict[str, List[str]] = {
    IntentType.CREATE_TRANSACTION: [
        "add a transaction",
        "log an expense",
        "record a purchase",
        "add $50 for lunch",
        "spent $20 at starbucks",
        "bought groceries for $100",
        "paid $30 for gas",
        "add income of $1000",
        "received payment of $500",
        "log my salary",
        "create new expense",
        "enter a bill payment",
    ],
    IntentType.EDIT_TRANSACTION: [
        "edit my transaction",
        "change the amount",
        "update the category",
        "modify my last purchase",
        "fix the transaction",
        "correct the amount to $50",
        "change category to food",
        "update my spending",
        "adjust the expense",
    ],
    IntentType.DELETE_TRANSACTION: [
        "delete a transaction",
        "remove an expense",
        "cancel my last purchase",
        "undo the transaction",
        "remove my spending entry",
        "delete the last one",
        "erase that transaction",
    ],
    IntentType.QUERY_SPENDING: [
        "how much did I spend",
        "what's my total spending",
        "show my expenses",
        "spending summary",
        "how much on food this month",
        "total expenses this week",
        "what did I spend on shopping",
        "my spending breakdown",
        "expense report",
    ],
    IntentType.QUERY_TRANSACTIONS: [
        "show my transactions",
        "list my purchases",
        "what are my recent expenses",
        "transaction history",
        "show all my spending",
        "list expenses from last week",
        "find my starbucks purchases",
    ],
    IntentType.BUDGET_STATUS: [
        "how's my budget",
        "budget status",
        "am I over budget",
        "how much can I spend",
        "remaining budget",
        "budget left for food",
        "check my spending limit",
    ],
    IntentType.GET_INSIGHTS: [
        "give me insights",
        "analyze my spending",
        "spending patterns",
        "where does my money go",
        "financial insights",
        "spending trends",
        "help me save money",
    ],
    IntentType.CATEGORIZE: [
        "what category is this",
        "categorize this merchant",
        "which category for starbucks",
        "is this food or shopping",
        "help me categorize",
    ],
    IntentType.HELP: [
        "help",
        "what can you do",
        "how does this work",
        "show me commands",
        "what commands are available",
        "guide me",
    ],
    IntentType.CONFIRM_ACTION: [
        "yes",
        "confirm",
        "do it",
        "proceed",
        "that's correct",
        "looks good",
        "go ahead",
        "sure",
        "ok",
        "yep",
    ],
    IntentType.CANCEL_ACTION: [
        "no",
        "cancel",
        "stop",
        "don't do it",
        "nevermind",
        "abort",
        "that's wrong",
        "wait",
    ],
    IntentType.GENERAL_CHAT: [
        "hello",
        "hi there",
        "hey",
        "good morning",
        "thanks",
        "thank you",
        "bye",
        "goodbye",
    ],
}


# =============================================================================
# INTENT KEYWORDS (Fast-Path Matching)
# =============================================================================

# Keywords for instant intent detection (bypasses MiniLM)
INTENT_KEYWORDS: Dict[str, List[str]] = {
    IntentType.CREATE_TRANSACTION: [
        "add",
        "spent",
        "bought",
        "paid",
        "purchased",
        "log",
        "record",
        "expense",
        "income",
        "received",
    ],
    IntentType.DELETE_TRANSACTION: [
        "delete",
        "remove",
        "cancel",
        "undo",
        "erase",
    ],
    IntentType.EDIT_TRANSACTION: [
        "edit",
        "change",
        "update",
        "modify",
        "fix",
        "correct",
        "adjust",
    ],
    IntentType.QUERY_SPENDING: [
        "how much",
        "total",
        "sum",
        "spending",
        "spent",
    ],
    IntentType.CONFIRM_ACTION: [
        "yes",
        "confirm",
        "ok",
        "sure",
        "proceed",
        "do it",
        "yep",
        "yeah",
    ],
    IntentType.CANCEL_ACTION: [
        "no",
        "cancel",
        "stop",
        "abort",
        "nevermind",
        "don't",
    ],
    IntentType.HELP: [
        "help",
        "?",
        "commands",
        "guide",
        "how to",
    ],
}


# =============================================================================
# CONFIDENCE THRESHOLDS
# =============================================================================


class ConfidenceThresholds:
    """Confidence thresholds for AI routing decisions."""

    # Category classification thresholds
    CATEGORY_HIGH: float = float(os.getenv("AI_CATEGORY_HIGH_THRESHOLD", "0.85"))
    CATEGORY_MEDIUM: float = float(os.getenv("AI_CATEGORY_MEDIUM_THRESHOLD", "0.70"))
    CATEGORY_LOW: float = float(os.getenv("AI_CATEGORY_LOW_THRESHOLD", "0.50"))

    # Intent classification thresholds
    INTENT_HIGH: float = float(os.getenv("AI_INTENT_HIGH_THRESHOLD", "0.85"))
    INTENT_MEDIUM: float = float(os.getenv("AI_INTENT_MEDIUM_THRESHOLD", "0.70"))
    INTENT_LOW: float = float(os.getenv("AI_INTENT_LOW_THRESHOLD", "0.50"))

    # Learned category confidence boost
    LEARNED_CONFIDENCE: float = 0.95

    # Keyword match confidence (always high)
    KEYWORD_CONFIDENCE: float = 0.98


# =============================================================================
# MODEL CONFIGURATION
# =============================================================================


class ModelConfig:
    """AI model configuration constants."""

    # HuggingFace models
    CATEGORIZER_MODEL: str = "distilbert-base-uncased-finetuned"
    INTENT_MODEL: str = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"

    # Model paths
    MODEL_STORE_PATH: str = "app/ai/model_store"

    # Gemini configuration
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_TEMPERATURE: float = 0.3
    GEMINI_MAX_TOKENS: int = 256

    # Rate limiting (free tier)
    GEMINI_RPM_LIMIT: int = 15
    GEMINI_DAILY_LIMIT: int = 1500
