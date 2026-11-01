import { test, expect } from '@playwright/test';

const PIPELINE_TIMEOUT = 60_000;

test.describe('History Flow', () => {
  test('should show the history page', async ({ page }) => {
    await page.goto('/history');
    await expect(page.getByRole('heading', { name: 'Query History' })).toBeVisible();
    // May show empty state or entries depending on previous tests
  });

  test('should record an agent analysis in history', async ({ page }) => {
    const query = `History flow check ${Date.now()}`;

    await page.goto('/agents');
    await page.fill('#agent-query', query);
    await page.click('#agent-submit');
    await expect(page.getByText('Executive Report', { exact: true })).toBeVisible({
      timeout: PIPELINE_TIMEOUT,
    });

    await page.getByRole('link', { name: 'History' }).click();
    await expect(page.getByRole('heading', { name: 'Query History' })).toBeVisible();
    await expect(page.getByText(query)).toBeVisible();
  });
});
