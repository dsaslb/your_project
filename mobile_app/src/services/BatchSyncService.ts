"""
배치 동기화 서비스
- 기존 OfflineQueueService를 개선하여 배치 업로드 지원
- 멱등성 키 관리
- 우선순위 기반 처리
"""
import AsyncStorage from '@react-native-async-storage/async-storage';
import { v4 as uuidv4 } from 'uuid';
import { mobileAPI } from '../api/client';
import { networkService } from './NetworkService';
import { Platform } from 'react-native';

export interface BatchItem {
  type: 'attendance' | 'po' | 'inventory';
  idem: string;
  payload: any;
  priority: number;
  createdAt: Date;
  retryCount: number;
  maxRetries: number;
}

export interface BatchSyncResult {
  success: boolean;
  processed: number;
  delivered: number;
  failed: number;
  duplicates: number;
  errors: string[];
}

export interface SyncProgress {
  current: number;
  total: number;
  percentage: number;
  status: 'idle' | 'syncing' | 'completed' | 'error';
}

export class BatchSyncService {
  private static instance: BatchSyncService;
  private queue: BatchItem[] = [];
  private isProcessing = false;
  private listeners: Set<(progress: SyncProgress) => void> = new Set();
  private processingInterval: NodeJS.Timeout | null = null;
  private readonly STORAGE_KEY = 'offline_batch_queue';
  private readonly BATCH_SIZE = 50; // 한 번에 처리할 최대 아이템 수
  private readonly SYNC_INTERVAL = 30000; // 30초마다 동기화 시도

  private constructor() {
    this.initialize();
  }

  public static getInstance(): BatchSyncService {
    if (!BatchSyncService.instance) {
      BatchSyncService.instance = new BatchSyncService();
    }
    return BatchSyncService.instance;
  }

  private async initialize(): Promise<void> {
    // 로컬 스토리지에서 대기 중인 아이템들 로드
    await this.loadQueueFromStorage();
    
    // 네트워크 상태 변경 리스너 등록
    networkService.addListener((networkState) => {
      if (networkState.isConnected && networkState.isInternetReachable) {
        this.startPeriodicSync();
      } else {
        this.stopPeriodicSync();
      }
    });

    // 주기적 동기화 시작
    this.startPeriodicSync();
  }

