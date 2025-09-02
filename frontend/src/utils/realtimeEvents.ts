/**
 * 🌐 실시간 이벤트 처리 시스템
 * 
 * Socket.IO를 통해 서버에서 전송되는 실시간 이벤트를 처리하고,
 * 웹 UI를 자동으로 업데이트하는 시스템
 */

import { io, Socket } from 'socket.io-client';
import { EventEmitter } from 'events';

// 이벤트 타입 정의
export interface RealtimeEvent {
  v: number;  // 이벤트 버전
  server_timestamp: string;
  [key: string]: any;
}

// 이벤트 리스너 타입
export type EventListener = (data: RealtimeEvent) => void;

// 구독 옵션
export interface SubscriptionOptions {
  branch_id?: string;
  brand_id?: string;
  industry_id?: string;
  user_id?: string;
  role?: string;
}

// 이벤트 처리기 클래스
class RealtimeEventHandler extends EventEmitter {
  private socket: Socket | null = null;
  private isConnected: boolean = false;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectDelay: number = 1000;
  private subscriptions: Map<string, Set<EventListener>> = new Map();
  private userContext: {
    user_id?: string;
    role?: string;
    industry_id?: string;
    brand_id?: string;
    branch_id?: string;
  } = {};

  constructor() {
    super();
    this.setupEventHandlers();
  }

  /**
   * 소켓 연결 초기화
   */
  connect(url: string, authToken: string, userContext: Partial<typeof this.userContext> = {}) {
    if (this.socket) {
      this.disconnect();
    }

    this.userContext = userContext;

    this.socket = io(url, {
      auth: {
        token: authToken
      },
      transports: ['websocket', 'polling'],
      timeout: 20000,
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay
    });

    this.setupSocketEventHandlers();
  }

  /**
   * 소켓 연결 해제
   */
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  /**
   * 사용자 컨텍스트 업데이트
   */
  updateUserContext(context: Partial<typeof this.userContext>) {
    this.userContext = { ...this.userContext, ...context };
    
    // 기존 구독들을 새로운 컨텍스트로 업데이트
    this.updateSubscriptions();
  }

  /**
   * 이벤트 구독
   */
  subscribe(eventType: string, listener: EventListener, options: SubscriptionOptions = {}) {
    if (!this.subscriptions.has(eventType)) {
      this.subscriptions.set(eventType, new Set());
    }
    
    this.subscriptions.get(eventType)!.add(listener);
    
    // 소켓에 룸 구독 요청
    this.joinRooms(eventType, options);
    
    return () => {
      this.unsubscribe(eventType, listener);
    };
  }

  /**
   * 이벤트 구독 해제
   */
  unsubscribe(eventType: string, listener: EventListener) {
    const listeners = this.subscriptions.get(eventType);
    if (listeners) {
      listeners.delete(listener);
      if (listeners.size === 0) {
        this.subscriptions.delete(eventType);
        // 룸에서 나가기
        this.leaveRooms(eventType);
      }
    }
  }

  /**
   * 특정 이벤트 타입의 모든 구독 해제
   */
  unsubscribeAll(eventType: string) {
    this.subscriptions.delete(eventType);
    this.leaveRooms(eventType);
  }

  /**
   * 모든 구독 해제
   */
  unsubscribeAllEvents() {
    this.subscriptions.clear();
    if (this.socket) {
      this.socket.emit('leave_all_rooms');
    }
  }

  /**
   * 연결 상태 확인
   */
  isSocketConnected(): boolean {
    return this.isConnected && this.socket?.connected === true;
  }

  /**
   * 소켓 이벤트 핸들러 설정
   */
  private setupSocketEventHandlers() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('🌐 소켓 연결됨');
      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.emit('connected');
      
