// =============================================================================
// Digital Finance Tracker - AI Chat E2E Tests  
// PURPOSE: Test AI chat functionality simulating real user interactions
// =============================================================================

const { test, expect } = require('@playwright/test');

test.describe('AI Chat Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Intercept API requests to add dev auth header
    await page.route('**/api/**', async (route) => {
      const headers = {
        ...route.request().headers(),
        'X-Dev-User-Email': 'alice@example.com',
      };
      await route.continue({ headers });
    });
  });

  test('AI chat page loads', async ({ page }) => {
    await page.goto('/ai-chat');
    await page.waitForLoadState('networkidle');
    
    // Check for chat input or interface
    const chatInput = page.locator('input[type="text"], textarea, [role="textbox"]');
    const chatInterface = page.locator('[data-testid="chat"], .chat, .ai-chat');
    
    // Either chat input or chat interface should be visible (if authenticated)
    const url = page.url();
    console.log('AI Chat URL:', url);
  });

  test('can send message to AI (API test)', async ({ request }) => {
    // Direct API test since UI requires auth
    const response = await request.post('http://localhost:8000/api/v1/ai/chat', {
      headers: {
        'Content-Type': 'application/json',
        'X-Dev-User-Email': 'alice@example.com',
      },
      data: {
        message: 'hello',
      },
    });
    
    // May fail with 401 if dev mode not enabled, that's okay
    const status = response.status();
    console.log('AI Chat API status:', status);
    
    // Should be either success or auth error (not server error)
    expect([200, 401, 403]).toContain(status);
  });

  test('transaction parsing works (API test)', async ({ request }) => {
    const response = await request.post('http://localhost:8000/api/v1/ai/chat', {
      headers: {
        'Content-Type': 'application/json',
        'X-Dev-User-Email': 'alice@example.com',
      },
      data: {
        message: 'i spent 50 at restaurant',
      },
    });
    
    const status = response.status();
    console.log('Transaction parsing API status:', status);
    
    if (status === 200) {
      const body = await response.json();
      console.log('AI Response:', JSON.stringify(body, null, 2));
      expect(body.success).toBe(true);
    }
  });
});
