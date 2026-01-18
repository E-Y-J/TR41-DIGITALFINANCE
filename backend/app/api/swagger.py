# =============================================================================
# Digital Finance Tracker - Swagger/OpenAPI Configuration
# PURPOSE: Configure Swagger UI for API documentation
# =============================================================================
"""
Swagger Configuration Module

This module provides OpenAPI/Swagger documentation for the API:
- Serves Swagger UI at /api/docs
- Provides OpenAPI spec at /api/docs/openapi.json
- Documents all API endpoints with schemas

Usage:
    # Register in app factory
    from app.api.swagger import init_swagger
    init_swagger(app)

Access:
    - Swagger UI: http://localhost:8000/api/docs
    - OpenAPI JSON: http://localhost:8000/api/docs/openapi.json

Note:
    Port 8000 is used to match the frontend's expected API base URL.
    Frontend (Vite) runs on port 5173, backend (Flask) runs on port 8000.
"""

import logging
from flask import Flask, Blueprint, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# OPENAPI SPECIFICATION
# =============================================================================

OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Digital Finance Tracker API",
        "description": """
## AI-Powered Personal Finance Management API

This API provides endpoints for managing personal finances including:
- **Authentication** - Auth0-based user authentication
- **Users** - User profile and settings management
- **Transactions** - CRUD operations for financial transactions

### Authentication
All protected endpoints require a valid Auth0 JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### Response Format
Most API endpoints follow a standard format:
```json
{
    "success": true,
    "data": {...},
    "message": "Success message"
}
```

### Special Cases
**Exceptions**:
- "/" and "/health" return unwrapped objects (no success/data/message).

Error responses:
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Error description",
        "details": {...}
    }
}
```
        """,
        "version": "1.0.0",
        "contact": {
            "name": "Digital Finance Tracker Team",
            "email": "support@digitalfinance.com",
        },
        "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    },
    # NOTE: Port 8000 matches frontend's apiClient baseURL configuration
    # Frontend expects backend at http://localhost:8000/api
    "servers": [{"url": "http://localhost:8000", "description": "Development server"}],
    "tags": [
        {"name": "Health", "description": "Health check endpoints"},
        {"name": "Test", "description": "Frontend-backend connection testing"},
        {"name": "Auth", "description": "Authentication and authorization"},
        {"name": "Users", "description": "User profile and settings"},
        {"name": "Transactions", "description": "Financial transaction operations"},
    ],
    "paths": {
        "/": {
            "get": {
                "tags": ["Health"],
                "summary": "API Root",
                "description": "Get API information and status. Note: This endpoint returns an unwrapped object (no success/data/message). ",
                "responses": {
                    "200": {
                        "description": "API information",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "example": "Digital Finance Tracker API",
                                        },
                                        "version": {
                                            "type": "string",
                                            "example": "1.0.0",
                                        },
                                        "status": {
                                            "type": "string",
                                            "example": "running",
                                        },
                                        "docs": {
                                            "type": "string",
                                            "example": "/api/docs",
                                        },
                                    },
                                }
                            }
                        },
                    }
                },
            }
        },
        "/health": {
            "get": {
                "tags": ["Health"],
                "summary": "Health Check",
                "description": "Check if the service is healthy. Note: This endpoint returns an unwrapped object (no success/data/message).",
                "responses": {
                    "200": {
                        "description": "Service is healthy",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {
                                            "type": "string",
                                            "example": "healthy",
                                        },
                                        "service": {
                                            "type": "string",
                                            "example": "digital-finance-api",
                                        },
                                    },
                                }
                            }
                        },
                    }
                },
            }
        },
        "/api/test": {
            "get": {
                "tags": ["Test"],
                "summary": "Test Connection",
                "description": "Simple endpoint for frontend-backend connection verification. No authentication required.",
                "responses": {
                    "200": {
                        "description": "Connection successful",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {
                                            "type": "boolean",
                                            "example": True,
                                        },
                                        "message": {
                                            "type": "string",
                                            "example": "Hello from backend!",
                                        },
                                        "data": {
                                            "type": "object",
                                            "properties": {
                                                "status": {
                                                    "type": "string",
                                                    "example": "connected",
                                                },
                                                "api_version": {
                                                    "type": "string",
                                                    "example": "1.0.0",
                                                },
                                                "service": {
                                                    "type": "string",
                                                    "example": "digital-finance-api",
                                                },
                                            },
                                        },
                                    },
                                }
                            }
                        },
                    }
                },
            }
        },
        "/api/auth/callback": {
            "post": {
                "tags": ["Auth"],
                "summary": "Auth0 Callback",
                "description": "Sync user after Auth0 login. Frontend calls this after receiving tokens from Auth0.",
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "User synced successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/UserResponse"}
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                },
            }
        },
        "/api/auth/me": {
            "get": {
                "tags": ["Auth"],
                "summary": "Get Current User",
                "description": "Get the currently authenticated user's information",
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "User information",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/UserResponse"}
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                },
            }
        },
        "/api/auth/status": {
            "get": {
                "tags": ["Auth"],
                "summary": "Check Auth Status",
                "description": "Check if the user is authenticated (optional auth)",
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Authentication status",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "data": {
                                            "type": "object",
                                            "properties": {
                                                "authenticated": {"type": "boolean"},
                                                "user": {
                                                    "$ref": "#/components/schemas/User"
                                                },
                                            },
                                        },
                                    },
                                }
                            }
                        },
                    }
                },
            }
        },
        "/api/auth/logout": {
            "post": {
                "tags": ["Auth"],
                "summary": "Logout Instructions",
                "description": "Get instructions for client-side logout",
                "responses": {
                    "200": {
                        "description": "Logout instructions",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "message": {"type": "string"},
                                        "data": {
                                            "type": "object",
                                            "properties": {
                                                "instructions": {"type": "string"},
                                                "auth0_logout_url": {"type": "string"},
                                            },
                                        },
                                    },
                                }
                            }
                        },
                    }
                },
            }
        },
        "/api/users/me": {
            "get": {
                "tags": ["Users"],
                "summary": "Get Current User Profile",
                "description": "Get the authenticated user's profile information",
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "User profile",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/UserResponse"}
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                },
            },
            "patch": {
                "tags": ["Users"],
                "summary": "Update Current User Profile",
                "description": "Update the authenticated user's profile information",
                "security": [{"bearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/UserUpdate"}
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Profile updated",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/UserResponse"}
                            }
                        },
                    },
                    "400": {
                        "description": "Validation error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                },
            },
        },
        "/api/users/me/settings": {
            "get": {
                "tags": ["Users"],
                "summary": "Get User Settings",
                "description": "Get the authenticated user's settings (currency, notification preferences)",
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "User settings",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/SettingsResponse"
                                }
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                },
            },
            "patch": {
                "tags": ["Users"],
                "summary": "Update User Settings",
                "description": "Update the authenticated user's settings",
                "security": [{"bearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SettingsUpdate"}
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Settings updated",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/SettingsResponse"
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Validation error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                },
            },
        },
        "/api/users/me/deactivate": {
            "post": {
                "tags": ["Users"],
                "summary": "Deactivate Account",
                "description": "Deactivate the current user's account. This is a soft delete - user data is preserved. User can contact support to reactivate.",
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Account deactivated",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean", "example": True},
                                        "message": {
                                            "type": "string",
                                            "example": "Account deactivated successfully",
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                },
            }
        },
        "/api/transactions": {
            "get": {
                "tags": ["Transactions"],
                "summary": "List Transactions",
                "description": "Get paginated list of user's transactions",
                "security": [{"bearerAuth": []}],
                "parameters": [
                    {
                        "name": "page",
                        "in": "query",
                        "schema": {"type": "integer", "default": 1},
                        "description": "Page number",
                    },
                    {
                        "name": "per_page",
                        "in": "query",
                        "schema": {"type": "integer", "default": 20, "maximum": 100},
                        "description": "Items per page (max 100)",
                    },
                    {
                        "name": "transaction_type",
                        "in": "query",
                        "schema": {"type": "string", "enum": ["income", "expense"]},
                        "description": "Filter by transaction type",
                    },
                    {
                        "name": "category",
                        "in": "query",
                        "schema": {"type": "string"},
                        "description": "Filter by category",
                    },
                    {
                        "name": "start_date",
                        "in": "query",
                        "schema": {"type": "string", "format": "date"},
                        "description": "Filter from date (YYYY-MM-DD)",
                    },
                    {
                        "name": "end_date",
                        "in": "query",
                        "schema": {"type": "string", "format": "date"},
                        "description": "Filter to date (YYYY-MM-DD)",
                    },
                    {
                        "name": "sort_by",
                        "in": "query",
                        "schema": {
                            "type": "string",
                            "enum": ["date", "amount", "created_at"],
                            "default": "date",
                        },
                        "description": "Sort field",
                    },
                    {
                        "name": "sort_order",
                        "in": "query",
                        "schema": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "default": "desc",
                        },
                        "description": "Sort order",
                    },
                ],
                "responses": {
                    "200": {
                        "description": "List of transactions",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/TransactionListResponse"
                                }
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                },
            },
            "post": {
                "tags": ["Transactions"],
                "summary": "Create Transaction",
                "description": "Create a new transaction",
                "security": [{"bearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/TransactionCreate"}
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "Transaction created",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/TransactionResponse"
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Validation error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                },
            },
        },
        "/api/transactions/{id}": {
            "get": {
                "tags": ["Transactions"],
                "summary": "Get Transaction",
                "description": "Get a single transaction by ID",
                "security": [{"bearerAuth": []}],
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"},
                        "description": "Transaction UUID",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Transaction details",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/TransactionResponse"
                                }
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                    "404": {
                        "description": "Transaction not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                },
            },
            "patch": {
                "tags": ["Transactions"],
                "summary": "Update Transaction",
                "description": "Update an existing transaction",
                "security": [{"bearerAuth": []}],
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"},
                        "description": "Transaction UUID",
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/TransactionUpdate"}
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Transaction updated",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/TransactionResponse"
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Validation error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                    "404": {
                        "description": "Transaction not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                },
            },
            "delete": {
                "tags": ["Transactions"],
                "summary": "Delete Transaction",
                "description": "Delete a transaction",
                "security": [{"bearerAuth": []}],
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"},
                        "description": "Transaction UUID",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Transaction deleted",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "message": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                    "404": {
                        "description": "Transaction not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                },
            },
        },
        "/api/transactions/summary": {
            "get": {
                "tags": ["Transactions"],
                "summary": "Get Transaction Summary",
                "description": "Get summary statistics for user's transactions",
                "security": [{"bearerAuth": []}],
                "parameters": [
                    {
                        "name": "start_date",
                        "in": "query",
                        "schema": {"type": "string", "format": "date"},
                        "description": "Start date for summary (YYYY-MM-DD)",
                    },
                    {
                        "name": "end_date",
                        "in": "query",
                        "schema": {"type": "string", "format": "date"},
                        "description": "End date for summary (YYYY-MM-DD)",
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Transaction summary",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/SummaryResponse"
                                }
                            }
                        },
                    },
                    "401": {"$ref": "#/components/responses/UnauthorizedError"},
                },
            }
        },
    },
    "components": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Auth0 JWT access token",
            }
        },
        "responses": {
            "UnauthorizedError": {
                "description": "Unauthorized - missing or invalid token",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "examples": {
                            "authorization_header_missing": {
                                "summary": "Authorization header missing",
                                "value": {
                                    "error": {
                                        "code": "UNAUTHORIZED",
                                        "message": "Authorization header missing",
                                    },
                                    "success": False,
                                },
                            },
                            "invalid_token": {
                                "summary": "Invalid or expired token",
                                "value": {
                                    "error": {
                                        "code": "UNAUTHORIZED",
                                        "message": "Invalid or expired token",
                                    },
                                    "success": False,
                                },
                            },
                        },
                    }
                },
            },
            "ValidationError": {
                "description": "Validation error - bad request payload or params",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "examples": {
                            "invalid_payload": {
                                "summary": "Invalid payload",
                                "value": {
                                    "error": {
                                        "code": "VALIDATION_ERROR",
                                        "message": "One or more fields are invalid",
                                        "details": {"field": "reason"},
                                    },
                                    "success": False,
                                },
                            }
                        },
                    }
                },
            },
            "NotFoundError": {
                "description": "Resource not found",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "examples": {
                            "not_found": {
                                "summary": "Entity not found",
                                "value": {
                                    "error": {
                                        "code": "NOT_FOUND",
                                        "message": "Resource not found",
                                    },
                                    "success": False,
                                },
                            }
                        },
                    }
                },
            },
        },
        "schemas": {
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "auth0_id": {
                        "type": "string",
                        "description": "Auth0 user identifier",
                    },
                    "email": {"type": "string", "format": "email"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "nickname": {
                        "type": "string",
                        "nullable": True,
                        "description": "Optional nickname/display name",
                    },
                    "full_name": {
                        "type": "string",
                        "description": "Computed full name",
                    },
                    "account_status": {
                        "type": "string",
                        "enum": ["pending", "active", "suspended", "deactivated"],
                    },
                    "role": {"type": "string", "enum": ["user", "admin"]},
                    "salary_amount": {
                        "type": "string",
                        "description": "Decimal as string",
                    },
                    "settings": {"$ref": "#/components/schemas/UserSettings"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"},
                    "last_login": {
                        "type": "string",
                        "format": "date-time",
                        "nullable": True,
                    },
                },
            },
            "UserSettings": {
                "type": "object",
                "properties": {
                    "currency": {
                        "type": "string",
                        "example": "USD",
                        "description": "3-letter currency code",
                    },
                    "timezone": {"type": "string", "example": "America/New_York"},
                    "notifications": {
                        "type": "object",
                        "additionalProperties": {"type": "boolean"},
                    },
                    "theme": {"type": "string", "enum": ["light", "dark", "system"]},
                },
            },
            "UserUpdate": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string", "maxLength": 100},
                    "last_name": {"type": "string", "maxLength": 100},
                    "nickname": {
                        "type": "string",
                        "maxLength": 100,
                        "nullable": True,
                        "description": "Optional nickname/display name",
                    },
                    "salary_amount": {
                        "type": "string",
                        "description": "Decimal as string for budgeting",
                    },
                },
            },
            "UserResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "data": {"$ref": "#/components/schemas/User"},
                    "message": {"type": "string"},
                },
            },
            "SettingsUpdate": {
                "type": "object",
                "properties": {
                    "currency": {
                        "type": "string",
                        "description": "3-letter currency code",
                    },
                    "timezone": {"type": "string"},
                    "notifications": {
                        "type": "object",
                        "additionalProperties": {"type": "boolean"},
                    },
                    "theme": {"type": "string", "enum": ["light", "dark", "system"]},
                },
            },
            "SettingsResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "data": {"$ref": "#/components/schemas/UserSettings"},
                    "message": {"type": "string"},
                },
            },
            "Transaction": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "user_id": {"type": "string", "format": "uuid"},
                    "transaction_type": {
                        "type": "string",
                        "enum": ["income", "expense"],
                    },
                    "amount": {"type": "string", "description": "Decimal as string"},
                    "date": {"type": "string", "format": "date"},
                    "merchant_name": {"type": "string", "nullable": True},
                    "category": {"type": "string", "nullable": True},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"},
                },
            },
            "TransactionCreate": {
                "type": "object",
                "required": ["transaction_type", "amount", "date"],
                "properties": {
                    "transaction_type": {
                        "type": "string",
                        "enum": ["income", "expense"],
                    },
                    "amount": {
                        "type": "string",
                        "description": "Decimal amount (e.g., '125.50')",
                    },
                    "date": {"type": "string", "format": "date"},
                    "merchant_name": {"type": "string", "maxLength": 255},
                    "category": {"type": "string", "maxLength": 100},
                },
            },
            "TransactionUpdate": {
                "type": "object",
                "properties": {
                    "transaction_type": {
                        "type": "string",
                        "enum": ["income", "expense"],
                    },
                    "amount": {
                        "type": "string",
                        "description": "Decimal amount (e.g., '125.50')",
                    },
                    "date": {"type": "string", "format": "date"},
                    "merchant_name": {"type": "string", "maxLength": 255},
                    "category": {"type": "string", "maxLength": 100},
                },
            },
            "TransactionResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "data": {"$ref": "#/components/schemas/Transaction"},
                    "message": {"type": "string"},
                },
            },
            "TransactionListResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "data": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Transaction"},
                    },
                    "message": {"type": "string"},
                    "meta": {
                        "type": "object",
                        "properties": {
                            "page": {"type": "integer"},
                            "per_page": {"type": "integer"},
                            "total": {"type": "integer"},
                            "total_pages": {"type": "integer"},
                        },
                    },
                },
            },
            "SummaryResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "total_income": {
                                "type": "string",
                                "description": "Decimal as string",
                            },
                            "total_expense": {
                                "type": "string",
                                "description": "Decimal as string",
                            },
                            "net_balance": {
                                "type": "string",
                                "description": "Decimal as string",
                            },
                            "income_count": {"type": "integer"},
                            "expense_count": {"type": "integer"},
                        },
                    },
                    "message": {"type": "string"},
                },
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": False},
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "message": {"type": "string"},
                            "details": {"type": "object"},
                        },
                    },
                },
            },
        },
    },
}


