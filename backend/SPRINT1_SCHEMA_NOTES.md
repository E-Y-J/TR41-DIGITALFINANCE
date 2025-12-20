# =============================================================================
# SPRINT 1 - DATABASE SCHEMA IMPLEMENTATION NOTES
# Digital Finance Tracker - Backend
# =============================================================================
# Task: Convert ERD into DB tables via migrations, Define PK's, FK's, constraints
# =============================================================================

## 📋 OVERVIEW

This document explains the database schema implementation for Sprint 1, converting
the agreed-upon ERD into SQLAlchemy models with proper constraints, relationships,
and validation schemas.

---

## 🗃️ ERD TO DATABASE MAPPING

### Users Table (ERD → Implementation)

| ERD Column        | DB Column        | Data Type              | Constraints                    | Notes                          |
|-------------------|------------------|------------------------|--------------------------------|--------------------------------|
| user_id           | id               | UUID                   | PK, unique, not null           | Using UUID instead of INT      |
| auth_provider_id  | auth0_id         | VARCHAR(128)           | unique, not null, indexed      | Auth0 sub claim                |
| email             | email            | VARCHAR(255)           | unique, indexed                | Can be null (social login)     |
| first_name        | first_name       | VARCHAR(255)           | not null                       | ✅ Per ERD requirement         |
| last_name         | last_name        | VARCHAR(255)           | not null                       | ✅ Per ERD requirement         |
| date_of_birth     | —                | —                      | —                              | 🔒 Managed by Auth0            |
| address_line_2    | —                | —                      | —                              | 🔒 Managed by Auth0            |
| address_line_3    | —                | —                      | —                              | 🔒 Managed by Auth0            |
| city              | —                | —                      | —                              | 🔒 Managed by Auth0            |
| state             | —                | —                      | —                              | 🔒 Managed by Auth0            |
| postal_code       | —                | —                      | —                              | 🔒 Managed by Auth0            |
| country           | —                | —                      | —                              | 🔒 Managed by Auth0            |
| occupation        | —                | —                      | —                              | 🔒 Managed by Auth0            |
| account_status    | account_status   | ENUM                   | not null, default "pending"    | ✅ pending/active/suspended    |
| role              | role             | ENUM                   | not null, default "user"       | ✅ user/admin                  |
| salary_amount     | salary_amount    | DECIMAL(12,2)          | not null, default 0            | ✅ For budgeting features      |
| created_at        | created_at       | TIMESTAMP(tz)          | not null, default now()        | ✅ Auto-generated              |
| updated_at        | updated_at       | TIMESTAMP(tz)          | not null, auto-update          | ✅ Auto-updated                |

**Design Decision:** Personal data (DOB, address, occupation) managed by Auth0
to reduce risk, simplify schema, and avoid storing sensitive data locally.


### Transactions Table (ERD → Implementation)

| ERD Column        | DB Column        | Data Type              | Constraints                    | Notes                          |
|-------------------|------------------|------------------------|--------------------------------|--------------------------------|
| transaction_id    | id               | UUID                   | PK, unique, not null           | Using UUID instead of INT      |
| user_id           | user_id          | UUID                   | FK → users.id, not null        | ✅ CASCADE on delete           |
| amount            | amount           | DECIMAL(12,2)          | not null                       | ✅ Financial precision         |
| transaction_type  | transaction_type | ENUM                   | not null                       | ✅ income/expense              |
| date              | date             | VARCHAR(50)            | not null, indexed              | ✅ Per ERD (string format)     |
| merchant_name     | merchant_name    | VARCHAR(255)           | nullable                       | ✅ Optional field              |
| category          | category         | VARCHAR(100)           | nullable, indexed              | ✅ Optional field              |
| created_at        | created_at       | TIMESTAMP(tz)          | not null, default now()        | ✅ Auto-generated              |
| updated_at        | updated_at       | TIMESTAMP(tz)          | not null, auto-update          | ✅ Auto-updated                |

---

## 🔗 RELATIONSHIP DETAILS

### Users ↔ Transactions (1:N)

```
┌─────────────┐         ┌─────────────────┐
│   USERS     │         │  TRANSACTIONS   │
├─────────────┤         ├─────────────────┤
│ id (PK)     │◄────────│ user_id (FK)    │
│ first_name  │    1:N  │ id (PK)         │
│ last_name   │         │ amount          │
│ email       │         │ transaction_type│
│ ...         │         │ ...             │
└─────────────┘         └─────────────────┘
```

**Cardinality & Ordinality:**

| Entity      | Min | Max  | Meaning                                           |
|-------------|-----|------|---------------------------------------------------|
| User        | 1   | 1    | Every transaction MUST belong to exactly one user |
| Transaction | 0   | Many | A user can have zero or unlimited transactions    |

