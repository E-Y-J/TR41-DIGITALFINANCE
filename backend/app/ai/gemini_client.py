# =============================================================================
# Digital Finance Tracker - Gemini Client
# PURPOSE: Google Gemini API client for AI categorization fallback
# =============================================================================
"""
Gemini Client Module

This module provides the Gemini API integration for transaction categorization
when the HuggingFace model confidence is below threshold (< 70%).

Features:
    - Free tier support (rate limited)
    - Structured prompts for consistent output
    - Category validation
    - Error handling and retry logic

Environment Variables:
    GEMINI_API_KEY: Google Gemini API key (required)

Usage:
    from app.ai.gemini_client import GeminiClient, get_gemini_client

    # Get singleton instance
    client = get_gemini_client()

    # Categorize a transaction
    result = client.categorize_transaction(
        merchant_name="Random Store ABC",
        amount=50.00,
        description="Purchase"
    )
    # {"category": "Shopping & Retail", "confidence": 0.75, "reasoning": "..."}

Notes:
    - Uses Gemini 1.5 Flash for fast, cost-effective responses
    - Rate limited to respect free tier limits
    - Fallback to "Unknown" if API fails
"""

import os
import logging
import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import threading

logger = logging.getLogger(__name__)


# =============================================================================
# SYSTEM CATEGORIES
# =============================================================================

# Import centralized constants
try:
    from app.ai.constants import SYSTEM_CATEGORIES, VALID_CATEGORIES

    # Add "Unknown" if not present
    if "Unknown" not in VALID_CATEGORIES:
        VALID_CATEGORIES = set(SYSTEM_CATEGORIES) | {"Unknown"}
except ImportError:
    # Fallback if constants.py not available
    VALID_CATEGORIES = {
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
        "Unknown",
    }


# =============================================================================
# GEMINI CLIENT CLASS
# =============================================================================


