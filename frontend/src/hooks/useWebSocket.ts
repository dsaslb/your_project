import { useEffect, useRef, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

export interface Notification {
  id: string;
  type: string;
  message: string;
  data: any;
  priority: 'high' | 'medium' | 'low';
  created_at: string;
  read: boolean;
  read_at?: string;
}

export interface WebSocketStatus {
  connected: boolean;
  connecting: boolean;
  error: string | null;
  lastActivity: Date | null;
}

export interface NotificationStats {
  total_notifications: number;
  unread_count: number;
  read_count: number;
  type_stats: Record<string, { total: number; unread: number }>;
  priority_stats: Record<string, number>;
  connected_clients: number;
}

interface UseWebSocketOptions {
  userId?: string;
  autoConnect?: boolean;
  reconnectAttempts?: number;
  reconnectDelay?: number;
}

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const {
    userId = 'anonymous',
    autoConnect = true,
    reconnectAttempts = 5,
    reconnectDelay = 1000
  } = options;

  const socketRef = useRef<Socket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const [status, setStatus] = useState<WebSocketStatus>({
    connected: false,
    connecting: false,
    error: null,
    lastActivity: null
  });

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [stats, setStats] = useState<NotificationStats | null>(null);

  // WebSocket 연결 생성
  const connect = useCallback(() => {
    if (socketRef.current?.connected) return;

    setStatus(prev => ({ ...prev, connecting: true, error: null }));

    try {
      const socket = io(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000', {
        query: { user_id: userId },
        transports: ['websocket', 'polling'],
        timeout: 20000,
        reconnection: false // 수동으로 재연결 처리
      });

      socketRef.current = socket;

      // 연결 이벤트
      socket.on('connect', () => {
        console.log('WebSocket 연결됨');
        setStatus({
          connected: true,
          connecting: false,
          error: null,
          lastActivity: new Date()
        });
        reconnectAttemptsRef.current = 0;
      });

      socket.on('disconnect', (reason) => {
        console.log('WebSocket 연결 해제:', reason);
        setStatus(prev => ({
          ...prev,
          connected: false,
          connecting: false,
          error: reason === 'io server disconnect' ? '서버에서 연결을 해제했습니다.' : null
        }));

        // 자동 재연결 시도
        if (reconnectAttemptsRef.current < reconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(`재연결 시도 ${reconnectAttemptsRef.current}/${reconnectAttempts}`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectDelay * reconnectAttemptsRef.current);
        }
      });

      socket.on('connect_error', (error) => {
        console.error('WebSocket 연결 오류:', error);
        setStatus(prev => ({
          ...prev,
          connecting: false,
          error: `연결 실패: ${error.message}`
        }));
      });

      // 알림 이벤트
      socket.on('notification', (notification: Notification) => {
        console.log('새 알림 수신:', notification);
        setNotifications(prev => [notification, ...prev]);
        setStatus(prev => ({ ...prev, lastActivity: new Date() }));
      });

      socket.on('notification_history', (data: { notifications: Notification[] }) => {
        console.log('알림 히스토리 수신:', data.notifications.length);
        setNotifications(data.notifications);
      });

      // 기타 이벤트
      socket.on('connection_established', (data) => {
        console.log('연결 확인:', data);
        setStatus(prev => ({ ...prev, lastActivity: new Date() }));
      });

      socket.on('room_joined', (data) => {
        console.log('룸 참가:', data);
      });

      socket.on('room_left', (data) => {
        console.log('룸 나감:', data);
      });

      socket.on('subscription_confirmed', (data) => {
        console.log('알림 구독 확인:', data);
      });

      socket.on('unsubscription_confirmed', (data) => {
        console.log('알림 구독 해제 확인:', data);
      });

      socket.on('notification_marked_read', (data) => {
        console.log('알림 읽음 처리:', data);
        setNotifications(prev => 
          prev.map(n => 
            n.id === data.notification_id 
              ? { ...n, read: true, read_at: data.timestamp }
              : n
          )
        );
      });

      socket.on('pong', (data) => {
        setStatus(prev => ({ ...prev, lastActivity: new Date() }));
      });

      socket.on('error', (error) => {
        console.error('WebSocket 오류:', error);
        setStatus(prev => ({ ...prev, error: error.message }));
      });

    } catch (error) {
      console.error('WebSocket 초기화 오류:', error);
      setStatus(prev => ({
        ...prev,
        connecting: false,
        error: `초기화 실패: ${error instanceof Error ? error.message : '알 수 없는 오류'}`
      }));
    }
  }, [userId, reconnectAttempts, reconnectDelay]);

  // 연결 해제
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
    }

    setStatus({
      connected: false,
      connecting: false,
      error: null,
      lastActivity: null
    });
  }, []);

  // 알림 구독
  const subscribeNotifications = useCallback((types: string[]) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('subscribe_notifications', { types });
    }
  }, []);

  // 알림 구독 해제
  const unsubscribeNotifications = useCallback((types: string[]) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('unsubscribe_notifications', { types });
    }
  }, []);

  // 룸 참가
  const joinRoom = useCallback((room: string) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('join_room', { room });
    }
  }, []);

  // 룸 나가기
  const leaveRoom = useCallback((room: string) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('leave_room', { room });
    }
  }, []);

  // 알림 읽음 처리
  const markNotificationRead = useCallback((notificationId: string) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('mark_notification_read', { notification_id: notificationId });
    }
  }, []);

  // 핑 전송
  const ping = useCallback(() => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('ping');
    }
  }, []);

  // 알림 통계 조회
  const fetchNotificationStats = useCallback(async () => {
    try {
      const response = await fetch('/api/websocket/notifications/stats');
      const data = await response.json();
      
      if (data.success) {
        setStats(data.data);
      }
    } catch (error) {
      console.error('알림 통계 조회 실패:', error);
    }
  }, []);

  // 알림 히스토리 조회
  const fetchNotificationHistory = useCallback(async (options?: {
    limit?: number;
    type?: string;
    unread_only?: boolean;
  }) => {
    try {
      const params = new URLSearchParams();
      if (options?.limit) params.append('limit', options.limit.toString());
      if (options?.type) params.append('type', options.type);
      if (options?.unread_only) params.append('unread_only', 'true');

      const response = await fetch(`/api/websocket/notifications/history?${params}`);
      const data = await response.json();
      
      if (data.success) {
        setNotifications(data.data.notifications);
      }
    } catch (error) {
      console.error('알림 히스토리 조회 실패:', error);
    }
  }, []);

  // 알림 읽음 처리 (배치)
  const markNotificationsRead = useCallback(async (notificationIds: string[]) => {
    try {
      const response = await fetch('/api/websocket/notifications/mark-read', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notification_ids: notificationIds })
      });
      
      const data = await response.json();
      if (data.success) {
        // 로컬 상태 업데이트
        setNotifications(prev => 
          prev.map(n => 
            notificationIds.includes(n.id) 
              ? { ...n, read: true, read_at: new Date().toISOString() }
              : n
          )
        );
      }
    } catch (error) {
      console.error('알림 읽음 처리 실패:', error);
    }
  }, []);

  // 모든 알림 읽음 처리
  const markAllNotificationsRead = useCallback(async () => {
    try {
      const response = await fetch('/api/websocket/notifications/mark-read', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mark_all: true })
      });
      
      const data = await response.json();
      if (data.success) {
        setNotifications(prev => 
          prev.map(n => ({ ...n, read: true, read_at: new Date().toISOString() }))
        );
      }
    } catch (error) {
      console.error('모든 알림 읽음 처리 실패:', error);
    }
  }, []);

  // 컴포넌트 마운트 시 연결
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  // 주기적 핑 전송
  useEffect(() => {
    if (!status.connected) return;

    const pingInterval = setInterval(ping, 30000); // 30초마다 핑

    return () => clearInterval(pingInterval);
  }, [status.connected, ping]);

  return {
    // 상태
    status,
    notifications,
    stats,
    
    // 연결 관리
    connect,
    disconnect,
    
    // 룸 관리
    joinRoom,
    leaveRoom,
    
    // 알림 관리
    subscribeNotifications,
    unsubscribeNotifications,
    markNotificationRead,
    markNotificationsRead,
    markAllNotificationsRead,
    
    // 데이터 조회
    fetchNotificationStats,
    fetchNotificationHistory,
    
    // 유틸리티
    ping
  };
};

