# Postman Collections

This folder contains Postman collections and environment files for API testing.

## Files to Create Here

| File | Description | Owner |
|------|-------------|-------|
| `digital-finance.postman_collection.json` | Full API collection | Backend |
| `local.postman_environment.json` | Local development env vars | Backend |
| `staging.postman_environment.json` | Staging env vars | Backend/CS |

## How to Import

1. Open Postman
2. Click **Import** button
3. Select the `.json` files from this folder

## Naming Convention

- Collections: `digital-finance-{feature}.postman_collection.json`
- Environments: `{env-name}.postman_environment.json`

## Testing Workflow

1. Run auth tests first (get token)
2. Token auto-saves to environment
3. Run other tests with saved token

## Required Environment Variables

```
{{BASE_URL}} = http://localhost:5000/api
{{ACCESS_TOKEN}} = (auto-populated after login)
{{USER_EMAIL}} = test@example.com
{{USER_PASSWORD}} = testpassword123
```
