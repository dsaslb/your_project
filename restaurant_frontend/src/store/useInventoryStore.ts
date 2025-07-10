import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { offlineStorage } from '../utils/offlineStorage';

export type InventoryItem = {
  id: number;
  name: string;
  category: string;
  currentStock: number;
  minStock: number;
  maxStock: number;
  unit: string;
  price: number;
  supplier: string;
  lastUpdated: string;
  branchId: number;
  status: 'normal' | 'low' | 'out' | 'overstock';
};

export type SyncStatus = 'synced' | 'pending' | 'offline' | 'error';

interface InventoryStore {
  items: InventoryItem[];
  syncStatus: SyncStatus;
  lastSync: string | null;
  fetchInventory: () => Promise<void>;
  addItem: (item: Omit<InventoryItem, 'id' | 'lastUpdated' | 'status'>) => void;
  updateItem: (id: number, updates: Partial<InventoryItem>) => void;
  removeItem: (id: number) => void;
  updateStock: (id: number, newStock: number) => void;
  getLowStockItems: () => InventoryItem[];
  getOutOfStockItems: () => InventoryItem[];
  clearAll: () => void;
  manualSync: () => Promise<void>;
  setOffline: () => void;
}

export const useInventoryStore = create<InventoryStore>()(
  persist(
    (set, get) => ({
      items: [],
      syncStatus: 'synced',
      lastSync: null,
      
      fetchInventory: async () => {
        try {
          set({ syncStatus: 'pending' });
          const res = await fetch('/api/inventory');
          if (!res.ok) throw new Error('API 오류');
          const data: InventoryItem[] = await res.json();
          set({ items: data, syncStatus: 'synced', lastSync: new Date().toISOString() });
          
          // 캐시에 저장
          await offlineStorage.saveCachedData('inventory', 'inventory', data);
        } catch (e: unknown) {
          set({ syncStatus: 'offline' });
          // 오프라인 시 캐시된 데이터 사용
          const cachedData = await offlineStorage.getCachedData('inventory');
          if (cachedData) {
            set({ items: cachedData });
          }
        }
      },
      
      addItem: async (item) => {
        const newItem: InventoryItem = {
          ...item,
          id: Date.now(),
          lastUpdated: new Date().toISOString(),
          status: item.currentStock <= item.minStock ? 'low' : 
                  item.currentStock === 0 ? 'out' : 
                  item.currentStock > item.maxStock ? 'overstock' : 'normal',
        };
        
        set((state: InventoryStore) => ({
          items: [...state.items, newItem],
          syncStatus: 'pending',
        }));
        
        // 오프라인 데이터로 저장
        await offlineStorage.saveOfflineData('inventory', 'create', newItem);
      },
      
      updateItem: async (id: number, updates: Partial<InventoryItem>) => {
        set((state: InventoryStore) => ({
          items: state.items.map((item) =>
            item.id === id ? { 
              ...item, 
              ...updates, 
              lastUpdated: new Date().toISOString(),
              status: updates.currentStock !== undefined ? 
                (updates.currentStock <= item.minStock ? 'low' : 
                 updates.currentStock === 0 ? 'out' : 
                 updates.currentStock > item.maxStock ? 'overstock' : 'normal') : 
                item.status
            } : item
          ),
          syncStatus: 'pending',
        }));
        
        // 오프라인 데이터로 저장
        await offlineStorage.saveOfflineData('inventory', 'update', { id, ...updates });
      },
      
      removeItem: async (id: number) => {
        set((state: InventoryStore) => ({
          items: state.items.filter((item) => item.id !== id),
          syncStatus: 'pending',
        }));
        
        // 오프라인 데이터로 저장
        await offlineStorage.saveOfflineData('inventory', 'delete', { id });
      },
      
      updateStock: async (id: number, newStock: number) => {
        const item = get().items.find(item => item.id === id);
        if (!item) return;
        
        const status = newStock <= item.minStock ? 'low' : 
                      newStock === 0 ? 'out' : 
                      newStock > item.maxStock ? 'overstock' : 'normal';
        
        await get().updateItem(id, { 
          currentStock: newStock, 
          status,
          lastUpdated: new Date().toISOString()
        });
      },

      getLowStockItems: () => {
        return get().items.filter(item => item.status === 'low');
      },
      
      getOutOfStockItems: () => {
        return get().items.filter(item => item.status === 'out');
      },
      
      manualSync: async () => {
        await get().fetchInventory();
      },
      
      clearAll: () => set({ items: [] }),
      setOffline: () => set({ syncStatus: 'offline' }),
    }),
    {
      name: 'inventory-store',
    }
  )
); 