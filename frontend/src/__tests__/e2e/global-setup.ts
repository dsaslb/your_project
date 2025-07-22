import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  // 테스트 데이터베이스 초기화
  await page.goto('http://localhost:5000/api/test/setup');
  await page.waitForResponse(response => response.url().includes('/api/test/setup'));
  
  // 테스트 사용자 생성
  await page.goto('http://localhost:5000/api/test/create-test-user');
  await page.waitForResponse(response => response.url().includes('/api/test/create-test-user'));
  
  await browser.close();
}

export default globalSetup; 