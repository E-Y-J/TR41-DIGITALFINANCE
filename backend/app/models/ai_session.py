# =============================================================================
# Digital Finance Tracker - AI Session Models
# PURPOSE: Database models for AI session management (replaces in-memory storage)
# =============================================================================
"""
AI Session Models Module

This module defines database models for AI session management:
- AISession: Stores chat conversation state per user
- PendingAction: Stores actions awaiting user confirmation
- UserLearning: Stores user corrections for personalized categorization

These tables replace in-memory storage to prevent data loss on restart.

Database Tables:
    - ai_sessions: User chat sessions with conversation history
    - pending_actions: Actions requiring user confirmation
    - user_learnings: Merchant → category mappings learned from user

Usage:
    from app.models.ai_session import AISession, PendingAction, UserLearning

    # Get or create session
    session = AISession.get_or_create(user_id)

    # Record user learning
    UserLearning.record(user_id, "Starbucks", "Food & Dining")

Notes:
    - Sessions expire after 30 minutes of inactivity
    - Pending actions expire after 24 hours
    - User learnings persist indefinitely
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

from sqlalchemy import String, DateTime, Boolean, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.extensions import db

# =============================================================================
# AI SESSION MODEL
# =============================================================================


class AISession(db.Model):
    """
    Stores chat session state for a user.

    Maintains conversation history and pending actions for multi-turn
    chat interactions. Replaces in-memory ChatSession class.

    Attributes:
        id: Primary key UUID
        user_id: Foreign key to users table
        conversation_history: JSON array of message objects
        last_intent: Last detected intent type
        is_active: Whether session is currently active
        created_at: Session creation timestamp
        updated_at: Last activity timestamp
        expires_at: Session expiration timestamp

    Example:
        >>> session = AISession.get_or_create(user_id)
        >>> session.add_message("user", "Add $50 for lunch")
        >>> db.session.commit()
    """

    __tablename__ = "ai_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    conversation_history: Mapped[Dict] = mapped_column(
        JSONB, nullable=False, default=list
    )
    last_intent: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(minutes=30),
    )

    # Relationship
    user = relationship("User", backref="ai_sessions")

    # Indexes
    __table_args__ = (
        Index("idx_ai_sessions_user_active", "user_id", "is_active"),
        Index("idx_ai_sessions_expires", "expires_at"),
    )

    @classmethod
    def get_or_create(cls, user_id: uuid.UUID) -> "AISession":
        """
        Get active session for user or create new one.

        Args:
            user_id: User's UUID

        Returns:
            Active AISession instance
        """
        # Look for active, non-expired session
        session = cls.query.filter(
            cls.user_id == user_id,
            cls.is_active == True,
            cls.expires_at > datetime.now(timezone.utc),
        ).first()

        if session:
            # Refresh expiration
            session.expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
            session.updated_at = datetime.now(timezone.utc)
            return session

        # Create new session
        session = cls(
            user_id=user_id,
            conversation_history=[],
        )
        db.session.add(session)
        return session

    @classmethod
    def resume(
        cls, session_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional["AISession"]:
        """
        Resume a specific session by ID, reactivating it if expired.

        Args:
            session_id: Session UUID to resume
            user_id: User's UUID (for ownership validation)

        Returns:
            AISession instance if found and owned by user, None otherwise
        """
        session = cls.query.filter(
            cls.id == session_id,
            cls.user_id == user_id,
        ).first()

        if session:
            # Reactivate and refresh expiration
            session.is_active = True
            session.expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
            session.updated_at = datetime.now(timezone.utc)
            return session

        return None

    def add_message(self, role: str, content: str) -> None:
        """
        Add message to conversation history.

        Args:
            role: 'user' or 'assistant'
            content: Message text
        """
        history = list(self.conversation_history or [])
        history.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        # Keep last 20 messages
        if len(history) > 20:
            history = history[-20:]
        self.conversation_history = history
        self.updated_at = datetime.now(timezone.utc)
        self.expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

    def clear(self) -> None:
        """Clear conversation history and mark inactive."""
        self.conversation_history = []
        self.last_intent = None
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "conversation_history": self.conversation_history,
            "last_intent": self.last_intent,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }

    @classmethod
    def get_all_for_user(
        cls,
        user_id: uuid.UUID,
        include_inactive: bool = False,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple:
        """
        Get all chat sessions for a user with pagination.

        Args:
            user_id: User's UUID
            include_inactive: Whether to include expired/inactive sessions
            page: Page number (1-indexed)
            per_page: Number of sessions per page

        Returns:
            Tuple of (sessions list, total count, has_more)
        """
        query = cls.query.filter(cls.user_id == user_id)

        if not include_inactive:
            query = query.filter(cls.is_active == True)

        # Order by most recent first
        query = query.order_by(cls.updated_at.desc())

        # Get total count
        total = query.count()

        # Apply pagination
        sessions = query.offset((page - 1) * per_page).limit(per_page).all()

        has_more = (page * per_page) < total

        return sessions, total, has_more

    @classmethod
    def cleanup_expired(cls) -> int:
        """
        Mark expired sessions as inactive.

        Returns:
            Number of sessions cleaned up
        """
        count = cls.query.filter(
            cls.is_active == True,
            cls.expires_at < datetime.now(timezone.utc),
        ).update({"is_active": False})
        db.session.commit()
        return count


# =============================================================================
# PENDING ACTION MODEL
# =============================================================================


class PendingAction(db.Model):
    """
    Stores actions awaiting user confirmation.

    When AI parses a command like "Add $50 for lunch", the action is
    stored here until user confirms. Replaces in-memory pending_action.

    Attributes:
        id: Primary key UUID
        user_id: Foreign key to users table
        session_id: Foreign key to ai_sessions table
        action_type: Type of action (create_transaction, etc.)
        action_data: JSON with parsed action parameters
        status: pending, confirmed, cancelled, expired
        created_at: When action was created
        expires_at: When action expires (24 hours)

    Example:
        >>> action = PendingAction.create(
        ...     user_id=user_id,
        ...     action_type="create_transaction",
        ...     action_data={"amount": 50, "merchant": "Subway"}
        ... )
    """

    __tablename__ = "pending_actions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action_data: Mapped[Dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(hours=24),
    )

    # Relationships
    user = relationship("User", backref="pending_actions")
    session = relationship("AISession", backref="pending_actions")

    # Indexes
    __table_args__ = (
        Index("idx_pending_actions_user_status", "user_id", "status"),
        Index("idx_pending_actions_expires", "expires_at"),
    )

    @classmethod
    def create(
        cls,
        user_id: uuid.UUID,
        action_type: str,
        action_data: Dict[str, Any],
        session_id: Optional[uuid.UUID] = None,
    ) -> "PendingAction":
        """
        Create a new pending action.

        Args:
            user_id: User's UUID
            action_type: Type of action
            action_data: Action parameters
            session_id: Optional session ID

        Returns:
            New PendingAction instance
        """
        action = cls(
            user_id=user_id,
            session_id=session_id,
            action_type=action_type,
            action_data=action_data,
        )
        db.session.add(action)
        return action

    @classmethod
    def get_pending_for_user(cls, user_id: uuid.UUID) -> Optional["PendingAction"]:
        """
        Get the most recent pending action for a user.

        Args:
            user_id: User's UUID

        Returns:
            PendingAction or None
        """
        return (
            cls.query.filter(
                cls.user_id == user_id,
                cls.status == "pending",
                cls.expires_at > datetime.now(timezone.utc),
            )
            .order_by(cls.created_at.desc())
            .first()
        )

    def confirm(self) -> None:
        """Mark action as confirmed."""
        self.status = "confirmed"

    def cancel(self) -> None:
        """Mark action as cancelled."""
        self.status = "cancelled"

    def is_expired(self) -> bool:
        """Check if action has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "action_type": self.action_type,
            "action_data": self.action_data,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }

    @classmethod
    def cleanup_expired(cls) -> int:
        """
        Mark expired actions as expired status.

        Returns:
            Number of actions cleaned up
        """
        count = cls.query.filter(
            cls.status == "pending",
            cls.expires_at < datetime.now(timezone.utc),
        ).update({"status": "expired"})
        db.session.commit()
        return count


