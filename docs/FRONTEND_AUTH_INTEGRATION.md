# Frontend Auth Integration Guide

> **Document Type:** Backend → Frontend Integration Guide  
> **Author:** Suryadi Zhang (Backend Team)  
> **Sprint:** Sprint 1 - Authentication & Setup  
> **Last Updated:** December 16, 2025

---

## 📋 Overview

This document explains how the frontend should integrate with the backend Auth0 authentication system.

**Key Points:**
- Frontend handles login/logout UI via Auth0 React SDK
- Backend validates tokens and provides protected API endpoints
- User sync happens automatically on first API call

---

## 🔧 Required Frontend Configuration

### 1. Add `audience` Parameter

**Current Issue:** The frontend Auth0 configuration is missing the `audience` parameter.

**Why It's Needed:** Without `audience`, Auth0 returns an opaque token that cannot be validated by the backend. With `audience`, Auth0 returns a proper JWT that the backend can verify.

**Required Change in `src/main.tsx`:**

```tsx
<Auth0Provider
  domain={import.meta.env.VITE_AUTH0_DOMAIN}
  clientId={import.meta.env.VITE_AUTH0_CLIENT_ID}
  authorizationParams={{
    redirect_uri: window.location.origin,
    audience: import.meta.env.VITE_AUTH0_AUDIENCE,  // ADD THIS LINE
    scope: "openid profile email",                   // ADD THIS LINE
  }}
  useRefreshTokens={true}
  cacheLocation="localstorage"
>
```

### 2. Add Environment Variable

Add to your `.env` file:

```env
VITE_AUTH0_AUDIENCE=https://your-api-identifier
```

> **Note:** Get the API identifier from Auth0 Dashboard → APIs → Your API → Identifier

---

## 🔐 Making Authenticated API Calls

### Get Access Token

Use the Auth0 React SDK hook to get the access token:

```tsx
import { useAuth0 } from '@auth0/auth0-react';

function MyComponent() {
  const { getAccessTokenSilently, isAuthenticated } = useAuth0();
  
  const fetchData = async () => {
    try {
      const token = await getAccessTokenSilently({
        authorizationParams: {
          audience: import.meta.env.VITE_AUTH0_AUDIENCE,
        }
      });
      
      const response = await fetch('/api/users/me', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      const data = await response.json();
      console.log(data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };
  
  // ...
}
```

### Create API Client (Recommended)

Create a reusable API client:

```tsx
// src/api/client.ts
import { useAuth0 } from '@auth0/auth0-react';

// NOTE: Port 8000 is used to match frontend's apiClient configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const useApiClient = () => {
  const { getAccessTokenSilently } = useAuth0();
  
  const request = async (endpoint: string, options: RequestInit = {}) => {
    const token = await getAccessTokenSilently({
      authorizationParams: {
        audience: import.meta.env.VITE_AUTH0_AUDIENCE,
      }
    });
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'API request failed');
    }
    
    return response.json();
  };
  
  return {
    get: (endpoint: string) => request(endpoint),
    post: (endpoint: string, data: any) => 
      request(endpoint, { method: 'POST', body: JSON.stringify(data) }),
    patch: (endpoint: string, data: any) => 
      request(endpoint, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (endpoint: string) => 
      request(endpoint, { method: 'DELETE' }),
  };
};
```

---

## 📡 Available API Endpoints

### User Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/me` | Get current user profile |
| PATCH | `/api/users/me` | Update user profile |
| GET | `/api/users/me/settings` | Get user settings |
| PATCH | `/api/users/me/settings` | Update user settings |
| POST | `/api/users/me/deactivate` | Deactivate account |

### Health Check (No Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | API health status |
| GET | `/` | API info |

---

## 📦 Response Format

### Success Response

```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "email": "user@example.com",
    "name": "John Doe",
    "nickname": "john",
    "picture": "https://...",
    "email_verified": true,
    "is_active": true,
    "settings": {
      "currency": "USD",
      "timezone": "UTC",
      "theme": "system"
    },
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "User retrieved successfully"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required",
    "details": {}
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | No token or invalid token |
| `TOKEN_EXPIRED` | 401 | Token has expired |
| `FORBIDDEN` | 403 | Not enough permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Invalid request data |
| `INTERNAL_ERROR` | 500 | Server error |

---

## 🔄 User Sync Flow

When the frontend makes the first authenticated API call:

1. Frontend sends request with `Authorization: Bearer <token>`
2. Backend validates token with Auth0
3. Backend creates local user record if first login
4. Backend updates user info if changed in Auth0
5. Backend returns response

**This is automatic** - no special handling needed on frontend.

---

## 📝 Example: User Profile Component

```tsx
// src/components/UserProfile.tsx
import { useEffect, useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { useApiClient } from '../api/client';

interface User {
  id: string;
  email: string;
  name: string;
  picture: string;
  settings: {
    currency: string;
    theme: string;
  };
}

export function UserProfile() {
  const { isAuthenticated, isLoading } = useAuth0();
  const api = useApiClient();
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    if (isAuthenticated) {
      loadUser();
    }
  }, [isAuthenticated]);
  
  const loadUser = async () => {
    try {
      const response = await api.get('/api/users/me');
      setUser(response.data);
    } catch (err) {
      setError(err.message);
    }
  };
  
  const updateSettings = async (settings: Partial<User['settings']>) => {
    try {
      const response = await api.patch('/api/users/me/settings', settings);
      setUser(prev => prev ? { ...prev, settings: response.data } : null);
    } catch (err) {
      setError(err.message);
    }
  };
  
  if (isLoading) return <div>Loading...</div>;
  if (!isAuthenticated) return <div>Please log in</div>;
  if (error) return <div>Error: {error}</div>;
  if (!user) return <div>Loading user...</div>;
  
  return (
    <div>
      <img src={user.picture} alt={user.name} />
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      <p>Currency: {user.settings.currency}</p>
      
      <button onClick={() => updateSettings({ theme: 'dark' })}>
        Switch to Dark Mode
      </button>
    </div>
  );
}
```

---

## ⚠️ Error Handling

Handle authentication errors properly:

```tsx
const handleApiError = (error: any) => {
  if (error.code === 'UNAUTHORIZED' || error.code === 'TOKEN_EXPIRED') {
    // Token issues - trigger re-login
    loginWithRedirect();
  } else if (error.code === 'VALIDATION_ERROR') {
    // Show validation errors to user
    showValidationErrors(error.details);
  } else {
    // Generic error handling
    showToast('Something went wrong. Please try again.');
  }
};
```

---

## 🚀 CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative dev port)

For production, update `backend/.env`:

```env
CORS_ORIGINS=https://your-frontend-domain.com
```

---

## 📞 Contact

For questions about backend integration:

- **Backend Lead:** Suryadi Zhang
- **Email:** suryadizhang86@gmail.com
- **Slack:** #backend-team

---

## 📅 Changelog

| Date | Change |
|------|--------|
| Dec 16, 2025 | Initial document created |
