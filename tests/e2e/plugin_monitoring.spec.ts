// @ts-ignore - Playwright 모듈 타입 선언
import { test, expect } from '@playwright/test';

test.describe('Plugin Monitoring E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // 관리자로 로그인
    await page.goto('http://localhost:3000/login');
    await page.fill('[data-testid="email"]', 'admin@example.com');
    await page.fill('[data-testid="password"]', 'admin123');
    await page.click('[data-testid="login-button"]');
    
    // 로그인 완료 대기
    await page.waitForURL('http://localhost:3000/admin/dashboard');
  });

  test('should display plugin monitoring dashboard', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/plugin-monitoring');
    
    // 대시보드 요소 확인
    await expect(page.locator('h1')).toContainText('플러그인 모니터링');
    await expect(page.locator('[data-testid="connection-status"]')).toBeVisible();
    await expect(page.locator('[data-testid="plugin-count"]')).toBeVisible();
    await expect(page.locator('[data-testid="alert-count"]')).toBeVisible();
  });

  test('should show real-time metrics', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/plugin-monitoring');
    
    // 실시간 메트릭 카드 확인
    await expect(page.locator('[data-testid="cpu-usage-card"]')).toBeVisible();
    await expect(page.locator('[data-testid="memory-usage-card"]')).toBeVisible();
    await expect(page.locator('[data-testid="response-time-card"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-rate-card"]')).toBeVisible();
    
    // 메트릭 값이 숫자인지 확인
    const cpuValue = await page.locator('[data-testid="cpu-usage-value"]').textContent();
    expect(parseFloat(cpuValue || '0')).toBeGreaterThanOrEqual(0);
    expect(parseFloat(cpuValue || '0')).toBeLessThanOrEqual(100);
  });

  test('should display plugin list with metrics', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/plugin-monitoring');
    
    // 플러그인 목록 확인
    await expect(page.locator('[data-testid="plugin-list"]')).toBeVisible();
    
    // 샘플 플러그인들이 표시되는지 확인
    await expect(page.locator('text=분석 플러그인')).toBeVisible();
    await expect(page.locator('text=알림 플러그인')).toBeVisible();
    await expect(page.locator('text=리포팅 플러그인')).toBeVisible();
    
    // 각 플러그인의 메트릭 확인
    const pluginCards = page.locator('[data-testid="plugin-card"]');
    await expect(pluginCards).toHaveCount(5); // 5개 샘플 플러그인
  });

  test('should show alerts when thresholds are exceeded', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/plugin-monitoring');
    
    // 알림 탭으로 이동
    await page.click('[data-testid="alerts-tab"]');
    
    // 알림 목록 확인
    await expect(page.locator('[data-testid="active-alerts"]')).toBeVisible();
    
    // 알림이 있으면 상세 정보 확인
    const alertItems = page.locator('[data-testid="alert-item"]');
    const alertCount = await alertItems.count();
    
    if (alertCount > 0) {
      await expect(alertItems.first()).toBeVisible();
      
      // 알림 레벨 확인
      const alertLevel = await alertItems.first().locator('[data-testid="alert-level"]').textContent();
      expect(['info', 'warning', 'error', 'critical']).toContain(alertLevel?.toLowerCase());
      
      // 알림 해결 버튼 확인
      await expect(alertItems.first().locator('[data-testid="resolve-alert"]')).toBeVisible();
    }
  });

  test('should resolve alerts', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/plugin-monitoring');
    await page.click('[data-testid="alerts-tab"]');
    
    const alertItems = page.locator('[data-testid="alert-item"]');
    const initialCount = await alertItems.count();
    
    if (initialCount > 0) {
      // 첫 번째 알림 해결
      await alertItems.first().locator('[data-testid="resolve-alert"]').click();
      
      // 알림이 해결되었는지 확인
      await page.waitForTimeout(2000);
      const newCount = await alertItems.count();
      expect(newCount).toBeLessThan(initialCount);
    }
  });

  test('should display detailed metrics charts', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/plugin-monitoring');
    await page.click('[data-testid="details-tab"]');
    
    // 차트 컨테이너 확인
    await expect(page.locator('[data-testid="metrics-charts"]')).toBeVisible();
    
    // CPU 차트 확인
    await expect(page.locator('[data-testid="cpu-chart"]')).toBeVisible();
    
    // 메모리 차트 확인
    await expect(page.locator('[data-testid="memory-chart"]')).toBeVisible();
    
    // 응답 시간 차트 확인
    await expect(page.locator('[data-testid="response-time-chart"]')).toBeVisible();
  });

  test('should handle WebSocket disconnection gracefully', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/plugin-monitoring');
    
    // 초기 연결 상태 확인
    await expect(page.locator('[data-testid="connection-status"]')).toContainText('연결됨');
    
    // WebSocket 서버 중지 (테스트용)
    await page.evaluate(() => {
      if ((window as any).notificationWebSocket) {
        (window as any).notificationWebSocket.close();
      }
    });
    
    // 재연결 시도 확인
    await page.waitForTimeout(5000);
    await expect(page.locator('[data-testid="connection-status"]')).toContainText('연결됨');
  });

  test('should show real-time toast notifications', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/plugin-monitoring');
    
    // 브라우저 알림 권한 허용
    await page.evaluate(() => {
      if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
      }
    });
    
    // 테스트 알림 생성 (실제로는 서버에서 생성)
    await page.evaluate(() => {
      // 테스트용 알림 생성
      const event = new CustomEvent('test-alert', {
        detail: {
          type: 'warning',
          title: '테스트 알림',
          message: '이것은 테스트 알림입니다.',
          plugin_name: '테스트 플러그인'
        }
      });
      window.dispatchEvent(event);
    });
    
    // Toast 알림이 표시되는지 확인
    await expect(page.locator('[data-testid="toast-notification"]')).toBeVisible();
  });

  test('should filter plugins by status', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/plugin-monitoring');
    
    // 상태 필터 확인
    await expect(page.locator('[data-testid="status-filter"]')).toBeVisible();
    
    // 활성 플러그인만 필터링
    await page.selectOption('[data-testid="status-filter"]', 'active');
    
    // 활성 플러그인만 표시되는지 확인
    const activePlugins = page.locator('[data-testid="plugin-card"]');
    for (let i = 0; i < await activePlugins.count(); i++) {
      const status = await activePlugins.nth(i).locator('[data-testid="plugin-status"]').textContent();
      expect(status).toBe('active');
    }
  });

  test('should export monitoring data', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/plugin-monitoring');
    
    // 내보내기 버튼 확인
    await expect(page.locator('[data-testid="export-json"]')).toBeVisible();
    await expect(page.locator('[data-testid="export-csv"]')).toBeVisible();
    
    // JSON 내보내기 테스트
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="export-json"]');
    const download = await downloadPromise;
    
    expect(download.suggestedFilename()).toMatch(/plugin_monitoring_.*\.json/);
    
    // CSV 내보내기 테스트
    const downloadPromise2 = page.waitForEvent('download');
    await page.click('[data-testid="export-csv"]');
    const download2 = await downloadPromise2;
    
    expect(download2.suggestedFilename()).toMatch(/plugin_monitoring_.*\.csv/);
  });

  test('should update metrics in real-time', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/plugin-monitoring');
    
    // 초기 CPU 사용률 기록
    const initialCpu = await page.locator('[data-testid="cpu-usage-value"]').textContent();
    const initialCpuValue = parseFloat(initialCpu || '0');
    
    // 10초 대기 후 값 변경 확인
    await page.waitForTimeout(10000);
    
    const newCpu = await page.locator('[data-testid="cpu-usage-value"]').textContent();
    const newCpuValue = parseFloat(newCpu || '0');
    
    // 값이 변경되었는지 확인 (랜덤 메트릭 시뮬레이션으로 인해)
    expect(Math.abs(newCpuValue - initialCpuValue)).toBeGreaterThan(0);
  });

  test('should handle high load scenarios', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/plugin-monitoring');
    
    // 고부하 시나리오 시뮬레이션
    await page.evaluate(() => {
      // 많은 알림 생성
      for (let i = 0; i < 50; i++) {
        setTimeout(() => {
          const event = new CustomEvent('test-alert', {
            detail: {
              type: 'warning',
              title: `고부하 테스트 알림 ${i}`,
              message: `테스트 메시지 ${i}`,
              plugin_name: '테스트 플러그인'
            }
          });
          window.dispatchEvent(event);
        }, i * 100);
      }
    });
    
    // 시스템이 안정적으로 동작하는지 확인
    await page.waitForTimeout(5000);
    
    // 페이지가 응답하는지 확인
    await expect(page.locator('h1')).toContainText('플러그인 모니터링');
    
    // 메모리 누수 확인 (간접적으로)
    const memoryUsage = await page.evaluate(() => {
      if ('memory' in performance) {
        return (performance as any).memory.usedJSHeapSize;
      }
      return 0;
    });
    
    // 메모리 사용량이 합리적인 범위인지 확인
    expect(memoryUsage).toBeLessThan(100 * 1024 * 1024); // 100MB 미만
  });

  test('should display error states gracefully', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/plugin-monitoring');
    
    // 네트워크 오류 시뮬레이션
    await page.route('**/api/advanced-monitoring/**', route => {
      route.abort('failed');
    });
    
    // 페이지 새로고침
    await page.reload();
    
    // 오류 상태가 적절히 표시되는지 확인
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
    
    // 네트워크 복구
    await page.unroute('**/api/advanced-monitoring/**');
    
    // 재시도 버튼 클릭
    await page.click('[data-testid="retry-button"]');
    
    // 정상 복구 확인
    await expect(page.locator('h1')).toContainText('플러그인 모니터링');
  });
}); 