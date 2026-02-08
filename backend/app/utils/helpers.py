# =============================================================================
# Digital Finance Tracker - Shared Utilities
# PURPOSE: Common helper functions used across routes and services
# =============================================================================
"""
Helpers Module

This module provides shared utility functions used across the application.
Centralizing these utilities:
- Reduces code duplication
- Ensures consistent behavior
- Simplifies maintenance

Created to consolidate duplicated functions from routes/users.py and
routes/transactions.py. All routes should import from here.

Usage:
    from app.utils.helpers import success_response, parse_uuid

    @bp.route("/items", methods=["GET"])
    def list_items():
        data = [...]
        return success_response(data=data, message="Items retrieved")

    @bp.route("/items/<item_id>", methods=["GET"])
    def get_item(item_id: str):
        uuid = parse_uuid(item_id)
        ...
"""

from typing import Any, Dict, Optional, Tuple
from uuid import UUID

from flask import jsonify

from app.utils.errors import ValidationError


# =============================================================================
# RESPONSE HELPERS
# =============================================================================


def success_response(
    data: Optional[Any] = None,
    message: str = "Success",
    status_code: int = 200,
    meta: Optional[Dict[str, Any]] = None,
) -> Tuple[Any, int]:
    """
    Create a standardized success response.

    All API endpoints should use this function to ensure consistent
    response format across the application.

    Args:
        data: Response data (will be included in 'data' field)
        message: Success message (default: "Success")
        status_code: HTTP status code (default: 200)
        meta: Optional metadata (pagination info, counts, etc.)

    Returns:
        Tuple of (Flask response, status_code)

    Example:
        >>> return success_response(
        ...     data={"id": "123", "name": "Test"},
        ...     message="Item created successfully",
        ...     status_code=201
        ... )

        Response:
        {
            "success": true,
            "message": "Item created successfully",
            "data": {"id": "123", "name": "Test"}
        }

    Example with pagination:
        >>> return success_response(
        ...     data=[...items...],
        ...     message="Items retrieved",
        ...     meta={"page": 1, "per_page": 20, "total": 100}
        ... )

        Response:
        {
            "success": true,
            "message": "Items retrieved",
            "data": [...items...],
            "meta": {"page": 1, "per_page": 20, "total": 100}
        }
    """
    response = {
        "success": True,
        "message": message,
    }

    if data is not None:
        response["data"] = data

    if meta is not None:
        response["meta"] = meta

    return jsonify(response), status_code


# =============================================================================
# VALIDATION HELPERS
# =============================================================================


def parse_uuid(value: str, field_name: str = "id") -> UUID:
    """
    Parse string to UUID with validation.

    Provides a consistent way to validate and convert UUID strings
    from path parameters or request bodies.

    Args:
        value: String value to parse as UUID
        field_name: Field name for error message (default: "id")

    Returns:
        UUID instance

    Raises:
        ValidationError: If value is not a valid UUID format

    Example:
        >>> uuid = parse_uuid("123e4567-e89b-12d3-a456-426614174000")
        >>> uuid
        UUID('123e4567-e89b-12d3-a456-426614174000')

        >>> parse_uuid("invalid-uuid")
        ValidationError: Invalid id: must be a valid UUID
    """
    try:
        return UUID(value)
    except (ValueError, AttributeError):
        raise ValidationError(f"Invalid {field_name}: must be a valid UUID")


def validate_pagination(
    page: int = 1,
    per_page: int = 20,
    max_per_page: int = 100,
) -> Tuple[int, int]:
    """
    Validate and normalize pagination parameters.

    Ensures pagination values are within acceptable bounds.

    Args:
        page: Page number (1-indexed, default: 1)
        per_page: Items per page (default: 20)
        max_per_page: Maximum allowed items per page (default: 100)

    Returns:
        Tuple of (validated_page, validated_per_page)

    Raises:
        ValidationError: If page is less than 1

    Example:
        >>> page, per_page = validate_pagination(page=2, per_page=50)
        >>> page, per_page
        (2, 50)

        >>> page, per_page = validate_pagination(per_page=500)  # Exceeds max
        >>> per_page
        100
    """
    if page < 1:
        raise ValidationError("Page number must be at least 1")

    # Ensure per_page doesn't exceed maximum
    per_page = min(max(per_page, 1), max_per_page)

    return page, per_page


# =============================================================================
# DATE HELPERS
# =============================================================================


def get_date_range_for_period(
    period: str,
    reference_date: Optional[str] = None,
):
    """
    Get start and end dates for a given period.

    Used by summary endpoints to calculate date ranges.

    Args:
        period: Period type - "daily", "weekly", "monthly", "yearly", "ytd"
        reference_date: Reference date (YYYY-MM-DD format). Defaults to today.

    Returns:
        Tuple of (start_date, end_date) as date objects

    Raises:
        ValidationError: If period is invalid

    Example:
        >>> start, end = get_date_range_for_period("weekly", "2026-01-06")
        >>> start, end
        (date(2025, 12, 30), date(2026, 1, 5))  # Monday to Sunday of that week
    """
    from datetime import datetime, timedelta, date

    # Parse reference date or use today
    if reference_date:
        try:
            ref = datetime.strptime(reference_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Invalid date format. Use YYYY-MM-DD")
    else:
        ref = date.today()

    if period == "daily":
        start = ref
        end = ref

    elif period == "weekly":
        # Week starts on Monday (ISO standard)
        start = ref - timedelta(days=ref.weekday())
        end = start + timedelta(days=6)

    elif period == "monthly":
        start = ref.replace(day=1)
        # Get last day of month
        if ref.month == 12:
            end = ref.replace(year=ref.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = ref.replace(month=ref.month + 1, day=1) - timedelta(days=1)

    elif period == "yearly":
        start = ref.replace(month=1, day=1)
        end = ref.replace(month=12, day=31)

    elif period == "ytd":
        # Year to date: from Jan 1 to reference date
        start = ref.replace(month=1, day=1)
        end = ref

    else:
        raise ValidationError(
            f"Invalid period: {period}. "
            "Must be one of: daily, weekly, monthly, yearly, ytd"
        )

    # Return date objects (convert datetime to date if needed)
    if hasattr(start, "date"):
        start = start.date()
    if hasattr(end, "date"):
        end = end.date()

    return start, end


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "success_response",
    "parse_uuid",
    "validate_pagination",
    "get_date_range_for_period",
]
