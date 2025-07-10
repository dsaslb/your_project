// IndexedDB를 활용한 오프라인 임시저장 유틸리티

interface OfflineData {
  id: string;
  table: string;
  action: 'create' | 'update' | 'delete';
  data: any;
  timestamp: string;
  synced: boolean;
}

class OfflineStorage {
  private dbName = 'restaurant-offline-db';
  private version = 1;
  private db: IDBDatabase | null = null;

  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        
        // 오프라인 데이터 저장소
        if (!db.objectStoreNames.contains('offlineData')) {
          const store = db.createObjectStore('offlineData', { keyPath: 'id' });
          store.createIndex('table', 'table', { unique: false });
          store.createIndex('synced', 'synced', { unique: false });
          store.createIndex('timestamp', 'timestamp', { unique: false });
        }

        // 캐시된 데이터 저장소
        if (!db.objectStoreNames.contains('cachedData')) {
          const store = db.createObjectStore('cachedData', { keyPath: 'key' });
          store.createIndex('table', 'table', { unique: false });
          store.createIndex('timestamp', 'timestamp', { unique: false });
        }
      };
    });
  }

  // 오프라인 데이터 저장
  async saveOfflineData(table: string, action: 'create' | 'update' | 'delete', data: any): Promise<void> {
    if (!this.db) await this.init();

    const offlineData: OfflineData = {
      id: `${table}_${Date.now()}_${Math.random()}`,
      table,
      action,
      data,
      timestamp: new Date().toISOString(),
      synced: false,
    };

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['offlineData'], 'readwrite');
      const store = transaction.objectStore('offlineData');
      const request = store.add(offlineData);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  // 동기화되지 않은 오프라인 데이터 조회
  async getUnsyncedData(): Promise<OfflineData[]> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['offlineData'], 'readonly');
      const store = transaction.objectStore('offlineData');
      const index = store.index('synced');
      const request = index.getAll(IDBKeyRange.only(false));

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  // 오프라인 데이터를 동기화됨으로 표시
  async markAsSynced(id: string): Promise<void> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['offlineData'], 'readwrite');
      const store = transaction.objectStore('offlineData');
      const getRequest = store.get(id);

      getRequest.onsuccess = () => {
        const data = getRequest.result;
        if (data) {
          data.synced = true;
          const putRequest = store.put(data);
          putRequest.onsuccess = () => resolve();
          putRequest.onerror = () => reject(putRequest.error);
        } else {
          resolve();
        }
      };
      getRequest.onerror = () => reject(getRequest.error);
    });
  }

  // 캐시된 데이터 저장
  async saveCachedData(key: string, table: string, data: any): Promise<void> {
    if (!this.db) await this.init();

    const cachedData = {
      key,
      table,
      data,
      timestamp: new Date().toISOString(),
    };

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['cachedData'], 'readwrite');
      const store = transaction.objectStore('cachedData');
      const request = store.put(cachedData);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  // 캐시된 데이터 조회
  async getCachedData(key: string): Promise<any | null> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['cachedData'], 'readonly');
      const store = transaction.objectStore('cachedData');
      const request = store.get(key);

      request.onsuccess = () => resolve(request.result?.data || null);
      request.onerror = () => reject(request.error);
    });
  }

  // 테이블별 캐시된 데이터 조회
  async getCachedDataByTable(table: string): Promise<any[]> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['cachedData'], 'readonly');
      const store = transaction.objectStore('cachedData');
      const index = store.index('table');
      const request = index.getAll(table);

      request.onsuccess = () => resolve(request.result.map(item => item.data));
      request.onerror = () => reject(request.error);
    });
  }

  // 오래된 캐시 데이터 정리 (7일 이상)
  async cleanupOldCache(): Promise<void> {
    if (!this.db) await this.init();

    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['cachedData', 'offlineData'], 'readwrite');
      const cacheStore = transaction.objectStore('cachedData');
      const offlineStore = transaction.objectStore('offlineData');
      
      // 캐시된 데이터 정리
      const cacheRequest = cacheStore.openCursor();
      cacheRequest.onsuccess = () => {
        const cursor = cacheRequest.result;
        if (cursor) {
          const timestamp = new Date(cursor.value.timestamp);
          if (timestamp < sevenDaysAgo) {
            cursor.delete();
          }
          cursor.continue();
        }
      };

      // 동기화된 오프라인 데이터 정리
      const offlineRequest = offlineStore.openCursor();
      offlineRequest.onsuccess = () => {
        const cursor = offlineRequest.result;
        if (cursor) {
          if (cursor.value.synced) {
            cursor.delete();
          }
          cursor.continue();
        }
      };

      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    });
  }

  // 온라인 상태에서 서버와 동기화
  async syncWithServer(): Promise<void> {
    const unsyncedData = await this.getUnsyncedData();
    
    for (const item of unsyncedData) {
      try {
        // 실제 API 호출 (서버 상태에 따라 조정)
        const response = await fetch(`/api/${item.table}`, {
          method: item.action === 'delete' ? 'DELETE' : 
                  item.action === 'create' ? 'POST' : 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: item.action !== 'delete' ? JSON.stringify(item.data) : undefined,
        });

        if (response.ok) {
          await this.markAsSynced(item.id);
        }
      } catch (error) {
        console.error(`동기화 실패 (${item.table}):`, error);
      }
    }
  }
}

// 싱글톤 인스턴스
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
      await offlineStorage.syncWithServer();
    }
  }, intervalMs);
}; 