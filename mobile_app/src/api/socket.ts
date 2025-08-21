import { io, Socket } from 'socket.io-client';
import { API_CONFIG } from '../config/api';

// 소켓 이벤트 타입 정의
export interface SocketEvents {
  // 출퇴근
  'attendance:update': {
    user_id: number;
    type: 'in' | 'out';
    timestamp: string;
    location: { lat: number; lng: number };
    qr_code?: string;
    user_name: string;
  };
  
  // 재고
  'inventory:update': {
    id: number;
    barcode: string;
    qty: number;
    user_id: number;
    timestamp: string;
  };
  
  // 발주
  'purchase_order:update': {
    id: number;
    status: 'requested' | 'approved' | 'ordered' | 'received';
    user_id: number;
    items: Array<{ barcode: string; name: string; qty: number }>;
  };
  
  // 스케줄
  'schedule:update': {
    id: number;
    user_id: number;
    date: string;
    type: 'created' | 'updated' | 'deleted';
  };
  
  // 주문
  'order:update': {
    id: number;
    status: string;
    user_id: number;
    timestamp: string;
  };
  
  // 긴급 알림
  'emergency:notification': {
    type: 'urgent' | 'warning' | 'info';
    message: string;
    target_users?: number[];
  };
  
  // 연결 상태
  'connect': () => void;
  'disconnect': (reason: string) => void;
  'connect_error': (error: Error) => void;
}

// 소켓 클라이언트 클래스
class SocketClient {
  private socket: Socket | null = null;
  private isConnected = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = API_CONFIG.SOCKET.RECONNECTION_ATTEMPTS;
  private reconnectDelay = API_CONFIG.SOCKET.RECONNECTION_DELAY;
  private eventListeners: Map<string, Set<Function>> = new Map();

  constructor() {
    this.initializeSocket();
  }

  // 소켓 초기화
  private initializeSocket() {
    try {
      this.socket = io(API_CONFIG.WS_URL, {
        transports: ['websocket'],
        timeout: API_CONFIG.SOCKET.TIMEOUT,
        reconnection: true,
        reconnectionAttempts: this.maxReconnectAttempts,
        reconnectionDelay: this.reconnectDelay,
        autoConnect: false, // 수동으로 연결
      });

      this.setupEventHandlers();
    } catch (error) {
      console.error('소켓 초기화 실패:', error);
    }
  }

  // 이벤트 핸들러 설정
  private setupEventHandlers() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('소켓 연결됨');
      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.emit('connect');
    });

    this.socket.on('disconnect', (reason) => {
      console.log('소켓 연결 해제:', reason);
      this.isConnected = false;
      this.emit('disconnect', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('소켓 연결 오류:', error);
      this.emit('connect_error', error);
    });

    // 자동 재연결
    this.socket.on('reconnect', (attemptNumber) => {
      console.log(`소켓 재연결 성공 (시도 ${attemptNumber})`);
      this.isConnected = true;
      this.reconnectAttempts = 0;
    });

    this.socket.on('reconnect_attempt', (attemptNumber) => {
      console.log(`소켓 재연결 시도 ${attemptNumber}`);
      this.reconnectAttempts = attemptNumber;
    });

    this.socket.on('reconnect_failed', () => {
      console.error('소켓 재연결 실패');
      this.isConnected = false;
    });
  }

  // 연결
  connect() {
    if (this.socket && !this.isConnected) {
      this.socket.connect();
    }
  }

  // 연결 해제
  disconnect() {
    if (this.socket && this.isConnected) {
      this.socket.disconnect();
      this.isConnected = false;
    }
  }

  // 연결 상태 확인
  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  // 이벤트 리스너 등록
  on<T extends keyof SocketEvents>(event: T, callback: SocketEvents[T]) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set());
    }
    this.eventListeners.get(event)!.add(callback as Function);

    // 소켓에도 등록
    if (this.socket) {
      this.socket.on(event, callback as Function);
    }
  }

  // 이벤트 리스너 제거
  off<T extends keyof SocketEvents>(event: T, callback: SocketEvents[T]) {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.delete(callback as Function);
    }

    // 소켓에서도 제거
    if (this.socket) {
      this.socket.off(event, callback as Function);
    }
  }

  // 이벤트 발생
  private emit(event: string, ...args: any[]) {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(...args);
        } catch (error) {
          console.error(`이벤트 핸들러 오류 (${event}):`, error);
        }
      });
    }
  }

  // 서버로 이벤트 전송
  emitToServer(event: string, data?: any) {
    if (this.socket && this.isConnected) {
      this.socket.emit(event, data);
    } else {
      console.warn('소켓이 연결되지 않았습니다. 이벤트 전송 실패:', event);
    }
  }

  // 연결 상태 모니터링
  onConnectionChange(callback: (connected: boolean) => void) {
    this.on('connect', () => callback(true));
    this.on('disconnect', () => callback(false));
  }

  // 특정 사용자에게만 전송되는 이벤트 필터링
  onUserSpecificEvent<T extends keyof SocketEvents>(
    event: T,
    userId: number,
    callback: (data: any) => void
  ) {
    this.on(event, (data: any) => {
      if (data.user_id === userId) {
        callback(data);
      }
    });
  }

  // 오프라인 큐 관리
  private offlineQueue: Array<{ event: string; data: any; timestamp: number }> = [];

  // 오프라인 상태에서 이벤트 큐에 저장
  queueEvent(event: string, data: any) {
    this.offlineQueue.push({
      event,
      data,
      timestamp: Date.now(),
    });

    // 로컬 스토리지에 저장
    this.saveOfflineQueue();
  }

  // 연결 복구 시 오프라인 큐 처리
  private processOfflineQueue() {
    if (this.offlineQueue.length > 0) {
      console.log(`오프라인 큐 처리 중: ${this.offlineQueue.length}개 이벤트`);
      
      this.offlineQueue.forEach(({ event, data }) => {
        this.emitToServer(event, data);
      });
      
      this.offlineQueue = [];
      this.saveOfflineQueue();
    }
  }

  // 오프라인 큐 저장
  private saveOfflineQueue() {
    try {
      // AsyncStorage를 사용하여 큐 저장 (필요시)
      // AsyncStorage.setItem('socket_offline_queue', JSON.stringify(this.offlineQueue));
    } catch (error) {
      console.error('오프라인 큐 저장 실패:', error);
    }
  }

  // 오프라인 큐 로드
  private loadOfflineQueue() {
    try {
      // AsyncStorage에서 큐 로드 (필요시)
      // const saved = await AsyncStorage.getItem('socket_offline_queue');
      // if (saved) {
      //   this.offlineQueue = JSON.parse(saved);
      // }
    } catch (error) {
      console.error('오프라인 큐 로드 실패:', error);
    }
  }

  // 연결 시 오프라인 큐 처리
  private handleReconnect() {
    this.processOfflineQueue();
  }
}

// 싱글톤 인스턴스
export const socketClient = new SocketClient();

// 편의 함수들
export const socket = {
  connect: socketClient.connect.bind(socketClient),
  disconnect: socketClient.disconnect.bind(socketClient),
  on: socketClient.on.bind(socketClient),
  off: socketClient.off.bind(socketClient),
  emit: socketClient.emitToServer.bind(socketClient),
  getConnectionStatus: socketClient.getConnectionStatus.bind(socketClient),
  onConnectionChange: socketClient.onConnectionChange.bind(socketClient),
  onUserSpecificEvent: socketClient.onUserSpecificEvent.bind(socketClient),
};

// 기본 연결 시도
socketClient.connect();
