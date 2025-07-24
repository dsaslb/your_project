import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { toast } from 'sonner';
import Router from 'next/router';
import useUserStore from '@/store/useUserStore';

// API 기본 설정
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Axios 인스턴스 생성
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 (토큰 자동 추가)
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 (에러 처리)
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      // 세션 만료 처리
      const { logout } = useUserStore.getState();
      if (logout) logout();
      toast.error('세션이 만료되었습니다. 다시 로그인 해주세요.');
      Router.push('/login');
    }
    return Promise.reject(error);
  }
);

// API 응답 타입 정의
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

// 브랜드 타입 정의
export interface Brand {
  id: string;
  name: string;
  industry: string;
  description: string;
  created_at: string;
  status: string;
}

// 매장 타입 정의
export interface Branch {
  id: string;
  brand_id: string;
  name: string;
  address: string;
  phone: string;
  manager: string;
  status: string;
  created_at: string;
}

// 직원 타입 정의
export interface Employee {
  id: string;
  branch_id: string;
  name: string;
  employee_id: string;
  position: string;
  department: string;
  phone: string;
  email: string;
  hire_date: string;
  status: string;
  salary: number;
}

// 스케줄 타입 정의
export interface Schedule {
  id: string;
  employee_id: string;
  date: string;
  start_time: string;
  end_time: string;
  status: 'scheduled' | 'working' | 'completed' | 'absent';
  notes: string;
}

// 직원 대시보드 타입 정의
export interface EmployeeDashboard {
  employee: {
    id: string;
    name: string;
    employee_id: string;
    position: string;
    department: string;
    branch: {
      id: string;
      name: string;
      address: string;
    };
    contact: {
      phone: string;
      email: string;
    };
    schedule: {
      today: string;
      start_time: string;
      end_time: string;
      status: string;
    };
    stats: {
      total_work_hours: number;
      this_month_hours: number;
      attendance_rate: number;
      overtime_hours: number;
    };
  };
  work_schedule: Schedule[];
}

// 관리자 대시보드 타입 정의
export interface AdminDashboard {
  stats: {
    total_brands: number;
    total_branches: number;
    total_employees: number;
    active_schedules: number;
    today_attendance: number;
  };
  recent_activities: Array<{
    id: string;
    type: string;
    employee_name: string;
    timestamp: string;
    date: string;
  }>;
  brands: Brand[];
  branches: Branch[];
}

// API 함수들
export const api = {
  // 브랜드 관련
  getBrands: (): Promise<ApiResponse<Brand[]>> => 
    apiClient.get('/api/brands').then(res => res.data),
  
  getBrand: (id: string): Promise<ApiResponse<Brand>> => 
    apiClient.get(`/api/brands/${id}`).then(res => res.data),
  
  createBrand: (data: Partial<Brand>): Promise<ApiResponse<Brand>> => 
    apiClient.post('/api/brands', data).then(res => res.data),
  
  // 매장 관련
  getBranches: (brandId?: string): Promise<ApiResponse<Branch[]>> => {
    const params = brandId ? { brand_id: brandId } : {};
    return apiClient.get('/api/branches', { params }).then(res => res.data);
  },
  
  getBranch: (id: string): Promise<ApiResponse<Branch>> => 
    apiClient.get(`/api/branches/${id}`).then(res => res.data),
  
  // 직원 관련
  getEmployees: (branchId?: string): Promise<ApiResponse<Employee[]>> => {
    const params = branchId ? { branch_id: branchId } : {};
    return apiClient.get('/api/employees', { params }).then(res => res.data);
  },
  
  getEmployee: (id: string): Promise<ApiResponse<Employee>> => 
    apiClient.get(`/api/employees/${id}`).then(res => res.data),
  
  // 스케줄 관련
  getSchedules: (employeeId?: string, date?: string): Promise<ApiResponse<Schedule[]>> => {
    const params: any = {};
    if (employeeId) params.employee_id = employeeId;
    if (date) params.date = date;
    return apiClient.get('/api/schedules', { params }).then(res => res.data);
  },
  
  createSchedule: (data: Partial<Schedule>): Promise<ApiResponse<Schedule>> => 
    apiClient.post('/api/schedules', data).then(res => res.data),
  
  // 직원 대시보드
  getEmployeeDashboard: (): Promise<ApiResponse<EmployeeDashboard>> => 
    apiClient.get('/api/employee/dashboard').then(res => res.data),
  
  clockIn: (data: { employee_id?: string; timestamp?: string }): Promise<ApiResponse> => 
    apiClient.post('/api/employee/clock-in', data).then(res => res.data),
  
  clockOut: (data: { employee_id?: string; timestamp?: string }): Promise<ApiResponse> => 
    apiClient.post('/api/employee/clock-out', data).then(res => res.data),
  
  // 관리자 대시보드
  getAdminDashboard: (): Promise<ApiResponse<AdminDashboard>> => 
    apiClient.get('/api/admin/dashboard').then(res => res.data),
  
  // 인증
  login: (credentials: { username: string; password: string }): Promise<ApiResponse> => 
    apiClient.post('/api/security/auth/login', credentials).then(res => res.data),

  // 사용자 정보 조회
  getProfile: (): Promise<any> =>
    apiClient.get('/api/auth/me').then(res => res.data.user),
  
  // 헬스체크
  healthCheck: (): Promise<ApiResponse> => 
    apiClient.get('/api/health').then(res => res.data),
  
  // 테스트 알림
  testNotification: (data: { message: string }): Promise<ApiResponse> => 
    apiClient.post('/api/test/notification', data).then(res => res.data),
  
  testSystemAlert: (data: { type: string; message: string }): Promise<ApiResponse> => 
    apiClient.post('/api/test/system-alert', data).then(res => res.data),
};

// 유틸리티 함수들
export const apiUtils = {
  // 에러 메시지 추출
  getErrorMessage: (error: any): string => {
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.message) {
      return error.message;
    }
    return '알 수 없는 오류가 발생했습니다.';
  },
  
  // 성공 여부 확인
  isSuccess: (response: ApiResponse): boolean => {
    return response.success === true;
  },
  
  // 데이터 추출
  getData: <T>(response: ApiResponse<T>): T | undefined => {
    return response.data;
  },
  
  // 토큰 관리
  setToken: (token: string) => {
    localStorage.setItem('token', token);
  },
  
  getToken: (): string | null => {
    return localStorage.getItem('token');
  },
  
  removeToken: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
  
  // 사용자 정보 관리
  setUser: (user: any) => {
    localStorage.setItem('user', JSON.stringify(user));
  },
  
  getUser: (): any => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
  
  // 로그인 상태 확인
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('token');
  },
};

export default api; 