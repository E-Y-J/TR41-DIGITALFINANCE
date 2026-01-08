# Backend - AI Digital Finance Tracker

Flask-based REST API for the AI Digital Finance Tracker application.

## 🎯 Project Overview

This backend supports a cloud-based finance tracker that:
- Centralizes income, expenses, and e-wallet balances
- Provides AI-powered transaction categorization
- Generates spending insights and predictions
- Supports cross-device sync with authenticated accounts

---

## 📊 Database Design & ERD

### Entity Relationship Diagram

The ERD for the database architecture is located at:
📁 **Path:** `backend/ERD.png`

![ERD](ERD.png)

---

### Understanding the User-Transaction Relationship

**Relationship Type:** One-to-Many (1:N)

**Cardinality & Ordinality:**

| Entity | Min (Ordinality) | Max | Meaning |
|--------|------------------|-----|---------|
| **User** (left side) | 1 | 1 | Every transaction MUST belong to exactly one user |
| **Transaction** (right side) | 0 | Many | A user can have zero transactions (new account) or unlimited transactions |

**Ordinality Explained:**
- **Min = 0 (optional):** New users can exist without any transactions
- **Min = 1 (mandatory):** Every transaction must have exactly one user (enforced by NOT NULL foreign key)

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | Flask, Flask-SQLAlchemy, Flask-Migrate |
| Database | PostgreSQL |
| Auth | Auth0 (token validation via python-jose) |
| Validation | Marshmallow |
| AI/ML | scikit-learn, pandas, numpy |
| Charts | matplotlib, plotly |
| Caching | Flask-Caching (Redis) |
| Rate Limiting | Flask-Limiter (Redis) |
| Monitoring | Sentry |
| Testing | pytest |
| Server | Gunicorn |

---

## 📁 Folder Structure & Where to Create Files

### `app/api/routes/`
**Purpose:** HTTP endpoints (Flask Blueprints)
**Create here:** New API route files

| File | Description | Sprint |
|------|-------------|--------|
| `auth.py` | `/api/auth/register`, `/api/auth/login`, `/api/auth/logout` | Sprint 1 |
| `users.py` | `/api/users/me`, `/api/users/profile` | Sprint 1 |
| `transactions.py` | CRUD `/api/transactions` | Sprint 2 |
| `dashboard.py` | `/api/dashboard/summary`, `/api/dashboard/categories` | Sprint 2 |
| `ai.py` | `/api/ai/categorize`, `/api/ai/chat`, `/api/ai/alerts` | Sprint 2-3 |
| `notifications.py` | `/api/notifications` | Sprint 2 |

**Rule:** Routes should be thin - call services, don't write business logic here.

---

### `app/auth/`
**Purpose:** Auth0 integration & token validation
**Create here:** Auth0-specific logic for backend

| File | Description |
|------|-------------|
| `auth0.py` | Auth0 token validation, JWKS fetching |
| `decorators.py` | `@requires_auth` decorator for protected routes |
| `user_sync.py` | Sync Auth0 user to local database |

> **Note:** Frontend handles Auth0 login UI. Backend only validates tokens and syncs user data.

---

### `app/core/`
**Purpose:** Infrastructure & configuration
**Create here:** Config, extensions, middleware

| File | Description |
|------|-------------|
| `config.py` | Environment variables, app settings, Auth0 config |
| `extensions.py` | Initialize db, cache, limiter |
| `middleware.py` | Request logging, error handlers, CORS |

---

### `app/models/`
**Purpose:** SQLAlchemy database models
**Create here:** One file per database table

| File | Table | Key Fields |
|------|-------|------------|
| `user.py` | `users` | id, auth0_id, email, first_name, last_name, created_at |
| `transaction.py` | `transactions` | id, user_id, amount, type (credit/debit), description, category_id, date |
| `category.py` | `categories` | id, name, is_default, user_id (nullable for defaults) |
| `notification.py` | `notifications` | id, user_id, message, is_read, created_at |
| `budget.py` | `budgets` | id, user_id, category_id, amount, period | (Sprint 3 - Nice to Have)

