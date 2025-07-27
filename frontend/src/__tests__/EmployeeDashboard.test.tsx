import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import EmployeeDashboard from '@/app/employee-dashboard/page';

// Mock API hooks
jest.mock('@/hooks/useApi', () => ({
  useEmployeeDashboard: () => ({
    data: {
      data: {
        employee: {
          id: 1,
          name: "김철수",
          employee_id: "EMP001",
          position: "매니저",
          department: "영업팀",
          branch: {
            id: 1,
            name: "강남점",
            address: "서울시 강남구 테헤란로 123"
          },
          contact: {
            phone: "010-1234-5678",
            email: "kim.cheolsu@company.com"
          },
          schedule: {
            today: "2025-07-20",
            start_time: "09:00",
            end_time: "18:00",
            status: "working"
          },
          stats: {
            total_work_hours: 160,
            this_month_hours: 120,
            attendance_rate: 95.5,
            overtime_hours: 8
          }
        },
        work_schedule: [
          {
            id: 1,
            date: "2025-07-20",
            start_time: "09:00",
            end_time: "18:00",
            status: "working"
          }
        ]
      }
    },
    isLoading: false,
    error: null
  }),
  useEmployeeClockIn: () => ({
    mutate: jest.fn(),
    isPending: false
  }),
  useEmployeeClockOut: () => ({
    mutate: jest.fn(),
    isPending: false
  })
}));

// Mock auth store
jest.mock('@/store/auth-store', () => ({
  useAuthStore: () => ({
    user: {
      id: 1,
      name: "관리자",
      role: "admin"
    }
  })
}));

// Mock toast
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn()
  },
  Toaster: () => <div data-testid="toaster" />
}));

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
      <Toaster />
    </QueryClientProvider>
  );
};

describe('EmployeeDashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders employee dashboard with correct information', () => {
    renderWithProviders(<EmployeeDashboard />);

    // 직원 정보 확인
    expect(screen.getByText('직원 대시보드')).toBeInTheDocument();
    expect(screen.getByText('김철수')).toBeInTheDocument();
    expect(screen.getByText('EMP001')).toBeInTheDocument();
    expect(screen.getByText('매니저')).toBeInTheDocument();
    expect(screen.getByText('영업팀')).toBeInTheDocument();
  });

  it('displays work schedule information', () => {
    renderWithProviders(<EmployeeDashboard />);

    // 근무 시간 확인
    expect(screen.getByText('09:00 - 18:00')).toBeInTheDocument();
    expect(screen.getByText('근무중')).toBeInTheDocument();
  });

  it('displays work statistics', () => {
    renderWithProviders(<EmployeeDashboard />);

    // 통계 정보 확인
    expect(screen.getByText('120시간')).toBeInTheDocument();
    expect(screen.getByText('95.5%')).toBeInTheDocument();
    expect(screen.getByText('8시간')).toBeInTheDocument();
  });

  it('displays branch information', () => {
    renderWithProviders(<EmployeeDashboard />);

    // 지점 정보 확인
    expect(screen.getByText('강남점')).toBeInTheDocument();
    expect(screen.getByText('서울시 강남구 테헤란로 123')).toBeInTheDocument();
    expect(screen.getByText('010-1234-5678')).toBeInTheDocument();
    expect(screen.getByText('kim.cheolsu@company.com')).toBeInTheDocument();
  });

  it('shows clock in/out buttons', () => {
    renderWithProviders(<EmployeeDashboard />);

    // 출근/퇴근 버튼 확인
    expect(screen.getByText('출근')).toBeInTheDocument();
    expect(screen.getByText('퇴근')).toBeInTheDocument();
  });

  it('displays current time', () => {
    renderWithProviders(<EmployeeDashboard />);

    // 현재 시간 표시 확인
    const timeElement = screen.getByText(/\d{4}년 \d{1,2}월 \d{1,2}일/);
    expect(timeElement).toBeInTheDocument();
  });

  it('shows work schedule list', () => {
    renderWithProviders(<EmployeeDashboard />);

    // 근무 일정 확인
    expect(screen.getByText('근무 일정')).toBeInTheDocument();
  });

  it('handles loading state', () => {
    // Mock loading state
    jest.doMock('@/hooks/useApi', () => ({
      useEmployeeDashboard: () => ({
        data: null,
        isLoading: true,
        error: null
      }),
      useEmployeeClockIn: () => ({
        mutate: jest.fn(),
        isPending: false
      }),
      useEmployeeClockOut: () => ({
        mutate: jest.fn(),
        isPending: false
      })
    }));

    renderWithProviders(<EmployeeDashboard />);
    expect(screen.getByText('직원 정보를 불러오는 중...')).toBeInTheDocument();
  });

  it('handles error state', () => {
    // Mock error state
    jest.doMock('@/hooks/useApi', () => ({
      useEmployeeDashboard: () => ({
        data: null,
        isLoading: false,
        error: new Error('Failed to load data')
      }),
      useEmployeeClockIn: () => ({
        mutate: jest.fn(),
        isPending: false
      }),
      useEmployeeClockOut: () => ({
        mutate: jest.fn(),
        isPending: false
      })
    }));

    renderWithProviders(<EmployeeDashboard />);
    expect(screen.getByText('직원 정보를 찾을 수 없습니다.')).toBeInTheDocument();
  });
});

describe('EmployeeDashboard Integration', () => {
  it('integrates with React Query', () => {
    const queryClient = createTestQueryClient();
    
    render(
      <QueryClientProvider client={queryClient}>
        <EmployeeDashboard />
      </QueryClientProvider>
    );

    // React Query가 정상적으로 작동하는지 확인
    expect(queryClient.getQueryCache().getAll()).toHaveLength(1);
  });

  it('handles clock in/out actions', async () => {
    const mockClockIn = jest.fn();
    const mockClockOut = jest.fn();

    jest.doMock('@/hooks/useApi', () => ({
      useEmployeeDashboard: () => ({
        data: {
          data: {
            employee: {
              id: 1,
              name: "김철수",
              employee_id: "EMP001",
              position: "매니저",
              department: "영업팀",
              branch: {
                id: 1,
                name: "강남점",
                address: "서울시 강남구 테헤란로 123"
              },
              contact: {
                phone: "010-1234-5678",
                email: "kim.cheolsu@company.com"
              },
              schedule: {
                today: "2025-07-20",
                start_time: "09:00",
                end_time: "18:00",
                status: "scheduled"
              },
              stats: {
                total_work_hours: 160,
                this_month_hours: 120,
                attendance_rate: 95.5,
                overtime_hours: 8
              }
            }
          }
        },
        isLoading: false,
        error: null
      }),
      useEmployeeClockIn: () => ({
        mutate: mockClockIn,
        isPending: false
      }),
      useEmployeeClockOut: () => ({
        mutate: mockClockOut,
        isPending: false
      })
    }));

    renderWithProviders(<EmployeeDashboard />);

    // 출근 버튼 클릭
    const clockInButton = screen.getByText('출근');
    fireEvent.click(clockInButton);

    await waitFor(() => {
      expect(mockClockIn).toHaveBeenCalled();
    });
  });
}); 