# Frontend API Integration Guide

> **Last Updated:** February 3, 2026

## Overview

This document provides comprehensive API documentation for the frontend team to integrate with the backend services. It covers all implementations including user authentication flow, profile management, budget system, custom categories, budget suggestions, AI chat history, and transaction filters.

---

## Table of Contents

1. [Authentication & User Onboarding Flow](#authentication--user-onboarding-flow)
2. [User Profile Management](#user-profile-management)
3. [Budget System](#budget-system)
4. [Budget Suggestions](#budget-suggestions)
5. [Categories](#categories)
6. [Custom Categories](#custom-categories)
7. [Transactions](#transactions)
8. [Alerts & Notifications](#alerts--notifications)
9. [AI Features](#ai-features)
10. [AI Chat History](#ai-chat-history)
11. [Recurring Transactions](#recurring-transactions)

---

## Authentication & User Onboarding Flow

### Overview

The application uses Auth0 for authentication. After a user logs in through Auth0, the frontend should call our backend to sync the user and check if they need to complete onboarding.

### Flow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   User      │────>│   Auth0     │────>│  Frontend   │────>│  Backend    │
│   Login     │     │   Login     │     │  Callback   │     │  Callback   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                              ┌────────────────────┴───────────────────┐
                                              │                                        │
                                              ▼                                        ▼
                                        is_new_user: true                    is_new_user: false
                                        account_status: "pending"            account_status: "active"
                                              │                                        │
                                              ▼                                        │
                                        Show Questionnaire                             │
                                        (first_name, last_name, salary)               │
                                              │                                        │
                                              ▼                                        │
                                        PATCH /api/users/me                           │
                                        Auto-activates account                        │
                                              │                                        │
                                              ▼                                        ▼
                                        ◄─────────────────────────────────────────────►
                                                    Dashboard
```

### Step 1: Post-Login Callback

**After Auth0 login completes, call this endpoint to sync user with backend.**

```http
POST /api/auth/callback
Authorization: Bearer <access_token>
Content-Type: application/json

{}
```

**Response (New User):**
```json
{
    "success": true,
    "data": {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "auth0_id": "auth0|507f1f77bcf86cd799439011",
            "email": "john@example.com",
            "first_name": "",
            "last_name": "",
            "nickname": null,
            "full_name": "",
            "account_status": "pending",
            "role": "user",
            "salary_amount": "0.00",
            "settings": {
                "currency": "USD",
                "timezone": "UTC",
                "theme": "light"
            },
            "created_at": "2026-01-15T10:00:00Z",
            "updated_at": "2026-01-15T10:00:00Z"
        },
        "is_new_user": true
    },
    "message": "User synced successfully"
}
```

**Response (Returning User):**
```json
{
    "success": true,
    "data": {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "auth0_id": "auth0|507f1f77bcf86cd799439011",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "nickname": "JohnD",
            "full_name": "John Doe",
            "account_status": "active",
            "role": "user",
            "salary_amount": "5000.00",
            "settings": {...},
            "created_at": "2026-01-10T10:00:00Z",
            "updated_at": "2026-01-15T10:00:00Z"
        },
        "is_new_user": false
    },
    "message": "User synced successfully"
}
```

### Step 2: Questionnaire Flow (New Users Only)

**If `is_new_user: true` AND `account_status: "pending"`, show the onboarding questionnaire.**

Required fields for activation:
- `first_name` (required)
- `last_name` (required)
- `salary_amount` (optional, but recommended)

### Step 3: Update Profile (Auto-Activation)

```http
PATCH /api/users/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "salary_amount": "5000.00"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "account_status": "active",  // <-- AUTO-ACTIVATED!
        "role": "user",
        "salary_amount": "5000.00",
        "settings": {...}
    },
    "message": "Profile updated successfully"
}
```

**⚠️ Important:** When a user with `account_status: "pending"` provides both `first_name` AND `last_name`, the account is **automatically activated** (changed to `account_status: "active"`).

---

## User Profile Management

### Get Current User Profile

```http
GET /api/users/me
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "auth0_id": "auth0|507f1f77bcf86cd799439011",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "nickname": "JohnD",
        "full_name": "John Doe",
        "account_status": "active",
        "role": "user",
        "salary_amount": "5000.00",
        "settings": {
            "currency": "USD",
            "timezone": "UTC",
            "theme": "light",
            "notifications": {
                "email": true,
                "push": false,
                "reminders": true
            }
        },
        "created_at": "2026-01-10T10:00:00Z",
        "updated_at": "2026-01-15T10:00:00Z",
        "last_login": "2026-01-15T10:00:00Z"
    },
    "message": "User retrieved successfully"
}
```

### Update User Profile

```http
PATCH /api/users/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Smith",
    "salary_amount": "6000.00",
    "settings": {
        "currency": "EUR",
        "theme": "dark"
    }
}
```

**Allowed Fields:**

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `first_name` | string | User's first name | Max 100 chars, not blank |
| `last_name` | string | User's last name | Max 100 chars, not blank |
| `nickname` | string | Optional display name | Max 100 chars, nullable |
| `salary_amount` | decimal | Monthly salary | >= 0, 2 decimal places |
| `settings` | object | User preferences | Merged with existing |

### Update User Settings Only

```http
PATCH /api/users/me/settings
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "currency": "GBP",
    "theme": "dark",
    "notifications": {
        "email": false
    }
}
```

---

## Budget System

### Overview

Users can create budgets to track their spending limits. Budgets can be:
- **TOTAL**: Overall spending limit across all categories
- **CATEGORY**: Spending limit for a specific category

Budget periods:
- **WEEKLY**: Resets every Monday
- **MONTHLY**: Resets on the 1st of each month

Warning threshold: **Fixed at 70%** (not configurable)

### Get All Budgets with Spending Info

```http
GET /api/budgets
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `active_only` | boolean | true | Only return active budgets |

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": "budget-uuid-1",
            "user_id": "user-uuid",
            "category_id": null,
            "category_name": null,
            "budget_type": "total",
            "amount": "2000.00",
            "period": "monthly",
            "warning_threshold": 70,
            "last_period_surplus": "150.00",
            "is_active": true,
            "spent": "1400.00",
            "remaining": "600.00",
            "percentage_used": 70.0,
            "is_warning": true,
            "is_exceeded": false,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-15T10:00:00Z"
        },
        {
            "id": "budget-uuid-2",
            "user_id": "user-uuid",
            "category_id": "food-category-uuid",
            "category_name": "Food & Dining",
            "budget_type": "category",
            "amount": "300.00",
            "period": "monthly",
            "warning_threshold": 70,
            "last_period_surplus": "25.00",
            "is_active": true,
            "spent": "245.00",
            "remaining": "55.00",
            "percentage_used": 81.7,
            "is_warning": true,
            "is_exceeded": false,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-15T10:00:00Z"
        }
    ],
    "message": "Budgets retrieved successfully",
    "meta": {
        "total": 2,
        "active": 2,
        "warning_count": 2,
        "exceeded_count": 0
    }
}
```

### Create Budget

**Create Total Budget:**
```http
POST /api/budgets
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "budget_type": "total",
    "amount": "2000.00",
    "period": "monthly"
}
```

**Create Category Budget:**
```http
POST /api/budgets
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "budget_type": "category",
    "category_id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": "300.00",
    "period": "monthly"
}
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `budget_type` | string | Yes | `"total"` or `"category"` |
| `category_id` | uuid | Conditional | Required for `category` type, must be `null` for `total` |
| `amount` | decimal | Yes | Budget limit (> 0) |
| `period` | string | Yes | `"weekly"` or `"monthly"` |
| `is_active` | boolean | No | Default: `true` |