// 특정 기능별 WebSocket 훅들
export const useClockInOutWebSocket = (user_id: string) => {
  const { isConnected, sendMessage, lastMessage, error } = useWebSocket({
    url: 'ws://localhost:8765',
    user_id,
    user_type: 'employee'
  });

  const clockIn = useCallback(() => {
    sendMessage({
      type: 'clock_in',
      user_id,
      timestamp: new Date().toISOString()
    });
  }, [sendMessage, user_id]);

  const clockOut = useCallback(() => {
    sendMessage({
      type: 'clock_out',
      user_id,
      timestamp: new Date().toISOString()
    });
  }, [sendMessage, user_id]);

  return {
    isConnected,
    clockIn,
    clockOut,
    lastMessage,
    error
  };
};

export const useAdminWebSocket = (user_id: string) => {
  const { isConnected, sendMessage, lastMessage, error } = useWebSocket({
    url: 'ws://localhost:8765',
    user_id,
    user_type: 'admin'
  });

  const sendNotification = useCallback((target_type: string, target_id: string, message: string) => {
    sendMessage({
      type: 'notification',
      target_type,
      target_id,
      message
    });
  }, [sendMessage]);

  const sendSystemAlert = useCallback((alert_type: string, message: string) => {
    sendMessage({
      type: 'system_alert',
      alert_type,
      message
    });
  }, [sendMessage]);

  const requestDashboardData = useCallback((dashboard_type: string) => {
    sendMessage({
      type: 'request_dashboard',
      dashboard_type
    });
  }, [sendMessage]);

  return {
    isConnected,
    sendNotification,
    sendSystemAlert,
    requestDashboardData,
    lastMessage,
    error
  };
};

export const useChatWebSocket = (user_id: string, room: string) => {
  const { isConnected, sendMessage, lastMessage, error } = useWebSocket({
    url: 'ws://localhost:8765',
    user_id,
    user_type: 'employee'
  });

  const joinRoom = useCallback(() => {
    sendMessage({
      type: 'join_room',
      room
    });
  }, [sendMessage, room]);

  const leaveRoom = useCallback(() => {
    sendMessage({
      type: 'leave_room',
      room
    });
  }, [sendMessage, room]);

  const sendChatMessage = useCallback((message: string) => {
    sendMessage({
      type: 'chat',
      room,
      user_id,
      message
    });
  }, [sendMessage, room, user_id]);

  return {
    isConnected,
    joinRoom,
    leaveRoom,
    sendChatMessage,
    lastMessage,
    error
  };
}; 