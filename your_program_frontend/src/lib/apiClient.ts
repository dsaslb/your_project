import { apiGet, apiPost, apiPut, apiDelete, checkBackendConnection } from './api';

// API 응답 타입 정의
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  pagination?: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// API 클라이언트 클래스
class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  async get<T = any>(endpoint: string): Promise<{ success: boolean; data?: T; error?: string }> {
    try {
      // 임시 더미 응답
      await new Promise(resolve => setTimeout(resolve, 100));
      return {
        success: true,
        data: {} as T
      };
    } catch (error) {
      return {
        success: false,
        error: 'API 호출 실패'
      };
    }
  }

  async post<T = any>(endpoint: string, data?: any): Promise<{ success: boolean; data?: T; error?: string }> {
    try {
      // 임시 더미 응답
      await new Promise(resolve => setTimeout(resolve, 100));
      return {
        success: true,
        data: {} as T
      };
    } catch (error) {
      return {
        success: false,
        error: 'API 호출 실패'
      };
    }
  }

  async put<T = any>(endpoint: string, data?: any): Promise<{ success: boolean; data?: T; error?: string }> {
    try {
      // 임시 더미 응답
      await new Promise(resolve => setTimeout(resolve, 100));
      return {
        success: true,
        data: {} as T
      };
    } catch (error) {
      return {
        success: false,
        error: 'API 호출 실패'
      };
    }
  }

  async delete<T = any>(endpoint: string): Promise<{ success: boolean; data?: T; error?: string }> {
    try {
      // 임시 더미 응답
      await new Promise(resolve => setTimeout(resolve, 100));
      return {
        success: true,
        data: {} as T
      };
    } catch (error) {
      return {
        success: false,
        error: 'API 호출 실패'
      };
    }
  }
}

export const apiClient = new ApiClient();

// 특정 도메인별 API 클라이언트
export class DomainApiClient {
  constructor(private domain: string) {}

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return apiClient.get<T>(`/api/${this.domain}${endpoint}`);
  }

  async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return apiClient.post<T>(`/api/${this.domain}${endpoint}`, data);
  }

  async put<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return apiClient.put<T>(`/api/${this.domain}${endpoint}`, data);
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return apiClient.delete<T>(`/api/${this.domain}${endpoint}`);
  }
}

// 도메인별 API 클라이언트 인스턴스
export const staffApi = new DomainApiClient('staff');
export const orderApi = new DomainApiClient('orders');
export const inventoryApi = new DomainApiClient('inventory');
export const scheduleApi = new DomainApiClient('schedule');
export const attendanceApi = new DomainApiClient('attendance');
export const notificationApi = new DomainApiClient('notifications');
export const reportApi = new DomainApiClient('reports'); 