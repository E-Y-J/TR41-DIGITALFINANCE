# =============================================================================
# Digital Finance Tracker - Chat Handler
# PURPOSE: Handle natural language commands for CRUD operations
# =============================================================================
"""
Chat Handler Module

This module provides natural language processing for user commands:
- Create transactions from text ("Add $50 for lunch at Subway")
- Edit transactions ("Change my last transaction to $40")
- Delete transactions ("Delete my last transaction")
- Query transactions ("How much did I spend on food?")
- Categorization help ("What category is Uber?")

Intent Types:
    - CREATE_TRANSACTION: User wants to add a new transaction
    - EDIT_TRANSACTION: User wants to modify a transaction
    - DELETE_TRANSACTION: User wants to remove a transaction
    - QUERY_SPENDING: User wants spending information
    - CATEGORIZE: User wants to know a category
    - GENERAL_CHAT: General conversation/help
    - CLARIFY_CATEGORY: User is clarifying a category for a transaction
    - CONFIRM_ACTION: User is confirming a pending action

Usage:
    from app.ai.chat_handler import ChatHandler, get_chat_handler

    # Get singleton instance
    handler = get_chat_handler()

    # Process user message
    response = handler.process_message(user_id, "Add $25 for coffee at Starbucks")
    # {
    #     "intent": "create_transaction",
    #     "action": "create_transaction",
    #     "requires_confirmation": True,
    #     "parsed_data": {...},
    #     "response": "I'll add a $25 expense at Starbucks..."
    # }

Notes:
    - Uses Gemini for NLP parsing
    - Maintains session state for multi-turn conversations
    - All actions require confirmation before execution
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation
import threading
import uuid

from app.core.extensions import db

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # Python < 3.9

logger = logging.getLogger(__name__)


def _serialize_for_json(obj: Any) -> Any:
    """
    Recursively convert objects to JSON-serializable types.

    Handles UUID, Decimal, datetime, and nested dicts/lists.
    """
    if isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: _serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_for_json(item) for item in obj]
    return obj


# =============================================================================
# INTENT TYPES
# =============================================================================


class Intent:
    """Intent type constants."""

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
    # NEW: Disambiguation and financial intents
    DISAMBIGUATE = "disambiguate"
    SET_BUDGET = "set_budget"
    MAKE_LOAN_PAYMENT = "make_loan_payment"
    ADD_LOAN = "add_loan"
    CHECK_LOAN = "check_loan"
    SAVINGS_GOAL = "savings_goal"


# =============================================================================
# AMBIGUOUS COMMAND DETECTION
# =============================================================================

# Keywords that when combined create ambiguous intent
# Each entry maps keyword-pairs to possible intents and clarification prompts
AMBIGUOUS_PATTERNS = {
    # "add X on/to budget" - could be expense or budget increase
    "add_budget": {
        "keywords": [("add", "budget"), ("increase", "budget"), ("put", "budget")],
        "candidates": ["add_transaction", "set_budget"],
        "prompt_template": (
            "I noticed you mentioned '{category}' budget. Did you mean:\n\n"
            "1️⃣ Add a **${amount} expense** under {category}\n"
            "2️⃣ **Increase** your {category} budget limit by ${amount}\n"
            "3️⃣ **Set** your {category} budget to ${amount}\n\n"
            "Reply with 1, 2, or 3"
        ),
    },
    # "add X to/on loan" - could be payment or new debt
    "add_loan": {
        "keywords": [("add", "loan"), ("put", "loan"), ("pay", "loan")],
        "candidates": ["make_loan_payment", "add_loan", "add_transaction"],
        "prompt_template": (
            "I see you mentioned a loan. Did you mean:\n\n"
            "1️⃣ Make a **${amount} loan payment** (reduces debt)\n"
            "2️⃣ Record a **${amount} expense** for loan payment\n"
            "3️⃣ Add a **new ${amount} loan** (new debt)\n\n"
            "Reply with 1, 2, or 3"
        ),
    },
    # "remove/reduce budget" - could be delete transaction or reduce limit
    "remove_budget": {
        "keywords": [
            ("remove", "budget"),
            ("reduce", "budget"),
            ("decrease", "budget"),
        ],
        "candidates": ["delete_transaction", "set_budget"],
        "prompt_template": (
            "Did you mean:\n\n"
            "1️⃣ **Delete** a transaction from {category}\n"
            "2️⃣ **Reduce** your {category} budget limit by ${amount}\n\n"
            "Reply with 1 or 2"
        ),
    },
    # "add to savings" - could be expense categorized as savings or savings goal
    "add_savings": {
        "keywords": [("add", "savings"), ("save", ""), ("put", "savings")],
        "candidates": ["add_transaction", "savings_goal"],
        "prompt_template": (
            "Did you mean:\n\n"
            "1️⃣ Record a **${amount} transfer** to savings account\n"
            "2️⃣ Set a **savings goal** of ${amount}\n\n"
            "Reply with 1 or 2"
        ),
    },
}


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================


class ChatSession:
    """
    Maintains state for a user's chat conversation.

    This class wraps the database-backed AISession model to provide
    a compatible interface while persisting data across restarts.

    The actual data is stored in:
    - ai_sessions table: conversation history, last_intent
    - pending_actions table: actions awaiting confirmation
    """

    def __init__(
        self, user_id: UUID, session_id: Optional[str] = None, db_session=None
    ):
        self.user_id = user_id
        self.session_id = session_id
        self._db_session = db_session  # SQLAlchemy AISession model
        self._pending_action: Optional[Dict[str, Any]] = None
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

        # Load from DB if available
        self._load_from_db()

    def _load_from_db(self):
        """Load session state from database."""
        try:
            from app.models.ai_session import AISession, PendingAction
            from app.core.extensions import db
            from sqlalchemy.orm import object_session
            from sqlalchemy.orm.exc import DetachedInstanceError

            # Check if existing db_session is detached and needs refresh
            if self._db_session is not None:
                try:
                    # Try to access an attribute to check if detached
                    existing_session = object_session(self._db_session)
                    if existing_session is None:
                        # Object is detached, merge it into current session
                        self._db_session = db.session.merge(self._db_session)
                except DetachedInstanceError:
                    # Explicitly detached, reload from DB
                    self._db_session = None

            # Get or create DB session if not available
            if self._db_session is None:
                self._db_session = AISession.get_or_create(self.user_id)

            db.session.commit()

            # Load pending action
            pending = PendingAction.get_pending_for_user(self.user_id)
            if pending and not pending.is_expired():
                self._pending_action = pending.action_data
                self._pending_action["_db_id"] = str(pending.id)

        except Exception as e:
            # Fallback to in-memory if DB unavailable
            logger.warning(f"DB session load failed, using in-memory: {e}")
            self._db_session = None

    @property
    def pending_action(self) -> Optional[Dict[str, Any]]:
        """Get pending action."""
        return self._pending_action

    @property
    def last_intent(self) -> Optional[str]:
        """Get last intent from DB session."""
        if self._db_session:
            return self._db_session.last_intent
        return None

    @last_intent.setter
    def last_intent(self, value: Optional[str]):
        """Set last intent in DB session."""
        if self._db_session:
            self._db_session.last_intent = value
            try:
                from app.core.extensions import db

                db.session.commit()
            except Exception as e:
                logger.warning(f"Failed to save last_intent: {e}")

    @property
    def conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history from DB session."""
        if self._db_session and self._db_session.conversation_history:
            return list(self._db_session.conversation_history)
        return []

    def add_message(self, role: str, content: str):
        """Add a message to conversation history."""
        if self._db_session:
            self._db_session.add_message(role, content)
            try:
                from app.core.extensions import db

                db.session.commit()
            except Exception as e:
                logger.warning(f"Failed to save message: {e}")
        self.updated_at = datetime.now(timezone.utc)

    def set_pending_action(self, action: Dict[str, Any]):
        """Set a pending action that needs confirmation."""
        self._pending_action = action
        self.updated_at = datetime.now(timezone.utc)

        # Store in DB - serialize UUIDs and other non-JSON types
        try:
            from app.models.ai_session import PendingAction
            from app.core.extensions import db

            # Cancel any existing pending actions
            existing = PendingAction.get_pending_for_user(self.user_id)
            if existing:
                existing.cancel()

            # Serialize action data to ensure JSON compatibility
            serialized_action = _serialize_for_json(action)

            # Create new pending action
            db_action = PendingAction.create(
                user_id=self.user_id,
                action_type=action.get("type", "unknown"),
                action_data=serialized_action,
                session_id=self._db_session.id if self._db_session else None,
            )
            db.session.commit()

            # Store DB ID for later reference
            self._pending_action["_db_id"] = str(db_action.id)

        except Exception as e:
            logger.warning(f"Failed to save pending action to DB: {e}")

    def clear_pending_action(self):
        """Clear the pending action."""
        # Update DB
        if self._pending_action and "_db_id" in self._pending_action:
            try:
                from app.models.ai_session import PendingAction
                from app.core.extensions import db
                from uuid import UUID as UUIDType

                db_id = UUIDType(self._pending_action["_db_id"])
                pending = db.session.get(PendingAction, db_id)
                if pending:
                    pending.confirm()
                    db.session.commit()
            except Exception as e:
                logger.warning(f"Failed to clear pending action in DB: {e}")

        self._pending_action = None
        self.updated_at = datetime.now(timezone.utc)

    def get_context(self) -> Dict[str, Any]:
        """Get session context for AI."""
        return {
            "has_pending_action": bool(self._pending_action),
            "pending_action_type": (
                self._pending_action.get("type") if self._pending_action else None
            ),
            "last_intent": self.last_intent,
            "message_count": len(self.conversation_history),
        }


# =============================================================================
# CHAT HANDLER CLASS
# =============================================================================


