import { useEffect, useRef, useState, useCallback } from 'react';

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

interface WebSocketHookOptions {
  url: string;
  user_id?: string;
  user_type?: string;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

interface WebSocketHookReturn {
  isConnected: boolean;
  sendMessage: (message: WebSocketMessage) => void;
  lastMessage: WebSocketMessage | null;
  error: string | null;
  connect: () => void;
  disconnect: () => void;
}

export const useWebSocket = ({
  url,
  user_id = 'anonymous',
  user_type = 'guest',
  autoReconnect = true,
  reconnectInterval = 3000,
  maxReconnectAttempts = 5
}: WebSocketHookOptions): WebSocketHookReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
        
        // 인증 메시지 전송
        ws.send(JSON.stringify({
          user_id,
          user_type
        }));
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          
          // 메시지 타입별 처리
          handleMessage(message);
        } catch (err) {
          console.error('WebSocket 메시지 파싱 오류:', err);
        }
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        
        if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(`WebSocket 재연결 시도 ${reconnectAttemptsRef.current}/${maxReconnectAttempts}`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setError('최대 재연결 시도 횟수를 초과했습니다.');
        }
      };

      ws.onerror = (event) => {
        setError('WebSocket 연결 오류가 발생했습니다.');
        console.error('WebSocket 오류:', event);
      };

    } catch (err) {
      setError('WebSocket 연결을 생성할 수 없습니다.');
      console.error('WebSocket 연결 오류:', err);
    }
  }, [url, user_id, user_type, autoReconnect, reconnectInterval, maxReconnectAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
    reconnectAttemptsRef.current = 0;
  }, []);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      setError('WebSocket이 연결되지 않았습니다.');
    }
  }, []);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'welcome':
        console.log('WebSocket 서버에 연결되었습니다:', message.message);
        break;
        
      case 'clock_event':
        console.log('출근/퇴근 이벤트:', message);
        // 출근/퇴근 알림 처리
        break;
        
      case 'schedule_update':
        console.log('스케줄 업데이트:', message);
        // 스케줄 업데이트 처리
        break;
        
      case 'notification':
        console.log('알림:', message);
        // 일반 알림 처리
        break;
        
      case 'system_alert':
        console.log('시스템 알림:', message);
        // 시스템 알림 처리
        break;
        
      case 'dashboard_update':
        console.log('대시보드 업데이트:', message);
        // 대시보드 업데이트 처리
        break;

      case 'order_update':
        console.log('주문 업데이트:', message);
        // 주문 상태 변경 처리
        break;

      case 'inventory_alert':
        console.log('재고 알림:', message);
        // 재고 부족/초과 알림 처리
        break;

      case 'customer_feedback':
        console.log('고객 피드백:', message);
        // 고객 피드백 처리
        break;

      case 'store_status':
        console.log('매장 상태:', message);
        // 매장 운영 상태 처리
        break;

      case 'employee_activity':
        console.log('직원 활동:', message);
        // 직원 활동 로그 처리
        break;

      case 'sales_report':
        console.log('매출 리포트:', message);
        // 매출 데이터 처리
        break;
        
      case 'pong':
        console.log('핑 응답:', message);
        break;
        
      case 'error':
        console.error('서버 오류:', message.message);
        setError(message.message);
        break;
        
      default:
        console.log('알 수 없는 메시지 타입:', message.type);
    }
  }, []);

  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    sendMessage,
    lastMessage,
    error,
    connect,
    disconnect
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