class GeminiClient:
    """
    Google Gemini API client for transaction categorization.

    Uses Gemini 1.5 Flash model for efficient categorization.
    Implements rate limiting for free tier compliance.

    Attributes:
        model: The Gemini generative model
        is_initialized: Whether client has been initialized
        api_key: The Gemini API key

    Rate Limits (Free Tier):
        - 15 requests per minute
        - 1,000 requests per day
        - 1 million tokens per minute

    Example:
        >>> client = GeminiClient()
        >>> client.initialize()
        >>> result = client.categorize_transaction("Shell Gas Station", 45.00)
        >>> print(result["category"])
        Transportation
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
        """Initialize the Gemini client."""
        if hasattr(self, "_init_done") and self._init_done:
            return

        self.model = None
        self.is_initialized = False
        self.api_key = None

        # Rate limiting
        self._request_times: List[float] = []
        self._rate_limit_per_minute = 15
        self._daily_requests = 0
        self._daily_limit = 1000
        self._last_reset_date = None

        self._init_done = True

    def initialize(self) -> bool:
        """
        Initialize the Gemini client with API key.

        Returns:
            True if initialized successfully, False otherwise

        Raises:
            ValueError: If GEMINI_API_KEY not set
        """
        if self.is_initialized:
            return True

        try:
            from google import genai

            # Get API key from environment
            self.api_key = os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                logger.warning(
                    "GEMINI_API_KEY not set. Gemini fallback will be disabled."
                )
                return False

            # Initialize the client with the API key
            self._client = genai.Client(api_key=self.api_key)

            # Store model name (Gemini 2.0 Flash-Lite - best for free tier)
            self._model_name = "gemini-2.0-flash-lite"

            # Create a simple wrapper for compatibility
            self.model = self

            self.is_initialized = True
            logger.info("Gemini client initialized successfully")
            return True

        except ImportError:
            logger.error(
                "google-genai package not installed. "
                "Install with: pip install google-genai"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}", exc_info=True)
            return False

    def generate_content(self, prompt: str) -> object:
        """
        Generate content using the Gemini API.

        Wrapper method to maintain compatibility with the old API.

        Args:
            prompt: The prompt to send to Gemini

        Returns:
            Response object with .text attribute
        """
        if not hasattr(self, "_client"):
            raise RuntimeError("Gemini client not initialized")

        response = self._client.models.generate_content(
            model=self._model_name,
            contents=prompt,
        )
        return response

    def _check_rate_limit(self) -> bool:
        """
        Check if we're within rate limits.

        Returns:
            True if request can proceed, False if rate limited
        """
        now = time.time()
        today = datetime.now(timezone.utc).date()

        # Reset daily counter if new day
        if self._last_reset_date != today:
            self._daily_requests = 0
            self._last_reset_date = today

        # Check daily limit
        if self._daily_requests >= self._daily_limit:
            logger.warning("Gemini daily rate limit reached")
            return False

        # Clean old request times (older than 1 minute)
        self._request_times = [t for t in self._request_times if now - t < 60]

        # Check per-minute limit
        if len(self._request_times) >= self._rate_limit_per_minute:
            logger.warning("Gemini per-minute rate limit reached")
            return False

        return True

    def _record_request(self):
        """Record a request for rate limiting."""
        self._request_times.append(time.time())
        self._daily_requests += 1

    def categorize_transaction(
        self,
        merchant_name: str,
        amount: Optional[float] = None,
        description: Optional[str] = None,
        transaction_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Categorize a transaction using Gemini.

        Args:
            merchant_name: Name of the merchant
            amount: Transaction amount (optional, helps with context)
            description: Additional description (optional)
            transaction_type: "income" or "expense" (optional)

        Returns:
            Dictionary with categorization results:
            {
                "category": "Food & Dining",
                "confidence": 0.85,
                "reasoning": "McDonald's is a fast food restaurant",
                "source": "gemini"
            }

        Example:
            >>> result = client.categorize_transaction(
            ...     "AMZN Mktp US",
            ...     amount=125.00,
            ...     description="Electronics purchase"
            ... )
            >>> result["category"]
            "Shopping & Retail"
        """
        if not self.is_initialized:
            if not self.initialize():
                return {
                    "category": "Unknown",
                    "confidence": 0.0,
                    "reasoning": "Gemini client not initialized",
                    "source": "gemini",
                    "error": "not_initialized",
                }

        # Check rate limit
        if not self._check_rate_limit():
            return {
                "category": "Unknown",
                "confidence": 0.0,
                "reasoning": "Rate limit exceeded",
                "source": "gemini",
                "error": "rate_limited",
            }

        try:
            # Build the prompt
            prompt = self._build_categorization_prompt(
                merchant_name, amount, description, transaction_type
            )

            # Make the API call
            self._record_request()
            response = self.model.generate_content(prompt)

            # Parse the response
            return self._parse_categorization_response(response.text)

        except Exception as e:
            logger.error(
                f"Gemini categorization failed for '{merchant_name}': {e}",
                exc_info=True,
            )
            return {
                "category": "Unknown",
                "confidence": 0.0,
                "reasoning": f"API error: {str(e)}",
                "source": "gemini",
                "error": str(e),
            }

    def _build_categorization_prompt(
        self,
        merchant_name: str,
        amount: Optional[float],
        description: Optional[str],
        transaction_type: Optional[str],
    ) -> str:
        """Build the categorization prompt for Gemini."""
        categories_list = ", ".join(
            [f'"{c}"' for c in VALID_CATEGORIES if c != "Unknown"]
        )

        prompt = f"""You are a financial transaction categorizer. Analyze the following transaction and categorize it.

TRANSACTION DETAILS:
- Merchant/Payee: {merchant_name}
{f'- Amount: ${amount:.2f}' if amount else ''}
{f'- Description: {description}' if description else ''}
{f'- Type: {transaction_type}' if transaction_type else ''}

AVAILABLE CATEGORIES:
{categories_list}

INSTRUCTIONS:
1. Analyze the merchant name and any available context
2. Choose the SINGLE most appropriate category from the list above
3. Provide a confidence score between 0.0 and 1.0
4. If you cannot determine the category with at least 50% confidence, use "Unknown"

RESPOND IN THIS EXACT JSON FORMAT (no markdown, just raw JSON):
{{"category": "Category Name", "confidence": 0.85, "reasoning": "Brief explanation"}}

YOUR RESPONSE:"""

        return prompt

    def _parse_categorization_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the Gemini response into structured data."""
        try:
            # Clean up the response (remove markdown code blocks if present)
            cleaned = response_text.strip()
            if cleaned.startswith("```"):
                # Remove markdown code block
                lines = cleaned.split("\n")
                cleaned = "\n".join(lines[1:-1])
            cleaned = cleaned.strip()

            # Parse JSON
            result = json.loads(cleaned)

            # Validate category
            category = result.get("category", "Unknown")
            if category not in VALID_CATEGORIES:
                # Try to match partial
                for valid_cat in VALID_CATEGORIES:
                    if category.lower() in valid_cat.lower():
                        category = valid_cat
                        break
                else:
                    category = "Unknown"

            # Validate confidence
            confidence = float(result.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1

            return {
                "category": category,
                "confidence": round(confidence, 4),
                "reasoning": result.get("reasoning", ""),
                "source": "gemini",
            }

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Gemini response as JSON: {e}")
            # Try to extract category from plain text
            for cat in VALID_CATEGORIES:
                if cat.lower() in response_text.lower():
                    return {
                        "category": cat,
                        "confidence": 0.5,
                        "reasoning": "Extracted from non-JSON response",
                        "source": "gemini",
                    }
            return {
                "category": "Unknown",
                "confidence": 0.0,
                "reasoning": "Failed to parse response",
                "source": "gemini",
                "error": "parse_error",
            }

    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        General chat interaction with Gemini for user queries.

        Args:
            message: User's message
            context: Optional context (user info, recent transactions, etc.)

        Returns:
            Gemini's response text

        Example:
            >>> response = client.chat("What category is Uber?")
            >>> print(response)
            "Uber is typically categorized as Transportation..."
        """
        if not self.is_initialized:
            if not self.initialize():
                return "I'm sorry, the AI assistant is currently unavailable."

        if not self._check_rate_limit():
            return "I'm currently busy. Please try again in a moment."

        try:
            # Build context-aware prompt
            system_context = """You are a helpful financial assistant for a personal finance tracking app.
You help users:
- Categorize transactions
- Understand their spending patterns
- Manage budgets and alerts
- Answer questions about their finances

Be concise, friendly, and helpful. Focus on financial topics."""

            if context:
                system_context += f"\n\nUser Context: {json.dumps(context)}"

            full_prompt = f"{system_context}\n\nUser: {message}\n\nAssistant:"

            self._record_request()
            response = self.model.generate_content(full_prompt)

            return response.text.strip()

        except Exception as e:
            logger.error(f"Gemini chat failed: {e}", exc_info=True)
            # Check for rate limit / quota exceeded errors
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                return "AI quota temporarily exceeded. The system is using local processing. For full AI features, please wait a minute or try again later."
            return "I encountered an error. Please try again."

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the Gemini client."""
        today = datetime.now(timezone.utc).date()
        if self._last_reset_date != today:
            self._daily_requests = 0
            self._last_reset_date = today

        return {
            "is_initialized": self.is_initialized,
            "api_key_set": bool(self.api_key),
            "daily_requests_used": self._daily_requests,
            "daily_limit": self._daily_limit,
            "requests_remaining_today": self._daily_limit - self._daily_requests,
            "per_minute_limit": self._rate_limit_per_minute,
            "requests_in_last_minute": len(
                [t for t in self._request_times if time.time() - t < 60]
            ),
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """
    Get the singleton GeminiClient instance.

    Returns:
        GeminiClient instance (creates if not exists)
    """
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client


def initialize_gemini() -> bool:
    """
    Initialize the Gemini client.

    Should be called at application startup.

    Returns:
        True if successful, False otherwise
    """
    client = get_gemini_client()
    return client.initialize()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "GeminiClient",
    "get_gemini_client",
    "initialize_gemini",
    "VALID_CATEGORIES",
]
