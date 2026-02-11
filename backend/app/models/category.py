# =============================================================================
# Digital Finance Tracker - Category Model
# PURPOSE: Category database model for transaction categorization
# =============================================================================
"""
Category Model Module

This module defines the Category model for the local database:
- Stores transaction categories for AI categorization
- Provides 11 default categories (10 main + Unknown)
- Supports frontend dropdown population

Database Table: categories
Primary Key: id (UUID)

AI Foundation:
    Created to support AI categorization feature. Categories are seeded
    on first migration and used by:
    - AI to classify transactions automatically
    - Frontend to display category dropdowns
    - Summary endpoints for grouping

Relationship:
    - One Category can have many Transactions (1:N)

Usage:
    from app.models import Category

    # Get all categories
    categories = Category.query.all()

    # Get category by name
    food = Category.query.filter_by(name="Food & Dining").first()

    # Get expense categories only
    expense_cats = Category.query.filter_by(category_type=CategoryType.EXPENSE).all()

Notes:
    - 11 default categories are seeded via migration
    - is_system=True categories cannot be deleted
    - display_order controls frontend dropdown order
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Text, Integer, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.extensions import db
from app.models.enums import CategoryType

if TYPE_CHECKING:
    from app.models.transaction import Transaction
    from app.models.budget import Budget


# =============================================================================
# KEYWORD MAPPINGS FOR RULE-BASED CATEGORIZATION
# =============================================================================
# Auto-categorization without AI (Rule-Based)
#
# Maps merchant keywords to category names. Used by CategoryService to
# auto-assign categories when creating transactions.
#
# HOW IT WORKS:
# 1. When a transaction is created, we check merchant_name against these keywords
# 2. First matching keyword determines the category
# 3. If no match, transaction gets "Unknown" category
#
# FUTURE: AI will handle unknown cases; this handles the common/obvious ones
#
# TO ADD NEW KEYWORDS:
# Add lowercase keywords to the appropriate category list below.

KEYWORD_CATEGORY_MAP = {
    "Food & Dining": [
        # Fast food & restaurants
        "mcdonald",
        "burger king",
        "wendy",
        "taco bell",
        "chipotle",
        "subway",
        "starbucks",
        "dunkin",
        "pizza hut",
        "domino",
        "papa john",
        "kfc",
        "chick-fil-a",
        "panera",
        "applebee",
        "olive garden",
        "denny",
        "ihop",
        "waffle house",
        "five guys",
        "shake shack",
        "in-n-out",
        # Coffee shops
        "coffee",
        "cafe",
        "bakery",
        "donut",
        # Grocery
        "grocery",
        "safeway",
        "kroger",
        "walmart grocery",
        "target grocery",
        "whole foods",
        "trader joe",
        "aldi",
        "costco",
        "sam's club",
        "publix",
        "wegmans",
        "food lion",
        "piggly wiggly",
        # Delivery
        "doordash",
        "uber eats",
        "grubhub",
        "postmates",
        "instacart",
        "seamless",
        "caviar",
        # General
        "restaurant",
        "diner",
        "eatery",
        "grill",
        "steakhouse",
        "sushi",
        "thai",
        "chinese",
        "mexican",
        "italian",
        "indian",
    ],
    "Transportation": [
        # Rideshare
        "uber",
        "lyft",
        "taxi",
        "cab",
        # Gas stations
        "shell",
        "chevron",
        "exxon",
        "mobil",
        "bp ",
        "texaco",
        "arco",
        "speedway",
        "circle k",
        "wawa",
        "sheetz",
        "quicktrip",
        "racetrac",
        "gas",
        "fuel",
        "petro",
        # Public transit
        "metro",
        "subway",
        "bus",
        "transit",
        "mta",
        "bart",
        "cta",
        "septa",
        "wmata",
        "amtrak",
        "greyhound",
        # Airlines
        "airline",
        "delta",
        "united",
        "american airlines",
        "southwest",
        "jetblue",
        "spirit",
        "frontier",
        "alaska air",
        # Car rental
        "hertz",
        "enterprise",
        "avis",
        "budget",
        "national car",
        # Parking & tolls
        "parking",
        "toll",
        "ezpass",
        "fastrak",
    ],
    "Shopping & Retail": [
        # General retail
        "amazon",
        "walmart",
        "target",
        "costco",
        "sam's club",
        "best buy",
        "home depot",
        "lowe's",
        "ikea",
        "bed bath",
        "wayfair",
        # Fashion
        "nike",
        "adidas",
        "gap",
        "old navy",
        "h&m",
        "zara",
        "uniqlo",
        "nordstrom",
        "macy's",
        "kohl's",
        "ross",
        "tj maxx",
        "marshalls",
        # Electronics
        "apple store",
        "microsoft store",
        "gamestop",
        "newegg",
        # Online
        "ebay",
        "etsy",
        "wish",
        "aliexpress",
        "shopify",
        # Supplement/Vitamin stores
        "gnc",
        "vitamin shoppe",
        "vitamin world",
        "supplement",
        "nutrition store",
    ],
    "Entertainment & Recreation": [
        # Streaming
        "netflix",
        "hulu",
        "disney+",
        "disney plus",
        "hbo",
        "spotify",
        "apple music",
        "youtube",
        "amazon prime",
        "peacock",
        "paramount",
        # Gaming
        "steam",
        "playstation",
        "xbox",
        "nintendo",
        "epic games",
        "twitch",
        # Movies & events
        "amc",
        "regal",
        "cinemark",
        "movie",
        "theater",
        "theatre",
        "ticketmaster",
        "stubhub",
        "eventbrite",
        "livenation",
        # Sports & fitness
        "gym",
        "fitness",
        "planet fitness",
        "equinox",
        "orangetheory",
        "peloton",
        "crossfit",
    ],
    "Healthcare & Medical": [
        # Medical
        "hospital",
        "clinic",
        "doctor",
        "physician",
        "medical",
        "health",
        "urgent care",
        "emergency",
        "dental",
        "dentist",
        "vision",
        "eye",
        "optometrist",
        "orthodontist",
        "dermatologist",
        # Pharmacy
        "cvs",
        "walgreens",
        "rite aid",
        "pharmacy",
        "rx ",
        "prescription",
        # Insurance
        "aetna",
        "cigna",
        "united health",
        "blue cross",
        "anthem",
        "kaiser",
    ],
    "Utilities & Services": [
        # Electricity & gas
        "electric",
        "power",
        "pge",
        "con edison",
        "duke energy",
        "xcel",
        "gas company",
        "utility",
        # Internet & phone
        "comcast",
        "xfinity",
        "verizon",
        "at&t",
        "t-mobile",
        "sprint",
        "spectrum",
        "cox",
        "centurylink",
        "frontier",
        "internet",
        "wireless",
        # Water & trash
        "water",
        "sewer",
        "trash",
        "waste management",
        "republic services",
        # Rent & housing
        "rent",
        "lease",
        "property management",
        "hoa",
    ],
    "Financial Services": [
        # Banks
        "bank",
        "chase",
        "wells fargo",
        "bank of america",
        "citibank",
        "capital one",
        "pnc",
        "us bank",
        "td bank",
        "fifth third",
        # Credit cards
        "credit card",
        "visa",
        "mastercard",
        "amex",
        "american express",
        "discover",
        # Investing
        "fidelity",
        "vanguard",
        "schwab",
        "robinhood",
        "etrade",
        "ameritrade",
        "coinbase",
        "investment",
        # Payments
        "paypal",
        "venmo",
        "zelle",
        "cash app",
        "wire transfer",
        "ach",
        # Insurance
        "insurance",
        "geico",
        "progressive",
        "state farm",
        "allstate",
        "liberty mutual",
    ],
    "Income": [
        # Employment
        "payroll",
        "salary",
        "direct deposit",
        "paycheck",
        "wages",
        "employer",
        "bonus",
        # Freelance
        "freelance",
        "consulting",
        "invoice payment",
        "client payment",
        # Benefits
        "tax refund",
        "irs refund",
        "stimulus",
        "benefit",
        "social security",
        "disability",
        "unemployment",
        # Other
        "dividend",
        "interest income",
        "rental income",
        "royalty",
    ],
    "Government & Legal": [
        # Government
        "irs",
        "tax",
        "dmv",
        "license",
        "permit",
        "court",
        "fine",
        "government",
        "federal",
        "state of",
        "city of",
        "county",
        # Legal
        "attorney",
        "lawyer",
        "legal",
        "law office",
        "notary",
    ],
    "Charity & Donations": [
        # Charities
        "donation",
        "charity",
        "nonprofit",
        "red cross",
        "salvation army",
        "goodwill",
        "united way",
        "habitat for humanity",
        # Religious
        "church",
        "temple",
        "mosque",
        "synagogue",
        "tithe",
        "offering",
        # Political
        "campaign",
        "political",
        "pac ",
        # Crowdfunding
        "gofundme",
        "kickstarter",
        "patreon",
    ],
}


# =============================================================================
# DEFAULT CATEGORIES DATA
# =============================================================================

# These are seeded into the database on first migration
DEFAULT_CATEGORIES = [
    {
        "name": "Food & Dining",
        "description": "Restaurants, groceries, fast food, coffee shops, food delivery",
        "category_type": CategoryType.BOTH,  # BOTH: Supports refunds (e.g., DoorDash refund)
        "display_order": 1,
    },
    {
        "name": "Transportation",
        "description": "Gas, rideshare, airlines, public transport, car rental",
        "category_type": CategoryType.BOTH,  # BOTH: Supports refunds (e.g., flight refund)
        "display_order": 2,
    },
    {
        "name": "Shopping & Retail",
        "description": "Online shopping, electronics, retail, fashion, home & garden",
        "category_type": CategoryType.BOTH,  # BOTH: Supports refunds (e.g., Amazon return)
        "display_order": 3,
    },
    {
        "name": "Entertainment & Recreation",
        "description": "Streaming, gaming, movies, music, sports",
        "category_type": CategoryType.BOTH,  # BOTH: Supports refunds (e.g., ticket refund)
        "display_order": 4,
    },
    {
        "name": "Healthcare & Medical",
        "description": "Medical, pharmacy, dental, vision, fitness",
        "category_type": CategoryType.BOTH,  # BOTH: Supports reimbursements (e.g., insurance)
        "display_order": 5,
    },
    {
        "name": "Utilities & Services",
        "description": "Electricity, water, gas, internet & phone, cable",
        "category_type": CategoryType.BOTH,  # BOTH: Supports refunds (e.g., overpayment)
        "display_order": 6,
    },
    {
        "name": "Financial Services",
        "description": "Banking, insurance, credit cards, investments, taxes",
        "category_type": CategoryType.BOTH,  # BOTH: Supports income (e.g., interest earned)
        "display_order": 7,
    },
    {
        "name": "Income",
        "description": "Salary, freelance, business, investments, government benefits",
        "category_type": CategoryType.INCOME,  # INCOME only: True income sources
        "display_order": 8,
    },
    {
        "name": "Government & Legal",
        "description": "Taxes, licenses, legal services, government fees",
        "category_type": CategoryType.BOTH,  # BOTH: Supports refunds (e.g., tax refund)
        "display_order": 9,
    },
    {
        "name": "Charity & Donations",
        "description": "Charitable, religious, community, political donations",
        "category_type": CategoryType.EXPENSE,  # EXPENSE only: Donations are not refunded
        "display_order": 10,
    },
    {
        "name": "Unknown",
        "description": "Uncategorized transactions (AI confidence below threshold)",
        "category_type": CategoryType.BOTH,
        "display_order": 99,
    },
]


# =============================================================================
# CATEGORY MODEL
# =============================================================================


class Category(db.Model):
    """
    Category model representing a transaction category.

    This model stores categories for classifying transactions.
    11 default categories are seeded on first migration.

    Attributes:
        id: Primary key UUID
        name: Category name (unique, e.g., "Food & Dining")
        description: Category description
        category_type: income, expense, or both
        is_system: Whether this is a system category (cannot delete)
        display_order: Order for frontend display (1, 2, 3...)
        created_at: Record creation timestamp
        updated_at: Record update timestamp

    Relationships:
        transactions: One-to-Many relationship with Transaction model
        original_transactions: Transactions where this was AI's original guess

    Example:
        >>> category = Category.query.filter_by(name="Food & Dining").first()
        >>> category.to_dict()
        {
            "id": "uuid-string",
            "name": "Food & Dining",
            "description": "Restaurants, groceries...",
            "category_type": "expense",
            "display_order": 1
        }
    """

    __tablename__ = "categories"

    # =========================================================================
    # PRIMARY KEY
    # =========================================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Primary key UUID",
    )

    # =========================================================================
    # CATEGORY FIELDS
    # =========================================================================

    # User ID for custom categories (NULL for system categories)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        doc="Owner user ID (NULL for system categories)",
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Category name (unique per user or system)",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Category description",
    )

    category_type: Mapped[CategoryType] = mapped_column(
        Enum(
            CategoryType,
            name="category_type_enum",
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
            validate_strings=True,
        ),
        nullable=False,
        default=CategoryType.EXPENSE,
        index=True,
        doc="Category type: income, expense, or both",
    )

    icon: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="Icon name for frontend display",
    )

    color: Mapped[Optional[str]] = mapped_column(
        String(7),
        nullable=True,
        doc="Hex color code for frontend display (e.g., #FF6B6B)",
    )

    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="System category (cannot be deleted by users)",
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Display order for frontend",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        doc="Whether category is active (for soft delete)",
    )

    # =========================================================================
    # TIMESTAMPS
    # =========================================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Record creation timestamp",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Record update timestamp",
    )

    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================

    # One Category has many Transactions (1:N relationship)
    # This is the current category assigned to transactions
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="category_rel",
        foreign_keys="Transaction.category_id",
    )

    # Transactions where this was the AI's original suggestion
    # (before user override)
    original_transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="original_category_rel",
        foreign_keys="Transaction.original_category_id",
    )

    # One Category can have many Budgets (1:N relationship)
    # Users can set budgets per category
    budgets: Mapped[List["Budget"]] = relationship(
        "Budget",
        back_populates="category",
    )

    # Relationship to User (for custom categories)
    user = relationship(
        "User",
        backref="custom_categories",
        foreign_keys=[user_id],
    )

    # Unique constraint: category name must be unique per user (or unique among system categories)
    __table_args__ = (
        db.UniqueConstraint("name", "user_id", name="uq_category_name_per_user"),
    )

    # =========================================================================
    # METHODS
    # =========================================================================

    def __repr__(self) -> str:
        """String representation of Category."""
        return f"<Category {self.name}>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert category to dictionary for API response.

        Returns:
            Dictionary representation of category

        Example:
            >>> category.to_dict()
            {
                "id": "uuid-string",
                "name": "Food & Dining",
                "description": "Restaurants, groceries...",
                "category_type": "expense",
                "display_order": 1,
                "is_system": true,
                "is_custom": false
            }
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "category_type": self.category_type.value,
            "is_system": self.is_system,
            "is_custom": self.user_id is not None,
            "user_id": str(self.user_id) if self.user_id else None,
            "display_order": self.display_order,
            "icon": self.icon,
            "color": self.color,
        }

    # =========================================================================
    # CLASS METHODS
    # =========================================================================

    @classmethod
    def get_by_name(cls, name: str) -> Optional["Category"]:
        """
        Find category by name.

        Args:
            name: Category name (case-sensitive)

        Returns:
            Category instance or None

        Example:
            >>> category = Category.get_by_name("Food & Dining")
        """
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_unknown_category(cls) -> Optional["Category"]:
        """
        Get the "Unknown" category for low-confidence AI predictions.

        Returns:
            Unknown Category instance or None

        Example:
            >>> unknown = Category.get_unknown_category()
        """
        return cls.get_by_name("Unknown")

    @classmethod
    def get_all_ordered(cls) -> List["Category"]:
        """
        Get all categories ordered by display_order.

        Returns:
            List of Category instances

        Example:
            >>> categories = Category.get_all_ordered()
        """
        return cls.query.order_by(cls.display_order).all()

    @classmethod
    def get_by_type(cls, category_type: CategoryType) -> List["Category"]:
        """
        Get categories filtered by type.

        Args:
            category_type: CategoryType.INCOME, EXPENSE, or BOTH

        Returns:
            List of Category instances

        Example:
            >>> expense_categories = Category.get_by_type(CategoryType.EXPENSE)
        """
        return (
            cls.query.filter(
                (cls.category_type == category_type)
                | (cls.category_type == CategoryType.BOTH)
            )
            .order_by(cls.display_order)
            .all()
        )

    @classmethod
    def seed_defaults(cls) -> List["Category"]:
        """
        Seed default categories into the database.

        Called during migration to populate initial categories.
        Skips categories that already exist.

        Returns:
            List of created Category instances

        Example:
            >>> created = Category.seed_defaults()
            >>> len(created)
            11
        """
        created = []
        for cat_data in DEFAULT_CATEGORIES:
            existing = cls.get_by_name(cat_data["name"])
            if not existing:
                category = cls(
                    name=cat_data["name"],
                    description=cat_data["description"],
                    category_type=cat_data["category_type"],
                    display_order=cat_data["display_order"],
                    is_system=True,
                    user_id=None,  # System categories have no owner
                )
                db.session.add(category)
                created.append(category)

        if created:
            db.session.commit()

        return created

    @classmethod
    def get_for_user(cls, user_id: uuid.UUID) -> List["Category"]:
        """
        Get all categories available to a user (system + user's custom).

        Args:
            user_id: User's UUID

        Returns:
            List of Category instances (system categories first, then custom)

        Example:
            >>> categories = Category.get_for_user(user_id)
        """
        from sqlalchemy import or_

        return (
            cls.query.filter(
                cls.is_active.is_(True),
                or_(
                    cls.is_system.is_(True),  # System categories
                    cls.user_id == user_id,  # User's custom categories
                ),
            )
            .order_by(cls.is_system.desc(), cls.display_order, cls.name)
            .all()
        )

    @classmethod
    def get_user_custom_categories(cls, user_id: uuid.UUID) -> List["Category"]:
        """
        Get only user's custom categories.

        Args:
            user_id: User's UUID

        Returns:
            List of user's custom Category instances

        Example:
            >>> custom = Category.get_user_custom_categories(user_id)
        """
        return (
            cls.query.filter(
                cls.is_active.is_(True),
                cls.user_id == user_id,
            )
            .order_by(cls.name)
            .all()
        )

    @classmethod
    def get_by_name_for_user(
        cls,
        name: str,
        user_id: Optional[uuid.UUID] = None,
    ) -> Optional["Category"]:
        """
        Get category by name, checking user's custom categories first.

        Args:
            name: Category name
            user_id: Optional user ID (to check custom categories)

        Returns:
            Category instance or None

        Example:
            >>> category = Category.get_by_name_for_user("Pet Expenses", user_id)
        """
        from sqlalchemy import func

        # Check user's custom category first (if user_id provided)
        if user_id:
            custom = cls.query.filter(
                func.lower(cls.name) == name.lower(),
                cls.user_id == user_id,
                cls.is_active.is_(True),
            ).first()
            if custom:
                return custom

        # Fall back to system category
        return cls.query.filter(
            func.lower(cls.name) == name.lower(),
            cls.is_system.is_(True),
            cls.is_active.is_(True),
        ).first()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "Category",
    "DEFAULT_CATEGORIES",
]