> **Note:** With Auth0, we don't store passwords. `auth0_id` links to Auth0 user.

---

### `app/schemas/`
**Purpose:** Marshmallow schemas for request/response validation
**Create here:** Schema files matching your routes

| File | Description |
|------|-------------|
| `user_schema.py` | UserSchema, ProfileUpdateSchema, Auth0UserSchema |
| `transaction_schema.py` | TransactionSchema, TransactionCreateSchema |
| `dashboard_schema.py` | SummarySchema, CategoryBreakdownSchema |
| `ai_schema.py` | CategorizationSchema, ChatQuerySchema, AlertSchema |
| `notification_schema.py` | NotificationSchema |

---

### `app/services/`
**Purpose:** Business logic layer
**Create here:** Service functions that routes call

| File | Handles |
|------|---------|
| `user_service.py` | Profile CRUD, user preferences, Auth0 user sync |
| `transaction_service.py` | Transaction CRUD, CSV export |
| `dashboard_service.py` | Spending summary (daily/weekly/monthly/yearly), category totals |
| `ai_service.py` | Orchestrates AI features, calls ai/ modules |
| `notification_service.py` | Create/read notifications, mark as read |

**Rule:** All complex logic goes here, not in routes.

---

### `app/ai/`
**Purpose:** AI/ML modules
**Create here:** All AI-related logic

| File | Feature | Description |
|------|---------|-------------|
| `categorize.py` | AI Categorization | Auto-categorize transactions based on description |
| `alerts.py` | Smart Spending Alert | Detect unusual spending patterns |
| `chatbot.py` | AI Chatbot Q&A | Answer queries like "How much did I spend on food?" |
| `recommendations.py` | Saving Recommendations | Suggest expense cuts (Stretch Goal) |
| `train.py` | Model Training | Train/retrain categorization model |
| `preprocess.py` | Data Preprocessing | Clean and prepare data for AI |

---

### `app/ai/model_store/`
**Purpose:** Trained model files
**Create here:** `.pkl` files, `metrics.json`

| File | Description |
|------|-------------|
| `categorizer.pkl` | Trained categorization model |
| `metrics.json` | Model accuracy, training date, version |

**Rule:** Large models are in `.gitignore`. Use Git LFS for versioning if needed.

---

### `app/charts/`
**Purpose:** Backend chart generation for spending summaries and exports
**Create here:** Chart generation functions using matplotlib/plotly

| File | Chart Type |
|------|------------|
| `spending_charts.py` | Pie/donut charts for spending by category |
| `trend_charts.py` | Line charts for spending over time |
| `budget_charts.py` | Progress bars for budget goals |
| `export.py` | Generate chart images for PDF/CSV export |

**Output formats:**
- Base64 encoded images (for API response)
- PNG/SVG files (for PDF export)

---

### `app/utils/`
**Purpose:** Shared utility functions
**Create here:** Helpers used across multiple modules

| File | Description |
|------|-------------|
| `errors.py` | Custom exception classes, error response formatters |
| `validators.py` | Input validation helpers |
| `helpers.py` | Date formatting, pagination, common utilities |

---

### `migrations/versions/`
**Purpose:** Alembic database migrations
**Create here:** Auto-generated by `flask db migrate`

**Commands:**
```bash
flask db init          # First time only
flask db migrate -m "description"
flask db upgrade
```

**Rule:** Review auto-generated migrations before applying.

---

### `tests/unit/`
**Purpose:** Unit tests
**Create here:** Test files matching your modules

| File | Tests |
|------|-------|
| `test_auth_service.py` | Registration, login, password hashing |
| `test_transaction_service.py` | CRUD operations |
| `test_ai_categorize.py` | Categorization accuracy |

---

### `tests/integration/`
**Purpose:** Integration/API tests
**Create here:** Tests that hit actual endpoints

| File | Tests |
|------|-------|
| `test_auth_routes.py` | `/api/auth/*` endpoints |
| `test_transactions_api.py` | `/api/transactions/*` endpoints |
| `test_dashboard_api.py` | `/api/dashboard/*` endpoints |

---

## 🚀 Quick Reference