**Enforcement:**
- FK constraint: `user_id` references `users.id`
- NOT NULL constraint on `user_id`
- CASCADE delete: Deleting user removes all their transactions

---

## 📁 FILE STRUCTURE (Modular Design)

```
backend/app/
├── models/
│   ├── __init__.py          # Exports all models + enums
│   ├── enums.py             # ⭐ Centralized enums (AccountStatus, UserRole, TransactionType)
│   ├── user.py              # User model (~350 lines)
│   └── transaction.py       # Transaction model (~250 lines)
│
├── schemas/
│   ├── __init__.py          # Exports all schemas
│   ├── base.py              # ⭐ Centralized BaseSchema + validators
│   ├── user_schema.py       # User validation schemas
│   └── transaction_schema.py # Transaction validation schemas
```

**Why Modular?**
- Single source of truth for enums and base configurations
- Easier maintenance and testing
- Smaller, focused files
- Reusable validators across schemas

---

## 🔐 CONSTRAINTS SUMMARY

### Primary Keys (PK)
| Table        | Column | Type | Notes                    |
|--------------|--------|------|--------------------------|
| users        | id     | UUID | Auto-generated UUIDv4    |
| transactions | id     | UUID | Auto-generated UUIDv4    |

### Foreign Keys (FK)
| Table        | Column  | References    | On Delete | Notes          |
|--------------|---------|---------------|-----------|----------------|
| transactions | user_id | users.id      | CASCADE   | Required field |

### Unique Constraints
| Table | Column   | Notes                              |
|-------|----------|------------------------------------|
| users | id       | Primary key                        |
| users | auth0_id | One user per Auth0 account         |
| users | email    | One user per email (if provided)   |

### Not Null Constraints
| Table        | Columns                                                        |
|--------------|----------------------------------------------------------------|
| users        | id, auth0_id, first_name, last_name, account_status, role, salary_amount, created_at, updated_at |
| transactions | id, user_id, amount, transaction_type, date, created_at, updated_at |

### Default Values
| Table        | Column         | Default Value              |
|--------------|----------------|----------------------------|
| users        | id             | uuid.uuid4()               |
| users        | account_status | AccountStatus.PENDING      |
| users        | role           | UserRole.USER              |
| users        | salary_amount  | Decimal("0.00")            |
| users        | email_verified | False                      |
| users        | settings       | {} (empty JSON)            |
| users        | created_at     | datetime.now(timezone.utc) |
| users        | updated_at     | datetime.now(timezone.utc) |
| transactions | id             | uuid.uuid4()               |
| transactions | created_at     | datetime.now(timezone.utc) |
| transactions | updated_at     | datetime.now(timezone.utc) |

### Indexes
| Table        | Column(s)              | Type      | Purpose                    |
|--------------|------------------------|-----------|----------------------------|
| users        | auth0_id               | Single    | Fast Auth0 lookup          |
| users        | email                  | Single    | Fast email lookup          |
| users        | account_status         | Single    | Filter by status           |
| users        | role                   | Single    | Filter by role             |
| transactions | user_id                | Single    | Fast user transactions     |
| transactions | transaction_type       | Single    | Filter by type             |
| transactions | date                   | Single    | Filter by date             |
| transactions | category               | Single    | Filter by category         |
| transactions | (user_id, date)        | Composite | Monthly reports            |
| transactions | (user_id, category)    | Composite | Category summaries         |

---

## 📊 ENUMS DEFINED

### AccountStatus
```python
class AccountStatus(enum.Enum):
    PENDING = "pending"    # New account, not activated
    ACTIVE = "active"      # Active, in good standing
    SUSPENDED = "suspended" # Account suspended
```

### UserRole
```python
class UserRole(enum.Enum):
    USER = "user"   # Standard user permissions
    ADMIN = "admin" # Elevated admin permissions
```

### TransactionType
```python
class TransactionType(enum.Enum):
    INCOME = "income"   # Money received
    EXPENSE = "expense" # Money spent
```

---

## ✅ VALIDATION SCHEMAS

### UserSchema (Response)
- id, auth0_id, email, email_verified
- first_name, last_name, full_name (computed property)
- nickname, picture
- account_status, role, salary_amount
- settings, created_at, updated_at, last_login

### UserUpdateSchema (Request)
- first_name (optional, min 1 char, max 255)
- last_name (optional, min 1 char, max 255)
- nickname (optional, no spaces allowed)
- settings (partial update allowed)

### TransactionSchema (Response)
- id, user_id, amount, transaction_type
- date, merchant_name, category
- created_at, updated_at

