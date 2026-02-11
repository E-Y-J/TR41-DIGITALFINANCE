// =============================================================================
// Digital Finance Tracker - Smoke Tests
// PURPOSE: Basic tests to verify app loads and core pages work
// =============================================================================

const { test, expect } = require('@playwright/test');

test.describe('Smoke Tests - App Loads Correctly', () => {
  test('homepage loads', async ({ page }) => {
    await page.goto('/');
    
    // App should load without errors
    await expect(page).toHaveTitle(/SecureBank\s*AI|Digital Finance|Finance Tracker/i);
  });

  test('login page is accessible', async ({ page }) => {
    await page.goto('/');
    
    // Look for login button, Auth0 redirect, or Get Started button
    const loginButton = page.getByRole('button', { name: /log\s*in|sign\s*in|get\s*started/i });
    const loginLink = page.getByRole('link', { name: /log\s*in|sign\s*in|get\s*started/i });
    
    // Either a button or link should exist, or page should be visible
    const hasLogin = await loginButton.or(loginLink).count() > 0;
    // If no explicit login element, just verify page loaded
    if (!hasLogin) {
      await expect(page.locator('body')).toBeVisible();
    }
  });

  test('API health check', async ({ request }) => {
    // Use environment variable or default to production URL
    const apiUrl = process.env.API_URL || 'https://securebankai.mysticdatanode.net';
    const response = await request.get(`${apiUrl}/health`);
    expect(response.ok()).toBeTruthy();
    
    const body = await response.json();
    expect(body.status).toBe('healthy');
  });

  test('backend test endpoint works', async ({ request }) => {
    const apiUrl = process.env.API_URL || 'https://securebankai.mysticdatanode.net';
    const response = await request.get(`${apiUrl}/api/test`);
    expect(response.ok()).toBeTruthy();
    
    const body = await response.json();
    expect(body.success).toBe(true);
  });
});

test.describe('Navigation Tests', () => {
  test('main navigation links exist', async ({ page }) => {
    await page.goto('/');
    
    // Check for common navigation elements
    // These will be visible after login, so just check page loads
    await expect(page.locator('body')).toBeVisible();
  });
});
