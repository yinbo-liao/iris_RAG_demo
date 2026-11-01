import { test, expect } from '@playwright/test';

test.describe('Query Flow', () => {
  test('should load the homepage', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Iris RAG' })).toBeVisible();
    await expect(page.locator('text=Query Iris Dataset')).toBeVisible();
  });

  test('should submit a function call query', async ({ page }) => {
    await page.goto('/');
    await page.fill('textarea', 'stats for setosa');
    await page.click('text=Submit Query');
    // Should show a result card
    await expect(page.locator('.card-function, .card-combined')).toBeVisible({ timeout: 10000 });
  });

  test('should submit a combined tools query', async ({ page }) => {
    await page.goto('/');
    // Select Combined Tools approach
    await page.click('text=Combined Tools');
    await page.fill('textarea', 'tell me about setosa');
    await page.click('text=Submit Query');
    // Should show RAG Enabled badge
    await expect(page.locator('text=RAG Enabled')).toBeVisible({ timeout: 10000 });
  });

  test('should navigate between pages', async ({ page }) => {
    await page.goto('/');
    await page.click('text=Knowledge');
    await expect(page.locator('text=Knowledge Base')).toBeVisible();

    await page.click('text=History');
    await expect(page.locator('text=Query History')).toBeVisible();

    await page.click('text=Query');
    await expect(page.locator('text=Query Iris Dataset')).toBeVisible();
  });

  test('should show sample queries', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('text=Try a sample query')).toBeVisible();
    await expect(page.locator('text=Predict species')).toBeVisible();
    await expect(page.locator('text=Species stats')).toBeVisible();
  });

  test('should approach selector toggle styles', async ({ page }) => {
    await page.goto('/');
    // Default: Function Call selected
    const fcButton = page.locator('button:has-text("Function Call")').first();
    await expect(fcButton).toHaveClass(/border-amber-400/);

    // Click Combined Tools
    await page.click('text=Combined Tools');
    const ctButton = page.locator('button:has-text("Combined Tools")').first();
    await expect(ctButton).toHaveClass(/border-emerald-400/);
  });
});
