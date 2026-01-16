# User Model Simplification - Configuration Guide

## Overview

This document describes the simplified User model and the required Auth0 configuration to make it work properly.

---

## Changes Made (January 15, 2026)

### Fields Removed from User Model

| Field | Reason |
|-------|--------|
| `email_verified` | Trust Auth0 to handle email verification |
| `nickname` | Not used in the application |
| `picture` | Frontend gets profile picture directly from Auth0 |

### Current User Model Structure

```python
User Model:
├── id              # UUID - Primary key
├── auth0_id        # String - Links to Auth0 (sub claim)
├── email           # String - User email address
├── first_name      # String - From Auth0 given_name
├── last_name       # String - From Auth0 family_name
├── account_status  # Enum - pending/active/suspended/deactivated
├── role            # Enum - user/admin
├── salary_amount   # Decimal - For budgeting features
├── settings        # JSONB - User preferences
├── created_at      # DateTime - Account creation timestamp
├── updated_at      # DateTime - Last update timestamp
└── last_login      # DateTime - Last login timestamp
```

### Files Modified

1. `backend/app/models/user.py` - Removed fields from model
2. `backend/app/schemas/user_schema.py` - Removed fields from schemas
3. `backend/app/auth/user_sync.py` - Simplified user creation from claims
4. `backend/app/services/user_service.py` - Removed nickname handling

---

## Auth0 Dashboard Configuration (REQUIRED)

### Why This Is Needed

By default, Auth0 access tokens only contain the `sub` claim (user ID). To get `email`, `given_name`, and `family_name` in the access token, we need to add a custom Auth0 Action.

Without this configuration:
- `g.current_user` will only have `sub` (auth0_id)
- `email`, `first_name`, `last_name` will be NULL in the database
- User sync will fail or create incomplete records

### Step-by-Step Instructions

#### Step 1: Log into Auth0 Dashboard

1. Go to [https://manage.auth0.com](https://manage.auth0.com)
2. Select your tenant (the one your app uses)

#### Step 2: Navigate to Actions

1. In the left sidebar, click **Actions**
2. Click **Flows**
3. Select **Login**

#### Step 3: Create a Custom Action

1. On the Login flow page, click **"+" (Add Action)**
2. Select **"Build from scratch"**
3. Fill in the details:
   - **Name:** `Add User Info to Access Token`
   - **Trigger:** `Login / Post Login`
   - **Runtime:** Node 18 (default)
4. Click **Create**

#### Step 4: Add the Action Code

Replace the default code with:

```javascript
/**
 * Handler that adds user profile info to the access token.
 * This allows the backend to receive email and name without extra API calls.
 *
 * @param {Event} event - Details about the user and the context
 * @param {PostLoginAPI} api - Interface to modify token claims
 */
exports.onExecutePostLogin = async (event, api) => {
  // Add email to access token
  if (event.user.email) {
    api.accessToken.setCustomClaim('email', event.user.email);
  }

  // Add name fields to access token
  // Auth0 uses given_name and family_name (OIDC standard)
  if (event.user.given_name) {
    api.accessToken.setCustomClaim('given_name', event.user.given_name);
  }

  if (event.user.family_name) {
    api.accessToken.setCustomClaim('family_name', event.user.family_name);
  }

  // Fallback: If given_name/family_name not set, try to split 'name'
  if (!event.user.given_name && !event.user.family_name && event.user.name) {
    api.accessToken.setCustomClaim('name', event.user.name);
  }
};
```

#### Step 5: Deploy the Action

1. Click **"Deploy"** button in the top right
2. Wait for deployment to complete (green checkmark)

#### Step 6: Add Action to Login Flow

1. Go back to **Actions** → **Flows** → **Login**
2. You'll see your new action in the right panel under "Custom"
3. **Drag** `Add User Info to Access Token` into the flow
4. Place it between **Start** and **Complete**
5. Click **"Apply"** to save the flow

#### Step 7: Test the Configuration

1. Log out of your application
2. Log back in
3. Check the backend logs to verify `g.current_user` contains:
   ```json
   {
     "sub": "auth0|507f1f77bcf86cd799439011",
     "email": "user@example.com",
     "given_name": "John",
     "family_name": "Doe",
     ...
   }
   ```

---

## Database Migration

After the code changes and Auth0 configuration, you need to update the database:

### Option 1: Drop and Recreate (Development Only)

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Drop all tables and recreate
flask db downgrade base
flask db upgrade
```

### Option 2: Create a Migration (Production)

```bash
# Create migration for the column drops
flask db migrate -m "Remove email_verified, nickname, picture from users"

# Review the generated migration file
# Then apply it
flask db upgrade
```

**Note:** If you get foreign key errors, you may need to drop the database entirely in development:

```sql
-- Connect to PostgreSQL and drop the database
DROP DATABASE IF EXISTS digital_finance_dev;
CREATE DATABASE digital_finance_dev;
```

Then run:
```bash
flask db upgrade
```

---

## API Response Changes

### Before (Old Response)

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "auth0_id": "auth0|123",
    "email": "user@example.com",
    "email_verified": true,
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "nickname": "johnd",
    "picture": "https://...",
    "account_status": "active",
    "role": "user",
    "salary_amount": "0.00",
    "settings": {...},
    "created_at": "...",
    "updated_at": "...",
    "last_login": "..."
  }
}
```

### After (New Response)

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "auth0_id": "auth0|123",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "account_status": "active",
    "role": "user",
    "salary_amount": "0.00",
    "settings": {...},
    "created_at": "...",
    "updated_at": "...",
    "last_login": "..."
  }
}
```

---

## Frontend Impact

The frontend team needs to be aware:

1. **Removed fields from API response:**
   - `email_verified` - No longer returned
   - `nickname` - No longer returned
   - `picture` - No longer returned

2. **Profile picture:**
   - Get directly from Auth0 via `auth0.getUser().picture`
   - Or use Auth0's ID token which contains the picture URL

3. **Update any code** that references these removed fields

---

## Troubleshooting

### Issue: Email/Name still NULL after login

**Cause:** Auth0 Action not configured or not in the flow

**Solution:**
1. Verify the Action is deployed (green checkmark)
2. Verify the Action is in the Login flow (between Start and Complete)
3. Check Auth0 logs for any Action errors

### Issue: Migration fails with "column does not exist"

**Cause:** Database schema mismatch

**Solution:**
1. Drop the database and recreate (development)
2. Or manually drop the columns:
   ```sql
   ALTER TABLE users DROP COLUMN IF EXISTS email_verified;
   ALTER TABLE users DROP COLUMN IF EXISTS nickname;
   ALTER TABLE users DROP COLUMN IF EXISTS picture;
   ```

### Issue: given_name/family_name not in token

**Cause:** User signed up with social login (Google, etc.) and these fields weren't set

**Solution:** The `_parse_name_from_claims()` function handles fallbacks:
1. First tries `given_name` / `family_name`
2. Falls back to splitting `name` field
3. Falls back to `nickname`
4. Falls back to email prefix

---
