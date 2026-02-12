# =============================================================================
# Digital Finance Tracker - Intent Classifier
# PURPOSE: MiniLM-based intent detection for natural language commands
# =============================================================================
"""
Intent Classifier Module

Uses sentence-transformers/multi-qa-MiniLM-L6-cos-v1 for semantic similarity
based intent classification. This model excels at understanding user queries
and matching them to predefined intents.

Model Info:
    - Name: multi-qa-MiniLM-L6-cos-v1
    - Size: ~80MB
    - Output: 384-dimensional embeddings
    - Training: 215M+ question-answer pairs
    - GPU: Not required

How It Works:
    1. Pre-compute embeddings for all intent examples
    2. When user sends message, embed their text
    3. Find most similar intent using cosine similarity
    4. Return intent with confidence score

Usage:
    from app.ai.intent_classifier import IntentClassifier, get_intent_classifier

    classifier = get_intent_classifier()
    intent, confidence = classifier.classify("show my spending last month")
    # ("summarize_transactions", 0.89)

Supported Intents (Elijah's Requirements):
    - summarize_transactions: "Summarize my transactions"
    - show_transactions: "Show me all my transactions"
    - add_transaction: "Add $50 for lunch"
    - edit_transaction: "Change my last transaction"
    - delete_transaction: "Delete my last transaction"
    - query_spending: "How much did I spend on food?"
    - categorize_help: "What category is Uber?"
    - budget_status: "Am I over budget?"

Notes:
    - Thread-safe singleton pattern
    - Lazy loading (model loaded on first use)
    - Works with guardrails.py for scope enforcement
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
import threading
import numpy as np

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

MODEL_NAME = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
CONFIDENCE_THRESHOLD = 0.70  # Below this, intent is uncertain


# =============================================================================
# INTENT DEFINITIONS
# =============================================================================
# Each intent has example phrases that represent it.
# The classifier embeds these examples and compares user input to them.

INTENT_EXAMPLES = {
    "summarize_transactions": [
        "summarize my transactions",
        "show me a summary",
        "give me an overview of my spending",
        "what's my spending summary",
        "how much did I spend",
        "spending overview",
        "transaction summary",
        "show spending breakdown",
    ],
    "show_transactions": [
        "show me all my transactions",
        "list my transactions",
        "show my recent transactions",
        "what are my transactions",
        "display transactions",
        "view my transactions",
        "get my transaction history",
    ],
    "add_transaction": [
        "add a transaction",
        "add expense",
        "log a purchase",
        "I bought something",
        "record spending",
        "add new expense",
        "I spent money on",
        "log expense",
        "create transaction",
    ],
    "edit_transaction": [
        "edit my transaction",
        "change my last transaction",
        "update transaction",
        "modify transaction",
        "fix my transaction",
        "correct the amount",
        "change the category",
    ],
    "delete_transaction": [
        "delete my transaction",
        "remove transaction",
        "delete my last transaction",
        "cancel transaction",
        "remove expense",
        "delete the expense",
    ],
    "query_spending": [
        "how much did I spend on",
        "what did I spend on food",
        "spending on transportation",
        "how much for groceries",
        "category spending",
        "spending by category",
        "total spent on",
    ],
    "categorize_help": [
        "what category is",
        "which category for",
        "how do I categorize",
        "category for Uber",
        "what category should I use",
        "help me categorize",
    ],
    "budget_status": [
        # Query/status phrases - READING not WRITING
        "am I over budget",
        "budget status",
        "how is my budget",
        "check my budget",
        "am I within budget",
        "budget remaining",
        "how much budget left",
        "show my budget",
        "view budget",
        "what is my budget",
        "how much budget do I have",
        "am I on track with my budget",
        "budget overview",
        "show budget status",
    ],
    # NEW: Budget modification intents
    # NOTE: These phrases must be CLEARLY DISTINCT from budget_status
    # Use action verbs: set, create, update, change, increase, decrease
    "set_budget": [
        # Primary action phrases - high priority
        "set my food budget to 500",
        "set budget for shopping to 300",
        "set a budget of 500 for groceries",
        "create a budget for entertainment",
        "create budget of 200",
        "make a new budget",
        # Update/change actions
        "update budget for groceries",
        "change my spending limit to 400",
        "change food budget to 600",
        "update my shopping budget",
        # Increase actions
        "increase my budget by 100",
        "raise my monthly budget to 2000",
        "bump up my food budget to 800",
        "add 200 to my budget limit",
        # Decrease actions
        "decrease my entertainment budget",
        "lower my shopping budget to 200",
        "reduce budget for dining",
        # Goal-setting phrases
        "I want to limit groceries to 500",
        "I want to cap my spending at 1000",
        "make my budget 1000",
        "set spending limit",
        "new budget for",
    ],
    # NEW: Loan intents
    "make_loan_payment": [
        "pay 500 towards my loan",
        "make a loan payment",
        "pay off some of my debt",
        "I paid 200 on my student loan",
        "reduce my loan balance",
        "pay down my loan",
        "make a payment on my car loan",
        "paid my loan",
    ],
    "add_loan": [
        "add a new loan",
        "I borrowed 5000",
        "create a loan for my car",
        "I took out a loan",
        "new debt of 10000",
        "record a new loan",
        "add debt",
        "I got a loan",
    ],
    "check_loan": [
        "how much do I owe",
        "loan balance",
        "check my loans",
        "remaining loan amount",
        "debt status",
        "show my loans",
        "what's my loan balance",
        "how much debt do I have",
    ],
    # NEW: Savings/Goals intents (future feature)
    "savings_goal": [
        "set a savings goal",
        "I want to save 1000",
        "create a savings goal",
        "add to my savings",
        "how much have I saved",
        "savings progress",
        "check my savings goal",
        "save for vacation",
        "save money for",
    ],
    "get_insights": [
        "spending insights",
        "analyze my spending",
        "spending patterns",
        "unusual spending",
        "spending analysis",
        "financial insights",
    ],
    "help": [
        "help",
        "what can you do",
        "how do I use this",
        "commands",
        "what are my options",
        "show me what you can do",
    ],
}


# =============================================================================
# INTENT CLASSIFIER CLASS
# =============================================================================


class IntentClassifier:
    """
    Semantic similarity-based intent classifier using MiniLM.

    Uses sentence embeddings to match user input to predefined intents.
    More robust than keyword matching - understands meaning, not just words.

    Attributes:
        model: SentenceTransformer model instance
        intent_embeddings: Pre-computed embeddings for intent examples
        is_initialized: Whether model is loaded

    Example:
        >>> classifier = IntentClassifier()
        >>> classifier.initialize()
        >>> intent, conf = classifier.classify("show my spending")
        >>> print(f"{intent}: {conf:.2f}")
        summarize_transactions: 0.87
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern for memory efficiency."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_done = False
        return cls._instance

    def __init__(self):
        """Initialize classifier (model loaded lazily)."""
        if self._init_done:
            return

        self.model = None
        self.intent_embeddings: Dict[str, np.ndarray] = {}
        self.is_initialized = False
        self._use_fallback = False  # True when sentence-transformers unavailable
        self._init_done = True
        logger.debug("IntentClassifier instance created (not yet initialized)")

    def initialize(self) -> bool:
        """
        Load MiniLM model and pre-compute intent embeddings.

        Returns:
            True if initialization successful, False if fallback mode

        Notes:
            If sentence-transformers is not installed, falls back to
            keyword-based matching (lower accuracy but works).
        """
        if self.is_initialized:
            return True

        # Check if intent classifier is disabled via config
        try:
            from app.core.config import get_config

            config = get_config()
            if (
                hasattr(config, "AI_INTENT_CLASSIFIER_ENABLED")
                and not config.AI_INTENT_CLASSIFIER_ENABLED
            ):
                logger.info(
                    "Intent classifier disabled via AI_INTENT_CLASSIFIER_ENABLED=0"
                )
                self.is_initialized = True
                self._use_fallback = True
                return True
        except Exception:
            pass  # Config not available, continue with normal init

        try:
            logger.info(f"Loading intent classifier model: {MODEL_NAME}")

            # Import here to allow graceful failure if not installed
            from sentence_transformers import SentenceTransformer

            # Load model
            self.model = SentenceTransformer(MODEL_NAME)

            # Pre-compute embeddings for all intent examples
            logger.info("Pre-computing intent embeddings...")
            for intent, examples in INTENT_EXAMPLES.items():
                embeddings = self.model.encode(examples, convert_to_numpy=True)
                # Store mean embedding for each intent
                self.intent_embeddings[intent] = np.mean(embeddings, axis=0)

            self.is_initialized = True
            self._use_fallback = False
            logger.info(
                f"Intent classifier initialized with {len(INTENT_EXAMPLES)} intents"
            )
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. "
                "Using keyword-based fallback for intent detection. "
                "For better accuracy, run: pip install sentence-transformers"
            )
            self.is_initialized = True
            self._use_fallback = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize intent classifier: {e}", exc_info=True)
            # Still mark as initialized to avoid repeated failures
            self.is_initialized = True
            self._use_fallback = True
            return False

    def _classify_by_rules(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Rule-based pre-classification for high-confidence patterns.
        
        Uses regex patterns to catch unambiguous user intents before
        falling back to semantic matching. This improves accuracy for
        critical operations like budget setting and transaction creation.
        
        Args:
            text: User's input message
            
        Returns:
            Tuple of (intent_name, confidence_score) if a rule matches,
            None if no rule matches (fall through to semantic matching)
        """
        text_lower = text.lower().strip()
        
        # =================================================================
        # BUDGET INTENTS - Critical to distinguish set vs check
        # =================================================================
        
        # SET_BUDGET: Action verbs + budget + amount/category
        set_budget_patterns = [
            # "set my food budget to 500", "set budget for shopping to 300"
            r"^set\s+(my\s+)?(\w+\s+)?budget\s+(to|at|for|of)\s+",
            # "create a budget of 500", "create budget for groceries"
            r"^create\s+(a\s+)?budget\s+(of|for)",
            # "update my shopping budget", "change my budget to"
            r"^(update|change|modify)\s+(my\s+)?(\w+\s+)?budget",
            # "increase/decrease/raise/lower budget"
            r"^(increase|decrease|raise|lower|bump)\s+(my\s+)?(\w+\s+)?budget",
            # "I want to limit groceries to 500"
            r"i\s+want\s+to\s+(limit|cap|set)\s+",
            # "make my budget 1000", "make a new budget"
            r"^make\s+(my\s+|a\s+)?(new\s+)?budget",
            # "budget for food should be 500"
            r"budget\s+for\s+\w+\s+should\s+be",
            # "put a limit on", "set a limit on"
            r"(put|set)\s+a\s+(spending\s+)?limit\s+on",
        ]
        
        for pattern in set_budget_patterns:
            if re.search(pattern, text_lower):
                logger.debug(f"Rule match: '{text}' → set_budget (pattern: {pattern})")
                return "set_budget", 0.95
        
        # BUDGET_STATUS: Query/check verbs without modification intent
        budget_status_patterns = [
            # "check my budget", "check budget status"
            r"^check\s+(my\s+)?budget",
            # "how is my budget", "how's my budget"
            r"^how('?s|\s+is)\s+(my\s+)?budget",
            # "what is my budget", "what's my budget"
            r"^what('?s|\s+is)\s+(my\s+)?budget",
            # "show my budget", "view my budget"
            r"^(show|view|display)\s+(me\s+)?(my\s+)?budget",
            # "am I over budget", "am I within budget"
            r"^am\s+i\s+(over|under|within|on)\s+budget",
            # "budget status", "budget remaining"
            r"^budget\s+(status|remaining|left|overview)",
        ]
        
        for pattern in budget_status_patterns:
            if re.search(pattern, text_lower):
                logger.debug(f"Rule match: '{text}' → budget_status (pattern: {pattern})")
                return "budget_status", 0.95
        
        # =================================================================
        # TRANSACTION INTENTS
        # =================================================================
        
        # CREATE_TRANSACTION: "add/spent/paid/bought" + amount
        create_transaction_patterns = [
            # "add $50 for lunch", "add 25 dollars for coffee"
            r"^add\s+\$?\d+",
            # "spent $100 on groceries", "spent 50 at walmart"
            r"^(i\s+)?spent\s+\$?\d+",
            # "paid $200 for rent", "paid 50 to john"
            r"^(i\s+)?paid\s+\$?\d+",
            # "bought something for $30"
            r"^(i\s+)?bought\s+",
            # "received $500 salary", "got paid $1000"
            r"^(i\s+)?(received|got\s+paid|earned)\s+\$?\d+",
            # "$50 for coffee", "$100 groceries"
            r"^\$\d+\s+(for|at|on)\s+",
        ]
        
        for pattern in create_transaction_patterns:
            if re.search(pattern, text_lower):
                logger.debug(f"Rule match: '{text}' → add_transaction (pattern: {pattern})")
                return "add_transaction", 0.92
        
        # =================================================================
        # LOAN INTENTS
        # =================================================================
        
        # CHECK_LOAN: Query loan status
        check_loan_patterns = [
            r"^(check|show|view)\s+(my\s+)?loan",
            r"^how\s+much\s+(do\s+i\s+)?owe",
            r"^(what('?s|\s+is)|show)\s+(my\s+)?loan\s+balance",
            r"^(my\s+)?debt\s+status",
            r"^(list|show)\s+(my\s+)?loans",
        ]
        
        for pattern in check_loan_patterns:
            if re.search(pattern, text_lower):
                logger.debug(f"Rule match: '{text}' → check_loan (pattern: {pattern})")
                return "check_loan", 0.95
        
        # LOAN_PAYMENT: Pay towards loan
        loan_payment_patterns = [
            r"^pay\s+\$?\d+\s+(towards?|on|for)\s+(my\s+)?loan",
            r"^make\s+(a\s+)?loan\s+payment",
            r"^(pay\s+off|pay\s+down)\s+(some\s+of\s+)?(my\s+)?loan",
        ]
        
        for pattern in loan_payment_patterns:
            if re.search(pattern, text_lower):
                logger.debug(f"Rule match: '{text}' → make_loan_payment (pattern: {pattern})")
                return "make_loan_payment", 0.92
        
        # ADD_LOAN: Add new loan
        add_loan_patterns = [
            r"^add\s+(a\s+)?(new\s+)?loan",
            r"^(i\s+)?(borrowed|took\s+out)\s+\$?\d+",
            r"^(create|record)\s+(a\s+)?(new\s+)?loan",
            r"^new\s+(debt|loan)\s+of\s+\$?\d+",
        ]
        
        for pattern in add_loan_patterns:
            if re.search(pattern, text_lower):
                logger.debug(f"Rule match: '{text}' → add_loan (pattern: {pattern})")
                return "add_loan", 0.92
        
        # =================================================================
        # QUERY INTENTS
        # =================================================================
        
        # QUERY_SPENDING: "how much" spent questions
        query_spending_patterns = [
            r"^how\s+much\s+(did\s+i|have\s+i)\s+spen[dt]",
            r"^(what|how\s+much)\s+(is|was)\s+my\s+spending",
            r"^total\s+spending\s+(for|on|this)",
            r"^spending\s+(on|for|by)\s+",
        ]
        
        for pattern in query_spending_patterns:
            if re.search(pattern, text_lower):
                logger.debug(f"Rule match: '{text}' → query_spending (pattern: {pattern})")
                return "query_spending", 0.90
        
        # GET_INSIGHTS: Analysis requests
        insights_patterns = [
            r"^(give\s+me|show\s+me|get)\s+(financial\s+)?insights",
            r"^analyze\s+(my\s+)?spending",
            r"^(spending|financial)\s+(trends?|patterns?|habits?)",
            r"^(any\s+)?tips?\s+(for|on|about)\s+(my\s+)?spending",
        ]
        
        for pattern in insights_patterns:
            if re.search(pattern, text_lower):
                logger.debug(f"Rule match: '{text}' → get_insights (pattern: {pattern})")
                return "get_insights", 0.90
        
        # CATEGORIZE: Category questions
        categorize_patterns = [
            r"^what\s+(category|type)\s+(is|for)\s+",
            r"^(which|what)\s+category\s+(should|would|does)",
            r"^categorize\s+",
            r"^how\s+(do\s+i|should\s+i|to)\s+categorize",
        ]
        
        for pattern in categorize_patterns:
            if re.search(pattern, text_lower):
                logger.debug(f"Rule match: '{text}' → categorize_help (pattern: {pattern})")
                return "categorize_help", 0.90
        
        # HELP: Help requests
        if re.search(r"^(help|what\s+can\s+you\s+do|how\s+do\s+i\s+use)", text_lower):
            logger.debug(f"Rule match: '{text}' → help")
            return "help", 0.95
        
        # No rule matched - fall through to semantic matching
        return None

    def classify(self, text: str) -> Tuple[str, float]:
        """
        Classify user text into an intent.
        
        Uses a hybrid approach:
        1. First, try rule-based matching for high-confidence patterns
        2. If no rule matches, use semantic similarity with MiniLM

        Args:
            text: User's input message

        Returns:
            Tuple of (intent_name, confidence_score)
            confidence_score is 0.0 to 1.0

        Example:
            >>> intent, conf = classifier.classify("how much did I spend")
            >>> print(intent, conf)
            query_spending 0.85
        """
        if not self.is_initialized:
            self.initialize()
        
        # Step 1: Try rule-based classification first (high confidence)
        rule_result = self._classify_by_rules(text)
        if rule_result is not None:
            return rule_result

        # Step 2: Use keyword-based fallback if model unavailable
        if self._use_fallback:
            return self._classify_by_keywords(text)

        # Step 3: Semantic similarity matching with MiniLM
        try:
            # Embed user input
            user_embedding = self.model.encode(text, convert_to_numpy=True)

            # Find most similar intent
            best_intent = None
            best_score = -1.0

            for intent, intent_emb in self.intent_embeddings.items():
                # Cosine similarity
                similarity = self._cosine_similarity(user_embedding, intent_emb)
                if similarity > best_score:
                    best_score = similarity
                    best_intent = intent

            # Convert similarity to confidence (0-1 range)
            confidence = max(0.0, min(1.0, best_score))

            logger.debug(
                f"Intent classification: '{text}' → {best_intent} ({confidence:.2f})"
            )

            return best_intent, confidence

        except Exception as e:
            logger.error(f"Intent classification error: {e}", exc_info=True)
            return "general_chat", 0.0

    def classify_with_alternatives(
        self, text: str, top_k: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Get top-k intent predictions with confidence scores.

        Useful when primary intent is uncertain and user needs options.

        Args:
            text: User's input message
            top_k: Number of top intents to return

        Returns:
            List of (intent_name, confidence_score) tuples, sorted by confidence
        """
        if not self.is_initialized:
            self.initialize()

        # Use keyword fallback if model unavailable
        if self._use_fallback:
            primary = self._classify_by_keywords(text)
            return [primary]  # Fallback only returns single result

        try:
            user_embedding = self.model.encode(text, convert_to_numpy=True)

            scores = []
            for intent, intent_emb in self.intent_embeddings.items():
                similarity = self._cosine_similarity(user_embedding, intent_emb)
                confidence = max(0.0, min(1.0, similarity))
                scores.append((intent, confidence))

            # Sort by confidence descending
            scores.sort(key=lambda x: x[1], reverse=True)

            return scores[:top_k]

        except Exception as e:
            logger.error(f"Intent classification error: {e}", exc_info=True)
            return [("general_chat", 0.0)]

    def embed_text(self, text: str) -> np.ndarray:
        """
        Get embedding vector for text.

        Useful for RAG, similarity search, and other embedding-based tasks.

        Args:
            text: Text to embed

        Returns:
            384-dimensional numpy array

        Raises:
            RuntimeError: If using fallback mode (model not available)
        """
        if not self.is_initialized:
            self.initialize()

        if self._use_fallback:
            raise RuntimeError(
                "embed_text requires sentence-transformers. "
                "Install with: pip install sentence-transformers"
            )

        return self.model.encode(text, convert_to_numpy=True)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Get embedding vectors for multiple texts.

        More efficient than calling embed_text multiple times.

        Args:
            texts: List of texts to embed

        Returns:
            2D numpy array of shape (len(texts), 384)

        Raises:
            RuntimeError: If using fallback mode (model not available)
        """
        if not self.is_initialized:
            self.initialize()

        if self._use_fallback:
            raise RuntimeError(
                "embed_batch requires sentence-transformers. "
                "Install with: pip install sentence-transformers"
            )

        return self.model.encode(texts, convert_to_numpy=True)

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.

        Uses sentence_transformers.util.cos_sim for efficiency when available.
        """
        try:
            from app.ai.utils import cos_sim

            return cos_sim(a, b)
        except ImportError:
            # Fallback to manual computation
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return float(np.dot(a, b) / (norm_a * norm_b))

    def _classify_by_keywords(self, text: str) -> Tuple[str, float]:
        """
        Keyword-based fallback when MiniLM model is unavailable.

        Less accurate than semantic matching but works without dependencies.

        Args:
            text: User's input message

        Returns:
            Tuple of (intent_name, confidence_score)
        """
        text_lower = text.lower()

        # Keyword patterns for each intent (ordered by specificity)
        keyword_patterns = {
            "add_transaction": [
                "add",
                "spent",
                "paid",
                "bought",
                "purchase",
                "expense",
                "received",
                "earned",
                "income",
                "got paid",
                "deposit",
            ],
            "categorize_transaction": [
                "categorize",
                "category",
                "classify",
                "what type",
                "label",
            ],
            # Budget status - READ operations (check, view, status, remaining)
            "budget_status": [
                "check budget",
                "budget status",
                "how is my budget",
                "over budget",
                "within budget",
                "budget remaining",
                "show my budget",
                "view my budget",
                "what is my budget",
                "budget left",
                "am i on budget",
            ],
            # Set budget - WRITE operations (set, create, update, change, limit)
            "set_budget": [
                "set budget",
                "set my budget",
                "create budget",
                "create a budget",
                "update budget",
                "change budget",
                "increase budget",
                "decrease budget",
                "lower budget",
                "raise budget",
                "new budget",
                "budget to $",
                "budget to 1",
                "budget to 2",
                "budget to 3",
                "budget to 4",
                "budget to 5",
                "budget to 6",
                "budget to 7",
                "budget to 8",
                "budget to 9",
                "budget of $",
                "spending limit",
                "cap spending",
                "limit groceries",
                "limit food",
                "limit shopping",
                "limit entertainment",
            ],
            "summarize_transactions": [
                "summary",
                "summarize",
                "overview",
                "report",
                "total spent",
                "spending breakdown",
                "how much spent",
                "spent this month",
                "spent this week",
            ],
            "get_insights": [
                "insight",
                "analyze",
                "pattern",
                "trend",
                "habit",
                "advice",
                "suggest",
                "recommend",
                "tips",
            ],
            "help": ["help", "what can you", "how do i", "guide", "tutorial"],
        }

        # Check each pattern
        best_intent = "general_chat"
        best_score = 0

        for intent, keywords in keyword_patterns.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > best_score:
                best_score = matches
                best_intent = intent

        # Confidence based on keyword matches (lower than semantic matching)
        confidence = min(0.7, 0.3 + (best_score * 0.15))

        logger.debug(
            f"Keyword fallback: '{text}' → {best_intent} "
            f"({best_score} matches, {confidence:.2f} conf)"
        )

        return best_intent, confidence

    def get_info(self) -> Dict[str, Any]:
        """Get classifier status and info."""
        return {
            "model": MODEL_NAME if not self._use_fallback else "keyword_fallback",
            "is_initialized": self.is_initialized,
            "using_fallback": self._use_fallback,
            "num_intents": len(INTENT_EXAMPLES),
            "intents": list(INTENT_EXAMPLES.keys()),
            "confidence_threshold": CONFIDENCE_THRESHOLD,
        }


# =============================================================================
# SINGLETON ACCESSOR
# =============================================================================

_classifier: Optional[IntentClassifier] = None


def get_intent_classifier() -> IntentClassifier:
    """Get the intent classifier singleton."""
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier()
    return _classifier


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "IntentClassifier",
    "get_intent_classifier",
    "INTENT_EXAMPLES",
    "CONFIDENCE_THRESHOLD",
]
