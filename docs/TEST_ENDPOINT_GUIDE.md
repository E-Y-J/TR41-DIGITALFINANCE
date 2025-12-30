# Test Endpoint Documentation

## Overview

This document describes the `/api/test` endpoint created for frontend-backend connection verification.

---

## Endpoint Details

| Property | Value |
|----------|-------|
| **URL** | `/api/test` |
| **Full URL (Development)** | `http://localhost:8000/api/test` |
| **Method** | `GET` |
| **Authentication** | ❌ Not Required |
| **Content-Type** | `application/json` |

> **Note:** Port 8000 is used to match the frontend's `apiClient` baseURL configuration.

---

## Purpose

This endpoint is designed for:

1. **Connection Testing** - Verify frontend can reach the backend API
2. **CORS Verification** - Confirm cross-origin requests work
3. **HTTP Client Validation** - Test Axios/fetch configuration
4. **Development Setup Check** - Quick health check during setup

---

## Request

```http
GET /api/test HTTP/1.1
Host: localhost:8000
```

**No headers required** - This endpoint works without authentication.

---

## Response

### Success Response (200 OK)

```json
{
    "success": true,
    "message": "Hello from backend!",
    "data": {
        "status": "connected",
        "api_version": "1.0.0",
        "service": "digital-finance-api"
    }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `true` for successful requests |
| `message` | string | Greeting message from backend |
| `data.status` | string | Connection status (`"connected"`) |
| `data.api_version` | string | Current API version |
| `data.service` | string | Service identifier |

---

## Frontend Usage Examples

### Using Axios (Your Current Setup)

```javascript
// frontend/src/api/test.js
export const getTest = async (client) => {
  const { data } = await client.get("/test");
  return data;
};
```

### Using TanStack Query (Your Current Setup)

```javascript
// frontend/src/hooks/queries/useTest.js
import { useQuery } from "@tanstack/react-query";
import { getTest } from "../../api/test";
import { useAxios } from "../useAxios";

export const useTest = () => {
  const apiClient = useAxios();

  return useQuery({
    queryKey: ["hello_world"],
    queryFn: () => getTest(apiClient),
    placeholderData: (previousData) => previousData,
  });
};
```

### In a React Component

```jsx
import { useTest } from "../hooks/queries/useTest";

const TestConnection = () => {
  const { data, isLoading, error } = useTest();

  if (isLoading) return <p>Connecting to backend...</p>;
  if (error) return <p>Connection failed: {error.message}</p>;

  return (
    <div>
      <h2>✅ {data.message}</h2>
      <p>Status: {data.data.status}</p>
      <p>API Version: {data.data.api_version}</p>
    </div>
  );
};
```

---

## CORS Configuration

The backend is configured to allow requests from:

| Origin | Port | Description |
|--------|------|-------------|
| `http://localhost:5173` | 5173 | Vite dev server (default) |

### Allowed Methods
- GET, POST, PUT, DELETE, OPTIONS

### Allowed Headers
- Content-Type
- Authorization

---

## Port Configuration

### ✅ Configured Ports (Aligned)

| Component | Port | Notes |
|-----------|------|-------|
| **Backend (Flask)** | `8000` | Run with `flask run --port=8000` |
| **Frontend (Vite)** | `5173` | Default Vite dev server |
| **Frontend apiClient** | `8000` | In `frontend/src/api/index.js` |

The backend is configured to run on port 8000 to match the frontend's expected API base URL.

---

## Error Responses

### 405 Method Not Allowed

If you try POST, PUT, or DELETE:

```json
{
    "success": false,
    "error": {
        "code": "METHOD_NOT_ALLOWED",
        "message": "The method is not allowed for the requested URL."
    }
}
```

### 404 Not Found

If you use wrong URL (e.g., `/api/tests` instead of `/api/test`):

```json
{
    "success": false,
    "error": {
        "code": "NOT_FOUND",
        "message": "The requested URL was not found on the server."
    }
}
```

---

## Quick Test Commands

### Using cURL

```bash
curl http://localhost:8000/api/test
```

### Using PowerShell

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/test" -Method Get
```

### Using Browser

Simply navigate to: `http://localhost:8000/api/test`

---

## Swagger Documentation

The endpoint is also documented in Swagger UI:

- **Swagger UI:** `http://localhost:8000/api/docs`
- **OpenAPI JSON:** `http://localhost:8000/api/docs/openapi.json`

---

## Contact

For backend-related questions, reach out to:

| Role | Name | Email |
|------|------|-------|
| BE Lead (Sprint 2/3) | Suryadi Zhang | suryadizhang86@gmail.com |
| BE Lead (Sprint 1/2) | Ariel Resendiz | resendiz.ariel6@gmail.com |
