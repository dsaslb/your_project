import { io, Socket } from "socket.io-client";
import Constants from "expo-constants";

// Socket.IO 클라이언트 생성
const WS_URL = (Constants.expoConfig?.extra as any)?.wsUrl || "ws://localhost:5000";

export const socket: Socket = io(WS_URL, {
  transports: ['polling', 'websocket'], // 폴링을 먼저 시도
  autoConnect: false, // 수동 연결
  reconnection: false, // 자동 재연결 비활성화 (서버가 없을 때)
  timeout: 3000, // 짧은 타임아웃
  forceNew: true,
});

// 연결 상태 관리
export const socketEvents = {
  // 출퇴근 업데이트 구독
  subscribeToAttendanceUpdates(callback: (data: any) => void) {
    socket.on('attendance:update', callback);
    return () => socket.off('attendance:update', callback);
  },

  // 재고 업데이트 구독
  subscribeToInventoryUpdates(callback: (data: any) => void) {
    socket.on('inventory:update', callback);
    return () => socket.off('inventory:update', callback);
  },

  // 발주 생성 구독
  subscribeToPurchaseOrderUpdates(callback: (data: any) => void) {
    socket.on('po:created', callback);
    return () => socket.off('po:created', callback);
  },

  // 연결 상태 확인
  isConnected(): boolean {
    return socket.connected;
  },

  // 연결
  connect() {
    socket.connect();
  },

  // 연결 해제
  disconnect() {
    socket.disconnect();
  }
};

// 개별 함수들도 export (호환성을 위해)
export const subscribeToAttendanceUpdates = (callback: (data: any) => void) => {
  return socketEvents.subscribeToAttendanceUpdates(callback);
};

export const subscribeToInventoryUpdates = (callback: (data: any) => void) => {
  return socketEvents.subscribeToInventoryUpdates(callback);
};

export const subscribeToPurchaseOrderUpdates = (callback: (data: any) => void) => {
  return socketEvents.subscribeToPurchaseOrderUpdates(callback);
};

// 연결 이벤트 리스너
socket.on('connect', () => {
  console.log('Socket.IO 연결됨:', socket.id);
});

socket.on('disconnect', (reason) => {
  console.log('Socket.IO 연결 해제됨:', reason);
});

socket.on('connect_error', (error) => {
  console.error('Socket.IO 연결 오류:', error);
});

// 네트워크 상태에 따른 자동 연결 관리
let isConnected = false;

export const connectSocket = () => {
  if (!isConnected) {
    socket.connect();
    isConnected = true;
  }
};

export const disconnectSocket = () => {
  if (isConnected) {
    socket.disconnect();
    isConnected = false;
  }
};

// 서버 연결 상태 확인 후 연결 시도
const checkServerAndConnect = async () => {
  try {
    // 간단한 HTTP 요청으로 서버 상태 확인
    const response = await fetch(`${WS_URL.replace('ws://', 'http://').replace('wss://', 'https://')}/healthz`, {
      method: 'GET',
      timeout: 2000
    });
    if (response.ok) {
      connectSocket();
    }
  } catch (error) {
    console.warn('서버 연결 불가, Socket.IO 연결 건너뜀:', error);
  }
};

// 초기 연결 시도 (비동기)
checkServerAndConnect();

export default socket;