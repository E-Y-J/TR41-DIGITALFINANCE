# =============================================================================
# Digital Finance Tracker - Category Service
# PURPOSE: Category service layer for business logic operations
# =============================================================================
"""
Category Service Module

AI FOUNDATION - Categorization

This module provides the service layer for Category operations:
- Get all categories (mostly read-only operations)
- Seed default categories
- Find category by name or ID

Categories are pre-defined and seeded at startup. Users cannot create
custom categories in the current implementation.

Usage:
    from app.services.category_service import CategoryService

    # Get all categories
    categories = CategoryService.get_all()

    # Get category by name
    category = CategoryService.get_by_name("Food & Dining")

Design Principles:
    - Stateless class methods for all operations
    - Categories are mostly read-only (seeded at startup)
    - Exception-based error handling for consistency
"""

import logging
from typing import List, Optional
from uuid import UUID

from app.core.extensions import db
from app.models.category import Category, DEFAULT_CATEGORIES
from app.models.enums import CategoryType
from app.utils.errors import NotFoundError


# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# CATEGORY SERVICE CLASS
# =============================================================================


class CategoryService:
    """
    Service class for Category operations.

    All methods are class methods (no instance needed).
    Categories are pre-defined and seeded at application startup.

    The 11 default categories are:
        - Food & Dining (BOTH) - Supports refunds
        - Transportation (BOTH) - Supports refunds
        - Shopping & Retail (BOTH) - Supports refunds
        - Entertainment & Recreation (BOTH) - Supports refunds
        - Healthcare & Medical (BOTH) - Supports reimbursements
        - Utilities & Services (BOTH) - Supports refunds
        - Financial Services (BOTH) - Supports interest income
        - Income (INCOME) - True income only
        - Government & Legal (BOTH) - Supports tax refunds
        - Charity & Donations (EXPENSE) - Donations only
        - Unknown (BOTH) - Used when AI confidence is too low

    Example:
        >>> categories = CategoryService.get_all()
        >>> expense_categories = CategoryService.get_by_type(CategoryType.EXPENSE)
    """

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    @classmethod
    def get_all(cls) -> List[Category]:
        """
        Get all categories ordered by display_order.

        Returns:
            List of all Category instances

        Example:
            >>> categories = CategoryService.get_all()
            >>> for cat in categories:
            ...     print(f"{cat.name}: {cat.description}")
        """
        categories = (
            Category.query.filter(Category.is_active.is_(True))
            .order_by(Category.display_order)
            .all()
        )

        logger.debug(f"Retrieved {len(categories)} active categories")
        return categories

    @classmethod
    def get_by_id(cls, category_id: UUID) -> Category:
        """
        Get category by primary key ID.

        Args:
            category_id: Category's UUID primary key

        Returns:
            Category instance

        Raises:
            NotFoundError: If category not found

        Example:
            >>> category = CategoryService.get_by_id(uuid.UUID("..."))
        """
        category = Category.query.get(category_id)

        if category is None:
            logger.debug(f"Category not found by ID: {category_id}")
            raise NotFoundError("Category not found")

        return category

    @classmethod
    def get_by_name(cls, name: str) -> Optional[Category]:
        """
        Get category by name (case-insensitive).

        Args:
            name: Category name to search for

        Returns:
            Category instance if found, None otherwise

        Example:
            >>> category = CategoryService.get_by_name("Food & Dining")
            >>> if category:
            ...     print(f"Found: {category.name}")
        """
        category = Category.query.filter(
            db.func.lower(Category.name) == name.lower()
        ).first()

        return category

    @classmethod
    def get_by_type(cls, category_type: CategoryType) -> List[Category]:
        """
        Get categories filtered by type.

        Args:
            category_type: CategoryType enum (INCOME, EXPENSE, BOTH)

        Returns:
            List of matching Category instances

        Example:
            >>> expense_cats = CategoryService.get_by_type(CategoryType.EXPENSE)
        """
        # BOTH categories should be included in INCOME and EXPENSE queries
        if category_type in (CategoryType.INCOME, CategoryType.EXPENSE):
            categories = (
                Category.query.filter(
                    Category.is_active.is_(True),
                    db.or_(
                        Category.category_type == category_type,
                        Category.category_type == CategoryType.BOTH,
                    ),
                )
                .order_by(Category.display_order)
                .all()
            )
        else:
            # For BOTH type, return only BOTH categories
            categories = (
                Category.query.filter(
                    Category.is_active.is_(True),
                    Category.category_type == category_type,
                )
                .order_by(Category.display_order)
                .all()
            )

        logger.debug(
            f"Retrieved {len(categories)} categories for type {category_type.value}"
        )
        return categories

    @classmethod
    def get_unknown_category(cls) -> Category:
        """
        Get the 'Unknown' category used when AI confidence is too low.

        Returns:
            The Unknown Category instance

        Raises:
            NotFoundError: If Unknown category doesn't exist (should never happen)

        Note:
            This is used by the AI categorization system when:
            - HuggingFace confidence < 70% AND
            - Gemini fallback also has low confidence (< 50%)
        """
        category = cls.get_by_name("Unknown")

        if category is None:
            logger.error("Unknown category not found - database may not be seeded")
            raise NotFoundError(
                "Unknown category not found. Please run database seeding."
            )

        return category

    # =========================================================================
    # SEED OPERATIONS
    # =========================================================================

    @classmethod
    def seed_defaults(cls) -> int:
        """
        Seed the database with default categories.

        This method is idempotent - it will skip categories that already exist.
        Should be called during application startup or migration.

        Returns:
            Number of new categories created

        Example:
            >>> created_count = CategoryService.seed_defaults()
            >>> print(f"Created {created_count} new categories")
        """
        # Delegate to model method for consistency
        created_count = Category.seed_defaults()

        logger.info(f"Category seeding complete: {created_count} new categories")
        return created_count

    @classmethod
    def ensure_categories_exist(cls) -> bool:
        """
        Ensure all default categories exist in the database.

        Returns:
            True if all categories exist (or were created)

        Note:
            This is a convenience method for startup checks.
        """
        existing_count = Category.query.count()

        if existing_count < len(DEFAULT_CATEGORIES):
            logger.info(
                f"Found {existing_count}/{len(DEFAULT_CATEGORIES)} categories. "
                "Seeding missing ones..."
            )
            cls.seed_defaults()

        return True

    # =========================================================================
    # KEYWORD-BASED CATEGORIZATION (No AI Required)
    # =========================================================================

    @classmethod
    def categorize_by_keyword(
        cls, merchant_name: str
    ) -> tuple[Optional[Category], float]:
        """
        Categorize a transaction based on merchant name keywords.

        This is rule-based categorization that works WITHOUT AI.
        Checks the merchant name against KEYWORD_CATEGORY_MAP.

        HOW IT WORKS:
        1. Lowercase the merchant name
        2. Check each keyword in KEYWORD_CATEGORY_MAP
        3. First matching keyword determines the category
        4. If no match, returns (None, 0.0) -> use Unknown category

        Args:
            merchant_name: Transaction merchant name or description

        Returns:
            Tuple of (Category or None, confidence_score)
            - Category: Matched category, or None if no keyword match
            - confidence: 1.0 for keyword match, 0.0 for no match

        Example:
            >>> category, confidence = CategoryService.categorize_by_keyword("Starbucks Coffee")
            >>> print(f"{category.name}: {confidence}")  # "Food & Dining: 1.0"

            >>> category, confidence = CategoryService.categorize_by_keyword("Random Store XYZ")
            >>> print(category)  # None (no keyword match)

        Note:
            When this returns None, the caller should:
            1. Try AI categorization (future)
            2. Or assign "Unknown" category
        """
        from app.models.category import KEYWORD_CATEGORY_MAP

        if not merchant_name:
            return None, 0.0

        merchant_lower = merchant_name.lower()

        # Check each category's keywords
        for category_name, keywords in KEYWORD_CATEGORY_MAP.items():
            for keyword in keywords:
                if keyword in merchant_lower:
                    # Found a match - get the category from database
                    category = cls.get_by_name(category_name)
                    if category:
                        logger.debug(
                            f"Keyword match: '{keyword}' -> {category_name} "
                            f"for merchant '{merchant_name}'"
                        )
                        return category, 1.0

        # No keyword match
        logger.debug(f"No keyword match for merchant: {merchant_name}")
        return None, 0.0

    @classmethod
    def auto_categorize(
        cls,
        merchant_name: str,
        amount: float = None,
        transaction_type: str = None,
    ) -> tuple[Category, float, str]:
        """
        Auto-categorize a transaction using AI-powered categorization.

        This is the main entry point for auto-categorization.
        Uses the AI Orchestrator which implements tiered fallback:

        CATEGORIZATION FLOW:
        1. Try keyword matching (instant, no API calls)
        2. Try HuggingFace DistilBERT model (local, 80% accuracy)
        3. Try Gemini API fallback (when HuggingFace confidence < 70%)
        4. If all fail or confidence < 50%, return "Unknown" category

        Args:
            merchant_name: Transaction merchant name or description
            amount: Optional transaction amount (helps with context)
            transaction_type: Optional "expense" or "income"

        Returns:
            Tuple of (category, confidence, source)
            - category: The matched Category (never None)
            - confidence: Float 0.0-1.0
            - source: "keyword", "huggingface", "gemini", or "unknown"

        Example:
            >>> category, conf, source = CategoryService.auto_categorize("Shell Gas")
            >>> print(f"{category.name} ({source}): {conf}")
            >>> # "Transportation (keyword): 1.0"

        Notes:
            - Keyword matching returns confidence 1.0 (exact matches)
            - HuggingFace returns model confidence (typically 0.5-0.95)
            - Gemini returns confidence from its assessment
            - Results with alternatives have confidence < 70%
        """
        try:
            # Try AI Orchestrator (handles all tiers)
            from app.ai.orchestrator import get_orchestrator

            orchestrator = get_orchestrator()

            # Get categorization result
            result = orchestrator.categorize(
                merchant_name=merchant_name,
                amount=amount,
                transaction_type=transaction_type,
            )

            # Get the category from the result
            category_id = result.get("category_id")
            confidence = result.get("confidence", 0.0)
            source = result.get("source", "unknown")

            if category_id:
                category = cls.get_by_id(category_id)
                if category:
                    logger.info(
                        f"Auto-categorize '{merchant_name}' -> "
                        f"{category.name} ({source}: {confidence:%})"
                    )
                    return category, confidence, source

            # Fall back to Unknown
            unknown = cls.get_unknown_category()
            return unknown, 0.0, "unknown"

        except Exception as e:
            logger.error(
                f"AI categorization failed for '{merchant_name}': {e}",
                exc_info=True,
            )

            # Fallback: Try keyword matching directly
            category, confidence = cls.categorize_by_keyword(merchant_name)
            if category:
                return category, confidence, "keyword"

            # Final fallback - return Unknown
            unknown = cls.get_unknown_category()
            return unknown, 0.0, "unknown"

    # =========================================================================
    # AI HELPER METHODS
    # =========================================================================

    @classmethod
    def find_category_for_ai_label(cls, ai_label: str) -> Optional[Category]:
        """
        Find a category matching an AI model's predicted label.

        The AI models (HuggingFace, Gemini) return category labels that need
        to be mapped to our Category model. This method handles that mapping.

        Args:
            ai_label: Category label from AI model prediction

        Returns:
            Matching Category instance, or None if no match

        Note:
            This mapping may need adjustments based on actual AI model outputs.
            Current implementation uses case-insensitive name matching.

        Example:
            >>> category = CategoryService.find_category_for_ai_label("Food")
            >>> # Returns "Food & Dining" category
        """
        # First try exact match
        category = cls.get_by_name(ai_label)
        if category:
            return category

        # Try partial match (e.g., "Food" -> "Food & Dining")
        ai_label_lower = ai_label.lower()
        for cat in cls.get_all():
            if ai_label_lower in cat.name.lower():
                return cat

        # No match found - AI service should use Unknown category
        logger.debug(f"No category match for AI label: {ai_label}")
        return None
