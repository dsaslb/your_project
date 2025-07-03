// Playwright E2E 테스트: 대시보드 진입 및 주요 UI 확인 예시
import { test, expect } from '@playwright/test';

test.describe('대시보드', () => {
  test.beforeEach(async ({ page }) => {
    // 로그인 선행
    await page.goto('http://localhost:3000/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpassword');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
  });

  test('대시보드 주요 카드/섹션 노출', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('대시보드');
    await expect(page.locator('.stat-card')).toHaveCount(3);
    // TODO: 주요 섹션/카드/그래프 등 추가 확인
  });
}); 