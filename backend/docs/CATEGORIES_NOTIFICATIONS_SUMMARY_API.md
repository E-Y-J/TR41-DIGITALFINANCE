# Categories, Notifications & Summary API Documentation

> **Status:** Foundation Complete
> **For:** Frontend Team, QA (Swagger & Postman Updates)
> **Last Updated:** January 7, 2026

---

## 📋 Overview

This document describes the API endpoints for:
- **Categories** - Transaction categorization (11 defaults)
- **Notifications** - User notification system (6 types)
- **Alerts** - Financial anomaly alerts (foundation)
- **Summary** - Spending summaries (daily/weekly/monthly/yearly/ytd)

All endpoints require **Auth0 authentication** via Bearer token.

---

## 🔐 Authentication

All endpoints require the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Unauthorized requests return:
```json
{
    "success": false,
    "error": {
        "code": "UNAUTHORIZED",
        "message": "Missing or invalid authorization token"
    }
}
```

---

## 📁 Categories API

### GET `/api/categories`

Get all transaction categories.

**Request:**
```
GET /api/categories
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Categories retrieved successfully",
    "data": [
        {
            "id": "uuid-string",
            "name": "Food & Dining",
            "description": "Restaurants, groceries, fast food, coffee shops, food delivery",
            "category_type": "expense",
            "is_system": true,
            "display_order": 1
        },
        {
            "id": "uuid-string",
            "name": "Transportation",
            "description": "Gas, rideshare, airlines, public transport, car rental",
            "category_type": "expense",
            "is_system": true,
            "display_order": 2
        }
        // ... 11 categories total
    ]
}
```

**Category Types:**
| Type | Description |
|------|-------------|
| `income` | Income transactions only |
| `expense` | Expense transactions only |
| `both` | Both income and expense |

**Default Categories (11):**
| # | Name | Type | Order |
|---|------|------|-------|
| 1 | Food & Dining | expense | 1 |
| 2 | Transportation | expense | 2 |
| 3 | Shopping & Retail | expense | 3 |
| 4 | Entertainment & Recreation | expense | 4 |
| 5 | Healthcare & Medical | expense | 5 |
| 6 | Utilities & Services | expense | 6 |
| 7 | Financial Services | both | 7 |
| 8 | Income | income | 8 |
| 9 | Government & Legal | both | 9 |
| 10 | Charity & Donations | expense | 10 |
| 11 | Unknown | both | 99 |

---

### GET `/api/categories/{id}`

Get a single category by ID.

**Request:**
```
GET /api/categories/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Category retrieved successfully",
    "data": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Food & Dining",
        "description": "Restaurants, groceries, fast food, coffee shops, food delivery",
        "category_type": "expense",
        "is_system": true,
        "display_order": 1
    }
}
```

**Error Response (404 Not Found):**
```json
{
    "success": false,
    "error": {
        "code": "NOT_FOUND",
        "message": "Category not found"
    }
}
```

---

## 🔔 Notifications API

### GET `/api/notifications`

Get paginated list of user's notifications.

**Request:**
```
GET /api/notifications?page=1&per_page=20&status=unread
Authorization: Bearer <token>
```

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number (1-indexed) |
| `per_page` | int | 20 | Items per page (max 100) |
| `status` | string | all | Filter: `unread`, `read`, or omit for all |
| `type` | string | all | Filter by notification type |

