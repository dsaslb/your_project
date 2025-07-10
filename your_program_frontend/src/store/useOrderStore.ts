import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { offlineStorage } from '../utils/offlineStorage';

export type Order = {
  id: number;
  orderNumber: string;
  customerName: string;
  items: OrderItem[];
  totalAmount: number;
  status: 'pending' | 'confirmed' | 'preparing' | 'ready' | 'delivered' | 'cancelled';
  branchId: number;
  createdAt: string;
  updatedAt: string;
};

export type OrderItem = {
  id: number;
  productName: string;
  quantity: number;
  price: number;
  notes?: string;
};

export type SyncStatus = 'synced' | 'pending' | 'offline' | 'error';

interface OrderStore {
  orders: Order[];
  syncStatus: SyncStatus;
  lastSync: string | null;
  fetchOrders: () => Promise<void>;
  addOrder: (order: Omit<Order, 'id' | 'createdAt' | 'updatedAt'>) => void;
  updateOrder: (id: number, updates: Partial<Order>) => void;
  removeOrder: (id: number) => void;
  clearAll: () => void;
  manualSync: () => Promise<void>;
  setOffline: () => void;
  
  // 실시간 동기화 관련
  subscribeToChanges: (callback: (orders: Order[]) => void) => () => void;
  broadcastChange: (action: string, data?: any) => void;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
}

