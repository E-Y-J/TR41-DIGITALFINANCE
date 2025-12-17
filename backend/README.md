# Backend - AI Digital Finance Tracker

Flask-based REST API for the AI Digital Finance Tracker application.

## 🎯 Project Overview

This backend supports a cloud-based finance tracker that:
- Centralizes income, expenses, and e-wallet balances
- Provides AI-powered transaction categorization
- Generates spending insights and predictions
- Supports cross-device sync with authenticated accounts

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

### Sprint 1 - Authentication & Setup (Auth0)
- [ ] `app/core/config.py` - Environment configuration (Auth0 settings)
- [ ] `app/core/extensions.py` - Initialize Flask extensions
- [ ] `app/auth/auth0.py` - Auth0 token validation
- [ ] `app/auth/decorators.py` - `@requires_auth` decorator
- [ ] `app/auth/user_sync.py` - Sync Auth0 user to local DB
- [ ] `app/models/user.py` - User model (with auth0_id)
- [ ] `app/models/category.py` - Category model (default categories)
- [ ] `app/services/user_service.py` - User sync logic
- [ ] `app/api/routes/users.py` - User endpoints (`/me`, `/profile`)
- [ ] `migrations/` - Initial database migration
- [ ] `tests/integration/test_auth.py` - Auth0 validation tests

### Sprint 2 - Transactions, Dashboard & AI
- [ ] `app/models/transaction.py` - Transaction model
- [ ] `app/models/notification.py` - Notification model
- [ ] `app/schemas/transaction_schema.py` - Transaction validation
- [ ] `app/services/transaction_service.py` - Transaction CRUD
- [ ] `app/services/dashboard_service.py` - Summary calculations
- [ ] `app/api/routes/transactions.py` - Transaction endpoints
- [ ] `app/api/routes/dashboard.py` - Dashboard endpoints
- [ ] `app/ai/categorize.py` - AI categorization
- [ ] `app/ai/chatbot.py` - Basic Q&A chatbot
- [ ] `app/api/routes/ai.py` - AI endpoints

### Sprint 3 - Polish & Stretch Goals
- [ ] `app/ai/alerts.py` - Smart spending alerts
- [ ] `app/ai/recommendations.py` - Saving recommendations (stretch)
- [ ] `app/models/budget.py` - Budget model (nice-to-have)
- [ ] CSV export functionality
- [ ] Performance optimization
- [ ] Full test coverage

---

## 🔧 Setup Instructions

```bash
# 1. Navigate to backend folder
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy environment variables
cp .env.example .env
# Edit .env with your values

# 6. Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 7. Run development server
flask run
```

---

## 🔗 API Endpoints Overview

> **Auth Note:** Login/Register handled by Auth0 on frontend. Backend validates Auth0 tokens.

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/users/me` | Get current user (syncs from Auth0) | Yes |
| PUT | `/api/users/profile` | Update profile | Yes |
| GET | `/api/transactions` | List transactions | Yes |
| POST | `/api/transactions` | Create transaction | Yes |
| PUT | `/api/transactions/:id` | Update transaction | Yes |
| DELETE | `/api/transactions/:id` | Delete transaction | Yes |
| GET | `/api/dashboard/summary` | Spending summary | Yes |
| GET | `/api/dashboard/categories` | Category breakdown | Yes |
| POST | `/api/ai/categorize` | Get AI category prediction | Yes |
| POST | `/api/ai/chat` | Ask spending question | Yes |
| GET | `/api/notifications` | List notifications | Yes |

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
- ERD.md - Entity Relationship Diagram
- API_CONTRACT.md - API endpoint specifications
- SECURITY_REQUIREMENTS.md - Security requirements
