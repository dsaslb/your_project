/**
 * 📱 오프라인 큐 시스템
 * 
 * 네트워크 연결이 끊어진 상태에서 발생한 요청을 로컬에 저장하고,
 * 재연결 시 자동으로 동기화하는 시스템
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import { v4 as uuid } from 'uuid';

// 큐 아이템 타입 정의
export interface QueueItem {
  id: string;
  url: string;
  method: 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  body: any;
  headers: Record<string, string>;
  timestamp: number;
  retryCount: number;
  maxRetries: number;
}

// 큐 상태 타입
export interface QueueStatus {
  isOnline: boolean;
  queueLength: number;
  lastSync: number | null;
  isProcessing: boolean;
}

// 네트워크 상태 변경 콜백
type NetworkStatusCallback = (isOnline: boolean) => void;

class OfflineQueue {
  private queue: QueueItem[] = [];
  private isOnline: boolean = true;
  private isProcessing: boolean = false;
  private networkCallbacks: NetworkStatusCallback[] = [];
  private syncInterval: NodeJS.Timeout | null = null;
  
  constructor() {
    this.initialize();
  }
  
  /**
   * 시스템 초기화
   */
  private async initialize() {
    // 저장된 큐 로드
    await this.loadQueue();
    
    // 네트워크 상태 모니터링 시작
    this.startNetworkMonitoring();
    
    // 주기적 동기화 시작
    this.startPeriodicSync();
    
    // 앱 시작 시 큐 처리
    this.processQueue();
  }
  
  /**
   * 네트워크 상태 모니터링 시작
   */
  private startNetworkMonitoring() {
    NetInfo.addEventListener(state => {
      const wasOnline = this.isOnline;
      this.isOnline = state.isConnected ?? false;
      
      // 온라인 상태가 되었을 때 큐 처리
      if (!wasOnline && this.isOnline) {
        console.log('🌐 네트워크 연결 복구됨, 큐 동기화 시작');
        this.processQueue();
      }
      
      // 콜백 실행
      this.networkCallbacks.forEach(callback => callback(this.isOnline));
    });
  }
  
  /**
   * 주기적 동기화 시작 (5분마다)
   */
  private startPeriodicSync() {
    this.syncInterval = setInterval(() => {
      if (this.isOnline && this.queue.length > 0) {
        console.log('⏰ 주기적 큐 동기화 실행');
        this.processQueue();
      }
    }, 5 * 60 * 1000); // 5분
  }
  
  /**
   * 네트워크 상태 변경 콜백 등록
   */
  onNetworkStatusChange(callback: NetworkStatusCallback) {
    this.networkCallbacks.push(callback);
    return () => {
      const index = this.networkCallbacks.indexOf(callback);
      if (index > -1) {
        this.networkCallbacks.splice(index, 1);
      }
    };
  }
  
  /**
   * 큐에 요청 추가
   */
  async addToQueue(
    url: string, 
    method: 'POST' | 'PUT' | 'DELETE' | 'PATCH', 
    body: any, 
    headers: Record<string, string> = {}
  ): Promise<string> {
    const queueItem: QueueItem = {
      id: uuid(),
      url,
      method,
      body,
      headers: {
        ...headers,
        'X-Idempotency-Key': headers['X-Idempotency-Key'] || uuid(),
        'X-Offline-Queue': 'true',
        'X-Queue-Timestamp': Date.now().toString()
      },
      timestamp: Date.now(),
      retryCount: 0,
      maxRetries: 3
    };
    
    this.queue.push(queueItem);
    await this.saveQueue();
    
    console.log(`📥 큐에 추가됨: ${method} ${url} (ID: ${queueItem.id})`);
    
    // 온라인 상태라면 즉시 처리 시도
    if (this.isOnline) {
      this.processQueue();
    }
    
    return queueItem.id;
  }
  
  /**
   * 큐에서 요청 제거
   */
  async removeFromQueue(id: string): Promise<boolean> {
    const index = this.queue.findIndex(item => item.id === id);
    if (index > -1) {
      this.queue.splice(index, 1);
      await this.saveQueue();
      console.log(`🗑️ 큐에서 제거됨: ${id}`);
      return true;
    }
    return false;
  }
  
  /**
   * 큐 상태 조회
   */
  getQueueStatus(): QueueStatus {
    return {
      isOnline: this.isOnline,
      queueLength: this.queue.length,
      lastSync: this.queue.length > 0 ? Math.max(...this.queue.map(item => item.timestamp)) : null,
      isProcessing: this.isProcessing
    };
  }
  
  /**
   * 큐 내용 조회
   */
  getQueueItems(): QueueItem[] {
    return [...this.queue];
  }
  
  /**
   * 큐 처리 (온라인 상태에서만)
   */
  private async processQueue() {
    if (!this.isOnline || this.isProcessing || this.queue.length === 0) {
      return;
    }
    
    this.isProcessing = true;
    console.log(`🔄 큐 처리 시작 (${this.queue.length}개 항목)`);
    
    const itemsToProcess = [...this.queue];
    const failedItems: QueueItem[] = [];
    
    for (const item of itemsToProcess) {
      try {
        const success = await this.processQueueItem(item);
        if (success) {
          await this.removeFromQueue(item.id);
        } else {
          failedItems.push(item);
        }
      } catch (error) {
        console.error(`❌ 큐 아이템 처리 실패: ${item.id}`, error);
        failedItems.push(item);
      }
    }
    
    // 실패한 아이템들의 재시도 횟수 증가
    for (const item of failedItems) {
      item.retryCount++;
      if (item.retryCount >= item.maxRetries) {
        console.warn(`⚠️ 최대 재시도 횟수 초과: ${item.id}`);
        // 사용자에게 알림을 보낼 수 있음
      }
    }
    
    // 실패한 아이템들을 큐 앞쪽으로 이동 (우선 처리)
    this.queue = [...failedItems, ...this.queue.filter(item => 
      !failedItems.some(failed => failed.id === item.id)
    )];
    
    await this.saveQueue();
    this.isProcessing = false;
    
    console.log(`✅ 큐 처리 완료. 성공: ${itemsToProcess.length - failedItems.length}, 실패: ${failedItems.length}`);
  }
  
  /**
   * 개별 큐 아이템 처리
   */
  private async processQueueItem(item: QueueItem): Promise<boolean> {
    try {
      const response = await fetch(item.url, {
        method: item.method,
        headers: {
          'Content-Type': 'application/json',
          ...item.headers
        },
        body: JSON.stringify(item.body)
      });
      
      if (response.ok) {
        console.log(`✅ 큐 아이템 처리 성공: ${item.id}`);
        return true;
      } else {
        console.warn(`⚠️ 큐 아이템 처리 실패 (HTTP ${response.status}): ${item.id}`);
        return false;
      }
    } catch (error) {
      console.error(`❌ 큐 아이템 처리 중 오류: ${item.id}`, error);
      return false;
    }
  }
  
  /**
   * 큐를 로컬 스토리지에 저장
   */
  private async saveQueue() {
    try {
      await AsyncStorage.setItem('offlineQueue', JSON.stringify(this.queue));
    } catch (error) {
      console.error('❌ 큐 저장 실패:', error);
    }
  }
  
  /**
   * 로컬 스토리지에서 큐 로드
   */
  private async loadQueue() {
    try {
      const savedQueue = await AsyncStorage.getItem('offlineQueue');
      if (savedQueue) {
        this.queue = JSON.parse(savedQueue);
        console.log(`📱 저장된 큐 로드됨: ${this.queue.length}개 항목`);
      }
    } catch (error) {
      console.error('❌ 큐 로드 실패:', error);
      this.queue = [];
    }
  }
  
  /**
   * 큐 초기화
   */
  async clearQueue(): Promise<void> {
    this.queue = [];
    await AsyncStorage.removeItem('offlineQueue');
    console.log('🗑️ 큐 초기화 완료');
  }
  
  /**
   * 시스템 정리
   */
  cleanup() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }
    this.networkCallbacks = [];
  }
}