export const useOrderStore = create<OrderStore>()(
  persist(
    (set, get) => ({
      orders: [],
      syncStatus: 'synced',
      lastSync: null,
      
      fetchOrders: async () => {
        try {
          set({ syncStatus: 'pending' });
          const res = await fetch('/api/orders');
          if (!res.ok) throw new Error('API 오류');
          const data: Order[] = await res.json();
          set({ orders: data, syncStatus: 'synced', lastSync: new Date().toISOString() });
          
          // 캐시에 저장
          await offlineStorage.saveCachedData('orders', 'orders', data);
          
          // 실시간 동기화: 데이터 로드 완료 브로드캐스트
          get().broadcastChange('orders_loaded', { count: data.length, timestamp: new Date().toISOString() });
        } catch (e: unknown) {
          set({ syncStatus: 'offline' });
          // 오프라인 시 캐시된 데이터 사용
          const cachedData = await offlineStorage.getCachedData('orders');
          if (cachedData) {
            set({ orders: cachedData });
          }
        }
      },
      
      addOrder: async (order) => {
        const newOrder: Order = {
          ...order,
          id: Date.now(),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        
        set((state: OrderStore) => ({
          orders: [...state.orders, newOrder],
          syncStatus: 'pending',
        }));
        
        // 오프라인 데이터로 저장
        await offlineStorage.saveOfflineData('orders', 'create', newOrder);
        
        // 실시간 동기화: 주문 추가 브로드캐스트
        get().broadcastChange('order_added', { order: newOrder, timestamp: new Date().toISOString() });
      },
      
      updateOrder: async (id: number, updates: Partial<Order>) => {
        set((state: OrderStore) => ({
          orders: state.orders.map((order) =>
            order.id === id ? { ...order, ...updates, updatedAt: new Date().toISOString() } : order
          ),
          syncStatus: 'pending',
        }));
        
        // 오프라인 데이터로 저장
        await offlineStorage.saveOfflineData('orders', 'update', { id, ...updates });
        
        // 실시간 동기화: 주문 업데이트 브로드캐스트
        get().broadcastChange('order_updated', { id, updates, timestamp: new Date().toISOString() });
      },
      
      removeOrder: async (id: number) => {
        set((state: OrderStore) => ({
          orders: state.orders.filter((order) => order.id !== id),
          syncStatus: 'pending',
        }));
        
        // 오프라인 데이터로 저장
        await offlineStorage.saveOfflineData('orders', 'delete', { id });
        
        // 실시간 동기화: 주문 삭제 브로드캐스트
        get().broadcastChange('order_removed', { id, timestamp: new Date().toISOString() });
      },
      
      manualSync: async () => {
        await get().fetchOrders();
      },
      
      clearAll: () => set({ orders: [] }),
      setOffline: () => set({ syncStatus: 'offline' }),
      
      // 실시간 동기화: 구독자 관리
      subscribeToChanges: (callback: (orders: Order[]) => void) => {
        // localStorage 이벤트 리스너로 다른 탭의 변경사항 감지
        const handleStorageChange = (e: StorageEvent) => {
          if (e.key === 'order-store') {
            try {
              const newState = JSON.parse(e.newValue || '{}');
              if (newState.orders) {
                callback(newState.orders);
              }
            } catch (error) {
              console.error('Order store state 파싱 오류:', error);
            }
          }
        };
        
        // 브로드캐스트 이벤트 리스너
        const handleBroadcast = (e: StorageEvent) => {
          if (e.key === 'order-store-broadcast') {
            try {
              const broadcastData = JSON.parse(e.newValue || '{}');
              if (broadcastData.action === 'order_added') {
                set((state: OrderStore) => ({
                  orders: [...state.orders, broadcastData.data.order]
                }));
              } else if (broadcastData.action === 'order_updated') {
                set((state: OrderStore) => ({
                  orders: state.orders.map(order => 
                    order.id === broadcastData.data.id 
                      ? { ...order, ...broadcastData.data.updates }
                      : order
                  )
                }));
              } else if (broadcastData.action === 'order_removed') {
                set((state: OrderStore) => ({
                  orders: state.orders.filter(order => order.id !== broadcastData.data.id)
                }));
              }
            } catch (error) {
              console.error('Order broadcast 파싱 오류:', error);
            }
          }
        };
        
        window.addEventListener('storage', handleStorageChange);
        window.addEventListener('storage', handleBroadcast);
        
        // 구독 해제 함수 반환
        return () => {
          window.removeEventListener('storage', handleStorageChange);
          window.removeEventListener('storage', handleBroadcast);
        };
      },
      
      // 실시간 동기화: 변경사항 브로드캐스트
      broadcastChange: (action: string, data?: any) => {
        const currentState = get();
        const broadcastData = {
          action,
          data,
          timestamp: new Date().toISOString()
        };
        
        // localStorage를 통한 다른 탭에 브로드캐스트
        localStorage.setItem('order-store-broadcast', JSON.stringify(broadcastData));
        localStorage.removeItem('order-store-broadcast'); // 즉시 제거하여 중복 방지
        
        // WebSocket을 통한 실시간 브로드캐스트
        if (typeof window !== 'undefined' && (window as any).orderWebSocket) {
          try {
            (window as any).orderWebSocket.send(JSON.stringify({
              type: 'order_update',
              ...broadcastData
            }));
          } catch (error) {
            console.warn('Order WebSocket 브로드캐스트 실패:', error);
          }
        }
      },
      
      // WebSocket 연결
      connectWebSocket: () => {
        try {
          const ws = new WebSocket('ws://localhost:5001/orders');
          
          ws.onopen = () => {
            console.log('Order WebSocket 연결됨');
          };
          
          ws.onmessage = (event) => {
            try {
              const data = JSON.parse(event.data);
              if (data.type === 'order_update') {
                // 서버에서 받은 주문 업데이트를 store에 반영
                if (data.action === 'order_added') {
                  set((state: OrderStore) => ({
                    orders: [...state.orders, data.data.order]
                  }));
                } else if (data.action === 'order_updated') {
                  set((state: OrderStore) => ({
                    orders: state.orders.map(order => 
                      order.id === data.data.id 
                        ? { ...order, ...data.data.updates }
                        : order
                    )
                  }));
                } else if (data.action === 'order_removed') {
                  set((state: OrderStore) => ({
                    orders: state.orders.filter(order => order.id !== data.data.id)
                  }));
                }
              }
            } catch (error) {
              console.error('Order WebSocket 데이터 파싱 오류:', error);
            }
          };
          
          ws.onclose = () => {
            console.log('Order WebSocket 연결 끊어짐');
            // 재연결 시도
            setTimeout(() => {
              get().connectWebSocket();
            }, 5000);
          };
          
          ws.onerror = (error) => {
            console.error('Order WebSocket 오류:', error);
          };
          
          // WebSocket 인스턴스를 저장
          (window as any).orderWebSocket = ws;
        } catch (error) {
          console.error('Order WebSocket 연결 실패:', error);
        }
      },
      
      disconnectWebSocket: () => {
        const ws = (window as any).orderWebSocket;
        if (ws) {
          ws.close();
          (window as any).orderWebSocket = null;
        }
      },
    }),
    {
      name: 'order-store',
    }
  )
); 