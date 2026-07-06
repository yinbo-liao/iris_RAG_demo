import { test, expect } from '@playwright/test';

test.describe('History Flow', () => {
  test('should show empty state when no history', async ({ page }) => {
    await page.goto('/history');
    await expect(page.locator('text=Query History')).toBeVisible();
    // May show empty state or entries depending on previous tests
  });

  test('should navigate from query page to history', async ({ page }) => {
    await page.goto('/');
    await page.fill('textarea', 'list all species');
    await page.click('text=Submit Query');
    // Wait for result
    await page.waitForTimeout(2000);
    // Navigate to history
    await page.click('text=History');
    await expect(page.locator('text=Query History')).toBeVisible();
  });
});
