import { localStorageService, OfflineAction } from './LocalStorageService';
import { networkService } from './NetworkService';
import { mobileAPI } from '../api/client';
import { v4 as uuidv4 } from 'uuid';

export interface QueueItem {
  id: string;
  action: OfflineAction;
  priority: number; // 높을수록 우선순위 높음
  createdAt: Date;
}

export class OfflineQueueService {
  private static instance: OfflineQueueService;
  private queue: QueueItem[] = [];
  private isProcessing = false;
  private processingInterval: NodeJS.Timeout | null = null;
  private listeners: Set<(queue: QueueItem[]) => void> = new Set();

  private constructor() {
    this.initialize();
  }

  public static getInstance(): OfflineQueueService {
    if (!OfflineQueueService.instance) {
      OfflineQueueService.instance = new OfflineQueueService();
    }
    return OfflineQueueService.instance;
  }

  private async initialize(): Promise<void> {
    // 로컬 스토리지에서 대기 중인 액션들 로드
    await this.loadPendingActions();
    
    // 네트워크 상태 변경 리스너 등록
    networkService.addListener((networkState) => {
      if (networkState.isConnected && networkState.isInternetReachable) {
        this.startProcessing();
      } else {
        this.stopProcessing();
      }
    });

    // 주기적으로 큐 처리 (30초마다)
    this.processingInterval = setInterval(() => {
      if (networkService.isOnline() && !this.isProcessing) {
        this.processQueue();
      }
    }, 30000);
  }

  /**
   * 로컬 스토리지에서 대기 중인 액션들 로드
   */
  private async loadPendingActions(): Promise<void> {
    try {
      const pendingActions = await localStorageService.getPendingActions();
      
      this.queue = pendingActions.map(action => ({
        id: action.id,
        action,
        priority: this.getActionPriority(action.type),
        createdAt: new Date(action.timestamp),
      }));

      // 우선순위 순으로 정렬
      this.queue.sort((a, b) => b.priority - a.priority);
      
      this.notifyListeners();
    } catch (error) {
      console.error('대기 중인 액션 로드 실패:', error);
    }
  }

  /**
   * 액션 타입별 우선순위 반환
   */
  private getActionPriority(actionType: OfflineAction['type']): number {
    const priorities = {
      'clock_in': 10,
      'clock_out': 10,
      'inventory_check': 5,
      'purchase_order': 8,
      'sync_data': 3,
    };
    return priorities[actionType] || 1;
  }

  /**
   * 액션을 큐에 추가
   */
  async enqueue(
    type: OfflineAction['type'],
    data: any,
    maxRetries: number = 3
  ): Promise<string> {
    try {
      const actionId = await localStorageService.addOfflineAction({
        type,
        data,
        max_retries: maxRetries,
      });

      const queueItem: QueueItem = {
        id: actionId,
        action: {
          id: actionId,
          type,
          data,
          timestamp: new Date().toISOString(),
          retry_count: 0,
          max_retries: maxRetries,
          status: 'pending',
        },
        priority: this.getActionPriority(type),
        createdAt: new Date(),
      };

      this.queue.push(queueItem);
      this.queue.sort((a, b) => b.priority - a.priority);
      this.notifyListeners();

      // 온라인 상태라면 즉시 처리 시도
      if (networkService.isOnline()) {
        this.processQueue();
      }

      return actionId;
    } catch (error) {
      console.error('액션 큐 추가 실패:', error);
      throw error;
    }
  }

  /**
   * 큐에서 액션 제거
   */
  async dequeue(actionId: string): Promise<void> {
    try {
      this.queue = this.queue.filter(item => item.id !== actionId);
      await localStorageService.deleteCompletedAction(actionId);
      this.notifyListeners();
    } catch (error) {
      console.error('액션 큐 제거 실패:', error);
    }
  }

  /**
   * 큐 처리 시작
   */
  private startProcessing(): void {
    if (!this.isProcessing) {
      this.processQueue();
    }
  }

  /**
   * 큐 처리 중지
   */
  private stopProcessing(): void {
    this.isProcessing = false;
  }

  /**
   * 큐 처리
   */
  private async processQueue(): Promise<void> {
    if (this.isProcessing || !networkService.isOnline() || this.queue.length === 0) {
      return;
    }

    this.isProcessing = true;

    try {
      const itemsToProcess = [...this.queue];
      
      for (const item of itemsToProcess) {
        if (!networkService.isOnline()) {
          break; // 네트워크가 끊어지면 중단
        }

        try {
          await this.processAction(item);
          await this.dequeue(item.id);
        } catch (error) {
          console.error(`액션 처리 실패 (${item.id}):`, error);
          await this.handleActionFailure(item, error);
        }
      }
    } finally {
      this.isProcessing = false;
    }
  }

