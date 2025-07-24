'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';

interface WebSocketContextType {
  isConnected: boolean;
  sendMessage: (message: any) => void;
}

const WebSocketContext = createContext<WebSocketContextType>({
  isConnected: false,
  sendMessage: () => {},
});

export const useWebSocket = () => useContext(WebSocketContext);

interface WebSocketProviderProps {
  children: React.ReactNode;
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    // 개발 환경에서는 WebSocket 연결을 비활성화
    if (process.env.NODE_ENV === 'development') {
      console.log('개발 환경: WebSocket 연결 비활성화');
      return;
    }

    // 프로덕션 환경에서만 WebSocket 연결
    const connectWebSocket = () => {
      try {
        const websocket = new WebSocket('wss://yourserver/ws');
        
        websocket.onopen = () => {
          console.log('WebSocket 연결됨');
          setIsConnected(true);
        };

        websocket.onclose = () => {
          console.log('WebSocket 연결 끊어짐');
          setIsConnected(false);
          // 재연결 시도
          setTimeout(connectWebSocket, 5000);
        };

        websocket.onerror = (error) => {
          console.error('WebSocket 오류:', error);
          setIsConnected(false);
        };

        setWs(websocket);
      } catch (error) {
        console.error('WebSocket 연결 실패:', error);
        setIsConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const sendMessage = (message: any) => {
    if (ws && isConnected) {
      ws.send(JSON.stringify(message));
    }
  };

  return (
    <WebSocketContext.Provider value={{ isConnected, sendMessage }}>
      {children}
    </WebSocketContext.Provider>
  );
} 