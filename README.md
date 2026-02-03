# TR41-DIGITALFINANCE – SecureBank AI

**SecureBank AI** is an AI-powered personal finance assistant that helps users:

- Centralize multiple e-wallets and accounts  
- Track income and expenses  
- Understand spending patterns and trends  
- Receive AI-assisted categorization and financial insights  

This is a full-stack, cloud-based **AI Digital Finance Tracker** MVP built as part of a Tech Residency program.

---

## Team Members

-   Front End Developers:
    -   [Jae Young Seo]()
-   Back End Developers:
    -   [Suryadi Zhang]()
    -   [Ariel Resendiz]()
-   Cybersecurity Specialist:
    -   [Monira Lizu]()

## 🌟 Core Features

- **Manual & AI-assisted transaction entry**
- **AI prediction of spending categories**
- **Unified dashboard** with balances, trends, and summaries
- **Cloud sync** across devices
- **Authentication & authorization** via Auth0
- **Optional / stretch goals**
  - Budgeting goals and alerts  
  - CSV export & enhanced reporting  
  - Advanced analytics & recommendations  

---

## 🧱 Tech Stack Overview

### Frontend

- React (Vite)
- JavaScript
- MUI (Material UI)
- TanStack Query
- Redux Toolkit
- Auth0 (SPA auth)

> See: `frontend/README.md` for full setup, scripts, and env vars.

---

### Backend

- Python, Flask
- Flask-SQLAlchemy, Alembic (Flask-Migrate)
- Marshmallow (serialization & validation)
- OpenAPI/Swagger (flask-swagger / flask-swagger-ui)
- pytest, gunicorn
- Flask-JWT-Extended / Auth0 token validation
- flask-limiter (Redis), flask-caching (Redis)
- Sentry (monitoring)

> See: `backend/README.md` for architecture, API design, setup, and detailed docs.  
> See: `backend/docs/DEMO_GUIDE.md` for AI demo walkthroughs and Docker-based demo flow.

---

### Data & AI

- **Database:** PostgreSQL (seeded with mock data for development)
- **AI / ML:**  
  - HuggingFace models  
  - Transaction categorization training in `training/`  
- **AI Hosting / Models:** HuggingFace, local models orchestrated by backend

> See: `training/README.md` for transaction categorization research and model training details.

---

### DevOps, Hosting & Deployment

- **Containers / Orchestration:** Docker, Docker Compose
- **Frontend Hosting:** Vercel
- **Backend Hosting:** VPS (Plesk), GCSM, Cloudflare, potentially AWS/Supabase
- **Local Orchestration & Automation:**  
  - Root `Makefile` – dev environment and utility commands  
  - `docker/` – Docker configuration documentation  
  - `RUN_APP.md` – commands and setup to run Docker containers with Docker Desktop + `make`

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