import { test, expect } from '@playwright/test';

test.describe('MealHistory Component E2E Tests', () => {
  // Before each test, login and navigate to meal history page
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Fill login form
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    
    // Submit login form
    await page.click('[data-testid="login-button"]');
    
    // Wait for dashboard to load
    await page.waitForSelector('[data-testid="dashboard"]');
    
    // Navigate to meal history page
    await page.click('[data-testid="meal-history-nav"]');
    
    // Wait for meal history to load
    await page.waitForSelector('[data-testid="meal-history-container"]', { state: 'visible' });
  });
  
  test('displays meal history and allows filtering', async ({ page }) => {
    // Check initial page load
    await expect(page.locator('[data-testid="meal-item"]')).toHaveCount.above(0);
    
    // Filter by date
    await page.fill('[data-testid="date-filter"]', '2024-06-01');
    await page.press('[data-testid="date-filter"]', 'Enter');
    
    // Wait for filter to apply
    await page.waitForResponse(response => 
      response.url().includes('/api/meals') && response.status() === 200
    );
    
    // Verify filtered results
    const dateText = await page.locator('[data-testid="meal-date"]').first().innerText();
    expect(dateText).toContain('01/06/2024');
    
    // Filter by meal type
    await page.click('[data-testid="meal-type-filter-breakfast"]');
    
    // Wait for filter to apply
    await page.waitForResponse(response => 
      response.url().includes('/api/meals') && response.status() === 200
    );
    
    // Verify that all visible meals are breakfast
    const mealTypes = await page.locator('[data-testid="meal-type-badge"]').allInnerTexts();
    for (const type of mealTypes) {
      expect(type).toContain('ארוחת בוקר');
    }
    
    // Clear filters
    await page.click('[data-testid="clear-filters"]');
    
    // Wait for filter to reset
    await page.waitForResponse(response => 
      response.url().includes('/api/meals') && response.status() === 200
    );
    
    // Verify more results are shown
    await expect(page.locator('[data-testid="meal-item"]')).toHaveCount.above(mealTypes.length);
  });
  
  test('adds a new meal', async ({ page }) => {
    // Count initial meals
    const initialCount = await page.locator('[data-testid="meal-item"]').count();
    
    // Click add meal button
    await page.click('[data-testid="add-meal-button"]');
    
    // Wait for meal form to appear
    await page.waitForSelector('[data-testid="meal-form"]', { state: 'visible' });
    
    // Fill form
    await page.selectOption('[data-testid="meal-type-select"]', 'dinner');
    await page.fill('[data-testid="meal-date"]', '2024-06-05');
    await page.fill('[data-testid="meal-time"]', '19:00');
    
    // Add food item
    await page.click('[data-testid="add-food-button"]');
    await page.fill('[data-testid="food-search"]', 'עוף');
    await page.click('[data-testid="food-item-0"]');
    await page.fill('[data-testid="food-amount"]', '150');
    
    // Save meal
    await page.click('[data-testid="save-meal-button"]');
    
    // Wait for success message
    await page.waitForSelector('[data-testid="success-alert"]', { state: 'visible' });
    
    // Check that new meal was added
    await page.waitForSelector('[data-testid="meal-history-container"]', { state: 'visible' });
    const newCount = await page.locator('[data-testid="meal-item"]').count();
    expect(newCount).toBeGreaterThan(initialCount);
    
    // Verify new meal data
    const mealTypes = await page.locator('[data-testid="meal-type-badge"]').allInnerTexts();
    expect(mealTypes).toContain('ארוחת ערב');
  });
  
  test('edits existing meal', async ({ page }) => {
    // Click edit button on first meal
    await page.click('[data-testid="edit-meal-0"]');
    
    // Wait for edit form to appear
    await page.waitForSelector('[data-testid="meal-form"]', { state: 'visible' });
    
    // Check prefilled form data
    const mealType = await page.inputValue('[data-testid="meal-type-select"]');
    const originalType = mealType;
    
    // Change meal type
    await page.selectOption('[data-testid="meal-type-select"]', 'snack');
    
    // Save changes
    await page.click('[data-testid="save-meal-button"]');
    
    // Wait for success message
    await page.waitForSelector('[data-testid="success-alert"]', { state: 'visible' });
    
    // Check that meal type was updated
    await page.waitForSelector('[data-testid="meal-history-container"]', { state: 'visible' });
    const updatedType = await page.locator('[data-testid="meal-type-badge"]').first().innerText();
    expect(updatedType).toContain('ארוחת ביניים');
    expect(updatedType).not.toEqual(originalType);
  });
  
  test('deletes a meal', async ({ page }) => {
    // Count initial meals
    const initialCount = await page.locator('[data-testid="meal-item"]').count();
    
    // Get ID of first meal to delete
    const mealId = await page.getAttribute('[data-testid="meal-item"]:first-child', 'data-meal-id');
    
    // Click delete button
    await page.click(`[data-testid="delete-meal-${mealId}"]`);
    
    // Wait for confirmation dialog
    await page.waitForSelector('[data-testid="confirm-dialog"]', { state: 'visible' });
    
    // Confirm deletion
    await page.click('[data-testid="confirm-delete"]');
    
    // Wait for success message
    await page.waitForSelector('[data-testid="success-alert"]', { state: 'visible' });
    
    // Check that meal was removed
    await page.waitForTimeout(500); // Wait for UI update
    const newCount = await page.locator('[data-testid="meal-item"]').count();
    expect(newCount).toBeLessThan(initialCount);
  });
  
  test('switches between list and grid views', async ({ page }) => {
    // Check default view (list)
    await expect(page.locator('[data-testid="list-view"]')).toBeVisible();
    await expect(page.locator('[data-testid="grid-view"]')).not.toBeVisible();
    
    // Switch to grid view
    await page.click('[data-testid="grid-view-toggle"]');
    
    // Verify grid view is displayed
    await expect(page.locator('[data-testid="grid-view"]')).toBeVisible();
    await expect(page.locator('[data-testid="list-view"]')).not.toBeVisible();
    
    // Switch back to list view
    await page.click('[data-testid="list-view-toggle"]');
    
    // Verify list view is displayed
    await expect(page.locator('[data-testid="list-view"]')).toBeVisible();
    await expect(page.locator('[data-testid="grid-view"]')).not.toBeVisible();
  });
  
  test('exports meal history data', async ({ page, context }) => {
    // Setup download listener
    const downloadPromise = page.waitForEvent('download');
    
    // Click export button
    await page.click('[data-testid="export-button"]');
    
    // Select CSV format from dropdown
    await page.click('[data-testid="export-csv"]');
    
    // Wait for download to start
    const download = await downloadPromise;
    
    // Verify file name
    expect(download.suggestedFilename()).toContain('meal-history');
    expect(download.suggestedFilename()).toContain('.csv');
  });
  
  test('shares meal history with healthcare provider', async ({ page }) => {
    // Click share button
    await page.click('[data-testid="share-button"]');
    
    // Wait for share dialog
    await page.waitForSelector('[data-testid="share-dialog"]', { state: 'visible' });
    
    // Fill provider email
    await page.fill('[data-testid="provider-email"]', 'doctor@example.com');
    
    // Set expiration date
    await page.fill('[data-testid="share-expiration"]', '2024-07-01');
    
    // Select data to share
    await page.click('[data-testid="share-meals"]');
    await page.click('[data-testid="share-health-logs"]');
    
    // Confirm share
    await page.click('[data-testid="confirm-share"]');
    
    // Wait for success message
    await page.waitForSelector('[data-testid="success-alert"]', { state: 'visible' });
    
    // Verify share link is displayed
    await expect(page.locator('[data-testid="share-link"]')).toBeVisible();
  });
  
  test('analyzing meal patterns', async ({ page }) => {
    // Click analyze button
    await page.click('[data-testid="analyze-meals-button"]');
    
    // Wait for analytics to load
    await page.waitForSelector('[data-testid="meal-analytics"]', { state: 'visible' });
    
    // Verify charts are displayed
    await expect(page.locator('[data-testid="meal-distribution-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="meal-timing-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="most-frequent-foods"]')).toBeVisible();
    
    // Check for insights section
    await expect(page.locator('[data-testid="meal-insights"]')).toBeVisible();
    
    // Return to meal history
    await page.click('[data-testid="back-to-history"]');
    
    // Verify we're back to meal history
    await expect(page.locator('[data-testid="meal-history-container"]')).toBeVisible();
  });
  
  test('applies complex date range filters', async ({ page }) => {
    // Open advanced filters
    await page.click('[data-testid="advanced-filters-toggle"]');
    
    // Wait for advanced filters to appear
    await page.waitForSelector('[data-testid="advanced-filters"]', { state: 'visible' });
    
    // Set date range
    await page.fill('[data-testid="date-range-start"]', '2024-06-01');
    await page.fill('[data-testid="date-range-end"]', '2024-06-30');
    
    // Select multiple meal types
    await page.click('[data-testid="meal-type-breakfast-checkbox"]');
    await page.click('[data-testid="meal-type-dinner-checkbox"]');
    
    // Filter by food containing
    await page.fill('[data-testid="food-contains"]', 'ירקות');
    
    // Apply filters
    await page.click('[data-testid="apply-filters"]');
    
    // Wait for filtered results
    await page.waitForResponse(response => 
      response.url().includes('/api/meals') && response.status() === 200
    );
    
    // Verify filter chips are displayed
    await expect(page.locator('[data-testid="filter-chip-date-range"]')).toBeVisible();
    await expect(page.locator('[data-testid="filter-chip-meal-types"]')).toBeVisible();
    await expect(page.locator('[data-testid="filter-chip-food"]')).toBeVisible();
    
    // Verify results include the food
    const mealContents = await page.locator('[data-testid="meal-foods"]').allInnerTexts();
    const hasVegetables = mealContents.some(content => content.includes('ירקות'));
    expect(hasVegetables).toBeTruthy();
  });
}); 