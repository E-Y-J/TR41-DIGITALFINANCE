// =============================================================================
// Digital Finance Tracker - Playwright E2E Test Configuration
// PURPOSE: Configure Playwright for end-to-end testing
// =============================================================================

const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  
  // Run tests in parallel
  fullyParallel: true,
  
  // Fail the build on CI if you accidentally left test.only
  forbidOnly: !!process.env.CI,
  
  // Retry once on failure
  retries: process.env.CI ? 2 : 1,
  
  // Use 2 workers for parallel execution
  workers: process.env.CI ? 1 : 2,
  
  // Reporter configuration
  reporter: [
    ['html', { open: 'never' }],
    ['list'],
  ],
  
  // Global test timeout
  timeout: 30000,
  
  use: {
    // Base URL for the frontend
    baseURL: process.env.FRONTEND_URL || 'http://localhost:3000',
    
    // Collect trace when retrying failed test
    trace: 'on-first-retry',
    
    // Take screenshot on failure
    screenshot: 'only-on-failure',
    
    // Video on first retry
    video: 'on-first-retry',
    
    // Browser viewport
    viewport: { width: 1280, height: 720 },
  },

  // Configure projects for major browsers
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
  ],

  // Run local dev server before starting tests (optional)
  // Uncomment if you want Playwright to start the servers
  // webServer: [
  //   {
  //     command: 'docker compose up -d',
  //     url: 'http://localhost:3000',
  //     reuseExistingServer: true,
  //     timeout: 120000,
  //   },
  // ],
});
