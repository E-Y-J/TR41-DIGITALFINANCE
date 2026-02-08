# Backend Folder Structure

This document explains the folder structure of the backend application and what each folder is meant to build.

---

## 📁 Root Level

```
backend/
├── app/                    # Main application package
├── migrations/             # Database migrations (Alembic)
├── tests/                  # Test files
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules for Python
├── requirements.txt        # Python dependencies
├── README.md               # Backend documentation & guide
└── STRUCTURE.md            # This file - folder explanations
```

---

## 📁 app/ - Main Application Package

The core Flask application. All application code lives here.

### `app/api/`
**Purpose:** API layer - HTTP request/response handling

```
app/api/
├── __init__.py
└── routes/                 # Flask Blueprints for each resource
    └── __init__.py
```

**What to build here:**
- Flask Blueprint files for each API resource
- Route definitions (`@bp.route()`)
- Request parsing and response formatting
- Call services for business logic (routes should be thin)

**Files to create:**
| File | Endpoints | Status |
|------|-----------|--------|
| `auth.py` | `/api/auth/callback`, `/api/auth/me` | ✅ Sprint 1 |
| `users.py` | `/api/users/me`, `/api/users/profile` | ✅ Sprint 1 |
| `transactions.py` | `/api/transactions` (CRUD) | ✅ Sprint 1 |
| `test.py` | `/api/test` (connection test) | ✅ Sprint 1 |
| `categories.py` | `/api/categories` (list 11 defaults) | ✅ AI Foundation |
| `notifications.py` | `/api/notifications` (CRUD + mark read) | ✅ AI Foundation |
| `alerts.py` | `/api/alerts` (list, dismiss) | ✅ AI Foundation |
| `summary.py` | `/api/summary` (spending analytics) | ✅ AI Foundation |
| `ai.py` | `/api/ai/categorize`, `/api/ai/chat` | ⏳ AI Integration |

---

### `app/auth/`
**Purpose:** Auth0 integration and token validation

```
app/auth/
└── __init__.py
```

**What to build here:**
- Auth0 token validation logic
- JWKS (JSON Web Key Set) fetching and caching
- `@requires_auth` decorator for protected routes
- User sync from Auth0 claims to local database

**Files to create:**
| File | Purpose |
|------|---------|
| `auth0.py` | Validate Auth0 JWT tokens, fetch JWKS |
| `decorators.py` | `@requires_auth`, `@requires_scope` decorators |
| `user_sync.py` | Create/update local user from Auth0 token claims |

**Note:** Frontend handles Auth0 login UI. Backend only validates tokens.

---

### `app/core/`
**Purpose:** Application configuration and infrastructure

```
app/core/
└── __init__.py
```

**What to build here:**
- Environment variable loading
- Flask app configuration
- Extension initialization (database, cache, rate limiter)
- Middleware (CORS, logging, error handlers)

**Files to create:**
| File | Purpose |
|------|---------|
| `config.py` | Load env vars, define Config classes (Dev/Prod/Test) |
| `extensions.py` | Initialize SQLAlchemy, Redis cache, rate limiter |
| `middleware.py` | Request logging, error handlers, CORS setup |

---

### `app/models/`
**Purpose:** SQLAlchemy database models (ORM)

```
app/models/
└── __init__.py
```

**What to build here:**
- SQLAlchemy model classes
- Table definitions with columns, relationships, constraints
- Model methods for common queries

**Files to create:**
| File | Table | Description | Status |
|------|-------|-------------|--------|
| `user.py` | `users` | User profile (linked to Auth0) | ✅ Sprint 1 |
| `transaction.py` | `transactions` | Income/expense entries | ✅ Sprint 1 |
| `enums.py` | N/A | Centralized enums for all models | ✅ Sprint 1 + AI Foundation |
| `category.py` | `categories` | 11 default categories for AI categorization | ✅ AI Foundation |
| `notification.py` | `notifications` | User notifications (6 types) | ✅ AI Foundation |
| `alert.py` | `alerts` | Financial anomaly alerts | ✅ AI Foundation |
| `budget.py` | `budgets` | Budget goals per category | ⏳ Future |

---

### `app/schemas/`
**Purpose:** Marshmallow schemas for validation and serialization

```
app/schemas/
└── __init__.py
```

**What to build here:**
- Request validation schemas (what data is required/optional)
- Response serialization schemas (what data to return)
- Nested schemas for related objects

**Files to create:**
| File | Purpose | Status |
|------|---------|--------|
| `base.py` | Base schema class with common validators | ✅ Sprint 1 |
| `user_schema.py` | User profile validation/serialization | ✅ Sprint 1 |
| `transaction_schema.py` | Transaction CRUD validation | ✅ Sprint 1 |
| `category_schema.py` | Category serialization | ✅ AI Foundation |
| `notification_schema.py` | Notification serialization | ✅ AI Foundation |
| `alert_schema.py` | Alert serialization | ✅ AI Foundation |
| `ai_schema.py` | AI request/response schemas | ⏳ AI Integration |
| `notification_schema.py` | Notification serialization |

---

### `app/services/`
**Purpose:** Business logic layer

```
app/services/
└── __init__.py
```

**What to build here:**
- Core business logic (not in routes, not in models)
- Complex operations that span multiple models
- External API integrations
- Data processing and calculations

**Files to create:**
| File | Purpose | Status |
|------|---------|--------|
| `user_service.py` | User CRUD, profile updates, Auth0 sync | ✅ Sprint 1 |
| `transaction_service.py` | Transaction CRUD, filtering, CSV export | ✅ Sprint 1 |
| `category_service.py` | Category lookup, keyword categorization | ✅ AI Foundation |
| `notification_service.py` | Notification CRUD, mark as read | ✅ AI Foundation |
| `alert_service.py` | Alert management, dismiss alerts | ✅ AI Foundation |
| `summary_service.py` | Spending summaries, trends, comparisons | ✅ AI Foundation |
| `ai_service.py` | Orchestrate AI modules, format responses | ⏳ AI Integration |

