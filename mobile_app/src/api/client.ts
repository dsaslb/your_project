/**
 * 📡 API 클라이언트
 * 
 * 모바일 앱에서 백엔드 API와 통신하기 위한 클라이언트
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL, API_ENDPOINTS, APP_CONFIG } from '../config/env';

// API 클라이언트 인스턴스 생성
export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: APP_CONFIG.API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 - JWT 토큰 자동 추가
api.interceptors.request.use(
  async (config: AxiosRequestConfig) => {
    try {
      const token = await AsyncStorage.getItem('token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('토큰 로드 실패:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 에러 처리
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error) => {
    if (error.response?.status === 401) {
      // 토큰 만료 시 자동 로그아웃
      try {
        await AsyncStorage.removeItem('token');
        await AsyncStorage.removeItem('user');
        // 로그인 화면으로 리다이렉트 로직 추가 필요
      } catch (storageError) {
        console.error('토큰 제거 실패:', storageError);
      }
    }
    return Promise.reject(error);
  }
);

// API 함수들
export const mobileAPI = {
  // 로그인
  login: async (username: string, password: string) => {
    const response = await api.post(API_ENDPOINTS.LOGIN, {
      username,
      password,
    });
    return response.data;
  },

  // 푸시 토큰 등록
  registerPushToken: async (expoPushToken: string) => {
    const response = await api.post(API_ENDPOINTS.PUSH_REGISTER, {
      expo_push_token: expoPushToken,
    });
    return response.data;
  },

  // 출퇴근 체크
  clockAttendance: async (type: 'in' | 'out', data: {
    lat?: number;
    lng?: number;
    qr?: string;
  }) => {
    const response = await api.post(API_ENDPOINTS.ATTENDANCE_CLOCK, {
      type,
      ...data,
    });
    return response.data;
  },

  // 재고 조사
  checkInventory: async (data: {
    barcode: string;
    qty: number;
    photo_url?: string;
  }) => {
    const response = await api.post(API_ENDPOINTS.INVENTORY_CHECK, data);
    return response.data;
  },

  // 발주 생성
  createPurchaseOrder: async (items: Array<{
    barcode: string;
    name: string;
    qty: number;
  }>) => {
    const response = await api.post(API_ENDPOINTS.PURCHASE_ORDERS, {
      items,
    });
    return response.data;
  },

  // 스케줄 조회
  getSchedule: async () => {
    const response = await api.get(API_ENDPOINTS.SCHEDULE);
    return response.data;
  },

  // 주문 상태 변경
  updateOrderStatus: async (orderId: number, status: string) => {
    const response = await api.post(API_ENDPOINTS.ORDERS_UPDATE_STATUS, {
      order_id: orderId,
      status,
    });
    return response.data;
  },

  // 대시보드 데이터
  getDashboard: async () => {
    const response = await api.get(API_ENDPOINTS.DASHBOARD);
    return response.data;
  },
};

// 기본 export
export default mobileAPI;