**Response (201 Created):**
```json
{
    "success": true,
    "data": {
        "id": "new-budget-uuid",
        "user_id": "user-uuid",
        "category_id": null,
        "budget_type": "total",
        "amount": "2000.00",
        "period": "monthly",
        "warning_threshold": 70,
        "last_period_surplus": "0.00",
        "is_active": true,
        "created_at": "2026-01-15T10:00:00Z",
        "updated_at": "2026-01-15T10:00:00Z"
    },
    "message": "Budget created successfully"
}
```

**Error Response (409 Conflict):**
```json
{
    "success": false,
    "error": {
        "code": "CONFLICT_ERROR",
        "message": "A monthly total budget already exists"
    }
}
```

### Update Budget

```http
PUT /api/budgets/<budget_id>
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "amount": "2500.00",
    "is_active": true
}
```

**Allowed Update Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `amount` | decimal | New budget limit |
| `period` | string | New period (may cause conflict) |
| `is_active` | boolean | Active status |

**Note:** Cannot change `budget_type` or `category_id` after creation.

### Delete Budget

```http
DELETE /api/budgets/<budget_id>
Authorization: Bearer <access_token>
```

### Get Budget Status Summary

```http
GET /api/budgets/status
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "success": true,
    "data": {
        "total_budget": {
            "has_budget": true,
            "budget_id": "budget-uuid",
            "budget_amount": "2000.00",
            "period": "monthly",
            "spent": "1400.00",
            "remaining": "600.00",
            "percentage_used": 70.0,
            "is_warning": true,
            "is_exceeded": false,
            "warning_threshold": 70,
            "last_period_surplus": "150.00"
        },
        "category_budgets_count": 5,
        "warning_budgets": [
            {
                "category_name": "Food & Dining",
                "percentage_used": 85.0,
                "remaining": "45.00"
            },
            {
                "category_name": "Entertainment",
                "percentage_used": 72.0,
                "remaining": "28.00"
            }
        ],
        "exceeded_budgets": [],
        "total_surplus_last_period": "250.00"
    },
    "message": "Budget status retrieved successfully"
}
```

