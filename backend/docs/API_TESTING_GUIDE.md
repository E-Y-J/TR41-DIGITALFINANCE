# API Testing Guide

Comprehensive guide for testing the Digital Finance Tracker API.

---

## 📋 Table of Contents

1. [Overview](#-overview)
2. [Getting Started](#-getting-started)
3. [Swagger UI Testing](#-swagger-ui-testing)
4. [Postman Testing](#-postman-testing)
5. [Pytest Testing](#-pytest-testing)
6. [Authentication Setup](#-authentication-setup)
7. [API Endpoints Reference](#-api-endpoints-reference)
8. [Test Scenarios](#-test-scenarios)
9. [Troubleshooting](#-troubleshooting)

---

## 📖 Overview

The Digital Finance Tracker API provides endpoints across 8 categories:

| Category | Endpoints | Auth Required | Status |
|----------|-----------|---------------|--------|
| Health | 2 | ❌ No | ✅ Sprint 1 |
| Auth | 4 | Mixed | ✅ Sprint 1 |
| Users | 5 | ✅ Yes | ✅ Sprint 1 |
| Transactions | 6 | ✅ Yes | ✅ Sprint 1 |
| Categories | 2 | ✅ Yes | ✅ Sprint 2 Foundation |
| Notifications | 6 | ✅ Yes | ✅ Sprint 2 Foundation |
| Alerts | 4 | ✅ Yes | ✅ Sprint 2 Foundation |
| Summary | 4 | ✅ Yes | ✅ Sprint 2 Foundation |

### Testing Tools Available

| Tool | Purpose | Location |
|------|---------|----------|
| **Swagger UI** | Interactive browser testing | http://localhost:8000/api/docs |
| **Postman** | Collection-based testing | `shared/postman/` |
| **pytest** | Automated unit/integration tests | `backend/tests/` |

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.11+** installed
2. **PostgreSQL** running on `localhost:5432`
3. **Database** `digital_finance_db` created
4. **Virtual environment** set up

### Start the Backend Server

```powershell
# Navigate to backend
cd backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Set environment variables (PowerShell)
$env:FLASK_APP = "app:create_app"
$env:FLASK_ENV = "development"

# Start server (port 8000 matches frontend's expected API URL)
flask run --host=0.0.0.0 --port=8000
```

### Verify Server is Running

```powershell
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "service": "digital-finance-api"}
```

---

## 🔷 Swagger UI Testing

### Access Swagger UI

1. Start the backend server (see above)
2. Open browser: **http://localhost:8000/api/docs**
3. You'll see the interactive API documentation

### Swagger UI Features

| Feature | Description |
|---------|-------------|
| **Try it out** | Execute API calls directly in browser |
| **Request body** | Edit JSON payloads |
| **Response preview** | See actual API responses |
| **Schema viewer** | Inspect request/response schemas |
| **Authorize** | Add Bearer token for protected endpoints |

### Testing Public Endpoints (No Auth)

These endpoints work without authentication:

1. Click on endpoint (e.g., `GET /health`)
2. Click **"Try it out"** button
3. Click **"Execute"**
4. View response below

### Testing Protected Endpoints (With Auth)

1. **Get an Auth0 token** (see [Authentication Setup](#-authentication-setup))
2. Click **"Authorize"** button (🔒 icon at top)
3. Enter: `Bearer <your_access_token>`
4. Click **"Authorize"** then **"Close"**
5. Now all protected endpoints will include your token

### Swagger UI Tips

- ✅ Use **"Try it out"** to test before writing code
- ✅ Check **response codes** (200, 201, 400, 401, 404)
- ✅ Review **schema definitions** at bottom of page
- ✅ **Copy curl commands** from executed requests

---

## 📮 Postman Testing

### Import Collection

1. Open Postman
2. Click **Import** → Select files from `shared/postman/`:
   - `digital-finance.postman_collection.json`
   - `local.postman_environment.json`
3. Select **"Local Development"** environment

### Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `{{base_url}}` | `http://localhost:8000` | API base URL (matches frontend config) |
| `{{access_token}}` | (your token) | Auth0 JWT token |
| `{{user_id}}` | (auto-populated) | Current user's UUID |
| `{{transaction_id}}` | (auto-populated) | Test transaction UUID |

### Testing Workflow

```
1. Run "Health Check" request → Verify server is up
2. Set access_token in environment
3. Run "Auth - Callback" → Syncs user, saves user_id
4. Run "Transactions - Create" → Creates test data
5. Run other requests as needed
```

### Creating New Postman Tests

#### Pre-request Scripts
```javascript
// Set timestamp for unique test data
pm.environment.set("timestamp", new Date().getTime());

// Generate random amount
pm.environment.set("random_amount", (Math.random() * 1000).toFixed(2));
```

#### Test Scripts (Assertions)
```javascript
// Basic status check
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Response structure check
pm.test("Response has success flag", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.success).to.be.true;
});

// Save response data for chaining
pm.test("Save transaction ID", function () {
    var jsonData = pm.response.json();
    pm.environment.set("transaction_id", jsonData.data.id);
});

// Validate data types
pm.test("Amount is a string (decimal)", function () {
    var jsonData = pm.response.json();
    pm.expect(typeof jsonData.data.amount).to.equal("string");
});
```

### Running Collection Tests

1. Click collection name → **"Run"**
2. Select environment: **"Local Development"**
3. Configure iterations (1 for manual, more for load testing)
4. Click **"Run"**
5. Review results

---

## 🧪 Pytest Testing

### Test Structure

```
backend/tests/
├── __init__.py
├── conftest.py           # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_user_service.py
│   ├── test_transaction_service.py
│   └── test_schemas.py
└── integration/
    ├── __init__.py
    ├── test_auth_routes.py
    ├── test_user_routes.py
    └── test_transaction_routes.py
```

### Running Tests

```powershell
# Activate virtual environment
cd backend
.\venv\Scripts\Activate.ps1

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_transaction_service.py

# Run specific test
pytest tests/unit/test_transaction_service.py::test_create_transaction

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Example Test Fixtures (conftest.py)

```python
# backend/tests/conftest.py
import pytest
from app import create_app
from app.core.extensions import db

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client for API requests."""
    return app.test_client()

@pytest.fixture
def auth_headers():
    """Mock auth headers for protected endpoints."""
    # In testing mode, we can mock the token validation
    return {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }

@pytest.fixture
def sample_user(app):
    """Create a sample user for testing."""
    from app.models.user import User

    user = User(
        auth0_id="auth0|test123",
        email="test@example.com",
        first_name="Test",
        last_name="User"
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def sample_transaction(app, sample_user):
    """Create a sample transaction for testing."""
    from app.models.transaction import Transaction

    transaction = Transaction(
        user_id=sample_user.id,
        amount="100.00",
        transaction_type="expense",
        date="2025-12-20",
        merchant_name="Test Store",
        category="Shopping"
    )
    db.session.add(transaction)
    db.session.commit()
    return transaction
```

### Example Unit Tests

```python
# backend/tests/unit/test_transaction_service.py
import pytest
from decimal import Decimal
from app.services.transaction_service import TransactionService

class TestTransactionService:
    """Unit tests for TransactionService."""

    def test_create_transaction_success(self, app, sample_user):
        """Test creating a valid transaction."""
        with app.app_context():
            data = {
                "amount": "150.50",
                "transaction_type": "expense",
                "date": "2025-12-20",
                "merchant_name": "Amazon",
                "category": "Shopping"
            }

            transaction = TransactionService.create_transaction(sample_user, data)

            assert transaction.id is not None
            assert str(transaction.amount) == "150.50"
            assert transaction.transaction_type.value == "expense"
            assert transaction.user_id == sample_user.id

    def test_create_transaction_invalid_type(self, app, sample_user):
        """Test that invalid transaction type raises error."""
        with app.app_context():
            data = {
                "amount": "100.00",
                "transaction_type": "invalid",
                "date": "2025-12-20"
            }

            with pytest.raises(ValidationError) as exc_info:
                TransactionService.create_transaction(sample_user, data)

            assert "transaction_type" in str(exc_info.value)

    def test_get_user_transactions_pagination(self, app, sample_user):
        """Test transaction list pagination."""
        with app.app_context():
            # Create 25 transactions
            for i in range(25):
                TransactionService.create_transaction(sample_user, {
                    "amount": f"{i + 1}.00",
                    "transaction_type": "expense",
                    "date": "2025-12-20"
                })

            # Get first page
            transactions, meta = TransactionService.get_user_transactions(
                sample_user, page=1, per_page=10
            )

            assert len(transactions) == 10
            assert meta["total"] == 25
            assert meta["total_pages"] == 3
```

### Example Integration Tests

```python
# backend/tests/integration/test_transaction_routes.py
import pytest
import json

class TestTransactionRoutes:
    """Integration tests for transaction API endpoints."""

    def test_list_transactions_unauthorized(self, client):
        """Test that listing transactions requires auth."""
        response = client.get("/api/transactions")

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data["success"] is False

    def test_create_transaction_success(self, client, auth_headers, sample_user):
        """Test creating a transaction via API."""
        payload = {
            "amount": "99.99",
            "transaction_type": "expense",
            "date": "2025-12-20",
            "merchant_name": "Test Merchant",
            "category": "Food"
        }

        response = client.post(
            "/api/transactions",
            data=json.dumps(payload),
            headers=auth_headers
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["data"]["amount"] == "99.99"
        assert data["data"]["transaction_type"] == "expense"

    def test_create_transaction_validation_error(self, client, auth_headers):
        """Test validation error for missing required fields."""
        payload = {
            "amount": "100.00"
            # Missing: transaction_type, date
        }

        response = client.post(
            "/api/transactions",
            data=json.dumps(payload),
            headers=auth_headers
        )

        assert response.status_code == 422
        data = json.loads(response.data)
        assert data["success"] is False

    def test_get_transaction_not_found(self, client, auth_headers):
        """Test 404 for non-existent transaction."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"

        response = client.get(
            f"/api/transactions/{fake_uuid}",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_transaction_summary(self, client, auth_headers, sample_transaction):
        """Test transaction summary endpoint."""
        response = client.get(
            "/api/transactions/summary",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "total_income" in data["data"]
        assert "total_expense" in data["data"]
```

---

## 🔐 Authentication Setup

### Option 1: Get Token via Frontend

1. Start the frontend: `cd frontend && npm run dev`
2. Open http://localhost:5173
3. Click **Login** → Complete Auth0 login
4. Open DevTools (F12) → **Application** → **Local Storage**
5. Find `@@auth0...` entry → Copy the `access_token` value

### Option 2: Get Token from Auth0 Dashboard

1. Go to [Auth0 Dashboard](https://manage.auth0.com)
2. Navigate to **Applications** → **APIs** → **Your API**
3. Click **Test** tab
4. Copy the provided test token

### Option 3: Auth0 Machine-to-Machine Token

For automated testing without user interaction:

```bash
curl --request POST \
  --url https://YOUR_DOMAIN.auth0.com/oauth/token \
  --header 'content-type: application/json' \
  --data '{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "audience": "YOUR_API_AUDIENCE",
    "grant_type": "client_credentials"
  }'
```

### Using Token in Tests

#### Swagger UI
1. Click 🔒 **Authorize** button
2. Enter: `Bearer <your_token>`
3. Click **Authorize**

#### Postman
1. Set `{{access_token}}` environment variable
2. Headers auto-include: `Authorization: Bearer {{access_token}}`

#### pytest
```python
# Mock token validation in conftest.py
@pytest.fixture(autouse=True)
def mock_auth(mocker):
    """Mock Auth0 token validation for tests."""
    mocker.patch(
        'app.auth.decorators.validate_token',
        return_value={"sub": "auth0|test123", "email": "test@example.com"}
    )
```

---

## 📚 API Endpoints Reference

### Health Endpoints (No Auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API info and version |
| `GET` | `/health` | Service health check |

### Auth Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/callback` | ✅ | Sync user after Auth0 login |
| `GET` | `/api/auth/me` | ✅ | Get authenticated user info |
| `POST` | `/api/auth/logout` | ⚪ | Get logout instructions |
| `GET` | `/api/auth/status` | ⚪ | Check auth status |

### User Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/users/me` | ✅ | Get current user profile |
| `PATCH` | `/api/users/me` | ✅ | Update current user profile |
| `GET` | `/api/users/me/settings` | ✅ | Get user settings |
| `PATCH` | `/api/users/me/settings` | ✅ | Update user settings |
| `POST` | `/api/users/me/deactivate` | ✅ | Deactivate account |

### Transaction Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/transactions` | ✅ | List transactions (paginated) |
| `POST` | `/api/transactions` | ✅ | Create transaction |
| `GET` | `/api/transactions/{id}` | ✅ | Get single transaction |
| `PATCH` | `/api/transactions/{id}` | ✅ | Update transaction |
| `DELETE` | `/api/transactions/{id}` | ✅ | Delete transaction |
| `GET` | `/api/transactions/summary` | ✅ | Get summary statistics |

### Category Endpoints (Sprint 2 Foundation)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/categories` | ✅ | List all 11 default categories |
| `GET` | `/api/categories/{id}` | ✅ | Get category by ID |

### Notification Endpoints (Sprint 2 Foundation)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/notifications` | ✅ | List notifications (paginated) |
| `GET` | `/api/notifications/unread-count` | ✅ | Get unread notification count |
| `PATCH` | `/api/notifications/{id}/read` | ✅ | Mark notification as read |
| `PATCH` | `/api/notifications/read-all` | ✅ | Mark all notifications as read |
| `DELETE` | `/api/notifications/{id}` | ✅ | Delete single notification |
| `DELETE` | `/api/notifications/read` | ✅ | Delete all read notifications |

### Alert Endpoints (Sprint 2 Foundation)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/alerts` | ✅ | List alerts (paginated) |
| `GET` | `/api/alerts/count` | ✅ | Get active (undismissed) alert count |
| `PATCH` | `/api/alerts/{id}/dismiss` | ✅ | Dismiss single alert |
| `PATCH` | `/api/alerts/dismiss-all` | ✅ | Dismiss all alerts |

### Summary Endpoints (Sprint 2 Foundation)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/summary/{period}` | ✅ | Get spending summary (daily/weekly/monthly/yearly/ytd) |
| `GET` | `/api/summary/{period}/categories` | ✅ | Get category breakdown for period |
| `GET` | `/api/summary/trends` | ✅ | Get spending trends over multiple periods |
| `GET` | `/api/summary/compare/{period}` | ✅ | Compare current vs previous period |

---

## 🎯 Test Scenarios

### Happy Path Scenarios

| # | Scenario | Steps |
|---|----------|-------|
| 1 | User Registration Flow | Login via Auth0 → Call `/api/auth/callback` → Verify user created |
| 2 | Create Transaction | Authenticate → POST `/api/transactions` → Verify 201 response |
| 3 | List Transactions | Authenticate → GET `/api/transactions` → Verify pagination |
| 4 | Update Transaction | Create → PATCH with new data → Verify changes |
| 5 | Delete Transaction | Create → DELETE → Verify 404 on re-fetch |
| 6 | Get Summary | Create income/expense → GET `/api/transactions/summary` → Verify totals |

### Edge Case Scenarios

| # | Scenario | Expected Result |
|---|----------|-----------------|
| 1 | Create transaction with negative amount | 422 Validation Error |
| 2 | Create transaction with future date | 201 Created (allowed) |
| 3 | Update non-existent transaction | 404 Not Found |
| 4 | Delete another user's transaction | 403 Forbidden |
| 5 | List transactions with invalid page | 400 Bad Request |
| 6 | Create transaction with missing fields | 422 Validation Error |

### Security Scenarios

| # | Scenario | Expected Result |
|---|----------|-----------------|
| 1 | Access protected endpoint without token | 401 Unauthorized |
| 2 | Access with expired token | 401 Unauthorized |
| 3 | Access with malformed token | 401 Unauthorized |
| 4 | SQL injection in query params | Safe (ORM prevents) |
| 5 | XSS in merchant_name | Safe (escaped in response) |

---

## 🔧 Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Missing/invalid token | Check token in Authorize dialog |
| `422 Validation Error` | Invalid request body | Check required fields in schema |
| `404 Not Found` | Wrong endpoint or ID | Verify URL and UUID format |
| `500 Internal Error` | Server crash | Check terminal logs |
| CORS error | Frontend domain mismatch | Check `FRONTEND_URL` in `.env` |

### Debug Tips

1. **Check server logs** - Terminal running Flask shows all errors
2. **Use Swagger UI** - Test endpoints before writing code
3. **Inspect response body** - Error details are in the response
4. **Verify environment** - Check `.env` configuration

### Getting Help

- **Backend issues:** Suryadi Zhang (suryadizhang86@gmail.com)
- **Auth0 issues:** See `docs/FRONTEND_AUTH_INTEGRATION.md`
- **Postman issues:** Check `shared/postman/README.md`

---

## 📎 Quick Reference

### Response Format

**Success:**
```json
{
    "success": true,
    "data": { ... },
    "message": "Success message",
    "meta": { "page": 1, "per_page": 20, "total": 100 }
}
```

**Error:**
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Error description",
        "details": { ... }
    }
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Auth required |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource missing |
| 422 | Validation Error - Invalid data |
| 500 | Server Error - Bug in code |