// 싱글톤 인스턴스 생성
export const offlineQueue = new OfflineQueue();

/**
 * 안전한 API 호출 함수
 * 네트워크 연결이 끊어진 경우 자동으로 큐에 추가
 */
export async function safeApiCall<T>(
  url: string,
  method: 'POST' | 'PUT' | 'DELETE' | 'PATCH',
  body: any,
  headers: Record<string, string> = {}
): Promise<{ success: boolean; data?: T; queueId?: string; error?: string }> {
  try {
    // 네트워크 상태 확인
    const netInfo = await NetInfo.fetch();
    
    if (!netInfo.isConnected) {
      // 오프라인 상태: 큐에 추가
      const queueId = await offlineQueue.addToQueue(url, method, body, headers);
      return {
        success: false,
        queueId,
        error: 'offline'
      };
    }
    
    // 온라인 상태: 직접 API 호출
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      body: JSON.stringify(body)
    });
    
    if (response.ok) {
      const data = await response.json();
      return { success: true, data };
    } else {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
  } catch (error) {
    console.error('API 호출 실패:', error);
    
    // 오류 발생 시에도 큐에 추가 시도
    try {
      const queueId = await offlineQueue.addToQueue(url, method, body, headers);
      return {
        success: false,
        queueId,
        error: 'failed_and_queued'
      };
    } catch (queueError) {
      return {
        success: false,
        error: 'failed_and_queue_failed'
      };
    }
  }
}

/**
 * 특정 큐 아이템 재시도
 */
export async function retryQueueItem(queueId: string): Promise<boolean> {
  const queueItems = offlineQueue.getQueueItems();
  const item = queueItems.find(q => q.id === queueId);
  
  if (!item) {
    console.warn(`⚠️ 큐 아이템을 찾을 수 없음: ${queueId}`);
    return false;
  }
  
  // 재시도 횟수 초기화
  item.retryCount = 0;
  
  // 큐 처리 시작
  offlineQueue.processQueue();
  
  return true;
}

export default OfflineQueue;