### Get Category Budget Status

```http
GET /api/budgets/category/<category_id>/status
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "success": true,
    "data": {
        "has_budget": true,
        "budget_id": "budget-uuid",
        "budget_amount": "300.00",
        "period": "monthly",
        "spent": "210.00",
        "remaining": "90.00",
        "percentage_used": 70.0,
        "is_warning": true,
        "is_exceeded": false,
        "warning_threshold": 70,
        "last_period_surplus": "50.00"
    },
    "message": "Category budget status retrieved successfully"
}
```

---

## Budget Alerts Integration

### Alert Types

The system automatically creates alerts when budget thresholds are crossed:

| Alert Type | Trigger | Severity |
|------------|---------|----------|
| `budget_warning` | Spending reaches 70% | Medium |
| `budget_exceeded` | Spending reaches 100% | High |

### When Alerts Are Triggered

Alerts are automatically triggered when:
1. A new expense transaction is created
2. Spending crosses the 70% or 100% threshold

**Alert Response Example:**
```json
{
    "id": "alert-uuid",
    "alert_type": "budget_warning",
    "severity": "medium",
    "title": "Budget Warning: Food & Dining",
    "message": "You've used 75% of your monthly Food & Dining budget ($225.00 of $300.00)",
    "is_dismissed": false,
    "category_id": "food-category-uuid",
    "data": {
        "budget_id": "budget-uuid",
        "budget_amount": "300.00",
        "spent_amount": "225.00",
        "percentage_used": 75.0,
        "period": "monthly",
        "threshold": 70
    },
    "created_at": "2026-01-15T10:00:00Z"
}
```

### Get Active Alerts

```http
GET /api/alerts
Authorization: Bearer <access_token>
```

### Dismiss Alert