# =============================================================================
# SWAGGER UI CONFIGURATION
# =============================================================================

# Swagger UI Blueprint
SWAGGER_URL = "/api/docs"
API_URL = "/api/docs/openapi.json"


def init_swagger(app: Flask) -> None:
    """
    Initialize Swagger UI for the Flask application.

    Args:
        app: Flask application instance

    Notes:
        - Swagger UI available at /api/docs
        - OpenAPI spec available at /api/docs/openapi.json
    """
    # Create blueprint for serving OpenAPI spec
    swagger_spec_bp = Blueprint("swagger_spec", __name__)

    @swagger_spec_bp.route("/api/docs/openapi.json")
    def get_openapi_spec():
        """Serve the OpenAPI specification as JSON."""
        return jsonify(OPENAPI_SPEC)

    # Register the spec blueprint
    app.register_blueprint(swagger_spec_bp)

    # Create Swagger UI blueprint
    swagger_ui_bp = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            "app_name": "Digital Finance Tracker API",
            "layout": "BaseLayout",
            "deepLinking": True,
            "displayRequestDuration": True,
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
        },
    )

    # Register Swagger UI blueprint
    app.register_blueprint(swagger_ui_bp, url_prefix=SWAGGER_URL)

    logger.info(f"Swagger UI initialized at {SWAGGER_URL}")


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "init_swagger",
    "OPENAPI_SPEC",
]
