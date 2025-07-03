// Playwright E2E 테스트: 로그인 시나리오 예시
import { test, expect } from '@playwright/test';

test.describe('로그인', () => {
  test('성공: 올바른 계정으로 로그인', async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpassword');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
  });

  test('실패: 잘못된 비밀번호', async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    await expect(page.locator('.error-message')).toBeVisible();
  });
}); 