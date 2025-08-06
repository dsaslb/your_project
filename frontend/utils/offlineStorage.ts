export class OfflineStorage {
  // 스케줄 관련 메서드들
  static saveSchedules(schedules: any[]) {
    try {
      localStorage.setItem('schedules', JSON.stringify(schedules));
      console.log('✅ 스케줄 데이터 저장 완료:', schedules.length, '개');
    } catch (error) {
      console.error('❌ 스케줄 데이터 저장 실패:', error);
    }
  }

  static loadSchedules(): any[] {
    try {
      const data = localStorage.getItem('schedules');
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('❌ 스케줄 데이터 로드 실패:', error);
      return [];
    }
  }

  static saveEmployees(employees: any[]) {
    try {
      localStorage.setItem('employees', JSON.stringify(employees));
      console.log('✅ 직원 데이터 저장 완료:', employees.length, '개');
    } catch (error) {
      console.error('❌ 직원 데이터 저장 실패:', error);
    }
  }

  static loadEmployees(): any[] {
    try {
      const data = localStorage.getItem('employees');
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('❌ 직원 데이터 로드 실패:', error);
      return [];
    }
  }

  // 캐시 데이터 관련 메서드들
  static async saveCachedData(key: string, type: string, data: any) {
    try {
      const cacheKey = `cache_${type}_${key}`;
      const cacheData = {
        data,
        timestamp: Date.now(),
        type
      };
      localStorage.setItem(cacheKey, JSON.stringify(cacheData));
      console.log('✅ 캐시 데이터 저장 완료:', cacheKey);
    } catch (error) {
      console.error('❌ 캐시 데이터 저장 실패:', error);
    }
  }

  static async getCachedData(key: string): Promise<any | null> {
    try {
      const cacheKey = `cache_${key}`;
      const data = localStorage.getItem(cacheKey);
      if (!data) return null;
      
      const cacheData = JSON.parse(data);
      const now = Date.now();
      const cacheAge = now - cacheData.timestamp;
      const maxAge = 30 * 60 * 1000; // 30분
      
      if (cacheAge > maxAge) {
        localStorage.removeItem(cacheKey);
        return null;
      }
      
      return cacheData.data;
    } catch (error) {
      console.error('❌ 캐시 데이터 로드 실패:', error);
      return null;
    }
  }

  // 오프라인 데이터 관련 메서드들
  static async saveOfflineData(type: string, action: string, data: any) {
    try {
      const offlineKey = `offline_${type}_${action}_${Date.now()}`;
      const offlineData = {
        type,
        action,
        data,
        timestamp: Date.now(),
        synced: false
      };
      localStorage.setItem(offlineKey, JSON.stringify(offlineData));
      console.log('✅ 오프라인 데이터 저장 완료:', offlineKey);
    } catch (error) {
      console.error('❌ 오프라인 데이터 저장 실패:', error);
    }
  }

  static async getOfflineData(): Promise<any[]> {
    try {
      const offlineData: any[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('offline_')) {
          const data = localStorage.getItem(key);
          if (data) {
            offlineData.push(JSON.parse(data));
          }
        }
      }
      return offlineData;
    } catch (error) {
      console.error('❌ 오프라인 데이터 로드 실패:', error);
      return [];
    }
  }

  static async clearOfflineData(key: string) {
    try {
      localStorage.removeItem(key);
      console.log('✅ 오프라인 데이터 삭제 완료:', key);
    } catch (error) {
      console.error('❌ 오프라인 데이터 삭제 실패:', error);
    }
  }

  // 네트워크 상태 확인
  static isOnline(): boolean {
    return navigator.onLine;
  }

  // 저장소 용량 확인
  static getStorageUsage(): { used: number; total: number; percentage: number } {
    try {
      let used = 0;
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key) {
          const value = localStorage.getItem(key);
          used += (key.length + (value?.length || 0)) * 2; // UTF-16 문자열은 2바이트
        }
      }
      
      const total = 5 * 1024 * 1024; // 5MB (일반적인 localStorage 제한)
      const percentage = (used / total) * 100;
      
      return { used, total, percentage };
    } catch (error) {
      console.error('❌ 저장소 용량 확인 실패:', error);
      return { used: 0, total: 0, percentage: 0 };
    }
  }
} 