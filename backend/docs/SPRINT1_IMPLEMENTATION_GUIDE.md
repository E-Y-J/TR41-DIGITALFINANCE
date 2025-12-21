# Sprint 1 Backend Implementation Guide

Sprint 1 - Schema & Migrations

---

## 🆕 Latest Updates

### Swagger UI Added
Interactive API documentation is now available:

| Resource | URL |
|----------|-----|
| **Swagger UI** | http://localhost:5000/api/docs |
| **OpenAPI JSON** | http://localhost:5000/api/docs/openapi.json |

**New Files:**
- `app/api/swagger.py` - Swagger configuration and OpenAPI spec

---

## 📋 Summary

Sprint 1 focused on implementing the **database layer** and **core API endpoints** for the Digital Finance Tracker backend. This includes:

1. ✅ PostgreSQL database setup with migrations
2. ✅ Users and Transactions tables per ERD specifications
3. ✅ Transaction CRUD endpoints (6 endpoints)
4. ✅ Auth0 authentication endpoints (4 endpoints)
5. ✅ User endpoints (already existed, verified working)

---

## 🏗️ What Was Implemented

### Database Tables

#### `users` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | Primary key |
| `auth0_id` | VARCHAR(128) | UNIQUE, NOT NULL | Auth0 subject ID |
| `email` | VARCHAR(255) | UNIQUE | User's email |
| `email_verified` | BOOLEAN | NOT NULL, default FALSE | Email verification status |
| `first_name` | VARCHAR(255) | NOT NULL | User's first name |
| `last_name` | VARCHAR(255) | NOT NULL | User's last name |
| `nickname` | VARCHAR(100) | NULLABLE | Display name |
| `picture` | TEXT | NULLABLE | Profile picture URL |
| `settings` | JSONB | NOT NULL, default {} | User preferences |
| `account_status` | ENUM | NOT NULL, default 'PENDING' | PENDING, ACTIVE, SUSPENDED |
| `role` | ENUM | NOT NULL, default 'USER' | USER, ADMIN |
| `salary_amount` | DECIMAL(12,2) | NOT NULL, default 0.00 | Monthly salary |
| `created_at` | TIMESTAMPTZ | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Last update timestamp |
| `last_login` | TIMESTAMPTZ | NULLABLE | Last login timestamp |

**Indexes:**
- `ix_users_auth0_id` (UNIQUE) - Fast Auth0 lookup
- `ix_users_email` (UNIQUE) - Fast email lookup
- `ix_users_account_status` - Filter by status
- `ix_users_role` - Filter by role

#### `transactions` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | Primary key |
| `user_id` | UUID | FK → users.id, ON DELETE CASCADE | Owner |
| `amount` | DECIMAL(12,2) | NOT NULL | Transaction amount |
| `transaction_type` | ENUM | NOT NULL | INCOME, EXPENSE |
| `date` | VARCHAR(50) | NOT NULL | Transaction date (YYYY-MM-DD) |
| `merchant_name` | VARCHAR(255) | NULLABLE | Merchant or source |
| `category` | VARCHAR(100) | NULLABLE | Category label |
| `created_at` | TIMESTAMPTZ | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Last update timestamp |

**Indexes:**
- `ix_transactions_user_id` - Filter by user
- `ix_transactions_date` - Filter/sort by date
- `ix_transactions_category` - Filter by category
- `ix_transactions_transaction_type` - Filter by type
- `idx_transaction_user_date` (COMPOSITE) - User + date queries
- `idx_transaction_user_category` (COMPOSITE) - User + category queries

**Cascade Delete:** When a user is deleted, all their transactions are automatically deleted.

---

## 🔌 API Endpoints

### Base URL
```
Development: http://localhost:5001/api
```

### Authentication Flow (Auth0)

```
┌──────────────────────────────────────────────────────────────────────┐
│                        AUTH0 AUTHENTICATION FLOW                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Frontend redirects to Auth0 Universal Login                      │
│                     ↓                                                │
│  2. User logs in via Auth0 (email/password, Google, etc.)            │
│                     ↓                                                │
│  3. Auth0 redirects back to frontend with tokens                     │
│                     ↓                                                │
│  4. Frontend calls POST /api/auth/callback with access_token         │
│                     ↓                                                │
│  5. Backend validates token, syncs user to database                  │
│                     ↓                                                │
│  6. Frontend stores token, uses for all API requests                 │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Auth Endpoints (`/api/auth`)

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `POST` | `/callback` | ✅ Yes | Sync Auth0 user to database after login |
| `GET` | `/me` | ✅ Yes | Get current authenticated user info |
| `POST` | `/logout` | ❌ No | Get logout instructions (client-side) |
| `GET` | `/status` | ⚪ Optional | Check authentication status |

### User Endpoints (`/api/users`)

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `GET` | `/` | ✅ Yes | List all users (admin only) |
| `GET` | `/me` | ✅ Yes | Get current user profile |
| `GET` | `/:id` | ✅ Yes | Get user by ID |
| `PATCH` | `/me` | ✅ Yes | Update current user profile |
| `DELETE` | `/me` | ✅ Yes | Soft delete current user |

### Transaction Endpoints (`/api/transactions`)

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `GET` | `/` | ✅ Yes | List user's transactions (paginated) |
| `POST` | `/` | ✅ Yes | Create new transaction |
| `GET` | `/:id` | ✅ Yes | Get single transaction |
| `PATCH` | `/:id` | ✅ Yes | Update transaction |
| `DELETE` | `/:id` | ✅ Yes | Delete transaction |
| `GET` | `/summary` | ✅ Yes | Get income/expense summary |

---

## 📝 Request/Response Examples

### Create Transaction
```http
POST /api/transactions
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "amount": "125.50",
    "transaction_type": "expense",
    "date": "2025-12-19",
    "merchant_name": "Amazon",
    "category": "Shopping"
}
```

**Response (201 Created):**
```json
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "660e8400-e29b-41d4-a716-446655440001",
        "amount": "125.50",
        "transaction_type": "expense",
        "date": "2025-12-19",
        "merchant_name": "Amazon",
        "category": "Shopping",
        "created_at": "2025-12-19T21:30:00Z",
        "updated_at": "2025-12-19T21:30:00Z"
    },
    "message": "Transaction created successfully"
}
```

### List Transactions (with filters)
```http
GET /api/transactions?page=1&per_page=20&transaction_type=expense&category=Food
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid-1",
            "amount": "50.00",
            "transaction_type": "expense",
            "date": "2025-12-18",
            "merchant_name": "Grocery Store",
            "category": "Food"
        }
    ],
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 45,
        "total_pages": 3
    },
    "message": "Transactions retrieved successfully"
}
```

### Get Transaction Summary
```http
GET /api/transactions/summary
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "total_income": "5000.00",
        "total_expense": "2500.00",
        "net": "2500.00",
        "transaction_count": 45
    },
    "message": "Summary retrieved successfully"
}
```

### Error Response Format
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid transaction_type: must be 'income' or 'expense'",
        "details": {
            "field": "transaction_type",
            "received": "invalid"
        }
    }
}
```

