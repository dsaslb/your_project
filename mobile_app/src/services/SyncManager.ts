import { networkService } from './NetworkService';
import { localStorageService } from './LocalStorageService';
import { offlineQueueService } from './OfflineQueueService';
import { batchSyncService } from './BatchSyncService';
import { mobileAPI } from '../api/client';

export interface SyncStatus {
  isOnline: boolean;
  isSyncing: boolean;
  lastSyncTime: Date | null;
  pendingActions: number;
  failedActions: number;
  syncProgress: number; // 0-100
  batchQueueSize: number;
  batchSyncStatus: 'idle' | 'syncing' | 'completed' | 'error';
}

export class SyncManager {
  private static instance: SyncManager;
  private isSyncing = false;
  private lastSyncTime: Date | null = null;
  private listeners: Set<(status: SyncStatus) => void> = new Set();
  private syncInterval: NodeJS.Timeout | null = null;

  private constructor() {
    this.initialize();
  }

  public static getInstance(): SyncManager {
    if (!SyncManager.instance) {
      SyncManager.instance = new SyncManager();
    }
    return SyncManager.instance;
  }

  private initialize(): void {
    // 네트워크 상태 변경 리스너 등록
    networkService.addListener((networkState) => {
      if (networkState.isConnected && networkState.isInternetReachable) {
        this.startAutoSync();
      } else {
        this.stopAutoSync();
      }
    });

    // 주기적 동기화 (5분마다)
    this.syncInterval = setInterval(() => {
      if (networkService.isOnline() && !this.isSyncing) {
        this.performSync();
      }
    }, 5 * 60 * 1000); // 5분
  }

  /**
   * 자동 동기화 시작
   */
  private startAutoSync(): void {
    console.log('네트워크 연결됨 - 자동 동기화 시작');
    this.performSync();
  }

  /**
   * 자동 동기화 중지
   */
  private stopAutoSync(): void {
    console.log('네트워크 연결 끊김 - 자동 동기화 중지');
  }

  /**
   * 수동 동기화 실행
   */
  async performSync(): Promise<SyncStatus> {
    if (this.isSyncing || !networkService.isOnline()) {
      return this.getCurrentStatus();
    }

    this.isSyncing = true;
    this.notifyListeners();

    try {
      console.log('동기화 시작...');
      
      // 1. 배치 동기화 (새로운 방식)
      await this.performBatchSync();
      
      // 2. 기존 오프라인 큐 처리 (호환성)
      await this.syncOfflineQueue();
      
      // 3. 로컬 데이터 동기화
      await this.syncLocalData();
      
      // 4. 서버 데이터 가져오기
      await this.syncServerData();
      
      // 5. 정리 작업
      await this.cleanup();
      
      this.lastSyncTime = new Date();
      console.log('동기화 완료');
      
    } catch (error) {
      console.error('동기화 실패:', error);
    } finally {
      this.isSyncing = false;
      this.notifyListeners();
    }

    return this.getCurrentStatus();
  }

  /**
   * 배치 동기화 실행
   */
  private async performBatchSync(): Promise<void> {
    try {
      const result = await batchSyncService.performSync((progress) => {
        // 진행률 업데이트를 리스너들에게 전달
        this.notifyListeners();
      });
      
      console.log(`배치 동기화 결과: ${result.delivered}개 전송, ${result.failed}개 실패`);
      
      if (result.errors.length > 0) {
        console.warn('배치 동기화 에러:', result.errors);
      }
      
    } catch (error) {
      console.error('배치 동기화 실패:', error);
    }
  }

  /**
   * 오프라인 큐 동기화
   */
  private async syncOfflineQueue(): Promise<void> {
    const queue = offlineQueueService.getQueue();
    if (queue.length === 0) return;

    console.log(`오프라인 큐 동기화: ${queue.length}개 액션`);
    
    // 큐 서비스가 자동으로 처리하도록 함
    // 여기서는 상태만 확인
  }

