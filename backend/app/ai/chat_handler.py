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

    def __init__(self, user_id: UUID, db_session=None):
        self.user_id = user_id
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

    def _get_session(self, user_id: UUID) -> ChatSession:
        """Get or create a session for a user."""
        # Clean expired sessions
        self._cleanup_sessions()

        if user_id not in self._sessions:
            self._sessions[user_id] = ChatSession(user_id)
        else:
            # Refresh db session for cached ChatSession to avoid detached instance errors
            self._sessions[user_id]._load_from_db()

        return self._sessions[user_id]

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
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a user message and return response.

        Args:
            user_id: User's UUID
            message: User's message text
            context: Optional additional context
            session_id: Optional session ID (currently unused, for future use)

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

        session = self._get_session(user_id)
        session.add_message("user", message)

        # Normalize message
        message_lower = message.strip().lower()

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
                "set_budget": Intent.BUDGET_STATUS,
                "summarize_transactions": Intent.QUERY_SPENDING,
                "get_insights": Intent.GET_INSIGHTS,
                "help": Intent.HELP,
                "general_chat": Intent.GENERAL_CHAT,
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
                ]:
                    # Extract entities locally using regex - NO GEMINI NEEDED
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
            # "add 100 for X at Y"
            r"add\s+\$?(\d+(?:\.\d{2})?)\s+(?:for\s+)?(.+?)(?:\s+at\s+(.+))?$",
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

        # Budget patterns
        if "budget" in message_lower:
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
        if description and merchant and description.lower() != merchant.lower():
            # Both product and store specified: "bought shoes at Nike Store"
            what_where = f"for **{description}** at {merchant}"
        elif description:
            # Only product: "bought shoes"
            what_where = f"for **{description}**"
        else:
            # Only merchant/location: "at Starbucks"
            what_where = f"at **{merchant}**"

        response = (
            f"I'll add a **${amount}** {tx_type} {what_where} "
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
                    pct = b.get("percentage_used", 0)
                    status = "✅" if pct < 70 else "⚠️" if pct < 100 else "🔴"
                    response += (
                        f"{status} **{b.get('category_name', 'Total')}**: "
                        f"${b.get('spent', 0):.2f} / ${b.get('budget_amount', 0)} "
                        f"({pct:.0f}%)\n"
                    )

            session.add_message("assistant", response)
            return {
                "intent": Intent.BUDGET_STATUS,
                "action": None,
                "requires_confirmation": False,
                "parsed_data": budgets,
                "response": response,
                "session_id": str(user_id),
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
                "session_id": str(user_id),
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
                "session_id": str(user_id),
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
                "session_id": str(user_id),
            }

    def _handle_help(self, session: ChatSession) -> Dict[str, Any]:
        """Handle help request."""
        response = """**I can help you with:**

📝 **Add transactions:**
- "Add $50 for lunch at Subway"
- "Spent $30 on groceries"

🗑️ **Delete transactions:**
- "Delete my last transaction"

💰 **Check spending:**
- "How much did I spend this month?"
- "What's my spending on food?"

📊 **Budget status:**
- "Show my budget status"

💡 **Get insights:**
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
            "session_id": str(session.user_id),
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
                "session_id": str(user_id),
            }

        action_type = action.get("type")

        try:
            if action_type == "create_transaction":
                return self._execute_create_transaction(user_id, session, action)
            elif action_type == "delete_transaction":
                return self._execute_delete_transaction(user_id, session, action)
            elif action_type == "edit_transaction":
                return self._execute_edit_transaction(user_id, session, action)
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
            "session_id": str(user_id),
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
            "session_id": str(user_id),
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
            "session_id": str(user_id),
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
            "session_id": str(user_id),
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
            "session_id": str(user_id),
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
