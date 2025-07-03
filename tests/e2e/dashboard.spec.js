const { test, expect } = require('@playwright/test');

test('대시보드 주요 기능 E2E', async ({ page }) => {
  await page.goto('http://localhost:3000/admin/monitor');
  await expect(page.locator('h1')).toContainText('현황판');
  await expect(page.locator('canvas')).toHaveCount(6); // 다양한 차트
  await page.fill('input[aria-label="검색"]', '경고');
  await expect(page.locator('table')).toContainText('경고');
  await page.click('button[aria-label="새로고침"]');
  await expect(page.locator('h1')).toBeVisible();
}); 