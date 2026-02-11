# TR41-DIGITALFINANCE – SecureBank AI

**SecureBank AI** is an AI-powered personal finance assistant that helps users:

- Centralize multiple e-wallets and accounts  
- Track income and expenses  
- Understand spending patterns and trends  
- Receive AI-assisted categorization and financial insights  
- Chat with an AI assistant for financial queries and transaction management

This is a full-stack, cloud-based **AI Digital Finance Tracker** MVP built as part of a Tech Residency program.

---

## 🌐 Live Demo

| Environment | URL |
|-------------|-----|
| **Frontend** | https://securebankai.vercel.app |
| **API** | https://securebankai.mysticdatanode.net |
| **API Health** | https://securebankai.mysticdatanode.net/health |
| **API Docs** | https://securebankai.mysticdatanode.net/api/docs/ |

---

## 👥 Team Members

| Role | Name | Email |
|------|------|-------|
| **Frontend Developer** | Jae Young Seo | jaeyseo0922@gmail.com |
| **Backend Developer** | Suryadi Zhang | suryadizhang86@gmail.com |
| **Backend Developer** | Ariel Resendiz | resendiz.ariel6@gmail.com |
| **Cybersecurity Specialist** | Monira Lizu | moniralizu1@gmail.com |

## 🌟 Core Features

### User Management
- **Auth0 Authentication** - Secure OAuth2/OIDC login with Google, GitHub, email/password
- **User Onboarding** - Guided setup for new users with preferences configuration
- **Profile Management** - Update personal info, currency preferences, settings

### Transaction Management
- **CRUD Operations** - Create, read, update, delete transactions
- **AI-Powered Categorization** - Automatic category prediction using DistilBERT (99.7% accuracy)
- **Transaction History** - Paginated, filterable, searchable transaction list
- **Summary & Trends** - Daily, weekly, monthly spending analytics

### Budget Management
- **Budget Creation** - Set spending limits by category or overall
- **Budget Alerts** - Real-time alerts when approaching or exceeding limits
- **Budget Suggestions** - AI-powered recommendations based on spending patterns

### AI Chat Assistant
- **Natural Language Interface** - Chat with AI for financial queries
- **Intent Classification** - MiniLM model identifies user intent
- **Command Execution** - Add transactions, check budgets via chat
- **Spending Insights** - AI-generated analysis of spending patterns
- **Recurring Transaction Detection** - Automatic identification of subscriptions
- **RAG Knowledge Base** - Contextual answers from documentation

### Notifications & Alerts
- **Budget Alerts** - Over-budget and near-limit warnings
- **Bill Reminders** - Upcoming recurring payment notifications
- **Anomaly Detection** - Unusual spending pattern alerts

### Loans & Debt Tracking
- **Loan Management** - Track loans, payments, interest rates
- **Payment History** - Record loan payments and remaining balance

### Data Visualization
- **Dashboard** - Overview of financial health
- **Spending Charts** - Category breakdowns, trend graphs
- **Comparative Analysis** - Month-over-month spending comparison  

---

## 🧱 Tech Stack Overview

### Frontend

| Category | Technology |
|----------|------------|
| **Framework** | React 19 (Vite 6) |
| **Language** | JavaScript/JSX |
| **UI Library** | MUI (Material UI) v6 |
| **State Management** | Redux Toolkit, TanStack Query |
| **Routing** | React Router v7 |
| **Authentication** | Auth0 React SDK |
| **HTTP Client** | Axios |
| **Hosting** | Vercel |

> See: `frontend/README.md` for full setup, scripts, and env vars.

---

### Backend

| Category | Technology |
|----------|------------|
| **Framework** | Flask 3.0+ (Python 3.13) |
| **ORM** | Flask-SQLAlchemy, Alembic (Flask-Migrate) |
| **Validation** | Marshmallow |
| **API Docs** | OpenAPI/Swagger (flask-swagger-ui) |
| **Authentication** | Auth0 (python-jose, PyJWT) |
| **Caching** | Flask-Caching (Redis) |
| **Rate Limiting** | Flask-Limiter (Redis) |
| **WSGI Server** | Gunicorn |
| **Monitoring** | Sentry |
| **Testing** | pytest (146+ tests) |

> See: `backend/README.md` for architecture, API design, setup, and detailed docs.  
> See: `backend/docs/DEMO_GUIDE.md` for AI demo walkthroughs and Docker-based demo flow.

---

### AI / Machine Learning

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Categorizer** | DistilBERT (HuggingFace) | Transaction category prediction (99.7% accuracy) |
| **Intent Classifier** | MiniLM-L6 (Sentence Transformers) | User intent detection in chat |
| **Chat Fallback** | Google Gemini 2.0 Flash | Complex queries requiring LLM |
| **Guardrails** | Custom NLP | Finance-only query filtering |
| **RAG** | Sentence Transformers | Knowledge base retrieval |
| **Recurring Detector** | Custom Python | Subscription/recurring payment detection |
| **Anomaly Detector** | Statistical Analysis | Unusual spending pattern detection |

