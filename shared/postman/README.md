# Postman Collections

This folder contains Postman collections and environment files for API testing.

---

## 🚀 Quick Start for QA

### Auto-Import from Swagger

**You can import the OpenAPI spec directly into Postman:**

1. Start backend: `cd backend && flask run --port=5000`
2. Open Postman → **Import** → **Link** tab
3. Paste: `http://localhost:5000/api/docs/openapi.json`
4. All 17 requests auto-generated!

### View Endpoints in Swagger UI

Open in browser: http://localhost:5000/api/docs

---

## 📋 Endpoints to Test (17 Total)

| Category | Count | Auth Required |
|----------|-------|---------------|
| Health | 2 | ❌ No |
| Auth | 4 | Mixed |
| Users | 5 | ✅ Yes |
| Transactions | 6 | ✅ Yes |

---

## 🔐 Authentication

All protected endpoints require an Auth0 JWT token.

### Getting a Token

**Option 1: Via Frontend**
1. Start frontend: `cd frontend && npm run dev`
2. Login at http://localhost:5173
3. Open DevTools → Application → Local Storage
4. Copy the `access_token` value

**Option 2: Auth0 Dashboard**
1. Go to Auth0 Dashboard → APIs → Your API → Test tab
2. Copy the test token

### Using Token in Postman

Set environment variable: `{{access_token}} = <your-token>`

Add header: `Authorization: Bearer {{access_token}}`

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

## 🔧 Environment Variables

```json
{
    "base_url": "http://localhost:5000",
    "access_token": "",
    "user_id": "",
    "transaction_id": ""
}
```

---

## 📚 Related Docs

- **Swagger UI:** http://localhost:5000/api/docs
- **API Testing Guide:** `backend/docs/API_TESTING_GUIDE.md`
- **Sprint 1 Guide:** `backend/docs/SPRINT1_IMPLEMENTATION_GUIDE.md`
