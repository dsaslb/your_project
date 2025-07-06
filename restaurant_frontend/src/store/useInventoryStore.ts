import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface InventoryItem {
  id: number;
  name: string;
  category: string;
  current_stock: number;
  min_stock: number;
  max_stock: number;
  unit: string;
  unit_price: number;
  supplier: string;
  description: string;
  expiry_date?: string;
  location: string;
  status: string;
  created_at: string;
  updated_at: string;
  branch_id: number;
}

export interface StockMovement {
  id: number;
  inventory_item_id: number;
  movement_type: 'in' | 'out' | 'adjustment';
  quantity: number;
  reason: string;
  created_by: number;
  created_at: string;
}

interface InventoryStore {
  // 상태
  inventoryItems: InventoryItem[];
  stockMovements: StockMovement[];
  loading: boolean;
  error: string | null;

  // 액션
  setInventoryItems: (items: InventoryItem[]) => void;
  setStockMovements: (movements: StockMovement[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // 재고 관리
  addInventoryItem: (item: InventoryItem) => void;
  updateInventoryItem: (id: number, updates: Partial<InventoryItem>) => void;
  deleteInventoryItem: (id: number) => void;
  updateStock: (itemId: number, quantity: number, type: 'in' | 'out' | 'adjustment', reason: string) => void;
  
  // API 호출
  fetchInventory: () => Promise<void>;
  fetchStockMovements: () => Promise<void>;
  createInventoryItem: (itemData: Partial<InventoryItem>) => Promise<boolean>;
  updateInventoryItemAPI: (id: number, itemData: Partial<InventoryItem>) => Promise<boolean>;
  deleteInventoryItemAPI: (id: number) => Promise<boolean>;
  
  // 유틸리티
  getInventoryByCategory: (category: string) => InventoryItem[];
  getInventoryById: (id: number) => InventoryItem | undefined;
  getLowStockItems: () => InventoryItem[];
  getOverStockItems: () => InventoryItem[];
  getStockMovementsByItem: (itemId: number) => StockMovement[];
  getStockMovementsByDateRange: (startDate: string, endDate: string) => StockMovement[];
}

// 더미 데이터 (API 실패 시 사용)
const getDummyInventoryData = (): InventoryItem[] => [
  {
    id: 1,
    name: "소고기",
    category: "육류",
    current_stock: 25,
    min_stock: 10,
    max_stock: 100,
    unit: "kg",
    unit_price: 45000,
    supplier: "한우공급업체",
    description: "한우 등급 소고기",
    location: "냉동고 A",
    status: "active",
    created_at: "2024-01-15T10:00:00Z",
    updated_at: "2024-01-16T14:30:00Z",
    branch_id: 1
  },
  {
    id: 2,
    name: "양파",
    category: "채소",
    current_stock: 80,
    min_stock: 20,
    max_stock: 200,
    unit: "kg",
    unit_price: 3000,
    supplier: "채소공급업체",
    description: "신선한 양파",
    location: "야채보관실",
    status: "active",
    created_at: "2024-01-16T14:30:00Z",
    updated_at: "2024-01-16T14:30:00Z",
    branch_id: 1
  },
  {
    id: 3,
    name: "고추장",
    category: "조미료",
    current_stock: 15,
    min_stock: 5,
    max_stock: 50,
    unit: "kg",
    unit_price: 12000,
    supplier: "조미료공급업체",
    description: "전통 고추장",
    location: "조미료보관실",
    status: "active",
    created_at: "2024-01-17T09:15:00Z",
    updated_at: "2024-01-17T09:15:00Z",
    branch_id: 1
  },
  {
    id: 4,
    name: "김치",
    category: "반찬",
    current_stock: 8,
    min_stock: 10,
    max_stock: 30,
    unit: "kg",
    unit_price: 8000,
    supplier: "김치공급업체",
    description: "맛김치",
    location: "냉장고 B",
    status: "active",
    created_at: "2024-01-18T16:45:00Z",
    updated_at: "2024-01-18T16:45:00Z",
    branch_id: 1
  }
];

const getDummyStockMovements = (): StockMovement[] => [
  {
    id: 1,
    inventory_item_id: 1,
    movement_type: "in",
    quantity: 50,
    reason: "발주 입고 (발주번호: 1)",
    created_by: 1,
    created_at: "2024-01-16T14:30:00Z"
  },
  {
    id: 2,
    inventory_item_id: 1,
    movement_type: "out",
    quantity: 25,
    reason: "주문 처리",
    created_by: 2,
    created_at: "2024-01-17T10:00:00Z"
  },
  {
    id: 3,
    inventory_item_id: 2,
    movement_type: "in",
    quantity: 100,
    reason: "발주 입고 (발주번호: 2)",
    created_by: 1,
    created_at: "2024-01-17T11:00:00Z"
  }
];

export const useInventoryStore = create<InventoryStore>()(
  devtools(
    (set, get) => ({
      // 초기 상태
      inventoryItems: [],
      stockMovements: [],
      loading: false,
      error: null,

      // 상태 설정
      setInventoryItems: (items) => set({ inventoryItems: items }),
      setStockMovements: (movements) => set({ stockMovements: movements }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),

      // 재고 관리
      addInventoryItem: (item) => set((state) => ({
        inventoryItems: [...state.inventoryItems, item]
      })),

      updateInventoryItem: (id, updates) => set((state) => ({
        inventoryItems: state.inventoryItems.map(item =>
          item.id === id ? { ...item, ...updates, updated_at: new Date().toISOString() } : item
        )
      })),

      deleteInventoryItem: (id) => set((state) => ({
        inventoryItems: state.inventoryItems.filter(item => item.id !== id)
      })),

      updateStock: (itemId, quantity, type, reason) => {
        const { inventoryItems, stockMovements } = get();
        const item = inventoryItems.find(i => i.id === itemId);
        
        if (!item) return;

        let newStock = item.current_stock;
        if (type === 'in') {
          newStock += quantity;
        } else if (type === 'out') {
          newStock -= quantity;
        } else if (type === 'adjustment') {
          newStock = quantity;
        }

        // 재고 아이템 업데이트
        set((state) => ({
          inventoryItems: state.inventoryItems.map(i =>
            i.id === itemId ? { ...i, current_stock: newStock, updated_at: new Date().toISOString() } : i
          )
        }));

        // 재고 변동 이력 추가
        const newMovement: StockMovement = {
          id: Date.now(),
          inventory_item_id: itemId,
          movement_type: type,
          quantity: quantity,
          reason: reason,
          created_by: 1, // TODO: 실제 사용자 ID로 변경
          created_at: new Date().toISOString()
        };

        set((state) => ({
          stockMovements: [...state.stockMovements, newMovement]
        }));
      },

      // API 호출
      fetchInventory: async () => {
        set({ loading: true, error: null });
        try {
          const response = await fetch('/api/inventory', {
            credentials: 'include'
          });
          const data = await response.json();
          
          if (data.success) {
            set({ inventoryItems: data.data, loading: false });
            console.log('재고 데이터 로드 성공:', data.data.length, '건');
          } else {
            console.error('재고 목록 로드 실패:', data.error);
            set({ inventoryItems: getDummyInventoryData(), loading: false });
          }
        } catch (error) {
          console.error('재고 목록 로드 오류:', error);
          set({ inventoryItems: getDummyInventoryData(), loading: false });
        }
      },

      fetchStockMovements: async () => {
        try {
          const response = await fetch('/api/inventory/movements', {
            credentials: 'include'
          });
          const data = await response.json();
          
          if (data.success) {
            set({ stockMovements: data.data });
            console.log('재고 변동 이력 로드 성공:', data.data.length, '건');
          } else {
            console.error('재고 변동 이력 로드 실패:', data.error);
            set({ stockMovements: getDummyStockMovements() });
          }
        } catch (error) {
          console.error('재고 변동 이력 로드 오류:', error);
          set({ stockMovements: getDummyStockMovements() });
        }
      },

      createInventoryItem: async (itemData) => {
        try {
          const response = await fetch('/api/inventory', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(itemData)
          });

          const result = await response.json();

          if (result.success) {
            get().addInventoryItem(result.data);
            console.log('재고 아이템 생성 성공');
            return true;
          } else {
            console.error('재고 아이템 생성 실패:', result.error);
            set({ error: result.error });
            return false;
          }
        } catch (error) {
          console.error('재고 아이템 생성 오류:', error);
          set({ error: '재고 아이템 생성 중 오류가 발생했습니다.' });
          return false;
        }
      },

      updateInventoryItemAPI: async (id, itemData) => {
        try {
          const response = await fetch(`/api/inventory/${id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(itemData)
          });

          const result = await response.json();

          if (result.success) {
            get().updateInventoryItem(id, result.data);
            console.log('재고 아이템 수정 성공');
            return true;
          } else {
            console.error('재고 아이템 수정 실패:', result.error);
            set({ error: result.error });
            return false;
          }
        } catch (error) {
          console.error('재고 아이템 수정 오류:', error);
          set({ error: '재고 아이템 수정 중 오류가 발생했습니다.' });
          return false;
        }
      },

      deleteInventoryItemAPI: async (id) => {
        try {
          const response = await fetch(`/api/inventory/${id}`, {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include'
          });

          const result = await response.json();

          if (result.success) {
            get().deleteInventoryItem(id);
            console.log('재고 아이템 삭제 성공');
            return true;
          } else {
            console.error('재고 아이템 삭제 실패:', result.error);
            set({ error: result.error });
            return false;
          }
        } catch (error) {
          console.error('재고 아이템 삭제 오류:', error);
          set({ error: '재고 아이템 삭제 중 오류가 발생했습니다.' });
          return false;
        }
      },

      // 유틸리티
      getInventoryByCategory: (category) => {
        const { inventoryItems } = get();
        return inventoryItems.filter(item => item.category === category);
      },

      getInventoryById: (id) => {
        const { inventoryItems } = get();
        return inventoryItems.find(item => item.id === id);
      },

      getLowStockItems: () => {
        const { inventoryItems } = get();
        return inventoryItems.filter(item => item.current_stock <= item.min_stock);
      },

      getOverStockItems: () => {
        const { inventoryItems } = get();
        return inventoryItems.filter(item => item.current_stock >= item.max_stock);
      },

      getStockMovementsByItem: (itemId) => {
        const { stockMovements } = get();
        return stockMovements.filter(movement => movement.inventory_item_id === itemId);
      },

      getStockMovementsByDateRange: (startDate, endDate) => {
        const { stockMovements } = get();
        return stockMovements.filter(movement => {
          const movementDate = new Date(movement.created_at);
          const start = new Date(startDate);
          const end = new Date(endDate);
          return movementDate >= start && movementDate <= end;
        });
      },
    }),
    {
      name: 'inventory-store',
    }
  )
); 