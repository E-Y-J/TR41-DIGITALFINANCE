# Postman Collections

This folder contains Postman collections and environment files for API testing.

---

## 🌐 Production API

| Environment | URL |
|-------------|-----|
| **Production API** | https://securebankai.mysticdatanode.net |
| **Swagger UI** | https://securebankai.mysticdatanode.net/api/docs/ |
| **OpenAPI Spec** | https://securebankai.mysticdatanode.net/api/docs/openapi.json |

---

## 🚀 Quick Start for QA

### Auto-Import from Swagger

**You can import the OpenAPI spec directly into Postman:**

1. Open Postman → **Import** → **Link** tab
2. Paste: `https://securebankai.mysticdatanode.net/api/docs/openapi.json`
3. All endpoints are auto-generated from the OpenAPI spec.

### Local Development

1. Start backend: `cd backend && flask db upgrade && flask run --port=8000`
2. Open Postman → **Import** → **Link** tab
3. Paste: `http://localhost:8000/api/docs/openapi.json`

---

### View Endpoints in Swagger UI

- **Production:** https://securebankai.mysticdatanode.net/api/docs/
- **Local:** http://localhost:8000/api/docs

---

## ⚠️ Common Gotchas

- **If `{{access_token}}` is empty, authenticated tests will fail with 401 (expected).**
- `amount` must be a **string**, not a number.
- `transaction_type` must be `"income"` or `"expense"`.
- **Deactivated users will receive 403, not 401.**
- Re-import the OpenAPI spec if endpoints change — manual edits may be overwritten.
  > 💡 Tip: Always ensure `{{access_token}}` is valid before running protected endpoint tests to avoid 401 errors.

## 📦 What’s Included in This Postman Collection

- Preconfigured requests for all public and protected API endpoints
- Automated Postman test scripts for:
  - Status codes
  - Content-Type validation
  - Response envelope shape
  - Core field validation
- Positive and negative auth coverage:
  - Authenticated callback
  - Missing token (401)
  - Invalid token (401)
- Tolerant test guards to avoid false failures when placeholders are used
- Sample request bodies for create/update operations

---

## 📋 Endpoints (17)

| Category     | Count | Auth |
| ------------ | ----- | ---- |
| Health       | 2     | ❌   |
| Auth         | 4     | ✅   |
| Users        | 5     | ✅   |
| Transactions | 6     | ✅   |

---

## 🔐 Authentication

All protected endpoints require an Auth0 JWT token.

- Collection auth: Authorization → Bearer Token → `{{access_token}}`
- Or header: `Authorization: Bearer {{access_token}}`
- Missing/invalid → 401

### Getting a Token

**Option 1: Via Frontend**

1. Start frontend: `cd frontend && npm run dev`
2. Login at http://localhost:5173
3. Open DevTools → Application → Local Storage
4. Copy the `access_token` value

**Option 2: Auth0 Client Credentials (Postman)**

- Env: `auth0_domain`, `auth0_client_id`, `auth0_client_secret`, `auth0_audience`
- POST https://{{auth0_domain}}/oauth/token
  ```json
  {
    "grant_type": "client_credentials",
    "client_id": "{{auth0_client_id}}",
    "client_secret": "{{auth0_client_secret}}",
    "audience": "{{auth0_audience}}"
  }
  ```

### Using Token in Postman

Set environment variable: `{{access_token}} = <your-token>`

Add header: `Authorization: Bearer {{access_token}}`

---

## 🧪 Test Coverage Summary

| Area           | Coverage                                      |
| -------------- | --------------------------------------------- |
| Health & Root  | ✅ Status + schema                            |
| Auth Callback  | ✅ Success, missing token, invalid token      |
| Auth Status    | ✅ JWT validation                             |
| Users          | ✅ Profile, settings (get/update), deactivate |
| Transactions   | ✅ List, get, create, update, delete, summary |
| Error Handling | ✅ 401, 403 envelopes validated               |

---

## 📝 Key Schema Details

### Transaction Create (POST /api/transactions)

```json
{
  "amount": "125.50",
  "transaction_type": "expense",
  "date": "2025-12-20",
  "merchant_name": "Amazon",
  "category": "Shopping"
}
```

**Important:**

- `amount` - String (decimal precision)
- `transaction_type` - "income" or "expense" (not credit/debit)
- `merchant_name` - not "description"

---

## ⚠️ Deactivated Accounts

- `account_status = "deactivated"` blocks protected endpoints (expect 403).
- Reactivate (local):
  - SQL:
    ```sql
    UPDATE users SET account_status='active', updated_at=NOW() WHERE auth0_id='<your-auth0-id>';
    ```
  - Flask shell:
    ```python
    from app.core.extensions import db
    from app.models.user import User
    from app.models.enums import AccountStatus
    u = User.get_by_auth0_id("<your-auth0-id>"); u.account_status = AccountStatus.ACTIVE; db.session.commit()
    ```

---

## 🔧 Environment (recommended)

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "user_id": "",
  "transaction_id": "",
  "auth0_domain": "",
  "auth0_client_id": "",
  "auth0_client_secret": "",
  "auth0_audience": ""
}
```

---

## 📚 Links

- Swagger UI: http://localhost:8000/api/docs
- OpenAPI JSON: http://localhost:8000/api/docs/openapi.json
- API Testing Guide: `backend/docs/API_TESTING_GUIDE.md`
- Sprint 1 Guide: `backend/docs/SPRINT1_IMPLEMENTATION_GUIDE.md`
