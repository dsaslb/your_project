import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
// 실제 컴포넌트 import 경로에 맞게 수정 필요
import { AutomationStatusBanner } from '../../app/admin-dashboard/page';

describe('AutomationStatusBanner', () => {
  beforeEach(() => {
    // fetch 모킹
    global.fetch = jest.fn((url) => {
      if (url === '/api/automation-status') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            upToDate: false,
            outdatedFiles: 2,
            securityPatch: true,
            lastCheck: '2024-06-01 09:00',
            details: ['README.md - 45일 미수정 (최종: 2024-04-17)', 'scripts/auto_env_check_and_notify.py - 31일 미수정 (최종: 2024-05-01)'],
          })
        }) as any;
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) }) as any;
    });
  });

  it('경고 상태(미점검/미최신화 파일) 배너가 정상적으로 표시된다', async () => {
    render(<AutomationStatusBanner />);
    await waitFor(() => expect(screen.getByText('미점검/미최신화 파일 2개, 보안 패치 필요')).toBeInTheDocument());
    expect(screen.getByText('README.md - 45일 미수정 (최종: 2024-04-17)')).toBeInTheDocument();
    expect(screen.getByText('scripts/auto_env_check_and_notify.py - 31일 미수정 (최종: 2024-05-01)')).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveAttribute('aria-label', '자동화 상태 및 최신화 점검 결과');
  });
}); 