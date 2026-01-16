# Frontend API Integration Guide

## Overview

This document provides comprehensive API documentation for the frontend team to integrate with the backend services. It covers all recent implementations including user authentication flow, profile management, and the new budget system.

---

## Table of Contents

1. [Authentication & User Onboarding Flow](#authentication--user-onboarding-flow)
2. [User Profile Management](#user-profile-management)
3. [Budget System](#budget-system)
4. [Categories](#categories)
5. [Transactions](#transactions)
6. [Alerts & Notifications](#alerts--notifications)

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

## Transactions

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

---
