import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';

// API 기본 설정
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:5000';

// Axios 인스턴스 생성
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터
apiClient.interceptors.request.use(
  async (config) => {
    // 네트워크 연결 확인
    const netInfo = await NetInfo.fetch();
    if (!netInfo.isConnected) {
      throw new Error('네트워크 연결을 확인해주세요.');
    }

    // 토큰 추가
    const token = await AsyncStorage.getItem('auth_token');
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
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // 401 에러 (토큰 만료) 처리
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // 토큰 갱신 시도
        const refreshToken = await AsyncStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { token: newToken } = response.data;
          await AsyncStorage.setItem('auth_token', newToken);

          // 원래 요청 재시도
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // 토큰 갱신 실패 시 로그아웃 처리
        await AsyncStorage.removeItem('auth_token');
        await AsyncStorage.removeItem('refresh_token');
        await AsyncStorage.removeItem('auth_user');
        
        // 로그인 화면으로 리다이렉트 (네비게이션 처리 필요)
        throw new Error('세션이 만료되었습니다. 다시 로그인해주세요.');
      }
    }

    return Promise.reject(error);
  }
);

// API 헬퍼 함수들
export const apiHelpers = {
  // GET 요청
  get: async (url: string, config = {}) => {
    try {
      const response = await apiClient.get(url, config);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // POST 요청
  post: async (url: string, data = {}, config = {}) => {
    try {
      const response = await apiClient.post(url, data, config);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // PUT 요청
  put: async (url: string, data = {}, config = {}) => {
    try {
      const response = await apiClient.put(url, data, config);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // DELETE 요청
  delete: async (url: string, config = {}) => {
    try {
      const response = await apiClient.delete(url, config);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // 파일 업로드
  upload: async (url: string, formData: FormData, config = {}) => {
    try {
      const response = await apiClient.post(url, formData, {
        ...config,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

// 에러 처리 함수
const handleApiError = (error: any) => {
  if (error.response) {
    // 서버 응답이 있는 경우
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return new Error(data.message || '잘못된 요청입니다.');
      case 401:
        return new Error('인증이 필요합니다.');
      case 403:
        return new Error('접근 권한이 없습니다.');
      case 404:
        return new Error('요청한 리소스를 찾을 수 없습니다.');
      case 500:
        return new Error('서버 오류가 발생했습니다.');
      default:
        return new Error(data.message || '알 수 없는 오류가 발생했습니다.');
    }
  } else if (error.request) {
    // 요청은 보냈지만 응답이 없는 경우
    return new Error('서버에 연결할 수 없습니다.');
  } else {
    // 요청 자체에 문제가 있는 경우
    return new Error(error.message || '네트워크 오류가 발생했습니다.');
  }
};

// API 엔드포인트 상수
export const API_ENDPOINTS = {
  // 인증
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
    VALIDATE: '/api/auth/validate',
    PROFILE: '/api/auth/profile',
  },

  // 대시보드
  DASHBOARD: {
    STATS: '/api/dashboard/stats',
    REALTIME: '/api/dashboard/realtime',
    SALES: '/api/dashboard/sales',
  },

  // 직원 관리
  STAFF: {
    LIST: '/api/staff',
    CREATE: '/api/staff',
    UPDATE: (id: number) => `/api/staff/${id}`,
    DELETE: (id: number) => `/api/staff/${id}`,
    ATTENDANCE: '/api/staff/attendance',
  },

  // 주문 관리
  ORDERS: {
    LIST: '/api/orders',
    CREATE: '/api/orders',
    UPDATE: (id: number) => `/api/orders/${id}`,
    DELETE: (id: number) => `/api/orders/${id}`,
    STATUS: (id: number) => `/api/orders/${id}/status`,
  },

  // 재고 관리
  INVENTORY: {
    LIST: '/api/inventory',
    CREATE: '/api/inventory',
    UPDATE: (id: number) => `/api/inventory/${id}`,
    DELETE: (id: number) => `/api/inventory/${id}`,
    ALERTS: '/api/inventory/alerts',
  },

  // 근무 일정
  SCHEDULE: {
    LIST: '/api/schedule',
    CREATE: '/api/schedule',
    UPDATE: (id: number) => `/api/schedule/${id}`,
    DELETE: (id: number) => `/api/schedule/${id}`,
    MY_SCHEDULE: '/api/schedule/my',
  },

  // 출근 관리
  ATTENDANCE: {
    CHECK_IN: '/api/attendance/check-in',
    CHECK_OUT: '/api/attendance/check-out',
    HISTORY: '/api/attendance/history',
    REPORT: '/api/attendance/report',
  },

  // 알림
  NOTIFICATIONS: {
    LIST: '/api/notifications',
    MARK_READ: (id: number) => `/api/notifications/${id}/read`,
    MARK_ALL_READ: '/api/notifications/mark-all-read',
    COUNT: '/api/notifications/count',
  },

  // 고급 기능
  ADVANCED: {
    CHATBOT: '/api/advanced/chatbot/message',
    VOICE: '/api/advanced/voice/process',
    IMAGE: '/api/advanced/image/analyze',
    TRANSLATION: '/api/advanced/translate/text',
  },

  // 보고서
  REPORTS: {
    SALES: '/api/reports/sales',
    ATTENDANCE: '/api/reports/attendance',
    INVENTORY: '/api/reports/inventory',
    STAFF: '/api/reports/staff',
  },

  // 분석
  ANALYTICS: {
    SALES: '/api/analytics/sales',
    ATTENDANCE: '/api/analytics/attendance',
    PERFORMANCE: '/api/analytics/performance',
    PREDICTIONS: '/api/analytics/predictions',
  },
};

export default apiClient; 