```http
PATCH /api/alerts/<alert_id>/dismiss
Authorization: Bearer <access_token>
```

---

## Budget Suggestions

Get AI-powered budget suggestions based on spending history.

### Get Budget Suggestions

```http
GET /api/budgets/suggestions
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "success": true,
    "data": {
        "suggestions": [
            {
                "category_id": "550e8400-e29b-41d4-a716-446655440001",
                "category_name": "Food & Dining",
                "suggested_amount": "450.00",
                "average_spending": "425.00",
                "spending_trend": "stable",
                "confidence": 0.85,
                "reasoning": "Based on 3 months of consistent spending around $400-450"
            },
            {
                "category_id": "550e8400-e29b-41d4-a716-446655440002",
                "category_name": "Transportation",
                "suggested_amount": "200.00",
                "average_spending": "175.00",
                "spending_trend": "increasing",
                "confidence": 0.78,
                "reasoning": "Spending has increased 15% over the last 2 months"
            }
        ],
        "total_suggested": "1250.00",
        "salary_percentage": 25.0,
        "analysis_period": {
            "start_date": "2025-11-01",
            "end_date": "2026-02-01",
            "months_analyzed": 3
        }
    },
    "message": "Budget suggestions generated successfully"
}
```

**Spending Trend Values:**
| Trend | Description |
|-------|-------------|
| `stable` | Spending consistent (±10%) |
| `increasing` | Spending trending up (>10%) |
| `decreasing` | Spending trending down (>10%) |
| `variable` | Spending fluctuates significantly |

---

## Categories

### Get All Categories

```http
GET /api/categories
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid-1",
            "name": "Food & Dining",
            "category_type": "expense",
            "icon": "utensils",
            "color": "#FF6B6B",
            "display_order": 1,
            "is_system": true
        },
        {
            "id": "uuid-2",
            "name": "Transportation",
            "category_type": "expense",
            "icon": "car",
            "color": "#4ECDC4",
            "display_order": 2,
            "is_system": true
        }
        // ... 11 total default categories
    ],
    "message": "Categories retrieved successfully",
    "meta": {
        "total": 11
    }
}
```

### Default Categories

| # | Name | Type | Icon |
|---|------|------|------|
| 1 | Food & Dining | expense | utensils |
| 2 | Transportation | expense | car |
| 3 | Shopping | expense | shopping-bag |
| 4 | Entertainment | expense | film |
| 5 | Bills & Utilities | expense | file-invoice |
| 6 | Healthcare | expense | medkit |
| 7 | Travel | expense | plane |
| 8 | Education | expense | graduation-cap |
| 9 | Personal Care | expense | spa |
| 10 | Income | income | wallet |
| 11 | Unknown | other | question |

---

## Custom Categories

Users can create, update, and delete custom categories in addition to system categories.

### Create Custom Category

```http
POST /api/categories
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "Side Hustle Income",
    "category_type": "income",
    "description": "Freelance and gig economy income",
    "icon": "briefcase",
    "color": "#4CAF50"
}
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Category name (1-100 chars) |
| `category_type` | string | Yes | `income`, `expense`, or `both` |
| `description` | string | No | Optional description |
| `icon` | string | No | Icon identifier |
| `color` | string | No | Hex color code (e.g., `#FF6B6B`) |

**Response (201 Created):**
```json
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440099",
        "name": "Side Hustle Income",
        "category_type": "income",
        "description": "Freelance and gig economy income",
        "icon": "briefcase",
        "color": "#4CAF50",
        "display_order": 12,
        "is_system": false,
        "user_id": "user-uuid"
    },
    "message": "Category created successfully"
}
```

**Error Response (409 Conflict):**
```json
{
    "success": false,
    "error": {
        "code": "CONFLICT_ERROR",
        "message": "A category with this name already exists"
    }
}
```

### Update Custom Category

```http
PUT /api/categories/<category_id>
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "Freelance Income",
    "description": "Updated description",
    "color": "#2196F3"
}
```

