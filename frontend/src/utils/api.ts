// API 호출을 위한 공통 유틸리티
import { useState } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ApiError {
  code: number;
  status: string;
  message?: string;
}

// 기본 API 설정
const defaultHeaders = {
  'Content-Type': 'application/json',
};

// API 호출 기본 함수
export async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    // credentials: 'include'가 항상 적용되도록 명확하게 보장
    const config: RequestInit = {
      ...options,
      credentials: 'include', // 항상 포함
      headers: {
        ...defaultHeaders,
        ...(options.headers || {}),
      },
    };

    let response;
    try {
      response = await fetch(url, config);
    } catch (networkError) {
      // 네트워크 에러(서버 연결 불가 등) 처리
      console.error('API 네트워크 오류:', networkError, url, config.method || 'GET');
      return {
        success: false,
        error: `네트워크 오류: 서버에 연결할 수 없습니다. (URL: ${url}, method: ${config.method || 'GET'})`,
      };
    }

    let data;
    try {
      // 204 No Content 등은 json()이 불가하므로 예외 처리
      if (response.status === 204) {
        data = null;
      } else {
        data = await response.json();
      }
    } catch (jsonError) {
      data = null;
    }

    if (response.ok) {
      return {
        success: true,
        data,
      };
    } else {
      return {
        success: false,
        error: (data && data.message) || `HTTP ${response.status}`,
      };
    }
  } catch (error) {
    console.error('API 호출 오류:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : '알 수 없는 오류',
    };
  }
}

// GET 요청
export async function apiGet<T>(endpoint: string): Promise<ApiResponse<T>> {
  return apiCall<T>(endpoint, { method: 'GET' });
}

// POST 요청
export async function apiPost<T>(
  endpoint: string,
  data?: any
): Promise<ApiResponse<T>> {
  return apiCall<T>(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
}

// PUT 요청
export async function apiPut<T>(
  endpoint: string,
  data?: any
): Promise<ApiResponse<T>> {
  return apiCall<T>(endpoint, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  });
}

// DELETE 요청
export async function apiDelete<T>(endpoint: string): Promise<ApiResponse<T>> {
  return apiCall<T>(endpoint, { method: 'DELETE' });
}

// 특정 API 엔드포인트 함수들

// 인증 관련
export const authApi = {
  login: (credentials: { username: string; password: string }) =>
    apiPost('/api/auth/login', credentials),
  logout: () => apiPost('/api/security/auth/logout'),
  me: () => apiGet('/api/auth/me'),
};

// 브랜드 관련
export const brandApi = {
  getAll: () => apiGet('/api/admin/brands'),
  getById: (id: number) => apiGet(`/api/admin/brands/${id}`),
  create: (data: any) => apiPost('/api/admin/brands', data),
  update: (id: number, data: any) => apiPut(`/api/admin/brands/${id}`, data),
  delete: (id: number) => apiDelete(`/api/admin/brands/${id}`),
  getStats: () => apiGet('/api/admin/brand_stats'),
};

// 매장 관련
export const storeApi = {
  getAll: () => apiGet('/api/admin/stores'),
  getById: (id: number) => apiGet(`/api/admin/stores/${id}`),
  create: (data: any) => apiPost('/api/admin/stores', data),
  update: (id: number, data: any) => apiPut(`/api/admin/stores/${id}`, data),
  delete: (id: number) => apiDelete(`/api/admin/stores/${id}`),
  getStats: () => apiGet('/api/admin/store_stats'),
};

// 직원 관련
export const employeeApi = {
  getAll: () => apiGet('/api/admin/employees'),
  getById: (id: number) => apiGet(`/api/admin/employees/${id}`),
  create: (data: any) => apiPost('/api/admin/employees', data),
  update: (id: number, data: any) => apiPut(`/api/admin/employees/${id}`, data),
  delete: (id: number) => apiDelete(`/api/admin/employees/${id}`),
  updateStatus: (id: number, status: string) =>
    apiPost(`/api/admin/user/${id}/status`, { status }),
};

// 시스템 관련
export const systemApi = {
  getLogs: () => apiGet('/api/admin/system-logs'),
  clearCache: () => apiPost('/api/admin/clear-cache'),
  getStats: () => apiGet('/api/admin/dashboard-stats'),
  getSystemStatus: () => apiGet('/api/admin/system-status'),
};

// 합 대시보드 관련
export const comprehensiveApi = {
  getOverview: () => apiGet('/admin/comprehensive/api/overview'),
  getTrends: () => apiGet('/admin/comprehensive/api/trends'),
  getRealTime: () => apiGet('/admin/comprehensive/api/real-time'),
  getAnalytics: () => apiGet('/admin/comprehensive/api/analytics'),
  getNotifications: () => apiGet('/admin/comprehensive/api/notifications'),
  exportData: (format: 'json' | 'csv') =>
    apiGet(`/admin/comprehensive/export?format=${format}`),
};

// 에러 처리 유틸리티
export function handleApiError(error: any): string {
  if (typeof error === 'string') return error;
  if (error?.message) return error.message;
  if (error?.error) return error.error;
  return '알 수 없는 오류가 발생했습니다.';
}

// 로딩 상태 관리를 위한 훅
export function useApiCall<T>() {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = async (apiCall: () => Promise<ApiResponse<T>>) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiCall();
      if (result.success) {
        setData(result.data || null);
      } else {
        setError(result.error || 'API 호출 실패');
      }
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, execute };
} 