# =============================================================================
# USER LEARNING MODEL
# =============================================================================


class UserLearning(db.Model):
    """
    Stores user corrections for personalized categorization.

    When a user corrects an AI-assigned category, we store the mapping
    so future transactions from that merchant use the learned category.

    Attributes:
        id: Primary key UUID
        user_id: Foreign key to users table
        merchant_normalized: Normalized merchant name (lowercase, trimmed)
        category_name: Category user selected
        correction_count: How many times user selected this
        original_category: What AI originally predicted
        created_at: First correction timestamp
        updated_at: Most recent correction timestamp

    Example:
        >>> UserLearning.record(user_id, "starbucks", "Food & Dining")
        >>> category = UserLearning.get_learned(user_id, "starbucks")
        >>> print(category)  # "Food & Dining"
    """

    __tablename__ = "user_learnings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    merchant_normalized: Mapped[str] = mapped_column(String(255), nullable=False)
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    correction_count: Mapped[int] = mapped_column(Integer, default=1)
    original_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship
    user = relationship("User", backref="user_learnings")

    # Indexes and constraints
    __table_args__ = (
        Index(
            "idx_user_learnings_lookup",
            "user_id",
            "merchant_normalized",
            unique=True,
        ),
    )

    @classmethod
    def normalize_merchant(cls, merchant_name: str) -> str:
        """
        Normalize merchant name for consistent matching.

        Args:
            merchant_name: Raw merchant name

        Returns:
            Normalized lowercase string
        """
        import re

        # Lowercase, strip, remove special chars
        normalized = merchant_name.lower().strip()
        normalized = re.sub(r"[#\d]+$", "", normalized)  # Remove trailing numbers
        normalized = re.sub(r"\s+", " ", normalized)  # Normalize whitespace
        return normalized.strip()

    @classmethod
    def record(
        cls,
        user_id: uuid.UUID,
        merchant_name: str,
        category_name: str,
        original_category: Optional[str] = None,
    ) -> "UserLearning":
        """
        Record a user's category correction.

        If mapping exists, increments count. Otherwise creates new.

        Args:
            user_id: User's UUID
            merchant_name: Merchant name (will be normalized)
            category_name: Category user selected
            original_category: What AI predicted (for analysis)

        Returns:
            UserLearning instance
        """
        normalized = cls.normalize_merchant(merchant_name)

        existing = cls.query.filter(
            cls.user_id == user_id,
            cls.merchant_normalized == normalized,
        ).first()

        if existing:
            existing.category_name = category_name
            existing.correction_count += 1
            existing.updated_at = datetime.now(timezone.utc)
            return existing

        learning = cls(
            user_id=user_id,
            merchant_normalized=normalized,
            category_name=category_name,
            original_category=original_category,
        )
        db.session.add(learning)
        return learning

    @classmethod
    def get_learned(cls, user_id: uuid.UUID, merchant_name: str) -> Optional[str]:
        """
        Get learned category for a merchant.

        Args:
            user_id: User's UUID
            merchant_name: Merchant name

        Returns:
            Category name or None if not learned
        """
        normalized = cls.normalize_merchant(merchant_name)

        learning = cls.query.filter(
            cls.user_id == user_id,
            cls.merchant_normalized == normalized,
        ).first()

        return learning.category_name if learning else None

    @classmethod
    def get_all_for_user(cls, user_id: uuid.UUID) -> List["UserLearning"]:
        """
        Get all learned mappings for a user.

        Args:
            user_id: User's UUID

        Returns:
            List of UserLearning instances
        """
        return cls.query.filter(cls.user_id == user_id).all()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "merchant": self.merchant_normalized,
            "category": self.category_name,
            "correction_count": self.correction_count,
            "original_category": self.original_category,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
