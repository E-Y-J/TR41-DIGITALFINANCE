# End-to-End (E2E) Testing

This folder contains Playwright end-to-end tests that test the full stack (Frontend + Backend).

## Tech Stack

- **Playwright** - Browser automation
- **JavaScript** - Test scripts

## Quick Start

### 1. Install Dependencies

```bash
cd shared/e2e
npm install
npx playwright install chromium
```

### 2. Start the Application

Make sure Docker containers are running:

```bash
# From project root
docker compose up -d

# Wait for all services to be healthy
docker compose ps
```

### 3. Run Tests

```bash
# Run all tests
npm test

# Run with browser UI visible
npm run test:headed

# Run only smoke tests
npm run test:smoke

# Run with Playwright UI (interactive)
npm run test:ui

# Debug mode
npm run test:debug

# View HTML report
npm run report
```

## Test Files

| File | Description | Status |
|------|-------------|--------|
| `smoke.spec.js` | Basic app loading & API health | ✅ Ready |
| `dashboard.spec.js` | Dashboard page tests | ✅ Ready |
| `transactions.spec.js` | Transaction CRUD operations | ✅ Ready |
| `ai-chat.spec.js` | AI chat functionality | ✅ Ready |

## Running in CI/CD

For GitHub Actions or other CI:

```yaml
- name: Run E2E Tests
  run: |
    cd shared/e2e
    npm ci
    npx playwright install chromium
    npm test
```

## Troubleshooting

**Tests fail with "Cannot connect"**
- Ensure Docker containers are running: `docker compose ps`
- Check backend health: `curl http://localhost:8000/health`
- Check frontend: `curl http://localhost:3000`

**Auth-related tests fail**
- Expected behavior - testing auth requires either:
  - Real Auth0 tokens (for production-like testing)
  - DEV_IMPERSONATION=true in backend (for dev testing)

**View test trace on failure**
```bash
npx playwright show-trace test-results/[test-name]/trace.zip
```
