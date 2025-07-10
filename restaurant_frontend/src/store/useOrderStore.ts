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
      },
      
      removeOrder: async (id: number) => {
        set((state: OrderStore) => ({
          orders: state.orders.filter((order) => order.id !== id),
          syncStatus: 'pending',
        }));
        
        // 오프라인 데이터로 저장
        await offlineStorage.saveOfflineData('orders', 'delete', { id });
      },
      
      manualSync: async () => {
        await get().fetchOrders();
      },
      
      clearAll: () => set({ orders: [] }),
      setOffline: () => set({ syncStatus: 'offline' }),
    }),
    {
      name: 'order-store',
    }
  )
); 