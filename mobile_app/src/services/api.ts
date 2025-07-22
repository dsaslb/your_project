/**
 * 모바일 앱 API 서비스
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// API 응답 타입 정의
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface User {
  id: string;
  username: string;
  name: string;
  email: string;
  role: string;
  brand_id?: string;
  branch_id?: string;
}

export interface Employee {
  id: string;
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

export interface Schedule {
  id: string;
  employee_id: string;
  date: string;
  start_time: string;
  end_time: string;
  status: string;
  notes?: string;
}

export interface ClockRecord {
  id: string;
  employee_id: string;
  clock_in_time?: string;
  clock_out_time?: string;
  date: string;
  total_hours?: number;
  status: string;
}

export interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: string;
  is_read: boolean;
}

export interface DashboardStats {
  total_employees: number;
  active_employees: number;
  today_clock_ins: number;
  today_clock_outs: number;
  pending_schedules: number;
  recent_activities: any[];
}

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = __DEV__ 
      ? 'http://localhost:5000' 
      : 'https://your-production-domain.com';
    
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 요청 인터셉터
    this.api.interceptors.request.use(
      async (config) => {
        const token = await this.getAuthToken();
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
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // 토큰 만료 시 로그아웃
          await this.logout();
        }
        return Promise.reject(error);
      }
    );
  }

  // 인증 토큰 관리
  private async getAuthToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem('auth_token');
    } catch (error) {
      console.error('토큰 조회 실패:', error);
      return null;
    }
  }

  private async setAuthToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem('auth_token', token);
    } catch (error) {
      console.error('토큰 저장 실패:', error);
    }
  }

  private async removeAuthToken(): Promise<void> {
    try {
      await AsyncStorage.removeItem('auth_token');
    } catch (error) {
      console.error('토큰 삭제 실패:', error);
    }
  }

  // 인증 API
  async login(username: string, password: string): Promise<ApiResponse<{ user: User; token: string }>> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.post('/security/auth/login', {
        username,
        password,
      });

      if (response.data.success && response.data.data?.token) {
        await this.setAuthToken(response.data.data.token);
      }

      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '로그인에 실패했습니다.',
      };
    }
  }

  async logout(): Promise<void> {
    await this.removeAuthToken();
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.get('/user/profile');
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '사용자 정보 조회에 실패했습니다.',
      };
    }
  }

  // 직원 API
  async getEmployees(): Promise<ApiResponse<Employee[]>> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.get('/employees');
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '직원 목록 조회에 실패했습니다.',
      };
    }
  }

  async getEmployee(employeeId: string): Promise<ApiResponse<Employee>> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.get(`/employees/${employeeId}`);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '직원 정보 조회에 실패했습니다.',
      };
    }
  }

  // 스케줄 API
  async getSchedules(employeeId?: string): Promise<ApiResponse<Schedule[]>> {
    try {
      const params = employeeId ? { employee_id: employeeId } : {};
      const response: AxiosResponse<ApiResponse> = await this.api.get('/schedules', { params });
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '스케줄 조회에 실패했습니다.',
      };
    }
  }

  async createSchedule(scheduleData: Partial<Schedule>): Promise<ApiResponse<Schedule>> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.post('/schedules', scheduleData);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '스케줄 생성에 실패했습니다.',
      };
    }
  }

  async updateSchedule(scheduleId: string, scheduleData: Partial<Schedule>): Promise<ApiResponse<Schedule>> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.put(`/schedules/${scheduleId}`, scheduleData);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '스케줄 수정에 실패했습니다.',
      };
    }
  }

  async deleteSchedule(scheduleId: string): Promise<ApiResponse> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.delete(`/schedules/${scheduleId}`);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '스케줄 삭제에 실패했습니다.',
      };
    }
  }

  // 출근/퇴근 API
  async clockIn(employeeId: string, timestamp?: string): Promise<ApiResponse<ClockRecord>> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.post('/employee/clock-in', {
        employee_id: employeeId,
        timestamp: timestamp || new Date().toISOString(),
      });
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '출근 체크에 실패했습니다.',
      };
    }
  }

  async clockOut(employeeId: string, timestamp?: string): Promise<ApiResponse<ClockRecord>> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.post('/employee/clock-out', {
        employee_id: employeeId,
        timestamp: timestamp || new Date().toISOString(),
      });
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '퇴근 체크에 실패했습니다.',
      };
    }
  }

  async getClockRecords(employeeId?: string, date?: string): Promise<ApiResponse<ClockRecord[]>> {
    try {
      const params: any = {};
      if (employeeId) params.employee_id = employeeId;
      if (date) params.date = date;

      const response: AxiosResponse<ApiResponse> = await this.api.get('/employee/clock-records', { params });
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '출근 기록 조회에 실패했습니다.',
      };
    }
  }

  // 대시보드 API
  async getDashboardStats(): Promise<ApiResponse<DashboardStats>> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.get('/employee/dashboard');
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '대시보드 정보 조회에 실패했습니다.',
      };
    }
  }

  async getAdminDashboard(): Promise<ApiResponse<any>> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.get('/admin/dashboard');
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '관리자 대시보드 조회에 실패했습니다.',
      };
    }
  }

  // 알림 API
  async getNotifications(): Promise<ApiResponse<Notification[]>> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.get('/notifications');
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '알림 조회에 실패했습니다.',
      };
    }
  }

  async markNotificationAsRead(notificationId: string): Promise<ApiResponse> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.put(`/notifications/${notificationId}/read`);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '알림 읽음 처리에 실패했습니다.',
      };
    }
  }

  async markAllNotificationsAsRead(): Promise<ApiResponse> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.put('/notifications/read-all');
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '모든 알림 읽음 처리에 실패했습니다.',
      };
    }
  }

  // 브랜드/매장 API
  async getBrands(): Promise<ApiResponse<any[]>> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.get('/brands');
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '브랜드 목록 조회에 실패했습니다.',
      };
    }
  }

  async getBranches(brandId?: string): Promise<ApiResponse<any[]>> {
    try {
      const params = brandId ? { brand_id: brandId } : {};
      const response: AxiosResponse<ApiResponse> = await this.api.get('/branches', { params });
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '매장 목록 조회에 실패했습니다.',
      };
    }
  }

  // 파일 업로드 API
  async uploadFile(file: any, type: 'profile' | 'document' | 'image'): Promise<ApiResponse<{ url: string }>> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', type);

      const response: AxiosResponse<ApiResponse> = await this.api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '파일 업로드에 실패했습니다.',
      };
    }
  }

  // 실시간 알림 (WebSocket 대체)
  async subscribeToNotifications(callback: (notification: Notification) => void): Promise<void> {
    // 실제 구현에서는 WebSocket을 사용하지만, 여기서는 폴링으로 대체
    setInterval(async () => {
      const response = await this.getNotifications();
      if (response.success && response.data) {
        const unreadNotifications = response.data.filter(n => !n.is_read);
        unreadNotifications.forEach(callback);
      }
    }, 30000); // 30초마다 폴링
  }

  // 오프라인 데이터 동기화
  async syncOfflineData(): Promise<ApiResponse> {
    try {
      // 오프라인 저장된 데이터 가져오기
      const offlineData = await AsyncStorage.getItem('offline_data');
      if (offlineData) {
        const data = JSON.parse(offlineData);
        
        // 서버에 동기화
        const response: AxiosResponse<ApiResponse> = await this.api.post('/sync', data);
        
        // 동기화 성공 시 오프라인 데이터 삭제
        if (response.data.success) {
          await AsyncStorage.removeItem('offline_data');
        }
        
        return response.data;
      }
      
      return { success: true, message: '동기화할 데이터가 없습니다.' };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || '데이터 동기화에 실패했습니다.',
      };
    }
  }

  // 오프라인 데이터 저장
  async saveOfflineData(action: string, data: any): Promise<void> {
    try {
      const offlineData = await AsyncStorage.getItem('offline_data');
      const existingData = offlineData ? JSON.parse(offlineData) : [];
      
      existingData.push({
        action,
        data,
        timestamp: new Date().toISOString(),
      });
      
      await AsyncStorage.setItem('offline_data', JSON.stringify(existingData));
    } catch (error) {
      console.error('오프라인 데이터 저장 실패:', error);
    }
  }

  // 헬스체크
  async healthCheck(): Promise<ApiResponse> {
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.get('/health');
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: '서버 연결에 실패했습니다.',
      };
    }
  }
}

// 싱글톤 인스턴스
export const apiService = new ApiService();
export default apiService; 