import axios from "axios";
import Constants from "expo-constants";
import * as SecureStore from "expo-secure-store";
import { Platform } from "react-native";
import { v4 as uuidv4 } from 'uuid';
import { networkService } from "../services/NetworkService";
import { localStorageService } from "../services/LocalStorageService";
import { offlineQueueService } from "../services/OfflineQueueService";

// 웹과 네이티브 환경을 구분하여 토큰 저장/조회
const tokenStorage = {
  async getItem(key: string): Promise<string | null> {
    if (Platform.OS === 'web') {
      return localStorage.getItem(key);
    } else {
      return await SecureStore.getItemAsync(key);
    }
  },
  
  async setItem(key: string, value: string): Promise<void> {
    if (Platform.OS === 'web') {
      localStorage.setItem(key, value);
    } else {
      await SecureStore.setItemAsync(key, value);
    }
  },
  
  async removeItem(key: string): Promise<void> {
    if (Platform.OS === 'web') {
      localStorage.removeItem(key);
    } else {
      await SecureStore.deleteItemAsync(key);
    }
  }
};

const api = axios.create({
  baseURL: (Constants.expoConfig?.extra as any)?.apiUrl || "http://localhost:5000",
  timeout: 5000, // 타임아웃을 짧게 설정
});

api.interceptors.request.use(async (config) => {
  const token = await tokenStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  async (err) => {
    if (err.response?.status === 401) await tokenStorage.removeItem("token");
    return Promise.reject(err);
  }
);

// 모바일 API 메서드들 (새로운 v2 API 사용)
export const mobileAPI = {
  // 대시보드 데이터 가져오기
  async getDashboard() {
    try {
      const response = await api.get('/api/mobile/dashboard');
      return response.data;
    } catch (error) {
      console.warn('서버 연결 실패, 기본 대시보드 데이터 사용:', error);
      
      // 서버 연결 실패 시 기본 데이터 반환
      return {
        user: {
          id: 1,
          username: '사용자',
          role: 'employee'
        },
        today_schedule: '09:00 - 18:00',
        attendance_status: '미체크',
        pending_orders: 0,
        inventory_alerts: 0,
        quick_stats: {
          today_orders: 0,
          pending_orders: 0,
          today_revenue: 0,
          staff_on_duty: 0
        },
        recent_activities: [
          {
            id: 1,
            type: 'system',
            title: '서버 연결 실패',
            message: '서버에 연결할 수 없습니다. 오프라인 모드로 실행 중입니다.',
            timestamp: new Date().toISOString(),
            priority: 'high'
          }
        ],
        quick_actions: [
          {
            id: 'attendance',
            title: '출퇴근',
            icon: 'clock',
            color: 'orange'
          },
          {
            id: 'inventory_check',
            title: '재고 확인',
            icon: 'package',
            color: 'green'
          }
        ],
        timestamp: new Date().toISOString()
      };
    }
  },

  // 출근 체크
  async clockIn(data: { lat?: number; lng?: number; qr?: string; localId?: string }) {
    if (!networkService.isOnline()) {
      // 오프라인 상태: 배치 큐에 추가
      const { batchSyncService } = await import('../services/BatchSyncService');
      
      const payload = {
        user_id: 1, // 실제로는 현재 사용자 ID
        type: 'in',
        lat: data.lat || 0,
        lng: data.lng || 0,
        timestamp: new Date().toISOString(),
        qr: data.qr
      };

      const idem = await batchSyncService.enqueue('attendance', payload, 10);
      
      return {
        id: idem,
        at: new Date().toISOString(),
        status: 'offline_pending'
      };
    }

    const response = await api.post('/api/mobile/attendance/clock-in', data);
    return response.data;
  },

  // 퇴근 체크
  async clockOut(data: { lat?: number; lng?: number; localId?: string }) {
    if (!networkService.isOnline()) {
      // 오프라인 상태: 배치 큐에 추가
      const { batchSyncService } = await import('../services/BatchSyncService');
      
      const payload = {
        user_id: 1, // 실제로는 현재 사용자 ID
        type: 'out',
        lat: data.lat || 0,
        lng: data.lng || 0,
        timestamp: new Date().toISOString()
      };

      const idem = await batchSyncService.enqueue('attendance', payload, 10);
      
      return {
        id: idem,
        at: new Date().toISOString(),
        status: 'offline_pending'
      };
    }

    const response = await api.post('/api/mobile/attendance/clock-out', data);
    return response.data;
  },

  // 로그인
  async login(username: string, password: string) {
    const response = await api.post('/api/mobile/login', { username, password });
    return response.data;
  },

  // 사용자 정보 가져오기
  async getMe() {
    const response = await api.get('/api/mobile/auth/me');
    return response.data;
  },

  // 재고 조사
  async checkInventory(data: { barcode: string; qty: number; photo_url?: string }) {
    if (!networkService.isOnline()) {
      // 오프라인 상태: 배치 큐에 추가
      const { batchSyncService } = await import('../services/BatchSyncService');
      
      const payload = {
        user_id: 1, // 실제로는 현재 사용자 ID
        barcode: data.barcode,
        quantity: data.qty,
        photo_url: data.photo_url,
        timestamp: new Date().toISOString()
      };

      const idem = await batchSyncService.enqueue('inventory', payload, 5);
      
      return {
        id: idem,
        status: 'offline_pending'
      };
    }

    const response = await api.post('/api/mobile/inventory/check', data);
    return response.data;
  },

  // 발주 요청
  async createPurchaseOrder(data: { branch_id: string; items: any[] }) {
    if (!networkService.isOnline()) {
      // 오프라인 상태: 배치 큐에 추가
      const { batchSyncService } = await import('../services/BatchSyncService');
      
      const payload = {
        user_id: 1, // 실제로는 현재 사용자 ID
        branch_id: data.branch_id,
        items: data.items,
        timestamp: new Date().toISOString()
      };

      const idem = await batchSyncService.enqueue('po', payload, 8);
      
      return {
        order_id: idem,
        status: 'offline_pending'
      };
    }

    const response = await api.post('/api/mobile/purchase-orders', data);
    return response.data;
  },

  // 스케줄 조회
  async getSchedules(startDate?: string, endDate?: string) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/api/mobile/schedules?${params.toString()}`);
    return response.data;
  },

  // 푸시 토큰 등록
  async registerPushToken(token: string, platform: string) {
    const response = await api.post('/api/mobile/notifications/register-token', {
      token,
      platform
    });
    return response.data;
  },

  // 헬스체크
  async healthCheck() {
    const response = await api.get('/api/mobile/health');
    return response.data;
  },

  // 배치 동기화
  async syncBatch(data: {
    items: Array<{
      type: 'attendance' | 'po' | 'inventory';
      idem: string;
      payload: any;
    }>;
    meta: {
      device_id: string;
      branch_id: number;
      user_id: number;
    };
  }) {
    const response = await api.post('/api/mobile/sync/batch', data, {
      headers: {
        'X-Idempotency-Key': uuidv4()
      }
    });
    return response.data;
  },

  // 동기화 상태 조회
  async getSyncStatus() {
    const response = await api.get('/api/mobile/sync/status');
    return response.data;
  },

  // 동기화 헬스체크
  async getSyncHealth() {
    const response = await api.get('/api/mobile/sync/health');
    return response.data;
  }
};

export default api;