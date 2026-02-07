import { test, expect } from '@playwright/test'

test.describe('Workflow Creation E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login')
    await page.fill('[data-testid="email"]', 'test@example.com')
    await page.fill('[data-testid="password"]', 'password123')
    await page.click('button[type="submit"]')
    await page.waitForURL('/dashboard')
  })

  test('creates new workflow from scratch', async ({ page }) => {
    // Arrange
    await page.goto('/workflows')
    await page.click('text=Create Workflow')

    // Act - Fill in workflow details
    await page.fill('[data-testid="workflow-name"]', 'E2E Test Workflow')
    await page.fill('[data-testid="workflow-description"]', 'Testing workflow creation end-to-end')
    await page.selectOption('[data-testid="trigger-type"]', 'webhook')

    // Act - Create workflow
    await page.click('text=Create')

    // Assert
    await expect(page).toHaveURL(/\/workflows\/[a-f0-9-]+$/)
    await expect(page.locator('text=E2E Test Workflow')).toBeVisible()
    await expect(page.locator('[data-testid="workflow-status"]')).toContainText('Draft')
  })

  test('adds trigger to workflow', async ({ page }) => {
    // Arrange
    await page.goto('/workflows/create')
    await page.fill('[data-testid="workflow-name"]', 'Workflow with Trigger')
    await page.click('text=Create')

    // Act
    await page.click('[data-testid="add-trigger-button"]')
    await page.click('text=Webhook')
    await page.fill('[data-testid="webhook-url"]', '/webhooks/test-webhook')
    await page.click('text=Save Trigger')

    // Assert
    await expect(page.locator('text=Webhook')).toBeVisible()
    await expect(page.locator('[data-testid="trigger-config"]')).toContainText('/webhooks/test-webhook')
  })

  test('adds action step to workflow', async ({ page }) => {
    // Arrange
    await page.goto('/workflows/create')
    await page.fill('[data-testid="workflow-name"]', 'Workflow with Action')
    await page.click('text=Create')

    // Act
    await page.click('[data-testid="add-step-button"]')
    await page.click('text=Send Email')

    // Fill in email action details
    await page.fill('[data-testid="email-to"]', '{{contact.email}}')
    await page.fill('[data-testid="email-subject"]', 'Test Email Subject')
    await page.fill('[data-testid="email-body"]', 'Test email body content')
    await page.click('text=Save Step')

    // Assert
    await expect(page.locator('text=Send Email')).toBeVisible()
    await expect(page.locator('[data-testid="step-count"]')).toContainText('1')
  })

  test('adds condition step to workflow', async ({ page }) => {
    // Arrange
    await page.goto('/workflows/create')
    await page.fill('[data-testid="workflow-name"]', 'Workflow with Condition')
    await page.click('text=Create')

    // Act
    await page.click('[data-testid="add-step-button"]')
    await page.click('text=Condition')
    await page.selectOption('[data-testid="condition-field"]', 'status')
    await page.selectOption('[data-testid="condition-operator"]', 'equals')
    await page.fill('[data-testid="condition-value"]', 'premium')
    await page.click('text=Save Step')

    // Assert
    await expect(page.locator('[data-testid="condition-display"]')).toBeVisible()
    await expect(page.locator('text=status equals premium')).toBeVisible()
  })

  test('adds wait step to workflow', async ({ page }) => {
    // Arrange
    await page.goto('/workflows/create')
    await page.fill('[data-testid="workflow-name"]', 'Workflow with Wait')
    await page.click('text=Create')

    // Act
    await page.click('[data-testid="add-step-button"]')
    await page.click('text=Wait')
    await page.fill('[data-testid="wait-duration"]', '30')
    await page.selectOption('[data-testid="wait-unit"]', 'minutes')
    await page.click('text=Save Step')

    // Assert
    await expect(page.locator('text=Wait 30 minutes')).toBeVisible()
  })

  test('activates workflow successfully', async ({ page }) => {
    // Arrange
    await page.goto('/workflows/create')
    await page.fill('[data-testid="workflow-name"]', 'Workflow to Activate')
    await page.click('text=Create')

    // Add a trigger (required for activation)
    await page.click('[data-testid="add-trigger-button"]')
    await page.click('text=Webhook')
    await page.click('text=Save Trigger')

    // Act
    await page.click('[data-testid="activate-workflow-button"]')
    await page.click('text=Confirm') // Confirmation dialog

    // Assert
    await expect(page.locator('[data-testid="workflow-status"]')).toContainText('Active')
    await expect(page.locator('[data-testid="activate-workflow-button"]')).toBeDisabled()
  })

  test('validates workflow name cannot be empty', async ({ page }) => {
    // Arrange
    await page.goto('/workflows/create')

    // Act - Try to create without name
    await page.click('text=Create')

    // Assert
    await expect(page.locator('text=Workflow name is required')).toBeVisible()
  })

  test('validates trigger is required before activation', async ({ page }) => {
    // Arrange
    await page.goto('/workflows/create')
    await page.fill('[data-testid="workflow-name"]', 'Workflow without Trigger')
    await page.click('text=Create')

    // Act - Try to activate without trigger
    await page.click('[data-testid="activate-workflow-button"]')

    // Assert
    await expect(page.locator('text=Workflow must have a trigger')).toBeVisible()
  })

  test('clones existing workflow', async ({ page }) => {
    // Arrange
    await page.goto('/workflows')
    // Create a workflow to clone
    await page.click('text=Create Workflow')
    await page.fill('[data-testid="workflow-name"]', 'Original Workflow')
    await page.click('text=Create')

    // Act
    await page.click('[data-testid="workflow-menu-button"]')
    await page.click('text=Clone')
    await page.fill('[data-testid="workflow-name"]', 'Cloned Workflow')
    await page.click('text=Create')

    // Assert
    await expect(page.locator('text=Cloned Workflow')).toBeVisible()
    await expect(page.locator('[data-testid="workflow-status"]')).toContainText('Draft')
  })

  test('deletes draft workflow', async ({ page }) => {
    // Arrange
    await page.goto('/workflows')
    await page.click('text=Create Workflow')
    await page.fill('[data-testid="workflow-name"]', 'Workflow to Delete')
    await page.click('text=Create')

    // Act
    await page.click('[data-testid="workflow-menu-button"]')
    await page.click('text=Delete')
    await page.click('text=Confirm') // Confirmation dialog

    // Assert
    await expect(page.locator('text=Workflow to Delete')).not.toBeVisible()
  })

  test('exports workflow configuration', async ({ page }) => {
    // Arrange
    await page.goto('/workflows/create')
    await page.fill('[data-testid="workflow-name"]', 'Export Test Workflow')
    await page.click('text=Create')

    // Act
    const downloadPromise = page.waitForEvent('download')
    await page.click('[data-testid="export-button"]')
    const download = await downloadPromise

    // Assert
    expect(download.suggestedFilename()).toContain('export-test-workflow')
  })

  test('searches and filters workflows', async ({ page }) => {
    // Arrange
    await page.goto('/workflows')

    // Create multiple workflows
    for (let i = 1; i <= 5; i++) {
      await page.click('text=Create Workflow')
      await page.fill('[data-testid="workflow-name"]', `Search Test Workflow ${i}`)
      await page.click('text=Create')
      await page.goto('/workflows')
    }

    // Act - Search
    await page.fill('[data-testid="search-input"]', 'Search Test Workflow 3')

    // Assert
    await expect(page.locator('text=Search Test Workflow 3')).toBeVisible()
    await expect(page.locator('text=Search Test Workflow 1')).not.toBeVisible()

    // Act - Filter by status
    await page.fill('[data-testid="search-input"]', '') // Clear search
    await page.selectOption('[data-testid="status-filter"]', 'draft')

    // Assert - All should be draft
    const workflows = await page.locator('[data-testid="workflow-item"]').count()
    expect(workflows).toBeGreaterThan(0)
  })
})

