import { useEffect, useState, useCallback } from 'react';
import { socketEvents } from '@/lib/socket';
import { toast } from 'sonner';

// 실시간 업데이트 타입 정의
interface AttendanceUpdate {
  type: 'in' | 'out';
  user_id: number;
  user_name: string;
  timestamp: string;
  location?: {
    lat: number;
    lng: number;
  };
}

interface InventoryUpdate {
  barcode: string;
  product_name: string;
  quantity: number;
  user_id: number;
  user_name: string;
  timestamp: string;
}

interface PurchaseOrderUpdate {
  order_id: string;
  branch_id: string;
  branch_name: string;
  user_id: number;
  user_name: string;
  total_amount: number;
  timestamp: string;
}

// 실시간 업데이트 상태 타입
interface RealtimeUpdatesState {
  attendanceUpdates: AttendanceUpdate[];
  inventoryUpdates: InventoryUpdate[];
  purchaseOrderUpdates: PurchaseOrderUpdate[];
  isConnected: boolean;
  lastUpdate: Date | null;
}

export function useRealtimeUpdates() {
  const [updates, setUpdates] = useState<RealtimeUpdatesState>({
    attendanceUpdates: [],
    inventoryUpdates: [],
    purchaseOrderUpdates: [],
    isConnected: false,
    lastUpdate: null,
  });

  // 출퇴근 업데이트 처리
  const handleAttendanceUpdate = useCallback((data: AttendanceUpdate) => {
    setUpdates(prev => ({
      ...prev,
      attendanceUpdates: [data, ...prev.attendanceUpdates.slice(0, 9)], // 최근 10개만 유지
      lastUpdate: new Date(),
    }));

    // 토스트 알림 표시
    toast.success(
      `${data.user_name}님이 ${data.type === 'in' ? '출근' : '퇴근'}했습니다.`,
      {
        description: new Date(data.timestamp).toLocaleString('ko-KR'),
        duration: 5000,
      }
    );
  }, []);

  // 재고 업데이트 처리
  const handleInventoryUpdate = useCallback((data: InventoryUpdate) => {
    setUpdates(prev => ({
      ...prev,
      inventoryUpdates: [data, ...prev.inventoryUpdates.slice(0, 9)], // 최근 10개만 유지
      lastUpdate: new Date(),
    }));

    // 토스트 알림 표시
    toast.info(
      `재고 조사 완료: ${data.product_name}`,
      {
        description: `${data.user_name}님이 수량 ${data.quantity}개로 조사했습니다.`,
        duration: 4000,
      }
    );
  }, []);

  // 발주 업데이트 처리
  const handlePurchaseOrderUpdate = useCallback((data: PurchaseOrderUpdate) => {
    setUpdates(prev => ({
      ...prev,
      purchaseOrderUpdates: [data, ...prev.purchaseOrderUpdates.slice(0, 9)], // 최근 10개만 유지
      lastUpdate: new Date(),
    }));

    // 토스트 알림 표시
    toast.warning(
      `새로운 발주 요청: ${data.branch_name}`,
      {
        description: `${data.user_name}님이 ${data.total_amount.toLocaleString()}원 발주를 요청했습니다.`,
        duration: 6000,
      }
    );
  }, []);

  // 연결 상태 업데이트
  const updateConnectionStatus = useCallback(() => {
    const isConnected = socketEvents.isConnected();
    setUpdates(prev => ({
      ...prev,
      isConnected,
    }));
  }, []);

  useEffect(() => {
    // SocketIO 이벤트 구독
    const unsubscribeAttendance = socketEvents.subscribeToAttendanceUpdates(handleAttendanceUpdate);
    const unsubscribeInventory = socketEvents.subscribeToInventoryUpdates(handleInventoryUpdate);
    const unsubscribePurchaseOrder = socketEvents.subscribeToPurchaseOrderUpdates(handlePurchaseOrderUpdate);

    // 연결 상태 주기적 확인
    const connectionInterval = setInterval(updateConnectionStatus, 5000);

    // 초기 연결 상태 확인
    updateConnectionStatus();

    // 정리 함수
    return () => {
      unsubscribeAttendance();
      unsubscribeInventory();
      unsubscribePurchaseOrder();
      clearInterval(connectionInterval);
    };
  }, [handleAttendanceUpdate, handleInventoryUpdate, handlePurchaseOrderUpdate, updateConnectionStatus]);

  // 수동으로 업데이트 초기화
  const clearUpdates = useCallback(() => {
    setUpdates(prev => ({
      ...prev,
      attendanceUpdates: [],
      inventoryUpdates: [],
      purchaseOrderUpdates: [],
      lastUpdate: null,
    }));
  }, []);

  // 특정 타입의 업데이트만 초기화
  const clearUpdatesByType = useCallback((type: 'attendance' | 'inventory' | 'purchaseOrder') => {
    setUpdates(prev => ({
      ...prev,
      [`${type}Updates`]: [],
    }));
  }, []);

  return {
    ...updates,
    clearUpdates,
    clearUpdatesByType,
    // 편의 함수들
    hasUpdates: updates.attendanceUpdates.length > 0 || 
                updates.inventoryUpdates.length > 0 || 
                updates.purchaseOrderUpdates.length > 0,
    totalUpdates: updates.attendanceUpdates.length + 
                  updates.inventoryUpdates.length + 
                  updates.purchaseOrderUpdates.length,
  };
}
