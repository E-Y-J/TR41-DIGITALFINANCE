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
        category = db.session.get(Category, category_id)

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

    # =========================================================================
    # CUSTOM CATEGORY CRUD OPERATIONS
    # =========================================================================

    @classmethod
    def get_for_user(cls, user_id: UUID) -> List[Category]:
        """
        Get all categories available to a user (system + custom).

        Args:
            user_id: User's UUID

        Returns:
            List of Category instances (system first, then custom)

        Example:
            >>> categories = CategoryService.get_for_user(user_id)
        """
        return Category.get_for_user(user_id)

    @classmethod
    def get_user_custom_categories(cls, user_id: UUID) -> List[Category]:
        """
        Get only user's custom categories.

        Args:
            user_id: User's UUID

        Returns:
            List of user's custom Category instances
        """
        return Category.get_user_custom_categories(user_id)

    @classmethod
    def create_custom_category(
        cls,
        user_id: UUID,
        name: str,
        description: Optional[str] = None,
        category_type: CategoryType = CategoryType.EXPENSE,
        icon: Optional[str] = None,
        color: Optional[str] = None,
    ) -> Category:
        """
        Create a custom category for a user.

        Args:
            user_id: User's UUID (owner)
            name: Category name (must be unique for user)
            description: Optional category description
            category_type: income, expense, or both (default: expense)
            icon: Optional icon name for frontend
            color: Optional hex color code (e.g., #FF6B6B)

        Returns:
            Created Category instance

        Raises:
            ValidationError: If category name already exists for user
            ValidationError: If trying to use a system category name

        Example:
            >>> category = CategoryService.create_custom_category(
            ...     user_id, "Pet Expenses", "Pet food, vet visits, etc."
            ... )
        """
        from app.utils.errors import ValidationError, ConflictError

        # Validate name
        name = name.strip()
        if not name or len(name) < 2:
            raise ValidationError("Category name must be at least 2 characters")

        if len(name) > 100:
            raise ValidationError("Category name must be 100 characters or less")

        # Check if name conflicts with system category
        system_cat = Category.query.filter(
            db.func.lower(Category.name) == name.lower(),
            Category.is_system == True,
        ).first()

        if system_cat:
            raise ConflictError(
                f"Cannot create category '{name}' - a system category with this name exists"
            )

        # Check if user already has a category with this name
        existing = Category.query.filter(
            db.func.lower(Category.name) == name.lower(),
            Category.user_id == user_id,
        ).first()

        if existing:
            raise ConflictError(f"You already have a category named '{name}'")

        # Get max display_order for user's categories
        max_order = (
            db.session.query(db.func.max(Category.display_order))
            .filter(Category.user_id == user_id)
            .scalar()
        ) or 100  # Start custom categories at 100+

        # Create the category
        category = Category(
            name=name,
            description=description,
            category_type=category_type,
            icon=icon,
            color=color,
            is_system=False,
            user_id=user_id,
            display_order=max_order + 1,
        )

        db.session.add(category)
        db.session.commit()

        logger.info(f"Created custom category '{name}' for user {user_id}")
        return category

    @classmethod
    def update_custom_category(
        cls,
        category_id: UUID,
        user_id: UUID,
        **updates,
    ) -> Category:
        """
        Update a user's custom category.

        Args:
            category_id: Category's UUID
            user_id: User's UUID (must be owner)
            **updates: Fields to update (name, description, category_type, icon, color)

        Returns:
            Updated Category instance

        Raises:
            NotFoundError: If category not found
            ValidationError: If trying to update a system category
            ValidationError: If new name conflicts with existing

        Example:
            >>> updated = CategoryService.update_custom_category(
            ...     category_id, user_id, name="Pet Care", color="#FF6B6B"
            ... )
        """
        from app.utils.errors import ValidationError, ConflictError

        # Get the category
        category = db.session.get(Category, category_id)

        if not category:
            raise NotFoundError("Category not found")

        # Verify ownership
        if category.is_system:
            raise ValidationError("Cannot modify system categories")

        if category.user_id != user_id:
            raise NotFoundError("Category not found")  # Hide existence from other users

        # Handle name update with conflict check
        if "name" in updates and updates["name"]:
            new_name = updates["name"].strip()

            if new_name.lower() != category.name.lower():
                # Check for conflicts
                conflict = Category.query.filter(
                    db.func.lower(Category.name) == new_name.lower(),
                    db.or_(
                        Category.is_system == True,
                        Category.user_id == user_id,
                    ),
                    Category.id != category_id,
                ).first()

                if conflict:
                    raise ConflictError(f"Category name '{new_name}' already exists")

                category.name = new_name

        # Update other fields
        if "description" in updates:
            category.description = updates["description"]

        if "category_type" in updates and updates["category_type"]:
            category.category_type = updates["category_type"]

        if "icon" in updates:
            category.icon = updates["icon"]

        if "color" in updates:
            category.color = updates["color"]

        db.session.commit()

        logger.info(f"Updated custom category {category_id} for user {user_id}")
        return category

    @classmethod
    def delete_custom_category(
        cls,
        category_id: UUID,
        user_id: UUID,
        reassign_to: Optional[UUID] = None,
    ) -> bool:
        """
        Delete a user's custom category.

        Args:
            category_id: Category's UUID
            user_id: User's UUID (must be owner)
            reassign_to: Optional category ID to reassign transactions to

        Returns:
            True if deleted successfully

        Raises:
            NotFoundError: If category not found
            ValidationError: If trying to delete a system category
            ValidationError: If category has transactions and no reassign target

        Example:
            >>> CategoryService.delete_custom_category(category_id, user_id)
        """
        from app.utils.errors import ValidationError
        from app.models.transaction import Transaction

        # Get the category
        category = db.session.get(Category, category_id)

        if not category:
            raise NotFoundError("Category not found")

        # Verify ownership
        if category.is_system:
            raise ValidationError("Cannot delete system categories")

        if category.user_id != user_id:
            raise NotFoundError("Category not found")

        # Check for associated transactions
        transaction_count = Transaction.query.filter(
            Transaction.category_id == category_id
        ).count()

        if transaction_count > 0:
            if reassign_to:
                # Validate reassign target
                target = db.session.get(Category, reassign_to)
                if not target:
                    raise ValidationError("Reassign target category not found")

                # Must be accessible to user
                if not target.is_system and target.user_id != user_id:
                    raise ValidationError("Invalid reassign target")

                # Reassign transactions
                Transaction.query.filter(Transaction.category_id == category_id).update(
                    {"category_id": reassign_to}
                )

                logger.info(
                    f"Reassigned {transaction_count} transactions from "
                    f"{category_id} to {reassign_to}"
                )
            else:
                # Default: reassign to Unknown
                unknown = cls.get_unknown_category()
                Transaction.query.filter(Transaction.category_id == category_id).update(
                    {"category_id": unknown.id}
                )

                logger.info(
                    f"Reassigned {transaction_count} transactions from "
                    f"{category_id} to Unknown"
                )

        # Soft delete (mark inactive) or hard delete
        # Using soft delete to preserve data integrity
        category.is_active = False
        db.session.commit()

        logger.info(f"Deleted custom category {category_id} for user {user_id}")
        return True
