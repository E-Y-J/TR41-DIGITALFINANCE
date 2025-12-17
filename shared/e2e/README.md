# End-to-End (E2E) Testing

This folder contains Playwright end-to-end tests that test the full stack (Frontend + Backend).

## Tech Stack

- **Playwright** - Browser automation
- **TypeScript/JavaScript** - Test scripts

## Setup

```bash
cd shared/e2e
npm install
npx playwright install
```

## Running Tests

```bash
# Run all tests
npx playwright test

# Run with UI
npx playwright test --ui

# Run specific test file
npx playwright test tests/auth.spec.ts
```

## Test Files to Create

| File | Description | Owner |
|------|-------------|-------|
| `auth.spec.ts` | Login/Register flows | QA |
| `transactions.spec.ts` | Transaction CRUD | QA |
| `dashboard.spec.ts` | Dashboard loads correctly | QA |
| `ai-features.spec.ts` | AI categorization works | QA |

## Configuration

Create `playwright.config.ts`:
```typescript
export default {
  baseURL: 'http://localhost:5173',
  testDir: './tests',
  use: {
    trace: 'on-first-retry',
  },
};
```
