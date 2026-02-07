import { test, expect, type Page } from '@playwright/test';

test.describe('Workflow Management', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to workflows page
    await page.goto('/workflows');
    await page.waitForLoadState('networkidle');
  });

  test('should display workflows list', async ({ page }) => {
    // Check if workflows are displayed
    await expect(page.locator('table')).toBeVisible();
    await expect(page.getByText('Workflows')).toBeVisible();
  });

  test('should create new workflow', async ({ page }) => {
    // Click create button
    await page.click('button:has-text("Create Workflow")');

    // Fill form
    await page.fill('input[name="name"]', 'Test Workflow');
    await page.fill('textarea[name="description"]', 'Test Description');

    // Submit form
    await page.click('button:has-text("Create")');

    // Wait for navigation
    await page.waitForURL(/\/workflows\/[a-z0-9-]+/);

    // Verify success
    await expect(page.getByText('Test Workflow')).toBeVisible();
  });

  test('should navigate to workflow builder', async ({ page }) => {
    // Click on a workflow
    const firstWorkflow = page.locator('table tbody tr').first();
    await firstWorkflow.click();

    // Wait for navigation
    await page.waitForURL(/\/workflows\/[a-z0-9-]+\/builder/);

    // Verify builder loaded
    await expect(page.locator('[data-testid="workflow-builder"]')).toBeVisible();
  });

  test('should add action to workflow', async ({ page }) => {
    // Navigate to builder
    await page.goto('/workflows/test-id/builder');
    await page.waitForLoadState('networkidle');

    // Open action sidebar
    await page.click('[data-testid="add-action-button"]');

    // Select email action
    await page.click('text=Send Email');

    // Verify action added
    await expect(page.locator('[data-testid="action-node"]')).toBeVisible();
  });

  test('should save workflow', async ({ page }) => {
    // Navigate to builder
    await page.goto('/workflows/test-id/builder');
    await page.waitForLoadState('networkidle');

    // Click save button
    await page.click('button:has-text("Save")');

    // Wait for success message
    await expect(page.getByText('Workflow saved successfully')).toBeVisible();
  });
});

test.describe('Analytics Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/workflows/test-id/analytics');
    await page.waitForLoadState('networkidle');
  });

  test('should display metrics', async ({ page }) => {
    // Check metrics cards
    await expect(page.getByText('Total Enrolled')).toBeVisible();
    await expect(page.getByText('Currently Active')).toBeVisible();
    await expect(page.getByText('Completed')).toBeVisible();
  });

  test('should display funnel chart', async ({ page }) => {
    await expect(page.getByText('Workflow Funnel')).toBeVisible();
  });

  test('should change date range', async ({ page }) => {
    // Open date picker
    await page.click('[aria-label="Select date range"]');

    // Select preset
    await page.click('text=Last 30 days');

    // Wait for data refresh
    await page.waitForTimeout(1000);

    // Verify date changed
    await expect(page.getByText('Last 30 days')).toBeVisible();
  });

  test('should export analytics data', async ({ page }) => {
    // Click export button
    await page.click('button:has-text("Export")');

    // Click CSV export
    await page.click('text=Export as CSV');

    // Wait for download (verify in downloads folder)
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('text=Export as CSV'),
    ]);

    expect(download.suggestedFilename()).toContain('.csv');
  });
});

test.describe('Execution Logs', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/workflows/test-id/executions');
    await page.waitForLoadState('networkidle');
  });

  test('should display execution list', async ({ page }) => {
    await expect(page.getByText('Execution Logs')).toBeVisible();
    await expect(page.locator('[data-testid="execution-list"]')).toBeVisible();
  });

  test('should filter executions by status', async ({ page }) => {
    // Open status filter
    await page.click('[aria-label="Filter by status"]');

    // Select error status
    await page.click('text=Error');

    // Wait for filter
    await page.waitForTimeout(500);

    // Verify filtered results
    const statusBadges = page.locator('[data-testid="execution-status"]');
    for (const badge of await statusBadges.all()) {
      await expect(badge).toHaveText(/error/i);
    }
  });

  test('should search executions', async ({ page }) => {
    // Type search query
    await page.fill('input[placeholder*="search"]', 'john@example.com');

    // Wait for search
    await page.waitForTimeout(500);

    // Verify results
    await expect(page.getByText('john@example.com')).toBeVisible();
  });

  test('should open execution detail modal', async ({ page }) => {
    // Click first execution
    await page.click('[data-testid="execution-item"]:first-child');

    // Verify modal opened
    await expect(page.getByText('Execution Details')).toBeVisible();
  });
});

test.describe('Template Marketplace', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/templates');
    await page.waitForLoadState('networkidle');
  });

  test('should display template gallery', async ({ page }) => {
    await expect(page.locator('[data-testid="template-gallery"]')).toBeVisible();
  });

  test('should filter templates by category', async ({ page }) => {
    // Open category filter
    await page.click('[aria-label="Filter by category"]');

    // Select category
    await page.click('text=Lead Nurturing');

    // Wait for filter
    await page.waitForTimeout(500);

    // Verify filtered templates
    const templates = page.locator('[data-testid="template-card"]');
    await expect(templates.first()).toBeVisible();
  });

  test('should preview template', async ({ page }) => {
    // Click first template
    await page.click('[data-testid="template-card"]:first-child');

    // Verify preview modal opened
    await expect(page.getByText('Use This Template')).toBeVisible();
  });

  test('should instantiate template', async ({ page }) => {
    // Click template
    await page.click('[data-testid="template-card"]:first-child');

    // Click use template button
    await page.click('button:has-text("Use This Template")');

    // Wait for navigation
    await page.waitForURL(/\/workflows\/[a-z0-9-]+\/builder/);

    // Verify success
    await expect(page.locator('[data-testid="workflow-builder"]')).toBeVisible();
  });
});

test.describe('Accessibility', () => {
  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/workflows');

    // Tab through interactive elements
    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toBeVisible();

    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toBeVisible();
  });

  test('should have skip links', async ({ page }) => {
    await page.goto('/workflows');

    // Focus skip link
    await page.keyboard.press('Tab');

    // Should show skip link on focus
    await expect(page.getByText('Skip to main content')).toBeVisible();
  });

  test('should have proper ARIA labels', async ({ page }) => {
    await page.goto('/workflows');

    // Check ARIA labels on buttons
    const buttons = page.locator('button[aria-label]');
    await expect(buttons.first()).toBeVisible();
  });
});