**Notification Types (6):**
| Type | Trigger |
|------|---------|
| `default` | Generic/system notification |
| `new_transaction` | Transaction created |
| `deleted_transaction` | Transaction deleted |
| `edited_profile` | Profile updated |
| `weekly_summary_ready` | Weekly summary available |
| `category_updated` | Transaction category changed |

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Notifications retrieved successfully",
    "data": [
        {
            "id": "uuid-string",
            "user_id": "uuid-string",
            "type": "new_transaction",
            "status": "unread",
            "message": "New transaction: $50.00 in Food & Dining",
            "data": {
                "transaction_id": "txn-uuid"
            },
            "created_at": "2026-01-07T10:30:00Z"
        }
    ],
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 5,
        "total_pages": 1,
        "has_next": false,
        "has_prev": false
    }
}
```

---

### GET `/api/notifications/{id}`

Get a single notification by ID.

**Request:**
```
GET /api/notifications/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Notification retrieved",
    "data": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "user_id": "uuid-string",
        "type": "new_transaction",
        "status": "unread",
        "message": "New transaction: $50.00 in Food & Dining",
        "data": {
            "transaction_id": "txn-uuid"
        },
        "created_at": "2026-01-07T10:30:00Z"
    }
}
```

---

### GET `/api/notifications/unread-count`

Get count of unread notifications.

**Request:**
```
GET /api/notifications/unread-count
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Unread count retrieved",
    "data": {
        "unread_count": 5
    }
}
```

---

### PATCH `/api/notifications/{id}/read`

Mark a single notification as read.

**Request:**
```
PATCH /api/notifications/123e4567-e89b-12d3-a456-426614174000/read
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Notification marked as read",
    "data": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "status": "read"
    }
}
```

---

### PATCH `/api/notifications/read-all`

Mark all notifications as read.

**Request:**
```
PATCH /api/notifications/read-all
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "All notifications marked as read",
    "data": {
        "count": 5
    }
}
```

---

### DELETE `/api/notifications/{id}`

Delete a notification.

**Request:**
```
DELETE /api/notifications/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Notification deleted"
}
```

---

## ⚠️ Alerts API

### GET `/api/alerts`

Get paginated list of user's alerts.

**Request:**
```
GET /api/alerts?page=1&per_page=20&include_dismissed=false
Authorization: Bearer <token>
```

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `per_page` | int | 20 | Items per page (max 100) |
| `include_dismissed` | bool | false | Include dismissed alerts |
| `alert_type` | string | all | Filter by type |
| `severity` | string | all | Filter by severity |

**Alert Types:**
| Type | Description |
|------|-------------|
| `high_spending` | Spending exceeds baseline |
| `large_transaction` | Single transaction exceeds threshold |
| `unusual_category` | Unusual spending pattern |
| `budget_warning` | Approaching budget limit |
| `budget_exceeded` | Budget exceeded |

**Severity Levels:**
| Level | Description |
|-------|-------------|
| `low` | Informational |
| `medium` | Notable, should review |
| `high` | Significant, requires attention |
| `critical` | Urgent issue |

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Alerts retrieved successfully",
    "data": [
        {
            "id": "uuid-string",
            "user_id": "uuid-string",
            "alert_type": "high_spending",
            "severity": "medium",
            "title": "High Spending: Food & Dining",
            "message": "Your spending in Food & Dining is 2.5x your usual",
            "is_dismissed": false,
            "dismissed_at": null,
            "transaction_id": null,
            "category_id": "category-uuid",
            "data": {
                "current_amount": 500.00,
                "baseline_amount": 200.00,
                "multiplier": 2.5
            },
            "created_at": "2026-01-07T10:30:00Z"
        }
    ],
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 3,
        "total_pages": 1,
        "has_next": false,
        "has_prev": false
    }
}
```

---

### GET `/api/alerts/count`

Get count of active (undismissed) alerts.

**Request:**
```
GET /api/alerts/count
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Active alert count retrieved",
    "data": {
        "active_count": 3
    }
}
```

---

### PATCH `/api/alerts/{id}/dismiss`

Dismiss a single alert.

**Request:**
```
PATCH /api/alerts/123e4567-e89b-12d3-a456-426614174000/dismiss
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Alert dismissed",
    "data": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "is_dismissed": true,
        "dismissed_at": "2026-01-07T15:00:00Z"
    }
}
```

---

### PATCH `/api/alerts/dismiss-all`

Dismiss all active alerts.

**Request:**
```
PATCH /api/alerts/dismiss-all
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "All alerts dismissed",
    "data": {
        "count": 3
    }
}
```

---

## 📊 Summary API

### GET `/api/summary/daily`

Get daily spending summary (today).