test.describe('Workflow Execution E2E', () => {
  test('executes manual trigger workflow', async ({ page }) => {
    // Arrange
    await page.goto('/workflows')
    await page.click('text=Create Workflow')
    await page.fill('[data-testid="workflow-name"]', 'Manual Execution Test')
    await page.click('[data-testid="add-trigger-button"]')
    await page.click('text=Manual Trigger')
    await page.click('text=Save Trigger')
    await page.click('text=Create')
    await page.click('[data-testid="activate-workflow-button"]')
    await page.click('text=Confirm')

    // Act
    await page.click('[data-testid="execute-now-button"]')

    // Assert
    await expect(page.locator('text=Workflow executed successfully')).toBeVisible()
  })

  test('views workflow execution history', async ({ page }) => {
    // Arrange
    await page.goto('/workflows')
    await page.click('[data-testid="workflow-item"]') // Click on a workflow

    // Act
    await page.click('[data-testid="executions-tab"]')

    // Assert
    await expect(page.locator('[data-testid="execution-history"]')).toBeVisible()
  })
})

test.describe('Workflow Analytics E2E', () => {
  test('views workflow execution metrics', async ({ page }) => {
    // Arrange
    await page.goto('/workflows')
    await page.click('[data-testid="workflow-item"]')

    // Act
    await page.click('[data-testid="analytics-tab"]')

    // Assert
    await expect(page.locator('text=Execution Count')).toBeVisible()
    await expect(page.locator('text=Success Rate')).toBeVisible()
    await expect(page.locator('text=Average Duration')).toBeVisible()
  })

  test('exports analytics report', async ({ page }) => {
    // Arrange
    await page.goto('/workflows')
    await page.click('[data-testid="workflow-item"]')
    await page.click('[data-testid="analytics-tab"]')

    // Act
    const downloadPromise = page.waitForEvent('download')
    await page.click('[data-testid="export-analytics-button"]')
    const download = await downloadPromise

    // Assert
    expect(download.suggestedFilename()).toMatch(/\.(csv|xlsx)$/)
  })
})