> See: `training/README.md` for transaction categorization research and model training details.

---

### Database & Infrastructure

| Category | Technology |
|----------|------------|
| **Database** | PostgreSQL 15 |
| **Cache/Session** | Redis 7.4 |
| **Containerization** | Docker, Docker Compose |
| **Frontend Hosting** | Vercel (automatic deployments from GitHub) |
| **Backend Hosting** | VPS (IONOS) with Plesk, Apache reverse proxy |
| **SSL/TLS** | Let's Encrypt (auto-renewal) |
| **DNS/CDN** | Cloudflare |
| **Secrets** | Google Cloud Secret Manager |

> See: `docker/README.md` and `RUN_APP.md` for container setup and local orchestration.

---

## 📂 Repository Structure

High-level layout of key modules:

```text
.
├─ README.md                # You are here – project overview
├─ Makefile                 # Dev, test, and health-check commands
├─ RUN_APP.md               # Docker + make run instructions
├─ docker/
│  └─ README.md             # Docker configuration & usage
├─ backend/
│  ├─ README.md             # Backend architecture, API, setup
│  └─ docs/
│     └─ DEMO_GUIDE.md      # AI demo guide & Docker demo flow
├─ frontend/
│  └─ README.md             # React + Vite setup & frontend dev guide
├─ training/
│  └─ README.md             # Transaction categorization training details
└─ shared/
   ├─ security/
   │  └─ README.md          # Security practices & requirements
   ├─ postman/
   │  └─ README.md          # Postman collections & env setup
   └─ e2e/
      └─ README.md          # Playwright end-to-end test setup & usage
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Docker & Docker Compose **or**
- Python 3.11+, Node.js, PostgreSQL, Redis installed locally
- Auth0 tenant (for full auth integration)

---

### 2. Run with Docker + Make

From the **project root**:

```bash
# Start development environment (backend, db, etc.)
make run

# Stop all services
make down

# Stop and clear containers + volumes
make clear

# View DB data (PostgreSQL shell)
make view-data

# AI demo CLI (inside backend container)
make demo

# Run AI component tests (inside backend container)
make test-ai

# Quick backend health check
make health
```

> All of the above use `docker compose --env-file .env.dev ...` under the hood.  
> See: `RUN_APP.md` and `docker/README.md` for detailed Docker configuration.

---

### 3. Frontend (Local Dev)

Basic flow (summary – see `frontend/README.md` for details):

```bash
cd frontend

# 1. Create .env with Auth0 values
# VITE_AUTH0_DOMAIN=******.auth0.com
# VITE_AUTH0_CLIENT_ID=******
# VITE_AUTH0_AUDIENCE=******

# 2. Install dependencies
npm install

# 3. Run dev server
npm run dev
```

Frontend will typically be available at `http://localhost:5173`.

---

### 4. Backend (Local Dev Without Docker)

Reference only – if you’re not using Docker/Make:

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure .env (see backend/README.md for fields)
cp .env.example .env

# Run migrations
flask db upgrade

# Start server
flask run
```

Backend will typically run at `http://localhost:8000`.

---

## 🧪 Testing & Tooling

- **Backend unit & integration tests:** `pytest` (see `backend/README.md`)
- **E2E tests (full stack):** Playwright in `shared/e2e/`
- **API testing:** Postman collections in `shared/postman/`
- **Security documentation & checks:** `shared/security/`

> See each subdirectory’s `README.md` for how to run tests and what’s covered.

---

## 👥 Residency & Collaboration Context

This project is part of a **Tech Residency** focused on AI-powered personal finance and digital payments.

- Acting “employer” / client: **Elijah** (product direction, feedback, expectations)
- Team responsibility: architecture, design, development, testing, and delivery of the MVP
- Team task (Sprint 0): select a fictional FinTech company name  
  (e.g., ClearLedger AI, SpendSmart Systems, NovaFinance, FlowWise)

### Weekly Structure (Residency)

- **Standups:** Mon / Wed / Fri, 5–6 PM CST (from Week 2)
- **Office Hours:** Tue & Thu, 5–6 PM CST with Elijah
- **Employer Check-In:** Weekly alignment session (scheduled in Sprint 0)
- **Demo Day:** Thursday, February 12 – students, alumni, employers showcase final builds

By Demo Day, the goal is to ship a **polished, portfolio-ready MVP** that demonstrates:

- Applied AI in a realistic FinTech setting  
- Solid engineering fundamentals (testing, security, observability)  
- Production-style workflows across frontend, backend, and DevOps  

---

## 🔐 Security, API, and E2E Docs

- `shared/security/README.md` – security requirements, best practices, and controls  
- `shared/postman/README.md` – Postman collections, environments, and usage  
- `shared/e2e/README.md` – Playwright end-to-end tests covering full stack  

These documents are the primary references for API validation, security posture, and full-stack regression testing.

---