  /**
   * 로컬 데이터 동기화
   */
  private async syncLocalData(): Promise<void> {
    const unsyncedData = await localStorageService.getUnsyncedData();
    
    let totalItems = unsyncedData.attendance.length + 
                    unsyncedData.inventory.length + 
                    unsyncedData.orders.length;
    
    if (totalItems === 0) return;

    console.log(`로컬 데이터 동기화: ${totalItems}개 항목`);
    
    let syncedItems = 0;

    // 출퇴근 기록 동기화
    for (const attendance of unsyncedData.attendance) {
      try {
        const result = await mobileAPI.clockIn({
          lat: attendance.lat,
          lng: attendance.lng,
        });
        await localStorageService.markAsSynced('local_attendance', attendance.id, result.id);
        syncedItems++;
        this.updateSyncProgress(syncedItems, totalItems);
      } catch (error) {
        console.error('출퇴근 기록 동기화 실패:', error);
      }
    }

    // 재고 조사 동기화
    for (const inventory of unsyncedData.inventory) {
      try {
        const result = await mobileAPI.checkInventory({
          barcode: inventory.barcode,
          qty: inventory.quantity,
          photo_url: inventory.photo_url,
        });
        await localStorageService.markAsSynced('local_inventory_checks', inventory.id, result.id);
        syncedItems++;
        this.updateSyncProgress(syncedItems, totalItems);
      } catch (error) {
        console.error('재고 조사 동기화 실패:', error);
      }
    }

    // 발주 동기화
    for (const order of unsyncedData.orders) {
      try {
        const result = await mobileAPI.createPurchaseOrder({
          branch_id: order.branch_id,
          items: order.items,
        });
        await localStorageService.markAsSynced('local_purchase_orders', order.id, result.order_id);
        syncedItems++;
        this.updateSyncProgress(syncedItems, totalItems);
      } catch (error) {
        console.error('발주 동기화 실패:', error);
      }
    }
  }

  /**
   * 서버 데이터 동기화 (최신 데이터 가져오기)
   */
  private async syncServerData(): Promise<void> {
    try {
      // 대시보드 데이터 새로고침
      await mobileAPI.getDashboard();
      
      // 스케줄 데이터 새로고침
      await mobileAPI.getSchedules();
      
      console.log('서버 데이터 동기화 완료');
    } catch (error) {
      console.error('서버 데이터 동기화 실패:', error);
    }
  }

  /**
   * 정리 작업
   */
  private async cleanup(): Promise<void> {
    try {
      await offlineQueueService.cleanup();
      await localStorageService.cleanup();
      console.log('정리 작업 완료');
    } catch (error) {
      console.error('정리 작업 실패:', error);
    }
  }

  /**
   * 동기화 진행률 업데이트
   */
  private updateSyncProgress(current: number, total: number): void {
    const progress = Math.round((current / total) * 100);
    // 진행률 업데이트 로직 (필요시 구현)
  }

  /**
   * 현재 동기화 상태 반환
   */
  getCurrentStatus(): SyncStatus {
    const queue = offlineQueueService.getQueue();
    const pendingActions = queue.filter(item => item.action.status === 'pending').length;
    const failedActions = queue.filter(item => item.action.status === 'failed').length;
    
    const batchQueueStatus = batchSyncService.getQueueStatus();

    return {
      isOnline: networkService.isOnline(),
      isSyncing: this.isSyncing,
      lastSyncTime: this.lastSyncTime,
      pendingActions,
      failedActions,
      syncProgress: this.isSyncing ? 50 : 100, // 간단한 진행률
      batchQueueSize: batchQueueStatus.total,
      batchSyncStatus: this.isSyncing ? 'syncing' : 'idle'
    };
  }

  /**
   * 동기화 상태 리스너 등록
   */
  addListener(listener: (status: SyncStatus) => void): () => void {
    this.listeners.add(listener);
    
    // 즉시 현재 상태 전달
    listener(this.getCurrentStatus());
    
    // 리스너 제거 함수 반환
    return () => {
      this.listeners.delete(listener);
    };
  }

  /**
   * 리스너들에게 상태 알림
   */
  private notifyListeners(): void {
    const status = this.getCurrentStatus();
    this.listeners.forEach(listener => {
      try {
        listener(status);
      } catch (error) {
        console.error('동기화 상태 리스너 오류:', error);
      }
    });
  }

  /**
   * 강제 동기화 (사용자가 수동으로 실행)
   */
  async forceSync(): Promise<SyncStatus> {
    console.log('강제 동기화 실행');
    return await this.performSync();
  }

  /**
   * 동기화 일시 중지
   */
  pauseSync(): void {
    this.stopAutoSync();
  }

  /**
   * 동기화 재개
   */
  resumeSync(): void {
    if (networkService.isOnline()) {
      this.startAutoSync();
    }
  }

  /**
   * 서비스 종료
   */
  destroy(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
    this.listeners.clear();
  }
}

// 싱글톤 인스턴스 내보내기
export const syncManager = SyncManager.getInstance();
