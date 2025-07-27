// 관리자 대시보드 자동화 테스트 예시 (Jest + React Testing Library)
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AdminDashboard from '../../../app/admin-dashboard/page';

// API mocking 예시 (실제 환경에 맞게 fetch mocking 필요)
beforeAll(() => {
  global.fetch = jest.fn((url) => {
    if (url.includes('/api/admin/brand_stats')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ stats: { totalUsers: 10, totalBranches: 2, systemHealth: '정상', recentActivities: [], onlineStatus: '2/2', databaseStatus: '정상' } }) });
    }
    if (url.includes('/api/admin/system-alerts')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ alerts: [{ id: 1, message: '테스트 알림', priority: 'high' }] }) });
    }
    if (url.includes('/api/feedback')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ feedbacks: [{ id: 'f1', title: '테스트 피드백', description: '설명', status: 'pending', created_at: '2024-01-01' }] }) });
    }
    if (url.includes('/api/brands')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ brands: [{ id: 'b1', name: '테스트브랜드' }] }) });
    }
    return Promise.resolve({ ok: false });
  }) as any;
});

describe('AdminDashboard', () => {
  it('요약 배너/통계/알림/피드백이 정상적으로 표시된다', async () => {
    render(<AdminDashboard />);
    // 통계/알림/피드백 요약 배너
    expect(await screen.findByText('신규 피드백')).toBeInTheDocument();
    expect(await screen.findByText('미처리 알림')).toBeInTheDocument();
    expect(await screen.findByText('시스템 상태')).toBeInTheDocument();
    // 통계 값
    expect(await screen.findByText('10')).toBeInTheDocument(); // totalUsers
    expect(await screen.findByText('2')).toBeInTheDocument(); // totalBranches
    expect(await screen.findByText('정상')).toBeInTheDocument(); // systemHealth
    // 알림
    expect(await screen.findByText('테스트 알림')).toBeInTheDocument();
    // 피드백
    expect(await screen.findByText('테스트 피드백')).toBeInTheDocument();
  });

  it('알림 클릭 시 상세 모달이 뜬다', async () => {
    render(<AdminDashboard />);
    const alertBtn = await screen.findByText('테스트 알림');
    fireEvent.click(alertBtn);
    expect(await screen.findByRole('dialog', { name: '알림 상세 모달' })).toBeInTheDocument();
    expect(await screen.findByText('테스트 알림')).toBeInTheDocument();
  });

  it('피드백 클릭 시 상세 모달이 뜬다', async () => {
    render(<AdminDashboard />);
    const feedbackCard = await screen.findByText('테스트 피드백');
    fireEvent.click(feedbackCard);
    expect(await screen.findByRole('dialog', { name: '피드백 상세 모달' })).toBeInTheDocument();
    expect(await screen.findByText('테스트 피드백')).toBeInTheDocument();
  });
}); 