**Allowed Update Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | New category name |
| `description` | string | New description |
| `icon` | string | New icon identifier |
| `color` | string | New hex color |
| `category_type` | string | New type (income/expense/both) |

**⚠️ Important:** You can only update categories where `is_system: false` (custom categories). System categories cannot be modified.

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440099",
        "name": "Freelance Income",
        "category_type": "income",
        "description": "Updated description",
        "icon": "briefcase",
        "color": "#2196F3",
        "display_order": 12,
        "is_system": false
    },
    "message": "Category updated successfully"
}
```

**Error Response (403 Forbidden):**
```json
{
    "success": false,
    "error": {
        "code": "FORBIDDEN",
        "message": "Cannot modify system categories"
    }
}
```

### Delete Custom Category

```http
DELETE /api/categories/<category_id>
Authorization: Bearer <access_token>
```

**⚠️ Important:**
- Only custom categories (`is_system: false`) can be deleted
- Transactions using this category will be reassigned to "Unknown" category

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Category deleted successfully"
}
```

**Error Response (403 Forbidden):**
```json
{
    "success": false,
    "error": {
        "code": "FORBIDDEN",
        "message": "Cannot delete system categories"
    }
}
```

---

## Transactions

### Get Transactions

```http
GET /api/transactions
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number (1-indexed) |
| `per_page` | int | 20 | Items per page (max 100) |
| `start_date` | date | - | Filter from date (YYYY-MM-DD) |
| `end_date` | date | - | Filter to date (YYYY-MM-DD) |
| `type` | string | - | Filter by `income` or `expense` |
| `category_id` | uuid | - | Filter by category UUID |
| `category` | string | - | Filter by category name (partial match) |
| `merchant_name` | string | - | Filter by merchant (partial match) |
| `min_amount` | decimal | - | Filter minimum amount |
| `max_amount` | decimal | - | Filter maximum amount |
| `sort_by` | string | date | Sort field: `date`, `amount`, `merchant_name` |
| `sort_order` | string | desc | Sort order: `asc` or `desc` |

**Filter Examples:**

```http
# Filter by category ID
GET /api/transactions?category_id=550e8400-e29b-41d4-a716-446655440001

# Filter by category name (case-insensitive partial match)
GET /api/transactions?category=Food

# Filter by merchant name (case-insensitive partial match)
GET /api/transactions?merchant_name=starbucks

# Combine multiple filters
GET /api/transactions?category=Food&merchant_name=mcdonald&start_date=2026-01-01
```

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": "txn-uuid",
            "amount": "45.00",
            "description": "Lunch",
            "merchant_name": "Restaurant ABC",
            "transaction_type": "expense",
            "category": {
                "id": "category-uuid",
                "name": "Food & Dining"
            },
            "date": "2026-01-15",
            "created_at": "2026-01-15T12:00:00Z"
        }
    ],
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 150,
        "total_pages": 8
    },
    "message": "Transactions retrieved successfully"
}
```

### Create Transaction (Triggers Budget Alert)

```http
POST /api/transactions
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "amount": "45.00",
    "description": "Lunch at restaurant",
    "merchant_name": "Restaurant ABC",
    "transaction_type": "expense",
    "category_id": "food-category-uuid",
    "date": "2026-01-15"
}
```

**Note:** Creating an expense transaction will automatically check budget thresholds and may create alerts.

---

## AI Features

The AI system provides intelligent features for categorization, chat, and insights.

### AI Health Check

```http
GET /api/v1/ai/health
```

**Response:**
```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "ai_components": {
            "categorizer": { "status": "ready" },
            "intent_classifier": { "status": "ready" },
            "guardrails": { "status": "ready" },
            "anomaly_detector": { "status": "ready" },
            "rag_engine": { "status": "ready" },
            "recurring_detector": { "status": "ready" }
        }
    }
}
```

### Chat with AI

