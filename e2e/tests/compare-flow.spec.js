import { test, expect } from '@playwright/test';

test.describe('Compare Flow', () => {
  test('should load compare page', async ({ page }) => {
    await page.goto('/compare');
    await expect(page.locator('text=Compare Approaches')).toBeVisible();
  });

  test('should run comparison', async ({ page }) => {
    await page.goto('/compare');
    await page.fill('textarea', 'predict 5.1 3.5 1.4 0.2');
    await page.click('text=Compare Both');
    // Should show two result columns
    await expect(page.locator('text=Key Differences')).toBeVisible({ timeout: 10000 });
  });

  test('should show VS divider after comparison', async ({ page }) => {
    await page.goto('/compare');
    await page.fill('textarea', 'compare setosa and versicolor');
    await page.click('text=Compare Both');
    await expect(page.getByText('VS', { exact: true })).toBeVisible({ timeout: 10000 });
  });

  test('should show function call and combined tools result cards', async ({ page }) => {
    await page.goto('/compare');
    await page.fill('textarea', 'stats for versicolor');
    await page.click('text=Compare Both');
    // Two result cards should appear
    await expect(page.locator('.card-function, .card-combined')).toHaveCount(2, { timeout: 10000 });
  });
});
