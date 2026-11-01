import { test, expect } from '@playwright/test';

const PIPELINE_TIMEOUT = 60_000;

test.describe('Multi-Agent Flow', () => {
  test('should load the agents page', async ({ page }) => {
    await page.goto('/agents');
    await expect(page.getByRole('heading', { name: 'Multi-Agent Analytics' })).toBeVisible();
    await expect(page.getByRole('button', { name: /Run Multi-Agent Analysis/i })).toBeVisible();
  });

  test('should run the full agent pipeline', async ({ page }) => {
    await page.goto('/agents');
    await page.fill('#agent-query', 'Analyze Iris dataset and recommend the best classifier.');
    await page.click('#agent-submit');

    await expect(page.getByText('Executive Report', { exact: true })).toBeVisible({
      timeout: PIPELINE_TIMEOUT,
    });
    await expect(page.getByRole('heading', { name: 'Model Ranking' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Agent Audit Trail' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Orchestration Plan' })).toBeVisible();
  });

  test('should list all seven agents in the audit trail', async ({ page }) => {
    await page.goto('/agents');
    await page.fill('#agent-query', 'Which classifier is best?');
    await page.click('#agent-submit');

    await expect(page.getByRole('heading', { name: 'Main Orchestrator Agent' })).toBeVisible({
      timeout: PIPELINE_TIMEOUT,
    });

    for (const agent of [
      'Data Pattern Analysis Agent',
      'Random Forest Agent',
      'SVM Agent',
      'XGBoost Agent',
      'Evaluation Agent',
      'RAG Knowledge Agent',
    ]) {
      await expect(page.getByRole('heading', { name: agent, exact: true })).toBeVisible();
    }
  });
});
