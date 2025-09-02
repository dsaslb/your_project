import { useEffect, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

// 배지 타입 정의
interface BadgeCounts {
  purchaseOrders: number;
  attendance: number;
  inventory: number;
  schedule: number;
  orders: number;
}

// 이벤트 타입 정의
interface RealtimeEvent {
  type: string;
  industry_id: string;
  brand_id: string;
  branch_id: string;
  data: any;
}

export const useBadges = (currentBranchId?: string) => {
  const [badges, setBadges] = useState<BadgeCounts>({
    purchaseOrders: 0,
    attendance: 0,
    inventory: 0,
    schedule: 0,
    orders: 0
  });
  
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  // Socket.IO 연결 초기화
  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:5000';
    const newSocket = io(wsUrl, {
      transports: ['polling', 'websocket'],
      timeout: 10000,
      forceNew: true
    });

    // 연결 이벤트
    newSocket.on('connect', () => {
      console.log('✅ Socket.IO 연결 성공:', newSocket.id);
      setIsConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('❌ Socket.IO 연결 해제');
      setIsConnected(false);
    });

    // 실시간 이벤트 구독
    newSocket.on('po:created', (event: RealtimeEvent) => {
      console.log('📦 발주 생성 이벤트:', event);
      if (event.branch_id === currentBranchId) {
        handlePurchaseOrderEvent(event);
      }
    });

    newSocket.on('po:status', (event: RealtimeEvent) => {
      console.log('🔄 발주 상태 변경 이벤트:', event);
      if (event.branch_id === currentBranchId) {
        handlePurchaseOrderEvent(event);
      }
    });

    newSocket.on('attendance:update', (event: RealtimeEvent) => {
      console.log('👥 출근 이벤트:', event);
      if (event.branch_id === currentBranchId) {
        handleAttendanceEvent(event);
      }
    });

    newSocket.on('inventory:update', (event: RealtimeEvent) => {
      console.log('📦 재고 이벤트:', event);
      if (event.branch_id === currentBranchId) {
        handleInventoryEvent(event);
      }
    });

    newSocket.on('schedule:update', (event: RealtimeEvent) => {
      console.log('📅 일정 이벤트:', event);
      if (event.branch_id === currentBranchId) {
        handleScheduleEvent(event);
      }
    });

    newSocket.on('order:update', (event: RealtimeEvent) => {
      console.log('🛒 주문 이벤트:', event);
      if (event.branch_id === currentBranchId) {
        handleOrderEvent(event);
      }
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, [currentBranchId]);

  // 이벤트 핸들러들
  const handlePurchaseOrderEvent = useCallback((event: RealtimeEvent) => {
    setBadges(prev => ({
      ...prev,
      purchaseOrders: prev.purchaseOrders + 1
    }));

    // 2초 후 백그라운드에서 실제 데이터 재조회
    setTimeout(() => {
      refetchPurchaseOrderCount();
    }, 2000);
  }, []);

  const handleAttendanceEvent = useCallback((event: RealtimeEvent) => {
    setBadges(prev => ({
      ...prev,
      attendance: prev.attendance + 1
    }));

    setTimeout(() => {
      refetchAttendanceCount();
    }, 2000);
  }, []);

  const handleInventoryEvent = useCallback((event: RealtimeEvent) => {
    setBadges(prev => ({
      ...prev,
      inventory: prev.inventory + 1
    }));

    setTimeout(() => {
      refetchInventoryCount();
    }, 2000);
  }, []);

  const handleScheduleEvent = useCallback((event: RealtimeEvent) => {
    setBadges(prev => ({
      ...prev,
      schedule: prev.schedule + 1
    }));

    setTimeout(() => {
      refetchScheduleCount();
    }, 2000);
  }, []);

  const handleOrderEvent = useCallback((event: RealtimeEvent) => {
    setBadges(prev => ({
      ...prev,
      orders: prev.orders + 1
    }));

    setTimeout(() => {
      refetchOrderCount();
    }, 2000);
  }, []);

  // 직접 백엔드 API 호출 (CSP 정책 허용됨)
  const API_BASE_URL = 'http://localhost:5000';
  
  // 인증 토큰 가져오기
  const getAuthHeaders = (): Record<string, string> => {
    const token = localStorage.getItem('jwt_token') || localStorage.getItem('auth_token') || sessionStorage.getItem('jwt_token') || sessionStorage.getItem('auth_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  };
  
  // 백그라운드 재조회 함수들
  const refetchPurchaseOrderCount = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/purchase_orders?status=requested&countOnly=1`, {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.count !== undefined) {
        setBadges(prev => ({
          ...prev,
          purchaseOrders: data.count
        }));
        console.log('🔄 발주 수량 재조회 완료:', data.count);
      }
    } catch (error) {
      console.error('❌ 발주 수량 재조회 실패:', error);
      // 오류 발생 시 기본값 유지
    }
  }, []);

  const refetchAttendanceCount = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/attendance?countOnly=1`, {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.count !== undefined) {
        setBadges(prev => ({
          ...prev,
          attendance: data.count
        }));
        console.log('🔄 출근 수량 재조회 완료:', data.count);
      }
    } catch (error) {
      console.error('❌ 출근 수량 재조회 실패:', error);
      // 오류 발생 시 기본값 유지
    }
  }, []);

  const refetchInventoryCount = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/inventory?countOnly=1`, {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.count !== undefined) {
        setBadges(prev => ({
          ...prev,
          inventory: data.count
        }));
        console.log('🔄 재고 수량 재조회 완료:', data.count);
      }
    } catch (error) {
      console.error('❌ 재고 수량 재조회 실패:', error);
      // 오류 발생 시 기본값 유지
    }
  }, []);

  const refetchScheduleCount = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/schedule?countOnly=1`, {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.count !== undefined) {
        setBadges(prev => ({
          ...prev,
          schedule: data.count
        }));
        console.log('🔄 일정 수량 재조회 완료:', data.count);
      }
    } catch (error) {
      console.error('❌ 일정 수량 재조회 실패:', error);
    }
  }, []);

  const refetchOrderCount = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/orders?countOnly=1`, {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.count !== undefined) {
        setBadges(prev => ({
          ...prev,
          orders: data.count
        }));
        console.log('🔄 주문 수량 재조회 완료:', data.count);
      }
    } catch (error) {
      console.error('❌ 주문 수량 재조회 실패:', error);
    }
  }, []);

  // 초기 데이터 로드
  useEffect(() => {
    if (currentBranchId) {
      refetchPurchaseOrderCount();
      refetchAttendanceCount();
      refetchInventoryCount();
      refetchScheduleCount();
      refetchOrderCount();
    }
  }, [currentBranchId, refetchPurchaseOrderCount, refetchAttendanceCount, refetchInventoryCount, refetchScheduleCount, refetchOrderCount]);

  return {
    badges,
    isConnected,
    socket,
    refetchPurchaseOrderCount,
    refetchAttendanceCount,
    refetchInventoryCount,
    refetchScheduleCount,
    refetchOrderCount
  };
};