class ChatHandler:
    """
    Handles natural language chat interactions.

    Processes user messages, extracts intents, and executes or confirms actions.

    Attributes:
        sessions: Dictionary of active user sessions
        gemini: Gemini client for NLP
        is_initialized: Whether handler is ready

    Example:
        >>> handler = ChatHandler()
        >>> handler.initialize()
        >>> response = handler.process_message(
        ...     user_id,
        ...     "Add $50 for dinner at Olive Garden"
        ... )
        >>> print(response["response"])
        "I'll add a $50 expense at Olive Garden under Food & Dining. Confirm?"
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the chat handler."""
        if hasattr(self, "_init_done") and self._init_done:
            return

        self._sessions: Dict[UUID, ChatSession] = {}
        self._session_timeout_minutes = 30
        self.gemini = None
        self.orchestrator = None
        self.intent_classifier = None  # MiniLM-based intent detection
        self.is_initialized = False

        self._init_done = True

    def initialize(self) -> bool:
        """
        Initialize the chat handler and dependencies.

        Returns:
            True if initialized successfully
        """
        if self.is_initialized:
            return True

        try:
            from app.ai.gemini_client import get_gemini_client
            from app.ai.orchestrator import get_orchestrator
            from app.ai.intent_classifier import get_intent_classifier

            self.gemini = get_gemini_client()
            self.orchestrator = get_orchestrator()
            self.intent_classifier = get_intent_classifier()

            # Initialize Gemini
            self.gemini.initialize()

            # Initialize intent classifier (optional - has fallback)
            self.intent_classifier.initialize()

            self.is_initialized = True
            logger.info("Chat handler initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize chat handler: {e}", exc_info=True)
            return False

    def _get_session(self, user_id: UUID, session_id: str = None) -> ChatSession:
        """Get a specific session or create a new one."""
        self._cleanup_sessions()

        if not session_id:
            new_id = str(uuid.uuid4())
            logger.debug(f"✨ Creating fresh session for user {user_id}: {new_id}")
            self._sessions[new_id] = ChatSession(user_id, session_id=new_id)
            return self._sessions[new_id]

        if session_id not in self._sessions:
            self._sessions[session_id] = ChatSession(user_id, session_id=session_id)
        else:
            self._sessions[session_id]._load_from_db()

        return self._sessions[session_id]

    def _get_user_timezone(self) -> timezone:
        """
        Get user's timezone from their settings.

        Returns:
            ZoneInfo timezone object, defaults to UTC if not set or invalid.
        """
        try:
            from app.models.user import User

            user = User.query.get(self.user_id)
            if user and user.settings:
                tz_name = user.settings.get("timezone", "UTC")
                try:
                    return ZoneInfo(tz_name)
                except Exception:
                    logger.debug(f"Invalid timezone '{tz_name}', using UTC")
                    return timezone.utc
        except Exception as e:
            logger.debug(f"Failed to get user timezone: {e}")

        return timezone.utc

    def _cleanup_sessions(self):
        """Remove expired sessions from memory and database."""
        now = datetime.now(timezone.utc)

        # Clean in-memory cache
        expired = [
            uid
            for uid, session in self._sessions.items()
            if (now - session.updated_at).total_seconds()
            > self._session_timeout_minutes * 60
        ]
        for uid in expired:
            del self._sessions[uid]

        # Clean expired DB sessions (periodically, not every call)
        if hasattr(self, "_last_db_cleanup"):
            if (now - self._last_db_cleanup).total_seconds() < 300:  # Every 5 mins
                return

        try:
            from app.models.ai_session import AISession, PendingAction

            AISession.cleanup_expired()
            PendingAction.cleanup_expired()
            self._last_db_cleanup = now
        except Exception as e:
            logger.debug(f"DB cleanup skipped: {e}")

    def process_message(
        self,
        user_id: UUID,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a user message and return response.

        Args:
            user_id: User's UUID
            message: User's message text
            session_id: Optional session ID for conversation continuity
            context: Optional additional context

        Returns:
            Dictionary with response data:
            {
                "intent": "create_transaction",
                "action": "create_transaction" or None,
                "requires_confirmation": True/False,
                "parsed_data": {...} or None,
                "response": "I'll add a $50 expense...",
                "session_id": "uuid-string",
                "alternatives": [] (for category clarification)
            }

        Example:
            >>> response = handler.process_message(user_id, "yes")
            >>> # Confirms pending action
        """
        if not self.is_initialized:
            self.initialize()

        session = self._get_session(user_id, session_id)

        if session and session._db_session:
            session._db_session = db.session.merge(session._db_session)

        session.add_message("user", message)

        # Normalize message
        message_lower = message.strip().lower()

        # Check for disambiguation response (1, 2, or 3)
        if (
            session.pending_action
            and session.pending_action.get("type") == "disambiguation"
        ):
            return self._handle_disambiguation_response(user_id, session, message_lower)

        # Check for confirmation/cancellation of pending action
        if session.pending_action:
            if self._is_confirmation(message_lower):
                return self._execute_pending_action(user_id, session)
            elif self._is_cancellation(message_lower):
                session.clear_pending_action()
                response = "Action cancelled. How else can I help you?"
                session.add_message("assistant", response)
                return {
                    "intent": Intent.CANCEL_ACTION,
                    "action": None,
                    "requires_confirmation": False,
                    "parsed_data": None,
                    "response": response,
                    "session_id": str(user_id),
                }

        # Check for ambiguous commands BEFORE parsing
        ambiguity = self._detect_ambiguity(message_lower)
        if ambiguity:
            return self._handle_ambiguous_command(user_id, session, message, ambiguity)

        # Parse intent and extract data
        parsed = self._parse_message(message, session, context)
        intent = parsed.get("intent", Intent.GENERAL_CHAT)
        session.last_intent = intent

        # Handle different intents
        if intent == Intent.CREATE_TRANSACTION:
            return self._handle_create_transaction(user_id, session, parsed)
        elif intent == Intent.EDIT_TRANSACTION:
            return self._handle_edit_transaction(user_id, session, parsed)
        elif intent == Intent.DELETE_TRANSACTION:
            return self._handle_delete_transaction(user_id, session, parsed)
        elif intent == Intent.QUERY_SPENDING:
            return self._handle_query_spending(user_id, session, parsed)
        elif intent == Intent.QUERY_TRANSACTIONS:
            return self._handle_query_transactions(user_id, session, parsed)
        elif intent == Intent.CATEGORIZE:
            return self._handle_categorize(session, parsed)
        elif intent == Intent.CLARIFY_CATEGORY:
            return self._handle_clarify_category(user_id, session, parsed)
        elif intent == Intent.BUDGET_STATUS:
            return self._handle_budget_status(user_id, session)
        elif intent == Intent.GET_INSIGHTS:
            return self._handle_get_insights(user_id, session)
        elif intent == Intent.HELP:
            return self._handle_help(session)
        # NEW: Financial feature intents
        elif intent == Intent.SET_BUDGET:
            return self._handle_set_budget(user_id, session, parsed)
        elif intent == Intent.MAKE_LOAN_PAYMENT:
            return self._handle_loan_payment(user_id, session, parsed)
        elif intent == Intent.ADD_LOAN:
            return self._handle_add_loan(user_id, session, parsed)
        elif intent == Intent.CHECK_LOAN:
            return self._handle_check_loan(user_id, session)
        elif intent == Intent.SAVINGS_GOAL:
            return self._handle_savings_goal(user_id, session, parsed)
        else:
            return self._handle_general_chat(session, message)

    def _is_confirmation(self, message: str) -> bool:
        """Check if message is a confirmation."""
        confirmations = [
            "yes",
            "y",
            "yeah",
            "yep",
            "sure",
            "ok",
            "okay",
            "confirm",
            "do it",
            "proceed",
            "go ahead",
            "correct",
            "that's right",
            "right",
            "affirmative",
        ]
        return message in confirmations

    def _is_cancellation(self, message: str) -> bool:
        """Check if message is a cancellation."""
        cancellations = [
            "no",
            "n",
            "nope",
            "cancel",
            "nevermind",
            "never mind",
            "stop",
            "abort",
            "don't",
            "forget it",
            "dismiss",
        ]
        return message in cancellations

    def _parse_message(
        self,
        message: str,
        session: ChatSession,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Parse message to extract intent and data.

        Uses a 3-tier approach for best accuracy:
        1. Rule-based parsing (fastest, high confidence patterns)
        2. MiniLM intent classifier (local, semantic understanding)
        3. Gemini parsing (cloud, complex extraction)
        """
        # TIER 0: Check if user is answering a pending question (e.g., just "100")
        pending = session.pending_action
        if pending and pending.get("type") == "create_transaction_awaiting_amount":
            # User might be providing the missing amount
            message_clean = message.strip()
            amount_match = re.match(
                r"^\$?(\d+(?:\.\d{2})?)\s*(?:dollars?|bucks?)?\s*$",
                message_clean,
                re.IGNORECASE,
            )
            if amount_match:
                try:
                    amount = str(Decimal(amount_match.group(1)))
                    partial_data = pending.get("partial_data", {})
                    partial_data["amount"] = amount
                    session.clear_pending_action()
                    logger.info(f"Tier 0: Found pending amount, merged: {partial_data}")
                    return {
                        "intent": Intent.CREATE_TRANSACTION,
                        "confidence": 0.95,
                        "data": partial_data,
                    }
                except (InvalidOperation, ValueError):
                    pass

        # Tier 1: Try rule-based parsing first (fastest)
        rule_based = self._rule_based_parse(message)
        if rule_based.get("confidence", 0) >= 0.8:
            return rule_based

        # Tier 2: Use MiniLM intent classifier for semantic understanding
        if self.intent_classifier and self.intent_classifier.is_initialized:
            intent_name, confidence = self.intent_classifier.classify(message)

            # Map intent classifier intents to ChatHandler intents
            intent_map = {
                "add_transaction": Intent.CREATE_TRANSACTION,
                "categorize_transaction": Intent.CATEGORIZE,
                "categorize_help": Intent.CATEGORIZE,
                "budget_status": Intent.BUDGET_STATUS,
                "set_budget": Intent.SET_BUDGET,
                "summarize_transactions": Intent.QUERY_SPENDING,
                "query_spending": Intent.QUERY_SPENDING,
                "show_transactions": Intent.QUERY_TRANSACTIONS,
                "edit_transaction": Intent.EDIT_TRANSACTION,
                "delete_transaction": Intent.DELETE_TRANSACTION,
                "get_insights": Intent.GET_INSIGHTS,
                "help": Intent.HELP,
                "general_chat": Intent.GENERAL_CHAT,
                # NEW: Financial feature intents
                "make_loan_payment": Intent.MAKE_LOAN_PAYMENT,
                "add_loan": Intent.ADD_LOAN,
                "check_loan": Intent.CHECK_LOAN,
                "savings_goal": Intent.SAVINGS_GOAL,
            }

            mapped_intent = intent_map.get(intent_name, Intent.GENERAL_CHAT)

            if confidence >= 0.7:
                logger.debug(
                    f"Intent classifier: {intent_name} ({confidence:.2f}) → {mapped_intent}"
                )
                # For high-confidence intents, enhance rule_based with the intent
                rule_based["intent"] = mapped_intent
                rule_based["ml_confidence"] = confidence
                rule_based["confidence"] = max(
                    rule_based.get("confidence", 0), confidence
                )

                # If we have a confident intent but low rule_based confidence,
                # extract entities LOCALLY instead of using Gemini
                if rule_based["confidence"] < 0.8 and mapped_intent in [
                    Intent.CREATE_TRANSACTION,
                    Intent.EDIT_TRANSACTION,
                    Intent.QUERY_SPENDING,
                    Intent.SET_BUDGET,
                ]:
                    # Extract entities locally using regex - NO GEMINI NEEDED
                    if mapped_intent == Intent.SET_BUDGET:
                        # Extract budget-specific entities
                        extracted = self._extract_budget_entities(message)
                    else:
                        extracted = self._extract_entities_locally(message)
                    if extracted:
                        rule_based["data"] = extracted
                        rule_based["confidence"] = 0.85  # Boost confidence
                        logger.debug(f"Extracted entities locally: {extracted}")

                return rule_based

        # Tier 3: Try local entity extraction before Gemini
        # Check if message looks like a transaction even if MiniLM was unsure
        transaction_keywords = [
            "bought",
            "spent",
            "paid",
            "purchase",
            "cost",
            "add",
            "expense",
            "income",
        ]
        if any(kw in message.lower() for kw in transaction_keywords):
            extracted = self._extract_entities_locally(message)
            if extracted and (
                extracted.get("amount") or extracted.get("merchant_name")
            ):
                logger.info(
                    f"Tier 3: Local extraction found transaction data: {extracted}"
                )
                return {
                    "intent": Intent.CREATE_TRANSACTION,
                    "confidence": 0.8,
                    "data": extracted,
                }

        # Only use Gemini as ABSOLUTE last resort for truly complex/ambiguous messages
        if self.gemini and self.gemini.is_initialized:
            logger.debug("Tier 3: Falling back to Gemini for complex message")
            return self._gemini_parse(message, session, context)

        return rule_based

    def _rule_based_parse(self, message: str) -> Dict[str, Any]:
        """Rule-based parsing for common patterns."""
        message_lower = message.lower().strip()

        # Help patterns
        if any(
            word in message_lower for word in ["help", "what can you do", "commands"]
        ):
            return {"intent": Intent.HELP, "confidence": 1.0}

        # Create transaction patterns - order matters, more specific first
        create_patterns = [
            # "bought 100 dollars shoes" or "bought $100 shoes" - amount before item
            r"(?:i\s+)?bough?t\s+\$?(\d+(?:\.\d{2})?)\s*(?:dollars?\s+)?(.+?)(?:\s+add\s+it)?(?:\s+to\s+the\s+data)?$",
            # "bought shoes for 100" - item before amount
            r"(?:i\s+)?bough?t\s+(.+?)\s+for\s+\$?(\d+(?:\.\d{2})?)",
            # "spent/spend 100 on/at/for X" (handles typos)
            r"(?:i\s+)?spen[td]?\s+\$?(\d+(?:\.\d{2})?)\s+(?:on|at|for)\s+(.+)",
            # "add 100 for X at Y" - but NOT "add X on/to budget" (handled by disambiguation)
            r"add\s+\$?(\d+(?:\.\d{2})?)\s+for\s+(.+?)(?:\s+at\s+(.+))?$",
            # "paid 100 to/for/at X"
            r"(?:i\s+)?paid\s+\$?(\d+(?:\.\d{2})?)\s+(?:to|for|at)\s+(.+)",
            # "100 dollars for X" or "$100 for X"
            r"^\$?(\d+(?:\.\d{2})?)\s*(?:dollars?\s+)?(?:for|on|at)\s+(.+)",
        ]

        for pattern in create_patterns:
            match = re.search(pattern, message_lower, re.IGNORECASE)
            if match:
                groups = match.groups()
                return self._parse_create_match(groups, message_lower)

        # Delete patterns
        if any(word in message_lower for word in ["delete", "remove"]):
            if "last" in message_lower or "recent" in message_lower:
                return {
                    "intent": Intent.DELETE_TRANSACTION,
                    "target": "last",
                    "confidence": 0.9,
                }

        # Query patterns
        if any(word in message_lower for word in ["how much", "spent", "spending"]):
            return self._parse_query(message_lower)

        # Budget patterns - distinguish between SET and CHECK intents
        if "budget" in message_lower:
            # SET_BUDGET: action verbs indicate modification intent
            set_budget_indicators = [
                "set ",
                "create ",
                "update ",
                "change ",
                "modify ",
                "increase ",
                "decrease ",
                "raise ",
                "lower ",
                "bump ",
                "budget to ",
                "budget of ",
                "limit ",
                "cap ",
            ]
            if any(indicator in message_lower for indicator in set_budget_indicators):
                # Extract amount and category for set_budget
                amount_match = re.search(r"\$?(\d+(?:\.\d{2})?)", message_lower)
                amount = amount_match.group(1) if amount_match else "?"

                # Extract category from message
                category_name = "Unknown"
                known_categories = [
                    "food",
                    "dining",
                    "groceries",
                    "transportation",
                    "transport",
                    "gas",
                    "shopping",
                    "entertainment",
                    "healthcare",
                    "medical",
                    "utilities",
                    "financial",
                    "housing",
                    "rent",
                    "education",
                    "personal",
                    "income",
                    "travel",
                    "subscription",
                ]
                category_map = {
                    "food": "Food & Dining",
                    "dining": "Food & Dining",
                    "groceries": "Food & Dining",
                    "transportation": "Transportation",
                    "transport": "Transportation",
                    "gas": "Transportation",
                    "shopping": "Shopping & Retail",
                    "entertainment": "Entertainment & Recreation",
                    "healthcare": "Healthcare & Medical",
                    "medical": "Healthcare & Medical",
                    "utilities": "Utilities & Services",
                    "financial": "Financial Services",
                    "housing": "Housing & Rent",
                    "rent": "Housing & Rent",
                    "education": "Education",
                    "personal": "Personal & Family",
                    "income": "Income",
                    "travel": "Travel",
                    "subscription": "Subscriptions",
                }
                for kw in known_categories:
                    if kw in message_lower:
                        category_name = category_map.get(kw, "Unknown")
                        break

                return {
                    "intent": Intent.SET_BUDGET,
                    "confidence": 0.95,
                    "data": {
                        "amount": amount,
                        "category_name": category_name,
                        "budget_action": "set",
                    },
                }
            # BUDGET_STATUS: query/check verbs indicate viewing intent
            return {"intent": Intent.BUDGET_STATUS, "confidence": 0.9}

        # Insights patterns
        if any(word in message_lower for word in ["insights", "analysis", "summary"]):
            return {"intent": Intent.GET_INSIGHTS, "confidence": 0.9}

        # Categorize patterns
        if "category" in message_lower or "categorize" in message_lower:
            return {"intent": Intent.CATEGORIZE, "text": message, "confidence": 0.8}

        return {"intent": Intent.GENERAL_CHAT, "confidence": 0.5}

    def _parse_create_match(self, groups: tuple, message_lower: str) -> Dict[str, Any]:
        """Parse a create transaction regex match."""
        try:
            # Extract amount (first number found)
            amount = None
            merchant = None
            description = None

            for g in groups:
                if g:
                    # Try to parse as amount
                    try:
                        val = Decimal(g.replace("$", "").strip())
                        if val > 0:
                            amount = val
                            continue
                    except (InvalidOperation, ValueError):
                        pass
                    # Otherwise it's likely merchant/description
                    if not merchant:
                        merchant = g.strip()
                    else:
                        description = g.strip()

            # Determine transaction type
            tx_type = "expense"
            if any(
                word in message_lower
                for word in ["income", "received", "earned", "salary", "paid me"]
            ):
                tx_type = "income"

            # Parse date using user's timezone
            user_tz = self._get_user_timezone()
            now_local = datetime.now(user_tz)
            date = now_local.strftime("%Y-%m-%d")
            if "yesterday" in message_lower:
                date = (now_local - timedelta(days=1)).strftime("%Y-%m-%d")
            elif "last week" in message_lower:
                date = (now_local - timedelta(days=7)).strftime("%Y-%m-%d")

            return {
                "intent": Intent.CREATE_TRANSACTION,
                "confidence": 0.85,
                "data": {
                    "amount": str(amount) if amount else None,
                    "merchant_name": merchant,
                    "description": description,
                    "transaction_type": tx_type,
                    "date": date,
                },
            }

        except Exception as e:
            logger.error(f"Failed to parse create match: {e}")
            return {"intent": Intent.GENERAL_CHAT, "confidence": 0.5}

    def _parse_query(self, message_lower: str) -> Dict[str, Any]:
        """Parse a spending query."""
        # Extract time period
        period = "monthly"
        if "today" in message_lower:
            period = "daily"
        elif "week" in message_lower:
            period = "weekly"
        elif "year" in message_lower:
            period = "yearly"

        # Extract category
        category = None
        categories = [
            "food",
            "dining",
            "transportation",
            "shopping",
            "entertainment",
            "healthcare",
            "utilities",
            "financial",
            "income",
            "government",
            "charity",
        ]
        for cat in categories:
            if cat in message_lower:
                category = cat
                break

        return {
            "intent": Intent.QUERY_SPENDING,
            "period": period,
            "category": category,
            "confidence": 0.85,
        }

    def _extract_entities_locally(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Extract transaction entities (amount, description, merchant, date) locally.

        Distinguishes between:
        - Description: What was bought (e.g., "shoes", "coffee", "groceries")
        - Merchant: Where it was bought (e.g., "Nike Store", "Starbucks")

        Args:
            message: User's message text

        Returns:
            Dictionary with extracted entities or None if extraction failed
        """
        message_lower = message.lower().strip()

        # Extract amount - look for dollar amounts or contextual numbers
        amount = None
        amount_patterns = [
            r"\$(\d+(?:\.\d{2})?)",  # $100 or $100.00
            r"(\d+(?:\.\d{2})?)\s*dollars?",  # 100 dollars
            r"(\d+(?:\.\d{2})?)\s*bucks?",  # 100 bucks
            r"(?:spent?|paid|spend)\s+\$?(\d+(?:\.\d{2})?)",  # spent/spend/paid 100 (handles typos)
            r"(?:bought|got)\s+(?:for\s+)?\$?(\d+(?:\.\d{2})?)",  # bought for 100
            r"^(\d+(?:\.\d{2})?)\s+(?:on|for|at)\s+",  # 100 on/for/at something
            r"(?:on|for)\s+\$?(\d+(?:\.\d{2})?)\b",  # on/for 100
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, message_lower)
            if match:
                try:
                    amount = str(Decimal(match.group(1)))
                    break
                except (InvalidOperation, ValueError):
                    pass

        # If no pattern matched but message is just a number (follow-up response)
        if not amount:
            just_number = re.match(r"^\$?(\d+(?:\.\d{2})?)\s*$", message_lower.strip())
            if just_number:
                try:
                    amount = str(Decimal(just_number.group(1)))
                except (InvalidOperation, ValueError):
                    pass

        # Extract DESCRIPTION (what was bought) - not merchant
        # Stop words: action phrases, time references, prepositions
        stop_pattern = r"(?:\s+yesterday|\s+today|\s+last|\s+add|\s+on\s+the|\s+to\s+the|\s+it\s+|\s*$)"

        description = None
        description_patterns = [
            # "bought shoes" or "bought 100 dollars shoes"
            rf"bought\s+(?:\$?\d+(?:\.\d{2})?\s*(?:dollars?\s+)?)?([a-zA-Z][a-zA-Z\s]*?){stop_pattern}",
            # "spent/spend on/for/at shoes" or "paid for/at shoes" (handles typos + all prepositions)
            rf"(?:spent?|spend|paid)\s+(?:\$?\d+(?:\.\d{2})?\s+)?(?:on|for|at)\s+([a-zA-Z][a-zA-Z\s]*?){stop_pattern}",
            # "100 on/for/at shoes" or "100 dollars on/for/at shoes"
            rf"\d+\s*(?:dollars?\s+)?(?:on|for|at)\s+([a-zA-Z][a-zA-Z\s]*?){stop_pattern}",
        ]
        for pattern in description_patterns:
            match = re.search(pattern, message_lower, re.IGNORECASE)
            if match:
                description = match.group(1).strip()
                # Clean up common suffixes
                description = re.sub(
                    r"\s+(yesterday|today|last\s+week|add\s+it)", "", description
                ).strip()
                if description and len(description) > 1:
                    break

        # Extract MERCHANT (where it was bought) - specific stores from "at X" or "from X"
        # Only extract if it looks like a proper store name (capitalized or known chains)
        merchant = None
        merchant_patterns = [
            # "at Starbucks", "at Walmart" - proper nouns after "at" followed by "for" or time
            r"\s+at\s+([A-Z][a-zA-Z\s\']+?)(?:\s+for|\s+yesterday|\s+today|\s*$)",
            r"\s+from\s+([A-Z][a-zA-Z\s\']+?)(?:\s+for|\s+yesterday|\s+today|\s*$)",
        ]
        for pattern in merchant_patterns:
            match = re.search(
                pattern, message, re.IGNORECASE
            )  # Use original message for case
            if match:
                merchant = match.group(1).strip()
                if merchant and len(merchant) > 1:
                    break

        # Use description as merchant_name for display if no specific merchant
        # The description (e.g., "restaurant", "grocery") will be used for categorization
        if not merchant and description:
            merchant = description.title()  # Capitalize for display

        # Extract date
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if "yesterday" in message_lower:
            date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        elif "last week" in message_lower:
            date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
        elif "today" in message_lower:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Determine transaction type
        tx_type = "expense"
        if any(
            word in message_lower
            for word in [
                "income",
                "received",
                "earned",
                "salary",
                "paid me",
                "got paid",
            ]
        ):
            tx_type = "income"

        # Only return if we extracted something useful
        if amount or description or merchant:
            return {
                "amount": amount,
                "merchant_name": merchant,  # Store/location if specified
                "description": description,  # Product/item name
                "transaction_type": tx_type,
                "date": date,
            }

        return None

    def _extract_budget_entities(self, message: str) -> Dict[str, Any]:
        """
        Extract budget-related entities (amount, category) from message.

        Args:
            message: User's message text

        Returns:
            Dictionary with extracted budget entities
        """
        message_lower = message.lower().strip()

        # Extract amount - order matters, more specific patterns first
        amount = "?"
        amount_patterns = [
            r"\$(\d+(?:\.\d{2})?)",  # $500
            r"(\d+(?:\.\d{2})?)\s*dollars?",  # 500 dollars
            r"budget\s+(?:to|of|at|for)\s+\$?(\d+(?:\.\d{2})?)",  # budget to 500
            r"(?:to|of|at)\s+\$?(\d+(?:\.\d{2})?)\s*$",  # to 500 (at end)
            r"(\d+(?:\.\d{2})?)\s+budget",  # 500 budget
            r"\b(\d+(?:\.\d{2})?)\b",  # any standalone number as fallback
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, message_lower)
            if match:
                try:
                    val = Decimal(match.group(1))
                    if val > 0:  # Only accept positive amounts
                        amount = str(val)
                        break
                except (InvalidOperation, ValueError):
                    pass

        # Extract category - map common keywords to full category names
        category_name = "Unknown"
        category_map = {
            "food": "Food & Dining",
            "dining": "Food & Dining",
            "groceries": "Food & Dining",
            "grocery": "Food & Dining",
            "restaurant": "Food & Dining",
            "transportation": "Transportation",
            "transport": "Transportation",
            "gas": "Transportation",
            "car": "Transportation",
            "shopping": "Shopping & Retail",
            "retail": "Shopping & Retail",
            "entertainment": "Entertainment & Recreation",
            "recreation": "Entertainment & Recreation",
            "healthcare": "Healthcare & Medical",
            "medical": "Healthcare & Medical",
            "health": "Healthcare & Medical",
            "utilities": "Utilities & Services",
            "utility": "Utilities & Services",
            "financial": "Financial Services",
            "finance": "Financial Services",
            "housing": "Housing & Rent",
            "rent": "Housing & Rent",
            "education": "Education",
            "school": "Education",
            "personal": "Personal & Family",
            "family": "Personal & Family",
            "income": "Income",
            "travel": "Travel",
            "vacation": "Travel",
            "subscription": "Subscriptions",
            "subscriptions": "Subscriptions",
        }

        for keyword, cat_name in category_map.items():
            if keyword in message_lower:
                category_name = cat_name
                break

        # Determine budget action
        action = "set"
        if any(
            word in message_lower for word in ["increase", "raise", "bump up", "add"]
        ):
            action = "increase"
        elif any(
            word in message_lower for word in ["decrease", "reduce", "lower", "cut"]
        ):
            action = "decrease"

        return {
            "amount": amount,
            "category_name": category_name,
            "budget_action": action,
        }

    def _gemini_parse(
        self,
        message: str,
        session: ChatSession,
        context: Optional[Dict[str, Any]],
        hint_intent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Use Gemini for complex message parsing.

        Args:
            message: User's message text
            session: Chat session with context
            context: Optional additional context
            hint_intent: Optional intent hint from MiniLM classifier

        Returns:
            Parsed intent and data dictionary
        """
        try:
            # If we have an intent hint from MiniLM, ask Gemini to extract entities
            intent_guidance = ""
            if hint_intent:
                intent_guidance = f"""
The intent has been pre-classified as "{hint_intent}" with high confidence.
Focus on extracting the relevant data for this intent type.
"""

            prompt = f"""You are parsing a user message for a finance app chatbot.

MESSAGE: "{message}"
{intent_guidance}
CONTEXT:
{json.dumps(session.get_context())}

Determine the user's intent and extract relevant data. Respond with ONLY valid JSON:

{{
    "intent": "create_transaction" | "edit_transaction" | "delete_transaction" | "query_spending" | "categorize" | "budget_status" | "get_insights" | "help" | "general_chat",
    "confidence": 0.0-1.0,
    "data": {{
        "amount": "50.00" or null,
        "merchant_name": "string" or null,
        "transaction_type": "expense" | "income" or null,
        "date": "YYYY-MM-DD" or null,
        "category": "string" or null,
        "period": "day" | "week" | "month" | "year" or null
    }},
    "explanation": "Brief explanation of interpretation"
}}

ONLY respond with the JSON, no other text."""

            response_text = self.gemini.model.generate_content(prompt).text.strip()

            # Clean and parse
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])

            parsed = json.loads(response_text)

            # If we had a hint_intent, use it to override if Gemini disagrees
            if hint_intent and parsed.get("intent") != hint_intent:
                logger.debug(
                    f"Using MiniLM intent ({hint_intent}) over Gemini ({parsed.get('intent')})"
                )
                parsed["intent"] = hint_intent

            return parsed

        except Exception as e:
            logger.error(f"Gemini parse failed: {e}")
            # On Gemini failure, fall back to enhanced rule-based parsing
            rule_result = self._rule_based_parse(message)
            if hint_intent:
                rule_result["intent"] = hint_intent
            # Add rate limit info if quota error
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                rule_result["rate_limited"] = True
            return rule_result

    def _handle_create_transaction(
        self,
        user_id: UUID,
        session: ChatSession,
        parsed: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle create transaction intent."""
        data = parsed.get("data", {})

        # Validate required fields
        if not data.get("amount"):
            response = "I need to know the amount. How much was the transaction?"
            session.add_message("assistant", response)

            # Save pending action so we can resume when user provides amount
            session.set_pending_action(
                {
                    "type": "create_transaction_awaiting_amount",
                    "partial_data": data,
                }
            )

            return {
                "intent": Intent.CREATE_TRANSACTION,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": data,
                "response": response,
                "session_id": str(user_id),
            }

        # Auto-categorize using description or merchant name
        category_info = None
        categorize_text = data.get("description") or data.get("merchant_name")
        if categorize_text and self.orchestrator:
            cat_result = self.orchestrator.categorize(
                categorize_text,
                amount=float(data["amount"]) if data.get("amount") else None,
                transaction_type=data.get("transaction_type"),
            )
            data["category_id"] = (
                str(cat_result["category_id"]) if cat_result["category_id"] else None
            )
            data["category_name"] = cat_result["category"]
            data["ai_confidence"] = cat_result["confidence"]
            data["ai_source"] = cat_result["source"]
            category_info = cat_result

        # Build confirmation message
        amount = data.get("amount", "?")
        description = data.get("description")
        merchant = data.get("merchant_name", "Unknown")
        tx_type = data.get("transaction_type", "expense")
        category = data.get("category_name", "Unknown")
        date = data.get("date", "today")

        # Smart message: show product vs location appropriately
        # If merchant is a category keyword (e.g., "food" -> "Food & Dining"), omit it
        merchant_is_category = (
            category != "Unknown" and merchant and merchant.lower() in category.lower()
        )

        if description and merchant and description.lower() != merchant.lower():
            # Both product and store specified: "bought shoes at Nike Store"
            what_where = f"for **{description}** at {merchant}"
        elif description:
            # Only product: "bought shoes"
            what_where = f"for **{description}**"
        elif merchant_is_category:
            # Merchant is just a category word (e.g., "food" for "Food & Dining")
            # Skip showing it separately since category is already shown
            what_where = ""
        else:
            # Only merchant/location: "at Starbucks"
            what_where = f"at **{merchant}**"

        # Build response - handle empty what_where
        if what_where:
            response = (
                f"I'll add a **${amount}** {tx_type} {what_where} "
                f"under **{category}** for {date}.\n\n"
                f"**Confirm?** (yes/no)"
            )
        else:
            response = (
                f"I'll add a **${amount}** {tx_type} "
                f"under **{category}** for {date}.\n\n"
                f"**Confirm?** (yes/no)"
            )

        # Set pending action
        session.set_pending_action(
            {
                "type": "create_transaction",
                "data": data,
                "category_info": category_info,
            }
        )

        session.add_message("assistant", response)

        return {
            "intent": Intent.CREATE_TRANSACTION,
            "action": "create_transaction",
            "requires_confirmation": True,
            "parsed_data": data,
            "response": response,
            "session_id": str(user_id),
            "alternatives": (
                category_info.get("alternatives", []) if category_info else []
            ),
        }

    def _handle_edit_transaction(
        self,
        user_id: UUID,
        session: ChatSession,
        parsed: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle edit transaction intent."""
        response = (
            "To edit a transaction, I need to know:\n"
            "1. Which transaction (e.g., 'my last transaction' or transaction ID)\n"
            "2. What to change (amount, category, date, etc.)\n\n"
            "For example: 'Change my last transaction to $40'"
        )
        session.add_message("assistant", response)
        return {
            "intent": Intent.EDIT_TRANSACTION,
            "action": None,
            "requires_confirmation": False,
            "parsed_data": parsed.get("data"),
            "response": response,
            "session_id": str(user_id),
        }

    def _handle_delete_transaction(
        self,
        user_id: UUID,
        session: ChatSession,
        parsed: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle delete transaction intent."""
        try:
            from app.models.transaction import Transaction
            from sqlalchemy import desc

            target = parsed.get("target", "last")

            if target == "last":
                # Get last transaction
                last_tx = (
                    Transaction.query.filter_by(user_id=user_id)
                    .order_by(desc(Transaction.created_at))
                    .first()
                )

                if not last_tx:
                    response = "You don't have any transactions to delete."
                    session.add_message("assistant", response)
                    return {
                        "intent": Intent.DELETE_TRANSACTION,
                        "action": None,
                        "requires_confirmation": False,
                        "parsed_data": None,
                        "response": response,
                        "session_id": str(user_id),
                    }

                # Build confirmation
                response = (
                    f"Delete this transaction?\n\n"
                    f"**${last_tx.amount}** at {last_tx.merchant_name or 'Unknown'} "
                    f"on {last_tx.date}\n\n"
                    f"**Confirm?** (yes/no)"
                )

                session.set_pending_action(
                    {
                        "type": "delete_transaction",
                        "transaction_id": str(last_tx.id),
                        "transaction_info": {
                            "amount": str(last_tx.amount),
                            "merchant": last_tx.merchant_name,
                            "date": last_tx.date,
                        },
                    }
                )

                session.add_message("assistant", response)
                return {
                    "intent": Intent.DELETE_TRANSACTION,
                    "action": "delete_transaction",
                    "requires_confirmation": True,
                    "parsed_data": {"transaction_id": str(last_tx.id)},
                    "response": response,
                    "session_id": str(user_id),
                }

        except Exception as e:
            logger.error(f"Delete transaction handling failed: {e}", exc_info=True)

        response = "I couldn't find the transaction. Please try again."
        session.add_message("assistant", response)
        return {
            "intent": Intent.DELETE_TRANSACTION,
            "action": None,
            "requires_confirmation": False,
            "parsed_data": None,
            "response": response,
            "session_id": str(user_id),
        }

    def _handle_query_spending(
        self,
        user_id: UUID,
        session: ChatSession,
        parsed: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle spending query."""
        try:
            from app.services.summary_service import SummaryService

            period = parsed.get("period", "month")
            _category = parsed.get("category")  # Reserved for future filtering

            # Get summary
            summary = SummaryService.get_spending_summary(user_id, period)

            # Build response
            total = summary.get("total_expense", 0)
            response = f"You've spent **${total:.2f}** this {period}."

            if summary.get("by_category"):
                response += "\n\n**By category:**\n"
                for cat in summary["by_category"][:5]:
                    response += f"- {cat['category_name']}: ${cat['total']:.2f}\n"

            session.add_message("assistant", response)
            return {
                "intent": Intent.QUERY_SPENDING,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": summary,
                "response": response,
                "session_id": str(user_id),
            }

        except Exception as e:
            logger.error(f"Query spending failed: {e}", exc_info=True)
            response = "I couldn't retrieve your spending data. Please try again."
            session.add_message("assistant", response)
            return {
                "intent": Intent.QUERY_SPENDING,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": None,
                "response": response,
                "session_id": str(user_id),
            }

    def _handle_query_transactions(
        self,
        user_id: UUID,
        session: ChatSession,
        parsed: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle transaction list query."""
        response = (
            "Please use the transactions page to view your full transaction history."
        )
        session.add_message("assistant", response)
        return {
            "intent": Intent.QUERY_TRANSACTIONS,
            "action": None,
            "requires_confirmation": False,
            "parsed_data": None,
            "response": response,
            "session_id": str(user_id),
        }

    def _handle_categorize(
        self,
        session: ChatSession,
        parsed: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle categorization question."""
        text = parsed.get("text", "")

        if self.orchestrator:
            result = self.orchestrator.categorize(text)
            response = (
                f"**{text}** would be categorized as **{result['category']}** "
                f"(confidence: {result['confidence']:.0%})"
            )
        else:
            response = "The categorization service is not available right now."

        session.add_message("assistant", response)
        return {
            "intent": Intent.CATEGORIZE,
            "action": None,
            "requires_confirmation": False,
            "parsed_data": result if self.orchestrator else None,
            "response": response,
            "session_id": str(session.user_id),
        }

    def _handle_clarify_category(
        self,
        user_id: UUID,
        session: ChatSession,
        parsed: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle category clarification from user."""
        category_name = parsed.get("category")

        if (
            session.pending_action
            and session.pending_action.get("type") == "clarify_category"
        ):
            transaction_id = session.pending_action.get("transaction_id")

            try:
                from app.services.transaction_service import TransactionService
                from app.services.category_service import CategoryService

                # Get category
                category = CategoryService.get_by_name(category_name)
                if category:
                    # Update transaction
                    TransactionService.update_category(
                        user_id, transaction_id, category.id
                    )
                    response = (
                        f"Got it! I've updated that transaction to **{category.name}**."
                    )
                    session.clear_pending_action()
                else:
                    response = f"I don't recognize '{category_name}' as a category. Please try again."

            except Exception as e:
                logger.error(f"Category clarification failed: {e}")
                response = "I couldn't update the category. Please try again."

        else:
            response = "I'm not waiting for a category clarification right now."

        session.add_message("assistant", response)
        return {
            "intent": Intent.CLARIFY_CATEGORY,
            "action": None,
            "requires_confirmation": False,
            "parsed_data": None,
            "response": response,
            "session_id": str(user_id),
        }

    def _handle_budget_status(
        self,
        user_id: UUID,
        session: ChatSession,
    ) -> Dict[str, Any]:
        """Handle budget status query."""
        try:
            from app.services.budget_service import BudgetService

            budgets = BudgetService.get_budgets_with_spending(user_id)

            if not budgets:
                response = "You haven't set up any budgets yet. Would you like me to help you create one?"
            else:
                response = "**Your Budget Status:**\n\n"
                for b in budgets[:5]:
                    pct = float(b.get("percentage_used", 0) or 0)
                    spent = float(b.get("spent", 0) or 0)
                    budget_amt = float(b.get("budget_amount", 0) or 0)
                    status = "✅" if pct < 70 else "⚠️" if pct < 100 else "🔴"
                    response += (
                        f"{status} **{b.get('category_name', 'Total')}**: "
                        f"${spent:.2f} / ${budget_amt:.2f} "
                        f"({pct:.0f}%)\n"
                    )

            session.add_message("assistant", response)
            return {
                "intent": Intent.BUDGET_STATUS,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": budgets,
                "response": response,
                "session_id": str(session.session_id),
            }

        except Exception as e:
            logger.error(f"Budget status failed: {e}", exc_info=True)
            response = "I couldn't retrieve your budget status."
            session.add_message("assistant", response)
            return {
                "intent": Intent.BUDGET_STATUS,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": None,
                "response": response,
                "session_id": str(session.session_id),
            }

    def _handle_get_insights(
        self,
        user_id: UUID,
        session: ChatSession,
    ) -> Dict[str, Any]:
        """Handle insights request."""
        try:
            from app.ai.anomaly_detector import get_detector

            detector = get_detector()
            insights = detector.get_spending_insights(user_id)

            response = (
                f"**Spending Insights ({insights.get('period', 'Last 30 days')})**\n\n"
            )

            # Top categories
            if insights.get("top_categories"):
                response += "**Top spending categories:**\n"
                for cat in insights["top_categories"][:3]:
                    response += f"- {cat['category_name']}: ${cat['total_spent']:.2f}\n"
                response += "\n"

            # Spending trend
            trend = insights.get("spending_trend", "unknown")
            trend_emoji = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}.get(
                trend, "❓"
            )
            response += f"**Trend:** {trend_emoji} {trend.title()}\n\n"

            # Recommendations
            if insights.get("recommendations"):
                response += "**Tips:**\n"
                for rec in insights["recommendations"]:
                    response += f"• {rec}\n"

            session.add_message("assistant", response)
            return {
                "intent": Intent.GET_INSIGHTS,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": insights,
                "response": response,
                "session_id": str(session.session_id),
            }

        except Exception as e:
            logger.error(f"Get insights failed: {e}", exc_info=True)
            response = "I couldn't generate your spending insights right now."
            session.add_message("assistant", response)
            return {
                "intent": Intent.GET_INSIGHTS,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": None,
                "response": response,
                "session_id": str(session.session_id),
            }

    def _handle_help(self, session: ChatSession) -> Dict[str, Any]:
        """Handle help request."""
        response = """**I can help you with:**

📝 **Transactions:**
- "Add $50 for lunch at Subway"
- "Spent $30 on groceries"
- "Delete my last transaction"

📊 **Budgets:**
- "Check my budget status"
- "Set my food budget to $500"
- "Increase my shopping budget by $100"

💳 **Loans:**
- "Check my loans"
- "Pay $200 towards my loan"
- "Add a new loan"

💰 **Spending Analysis:**
- "How much did I spend this month?"
- "What's my spending on food?"
- "Show my spending insights"

❓ **Categorization:**
- "What category is Uber?"

Just ask naturally and I'll help!"""

        session.add_message("assistant", response)
        return {
            "intent": Intent.HELP,
            "action": None,
            "requires_confirmation": False,
            "parsed_data": None,
            "response": response,
            "session_id": str(session.session_id),
        }

    # =========================================================================
    # DISAMBIGUATION METHODS
    # =========================================================================

    def _detect_ambiguity(self, message_lower: str) -> Optional[Dict[str, Any]]:
        """
        Detect if message contains ambiguous intent.

        Checks for keyword combinations that could have multiple meanings.

        Args:
            message_lower: Lowercased user message

        Returns:
            Ambiguity pattern dict if found, None otherwise
        """
        for pattern_name, pattern_data in AMBIGUOUS_PATTERNS.items():
            for keyword_pair in pattern_data["keywords"]:
                kw1, kw2 = keyword_pair
                # Both keywords must be present (or kw2 is empty for single-keyword patterns)
                if kw1 in message_lower and (not kw2 or kw2 in message_lower):
                    logger.info(f"Detected ambiguous pattern: {pattern_name}")
                    return {
                        "pattern": pattern_name,
                        **pattern_data,
                    }
        return None

    def _extract_amount_and_category(self, message: str) -> Dict[str, Any]:
        """Extract amount and category from ambiguous message."""
        message_lower = message.lower()

        # Extract amount
        amount = None
        amount_patterns = [
            r"\$(\d+(?:\.\d{2})?)",
            r"(\d+(?:\.\d{2})?)\s*(?:dollars?|bucks?)?",
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, message_lower)
            if match:
                try:
                    amount = str(Decimal(match.group(1)))
                    break
                except (InvalidOperation, ValueError):
                    pass

        # Extract category from known category keywords
        category = "Unknown"
        category_keywords = {
            "food": "Food & Dining",
            "dining": "Food & Dining",
            "grocery": "Food & Dining",
            "groceries": "Food & Dining",
            "transportation": "Transportation",
            "transport": "Transportation",
            "gas": "Transportation",
            "shopping": "Shopping & Retail",
            "entertainment": "Entertainment & Recreation",
            "healthcare": "Healthcare & Medical",
            "medical": "Healthcare & Medical",
            "utilities": "Utilities & Services",
            "financial": "Financial Services",
            "loan": "Financial Services",
        }
        for keyword, cat_name in category_keywords.items():
            if keyword in message_lower:
                category = cat_name
                break

        return {"amount": amount or "?", "category": category}

    def _handle_ambiguous_command(
        self,
        user_id: UUID,
        session: ChatSession,
        message: str,
        ambiguity: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Handle ambiguous commands by asking for clarification.

        Sets pending action with disambiguation context.
        """
        # Extract relevant data from message
        extracted = self._extract_amount_and_category(message)

        # Build clarification prompt
        prompt = ambiguity["prompt_template"].format(
            amount=extracted["amount"],
            category=extracted["category"],
        )

        # Store disambiguation context as pending action
        session.set_pending_action(
            {
                "type": "disambiguation",
                "pattern": ambiguity["pattern"],
                "candidates": ambiguity["candidates"],
                "extracted_data": extracted,
                "original_message": message,
            }
        )

        session.add_message("assistant", prompt)

        return {
            "intent": Intent.DISAMBIGUATE,
            "action": None,
            "requires_confirmation": False,
            "parsed_data": extracted,
            "response": prompt,
            "session_id": str(user_id),
        }

    def _handle_disambiguation_response(
        self,
        user_id: UUID,
        session: ChatSession,
        response: str,
    ) -> Dict[str, Any]:
        """
        Handle user's response to disambiguation prompt.

        Maps 1/2/3 responses to specific intents and routes accordingly.
        """
        pending = session.pending_action
        candidates = pending.get("candidates", [])
        extracted = pending.get("extracted_data", {})
        original_message = pending.get("original_message", "")

        # Parse user choice
        choice = None
        if response in ["1", "one", "first"]:
            choice = 0
        elif response in ["2", "two", "second"]:
            choice = 1
        elif response in ["3", "three", "third"]:
            choice = 2
        elif self._is_cancellation(response):
            session.clear_pending_action()
            resp = "No problem! What would you like to do instead?"
            session.add_message("assistant", resp)
            return {
                "intent": Intent.CANCEL_ACTION,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": None,
                "response": resp,
                "session_id": str(user_id),
            }

        if choice is None or choice >= len(candidates):
            resp = f"Please reply with a number (1-{len(candidates)}) or 'cancel' to start over."
            session.add_message("assistant", resp)
            return {
                "intent": Intent.DISAMBIGUATE,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": None,
                "response": resp,
                "session_id": str(user_id),
            }

        # Clear disambiguation pending action
        session.clear_pending_action()

        # Route to the selected intent
        selected_intent = candidates[choice]
        logger.info(f"User selected option {choice + 1}: {selected_intent}")

        # Map to Intent constant and handle
        intent_map = {
            "add_transaction": Intent.CREATE_TRANSACTION,
            "set_budget": Intent.SET_BUDGET,
            "make_loan_payment": Intent.MAKE_LOAN_PAYMENT,
            "add_loan": Intent.ADD_LOAN,
            "delete_transaction": Intent.DELETE_TRANSACTION,
            "savings_goal": Intent.SAVINGS_GOAL,
        }

        intent = intent_map.get(selected_intent, Intent.GENERAL_CHAT)
        parsed = {
            "intent": intent,
            "confidence": 1.0,
            "data": {
                "amount": extracted.get("amount"),
                "category_name": extracted.get("category"),
                "transaction_type": "expense",
            },
        }

        # Route to appropriate handler
        if intent == Intent.CREATE_TRANSACTION:
            return self._handle_create_transaction(user_id, session, parsed)
        elif intent == Intent.SET_BUDGET:
            # Check if this is option 2 (increase) or 3 (set to)
            if choice == 1:  # Increase by amount
                parsed["data"]["budget_action"] = "increase"
            else:  # Set to amount (choice == 2)
                parsed["data"]["budget_action"] = "set"
            return self._handle_set_budget(user_id, session, parsed)
        elif intent == Intent.MAKE_LOAN_PAYMENT:
            return self._handle_loan_payment(user_id, session, parsed)
        elif intent == Intent.ADD_LOAN:
            return self._handle_add_loan(user_id, session, parsed)
        elif intent == Intent.DELETE_TRANSACTION:
            return self._handle_delete_transaction(user_id, session, parsed)
        elif intent == Intent.SAVINGS_GOAL:
            return self._handle_savings_goal(user_id, session, parsed)
        else:
            return self._handle_general_chat(session, original_message)

    # =========================================================================
    # NEW FINANCIAL FEATURE HANDLERS
    # =========================================================================

    def _handle_set_budget(
        self,
        user_id: UUID,
        session: ChatSession,
        parsed: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle set/increase budget intent."""
        data = parsed.get("data", {})
        amount = data.get("amount", "?")
        category = data.get("category_name", "Unknown")
        action = data.get("budget_action", "set")  # "set" or "increase"

        # Validate amount before proceeding
        if amount == "?" or not amount:
            response = (
                f"I'd like to help you with your **{category}** budget.\n\n"
                "Please specify the amount. For example:\n"
                '• "Set my food budget to $500"\n'
                '• "I want a $300 budget for groceries"'
            )
            session.add_message("assistant", response)
            return {
                "intent": Intent.SET_BUDGET,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": data,
                "response": response,
                "session_id": str(user_id),
            }

        # Validate amount is a valid number
        try:
            float(amount)
        except (ValueError, TypeError):
            response = (
                f"I couldn't understand the amount '{amount}'.\n\n"
                "Please specify a valid number. For example:\n"
                '• "Set my budget to $500"\n'
                '• "I want a 300 budget"'
            )
            session.add_message("assistant", response)
            return {
                "intent": Intent.SET_BUDGET,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": data,
                "response": response,
                "session_id": str(user_id),
            }

        try:
            from app.models.budget import Budget
            from app.models.category import Category as CategoryModel
            from app.models.enums import BudgetPeriod

            # Get category
            cat = CategoryModel.get_by_name(category)
            if not cat:
                response = f"I couldn't find the '{category}' category. Please specify a valid category."
                session.add_message("assistant", response)
                return {
                    "intent": Intent.SET_BUDGET,
                    "action": None,
                    "requires_confirmation": False,
                    "parsed_data": data,
                    "response": response,
                    "session_id": str(user_id),
                }

            # Check for existing budget
            existing = Budget.query.filter_by(
                user_id=user_id,
                category_id=cat.id,
            ).first()

            if action == "increase" and existing:
                new_amount = float(existing.amount) + float(amount)
                action_desc = f"increase from ${existing.amount} to ${new_amount}"
            elif action == "set":
                new_amount = float(amount)
                action_desc = f"set to ${amount}"
            else:
                new_amount = float(amount)
                action_desc = f"set to ${amount}"

            # Build confirmation
            response = (
                f"I'll **{action_desc}** your **{category}** budget.\n\n"
                f"**Confirm?** (yes/no)"
            )

            session.set_pending_action(
                {
                    "type": "set_budget",
                    "data": {
                        "user_id": str(user_id),
                        "category_id": str(cat.id),
                        "category_name": category,
                        "amount": str(new_amount),
                        "action": action,
                        "period": BudgetPeriod.MONTHLY.value,
                    },
                }
            )

            session.add_message("assistant", response)
            return {
                "intent": Intent.SET_BUDGET,
                "action": "set_budget",
                "requires_confirmation": True,
                "parsed_data": data,
                "response": response,
                "session_id": str(user_id),
            }

        except Exception as e:
            logger.error(f"Error handling set_budget: {e}", exc_info=True)
            response = "I had trouble processing your budget request. Please try again."
            session.add_message("assistant", response)
            return {
                "intent": Intent.SET_BUDGET,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": data,
                "response": response,
                "session_id": str(user_id),
            }

    def _handle_loan_payment(
        self,
        user_id: UUID,
        session: ChatSession,
        parsed: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Handle loan payment intent.

        Creates a transaction AND reduces loan balance.
        """
        data = parsed.get("data", {})
        amount = data.get("amount", "?")

        try:
            from app.models.loan import Loan
            from app.models.category import Category as CategoryModel

            # Get user's loans
            loans = Loan.query.filter_by(user_id=user_id).all()
            open_loans = [loan for loan in loans if loan.status.value == "open"]

            if not open_loans:
                response = (
                    "You don't have any open loans. Would you like to:\n\n"
                    "1️⃣ Add a new loan\n"
                    "2️⃣ Record this as a regular expense\n\n"
                    "Reply with 1 or 2"
                )
                session.set_pending_action(
                    {
                        "type": "disambiguation",
                        "pattern": "no_loans",
                        "candidates": ["add_loan", "add_transaction"],
                        "extracted_data": data,
                        "original_message": "",
                    }
                )
                session.add_message("assistant", response)
                return {
                    "intent": Intent.DISAMBIGUATE,
                    "action": None,
                    "requires_confirmation": False,
                    "parsed_data": data,
                    "response": response,
                    "session_id": str(user_id),
                }

            # Get Financial Services category for the expense
            fin_cat = CategoryModel.get_by_name("Financial Services")

            # If multiple loans, ask which one (future enhancement)
            loan = open_loans[0]

            response = (
                f"I'll record a **${amount} loan payment** for '{loan.name}':\n\n"
                f"• Create expense transaction under Financial Services\n"
                f"• Reduce loan balance from ${loan.remaining_amount} to ${float(loan.remaining_amount) - float(amount)}\n\n"
                f"**Confirm?** (yes/no)"
            )

            session.set_pending_action(
                {
                    "type": "make_loan_payment",
                    "data": {
                        "user_id": str(user_id),
                        "loan_id": str(loan.id),
                        "loan_name": loan.name,
                        "amount": str(amount),
                        "category_id": str(fin_cat.id) if fin_cat else None,
                        "create_transaction": True,
                    },
                }
            )

            session.add_message("assistant", response)
            return {
                "intent": Intent.MAKE_LOAN_PAYMENT,
                "action": "make_loan_payment",
                "requires_confirmation": True,
                "parsed_data": data,
                "response": response,
                "session_id": str(user_id),
            }

        except Exception as e:
            logger.error(f"Error handling loan payment: {e}", exc_info=True)
            response = "I had trouble processing your loan payment. Please try again."
            session.add_message("assistant", response)
            return {
                "intent": Intent.MAKE_LOAN_PAYMENT,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": data,
                "response": response,
                "session_id": str(user_id),
            }

    def _handle_add_loan(
        self,
        user_id: UUID,
        session: ChatSession,
        parsed: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle add new loan intent."""
        data = parsed.get("data", {})
        amount = data.get("amount", "?")

        response = (
            f"To add a new loan of **${amount}**, I need a few more details:\n\n"
            f"• What's the loan name/purpose? (e.g., 'Car Loan', 'Student Loan')\n\n"
            f"Please provide the loan name."
        )

        session.set_pending_action(
            {
                "type": "add_loan_awaiting_name",
                "data": {
                    "user_id": str(user_id),
                    "amount": str(amount),
                },
            }
        )

        session.add_message("assistant", response)
        return {
            "intent": Intent.ADD_LOAN,
            "action": None,
            "requires_confirmation": False,
            "parsed_data": data,
            "response": response,
            "session_id": str(user_id),
        }

    def _handle_check_loan(
        self,
        user_id: UUID,
        session: ChatSession,
    ) -> Dict[str, Any]:
        """Handle check loan status intent."""
        try:
            from app.models.loan import Loan

            loans = Loan.query.filter_by(user_id=user_id).all()

            if not loans:
                response = (
                    "You don't have any loans recorded. Would you like to add one?"
                )
            else:
                open_loans = [loan for loan in loans if loan.status.value == "open"]
                closed_loans = [loan for loan in loans if loan.status.value == "closed"]

                total_remaining = sum(
                    float(loan.remaining_amount) for loan in open_loans
                )

                response = "**Your Loans:**\n\n"

                if open_loans:
                    response += "📋 **Open Loans:**\n"
                    for loan in open_loans:
                        progress = (
                            1
                            - float(loan.remaining_amount) / float(loan.original_amount)
                        ) * 100
                        response += f"• {loan.name}: ${loan.remaining_amount} remaining ({progress:.0f}% paid)\n"
                    response += f"\n**Total debt:** ${total_remaining:.2f}\n"

                if closed_loans:
                    response += f"\n✅ **Paid Off:** {len(closed_loans)} loan(s)\n"

            session.add_message("assistant", response)
            return {
                "intent": Intent.CHECK_LOAN,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": None,
                "response": response,
                "session_id": str(user_id),
            }

        except Exception as e:
            logger.error(f"Error checking loans: {e}", exc_info=True)
            response = "I had trouble fetching your loans. Please try again."
            session.add_message("assistant", response)
            return {
                "intent": Intent.CHECK_LOAN,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": None,
                "response": response,
                "session_id": str(user_id),
            }

    def _handle_savings_goal(
        self,
        user_id: UUID,
        session: ChatSession,
        parsed: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle savings goal intent (future feature)."""
        data = parsed.get("data", {})
        amount = data.get("amount", "?")

        response = (
            f"🚧 **Savings Goals Coming Soon!**\n\n"
            f"We're working on savings goal tracking. In the meantime, you can:\n\n"
            f"• Record transfers to your savings account as transactions\n"
            f"• Set a budget to limit spending and increase savings\n\n"
            f"Would you like to record a ${amount} savings transfer as a transaction?"
        )

        session.set_pending_action(
            {
                "type": "savings_fallback",
                "data": {
                    "amount": str(amount),
                    "description": "Savings Transfer",
                    "category_name": "Financial Services",
                },
            }
        )

        session.add_message("assistant", response)
        return {
            "intent": Intent.SAVINGS_GOAL,
            "action": None,
            "requires_confirmation": False,
            "parsed_data": data,
            "response": response,
            "session_id": str(user_id),
        }

    def _handle_general_chat(
        self,
        session: ChatSession,
        message: str,
    ) -> Dict[str, Any]:
        """Handle general chat messages."""
        if self.gemini and self.gemini.is_initialized:
            response = self.gemini.chat(message, session.get_context())
        else:
            response = (
                "I'm your finance assistant. I can help you add transactions, "
                "check spending, and manage budgets. Type 'help' for more info!"
            )

        session.add_message("assistant", response)
        return {
            "intent": Intent.GENERAL_CHAT,
            "action": None,
            "requires_confirmation": False,
            "parsed_data": None,
            "response": response,
            "session_id": str(session.user_id),
        }

    def _execute_pending_action(
        self,
        user_id: UUID,
        session: ChatSession,
    ) -> Dict[str, Any]:
        """Execute a confirmed pending action."""
        action = session.pending_action
        if not action:
            response = "No pending action to confirm."
            session.add_message("assistant", response)
            return {
                "intent": Intent.CONFIRM_ACTION,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": None,
                "response": response,
                "session_id": str(session.session_id),
            }

        action_type = action.get("type")

        try:
            if action_type == "create_transaction":
                return self._execute_create_transaction(user_id, session, action)
            elif action_type == "delete_transaction":
                return self._execute_delete_transaction(user_id, session, action)
            elif action_type == "edit_transaction":
                return self._execute_edit_transaction(user_id, session, action)
            elif action_type == "set_budget":
                return self._execute_set_budget(user_id, session, action)
            elif action_type == "make_loan_payment":
                return self._execute_loan_payment(user_id, session, action)
            elif action_type == "savings_fallback":
                # Treat as regular transaction
                action["type"] = "create_transaction"
                action["data"]["transaction_type"] = "expense"
                return self._execute_create_transaction(user_id, session, action)
            else:
                response = f"Unknown action type: {action_type}"

        except Exception as e:
            logger.error(f"Failed to execute action: {e}", exc_info=True)
            response = f"Sorry, I couldn't complete that action: {str(e)}"

        session.clear_pending_action()
        session.add_message("assistant", response)
        return {
            "intent": Intent.CONFIRM_ACTION,
            "action": None,
            "requires_confirmation": False,
            "parsed_data": None,
            "response": response,
            "session_id": str(session.session_id),
        }

    def _execute_create_transaction(
        self,
        user_id: UUID,
        session: ChatSession,
        action: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute create transaction action."""
        from app.services.transaction_service import TransactionService
        from app.models.user import User
        from app.core.extensions import db

        data = action.get("data", {})

        # Get user
        user = db.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")

        # Prepare transaction data
        tx_data = {
            "amount": data.get("amount"),
            "transaction_type": data.get("transaction_type", "expense"),
            "date": data.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
            "merchant_name": data.get("merchant_name"),
            "category_id": data.get("category_id"),
        }

        # Create transaction
        transaction = TransactionService.create_transaction(user, tx_data)

        session.clear_pending_action()

        # Build success message - prefer description over merchant for display
        description = data.get("description")
        merchant = transaction.merchant_name or "Unknown"
        if description:
            item_text = f"for **{description}**"
        else:
            item_text = f"at {merchant}"

        response = (
            f"✅ Done! Added **${transaction.amount}** {transaction.transaction_type.value} "
            f"{item_text}."
        )
        session.add_message("assistant", response)

        return {
            "intent": Intent.CONFIRM_ACTION,
            "action": "created",
            "requires_confirmation": False,
            "parsed_data": {"transaction_id": str(transaction.id)},
            "response": response,
            "session_id": str(session.session_id),
        }

    def _execute_delete_transaction(
        self,
        user_id: UUID,
        session: ChatSession,
        action: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute delete transaction action."""
        from app.services.transaction_service import TransactionService

        transaction_id = action.get("transaction_id")

        TransactionService.delete_transaction(user_id, UUID(transaction_id))

        session.clear_pending_action()

        response = "✅ Transaction deleted successfully."
        session.add_message("assistant", response)

        return {
            "intent": Intent.CONFIRM_ACTION,
            "action": "deleted",
            "requires_confirmation": False,
            "parsed_data": {"transaction_id": transaction_id},
            "response": response,
            "session_id": str(session.session_id),
        }

    def _execute_edit_transaction(
        self,
        user_id: UUID,
        session: ChatSession,
        action: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute edit transaction action."""
        # TODO: Implement edit logic
        session.clear_pending_action()
        response = "Transaction editing is not yet implemented."
        session.add_message("assistant", response)

        return {
            "intent": Intent.CONFIRM_ACTION,
            "action": None,
            "requires_confirmation": False,
            "parsed_data": None,
            "response": response,
            "session_id": str(session.session_id),
        }

    def _execute_set_budget(
        self,
        user_id: UUID,
        session: ChatSession,
        action: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute set/increase budget action."""
        from app.models.budget import Budget
        from app.models.enums import BudgetType, BudgetPeriod
        from app.core.extensions import db

        data = action.get("data", {})

        try:
            category_id = data.get("category_id")
            amount = Decimal(data.get("amount", "0"))
            period = BudgetPeriod(data.get("period", "monthly"))

            # Check for existing budget
            existing = Budget.query.filter_by(
                user_id=user_id,
                category_id=category_id,
            ).first()

            if existing:
                # Update existing budget
                existing.amount = amount
                existing.updated_at = datetime.now(timezone.utc)
                db.session.commit()
                action_text = "updated"
            else:
                # Create new budget
                new_budget = Budget(
                    user_id=user_id,
                    category_id=category_id,
                    budget_type=BudgetType.CATEGORY,
                    amount=amount,
                    period=period,
                )
                db.session.add(new_budget)
                db.session.commit()
                action_text = "set"

            session.clear_pending_action()

            category_name = data.get("category_name", "Unknown")
            response = f"✅ Done! {category_name} budget {action_text} to **${amount}** ({period.value})."
            session.add_message("assistant", response)

            return {
                "intent": Intent.CONFIRM_ACTION,
                "action": "budget_updated",
                "requires_confirmation": False,
                "parsed_data": {"amount": str(amount), "category": category_name},
                "response": response,
                "session_id": str(session.session_id),
            }

        except Exception as e:
            logger.error(f"Failed to set budget: {e}", exc_info=True)
            session.clear_pending_action()
            response = f"Sorry, I couldn't update the budget: {str(e)}"
            session.add_message("assistant", response)
            return {
                "intent": Intent.CONFIRM_ACTION,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": None,
                "response": response,
                "session_id": str(session.session_id),
            }

    def _execute_loan_payment(
        self,
        user_id: UUID,
        session: ChatSession,
        action: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute loan payment action.

        This does TWO things:
        1. Creates an expense transaction for the payment
        2. Reduces the loan's remaining balance
        """
        from app.models.loan import Loan
        from app.models.enums import LoanStatus
        from app.services.transaction_service import TransactionService
        from app.models.user import User
        from app.core.extensions import db

        data = action.get("data", {})

        try:
            loan_id = data.get("loan_id")
            amount = Decimal(data.get("amount", "0"))
            create_tx = data.get("create_transaction", True)

            # Get loan
            loan = db.session.get(Loan, loan_id)
            if not loan:
                raise ValueError("Loan not found")

            # Get user
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError("User not found")

            # Update loan balance
            old_balance = loan.remaining_amount
            new_balance = max(Decimal("0"), loan.remaining_amount - amount)
            loan.remaining_amount = new_balance
            loan.updated_at = datetime.now(timezone.utc)

            # Check if loan is paid off
            if new_balance == 0:
                loan.status = LoanStatus.CLOSED
                paid_off_text = " 🎉 **Loan fully paid off!**"
            else:
                paid_off_text = ""

            # Create expense transaction if requested
            tx_id = None
            if create_tx:
                tx_data = {
                    "amount": str(amount),
                    "transaction_type": "expense",
                    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "merchant_name": f"Loan Payment - {loan.name}",
                    "category_id": data.get("category_id"),
                }
                transaction = TransactionService.create_transaction(user, tx_data)
                tx_id = str(transaction.id)

            db.session.commit()
            session.clear_pending_action()

            response = (
                f"✅ Done! Recorded **${amount}** payment for '{loan.name}'.\n\n"
                f"• Loan balance: ${old_balance} → ${new_balance}\n"
                f"• Expense transaction created{paid_off_text}"
            )
            session.add_message("assistant", response)

            return {
                "intent": Intent.CONFIRM_ACTION,
                "action": "loan_payment",
                "requires_confirmation": False,
                "parsed_data": {
                    "loan_id": loan_id,
                    "amount": str(amount),
                    "transaction_id": tx_id,
                    "new_balance": str(new_balance),
                },
                "response": response,
                "session_id": str(session.session_id),
            }

        except Exception as e:
            logger.error(f"Failed to process loan payment: {e}", exc_info=True)
            session.clear_pending_action()
            response = f"Sorry, I couldn't process the loan payment: {str(e)}"
            session.add_message("assistant", response)
            return {
                "intent": Intent.CONFIRM_ACTION,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": None,
                "response": response,
                "session_id": str(session.session_id),
            }

    def request_category_clarification(
        self,
        user_id: UUID,
        transaction_id: UUID,
        alternatives: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Request category clarification from user.

        Called when AI confidence is low and user input is needed.

        Args:
            user_id: User's UUID
            transaction_id: Transaction needing clarification
            alternatives: List of category alternatives

        Returns:
            Chat response asking for clarification
        """
        session = self._get_session(user_id)

        # Set pending clarification
        session.set_pending_action(
            {
                "type": "clarify_category",
                "transaction_id": str(transaction_id),
                "alternatives": alternatives,
            }
        )

        # Build options
        options = "\n".join([f"- {a['category']}" for a in alternatives[:5]])

        response = (
            "I'm not sure how to categorize a recent transaction. "
            "Could you help me?\n\n"
            f"**Possible categories:**\n{options}\n\n"
            "Just tell me which one fits best!"
        )

        session.add_message("assistant", response)

        return {
            "intent": Intent.CLARIFY_CATEGORY,
            "action": None,
            "requires_confirmation": False,
            "parsed_data": {"transaction_id": str(transaction_id)},
            "response": response,
            "session_id": str(session.session_id),
            "alternatives": alternatives,
            "needs_clarification": True,
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_chat_handler: Optional[ChatHandler] = None


def get_chat_handler() -> ChatHandler:
    """
    Get the singleton ChatHandler instance.

    Returns:
        ChatHandler instance (creates if not exists)
    """
    global _chat_handler
    if _chat_handler is None:
        _chat_handler = ChatHandler()
    return _chat_handler


def initialize_chat() -> bool:
    """
    Initialize the chat handler.

    Should be called at application startup.

    Returns:
        True if successful
    """
    handler = get_chat_handler()
    return handler.initialize()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "ChatHandler",
    "ChatSession",
    "Intent",
    "get_chat_handler",
    "initialize_chat",
]