| I need to... | Create file in... |
|--------------|-------------------|
| Add new API endpoint | `app/api/routes/` |
| Add database table | `app/models/` |
| Add business logic | `app/services/` |
| Add request validation | `app/schemas/` |
| Add AI feature | `app/ai/` |
| Add chart generation | `app/charts/` |
| Add Auth0 logic | `app/auth/` |
| Add config/env vars | `app/core/config.py` |
| Write tests | `tests/unit/` or `tests/integration/` |

> **📖 For detailed folder explanations, see [STRUCTURE.md](STRUCTURE.md)**

---

## 📋 Sprint Tasks Mapping

### Sprint 1 - Authentication & Setup (Auth0) ✅ COMPLETED
- [x] `app/core/config.py` - Environment configuration (Auth0 settings) ✅
- [x] `app/core/extensions.py` - Initialize Flask extensions ✅
- [x] `app/auth/auth0.py` - Auth0 token validation ✅
- [x] `app/auth/decorators.py` - `@requires_auth` decorator ✅
- [x] `app/auth/user_sync.py` - Sync Auth0 user to local DB ✅
- [x] `app/models/user.py` - User model (with auth0_id) ✅
- [x] `app/models/transaction.py` - Transaction model ✅
- [x] `app/models/enums.py` - Centralized enums ✅
- [x] `app/schemas/base.py` - Base schema and validators ✅
- [x] `app/schemas/user_schema.py` - User validation schemas ✅
- [x] `app/schemas/transaction_schema.py` - Transaction validation ✅
- [x] `app/services/user_service.py` - User sync logic ✅
- [x] `app/services/transaction_service.py` - Transaction CRUD ✅
- [x] `app/api/routes/auth.py` - Auth0 endpoints ✅
- [x] `app/api/routes/users.py` - User endpoints (`/me`, `/profile`) ✅
- [x] `app/api/routes/transactions.py` - Transaction CRUD ✅
- [x] `app/utils/errors.py` - Custom exception classes ✅
- [x] `app/__init__.py` - Flask app factory ✅
- [x] `migrations/` - Database migration (users + transactions tables) ✅
- [ ] `tests/` - Unit and integration tests (Sprint 2)
- [ ] `shared/postman/` - Postman collection & tests for auth endpoints (**Ariel**)
  - Create Postman collection for auth endpoints
  - Add tests for success/failure and token validation
  - Run locally and note results in README
  - Environment variables for base_url, access_token

### Sprint 2 - Foundation (Models, Services, Routes) ✅ IN PROGRESS

**Sprint 2 Foundation - COMPLETED:**
- [x] `app/models/category.py` - Category model (11 default categories) ✅
- [x] `app/models/notification.py` - Notification model (6 types) ✅
- [x] `app/models/alert.py` - Alert model (anomaly detection foundation) ✅
- [x] `app/models/enums.py` - Sprint 2 enums (CategoryType, NotificationType, AlertType, etc.) ✅
- [x] `app/schemas/category_schema.py` - Category serialization ✅
- [x] `app/schemas/notification_schema.py` - Notification serialization ✅
- [x] `app/schemas/alert_schema.py` - Alert serialization ✅
- [x] `app/services/category_service.py` - Category business logic + keyword categorization ✅
- [x] `app/services/notification_service.py` - Notification CRUD ✅
- [x] `app/services/alert_service.py` - Alert management ✅
- [x] `app/services/summary_service.py` - Spending summary calculations ✅
- [x] `app/api/routes/categories.py` - Category endpoints ✅
- [x] `app/api/routes/notifications.py` - Notification endpoints ✅
- [x] `app/api/routes/alerts.py` - Alert endpoints ✅
- [x] `app/api/routes/summary.py` - Summary/analytics endpoints ✅
- [x] `app/utils/helpers.py` - Shared utilities ✅
- [x] `migrations/versions/sprint2_categories_notifications.py` - Database migration ✅
- [x] `tests/integration/test_sprint2_endpoints.py` - Integration tests (21 tests passing) ✅

