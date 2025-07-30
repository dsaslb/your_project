/**
 * 오프라인 동기화 시스템
 * 네트워크 연결 상태에 관계없이 데이터 동기화 및 오프라인 작업 지원
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-netinfo/netinfo';
import { Platform } from 'react-native';
import SQLite from 'react-native-sqlite-storage';
import { v4 as uuidv4 } from 'uuid';

// SQLite 설정
SQLite.DEBUG(true);
SQLite.enablePromise(true);

export interface SyncItem {
  id: string;
  type: 'CREATE' | 'UPDATE' | 'DELETE';
  entity: string;
  data: any;
  timestamp: number;
  retryCount: number;
  maxRetries: number;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  metadata?: any;
}

export interface SyncConfig {
  maxRetries: number;
  retryDelay: number;
  batchSize: number;
  syncInterval: number;
  conflictResolution: 'SERVER_WINS' | 'CLIENT_WINS' | 'LAST_WRITE_WINS';
}

export interface SyncStatus {
  isOnline: boolean;
  isSyncing: boolean;
  lastSyncTime: number;
  pendingItems: number;
  failedItems: number;
  syncProgress: number;
}

export class OfflineSyncService {
  private db: SQLite.SQLiteDatabase | null = null;
  private syncQueue: SyncItem[] = [];
  private isSyncing = false;
  private syncInterval: NodeJS.Timeout | null = null;
  private config: SyncConfig;
  private status: SyncStatus;
  private listeners: ((status: SyncStatus) => void)[] = [];

  constructor(config: Partial<SyncConfig> = {}) {
    this.config = {
      maxRetries: 3,
      retryDelay: 5000,
      batchSize: 50,
      syncInterval: 30000,
      conflictResolution: 'LAST_WRITE_WINS',
      ...config,
    };

    this.status = {
      isOnline: true,
      isSyncing: false,
      lastSyncTime: 0,
      pendingItems: 0,
      failedItems: 0,
      syncProgress: 0,
    };

    this.initializeDatabase();
    this.setupNetworkListener();
    this.startSyncInterval();
  }

  /**
   * 데이터베이스 초기화
   */
  private async initializeDatabase(): Promise<void> {
    try {
      this.db = await SQLite.openDatabase({
        name: 'OfflineSync.db',
        location: 'default',
      });

      await this.createTables();
      console.log('오프라인 동기화 데이터베이스 초기화 완료');
    } catch (error) {
      console.error('데이터베이스 초기화 오류:', error);
      throw error;
    }
  }

  /**
   * 테이블 생성
   */
  private async createTables(): Promise<void> {
    if (!this.db) return;

    const createSyncQueueTable = `
      CREATE TABLE IF NOT EXISTS sync_queue (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        entity TEXT NOT NULL,
        data TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        retry_count INTEGER DEFAULT 0,
        max_retries INTEGER DEFAULT 3,
        priority TEXT DEFAULT 'MEDIUM',
        metadata TEXT,
        created_at INTEGER DEFAULT (strftime('%s', 'now') * 1000)
      )
    `;

    const createLocalDataTable = `
      CREATE TABLE IF NOT EXISTS local_data (
        id TEXT PRIMARY KEY,
        entity TEXT NOT NULL,
        data TEXT NOT NULL,
        version INTEGER DEFAULT 1,
        last_modified INTEGER DEFAULT (strftime('%s', 'now') * 1000),
        is_synced INTEGER DEFAULT 0
      )
    `;

    const createSyncStatusTable = `
      CREATE TABLE IF NOT EXISTS sync_status (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at INTEGER DEFAULT (strftime('%s', 'now') * 1000)
      )
    `;

    try {
      await this.db.executeSql(createSyncQueueTable);
      await this.db.executeSql(createLocalDataTable);
      await this.db.executeSql(createSyncStatusTable);
      console.log('오프라인 동기화 테이블 생성 완료');
    } catch (error) {
      console.error('테이블 생성 오류:', error);
      throw error;
    }
  }

  /**
   * 네트워크 상태 리스너 설정
   */
  private setupNetworkListener(): void {
    NetInfo.addEventListener((state) => {
      const wasOnline = this.status.isOnline;
      this.status.isOnline = state.isConnected ?? false;

      if (!wasOnline && this.status.isOnline) {
        console.log('네트워크 연결 복구됨 - 동기화 시작');
        this.syncPendingItems();
      }

      this.notifyListeners();
    });
  }

  /**
   * 동기화 인터벌 시작
   */
  private startSyncInterval(): void {
    this.syncInterval = setInterval(() => {
      if (this.status.isOnline && !this.isSyncing) {
        this.syncPendingItems();
      }
    }, this.config.syncInterval);
  }

  /**
   * 동기화 큐에 아이템 추가
   */
  async addToSyncQueue(
    type: SyncItem['type'],
    entity: string,
    data: any,
    priority: SyncItem['priority'] = 'MEDIUM',
    metadata?: any
  ): Promise<string> {
    const syncItem: SyncItem = {
      id: uuidv4(),
      type,
      entity,
      data,
      timestamp: Date.now(),
      retryCount: 0,
      maxRetries: this.config.maxRetries,
      priority,
      metadata,
    };

    try {
      await this.saveSyncItem(syncItem);
      this.syncQueue.push(syncItem);
      this.updateStatus();
      console.log(`동기화 큐에 추가됨: ${entity} ${type}`);
      return syncItem.id;
    } catch (error) {
      console.error('동기화 큐 추가 오류:', error);
      throw error;
    }
  }

  /**
   * 동기화 아이템을 데이터베이스에 저장
   */
  private async saveSyncItem(item: SyncItem): Promise<void> {
    if (!this.db) return;

    const query = `
      INSERT INTO sync_queue (id, type, entity, data, timestamp, retry_count, max_retries, priority, metadata)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;

    try {
      await this.db.executeSql(query, [
        item.id,
        item.type,
        item.entity,
        JSON.stringify(item.data),
        item.timestamp,
        item.retryCount,
        item.maxRetries,
        item.priority,
        item.metadata ? JSON.stringify(item.metadata) : null,
      ]);
    } catch (error) {
      console.error('동기화 아이템 저장 오류:', error);
      throw error;
    }
  }

  /**
   * 로컬 데이터 저장
   */
  async saveLocalData(entity: string, data: any): Promise<void> {
    if (!this.db) return;

    const query = `
      INSERT OR REPLACE INTO local_data (id, entity, data, version, last_modified, is_synced)
      VALUES (?, ?, ?, ?, ?, ?)
    `;

    try {
      const id = data.id || uuidv4();
      const version = data.version || 1;
      const isSynced = this.status.isOnline ? 1 : 0;

      await this.db.executeSql(query, [
        id,
        entity,
        JSON.stringify(data),
        version,
        Date.now(),
        isSynced,
      ]);

      console.log(`로컬 데이터 저장됨: ${entity} ${id}`);
    } catch (error) {
      console.error('로컬 데이터 저장 오류:', error);
      throw error;
    }
  }

  /**
   * 로컬 데이터 조회
   */
  async getLocalData(entity: string, id?: string): Promise<any[]> {
    if (!this.db) return [];

    let query = 'SELECT * FROM local_data WHERE entity = ?';
    const params = [entity];

    if (id) {
      query += ' AND id = ?';
      params.push(id);
    }

    query += ' ORDER BY last_modified DESC';

    try {
      const [results] = await this.db.executeSql(query, params);
      const data: any[] = [];

      for (let i = 0; i < results.rows.length; i++) {
        const row = results.rows.item(i);
        data.push({
          ...JSON.parse(row.data),
          _localVersion: row.version,
          _lastModified: row.last_modified,
          _isSynced: Boolean(row.is_synced),
        });
      }

      return data;
    } catch (error) {
      console.error('로컬 데이터 조회 오류:', error);
      return [];
    }
  }

  /**
   * 대기 중인 동기화 아이템 조회
   */
  private async getPendingSyncItems(): Promise<SyncItem[]> {
    if (!this.db) return [];

    const query = `
      SELECT * FROM sync_queue 
      WHERE retry_count < max_retries 
      ORDER BY 
        CASE priority 
          WHEN 'HIGH' THEN 1 
          WHEN 'MEDIUM' THEN 2 
          WHEN 'LOW' THEN 3 
        END,
        timestamp ASC
      LIMIT ?
    `;

    try {
      const [results] = await this.db.executeSql(query, [this.config.batchSize]);
      const items: SyncItem[] = [];

      for (let i = 0; i < results.rows.length; i++) {
        const row = results.rows.item(i);
        items.push({
          id: row.id,
          type: row.type,
          entity: row.entity,
          data: JSON.parse(row.data),
          timestamp: row.timestamp,
          retryCount: row.retry_count,
          maxRetries: row.max_retries,
          priority: row.priority,
          metadata: row.metadata ? JSON.parse(row.metadata) : undefined,
        });
      }

      return items;
    } catch (error) {
      console.error('대기 중인 동기화 아이템 조회 오류:', error);
      return [];
    }
  }

  /**
   * 대기 중인 아이템 동기화
   */
  async syncPendingItems(): Promise<void> {
    if (this.isSyncing || !this.status.isOnline) return;

    this.isSyncing = true;
    this.status.isSyncing = true;
    this.notifyListeners();

    try {
      const pendingItems = await this.getPendingSyncItems();
      if (pendingItems.length === 0) {
        console.log('동기화할 아이템이 없습니다');
        return;
      }

      console.log(`${pendingItems.length}개의 아이템 동기화 시작`);

      let successCount = 0;
      let failCount = 0;

      for (let i = 0; i < pendingItems.length; i++) {
        const item = pendingItems[i];
        this.status.syncProgress = ((i + 1) / pendingItems.length) * 100;
        this.notifyListeners();

        try {
          await this.syncItem(item);
          await this.removeSyncItem(item.id);
          successCount++;
        } catch (error) {
          console.error(`동기화 실패: ${item.entity} ${item.type}`, error);
          await this.incrementRetryCount(item.id);
          failCount++;
        }

        // 배치 간 지연
        if (i < pendingItems.length - 1) {
          await this.delay(100);
        }
      }

      this.status.lastSyncTime = Date.now();
      this.status.failedItems = failCount;
      console.log(`동기화 완료: 성공 ${successCount}, 실패 ${failCount}`);

    } catch (error) {
      console.error('동기화 오류:', error);
    } finally {
      this.isSyncing = false;
      this.status.isSyncing = false;
      this.status.syncProgress = 0;
      this.updateStatus();
      this.notifyListeners();
    }
  }

  /**
   * 개별 아이템 동기화
   */
  private async syncItem(item: SyncItem): Promise<void> {
    const apiEndpoint = this.getApiEndpoint(item.entity);
    const headers = await this.getAuthHeaders();

    let response: Response;

    switch (item.type) {
      case 'CREATE':
        response = await fetch(apiEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...headers,
          },
          body: JSON.stringify(item.data),
        });
        break;

      case 'UPDATE':
        response = await fetch(`${apiEndpoint}/${item.data.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            ...headers,
          },
          body: JSON.stringify(item.data),
        });
        break;

      case 'DELETE':
        response = await fetch(`${apiEndpoint}/${item.data.id}`, {
          method: 'DELETE',
          headers,
        });
        break;

      default:
        throw new Error(`지원하지 않는 동기화 타입: ${item.type}`);
    }

    if (!response.ok) {
      throw new Error(`API 요청 실패: ${response.status} ${response.statusText}`);
    }

    // 응답 데이터로 로컬 데이터 업데이트
    if (item.type !== 'DELETE') {
      const responseData = await response.json();
      await this.saveLocalData(item.entity, responseData);
    }
  }

  /**
   * API 엔드포인트 가져오기
   */
  private getApiEndpoint(entity: string): string {
    const baseUrl = 'https://api.yourprogram.com';
    const endpoints: { [key: string]: string } = {
      users: `${baseUrl}/api/users`,
      products: `${baseUrl}/api/products`,
      orders: `${baseUrl}/api/orders`,
      notifications: `${baseUrl}/api/notifications`,
      settings: `${baseUrl}/api/settings`,
    };

    return endpoints[entity] || `${baseUrl}/api/${entity}`;
  }

  /**
   * 인증 헤더 가져오기
   */
  private async getAuthHeaders(): Promise<{ [key: string]: string }> {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      return token ? { Authorization: `Bearer ${token}` } : {};
    } catch (error) {
      console.error('인증 헤더 가져오기 오류:', error);
      return {};
    }
  }

  /**
   * 동기화 아이템 제거
   */
  private async removeSyncItem(id: string): Promise<void> {
    if (!this.db) return;

    const query = 'DELETE FROM sync_queue WHERE id = ?';

    try {
      await this.db.executeSql(query, [id]);
      this.syncQueue = this.syncQueue.filter(item => item.id !== id);
    } catch (error) {
      console.error('동기화 아이템 제거 오류:', error);
    }
  }

  /**
   * 재시도 횟수 증가
   */
  private async incrementRetryCount(id: string): Promise<void> {
    if (!this.db) return;

    const query = 'UPDATE sync_queue SET retry_count = retry_count + 1 WHERE id = ?';

    try {
      await this.db.executeSql(query, [id]);
    } catch (error) {
      console.error('재시도 횟수 증가 오류:', error);
    }
  }

  /**
   * 상태 업데이트
   */
  private updateStatus(): void {
    this.status.pendingItems = this.syncQueue.length;
    this.notifyListeners();
  }

  /**
   * 상태 리스너 등록
   */
  addStatusListener(listener: (status: SyncStatus) => void): () => void {
    this.listeners.push(listener);
    listener(this.status);

    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  /**
   * 리스너들에게 상태 알림
   */
  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.status));
  }

  /**
   * 지연 함수
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 동기화 상태 가져오기
   */
  getStatus(): SyncStatus {
    return { ...this.status };
  }

  /**
   * 강제 동기화
   */
  async forceSync(): Promise<void> {
    console.log('강제 동기화 시작');
    await this.syncPendingItems();
  }

  /**
   * 동기화 큐 초기화
   */
  async clearSyncQueue(): Promise<void> {
    if (!this.db) return;

    try {
      await this.db.executeSql('DELETE FROM sync_queue');
      this.syncQueue = [];
      this.updateStatus();
      console.log('동기화 큐 초기화 완료');
    } catch (error) {
      console.error('동기화 큐 초기화 오류:', error);
    }
  }

  /**
   * 로컬 데이터 초기화
   */
  async clearLocalData(entity?: string): Promise<void> {
    if (!this.db) return;

    try {
      if (entity) {
        await this.db.executeSql('DELETE FROM local_data WHERE entity = ?', [entity]);
      } else {
        await this.db.executeSql('DELETE FROM local_data');
      }
      console.log('로컬 데이터 초기화 완료');
    } catch (error) {
      console.error('로컬 데이터 초기화 오류:', error);
    }
  }

  /**
   * 서비스 정리
   */
  destroy(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }
    this.listeners = [];
    console.log('오프라인 동기화 서비스 정리 완료');
  }
}

// 싱글톤 인스턴스
export const offlineSyncService = new OfflineSyncService();

// 사용 예시
export const useOfflineSync = () => {
  return {
    addToSyncQueue: offlineSyncService.addToSyncQueue.bind(offlineSyncService),
    saveLocalData: offlineSyncService.saveLocalData.bind(offlineSyncService),
    getLocalData: offlineSyncService.getLocalData.bind(offlineSyncService),
    getStatus: offlineSyncService.getStatus.bind(offlineSyncService),
    forceSync: offlineSyncService.forceSync.bind(offlineSyncService),
    addStatusListener: offlineSyncService.addStatusListener.bind(offlineSyncService),
  };
}; 