      // 기존 구독 복원
      this.restoreSubscriptions();
    });

    this.socket.on('disconnect', (reason) => {
      console.log('❌ 소켓 연결 끊어짐:', reason);
      this.isConnected = false;
      this.emit('disconnected', reason);
      
      if (reason === 'io server disconnect') {
        // 서버에서 연결을 끊은 경우
        this.socket?.connect();
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('❌ 소켓 연결 오류:', error);
      this.emit('connection_error', error);
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log(`🔄 소켓 재연결 성공 (시도 ${attemptNumber})`);
      this.emit('reconnected', attemptNumber);
      
      // 구독 복원
      this.restoreSubscriptions();
    });

    this.socket.on('reconnect_attempt', (attemptNumber) => {
      console.log(`🔄 소켓 재연결 시도 ${attemptNumber}`);
      this.emit('reconnect_attempt', attemptNumber);
    });

    this.socket.on('reconnect_failed', () => {
      console.error('❌ 소켓 재연결 실패');
      this.emit('reconnect_failed');
    });

    // 비즈니스 이벤트들 처리
    this.setupBusinessEventHandlers();
  }

  /**
   * 비즈니스 이벤트 핸들러 설정
   */
  private setupBusinessEventHandlers() {
    if (!this.socket) return;

    // 출퇴근 이벤트
    this.socket.on('attendance:update', (data: RealtimeEvent) => {
      this.handleEvent('attendance:update', data);
    });

    // 재고 이벤트
    this.socket.on('inventory:update', (data: RealtimeEvent) => {
      this.handleEvent('inventory:update', data);
    });

    // 발주 이벤트
    this.socket.on('purchase_order:update', (data: RealtimeEvent) => {
      this.handleEvent('purchase_order:update', data);
    });

    // 주문 이벤트
    this.socket.on('order:update', (data: RealtimeEvent) => {
      this.handleEvent('order:update', data);
    });

    // 알림 이벤트
    this.socket.on('notification', (data: RealtimeEvent) => {
      this.handleEvent('notification', data);
    });

    // 시스템 이벤트
    this.socket.on('system:update', (data: RealtimeEvent) => {
      this.handleEvent('system:update', data);
    });

    // 오류 이벤트
    this.socket.on('error', (data: RealtimeEvent) => {
      this.handleEvent('error', data);
    });
  }

  /**
   * 이벤트 처리 및 리스너들에게 전파
   */
  private handleEvent(eventType: string, data: RealtimeEvent) {
    // 이벤트 버전 검증
    if (!this.validateEventVersion(data)) {
      console.warn(`⚠️ 이벤트 버전 불일치: ${eventType}`, data);
      return;
    }

    // 테넌트 스코프 검증
    if (!this.validateTenantScope(data)) {
      console.warn(`⚠️ 테넌트 스코프 불일치: ${eventType}`, data);
      return;
    }

    console.log(`📡 이벤트 수신: ${eventType}`, data);

    // 구독된 리스너들에게 이벤트 전파
    const listeners = this.subscriptions.get(eventType);
    if (listeners) {
      listeners.forEach(listener => {
        try {
          listener(data);
        } catch (error) {
          console.error(`❌ 이벤트 리스너 오류 (${eventType}):`, error);
        }
      });
    }

    // 전역 이벤트 발생
    this.emit(eventType, data);
  }

  /**
   * 이벤트 버전 검증
   */
  private validateEventVersion(data: RealtimeEvent): boolean {
    if (!data.v || typeof data.v !== 'number') {
      return false;
    }
    
    // 현재 지원하는 최대 버전 (필요시 조정)
    const maxSupportedVersion = 1;
    return data.v <= maxSupportedVersion;
  }

  /**
   * 테넌트 스코프 검증
   */
  private validateTenantScope(data: RealtimeEvent): boolean {
    // 사용자 컨텍스트가 설정되지 않은 경우 모든 이벤트 허용
    if (!this.userContext.industry_id && !this.userContext.brand_id && !this.userContext.branch_id) {
      return true;
    }

    // 이벤트 데이터에 테넌트 정보가 없는 경우 허용
    if (!data.industry_id && !data.brand_id && !data.branch_id) {
      return true;
    }

    // 테넌트 스코프 검증
    if (this.userContext.industry_id && data.industry_id && 
        this.userContext.industry_id !== data.industry_id) {
      return false;
    }

    if (this.userContext.brand_id && data.brand_id && 
        this.userContext.brand_id !== data.brand_id) {
      return false;
    }

    if (this.userContext.branch_id && data.branch_id && 
        this.userContext.branch_id !== data.branch_id) {
      return false;
    }

    return true;
  }

  /**
   * 룸 참가
   */
  private joinRooms(eventType: string, options: SubscriptionOptions) {
    if (!this.socket || !this.isConnected) return;

    const rooms: string[] = [];

    // 이벤트 타입별 기본 룸
    rooms.push(eventType);

    // 테넌트 스코프별 룸
    if (options.branch_id) {
      rooms.push(`branch:${options.branch_id}`);
    }
    if (options.brand_id) {
      rooms.push(`brand:${options.brand_id}`);
    }
    if (options.industry_id) {
      rooms.push(`industry:${options.industry_id}`);
    }

    // 사용자별 룸
    if (options.user_id) {
      rooms.push(`user:${options.user_id}`);
    }

    // 역할별 룸
    if (options.role) {
      rooms.push(`role:${options.role}`);
    }

    // 룸 참가 요청
    rooms.forEach(room => {
      this.socket!.emit('join', room);
      console.log(`🚪 룸 참가: ${room}`);
    });
  }

  /**
   * 룸 나가기
   */
  private leaveRooms(eventType: string) {
    if (!this.socket || !this.isConnected) return;

    // 이벤트 타입별 룸에서 나가기
    this.socket.emit('leave', eventType);
    console.log(`🚪 룸 나감: ${eventType}`);
  }

  /**
   * 구독 복원
   */
  private restoreSubscriptions() {
    if (!this.isConnected) return;

    console.log('🔄 구독 복원 중...');
    
    this.subscriptions.forEach((listeners, eventType) => {
      if (listeners.size > 0) {
        // 기본 룸에 다시 참가
        this.socket?.emit('join', eventType);
      }
    });
  }

  /**
   * 구독 업데이트
   */
  private updateSubscriptions() {
    if (!this.isConnected) return;

    // 모든 구독을 새로운 컨텍스트로 업데이트
    this.subscriptions.forEach((listeners, eventType) => {
      if (listeners.size > 0) {
        // 기존 룸에서 나가기
        this.socket?.emit('leave', eventType);
        
        // 새로운 컨텍스트로 룸 참가
        this.joinRooms(eventType, this.userContext);
      }
    });
  }

  /**
   * 이벤트 에미터 설정
   */
  private setupEventHandlers() {
    // 연결 상태 변경 이벤트
    this.on('connected', () => {
      console.log('✅ 실시간 이벤트 시스템 연결됨');
    });

    this.on('disconnected', (reason) => {
      console.log('❌ 실시간 이벤트 시스템 연결 끊어짐:', reason);
    });

    this.on('reconnected', (attemptNumber) => {
      console.log(`🔄 실시간 이벤트 시스템 재연결됨 (시도 ${attemptNumber})`);
    });
  }
}

// 싱글톤 인스턴스 생성
export const realtimeEvents = new RealtimeEventHandler();

// 편의 함수들
export const subscribeToEvent = (
  eventType: string, 
  listener: EventListener, 
  options: SubscriptionOptions = {}
) => realtimeEvents.subscribe(eventType, listener, options);

export const unsubscribeFromEvent = (eventType: string, listener: EventListener) => 
  realtimeEvents.unsubscribe(eventType, listener);

export const connectToRealtime = (url: string, authToken: string, userContext: any = {}) =>
  realtimeEvents.connect(url, authToken, userContext);

export const disconnectFromRealtime = () => realtimeEvents.disconnect();

export const isRealtimeConnected = () => realtimeEvents.isSocketConnected();

export default realtimeEvents;
