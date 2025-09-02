/**
 * 🌍 환경 변수 설정
 * 
 * 모바일 앱에서 사용하는 환경 변수들
 */

// API 기본 URL
export const API_BASE_URL = "http://192.168.0.5:5000";

// WebSocket URL
export const WS_URL = "ws://192.168.0.5:5000";

// 개발용 (로컬)
// export const API_BASE_URL = "http://localhost:5000";
// export const WS_URL = "ws://localhost:5000";

// 앱 설정
export const APP_CONFIG = {
  API_TIMEOUT: 10000, // 10초
  MAX_RETRIES: 3,
  PUSH_TOKEN_EXPIRY: 24 * 60 * 60 * 1000, // 24시간
};

// API 엔드포인트
export const API_ENDPOINTS = {
  LOGIN: "/api/mobile/login",
  PUSH_REGISTER: "/api/mobile/push/register",
  ATTENDANCE_CLOCK: "/api/mobile/attendance/clock",
  INVENTORY_CHECK: "/api/mobile/inventory/check",
  PURCHASE_ORDERS: "/api/mobile/purchase_orders",
  SCHEDULE: "/api/mobile/schedule",
  ORDERS_UPDATE_STATUS: "/api/mobile/orders/update_status",
  DASHBOARD: "/api/mobile/dashboard",
};

// Socket.IO 이벤트
export const SOCKET_EVENTS = {
  ATTENDANCE_UPDATE: "attendance:update",
  INVENTORY_UPDATE: "inventory:update",
  PURCHASE_ORDER_UPDATE: "purchase_order:update",
  ORDER_UPDATE: "order:update",
  SCHEDULE_UPDATE: "schedule:update",
};
