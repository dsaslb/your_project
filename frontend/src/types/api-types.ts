// ===== 자동 생성된 TypeScript 타입 =====
// 이 파일은 Swagger JSON에서 자동 생성되었습니다.
// 수동으로 편집하지 마세요.
// 생성 시간: 2024-12-19T10:00:00.000Z

// ===== HealthResponse =====
export interface HealthResponse {
  status: string;
  message: string;
  timestamp: string;
}

// ===== User =====
export interface User {
  id: number;
  username: string;
  name: string;
  role: string;
  email?: string;
}

// ===== LoginRequest =====
export interface LoginRequest {
  username: string;
  password: string;
}

// ===== LoginResponse =====
export interface LoginResponse {
  success: boolean;
  message: string;
  data?: Record<string, any>;
}

// ===== Brand =====
export interface Brand {
  id: string;
  name: string;
  industry: string;
  description?: string;
  created_at: string;
  status: string;
}

// ===== BrandCreate =====
export interface BrandCreate {
  name: string;
  industry: string;
  description?: string;
}

// ===== BrandListResponse =====
export interface BrandListResponse {
  success: boolean;
  data: Brand[];
  total: number;
}

// ===== Branch =====
export interface Branch {
  id: string;
  brand_id: string;
  name: string;
  address: string;
  phone?: string;
  manager?: string;
  status: string;
  created_at: string;
}

// ===== BranchCreate =====
export interface BranchCreate {
  brand_id: string;
  name: string;
  address: string;
  phone?: string;
  manager?: string;
}

// ===== Employee =====
export interface Employee {
  id: string;
  branch_id: string;
  name: string;
  employee_id: string;
  position: string;
  department: string;
  phone?: string;
  email?: string;
  hire_date: string;
  status: string;
  salary?: number;
}

// ===== Schedule =====
export interface Schedule {
  id: string;
  employee_id: string;
  date: string;
  start_time: string;
  end_time: string;
  status: string;
  notes?: string;
}

// ===== ScheduleCreate =====
export interface ScheduleCreate {
  employee_id: string;
  date: string;
  start_time: string;
  end_time: string;
  notes?: string;
}

// ===== EmployeeDashboard =====
export interface EmployeeDashboard {
  employee: Record<string, any>;
  work_schedule: Schedule[];
}

// ===== ClockInOutRequest =====
export interface ClockInOutRequest {
  employee_id?: string;
  timestamp?: string;
}

// ===== ClockInOutResponse =====
export interface ClockInOutResponse {
  success: boolean;
  message: string;
  data?: Record<string, any>;
}

// ===== AdminDashboard =====
export interface AdminDashboard {
  stats: Record<string, any>;
  recent_activities: Record<string, any>[];
  brands: Brand[];
  branches: Branch[];
}

// ===== NotificationRequest =====
export interface NotificationRequest {
  message: string;
}

// ===== SystemAlertRequest =====
export interface SystemAlertRequest {
  type: 'info' | 'warning' | 'error';
  message: string;
}

// ===== API 응답 타입 =====

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  total: number;
  page?: number;
  pageSize?: number;
}

// ===== API 엔드포인트 타입 =====

export interface ApiEndpoints {
  // 헬스체크
  'GET /api/health': {
    response: HealthResponse;
  };
  
  // 인증
  'POST /api/security/auth/login': {
    request: LoginRequest;
    response: LoginResponse;
  };
  
  // 브랜드
  'GET /api/brands': {
    response: PaginatedResponse<Brand>;
  };
  'POST /api/brands': {
    request: BrandCreate;
    response: Brand;
  };
  'GET /api/brands/{id}': {
    response: Brand;
  };
  
  // 매장
  'GET /api/branches': {
    response: PaginatedResponse<Branch>;
  };
  'POST /api/branches': {
    request: BranchCreate;
    response: Branch;
  };
  'GET /api/branches/{id}': {
    response: Branch;
  };
  
  // 직원
  'GET /api/employees': {
    response: PaginatedResponse<Employee>;
  };
  'GET /api/employees/{id}': {
    response: Employee;
  };
  
  // 스케줄
  'GET /api/schedules': {
    response: PaginatedResponse<Schedule>;
  };
  'POST /api/schedules': {
    request: ScheduleCreate;
    response: Schedule;
  };
  
  // 직원 대시보드
  'GET /api/employee/dashboard': {
    response: EmployeeDashboard;
  };
  'POST /api/employee/clock-in': {
    request: ClockInOutRequest;
    response: ClockInOutResponse;
  };
  'POST /api/employee/clock-out': {
    request: ClockInOutRequest;
    response: ClockInOutResponse;
  };
  
  // 관리자 대시보드
  'GET /api/admin/dashboard': {
    response: AdminDashboard;
  };
  
  // 테스트
  'POST /api/test/notification': {
    request: NotificationRequest;
    response: ApiResponse;
  };
  'POST /api/test/system-alert': {
    request: SystemAlertRequest;
    response: ApiResponse;
  };
}

// ===== API 클라이언트 타입 =====

export type ApiMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

export interface ApiRequestConfig {
  method: ApiMethod;
  url: string;
  data?: any;
  params?: Record<string, any>;
  headers?: Record<string, string>;
}

export interface ApiClient {
  request<T>(config: ApiRequestConfig): Promise<T>;
  get<T>(url: string, config?: Partial<ApiRequestConfig>): Promise<T>;
  post<T>(url: string, data?: any, config?: Partial<ApiRequestConfig>): Promise<T>;
  put<T>(url: string, data?: any, config?: Partial<ApiRequestConfig>): Promise<T>;
  delete<T>(url: string, config?: Partial<ApiRequestConfig>): Promise<T>;
}

// ===== 유틸리티 타입 =====

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type Required<T, K extends keyof T> = T & Required<Pick<T, K>>;

// ===== API 훅 타입 =====

export interface UseApiOptions<T> {
  enabled?: boolean;
  refetchInterval?: number;
  staleTime?: number;
  cacheTime?: number;
  retry?: number;
  retryDelay?: number;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
}

export interface UseMutationOptions<T, V> {
  onSuccess?: (data: T, variables: V) => void;
  onError?: (error: Error, variables: V) => void;
  onSettled?: (data: T | undefined, error: Error | null, variables: V) => void;
} 