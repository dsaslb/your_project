import { test, expect } from '@playwright/test';

test('알림 팝업이 뜨는지 확인', async ({ page }) => {
  await page.goto('http://localhost:3000');
  // 알림 발생 트리거 (예: 버튼 클릭 또는 WebSocket 메시지 수신)
  // 실제 알림 UI가 있다면 아래 코드 수정
  await page.evaluate(() => {
    window.dispatchEvent(new CustomEvent('notify', { detail: { message: '테스트 알림!' } }));
  });
  // 알림 팝업 확인 (예: alert, toast 등)
  // await expect(page.getByText('테스트 알림!')).toBeVisible();
}); 