```http
POST /api/v1/ai/chat
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "message": "How much did I spend on food last month?",
    "session_id": "optional-session-uuid"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "response": "Based on your transactions, you spent $450.00 on food last month...",
        "session_id": "session-uuid",
        "intent": "spending_summary",
        "confidence": 0.92
    }
}
```

### AI-Powered Categorization

```http
POST /api/v1/ai/categorize
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "merchant_name": "STARBUCKS",
    "amount": 5.75,
    "description": "Coffee purchase"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "category": "Food & Dining",
        "category_id": "uuid",
        "confidence": 0.95,
        "source": "huggingface"
    }
}
```

### RAG Query (Natural Language Transaction Search)

```http
POST /api/v1/ai/rag/query
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "query": "coffee purchases",
    "limit": 5
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "transactions": [
            {
                "transaction_id": "uuid",
                "merchant_name": "Starbucks",
                "category_name": "Food & Dining",
                "amount": 5.75,
                "similarity": 0.92
            }
        ]
    }
}
```

---

## AI Chat History

Retrieve conversation history for the AI chat feature.

### Get Chat History

```http
GET /api/ai/history
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `per_page` | int | 20 | Items per page (max 100) |
| `session_id` | uuid | - | Filter by specific session |

**Response:**
```json
{
    "success": true,
    "data": {
        "conversations": [
            {
                "id": "conv-uuid-1",
                "session_id": "session-uuid",
                "user_message": "How much did I spend on food?",
                "ai_response": "Based on your transactions, you spent $450 on food this month...",
                "intent": "spending_summary",
                "confidence": 0.92,
                "created_at": "2026-02-03T10:30:00Z"
            },
            {
                "id": "conv-uuid-2",
                "session_id": "session-uuid",
                "user_message": "What about last month?",
                "ai_response": "Last month you spent $380 on food, which is $70 less than this month...",
                "intent": "spending_comparison",
                "confidence": 0.88,
                "created_at": "2026-02-03T10:31:00Z"
            }
        ]
    },
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 45,
        "total_pages": 3
    },
    "message": "Chat history retrieved successfully"
}
```

### Get Session Conversations

Retrieve all messages from a specific chat session:

```http
GET /api/ai/history?session_id=session-uuid-here
Authorization: Bearer <access_token>
```

**Use Cases:**
- Display previous AI conversations in chat interface
- Allow users to continue previous sessions
- Show conversation context for debugging

---

## Recurring Transactions

Detect and track recurring transactions like subscriptions and bills.

### Get Recurring Patterns

```http
GET /api/v1/ai/recurring
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "success": true,
    "data": {
        "patterns": [
            {
                "merchant_name": "Netflix",
                "category_name": "Entertainment",
                "average_amount": 15.99,
                "interval": "monthly",
                "confidence": 0.95,
                "status": "active",
                "transaction_count": 6,
                "next_expected_date": "2026-02-15",
                "days_until_next": 19
            },
            {
                "merchant_name": "Spotify",
                "category_name": "Entertainment",
                "average_amount": 9.99,
                "interval": "monthly",
                "confidence": 0.92,
                "status": "active",
                "transaction_count": 8,
                "next_expected_date": "2026-02-01",
                "days_until_next": 5
            }
        ]
    }
}
```

### Get Upcoming Bills

```http
GET /api/v1/ai/recurring/upcoming?days=30
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | integer | 30 | Days to look ahead |

**Response:**
```json
{
    "success": true,
    "data": {
        "upcoming": [
            {
                "merchant_name": "Spotify",
                "expected_amount": 9.99,
                "expected_date": "2026-02-01",
                "days_until": 5
            },
            {
                "merchant_name": "Netflix",
                "expected_amount": 15.99,
                "expected_date": "2026-02-15",
                "days_until": 19
            }
        ],
        "total_expected": 25.98
    }
}
```

### Get Missed Payments