**Request:**
```
GET /api/summary/daily?date=2026-01-07
Authorization: Bearer <token>
```

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `date` | string | today | Reference date (YYYY-MM-DD) |

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Daily summary retrieved",
    "data": {
        "period": "daily",
        "start_date": "2026-01-07",
        "end_date": "2026-01-07",
        "total_income": 0.00,
        "total_expense": 75.50,
        "net": -75.50,
        "transaction_count": 3,
        "category_breakdown": [
            {
                "category_id": "uuid",
                "name": "Food & Dining",
                "amount": 45.00,
                "percentage": 59.60,
                "transaction_count": 2
            },
            {
                "category_id": "uuid",
                "name": "Transportation",
                "amount": 30.50,
                "percentage": 40.40,
                "transaction_count": 1
            }
        ],
        "top_categories": [...]
    }
}
```

---

### GET `/api/summary/weekly`

Get weekly spending summary (last 7 days).

**Request:**
```
GET /api/summary/weekly
Authorization: Bearer <token>
```

**Response:** Same structure as daily.

---

### GET `/api/summary/monthly`

Get monthly spending summary (current month).

**Request:**
```
GET /api/summary/monthly
Authorization: Bearer <token>
```

**Response:** Same structure as daily.

---

### GET `/api/summary/yearly`

Get yearly spending summary (current year).

**Request:**
```
GET /api/summary/yearly
Authorization: Bearer <token>
```

**Response:** Same structure as daily.

---

### GET `/api/summary/ytd`

Get year-to-date summary (Jan 1 to today).

**Request:**
```
GET /api/summary/ytd
Authorization: Bearer <token>
```

**Response:** Same structure as daily.

---

### GET `/api/summary/by-category`

Get category breakdown for a period.

**Request:**
```
GET /api/summary/by-category?period=monthly&type=expense
Authorization: Bearer <token>
```

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `period` | string | weekly | `daily`, `weekly`, `monthly`, `yearly`, `ytd` |
| `type` | string | expense | `income` or `expense` |

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Category breakdown retrieved",
    "data": [
        {
            "category_id": "uuid",
            "name": "Food & Dining",
            "amount": 450.00,
            "percentage": 35.50,
            "transaction_count": 15
        },
        {
            "category_id": "uuid",
            "name": "Transportation",
            "amount": 200.00,
            "percentage": 15.75,
            "transaction_count": 8
        }
    ]
}
```

---

### GET `/api/summary/trends`

Get spending trends over multiple periods.

**Request:**
```
GET /api/summary/trends?period=monthly&num_periods=6
Authorization: Bearer <token>
```

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `period` | string | monthly | `weekly` or `monthly` |
| `num_periods` | int | 6 | Number of periods (max 12) |

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Spending trends retrieved",
    "data": [
        {
            "period_start": "2025-08-01",
            "period_end": "2025-08-31",
            "period_label": "Aug 2025",
            "total_income": 5000.00,
            "total_expense": 3200.00,
            "net": 1800.00
        },
        {
            "period_start": "2025-09-01",
            "period_end": "2025-09-30",
            "period_label": "Sep 2025",
            "total_income": 5000.00,
            "total_expense": 2800.00,
            "net": 2200.00
        }
        // ... up to num_periods
    ]
}
```

---

### GET `/api/summary/compare`

Compare current period with previous period.

**Request:**
```
GET /api/summary/compare?period=monthly
Authorization: Bearer <token>
```

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `period` | string | weekly | `weekly` or `monthly` |

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Period comparison retrieved",
    "data": {
        "current_period": {
            "start_date": "2026-01-01",
            "end_date": "2026-01-07",
            "total_expense": 850.00,
            "total_income": 2500.00
        },
        "previous_period": {
            "start_date": "2025-12-01",
            "end_date": "2025-12-31",
            "total_expense": 1200.00,
            "total_income": 5000.00
        },
        "expense_change": -350.00,
        "expense_change_percent": -29.17,
        "trend": "down"
    }
}
```

---

## ❌ Error Responses

All endpoints follow this error format:

```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable message",
        "details": {}
    }
}
```

**Common Error Codes:**
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Access denied to resource |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Invalid request data |
| `INTERNAL_ERROR` | 500 | Server error |

---

## 📝 Notes for Swagger/Postman

1. **Base URL:** `http://localhost:5000/api` (development)
2. **Auth:** Use Auth0 Bearer token for all protected endpoints
3. **UUIDs:** All IDs are UUID v4 format
4. **Dates:** ISO 8601 format (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`)
5. **Pagination:** Uses `page` and `per_page` with max 100 items

---

## 🧪 Test Coverage

All endpoints have integration tests in:
`backend/tests/integration/test_sprint2_endpoints.py`

Run tests:
```bash
cd backend
pytest tests/integration/test_sprint2_endpoints.py -v
```

**Result:** 21 tests passing ✅

---

## 👥 Contact

Questions about these endpoints:
- **Backend:** See README.md for team contacts
- **Frontend:** See README.md for team contacts
