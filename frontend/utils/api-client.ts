import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface ApiError {
  status: number;
  message: string;
  data?: any;
}

export class ApiClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // 요청 인터셉터
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 응답 인터셉터
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          this.handleUnauthorized();
        }
        return Promise.reject(this.formatError(error));
      }
    );
  }

  private getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  }

  private handleUnauthorized() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('session_id');
      window.location.href = '/login';
    }
  }

  private formatError(error: AxiosError): ApiError {
    const status = error.response?.status || 500;
    let message = '서버 오류가 발생했습니다.';

    if (error.response?.data && typeof error.response.data === 'object') {
      const data = error.response.data as any;
      message = data.message || data.error || message;
    } else if (error.message) {
      message = error.message;
    }

    return {
      status,
      message,
      data: error.response?.data,
    };
  }

  // GET 요청
  async get<T = any>(url: string, params?: any): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.get<ApiResponse<T>>(url, { params });
      return response.data;
    } catch (error) {
      throw this.formatError(error as AxiosError);
    }
  }

  // POST 요청
  async post<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.post<ApiResponse<T>>(url, data);
      return response.data;
    } catch (error) {
      throw this.formatError(error as AxiosError);
    }
  }

  // PUT 요청
  async put<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.put<ApiResponse<T>>(url, data);
      return response.data;
    } catch (error) {
      throw this.formatError(error as AxiosError);
    }
  }

  // PATCH 요청
  async patch<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.patch<ApiResponse<T>>(url, data);
      return response.data;
    } catch (error) {
      throw this.formatError(error as AxiosError);
    }
  }

  // DELETE 요청
  async delete<T = any>(url: string): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.delete<ApiResponse<T>>(url);
      return response.data;
    } catch (error) {
      throw this.formatError(error as AxiosError);
    }
  }

  // 파일 업로드
  async uploadFile<T = any>(url: string, file: File, onProgress?: (progress: number) => void): Promise<ApiResponse<T>> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await this.client.post<ApiResponse<T>>(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(progress);
          }
        },
      });

      return response.data;
    } catch (error) {
      throw this.formatError(error as AxiosError);
    }
  }

  // 배치 요청
  async batch<T = any>(requests: Array<{ method: string; url: string; data?: any }>): Promise<ApiResponse<T>[]> {
    try {
      const promises = requests.map(({ method, url, data }) => {
        switch (method.toLowerCase()) {
          case 'get':
            return this.get<T>(url);
          case 'post':
            return this.post<T>(url, data);
          case 'put':
            return this.put<T>(url, data);
          case 'patch':
            return this.patch<T>(url, data);
          case 'delete':
            return this.delete<T>(url);
          default:
            throw new Error(`지원하지 않는 HTTP 메서드: ${method}`);
        }
      });

      return await Promise.all(promises);
    } catch (error) {
      throw this.formatError(error as AxiosError);
    }
  }

  // 연결 상태 확인
  async healthCheck(): Promise<boolean> {
    try {
      await this.client.get('/health');
      return true;
    } catch (error) {
      return false;
    }
  }

  // 토큰 설정
  setAuthToken(token: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  // 토큰 제거
  clearAuthToken() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }
}

// 기본 인스턴스 생성
export const apiClient = new ApiClient();

// 특정 엔드포인트별 클라이언트 생성
export const createApiClient = (baseURL: string) => new ApiClient(baseURL); 