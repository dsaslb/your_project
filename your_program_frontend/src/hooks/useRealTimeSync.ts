import { useEffect, useRef, useState } from 'react';
import { useGlobalStore } from '../store/useGlobalStore';

interface SyncOptions {
  autoSync: boolean;
  syncInterval: number; // milliseconds
  retryAttempts: number;
}

export const useRealTimeSync = (options: SyncOptions = {
  autoSync: true,
  syncInterval: 30000, // 30초
  retryAttempts: 3
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const retryCountRef = useRef(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const syncData = useGlobalStore((state) => state.syncData);
  const setOnline = useGlobalStore((state) => state.setOnline);

  // WebSocket 연결 설정
  const connectWebSocket = () => {
    try {
      // 환경 변수에서 WebSocket URL 가져오기
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:5000/ws';
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket 연결됨');
        setIsConnected(true);
        setOnline(true);
        setError(null);
        retryCountRef.current = 0;
      };

      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket 연결 끊어짐');
        setIsConnected(false);
        setOnline(false);
        handleReconnection();
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket 오류:', error);
        setError('연결 오류가 발생했습니다.');
      };
    } catch (err) {
      console.error('WebSocket 연결 실패:', err);
      setError('연결을 설정할 수 없습니다.');
    }
  };

  // WebSocket 메시지 처리
  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'data_update':
        // 데이터 업데이트 알림
        syncData();
        setLastSyncTime(new Date());
        break;
      case 'notification':
        // 실시간 알림
        console.log('새 알림:', data.message);
        break;
      case 'system_status':
        // 시스템 상태 업데이트
        console.log('시스템 상태:', data.status);
        break;
      default:
        console.log('알 수 없는 메시지 타입:', data.type);
    }
  };

  // 재연결 처리
  const handleReconnection = () => {
    if (retryCountRef.current < options.retryAttempts) {
      retryCountRef.current++;
      console.log(`재연결 시도 ${retryCountRef.current}/${options.retryAttempts}`);
      
      setTimeout(() => {
        connectWebSocket();
      }, 5000 * retryCountRef.current); // 지수 백오프
    } else {
      setError('최대 재연결 시도 횟수를 초과했습니다.');
    }
  };

  // 자동 동기화 설정
  useEffect(() => {
    if (options.autoSync) {
      intervalRef.current = setInterval(() => {
        if (isConnected) {
          syncData();
          setLastSyncTime(new Date());
        }
      }, options.syncInterval) as unknown as NodeJS.Timeout;
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isConnected, options.autoSync, options.syncInterval, syncData]);

  // WebSocket 연결/해제
  useEffect(() => {
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // 수동 동기화 함수
  const manualSync = () => {
    syncData();
    setLastSyncTime(new Date());
  };

  // WebSocket 메시지 전송
  const sendMessage = (type: string, data: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, data }));
    } else {
      console.warn('WebSocket이 연결되지 않았습니다.');
    }
  };

  return {
    isConnected,
    lastSyncTime,
    error,
    manualSync,
    sendMessage,
    reconnect: connectWebSocket
  };
}; 