**Rule:** Routes call services. Services call models. Keep it clean.

---

### `app/ai/`
**Purpose:** AI/ML modules for smart features

```
app/ai/
├── __init__.py
└── model_store/            # Trained model files (.pkl, metrics)
```

**What to build here:**
- Transaction categorization (ML model)
- Smart spending alerts (anomaly detection)
- Chatbot Q&A (rule-based intent parsing)
- Savings recommendations (stretch goal)
- Model training and evaluation scripts

**Files to create:**
| File | Feature |
|------|---------|
| `categorize.py` | Auto-categorize transactions by description |
| `alerts.py` | Detect unusual spending patterns |
| `chatbot.py` | Answer queries like "How much on food last month?" |
| `recommendations.py` | Suggest expense cuts (stretch goal) |
| `train.py` | Train/retrain the categorization model |
| `preprocess.py` | Clean and prepare data for AI |

**model_store/:**
| File | Purpose |
|------|---------|
| `categorizer.pkl` | Trained categorization model |
| `metrics.json` | Model accuracy, training date, version |

**Note:** Large model files are in `.gitignore`. Use Git LFS if needed.

---

### `app/charts/`
**Purpose:** Backend chart generation for exports and reports

```
app/charts/
└── __init__.py
```

**What to build here:**
- Spending summary pie/donut charts
- Category breakdown charts
- Saving progress bar charts
- Monthly/weekly trend line charts
- Charts for PDF export or image download

**Files to create:**
| File | Chart Type |
|------|------------|
| `spending_charts.py` | Pie/donut charts for spending by category |
| `trend_charts.py` | Line charts for spending over time |
| `budget_charts.py` | Progress bars for budget goals |
| `export.py` | Generate chart images for PDF/export |

**Libraries to use:**
- `matplotlib` - Static chart images
- `plotly` - Interactive charts (can export as images)

**Output formats:**
- Base64 encoded images (for API response)
- PNG/SVG files (for PDF export)

---

### `app/utils/`
**Purpose:** Shared utility functions

```
app/utils/
└── __init__.py
```

**What to build here:**
- Helper functions used across multiple modules
- Custom exceptions and error formatters
- Date/time utilities
- Pagination helpers

**Files to create:**
| File | Purpose |
|------|---------|
| `errors.py` | Custom exception classes, error response formatter |
| `validators.py` | Input validation helpers |
| `helpers.py` | Date formatting, pagination, common utilities |
| `constants.py` | App-wide constants (default categories, etc.) |

---

## 📁 migrations/ - Database Migrations

```
migrations/
└── versions/               # Migration files (auto-generated)
```

**Purpose:** Alembic/Flask-Migrate database schema versioning

**What happens here:**
- Auto-generated migration files from `flask db migrate`
- Schema changes tracked in version control
- Apply with `flask db upgrade`

**Commands:**
```bash
flask db init              # First time setup
flask db migrate -m "Add transactions table"
flask db upgrade           # Apply migrations
flask db downgrade         # Rollback
```

**Rule:** Review auto-generated migrations before committing.

---

## 📁 tests/ - Test Files

```
tests/
├── __init__.py
├── unit/                   # Unit tests (isolated functions)
│   └── __init__.py
└── integration/            # Integration tests (API endpoints)
    └── __init__.py
```

**What to build here:**

### `tests/unit/`
- Test individual functions/methods in isolation
- Mock external dependencies
- Fast to run

| File | Tests |
|------|-------|
| `test_transaction_service.py` | Transaction CRUD logic |
| `test_dashboard_service.py` | Summary calculations |
| `test_ai_categorize.py` | Categorization accuracy |

### `tests/integration/`
- Test full API request/response cycle
- Use test database
- Test authentication flow

| File | Tests |
|------|-------|
| `test_auth.py` | Auth0 token validation |
| `test_transactions_api.py` | `/api/transactions` endpoints |
| `test_dashboard_api.py` | `/api/dashboard` endpoints |

**Run tests:**
```bash
pytest                      # Run all tests
pytest tests/unit/          # Run unit tests only
pytest -v                   # Verbose output
pytest --cov=app            # With coverage report
```

---

## 🔄 Data Flow

```
Request → Routes → Services → Models → Database
                      ↓
                     AI
                      ↓
                   Charts
                      ↓
Response ← Routes ← Services ← Models
```

1. **Routes** receive HTTP request, validate with schemas
2. **Services** execute business logic
3. **Models** interact with database
4. **AI** provides smart categorization/alerts
5. **Charts** generate visualizations for export
6. **Services** format response
7. **Routes** return HTTP response

---

## 📝 Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | `snake_case.py` | `transaction_service.py` |
| Classes | `PascalCase` | `TransactionService` |
| Functions | `snake_case` | `get_user_transactions()` |
| Constants | `UPPER_SNAKE` | `DEFAULT_CATEGORIES` |
| Routes | `kebab-case` | `/api/spending-summary` |

---

## 🚀 Quick Reference

| I need to... | Create in... |
|--------------|--------------|
| Add API endpoint | `app/api/routes/` |
| Add database table | `app/models/` |
| Add business logic | `app/services/` |
| Add request validation | `app/schemas/` |
| Add AI feature | `app/ai/` |
| Add chart generation | `app/charts/` |
| Add Auth0 logic | `app/auth/` |
| Add utility function | `app/utils/` |
| Add configuration | `app/core/` |
| Add tests | `tests/unit/` or `tests/integration/` |
