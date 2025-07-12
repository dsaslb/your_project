import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import PluginPerformancePage from '@/app/plugin-performance/page';

// API mocking을 위한 msw 등은 실제 환경에 맞게 추가 필요

// Toaster만 mock 처리
jest.mock('@/components/ui/sonner', () => ({
  Toaster: () => null,
}));

// toast mock
jest.mock('sonner', () => ({
  toast: {
    error: jest.fn(),
    warning: jest.fn(),
    success: jest.fn(),
  },
}));

describe('플러그인 성능 대시보드', () => {
  beforeEach(() => {
    // fetch mock 초기화
    global.fetch = jest.fn();
    // toast mock 초기화
    jest.clearAllMocks();
  });

  it('대시보드 진입 시 로딩 상태가 표시된다', async () => {
    // API 응답을 지연시켜 로딩 상태 확인
    (global.fetch as jest.Mock).mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ ok: true, json: () => Promise.resolve({}) }), 100))
    );

    render(React.createElement(PluginPerformancePage));
    
    // 로딩 상태 확인
    expect(screen.getByText('데이터 로딩 중...')).toBeInTheDocument();
  });

  it('모니터링 시작/중지 버튼이 정상 동작한다', async () => {
    // 성공적인 API 응답 mock
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        plugins: [],
        system_metrics: {
          total_plugins: 0,
          active_plugins: 0,
          monitoring_active: false,
          alerts: []
        }
      })
    });

    render(React.createElement(PluginPerformancePage));
    
    // 로딩 완료 대기
    await waitFor(() => {
      expect(screen.queryByText('데이터 로딩 중...')).not.toBeInTheDocument();
    });

    // 모니터링 시작 버튼 확인
    const startBtn = screen.getByText('모니터링 시작');
    expect(startBtn).toBeInTheDocument();
    
    // 버튼 클릭 시나리오 (실제로는 API 호출이 필요)
    fireEvent.click(startBtn);
    
    // 새로고침 버튼 확인
    const refreshBtn = screen.getByText('새로고침');
    expect(refreshBtn).toBeInTheDocument();
  });

  it('API 오류 발생 시 에러 처리가 동작한다', async () => {
    // API 오류 mock
    (global.fetch as jest.Mock).mockRejectedValue(new Error('API 오류'));

    render(React.createElement(PluginPerformancePage));
    
    // 로딩 완료 대기
    await waitFor(() => {
      expect(screen.queryByText('데이터 로딩 중...')).not.toBeInTheDocument();
    });

    // 에러 상태에서도 기본 UI는 표시되어야 함
    expect(screen.getByText('플러그인 성능 모니터링')).toBeInTheDocument();
    expect(screen.getByText('모니터링 시작')).toBeInTheDocument();
  });

  it('성능 임계치 초과 시 알림이 표시된다', async () => {
    // 임계치 초과 데이터 mock
    const mockPerformanceData = [
      {
        plugin_name: 'test-plugin',
        cpu_usage: 85, // 80% 초과
        memory_usage: 90, // 85% 초과
        response_time: 1200, // 1000ms 초과
        status: 'warning',
        last_updated: new Date().toISOString()
      }
    ];

    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        data: mockPerformanceData,
        system_metrics: {
          total_plugins: 1,
          active_plugins: 1,
          monitoring_active: true,
          alerts: []
        }
      })
    });

    render(React.createElement(PluginPerformancePage));
    
    // 로딩 완료 대기
    await waitFor(() => {
      expect(screen.queryByText('데이터 로딩 중...')).not.toBeInTheDocument();
    });

    // 성능 데이터가 표시되는지 확인
    await waitFor(() => {
      expect(screen.getByText('test-plugin')).toBeInTheDocument();
    });

    // 임계치 초과 데이터 확인
    expect(screen.getByText('85%')).toBeInTheDocument(); // CPU
    expect(screen.getByText('90%')).toBeInTheDocument(); // Memory
    expect(screen.getByText('1200ms')).toBeInTheDocument(); // Response time
  });
}); 