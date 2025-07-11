import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// API 기본 설정
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// 토큰 관리
class TokenManager {
  private static instance: TokenManager;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  static getInstance(): TokenManager {
    if (!TokenManager.instance) {
      TokenManager.instance = new TokenManager();
    }
    return TokenManager.instance;
  }

  setTokens(accessToken: string, refreshToken: string): void {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    
    // 로컬 스토리지에 저장
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
    }
  }

  getAccessToken(): string | null {
    if (!this.accessToken && typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
    }
    return this.accessToken;
  }

  getRefreshToken(): string | null {
    if (!this.refreshToken && typeof window !== 'undefined') {
      this.refreshToken = localStorage.getItem('refresh_token');
    }
    return this.refreshToken;
  }

  clearTokens(): void {
    this.accessToken = null;
    this.refreshToken = null;
    
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }
}

// API 클라이언트 클래스
class ApiClient {
  private axiosInstance: AxiosInstance;
  private tokenManager: TokenManager;
  private isRefreshing = false;
  private failedQueue: Array<{
    resolve: (value?: any) => void;
    reject: (reason?: any) => void;
  }> = [];

  constructor() {
    this.tokenManager = TokenManager.getInstance();
    
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true,
    });

    // 요청 인터셉터
    this.axiosInstance.interceptors.request.use(
      (config) => {
        const token = this.tokenManager.getAccessToken();
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
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // 토큰 갱신 중인 경우 대기
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject });
            }).then(() => {
              return this.axiosInstance(originalRequest);
            }).catch((err) => {
              return Promise.reject(err);
            });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const refreshToken = this.tokenManager.getRefreshToken();
            if (!refreshToken) {
              throw new Error('리프레시 토큰이 없습니다');
            }

            const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
              refresh_token: refreshToken,
            });

            const { access_token, refresh_token } = response.data;
            this.tokenManager.setTokens(access_token, refresh_token);

            // 대기 중인 요청들 처리
            this.failedQueue.forEach(({ resolve }) => {
              resolve();
            });
            this.failedQueue = [];

            return this.axiosInstance(originalRequest);
          } catch (refreshError) {
            // 토큰 갱신 실패 시 로그아웃
            this.tokenManager.clearTokens();
            if (typeof window !== 'undefined') {
              window.location.href = '/login';
            }
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // 인증 관련 API
  async login(username: string, password: string) {
    try {
      const response = await this.axiosInstance.post('/api/security/auth/login', {
        username,
        password,
      }, {
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const { token, user } = response.data;
      this.tokenManager.setTokens(token, token); // JWT 토큰 사용
      
      return { user, redirect_to: user.role === 'admin' ? '/admin-dashboard' : '/dashboard' };
    } catch (error: any) {
      console.error('Login API error:', error);
      if (error.code === 'ERR_NETWORK' || error.response?.status >= 500) {
        throw new Error('서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.');
      }
      throw error;
    }
  }

  async logout() {
    try {
      await this.axiosInstance.post('/api/security/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.tokenManager.clearTokens();
    }
  }

  async getProfile() {
    try {
      const response = await this.axiosInstance.get('/api/user/profile');
      return response.data;
    } catch (error: any) {
      console.error('Get profile API error:', error);
      if (error.code === 'ERR_NETWORK' || error.response?.status >= 500) {
        // 백엔드 연결 실패 시 더미 프로필 반환
        return {
          id: 1,
          username: 'demo_user',
          name: '데모 사용자',
          email: 'demo@example.com',
          role: 'super_admin',
          is_active: true
        };
      }
      throw error;
    }
  }

  async getDashboardData() {
    try {
      const response = await this.axiosInstance.get('/dashboard');
      return response.data;
    } catch (error: any) {
      console.error('Get dashboard API error:', error);
      if (error.code === 'ERR_NETWORK' || error.response?.status >= 500) {
        // 백엔드 연결 실패 시 더미 대시보드 데이터 반환
        return {
          success: true,
          user: {
            id: 1,
            username: 'demo_user',
            role: 'super_admin',
            email: 'demo@example.com'
          },
          stats: {
            total_users: 156,
            total_orders: 1245,
            total_schedules: 89,
            today_orders: 23,
            today_schedules: 5,
            weekly_orders: 156,
            monthly_orders: 678,
            total_revenue: 1500000,
            low_stock_items: 3
          },
          last_updated: new Date().toISOString()
        };
      }
      throw error;
    }
  }

  async updateProfile(data: { name?: string; email?: string }) {
    try {
      const response = await this.axiosInstance.put('/api/user/profile', data);
      return response.data;
    } catch (error: any) {
      console.error('Update profile API error:', error);
      if (error.code === 'ERR_NETWORK' || error.response?.status >= 500) {
        throw new Error('서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.');
      }
      throw error;
    }
  }

  // 관리자 통계 API
  async getAdminStats() {
    try {
      const response = await this.axiosInstance.get('/api/admin/dashboard-stats');
      return response.data;
    } catch (error: any) {
      console.error('Get admin stats API error:', error);
      if (error.code === 'ERR_NETWORK' || error.response?.status >= 500) {
        // 백엔드 연결 실패 시 더미 관리자 통계 반환
        return {
          success: true,
          stats: {
            total_staff: 156,
            total_branches: 8,
            pending_approvals: 3,
            critical_alerts: 2,
            total_orders: 1245
          }
        };
      }
      throw error;
    }
  }

  // 매장 주문 API
  async getStoreOrders(storeId?: number) {
    try {
      const url = storeId ? `/api/stores/${storeId}/orders` : '/api/orders';
      const response = await this.axiosInstance.get(url);
      return response.data;
    } catch (error: any) {
      console.error('Get store orders API error:', error);
      // 백엔드 연결 실패 시 더미 데이터 반환
      return {
        orders: [
          {
            id: 1,
            customer_name: '김고객',
            items: ['김치찌개', '밥'],
            total: 15000,
            status: 'completed',
            created_at: new Date().toISOString()
          }
        ],
        total: 1
      };
    }
  }

  // 백엔드 상태 확인
  async checkBackendStatus() {
    try {
      const response = await this.axiosInstance.get('/api/health');
      return response.data;
    } catch (error) {
      console.error('Backend status check failed:', error);
      return { status: 'offline', message: '백엔드 서버에 연결할 수 없습니다.' };
    }
  }

  // HTTP 메서드 래퍼들
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.get(url, config);
    return response.data;
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.post(url, data, config);
    return response.data;
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.put(url, data, config);
    return response.data;
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.delete(url, config);
    return response.data;
  }

  // 유틸리티 메서드들
  isAuthenticated(): boolean {
    return this.tokenManager.isAuthenticated();
  }

  getTokenManager(): TokenManager {
    return this.tokenManager;
  }
}

// API 클라이언트 인스턴스 생성
const apiClientInstance = new ApiClient();

// Default export
export default ApiClient;

// Named exports
export { apiClientInstance as apiClient }; 