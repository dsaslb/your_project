/**
 * 🔌 Socket.IO 클라이언트
 * 
 * 모바일 앱에서 실시간 통신을 위한 Socket.IO 클라이언트
 */

import { io, Socket } from "socket.io-client";
import { WS_URL, SOCKET_EVENTS } from '../config/env';

// Socket.IO 클라이언트 인스턴스
let socket: Socket | null = null;

/**
 * Socket.IO 연결 초기화
 */
export function initSocket(): Socket {
  if (!socket) {
    socket = io(WS_URL, {
      transports: ["websocket"],
      autoConnect: true,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    });

    // 연결 이벤트 리스너
    socket.on("connect", () => {
      console.log("🔌 Socket.IO 연결됨:", socket?.id);
    });

    socket.on("disconnect", () => {
      console.log("🔌 Socket.IO 연결 해제됨");
    });

    socket.on("connect_error", (error) => {
      console.error("🔌 Socket.IO 연결 오류:", error);
    });

    socket.on("reconnect", (attemptNumber) => {
      console.log("🔌 Socket.IO 재연결됨 (시도:", attemptNumber, ")");
    });
  }

  return socket;
}

/**
 * Socket.IO 인스턴스 가져오기
 */
export function getSocket(): Socket | null {
  return socket;
}

/**
 * Socket.IO 연결 해제
 */
export function disconnectSocket(): void {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
}

/**
 * 실시간 이벤트 구독 훅
 */
export function useRealtime<T = any>(
  eventName: string,
  callback: (data: T) => void
): () => void {
  const socket = getSocket();
  
  if (socket) {
    socket.on(eventName, callback);
    
    // 이벤트 리스너 제거 함수 반환
    return () => {
      socket.off(eventName, callback);
    };
  }
  
  return () => {};
}

/**
 * 출퇴근 업데이트 구독
 */
export function subscribeToAttendanceUpdates(callback: (data: any) => void): () => void {
  const socket = getSocket();
  
  if (socket) {
    socket.on(SOCKET_EVENTS.ATTENDANCE_UPDATE, callback);
    return () => socket.off(SOCKET_EVENTS.ATTENDANCE_UPDATE, callback);
  }
  
  return () => {};
}

/**
 * 재고 업데이트 구독
 */
export function subscribeToInventoryUpdates(callback: (data: any) => void): () => void {
  const socket = getSocket();
  
  if (socket) {
    socket.on(SOCKET_EVENTS.INVENTORY_UPDATE, callback);
    return () => socket.off(SOCKET_EVENTS.INVENTORY_UPDATE, callback);
  }
  
  return () => {};
}

/**
 * 발주 업데이트 구독
 */
export function subscribeToPurchaseOrderUpdates(callback: (data: any) => void): () => void {
  const socket = getSocket();
  
  if (socket) {
    socket.on(SOCKET_EVENTS.PURCHASE_ORDER_UPDATE, callback);
    return () => socket.off(SOCKET_EVENTS.PURCHASE_ORDER_UPDATE, callback);
  }
  
  return () => {};
}

/**
 * 주문 업데이트 구독
 */
export function subscribeToOrderUpdates(callback: (data: any) => void): () => void {
  const socket = getSocket();
  
  if (socket) {
    socket.on(SOCKET_EVENTS.ORDER_UPDATE, callback);
    return () => socket.off(SOCKET_EVENTS.ORDER_UPDATE, callback);
  }
  
  return () => {};
}

/**
 * 스케줄 업데이트 구독
 */
export function subscribeToScheduleUpdates(callback: (data: any) => void): () => void {
  const socket = getSocket();
  
  if (socket) {
    socket.on(SOCKET_EVENTS.SCHEDULE_UPDATE, callback);
    return () => socket.off(SOCKET_EVENTS.SCHEDULE_UPDATE, callback);
  }
  
  return () => {};
}

// 기본 export
export default {
  initSocket,
  getSocket,
  disconnectSocket,
  useRealtime,
  subscribeToAttendanceUpdates,
  subscribeToInventoryUpdates,
  subscribeToPurchaseOrderUpdates,
  subscribeToOrderUpdates,
  subscribeToScheduleUpdates,
};