  /**
   * 개별 액션 처리
   */
  private async processAction(item: QueueItem): Promise<void> {
    const { action } = item;

    // 액션 상태를 처리 중으로 업데이트
    await localStorageService.updateActionStatus(action.id, 'processing');

    switch (action.type) {
      case 'clock_in':
        await this.processClockIn(action.data);
        break;
      case 'clock_out':
        await this.processClockOut(action.data);
        break;
      case 'inventory_check':
        await this.processInventoryCheck(action.data);
        break;
      case 'purchase_order':
        await this.processPurchaseOrder(action.data);
        break;
      case 'sync_data':
        await this.processDataSync(action.data);
        break;
      default:
        throw new Error(`알 수 없는 액션 타입: ${action.type}`);
    }

    // 액션 상태를 완료로 업데이트
    await localStorageService.updateActionStatus(action.id, 'completed');
  }

  /**
   * 출근 체크 처리
   */
  private async processClockIn(data: any): Promise<void> {
    const result = await mobileAPI.clockIn(data);
    
    // 로컬 출퇴근 기록을 동기화됨으로 표시
    if (data.localId) {
      await localStorageService.markAsSynced('local_attendance', data.localId, result.id);
    }
  }

  /**
   * 퇴근 체크 처리
   */
  private async processClockOut(data: any): Promise<void> {
    const result = await mobileAPI.clockOut(data);
    
    // 로컬 출퇴근 기록을 동기화됨으로 표시
    if (data.localId) {
      await localStorageService.markAsSynced('local_attendance', data.localId, result.id);
    }
  }

  /**
   * 재고 조사 처리
   */
  private async processInventoryCheck(data: any): Promise<void> {
    const result = await mobileAPI.checkInventory(data);
    
    // 로컬 재고 조사 기록을 동기화됨으로 표시
    if (data.localId) {
      await localStorageService.markAsSynced('local_inventory_checks', data.localId, result.id);
    }
  }

  /**
   * 발주 처리
   */
  private async processPurchaseOrder(data: any): Promise<void> {
    const result = await mobileAPI.createPurchaseOrder(data);
    
    // 로컬 발주 기록을 동기화됨으로 표시
    if (data.localId) {
      await localStorageService.markAsSynced('local_purchase_orders', data.localId, result.order_id);
    }
  }

  /**
   * 데이터 동기화 처리
   */
  private async processDataSync(data: any): Promise<void> {
    // 동기화되지 않은 데이터들을 서버로 전송
    const unsyncedData = await localStorageService.getUnsyncedData();
    
    // 출퇴근 기록 동기화
    for (const attendance of unsyncedData.attendance) {
      try {
        const result = await mobileAPI.clockIn({
          lat: attendance.lat,
          lng: attendance.lng,
        });
        await localStorageService.markAsSynced('local_attendance', attendance.id, result.id);
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
      } catch (error) {
        console.error('발주 동기화 실패:', error);
      }
    }
  }

  /**
   * 액션 실패 처리
   */
  private async handleActionFailure(item: QueueItem, error: any): Promise<void> {
    const { action } = item;

    if (action.retry_count >= action.max_retries) {
      // 최대 재시도 횟수 초과
      await localStorageService.updateActionStatus(
        action.id,
        'failed',
        `최대 재시도 횟수 초과: ${error.message}`
      );
      
      // 큐에서 제거
      this.queue = this.queue.filter(q => q.id !== action.id);
    } else {
      // 재시도 가능
      await localStorageService.updateActionStatus(
        action.id,
        'pending',
        `재시도 중: ${error.message}`
      );
    }

    this.notifyListeners();
  }

  /**
   * 큐 상태 리스너 등록
   */
  addListener(listener: (queue: QueueItem[]) => void): () => void {
    this.listeners.add(listener);
    
    // 즉시 현재 큐 상태 전달
    listener([...this.queue]);
    
    // 리스너 제거 함수 반환
    return () => {
      this.listeners.delete(listener);
    };
  }

  /**
   * 리스너들에게 큐 상태 알림
   */
  private notifyListeners(): void {
    this.listeners.forEach(listener => {
      try {
        listener([...this.queue]);
      } catch (error) {
        console.error('큐 상태 리스너 오류:', error);
      }
    });
  }

  /**
   * 현재 큐 상태 반환
   */
  getQueue(): QueueItem[] {
    return [...this.queue];
  }

  /**
   * 큐 크기 반환
   */
  getQueueSize(): number {
    return this.queue.length;
  }

  /**
   * 큐 정리 (완료된 액션들 삭제)
   */
  async cleanup(): Promise<void> {
    await localStorageService.cleanup();
    await this.loadPendingActions();
  }

  /**
   * 서비스 종료
   */
  destroy(): void {
    if (this.processingInterval) {
      clearInterval(this.processingInterval);
      this.processingInterval = null;
    }
    this.stopProcessing();
    this.listeners.clear();
  }
}

// 싱글톤 인스턴스 내보내기
export const offlineQueueService = OfflineQueueService.getInstance();