### TransactionCreateSchema (Request)
- amount (required, positive, max 2 decimal places)
- transaction_type (required, "income" or "expense")
- date (required, non-empty string)
- merchant_name (optional, max 255 chars)
- category (optional, max 100 chars)

---

## 🚀 NEXT STEPS (Future Sprints)

### Fields Noted for Future Implementation:
- [ ] Categories table (custom user categories)
- [ ] Notifications table (user alerts)
- [ ] Budgets table (user budgets by category)
- [ ] Recurring transactions
- [ ] Financial goals

### Migration Commands (Reference):
```bash
# Generate migration after model changes
flask db migrate -m "Description of changes"

# Apply migration to database
flask db upgrade

# Rollback if needed
flask db downgrade

# Show migration history
flask db history
```

### Sprint 1 Migrations Already Applied:
```bash
# Migration ID: 0ef6d8b45cc5
# Description: Create users and transactions tables with ERD constraints
# Status: ✅ APPLIED
```

---

## 📝 CODE REVIEW CHECKLIST

| Check                          | Status | Notes                           |
|--------------------------------|--------|---------------------------------|
| PKs defined correctly          | ✅     | UUID for both tables            |
| FKs defined correctly          | ✅     | user_id → users.id              |
| Constraints match ERD          | ✅     | All NOT NULL, UNIQUE applied    |
| Enums centralized              | ✅     | In models/enums.py              |
| Relationships bidirectional    | ✅     | back_populates used             |
| Cascade delete configured      | ✅     | On transactions FK              |
| Indexes for common queries     | ✅     | Composite indexes added         |
| Timestamps auto-managed        | ✅     | created_at, updated_at          |
| Schemas validate input         | ✅     | Marshmallow schemas complete    |
| Code is modular                | ✅     | Base classes extracted          |
| No hardcoded secrets           | ✅     | N/A for models                  |
| Docstrings added               | ✅     | All classes/methods documented  |
| Type hints used                | ✅     | Mapped[] type hints throughout  |

---

## 📚 USAGE EXAMPLES

### Import Models
```python
from app.models import User, Transaction, AccountStatus, UserRole, TransactionType
```

### Import Schemas
```python
from app.schemas import UserSchema, TransactionCreateSchema, BaseSchema
```

### Create User
```python
user = User(
    auth0_id="auth0|507f1f77bcf86cd799439011",
    email="john.doe@example.com",
    first_name="John",
    last_name="Doe",
    account_status=AccountStatus.ACTIVE,
    role=UserRole.USER
)
db.session.add(user)
db.session.commit()
```

### Create Transaction
```python
transaction = Transaction(
    user_id=user.id,
    amount=Decimal("125.50"),
    transaction_type=TransactionType.EXPENSE,
    date="2024-01-15",
    merchant_name="Amazon",
    category="Shopping"
)
db.session.add(transaction)
db.session.commit()
```

### Query User with Transactions
```python
user = User.query.filter_by(email="john.doe@example.com").first()
for transaction in user.transactions:
    print(f"{transaction.date}: {transaction.amount}")
```

---

## ✍️ SIGN-OFF

**Implementation Status:** ✅ COMPLETE

### Files Modified/Created:

**Models (Database Layer):**
- `backend/app/models/enums.py` (NEW) - Centralized enums
- `backend/app/models/user.py` (UPDATED) - User model with first_name/last_name
- `backend/app/models/transaction.py` (NEW) - Transaction model
- `backend/app/models/__init__.py` (UPDATED) - Exports

**Schemas (Validation Layer):**
- `backend/app/schemas/base.py` (NEW) - Base schema + validators
- `backend/app/schemas/user_schema.py` (UPDATED) - User validation
- `backend/app/schemas/transaction_schema.py` (NEW) - Transaction validation
- `backend/app/schemas/__init__.py` (UPDATED) - Exports

**Services (Business Logic):**
- `backend/app/services/user_service.py` (UPDATED) - first_name/last_name support
- `backend/app/services/transaction_service.py` (NEW) - Full CRUD operations
- `backend/app/services/__init__.py` (UPDATED) - Exports

**Routes (API Layer):**
- `backend/app/api/routes/auth.py` (NEW) - Auth0 endpoints
- `backend/app/api/routes/users.py` (UPDATED) - User profile endpoints
- `backend/app/api/routes/transactions.py` (NEW) - Transaction CRUD
- `backend/app/__init__.py` (UPDATED) - Blueprint registration

**Auth (Auth0 Integration):**
- `backend/app/auth/user_sync.py` (UPDATED) - Parse Auth0 name to first/last