```http
GET /api/v1/ai/recurring/missed
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "success": true,
    "data": {
        "missed": [
            {
                "merchant_name": "Gym Membership",
                "expected_amount": 29.99,
                "expected_date": "2026-01-15",
                "days_overdue": 12
            }
        ]
    }
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | User lacks permission |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT_ERROR` | 409 | Resource already exists |
| `INTERNAL_ERROR` | 500 | Server error |

**Error Response Format:**
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "User-friendly error message",
        "details": {
            "field_name": ["Error detail"]
        }
    }
}
```

---

## Frontend Implementation Checklist

### Post-Login Flow
- [ ] Call `POST /api/auth/callback` after Auth0 login
- [ ] Check `is_new_user` flag in response
- [ ] Check `account_status` field
- [ ] If `is_new_user: true` AND `account_status: "pending"`:
  - [ ] Show onboarding questionnaire
  - [ ] Collect `first_name`, `last_name`, `salary_amount`
  - [ ] Call `PATCH /api/users/me` to update profile
  - [ ] Verify `account_status` changed to `"active"`
- [ ] Redirect to dashboard

### Budget Dashboard
- [ ] Call `GET /api/budgets` to fetch all budgets with spending
- [ ] Display budget cards with progress bars
- [ ] Color code based on `is_warning` and `is_exceeded` flags
- [ ] Show `percentage_used` as percentage
- [ ] Show `remaining` amount

### Budget Creation
- [ ] Allow selection of `budget_type` (total/category)
- [ ] If category: Show category dropdown
- [ ] Allow input of `amount`
- [ ] Allow selection of `period` (weekly/monthly)
- [ ] Handle 409 conflict error (budget already exists)

### Alert Display
- [ ] Poll `GET /api/alerts` periodically
- [ ] Show budget warning/exceeded alerts prominently
- [ ] Allow dismissing alerts via `PATCH /api/alerts/<id>/dismiss`

### AI Chat Integration
- [ ] Implement chat interface for AI assistant
- [ ] Call `POST /api/v1/ai/chat` with user messages
- [ ] Maintain session_id for conversation continuity
- [ ] Display AI responses with confidence indicators
- [ ] Handle different intents (spending_summary, add_transaction, etc.)

### Recurring Transactions
- [ ] Call `GET /api/v1/ai/recurring` for detected subscriptions
- [ ] Display list with merchant, amount, interval
- [ ] Call `GET /api/v1/ai/recurring/upcoming` for upcoming bills
- [ ] Show calendar/timeline view of expected payments
- [ ] Alert on missed payments via `GET /api/v1/ai/recurring/missed`

### Custom Categories
- [ ] Display custom categories alongside system categories
- [ ] Show `is_system: false` badge for user-created categories
- [ ] Implement "Create Category" form with name, type, color, icon
- [ ] Call `POST /api/categories` to create custom categories
- [ ] Allow editing custom categories via `PUT /api/categories/<id>`
- [ ] Allow deleting custom categories via `DELETE /api/categories/<id>`
- [ ] Handle 403 error when trying to modify system categories
- [ ] Handle 409 conflict error for duplicate names

### Budget Suggestions
- [ ] Call `GET /api/budgets/suggestions` to get AI-powered suggestions
- [ ] Display suggested amounts per category
- [ ] Show spending trends (stable/increasing/decreasing/variable)
- [ ] Show confidence levels for suggestions
- [ ] Allow one-click budget creation from suggestions

### AI Chat History
- [ ] Call `GET /api/ai/history` to retrieve past conversations
- [ ] Display conversation history in chat interface
- [ ] Allow filtering by session_id for specific conversations
- [ ] Implement pagination for large history

### Transaction Filters
- [ ] Add category dropdown filter (by name) on transactions page
- [ ] Add category_id filter for precise category matching
- [ ] Add merchant name search/filter field
- [ ] Combine multiple filters for advanced search

---