  /**
   * 로컬 스토리지에서 큐 로드
   */
  private async loadQueueFromStorage(): Promise<void> {
    try {
      const stored = await AsyncStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        const items = JSON.parse(stored);
        this.queue = items.map((item: any) => ({
          ...item,
          createdAt: new Date(item.createdAt)
        }));
        
        // 우선순위 순으로 정렬
        this.queue.sort((a, b) => b.priority - a.priority);
        
        console.log(`배치 큐 로드됨: ${this.queue.length}개 아이템`);
      }
    } catch (error) {
      console.error('큐 로드 실패:', error);
    }
  }

  /**
   * 큐를 로컬 스토리지에 저장
   */
  private async saveQueueToStorage(): Promise<void> {
    try {
      await AsyncStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.queue));
    } catch (error) {
      console.error('큐 저장 실패:', error);
    }
  }

  /**
   * 아이템을 큐에 추가
   */
  async enqueue(
    type: BatchItem['type'],
    payload: any,
    priority?: number
  ): Promise<string> {
    const idem = uuidv4();
    const item: BatchItem = {
      type,
      idem,
      payload,
      priority: priority || this.getDefaultPriority(type),
      createdAt: new Date(),
      retryCount: 0,
      maxRetries: 3
    };

    this.queue.push(item);
    this.queue.sort((a, b) => b.priority - a.priority);
    
    await this.saveQueueToStorage();
    
    console.log(`아이템 큐에 추가됨: ${type} (우선순위: ${item.priority})`);
    
    // 온라인 상태라면 즉시 동기화 시도
    if (networkService.isOnline()) {
      this.performSync();
    }

    return idem;
  }

  /**
   * 타입별 기본 우선순위 반환
   */
  private getDefaultPriority(type: BatchItem['type']): number {
    const priorities = {
      'attendance': 10, // 출퇴근: 최고 우선순위
      'po': 8,          // 발주: 높은 우선순위
      'inventory': 5    // 재고: 중간 우선순위
    };
    return priorities[type] || 1;
  }

  /**
   * 배치 동기화 실행
   */
  async performSync(progressCallback?: (progress: SyncProgress) => void): Promise<BatchSyncResult> {
    if (this.isProcessing || !networkService.isOnline() || this.queue.length === 0) {
      return {
        success: true,
        processed: 0,
        delivered: 0,
        failed: 0,
        duplicates: 0,
        errors: []
      };
    }

    this.isProcessing = true;
    const startTime = Date.now();
    
    try {
      // 진행률 콜백 등록
      if (progressCallback) {
        this.listeners.add(progressCallback);
      }

      // 배치 단위로 처리
      const batches = this.createBatches();
      let totalProcessed = 0;
      let totalDelivered = 0;
      let totalFailed = 0;
      let totalDuplicates = 0;
      const errors: string[] = [];

      for (let i = 0; i < batches.length; i++) {
        const batch = batches[i];
        
        try {
          const result = await this.processBatch(batch);
          
          totalProcessed += result.processed;
          totalDelivered += result.delivered;
          totalFailed += result.failed;
          totalDuplicates += result.duplicates;
          errors.push(...result.errors);

          // 진행률 업데이트
          const progress: SyncProgress = {
            current: totalProcessed,
            total: this.queue.length,
            percentage: Math.round((totalProcessed / this.queue.length) * 100),
            status: i === batches.length - 1 ? 'completed' : 'syncing'
          };
          
          this.notifyProgress(progress);

        } catch (error) {
          console.error(`배치 ${i + 1} 처리 실패:`, error);
          errors.push(`배치 ${i + 1}: ${error.message}`);
        }
      }

      // 성공한 아이템들 큐에서 제거
      await this.cleanupProcessedItems();

      const processingTime = Date.now() - startTime;
      console.log(`배치 동기화 완료: ${totalProcessed}개 처리, ${processingTime}ms 소요`);

      return {
        success: errors.length === 0,
        processed: totalProcessed,
        delivered: totalDelivered,
        failed: totalFailed,
        duplicates: totalDuplicates,
        errors
      };

    } finally {
      this.isProcessing = false;
      
      // 진행률 콜백 제거
      if (progressCallback) {
        this.listeners.delete(progressCallback);
      }
    }
  }

  /**
   * 큐를 배치 단위로 분할
   */
  private createBatches(): BatchItem[][] {
    const batches: BatchItem[][] = [];
    
    for (let i = 0; i < this.queue.length; i += this.BATCH_SIZE) {
      batches.push(this.queue.slice(i, i + this.BATCH_SIZE));
    }
    
    return batches;
  }

  /**
   * 개별 배치 처리
   */
  private async processBatch(batch: BatchItem[]): Promise<BatchSyncResult> {
    try {
      // 배치 요청 데이터 구성
      const requestData = {
        items: batch.map(item => ({
          type: item.type,
          idem: item.idem,
          payload: item.payload
        })),
        meta: {
          device_id: this.getDeviceId(),
          branch_id: 1, // 실제로는 사용자 정보에서 가져와야 함
          user_id: 1    // 실제로는 현재 사용자 ID
        }
      };

      // 배치 동기화 API 호출
      const response = await mobileAPI.syncBatch(requestData);
      
      // 결과 처리
      const result: BatchSyncResult = {
        success: true,
        processed: batch.length,
        delivered: 0,
        failed: 0,
        duplicates: 0,
        errors: []
      };

      // 각 아이템 결과 처리
      for (const itemResult of response.results) {
        const item = batch.find(b => b.idem === itemResult.idem);
        if (!item) continue;

        switch (itemResult.status) {
          case 'ok':
            result.delivered++;
            item.retryCount = 0; // 성공 시 재시도 카운트 리셋
            break;
          case 'dup':
            result.duplicates++;
            item.retryCount = 0; // 중복도 성공으로 간주
            break;
          case 'error':
            result.failed++;
            item.retryCount++;
            if (itemResult.error) {
              result.errors.push(`${item.type}: ${itemResult.error}`);
            }
            break;
        }
      }

      return result;

    } catch (error) {
      console.error('배치 처리 실패:', error);
      
      // 모든 아이템의 재시도 카운트 증가
      batch.forEach(item => item.retryCount++);
      
      return {
        success: false,
        processed: batch.length,
        delivered: 0,
        failed: batch.length,
        duplicates: 0,
        errors: [error.message]
      };
    }
  }

  /**
   * 처리된 아이템들 큐에서 제거
   */
  private async cleanupProcessedItems(): Promise<void> {
    // 성공하거나 최대 재시도 횟수를 초과한 아이템들 제거
    this.queue = this.queue.filter(item => 
      item.retryCount < item.maxRetries
    );
    
    await this.saveQueueToStorage();
  }

  /**
   * 디바이스 ID 생성
   */
  private getDeviceId(): string {
    // 실제로는 expo-device나 react-native-device-info 사용
    return `RN-${Platform.OS}-${Date.now()}`;
  }

  /**
   * 주기적 동기화 시작
   */
  private startPeriodicSync(): void {
    if (this.processingInterval) return;
    
    this.processingInterval = setInterval(() => {
      if (networkService.isOnline() && !this.isProcessing && this.queue.length > 0) {
        this.performSync();
      }
    }, this.SYNC_INTERVAL);
  }

  /**
   * 주기적 동기화 중지
   */
  private stopPeriodicSync(): void {
    if (this.processingInterval) {
      clearInterval(this.processingInterval);
      this.processingInterval = null;
    }
  }

  /**
   * 진행률 리스너 등록
   */
  addProgressListener(listener: (progress: SyncProgress) => void): () => void {
    this.listeners.add(listener);
    
    // 즉시 현재 상태 전달
    const currentProgress: SyncProgress = {
      current: 0,
      total: this.queue.length,
      percentage: 0,
      status: this.isProcessing ? 'syncing' : 'idle'
    };
    listener(currentProgress);
    
    // 리스너 제거 함수 반환
    return () => {
      this.listeners.delete(listener);
    };
  }

  /**
   * 진행률 리스너들에게 알림
   */
  private notifyProgress(progress: SyncProgress): void {
    this.listeners.forEach(listener => {
      try {
        listener(progress);
      } catch (error) {
        console.error('진행률 리스너 오류:', error);
      }
    });
  }

  /**
   * 현재 큐 상태 반환
   */
  getQueueStatus(): {
    total: number;
    byType: Record<string, number>;
    byPriority: Record<string, number>;
    oldestItem?: Date;
  } {
    const byType: Record<string, number> = {};
    const byPriority: Record<string, number> = {};
    let oldestItem: Date | undefined;

    this.queue.forEach(item => {
      byType[item.type] = (byType[item.type] || 0) + 1;
      byPriority[item.priority.toString()] = (byPriority[item.priority.toString()] || 0) + 1;
      
      if (!oldestItem || item.createdAt < oldestItem) {
        oldestItem = item.createdAt;
      }
    });

    return {
      total: this.queue.length,
      byType,
      byPriority,
      oldestItem
    };
  }

  /**
   * 큐 강제 정리 (개발/테스트용)
   */
  async clearQueue(): Promise<void> {
    this.queue = [];
    await AsyncStorage.removeItem(this.STORAGE_KEY);
    console.log('배치 큐 정리됨');
  }

  /**
   * 서비스 종료
   */
  destroy(): void {
    this.stopPeriodicSync();
    this.listeners.clear();
  }
}

// 싱글톤 인스턴스 내보내기
export const batchSyncService = BatchSyncService.getInstance();
