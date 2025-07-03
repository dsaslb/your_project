const { test, expect } = require('@playwright/test');
const { injectAxe, checkA11y } = require('axe-playwright');

test.describe('접근성 자동화', () => {
  test('메인 대시보드 접근성 점검', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/monitor');
    await injectAxe(page);
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true }
    });
  });
}); 