import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_CONFIG } from '../config/api';
import { v4 as uuid } from 'uuid';

// API 클라이언트 클래스
class ApiClient {
  private instance: AxiosInstance;
  private isRefreshing = false;
  private failedQueue: Array<{
    resolve: (value?: any) => void;
    reject: (reason?: any) => void;
  }> = [];

  constructor() {
    this.instance = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: getApiConfig().timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  // 인터셉터 설정
  private setupInterceptors() {
    // 요청 인터셉터
    this.instance.interceptors.request.use(
      async (config) => {
        const token = await this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        // POST, PUT, DELETE 요청에 X-Idempotency-Key 자동 추가
        if (config.method && ['post', 'put', 'delete'].includes(config.method.toLowerCase())) {
          if (!config.headers['X-Idempotency-Key']) {
            const idempotencyKey = uuid();
            config.headers['X-Idempotency-Key'] = idempotencyKey;
            console.log(`🔑 Idempotency Key 추가: ${idempotencyKey} for ${config.method.toUpperCase()} ${config.url}`);
          }
        }
        
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 응답 인터셉터
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject });
            }).then(() => {
              return this.instance(originalRequest);
            }).catch((err) => {
              return Promise.reject(err);
            });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            // 토큰 갱신 로직 (필요시)
            // const newToken = await this.refreshToken();
            // await this.setAuthToken(newToken);
            
            // 실패한 요청들을 재시도
            this.failedQueue.forEach(({ resolve }) => {
              resolve();
            });
            this.failedQueue = [];
            
            return this.instance(originalRequest);
          } catch (refreshError) {
            // 토큰 갱신 실패 시 로그아웃
            await this.logout();
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // 인증 토큰 관리
  private async getAuthToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem(API_CONFIG.JWT.STORAGE_KEY);
    } catch (error) {
      console.error('토큰 읽기 실패:', error);
      return null;
    }
  }

  private async setAuthToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem(API_CONFIG.JWT.STORAGE_KEY, token);
    } catch (error) {
      console.error('토큰 저장 실패:', error);
    }
  }

  private async removeAuthToken(): Promise<void> {
    try {
      await AsyncStorage.removeItem(API_CONFIG.JWT.STORAGE_KEY);
    } catch (error) {
      console.error('토큰 삭제 실패:', error);
    }
  }

  // 로그아웃
  async logout(): Promise<void> {
    await this.removeAuthToken();
    // 추가 정리 작업
  }

  // HTTP 메서드들
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.get(url, config);
    return response.data;
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.post(url, data, config);
    return response.data;
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.put(url, data, config);
    return response.data;
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.delete(url, config);
    return response.data;
  }

  // 로그인 후 토큰 저장
  async login(credentials: { username: string; password: string }) {
    try {
      const response = await this.post(API_CONFIG.ENDPOINTS.LOGIN, credentials);
      if (response.token) {
        await this.setAuthToken(response.token);
      }
      return response;
    } catch (error) {
      console.error('로그인 실패:', error);
      throw error;
    }
  }

  // 푸시 토큰 등록
  async registerPushToken(expoPushToken: string) {
    try {
      return await this.post(API_CONFIG.ENDPOINTS.PUSH_REGISTER, {
        expo_push_token: expoPushToken,
      });
    } catch (error) {
      console.error('푸시 토큰 등록 실패:', error);
      throw error;
    }
  }

  // 출퇴근 기록
  async clockAttendance(data: {
    type: 'in' | 'out';
    lat?: number;
    lng?: number;
    qr?: string;
  }) {
    try {
      return await this.post(API_CONFIG.ENDPOINTS.ATTENDANCE_CLOCK, data);
    } catch (error) {
      console.error('출퇴근 기록 실패:', error);
      throw error;
    }
  }

  // 재고 조사
  async checkInventory(data: {
    barcode: string;
    qty: number;
    photo_url?: string;
  }) {
    try {
      return await this.post(API_CONFIG.ENDPOINTS.INVENTORY_CHECK, data);
    } catch (error) {
      console.error('재고 조사 실패:', error);
      throw error;
    }
  }

  // 재고 히스토리 조회
  async getInventoryHistory(limit: number = 50) {
    try {
      return await this.get(`${API_CONFIG.ENDPOINTS.INVENTORY_HISTORY}?limit=${limit}`);
    } catch (error) {
      console.error('재고 히스토리 조회 실패:', error);
      throw error;
    }
  }

  // 발주 목록 조회
  async getPurchaseOrders() {
    try {
      return await this.get(API_CONFIG.ENDPOINTS.PURCHASE_ORDERS);
    } catch (error) {
      console.error('발주 목록 조회 실패:', error);
      throw error;
    }
  }

  // 스케줄 조회
  async getSchedule() {
    try {
      return await this.get(API_CONFIG.ENDPOINTS.SCHEDULE);
    } catch (error) {
      console.error('스케줄 조회 실패:', error);
      throw error;
    }
  }

  // 휴가 신청
  async requestLeave(leaveData: {
    type: string;
    start_date: string;
    end_date: string;
    reason?: string;
  }) {
    try {
      return await this.post(API_CONFIG.ENDPOINTS.SCHEDULE_LEAVE, leaveData);
    } catch (error) {
      console.error('휴가 신청 실패:', error);
      throw error;
    }
  }

  // 근무 교대 신청
  async requestScheduleSwap(swapData: {
    target_date: string;
    swap_with_user: string;
    reason?: string;
  }) {
    try {
      return await this.post(API_CONFIG.ENDPOINTS.SCHEDULE_SWAP, swapData);
    } catch (error) {
      console.error('근무 교대 신청 실패:', error);
      throw error;
    }
  }

  // 발주 생성
  async createPurchaseOrder(data: {
    items: Array<{ barcode: string; name: string; qty: number }>;
  }) {
    try {
      return await this.post(API_CONFIG.ENDPOINTS.PURCHASE_ORDERS, data);
    } catch (error) {
      console.error('발주 생성 실패:', error);
      throw error;
    }
  }

  // 스케줄 조회
  async getSchedule() {
    try {
      return await this.get(API_CONFIG.ENDPOINTS.SCHEDULE);
    } catch (error) {
      console.error('스케줄 조회 실패:', error);
      throw error;
    }
  }

  // 주문 상태 업데이트
  async updateOrderStatus(data: {
    order_id: number;
    status: string;
  }) {
    try {
      return await this.post(API_CONFIG.ENDPOINTS.ORDER_STATUS, data);
    } catch (error) {
      console.error('주문 상태 업데이트 실패:', error);
      throw error;
    }
  }
}

// 싱글톤 인스턴스
export const apiClient = new ApiClient();

// 편의 함수들
export const api = {
  get: apiClient.get.bind(apiClient),
  post: apiClient.post.bind(apiClient),
  put: apiClient.put.bind(apiClient),
  delete: apiClient.delete.bind(apiClient),
  login: apiClient.login.bind(apiClient),
  logout: apiClient.logout.bind(apiClient),
  registerPushToken: apiClient.registerPushToken.bind(apiClient),
  clockAttendance: apiClient.clockAttendance.bind(apiClient),
  checkInventory: apiClient.checkInventory.bind(apiClient),
  getInventoryHistory: apiClient.getInventoryHistory.bind(apiClient),
  createPurchaseOrder: apiClient.createPurchaseOrder.bind(apiClient),
  getSchedule: apiClient.getSchedule.bind(apiClient),
  updateOrderStatus: apiClient.updateOrderStatus.bind(apiClient),
};
