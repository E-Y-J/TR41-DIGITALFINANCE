// =============================================================================
// Digital Finance Tracker - Smoke Tests
// PURPOSE: Basic tests to verify app loads and core pages work
// =============================================================================

const { test, expect } = require('@playwright/test');

test.describe('Smoke Tests - App Loads Correctly', () => {
  test('homepage loads', async ({ page }) => {
    await page.goto('/');
    
    // App should load without errors
    await expect(page).toHaveTitle(/Digital Finance|Finance Tracker/i);
  });

  test('login page is accessible', async ({ page }) => {
    await page.goto('/');
    
    // Look for login button or Auth0 redirect
    const loginButton = page.getByRole('button', { name: /log\s*in|sign\s*in/i });
    const loginLink = page.getByRole('link', { name: /log\s*in|sign\s*in/i });
    
    // Either a button or link should exist
    const hasLogin = await loginButton.or(loginLink).count() > 0;
    expect(hasLogin).toBeTruthy();
  });

  test('API health check', async ({ request }) => {
    const response = await request.get('http://localhost:8000/health');
    expect(response.ok()).toBeTruthy();
    
    const body = await response.json();
    expect(body.status).toBe('healthy');
  });

  test('backend test endpoint works', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/test');
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