**Sprint 2 AI Integration - PENDING:**
- [ ] `app/ai/categorize.py` - HuggingFace + Gemini AI categorization
- [ ] `app/ai/chatbot.py` - Basic Q&A chatbot
- [ ] `app/api/routes/ai.py` - AI endpoints
- [ ] Automatic alert generation (anomaly detection logic)
- [ ] Postman collection for Sprint 2 endpoints

### Sprint 3 - Polish & Stretch Goals
- [ ] `app/ai/alerts.py` - Smart spending alerts
- [ ] `app/ai/recommendations.py` - Saving recommendations (stretch)
- [ ] `app/models/budget.py` - Budget model (nice-to-have)
- [ ] CSV export functionality
- [ ] Performance optimization
- [ ] Full test coverage

---

## 🔧 Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL (or use SQLite for development)
- Redis (optional - falls back to memory for development)
- Auth0 account with API configured

### 1. Clone and Navigate

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `backend/` folder:

```bash
# Copy from example (if exists) or create new
cp .env.example .env
```

**Required `.env` values:**

```env
# Flask Configuration
FLASK_APP=app:create_app
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-change-in-production

# Database (PostgreSQL)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/digital_finance_db

# Auth0 Configuration (REQUIRED)
AUTH0_DOMAIN=your-tenant.us.auth0.com
AUTH0_API_AUDIENCE=https://your-api-identifier
AUTH0_ALGORITHMS=RS256

# Redis (optional for development)
REDIS_URL=redis://localhost:6379/0

# CORS (Frontend URL)
FRONTEND_URL=http://localhost:5173
```

### 5. Set Up Auth0

