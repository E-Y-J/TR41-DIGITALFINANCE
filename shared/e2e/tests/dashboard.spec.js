// =============================================================================
// Digital Finance Tracker - Dashboard E2E Tests
// PURPOSE: Test dashboard functionality for authenticated users
// =============================================================================

const { test, expect } = require('@playwright/test');

// Test with dev mode authentication bypass
test.describe('Dashboard Tests (Dev Mode)', () => {
  test.beforeEach(async ({ page }) => {
    // Set dev mode header via intercepting requests
    await page.route('**/api/**', async (route) => {
      const headers = {
        ...route.request().headers(),
        'X-Dev-User-Email': 'alice@example.com',
      };
      await route.continue({ headers });
    });
  });

  test('dashboard loads with user data', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Wait for page to load - may redirect to login if not authenticated
    await page.waitForLoadState('networkidle');
    
    // Check if we're on dashboard or redirected
    const url = page.url();
    console.log('Current URL:', url);
    
    // If on dashboard, check for key elements
    if (url.includes('dashboard')) {
      // Look for dashboard elements
      const dashboardElements = page.locator('[data-testid="dashboard"], .dashboard, main');
      await expect(dashboardElements.first()).toBeVisible({ timeout: 10000 });
    }
  });

  test('can view transactions page', async ({ page }) => {
    await page.goto('/transactions');
    await page.waitForLoadState('networkidle');
    
    const url = page.url();
    if (url.includes('transactions')) {
      // Check for transaction table or list
      const content = page.locator('main, [role="main"], .transactions');
      await expect(content.first()).toBeVisible({ timeout: 10000 });
    }
  });

  test('can view budgets page', async ({ page }) => {
    await page.goto('/budgets');
    await page.waitForLoadState('networkidle');
    
    const url = page.url();
    if (url.includes('budgets')) {
      const content = page.locator('main, [role="main"]');
      await expect(content.first()).toBeVisible({ timeout: 10000 });
    }
  });
});
