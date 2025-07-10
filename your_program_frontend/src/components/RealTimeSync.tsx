'use client';

import { useEffect, useRef } from 'react';
import useUserStore from '@/store/useUserStore';
import { useOrderStore } from '@/store/useOrderStore';

interface WebSocketMessage {
  type: string;
  action: string;
  data?: any;
  timestamp: string;
}

export default function RealTimeSync() {
  const { user, isAuthenticated, subscribeToChanges: subscribeToUserChanges } = useUserStore();
  const { 
    subscribeToChanges: subscribeToOrderChanges, 
    connectWebSocket: connectOrderWebSocket,
    disconnectWebSocket: disconnectOrderWebSocket 
  } = useOrderStore();
  
  const notificationWsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // 알림용 WebSocket 연결
  const connectNotificationWebSocket = () => {
    try {
      const ws = new WebSocket('ws://localhost:5001/notifications');
      
      ws.onopen = () => {
        console.log('알림 WebSocket 연결됨');
        // 사용자 인증 정보 전송
        if (user) {
          ws.send(JSON.stringify({
            type: 'auth',
            userId: user.id,
            role: user.role
          }));
        }
      };
      
      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          handleWebSocketMessage(message);
        } catch (error) {
          console.error('WebSocket 메시지 파싱 오류:', error);
        }
      };
      
      ws.onclose = () => {
        console.log('알림 WebSocket 연결 끊어짐');
        // 재연결 시도
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = setTimeout(() => {
          if (isAuthenticated) {
            connectNotificationWebSocket();
          }
        }, 5000);
      };
      
      ws.onerror = (error) => {
        console.error('알림 WebSocket 오류:', error);
      };
      
      notificationWsRef.current = ws;
      (window as any).notificationWebSocket = ws;
    } catch (error) {
      console.error('알림 WebSocket 연결 실패:', error);
    }
  };

  // WebSocket 메시지 처리
  const handleWebSocketMessage = (message: WebSocketMessage) => {
    switch (message.type) {
      case 'user_update':
        // 사용자 정보 업데이트
        console.log('사용자 정보 업데이트 수신:', message.data);
        break;
        
      case 'order_update':
        // 주문 정보 업데이트
        console.log('주문 정보 업데이트 수신:', message.data);
        break;
        
      case 'notification':
        // 새로운 알림
        console.log('새로운 알림 수신:', message.data);
        showNotification(message.data);
        break;
        
      case 'system_alert':
        // 시스템 알림
        console.log('시스템 알림 수신:', message.data);
        showSystemAlert(message.data);
        break;
        
      default:
        console.log('알 수 없는 메시지 타입:', message.type);
    }
  };

  // 브라우저 알림 표시
  const showNotification = (data: any) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(data.title || '새로운 알림', {
        body: data.message,
        icon: '/favicon.ico',
        tag: data.id || 'notification'
      });
    }
  };

  // 시스템 알림 표시
  const showSystemAlert = (data: any) => {
    // 토스트 알림 또는 모달로 표시
    console.log('시스템 알림:', data);
  };

  // 실시간 동기화 설정
  useEffect(() => {
    if (isAuthenticated && user) {
      // WebSocket 연결
      connectNotificationWebSocket();
      connectOrderWebSocket();
      
      // 사용자 상태 변경 구독
      const unsubscribeUser = subscribeToUserChanges((newState) => {
        console.log('사용자 상태 변경 감지 (RealTimeSync):', newState);
      });
      
      // 주문 상태 변경 구독
      const unsubscribeOrder = subscribeToOrderChanges((orders) => {
        console.log('주문 상태 변경 감지 (RealTimeSync):', orders.length);
      });
      
      // 브라우저 알림 권한 요청
      if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
      }
      
      return () => {
        unsubscribeUser();
        unsubscribeOrder();
        disconnectOrderWebSocket();
        
        if (notificationWsRef.current) {
          notificationWsRef.current.close();
          notificationWsRef.current = null;
        }
        
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
      };
    }
  }, [isAuthenticated, user, subscribeToUserChanges, subscribeToOrderChanges, connectOrderWebSocket, disconnectOrderWebSocket]);

  // 페이지 가시성 변경 감지 (탭 전환 시)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && isAuthenticated) {
        // 탭이 다시 활성화되면 WebSocket 재연결 시도
        if (!notificationWsRef.current || notificationWsRef.current.readyState !== WebSocket.OPEN) {
          connectNotificationWebSocket();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [isAuthenticated]);

  // 네트워크 상태 감지
  useEffect(() => {
    const handleOnline = () => {
      console.log('네트워크 연결 복구');
      if (isAuthenticated) {
        connectNotificationWebSocket();
        connectOrderWebSocket();
      }
    };

    const handleOffline = () => {
      console.log('네트워크 연결 끊어짐');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [isAuthenticated, connectOrderWebSocket]);

  // 컴포넌트는 UI를 렌더링하지 않음 (백그라운드 동작만)
  return null;
} 