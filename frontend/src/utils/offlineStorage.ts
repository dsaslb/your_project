// IndexedDB를 활용한 오프라인 임시저장 유틸리티

interface OfflineData {
  id: string;
  type: 'create' | 'update' | 'delete';
  data: any;
  timestamp: string;
  retryCount: number;
}

interface CachedData {
  key: string;
  data: any;
  timestamp: string;
  version: string;
}

class OfflineStorage {
  private readonly OFFLINE_DATA_KEY = 'offline_data';
  private readonly CACHED_DATA_KEY = 'cached_data';
  private readonly MAX_RETRY_COUNT = 3;
  private readonly CACHE_EXPIRY_HOURS = 24;

  // 오프라인 데이터 저장
  async saveOfflineData(collection: string, type: 'create' | 'update' | 'delete', data: any): Promise<void> {
    try {
      const offlineData: OfflineData = {
        id: `${collection}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type,
        data,
        timestamp: new Date().toISOString(),
        retryCount: 0
      };

      const existingData = this.getOfflineData();
      existingData.push(offlineData);
      
      localStorage.setItem(this.OFFLINE_DATA_KEY, JSON.stringify(existingData));
      
      // 실시간 동기화: 오프라인 데이터 저장 이벤트 브로드캐스트
      this.broadcastOfflineDataChange('offline_data_saved', { collection, type, data });
      
      console.log(`오프라인 데이터 저장됨: ${collection} - ${type}`, offlineData);
    } catch (error) {
      console.error('오프라인 데이터 저장 실패:', error);
    }
  }

  // 오프라인 데이터 조회
  getOfflineData(): OfflineData[] {
    try {
      const data = localStorage.getItem(this.OFFLINE_DATA_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('오프라인 데이터 조회 실패:', error);
      return [];
    }
  }

  // 오프라인 데이터 삭제
  removeOfflineData(id: string): void {
    try {
      const existingData = this.getOfflineData();
      const filteredData = existingData.filter(item => item.id !== id);
      localStorage.setItem(this.OFFLINE_DATA_KEY, JSON.stringify(filteredData));
      
      // 실시간 동기화: 오프라인 데이터 삭제 이벤트 브로드캐스트
      this.broadcastOfflineDataChange('offline_data_removed', { id });
    } catch (error) {
      console.error('오프라인 데이터 삭제 실패:', error);
    }
  }

  // 캐시 데이터 저장
  async saveCachedData(collection: string, key: string, data: any, version?: string): Promise<void> {
    try {
      const cachedData: CachedData = {
        key: `${collection}_${key}`,
        data,
        timestamp: new Date().toISOString(),
        version: version || '1.0'
      };

      const existingCache = this.getCachedData();
      const filteredCache = existingCache.filter((item: CachedData) => item.key !== cachedData.key);
      filteredCache.push(cachedData);
      
      localStorage.setItem(this.CACHED_DATA_KEY, JSON.stringify(filteredCache));
      
      // 실시간 동기화: 캐시 데이터 저장 이벤트 브로드캐스트
      this.broadcastOfflineDataChange('cache_data_saved', { collection, key, data });
    } catch (error) {
      console.error('캐시 데이터 저장 실패:', error);
    }
  }

  // 캐시 데이터 조회
  getCachedData(collection?: string, key?: string): any {
    try {
      const data = localStorage.getItem(this.CACHED_DATA_KEY);
      if (!data) return null;

      const cachedData: CachedData[] = JSON.parse(data);
      const now = new Date();
      
      // 만료된 캐시 제거
      const validCache = cachedData.filter((item: CachedData) => {
        const cacheTime = new Date(item.timestamp);
        const hoursDiff = (now.getTime() - cacheTime.getTime()) / (1000 * 60 * 60);
        return hoursDiff < this.CACHE_EXPIRY_HOURS;
      });

      // 만료된 캐시가 있으면 업데이트
      if (validCache.length !== cachedData.length) {
        localStorage.setItem(this.CACHED_DATA_KEY, JSON.stringify(validCache));
      }

      if (collection && key) {
        const targetKey = `${collection}_${key}`;
        const item = validCache.find(cache => cache.key === targetKey);
        return item ? item.data : null;
      }

      return validCache;
    } catch (error) {
      console.error('캐시 데이터 조회 실패:', error);
      return null;
    }
  }

  // 캐시 데이터 삭제
  removeCachedData(collection: string, key: string): void {
    try {
      const existingCache = this.getCachedData();
      const targetKey = `${collection}_${key}`;
      const filteredCache = existingCache.filter((item: CachedData) => item.key !== targetKey);
      localStorage.setItem(this.CACHED_DATA_KEY, JSON.stringify(filteredCache));
      
      // 실시간 동기화: 캐시 데이터 삭제 이벤트 브로드캐스트
      this.broadcastOfflineDataChange('cache_data_removed', { collection, key });
    } catch (error) {
      console.error('캐시 데이터 삭제 실패:', error);
    }
  }

  // 오프라인 데이터 동기화 시도
  async syncOfflineData(): Promise<{ success: boolean; syncedCount: number; errors: string[] }> {
    const offlineData = this.getOfflineData();
    const results = {
      success: true,
      syncedCount: 0,
      errors: [] as string[]
    };

    for (const item of offlineData) {
      try {
        const success = await this.syncSingleOfflineData(item);
        if (success) {
          this.removeOfflineData(item.id);
          results.syncedCount++;
        } else {
          item.retryCount++;
          if (item.retryCount >= this.MAX_RETRY_COUNT) {
            results.errors.push(`최대 재시도 횟수 초과: ${item.id}`);
            this.removeOfflineData(item.id);
          }
        }
      } catch (error) {
        console.error(`오프라인 데이터 동기화 실패: ${item.id}`, error);
        results.errors.push(`동기화 오류: ${item.id} - ${error}`);
        results.success = false;
      }
    }

    // 실시간 동기화: 동기화 완료 이벤트 브로드캐스트
    this.broadcastOfflineDataChange('offline_sync_completed', results);

    return results;
  }

  // 단일 오프라인 데이터 동기화
  private async syncSingleOfflineData(item: OfflineData): Promise<boolean> {
    try {
      const { collection, type, data } = this.parseOfflineData(item);
      
      switch (type) {
        case 'create':
          await this.apiCall('POST', `/api/${collection}`, data);
          break;
        case 'update':
          await this.apiCall('PUT', `/api/${collection}/${data.id}`, data);
          break;
        case 'delete':
          await this.apiCall('DELETE', `/api/${collection}/${data.id}`);
          break;
      }
      
      return true;
    } catch (error) {
      console.error(`단일 오프라인 데이터 동기화 실패: ${item.id}`, error);
      return false;
    }
  }

  // 오프라인 데이터 파싱
  private parseOfflineData(item: OfflineData): { collection: string; type: string; data: any } {
    const [collection, ...rest] = item.id.split('_');
    return {
      collection,
      type: item.type,
      data: item.data
    };
  }

  // API 호출
  private async apiCall(method: string, url: string, data?: any): Promise<any> {
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    if (!response.ok) {
      throw new Error(`API 호출 실패: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // 실시간 동기화: 오프라인 데이터 변경 이벤트 브로드캐스트
  private broadcastOfflineDataChange(action: string, data?: any): void {
    const broadcastData = {
      action,
      data,
      timestamp: new Date().toISOString()
    };
    
    // localStorage를 통한 다른 탭에 브로드캐스트
    localStorage.setItem('offline-storage-broadcast', JSON.stringify(broadcastData));
    localStorage.removeItem('offline-storage-broadcast'); // 즉시 제거하여 중복 방지
    
    // WebSocket을 통한 실시간 브로드캐스트
    if (typeof window !== 'undefined' && (window as any).notificationWebSocket) {
      try {
        (window as any).notificationWebSocket.send(JSON.stringify({
          type: 'offline_storage_update',
          ...broadcastData
        }));
      } catch (error) {
        console.warn('오프라인 스토리지 WebSocket 브로드캐스트 실패:', error);
      }
    }
  }

  // 오프라인 데이터 변경 구독
  subscribeToOfflineDataChanges(callback: (action: string, data?: any) => void): () => void {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'offline-storage-broadcast') {
        try {
          const broadcastData = JSON.parse(e.newValue || '{}');
          callback(broadcastData.action, broadcastData.data);
        } catch (error) {
          console.error('오프라인 스토리지 브로드캐스트 파싱 오류:', error);
        }
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }

  // 저장소 정리 (만료된 데이터 제거)
  cleanup(): void {
    try {
      // 만료된 캐시 제거
      this.getCachedData(); // 내부적으로 만료된 캐시 제거
      
      // 오래된 오프라인 데이터 제거 (7일 이상)
      const offlineData = this.getOfflineData();
      const now = new Date();
      const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      
      const validOfflineData = offlineData.filter((item: OfflineData) => {
        const itemTime = new Date(item.timestamp);
        return itemTime > sevenDaysAgo;
      });
      
      if (validOfflineData.length !== offlineData.length) {
        localStorage.setItem(this.OFFLINE_DATA_KEY, JSON.stringify(validOfflineData));
        console.log(`오래된 오프라인 데이터 ${offlineData.length - validOfflineData.length}개 제거됨`);
      }
    } catch (error) {
      console.error('저장소 정리 실패:', error);
    }
  }

  // 저장소 상태 조회
  getStorageStatus(): {
    offlineDataCount: number;
    cachedDataCount: number;
    totalSize: number;
  } {
    try {
      const offlineData = this.getOfflineData();
      const cachedData = this.getCachedData();
      
      const offlineSize = JSON.stringify(offlineData).length;
      const cachedSize = JSON.stringify(cachedData).length;
      const totalSize = offlineSize + cachedSize;
      
      return {
        offlineDataCount: offlineData.length,
        cachedDataCount: Array.isArray(cachedData) ? cachedData.length : 0,
        totalSize
      };
    } catch (error) {
      console.error('저장소 상태 조회 실패:', error);
      return {
        offlineDataCount: 0,
        cachedDataCount: 0,
        totalSize: 0
      };
    }
  }
}

export const offlineStorage = new OfflineStorage();

// 네트워크 상태 감지
export const isOnline = (): boolean => {
  return navigator.onLine;
};

// 네트워크 상태 변경 이벤트 리스너
export const setupNetworkListener = (onOnline: () => void, onOffline: () => void): void => {
  window.addEventListener('online', onOnline);
  window.addEventListener('offline', onOffline);
};

// 정기적인 동기화 설정
export const setupPeriodicSync = (intervalMs: number = 30000): NodeJS.Timeout => {
  return setInterval(async () => {
    if (isOnline()) {
      await offlineStorage.syncOfflineData();
    }
  }, intervalMs);
}; 