1. Go to [Auth0 Dashboard](https://manage.auth0.com/)
2. Create a new **API**:
   - Name: `Digital Finance API`
   - Identifier: `https://api.digitalfinance.local` (this is your `AUTH0_API_AUDIENCE`)
   - Signing Algorithm: RS256
3. Copy the **Identifier** to your `.env` as `AUTH0_API_AUDIENCE`
4. Copy your **Domain** (e.g., `dev-xxxxx.us.auth0.com`) to your `.env` as `AUTH0_DOMAIN`

### 6. Set Up Database

```bash
# Create PostgreSQL database (or use SQLite for development)
# PostgreSQL:
createdb digital_finance_db

# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 7. Run Development Server

```bash
flask run
```

Server starts at `http://localhost:8000`

### 8. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "service": "digital-finance-api"}
```

### Quick Test (Python)

```python
# Test app creation
python -c "from app import create_app; app = create_app(); print('App created:', app)"
```

---

## 🔐 Auth0 Integration Notes

- **Frontend** handles login/logout UI via Auth0 React SDK
- **Backend** validates JWT tokens from Auth0
- Users are synced to local database on first API call
- See `docs/FRONTEND_AUTH_INTEGRATION.md` for frontend setup

---

## 🔗 API Endpoints Overview

> **Auth Note:** Login/Register handled by Auth0 on frontend. Backend validates Auth0 tokens.

### Authentication Endpoints (`/api/auth`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/callback` | Sync user after Auth0 login | Yes |
| GET | `/api/auth/me` | Get current auth user info | Yes |
| POST | `/api/auth/logout` | Get logout instructions/URL | Optional |
| GET | `/api/auth/status` | Check authentication status | Optional |

### User Endpoints (`/api/users`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/users/me` | Get current user profile | Yes |
| PATCH | `/api/users/me` | Update user profile | Yes |
| GET | `/api/users/me/settings` | Get user settings | Yes |
| PATCH | `/api/users/me/settings` | Update user settings | Yes |
| POST | `/api/users/me/deactivate` | Deactivate account | Yes |

### Transaction Endpoints (`/api/transactions`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/transactions` | List transactions (paginated) | Yes |
| POST | `/api/transactions` | Create new transaction | Yes |
| GET | `/api/transactions/:id` | Get transaction by ID | Yes |
| PATCH | `/api/transactions/:id` | Update transaction | Yes |
| DELETE | `/api/transactions/:id` | Delete transaction | Yes |
| GET | `/api/transactions/summary` | Get income/expense summary | Yes |

### Utility Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | No |
| GET | `/` | API info | No |

### Category Endpoints (`/api/categories`) - Sprint 2 Foundation ✅

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/categories` | List all categories (11 defaults) | Yes |
| GET | `/api/categories/:id` | Get category by ID | Yes |

### Notification Endpoints (`/api/notifications`) - Sprint 2 Foundation ✅

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/notifications` | List notifications (paginated) | Yes |
| GET | `/api/notifications/unread-count` | Get unread count | Yes |
| PATCH | `/api/notifications/:id/read` | Mark notification as read | Yes |
| PATCH | `/api/notifications/read-all` | Mark all as read | Yes |
| DELETE | `/api/notifications/:id` | Delete notification | Yes |
| DELETE | `/api/notifications/read` | Delete all read notifications | Yes |

### Alert Endpoints (`/api/alerts`) - Sprint 2 Foundation ✅

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/alerts` | List alerts (paginated) | Yes |
| GET | `/api/alerts/count` | Get active alert count | Yes |
| PATCH | `/api/alerts/:id/dismiss` | Dismiss single alert | Yes |
| PATCH | `/api/alerts/dismiss-all` | Dismiss all alerts | Yes |

### Summary Endpoints (`/api/summary`) - Sprint 2 Foundation ✅

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/summary/:period` | Get spending summary (daily/weekly/monthly/yearly/ytd) | Yes |
| GET | `/api/summary/:period/categories` | Get category breakdown | Yes |
| GET | `/api/summary/trends` | Get spending trends | Yes |
| GET | `/api/summary/compare/:period` | Compare with previous period | Yes |

### Future Endpoints (Sprint 2 AI / Sprint 3)

| Method | Endpoint | Description | Sprint |
|--------|----------|-------------|--------|
| POST | `/api/ai/categorize` | Get AI category prediction | 2 |
| POST | `/api/ai/chat` | Ask spending question | 2-3 |
| GET | `/api/ai/alerts` | Get AI-generated alerts | 2-3 |

---

## 🧪 Postman Collection (Pending - Ariel)

> **Status:** 🔄 In Progress - Assigned to Ariel Resendiz

### Collection Requirements

| Item | Status | Description |
|------|--------|-------------|
| Auth Endpoints | ⏳ | POST /callback, GET /me, POST /logout, GET /status |
| Success Tests | ⏳ | Valid token returns 200, user data present |
| Failure Tests | ⏳ | Invalid/missing token returns 401 |
| Token Validation | ⏳ | Check token presence and JWT format |
| Environment Vars | ⏳ | base_url, access_token, auth0_domain |

### Expected Test Coverage

```
Auth Tests:
├── POST /api/auth/callback
│   ├── ✓ Returns 200 with valid token
│   ├── ✓ Syncs user to database
│   ├── ✓ Returns is_new_user flag
│   └── ✗ Returns 401 without token
├── GET /api/auth/me
│   ├── ✓ Returns user data with valid token
│   └── ✗ Returns 401 without token
├── POST /api/auth/logout
│   └── ✓ Returns logout instructions
└── GET /api/auth/status
    ├── ✓ Returns authenticated: true with token
    └── ✓ Returns authenticated: false without token
```

### Local Run Results
*(To be filled by Ariel after testing)*

```
Date: ___________
Environment: Local (http://localhost:5001)
Total Tests: ___
Passed: ___
Failed: ___
Notes: ___
```

---

## 👥 Team Contacts

| Role | Name | Contact |
|------|------|---------|
| BE Lead (Sprint 1/2) | Ariel Resendiz | resendiz.ariel6@gmail.com |
| BE Lead (Sprint 2/3) | Suryadi Zhang | suryadizhang86@gmail.com |
| Data Analytics | Kenneth Beckford | treybeckford@yahoo.com |
| Cybersecurity | Monira Lizu | moniralizu1@gmail.com |

---

## 📚 Related Documentation

Documents to be created in `../docs/`:
- PRD.md - Product Requirements Document
- ERD.png - Entity Relationship Diagram
- API_CONTRACT.md - API endpoint specifications
- SECURITY_REQUIREMENTS.md - Security requirements
