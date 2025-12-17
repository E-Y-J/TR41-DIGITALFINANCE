# =============================================================================
# Digital Finance Tracker - User Service
# PURPOSE: User service layer for business logic operations
# =============================================================================
"""
User Service Module

This module provides the service layer for User operations:
- Business logic separation from routes
- Data validation and transformation
- Database operations abstraction
- Error handling with meaningful exceptions

Usage:
    from app.services.user_service import UserService
    
    # Get user by Auth0 ID
    user = UserService.get_by_auth0_id("auth0|123")
    
    # Update user profile
    user = UserService.update_profile(user, {"name": "New Name"})
    
    # Update user settings
    user = UserService.update_settings(user, {"currency": "EUR"})

Design Principles:
    - Stateless class methods for all operations
    - All database commits happen here (not in routes)
    - All exceptions are domain-specific (not generic)
    - Input validation via schemas before operations
"""

import logging
from typing import Dict, Any, Optional, List
from uuid import UUID

from app.core.extensions import db
from app.models.user import User
from app.schemas.user_schema import user_update_schema, user_settings_update_schema
from app.utils.errors import (
    NotFoundError,
    ValidationError,
    ConflictError,
    InternalError,
)


# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# USER SERVICE CLASS
# =============================================================================

class UserService:
    """
    Service class for User operations.
    
    All methods are class methods (no instance needed).
    Handles business logic, validation, and database operations.
    
    Example:
        >>> user = UserService.get_by_auth0_id("auth0|123")
        >>> if user:
        ...     UserService.update_profile(user, {"name": "New Name"})
    """
    
    # =========================================================================
    # READ OPERATIONS
    # =========================================================================
    
    @classmethod
    def get_by_id(cls, user_id: UUID) -> User:
        """
        Get user by primary key ID.
        
        Args:
            user_id: User's UUID primary key
        
        Returns:
            User instance
        
        Raises:
            NotFoundError: If user not found
        
        Example:
            >>> user = UserService.get_by_id(uuid.UUID("..."))
        """
        user = User.query.get(user_id)
        
        if user is None:
            logger.debug(f"User not found by ID: {user_id}")
            raise NotFoundError("User not found")
        
        return user
    
    @classmethod
    def get_by_auth0_id(cls, auth0_id: str) -> User:
        """
        Get user by Auth0 ID.
        
        Args:
            auth0_id: Auth0 user ID (sub claim)
        
        Returns:
            User instance
        
        Raises:
            NotFoundError: If user not found
        
        Example:
            >>> user = UserService.get_by_auth0_id("auth0|123")
        """
        user = User.get_by_auth0_id(auth0_id)
        
        if user is None:
            logger.debug(f"User not found by Auth0 ID: {auth0_id}")
            raise NotFoundError("User not found")
        
        return user
    
    @classmethod
    def get_by_auth0_id_optional(cls, auth0_id: str) -> Optional[User]:
        """
        Get user by Auth0 ID, returning None if not found.
        
        Args:
            auth0_id: Auth0 user ID (sub claim)
        
        Returns:
            User instance or None
        
        Example:
            >>> user = UserService.get_by_auth0_id_optional("auth0|123")
            >>> if user:
            ...     print(user.email)
        """
        return User.get_by_auth0_id(auth0_id)
    
    @classmethod
    def get_by_email(cls, email: str) -> User:
        """
        Get user by email address.
        
        Args:
            email: User email address
        
        Returns:
            User instance
        
        Raises:
            NotFoundError: If user not found
        
        Example:
            >>> user = UserService.get_by_email("user@example.com")
        """
        user = User.get_by_email(email)
        
        if user is None:
            logger.debug(f"User not found by email: {email}")
            raise NotFoundError("User not found")
        
        return user
    
    # =========================================================================
    # UPDATE OPERATIONS
    # =========================================================================
    
    @classmethod
    def update_profile(cls, user: User, data: Dict[str, Any]) -> User:
        """
        Update user profile fields.
        
        Args:
            user: User instance to update
            data: Dictionary of fields to update
        
        Returns:
            Updated User instance
        
        Raises:
            ValidationError: If data fails validation
            InternalError: If database operation fails
        
        Example:
            >>> user = UserService.get_by_auth0_id("auth0|123")
            >>> updated = UserService.update_profile(user, {
            ...     "name": "New Name",
            ...     "nickname": "newnick"
            ... })
        
        Allowed Fields:
            - name: Display name
            - nickname: Short nickname
            - settings: User preferences (partial update)
        """
        # Validate input
        errors = user_update_schema.validate(data)
        if errors:
            raise ValidationError("Invalid profile data", details=errors)
        
        # Load validated data
        validated = user_update_schema.load(data)
        
        try:
            # Update name if provided
            if validated.get("name") is not None:
                user.name = validated["name"]
            
            # Update nickname if provided
            if validated.get("nickname") is not None:
                user.nickname = validated["nickname"]
            
            # Update settings if provided (merge with existing)
            if validated.get("settings"):
                cls._merge_settings(user, validated["settings"])
            
            db.session.commit()
            logger.info(f"Updated profile for user: {user.auth0_id}")
            
            return user
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update profile: {e}", exc_info=True)
            raise InternalError("Failed to update profile")
    
    @classmethod
    def update_settings(cls, user: User, settings: Dict[str, Any]) -> User:
        """
        Update user settings/preferences.
        
        Args:
            user: User instance to update
            settings: Dictionary of settings to update
        
        Returns:
            Updated User instance
        
        Raises:
            ValidationError: If settings fail validation
            InternalError: If database operation fails
        
        Example:
            >>> user = UserService.update_settings(user, {
            ...     "currency": "EUR",
            ...     "timezone": "Europe/London"
            ... })
        """
        # Validate settings
        errors = user_settings_update_schema.validate(settings)
        if errors:
            raise ValidationError("Invalid settings", details=errors)
        
        # Load validated data
        validated = user_settings_update_schema.load(settings)
        
        try:
            cls._merge_settings(user, validated)
            db.session.commit()
            logger.info(f"Updated settings for user: {user.auth0_id}")
            return user
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update settings: {e}", exc_info=True)
            raise InternalError("Failed to update settings")
    
    @classmethod
    def _merge_settings(cls, user: User, new_settings: Dict[str, Any]) -> None:
        """
        Merge new settings into existing user settings.
        
        Args:
            user: User instance
            new_settings: Settings to merge
        
        Notes:
            - Creates new dict to trigger SQLAlchemy change detection
            - Only updates provided keys (partial update)
            - Handles nested dicts (like notifications)
        """
        merged = dict(user.settings)
        
        for key, value in new_settings.items():
            if value is not None:
                if isinstance(value, dict) and isinstance(merged.get(key), dict):
                    # Merge nested dicts
                    merged[key] = {**merged[key], **value}
                else:
                    merged[key] = value
        
        user.settings = merged
    
    # =========================================================================
    # ACCOUNT OPERATIONS
    # =========================================================================
    
    @classmethod
    def deactivate_user(cls, user: User) -> User:
        """
        Deactivate a user account.
        
        Args:
            user: User instance to deactivate
        
        Returns:
            Updated User instance
        
        Raises:
            InternalError: If operation fails
        
        Notes:
            - Sets is_active to False
            - User data is preserved (soft delete)
            - User cannot login after deactivation
        """
        try:
            user.is_active = False
            db.session.commit()
            logger.info(f"Deactivated user: {user.auth0_id}")
            return user
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to deactivate user: {e}", exc_info=True)
            raise InternalError("Failed to deactivate account")
    
    @classmethod
    def reactivate_user(cls, user: User) -> User:
        """
        Reactivate a deactivated user account.
        
        Args:
            user: User instance to reactivate
        
        Returns:
            Updated User instance
        
        Raises:
            InternalError: If operation fails
        """
        try:
            user.is_active = True
            db.session.commit()
            logger.info(f"Reactivated user: {user.auth0_id}")
            return user
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to reactivate user: {e}", exc_info=True)
            raise InternalError("Failed to reactivate account")
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    @classmethod
    def get_user_for_request(cls, auth0_id: str) -> User:
        """
        Get user for current request, ensuring they exist and are active.
        
        Args:
            auth0_id: Auth0 user ID from token
        
        Returns:
            Active User instance
        
        Raises:
            NotFoundError: If user not found
            ValidationError: If user is deactivated
        
        Notes:
            Use this in routes after @requires_auth decorator.
        """
        user = cls.get_by_auth0_id(auth0_id)
        
        if not user.is_active:
            raise ValidationError("Account is deactivated")
        
        return user


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "UserService",
]