---

## 🔐 Authentication Details

### JWT Token Structure
The backend expects Auth0 JWTs with these claims:
```json
{
    "sub": "auth0|abc123",           // Auth0 user ID (required)
    "email": "user@example.com",     // Email (optional)
    "email_verified": true,          // Email verified (optional)
    "name": "John Doe",              // Full name (optional)
    "given_name": "John",            // First name (optional)
    "family_name": "Doe",            // Last name (optional)
    "nickname": "johnd",             // Nickname (optional)
    "picture": "https://..."         // Profile picture (optional)
}
```

### How to Call Protected Endpoints
```javascript
// Frontend example
const response = await fetch('/api/transactions', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    }
});
```

### User Sync Behavior
When a user authenticates:
1. Backend extracts `sub` claim as `auth0_id`
2. Looks up user by `auth0_id` in database
3. If not found → Creates new user record
4. If found → Updates `last_login` and any changed fields
5. Returns user data

---

## 📁 Files Created/Modified

### New Files
| File | Purpose |
|------|---------|
| `app/api/routes/auth.py` | Auth0 authentication endpoints |
| `app/api/routes/transactions.py` | Transaction CRUD endpoints |
| `app/services/transaction_service.py` | Transaction business logic |
| `migrations/versions/0ef6d8b45cc5_*.py` | Initial database migration |
| `docs/SPRINT1_IMPLEMENTATION_GUIDE.md` | This documentation |

### Modified Files
| File | Changes |
|------|---------|
| `app/__init__.py` | Registered auth and transactions blueprints |
| `app/auth/user_sync.py` | Added name parsing for first_name/last_name |
| `app/services/user_service.py` | Updated to use first_name/last_name |
| `app/schemas/transaction_schema.py` | Added `transaction_list_schema` |
| `README.md` | Added API endpoint documentation |
| `SPRINT1_SCHEMA_NOTES.md` | Added implementation notes |

---

## 🧪 Testing the API

### Prerequisites
1. PostgreSQL running on `localhost:5432`
2. Database `digital_finance_db` exists
3. `.env` file configured with Auth0 settings
4. Virtual environment activated

### Start the Server
```bash
cd backend
venv\Scripts\activate  # Windows
flask run --port 5001
```

### Health Check
```bash
curl http://localhost:5001/api/health
# Expected: {"status": "healthy"}
```

### Testing with Postman
1. Import the Postman collection from `shared/postman/`
2. Set environment variables:
   - `base_url`: `http://localhost:5001`
   - `access_token`: (get from Auth0 after login)
3. Run requests in order

---

## ⚠️ Important Notes for Frontend Team

1. **Auth0 Handles Login** - The backend does NOT have `/login` or `/register` endpoints. Use Auth0 Universal Login.

2. **Always Send Bearer Token** - All protected endpoints require `Authorization: Bearer <token>` header.

3. **Call `/api/auth/callback` After Login** - After Auth0 redirects back, call this endpoint to sync user data.

4. **UUIDs for IDs** - All IDs are UUIDs (36-character strings), not integers.

5. **Decimal Strings for Money** - Amounts are returned as strings to preserve precision (e.g., `"125.50"` not `125.5`).

6. **Pagination** - List endpoints return max 100 items per page. Use `page` and `per_page` query params.

---

## 🔜 Next Steps (Sprint 2/3)

- [ ] Budget endpoints
- [ ] Recurring transactions
- [ ] Financial goals
- [ ] AI insights integration
- [ ] Notifications
- [ ] Charts/reports data endpoints

---

## 📞 Contact

**Backend Team:** Suryadi Zhang (suryadizhang86@gmail.com)

For questions about:
- API behavior → Backend team
- Auth0 setup → Check `docs/FRONTEND_AUTH_INTEGRATION.md`
- Postman collection → `shared/postman/`