**Migrations:**
- `backend/migrations/` (INITIALIZED) - Alembic setup
- Migration: `0ef6d8b45cc5_create_users_and_transactions_tables_.py`

---

## 🔗 IMPLEMENTED API ROUTES

### Auth Routes (`/api/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/callback` | Sync user after Auth0 login |
| GET | `/api/auth/me` | Get current auth user info |
| POST | `/api/auth/logout` | Get logout instructions/URL |
| GET | `/api/auth/status` | Check authentication status |

### User Routes (`/api/users`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/me` | Get current user profile |
| PATCH | `/api/users/me` | Update user profile |
| GET | `/api/users/me/settings` | Get user settings |
| PATCH | `/api/users/me/settings` | Update user settings |
| POST | `/api/users/me/deactivate` | Deactivate account |

### Transaction Routes (`/api/transactions`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/transactions` | List transactions (paginated) |
| POST | `/api/transactions` | Create new transaction |
| GET | `/api/transactions/:id` | Get transaction by ID |
| PATCH | `/api/transactions/:id` | Update transaction |
| DELETE | `/api/transactions/:id` | Delete transaction |
| GET | `/api/transactions/summary` | Get income/expense summary |

---

## 🗄️ DATABASE STATUS

**Migration Applied:** ✅ YES

```sql
-- Tables Created:
CREATE TABLE users (
    id UUID PRIMARY KEY,
    auth0_id VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    picture TEXT,
    settings JSONB NOT NULL DEFAULT '{}',
    account_status VARCHAR(9) NOT NULL DEFAULT 'pending',
    role VARCHAR(5) NOT NULL DEFAULT 'user',
    salary_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount NUMERIC(12,2) NOT NULL,
    transaction_type VARCHAR(7) NOT NULL,
    date VARCHAR(50) NOT NULL,
    merchant_name VARCHAR(255),
    category VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Indexes Created:
CREATE INDEX ix_users_auth0_id ON users(auth0_id);
CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_account_status ON users(account_status);
CREATE INDEX ix_users_role ON users(role);
CREATE INDEX ix_transactions_user_id ON transactions(user_id);
CREATE INDEX ix_transactions_transaction_type ON transactions(transaction_type);
CREATE INDEX ix_transactions_date ON transactions(date);
CREATE INDEX ix_transactions_category ON transactions(category);
CREATE INDEX idx_transaction_user_date ON transactions(user_id, date);
CREATE INDEX idx_transaction_user_category ON transactions(user_id, category);
```

---

## 🔒 AUTH0 INTEGRATION

**Flow:** Frontend → Auth0 → JWT → Backend validation

1. Frontend redirects to Auth0 Universal Login
2. User authenticates (email/password, social, etc.)
3. Auth0 issues JWT tokens (access_token, id_token)
4. Frontend sends access_token in `Authorization: Bearer <token>` header
5. Backend validates token via `@requires_auth` decorator
6. User synced to local database via `sync_user_from_claims()`

**Backend Does NOT:**
- Handle login/register forms
- Store passwords
- Issue tokens

**Backend DOES:**
- Validate Auth0 JWTs
- Sync user data to local database
- Provide `/api/auth/callback` for frontend to call after login

---

## ✅ SPRINT 1 REQUIREMENTS CHECKLIST

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Convert ERD into DB tables | ✅ | `users` + `transactions` tables created |
| Define PKs | ✅ | UUID primary keys on both tables |
| Define FKs | ✅ | `user_id` FK on transactions |
| Basic constraints | ✅ | NOT NULL, UNIQUE, DEFAULT values |
| Keep schema minimal | ✅ | Personal data in Auth0, not local |
| Tables created with migrations | ✅ | `flask db upgrade` applied |
| Plan route map | ✅ | `/api/auth`, `/api/users`, `/api/transactions` |
| RESTful naming/status codes | ✅ | Standard REST conventions |
| Document in README | ✅ | API endpoints documented |
| Implement auth endpoints | ✅ | `/api/auth/*` routes |
| JWT validation | ✅ | `@requires_auth` decorator |
| Token storage documented | ✅ | Frontend stores tokens, backend validates |

---

## 🚀 READY FOR SPRINT 2

**Completed:**
- ✅ Database schema and migrations
- ✅ User and Transaction models
- ✅ Auth0 integration
- ✅ CRUD routes for users and transactions
- ✅ API documentation

**Next Sprint (2):**
- [ ] Dashboard service and routes
- [ ] AI categorization
- [ ] Postman collection
- [ ] Unit and integration tests
- [ ] Categories and Notifications models

---
*Sprint 1 - Backend Schema Implementation - COMPLETE*
