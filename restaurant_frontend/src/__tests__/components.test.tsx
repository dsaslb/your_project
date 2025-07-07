import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import MobileDashboard from '../components/mobile/MobileDashboard';

// 테스트용 QueryClient 생성
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

// 테스트용 래퍼 컴포넌트
const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = createTestQueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('MobileDashboard', () => {
  const mockStats = {
    totalUsers: 25,
    totalOrders: 150,
    totalRevenue: '₩2,450,000',
    pendingOrders: 8,
    activeUsers: 20,
    completedOrders: 142,
  };

  it('renders dashboard with correct title for store manager', () => {
    render(
      <TestWrapper>
        <MobileDashboard userRole="store_manager" stats={mockStats} />
      </TestWrapper>
    );

    expect(screen.getByText('매장 관리자 대시보드')).toBeInTheDocument();
    expect(screen.getByText('모바일 최적화')).toBeInTheDocument();
  });

  it('renders dashboard with correct title for super admin', () => {
    render(
      <TestWrapper>
        <MobileDashboard userRole="super_admin" stats={mockStats} />
      </TestWrapper>
    );

    expect(screen.getByText('슈퍼 관리자 대시보드')).toBeInTheDocument();
  });

  it('displays correct stats in overview tab', () => {
    render(
      <TestWrapper>
        <MobileDashboard userRole="store_manager" stats={mockStats} />
      </TestWrapper>
    );

    expect(screen.getByText('₩2,450,000')).toBeInTheDocument();
    expect(screen.getByText('8')).toBeInTheDocument(); // pending orders
    expect(screen.getByText('20')).toBeInTheDocument(); // active users
    expect(screen.getByText('142')).toBeInTheDocument(); // completed orders
  });

  it('switches between tabs correctly', async () => {
    render(
      <TestWrapper>
        <MobileDashboard userRole="store_manager" stats={mockStats} />
      </TestWrapper>
    );

    // 기본적으로 overview 탭이 활성화되어 있음
    expect(screen.getByText('빠른 액션')).toBeInTheDocument();

    // 주문 탭으로 전환
    const ordersTab = screen.getByText('주문');
    fireEvent.click(ordersTab);

    await waitFor(() => {
      expect(screen.getByText('최근 주문')).toBeInTheDocument();
    });

    // 직원 탭으로 전환
    const staffTab = screen.getByText('직원');
    fireEvent.click(staffTab);

    await waitFor(() => {
      expect(screen.getByText('오늘 출근')).toBeInTheDocument();
    });

    // 알림 탭으로 전환
    const alertsTab = screen.getByText('알림');
    fireEvent.click(alertsTab);

    await waitFor(() => {
      expect(screen.getByText('알림')).toBeInTheDocument();
    });
  });

  it('displays quick action buttons', () => {
    render(
      <TestWrapper>
        <MobileDashboard userRole="store_manager" stats={mockStats} />
      </TestWrapper>
    );

    expect(screen.getByText('주문 관리')).toBeInTheDocument();
    expect(screen.getByText('직원 관리')).toBeInTheDocument();
    expect(screen.getByText('스케줄')).toBeInTheDocument();
    expect(screen.getByText('재고')).toBeInTheDocument();
  });

  it('displays recent orders in orders tab', async () => {
    render(
      <TestWrapper>
        <MobileDashboard userRole="store_manager" stats={mockStats} />
      </TestWrapper>
    );

    // 주문 탭으로 전환
    const ordersTab = screen.getByText('주문');
    fireEvent.click(ordersTab);

    await waitFor(() => {
      expect(screen.getByText('주문 #1001')).toBeInTheDocument();
      expect(screen.getByText('주문 #1002')).toBeInTheDocument();
      expect(screen.getByText('주문 #1003')).toBeInTheDocument();
    });
  });

  it('displays staff attendance in staff tab', async () => {
    render(
      <TestWrapper>
        <MobileDashboard userRole="store_manager" stats={mockStats} />
      </TestWrapper>
    );

    // 직원 탭으로 전환
    const staffTab = screen.getByText('직원');
    fireEvent.click(staffTab);

    await waitFor(() => {
      expect(screen.getByText('김철수')).toBeInTheDocument();
      expect(screen.getByText('이영희')).toBeInTheDocument();
      expect(screen.getByText('박민수')).toBeInTheDocument();
    });
  });

  it('displays alerts in alerts tab', async () => {
    render(
      <TestWrapper>
        <MobileDashboard userRole="store_manager" stats={mockStats} />
      </TestWrapper>
    );

    // 알림 탭으로 전환
    const alertsTab = screen.getByText('알림');
    fireEvent.click(alertsTab);

    await waitFor(() => {
      expect(screen.getByText('재고 부족')).toBeInTheDocument();
      expect(screen.getByText('새 직원 등록')).toBeInTheDocument();
      expect(screen.getByText('목표 달성')).toBeInTheDocument();
    });
  });

  it('has correct tab navigation structure', () => {
    render(
      <TestWrapper>
        <MobileDashboard userRole="store_manager" stats={mockStats} />
      </TestWrapper>
    );

    // 탭 네비게이션이 존재하는지 확인
    expect(screen.getByText('개요')).toBeInTheDocument();
    expect(screen.getByText('주문')).toBeInTheDocument();
    expect(screen.getByText('직원')).toBeInTheDocument();
    expect(screen.getByText('알림')).toBeInTheDocument();
  });

  it('displays menu button in header', () => {
    render(
      <TestWrapper>
        <MobileDashboard userRole="store_manager" stats={mockStats} />
      </TestWrapper>
    );

    // 메뉴 버튼이 존재하는지 확인
    const menuButton = screen.getByRole('button');
    expect(menuButton).toBeInTheDocument();
  });
}); 