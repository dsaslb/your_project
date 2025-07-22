import { chromium, FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  // 테스트 데이터 정리
  await page.goto('http://localhost:5000/api/test/cleanup');
  await page.waitForResponse(response => response.url().includes('/api/test/cleanup'));
  
  await browser.close();
}

export default globalTeardown; 