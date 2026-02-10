# SecureBank AI - Documentation Hub

Central documentation hub for the AI Digital Finance Tracker project.

## 🌐 Production URLs

| Environment | URL |
|-------------|-----|
| **Frontend** | https://digital-finance-frontend.vercel.app |
| **API** | https://securebankai.mysticdatanode.net |
| **API Docs** | https://securebankai.mysticdatanode.net/api/docs/ |

---

## 📄 Documentation Index

### Setup & Deployment

| Document | Description | Location |
|----------|-------------|----------|
| Deployment Checklist | Production deployment steps | [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) |
| Frontend Auth Integration | Auth0 setup for frontend | [FRONTEND_AUTH_INTEGRATION.md](FRONTEND_AUTH_INTEGRATION.md) |
| Backend Local Setup | Local development guide | [backend/docs/LOCAL_SETUP_GUIDE.md](../backend/docs/LOCAL_SETUP_GUIDE.md) |

### API Documentation

| Document | Description | Location |
|----------|-------------|----------|
| OpenAPI Spec | Full API specification | [backend/openapi.json](../backend/openapi.json) |
| Swagger UI | Interactive API docs | https://securebankai.mysticdatanode.net/api/docs/ |
| Frontend API Guide | How frontend calls API | [backend/docs/FRONTEND_API_GUIDE.md](../backend/docs/FRONTEND_API_GUIDE.md) |
| API Testing Guide | Testing endpoints | [backend/docs/API_TESTING_GUIDE.md](../backend/docs/API_TESTING_GUIDE.md) |
| Categories/Notifications API | Specific endpoint docs | [backend/docs/CATEGORIES_NOTIFICATIONS_SUMMARY_API.md](../backend/docs/CATEGORIES_NOTIFICATIONS_SUMMARY_API.md) |

### AI System

| Document | Description | Location |
|----------|-------------|----------|
| AI Architecture | AI system design | [backend/docs/AI_ARCHITECTURE.md](../backend/docs/AI_ARCHITECTURE.md) |
| AI System Guide | How to use AI features | [backend/docs/AI_SYSTEM_GUIDE.md](../backend/docs/AI_SYSTEM_GUIDE.md) |
| AI Foundation Plan | Implementation roadmap | [backend/docs/AI_FOUNDATION_IMPLEMENTATION_PLAN.md](../backend/docs/AI_FOUNDATION_IMPLEMENTATION_PLAN.md) |
| AI Changelog | AI feature updates | [backend/docs/AI_CHANGELOG.md](../backend/docs/AI_CHANGELOG.md) |

### Testing

| Document | Description | Location |
|----------|-------------|----------|
| E2E Tests | Playwright test guide | [shared/e2e/README.md](../shared/e2e/README.md) |
| Postman Collection | API collection | [shared/postman/README.md](../shared/postman/README.md) |
| Test Endpoint Guide | Manual testing | [TEST_ENDPOINT_GUIDE.md](TEST_ENDPOINT_GUIDE.md) |

### Security

| Document | Description | Location |
|----------|-------------|----------|
| Security Documentation | Security practices | [shared/security/README.md](../shared/security/README.md) |

### Enterprise Features (Optional)

| Document | Description | Location |
|----------|-------------|----------|
| Optional Features | Future enterprise features | [OPTIONAL_ENTERPRISE_FEATURES.md](OPTIONAL_ENTERPRISE_FEATURES.md) |

---

## 👥 Team Members

| Role | Name | Email |
|------|------|-------|
| **Frontend Developer** | Jae Young Seo | jaeyseo0922@gmail.com |
| **Backend Developer** | Suryadi Zhang | suryadizhang86@gmail.com |
| **Backend Developer** | Ariel Resendiz | resendiz.ariel6@gmail.com |
| **Cybersecurity Specialist** | Monira Lizu | moniralizu1@gmail.com |

---

## 🛠 Tech Stack Summary

### Frontend
- React 19, Vite 6, MUI v6, Redux Toolkit, TanStack Query, Auth0

### Backend
- Flask 3.0+, Python 3.13, PostgreSQL 15, Redis 7.4, Gunicorn

### AI/ML
- DistilBERT (categorization), MiniLM (intent), Gemini 2.0 (LLM fallback)

### Infrastructure
- Docker, Vercel (frontend), VPS/Apache (backend), Cloudflare, Let's Encrypt
