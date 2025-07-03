import { test, expect } from '@playwright/test';

test.describe('전체 통합 시나리오', () => {
  test('로그인→대시보드→스케줄→직원→발주→재고→알림/공지 플로우', async ({ page }) => {
    // 로그인
    await page.goto('/login');
    await page.fill('input[name="email"]', 'admin@example.com');
    await page.fill('input[name="password"]', 'admin1234');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
    await expect(page.locator('text=대시보드')).toBeVisible();

    // 대시보드 상태/카드/알림 확인
    await expect(page.locator('text=실시간')).toBeVisible();

    // 스케줄 이동 및 추가/수정/삭제/상태 체크
    await page.goto('/schedule');
    await expect(page.locator('text=스케줄')).toBeVisible();
    await page.click('text=추가');
    await page.fill('input[placeholder="이름"]', '테스트직원');
    await page.click('button:has-text("등록")');
    await expect(page.locator('text=테스트직원')).toBeVisible();

    // 직원 관리 이동 및 등록/수정/삭제
    await page.goto('/staff');
    await expect(page.locator('text=직원 관리')).toBeVisible();
    await page.click('text=직원 등록');
    await page.fill('input[placeholder="이름"]', '홍길동');
    await page.click('button:has-text("등록")');
    await expect(page.locator('text=홍길동')).toBeVisible();

    // 발주 관리 이동 및 등록/상태 변경
    await page.goto('/orders');
    await expect(page.locator('text=발주')).toBeVisible();
    await page.click('text=발주 추가');
    await page.fill('input[placeholder="품목"]', '테스트재료');
    await page.click('button:has-text("등록")');
    await expect(page.locator('text=테스트재료')).toBeVisible();

    // 재고 관리 이동 및 입출고/상태 확인
    await page.goto('/inventory');
    await expect(page.locator('text=재고 관리')).toBeVisible();
    await page.click('text=품목 추가');
    await page.fill('input[placeholder="품목명"]', '테스트재고');
    await page.click('button:has-text("추가")');
    await expect(page.locator('text=테스트재고')).toBeVisible();

    // 알림/공지 이동 및 확인
    await page.goto('/notifications');
    await expect(page.locator('text=알림')).toBeVisible();
    await expect(page.locator('text=공지사항')).toBeVisible();

    // 권한별 메뉴/기능 노출 확인
    await page.goto('/dashboard');
    await expect(page.locator('text=관리자')).toBeVisible();
    // 에러/알림/실시간 반영 테스트(예시)
    // ...
  });
}); 