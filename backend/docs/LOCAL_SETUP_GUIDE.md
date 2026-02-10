# Local Development Setup Guide

Step-by-step guide for backend developers to run the Flask application locally.

---

## 📋 Table of Contents

1. [Prerequisites](#-prerequisites)
2. [Quick Start (TL;DR)](#-quick-start-tldr)
3. [Detailed Setup Steps](#-detailed-setup-steps)
4. [Environment Variables](#-environment-variables)
5. [Database Setup](#-database-setup)
6. [Running the Application](#-running-the-application)
7. [Verify Installation](#-verify-installation)
8. [Project Architecture](#-project-architecture)
9. [Common Errors & Fixes](#-common-errors--fixes)
10. [Getting Help](#-getting-help)

---

## 📦 Prerequisites

Before starting, make sure you have installed:

| Tool | Version | Check Command |
|------|---------|---------------|
| Python | 3.10+ | `python --version` |
| PostgreSQL | 14+ | `psql --version` |
| Git | Latest | `git --version` |

You'll also need:
- Auth0 credentials (from the shared Google doc)

---

## ⚡ Quick Start (TL;DR)

For experienced developers, here's the quick version:

```powershell
# 1. Navigate to backend
cd backend

# 2. Create & activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment file and configure
copy .env.example .env
# Edit .env with your database credentials and Auth0 config

# 5. Run migrations
flask db upgrade

# 6. Start server
# NOTE: Port 8000 matches frontend's expected API base URL
flask run --port=8000

# 7. Test it
curl http://localhost:8000/health
```

---

## 📝 Detailed Setup Steps

### Step 1: Navigate to Backend Directory

```powershell
cd "c:\Users\your-username\projects\digital finance\backend"
```

---

### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

✅ **Success indicator:** You should see `(venv)` in your terminal prompt.

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**If you encounter errors with `psycopg2-binary`:**
```bash
pip install psycopg2-binary --no-cache-dir
```

---

### Step 4: Set Up PostgreSQL Database

1. Open PostgreSQL (pgAdmin or terminal)
2. Create a new database:

```sql
CREATE DATABASE digital_finance_db;
```

**Using psql:**
```bash
psql -U postgres
CREATE DATABASE digital_finance_db;
\q
```

---

### Step 5: Configure Environment Variables

Copy the example environment file:

```powershell
copy .env.example .env
```

Edit `.env` with your values:

```env
# Flask Configuration
FLASK_APP=app:create_app
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=any-random-string-for-local-dev

# Database (update with YOUR PostgreSQL credentials)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/digital_finance_db

# Auth0 Configuration (from shared Google doc)
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_API_AUDIENCE=your-api-identifier
AUTH0_ALGORITHMS=RS256

# Redis (optional for local dev)
# REDIS_URL=redis://localhost:6379/0

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:5173
```

⚠️ **Important Notes:**
- Replace `YOUR_PASSWORD` with your actual PostgreSQL password
- Get `AUTH0_DOMAIN` and `AUTH0_API_AUDIENCE` from the shared team doc
- If you don't have Redis, comment out the `REDIS_URL` line

---

### Step 6: Run Database Migrations

```bash
flask db upgrade
```

This creates all the required tables (`users`, `transactions`, etc.).

**If migrations fail:**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

### Step 7: Start the Flask Server

```bash
# NOTE: Port 8000 matches frontend's apiClient baseURL configuration
flask run --port=8000
```

✅ **Success indicator:**
```
 * Running on http://127.0.0.1:8000
```

---

## ✅ Verify Installation

Open your browser or use curl to test:

| URL | Expected Response |
|-----|-------------------|
| http://localhost:8000/ | `{"name": "Digital Finance Tracker API", "version": "1.0.0", ...}` |
| http://localhost:8000/health | `{"status": "healthy", "service": "digital-finance-api"}` |
| http://localhost:8000/api/docs | Swagger UI (interactive documentation) |

**Using curl:**
```bash
curl http://localhost:8000/health
```

---

## 🔧 Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `FLASK_APP` | ✅ | Entry point | `app:create_app` |
| `FLASK_ENV` | ✅ | Environment | `development` |
| `FLASK_DEBUG` | ❌ | Debug mode | `1` |
| `SECRET_KEY` | ✅ | Flask secret | Any random string |
| `DATABASE_URL` | ✅ | PostgreSQL URL | `postgresql://user:pass@localhost:5432/db` |
| `AUTH0_DOMAIN` | ✅ | Auth0 tenant | `your-tenant.auth0.com` |
| `AUTH0_API_AUDIENCE` | ✅ | API identifier | `your-api-identifier` |
| `REDIS_URL` | ❌ | Redis URL | `redis://localhost:6379/0` |
| `FRONTEND_URL` | ❌ | CORS origins | `http://localhost:5173` || `SENTRY_DSN` | ❌ | Sentry error monitoring | `https://xxx@xxx.ingest.sentry.io/xxx` |
| `SENTRY_TRACES_SAMPLE_RATE` | ❌ | Performance sampling (0-1) | `0.1` |
---

## 📁 Project Architecture

```
backend/
├── app/
│   ├── __init__.py          # App factory (creates Flask app)
│   ├── api/
│   │   ├── routes/          # API endpoints
│   │   │   ├── auth.py      # /api/auth/* routes
│   │   │   ├── users.py     # /api/users/* routes
│   │   │   └── transactions.py  # /api/transactions/* routes
│   │   └── swagger.py       # OpenAPI/Swagger config
│   ├── auth/
│   │   ├── auth0.py         # Auth0 token validation
│   │   ├── decorators.py    # @requires_auth decorator
│   │   └── user_sync.py     # Sync Auth0 user to DB
│   ├── core/
│   │   ├── config.py        # Loads .env variables
│   │   └── extensions.py    # DB, cache, limiter init
│   ├── models/              # SQLAlchemy database models
│   │   ├── user.py          # User model
│   │   └── transaction.py   # Transaction model
│   ├── schemas/             # Marshmallow validation schemas
│   │   ├── user_schema.py
│   │   └── transaction_schema.py
│   ├── services/            # Business logic layer
│   │   ├── user_service.py
│   │   └── transaction_service.py
│   └── utils/
│       └── errors.py        # Custom exception classes
├── migrations/              # Alembic database migrations
├── tests/                   # pytest tests
├── docs/                    # Documentation (you are here!)
├── .env.example             # Environment template
└── requirements.txt         # Python dependencies
```

### How It Works

1. `flask run` calls `create_app()` in `app/__init__.py`
2. `create_app()` loads config from `.env` via `app/core/config.py`
3. Extensions (DB, cache) initialized in `app/core/extensions.py`
4. Blueprints registered for routes:
   - `/api/auth` → `app/api/routes/auth.py`
   - `/api/users` → `app/api/routes/users.py`
   - `/api/transactions` → `app/api/routes/transactions.py`

---

## ❌ Common Errors & Fixes

### `ModuleNotFoundError: No module named 'app'`

**Cause:** Not in the right directory or venv not activated

**Fix:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

---

### `AUTH0_DOMAIN is required` or `AUTH0_API_AUDIENCE is required`

**Cause:** Missing Auth0 config in `.env`

**Fix:** Add these to your `.env`:
```env
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_API_AUDIENCE=your-api-identifier
```

---

### `DATABASE_URL is required`

**Cause:** Missing database URL in `.env`

**Fix:** Add to `.env`:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/digital_finance_db
```

---

### `could not connect to server: Connection refused`

**Cause:** PostgreSQL isn't running

**Fix:** Start PostgreSQL service:
- Windows: Open Services → PostgreSQL → Start
- Mac: `brew services start postgresql`
- Linux: `sudo systemctl start postgresql`

---

### `FATAL: password authentication failed`

**Cause:** Wrong PostgreSQL credentials

**Fix:** Verify your username/password in `DATABASE_URL`

---

### `relation "users" does not exist`

**Cause:** Migrations haven't been run

**Fix:**
```bash
flask db upgrade
```

---

### Redis connection errors

**Cause:** Redis not installed or not running

**Fix:** Comment out `REDIS_URL` in `.env` - the app will use in-memory cache instead

---

### `error: Microsoft Visual C++ 14.0 is required`

**Cause:** Some packages need build tools (Windows)

**Fix:** Install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) or use:
```bash
pip install psycopg2-binary --no-cache-dir
```

---

## 📞 Getting Help

If you're stuck after following these steps:

1. **Check the error message carefully** - most issues are config-related
2. **Verify your `.env` file** - make sure all required variables are set
3. **Check PostgreSQL is running** - `psql -U postgres` should connect
4. **Share on Slack:**
   - Exact error message
   - Your `.env` file (mask passwords!)
   - Which step failed

---

## 📚 Related Documentation

- [API Testing Guide](./API_TESTING_GUIDE.md) - How to test endpoints
- [Sprint 1 Implementation Guide](./SPRINT1_IMPLEMENTATION_GUIDE.md) - Schema details
- [Swagger UI](http://localhost:8000/api/docs) - Interactive API docs (when running)
- [Postman Collections](../../shared/postman/README.md) - Postman setup
