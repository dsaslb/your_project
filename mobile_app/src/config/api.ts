// API 설정
export const API_CONFIG = {
  // 개발 환경 (로컬 IP 주소)
  BASE_URL: 'http://192.168.45.44:5000',
  WS_URL: 'ws://192.168.45.44:5000',
  
  // 프로덕션 환경 (실제 도메인)
  // BASE_URL: 'https://your-domain.com',
  // WS_URL: 'wss://your-domain.com',
  
  // API 엔드포인트
  ENDPOINTS: {
    LOGIN: '/api/mobile/login',
    PUSH_REGISTER: '/api/mobile/push/register',
    ATTENDANCE_CLOCK: '/api/mobile/attendance/clock',
    INVENTORY_CHECK: '/api/mobile/inventory/check',
    INVENTORY_HISTORY: '/api/mobile/inventory/history',
    PURCHASE_ORDERS: '/api/mobile/purchase_orders',
    SCHEDULE: '/api/mobile/schedule',
    SCHEDULE_LEAVE: '/api/mobile/schedule/leave',
    SCHEDULE_SWAP: '/api/mobile/schedule/swap',
    ORDER_STATUS: '/api/mobile/orders/update_status',
  },
  
  // JWT 설정
  JWT: {
    STORAGE_KEY: 'auth_token',
    EXPIRY_CHECK_INTERVAL: 5 * 60 * 1000, // 5분
  },
  
  // 소켓 설정
  SOCKET: {
    RECONNECTION_ATTEMPTS: 5,
    RECONNECTION_DELAY: 1000,
    TIMEOUT: 20000,
  },
  
  // 오프라인 설정
  OFFLINE: {
    MAX_RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 5000,
    QUEUE_STORAGE_KEY: 'offline_actions',
  },
};

// 환경별 설정
export const getApiConfig = () => {
  const isDevelopment = __DEV__;
  
  if (isDevelopment) {
    return {
      baseURL: API_CONFIG.BASE_URL,
      wsURL: API_CONFIG.WS_URL,
      timeout: 10000,
      debug: true,
    };
  }
  
  return {
    baseURL: API_CONFIG.BASE_URL,
    wsURL: API_CONFIG.WS_URL,
    timeout: 30000,
    debug: false,
  };
};
