import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface Order {
  id: number;
  item: string;
  quantity: number;
  unit: string;
  order_date: string;
  ordered_by: string;
  ordered_by_id: number;
  status: string;
  detail: string;
  memo: string;
  supplier: string;
  unit_price: number;
  total_cost: number;
  created_at: string;
  completed_at?: string;
  inventory_item_id?: number;
}

interface OrderStore {
  // 상태
  orders: Order[];
  loading: boolean;
  error: string | null;

  // 액션
  setOrders: (orders: Order[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // 발주 관리
  addOrder: (order: Order) => void;
  updateOrder: (id: number, updates: Partial<Order>) => void;
  deleteOrder: (id: number) => void;
  updateOrderStatus: (id: number, status: string) => void;
  
  // API 호출
  fetchOrders: () => Promise<void>;
  createOrder: (orderData: Partial<Order>) => Promise<boolean>;
  approveOrder: (orderId: number) => Promise<boolean>;
  rejectOrder: (orderId: number, reason?: string) => Promise<boolean>;
  deliverOrder: (orderId: number) => Promise<boolean>;
  
  // 유틸리티
  getOrdersByStatus: (status: string) => Order[];
  getOrderById: (id: number) => Order | undefined;
  getOrdersByStaff: (staffId: number) => Order[];
  getOrdersByDateRange: (startDate: string, endDate: string) => Order[];
}

// 더미 데이터 (API 실패 시 사용)
const getDummyOrderData = (): Order[] => [
  {
    id: 1,
    item: "소고기",
    quantity: 50,
    unit: "kg",
    order_date: "2024-01-15",
    ordered_by: "김철수",
    ordered_by_id: 1,
    status: "delivered",
    detail: "한우 등급 소고기",
    memo: "급하게 필요합니다",
    supplier: "한우공급업체",
    unit_price: 45000,
    total_cost: 2250000,
    created_at: "2024-01-15T10:00:00Z",
    completed_at: "2024-01-16T14:30:00Z"
  },
  {
    id: 2,
    item: "양파",
    quantity: 100,
    unit: "kg",
    order_date: "2024-01-16",
    ordered_by: "이영희",
    ordered_by_id: 2,
    status: "approved",
    detail: "신선한 양파",
    memo: "",
    supplier: "채소공급업체",
    unit_price: 3000,
    total_cost: 300000,
    created_at: "2024-01-16T14:30:00Z"
  },
  {
    id: 3,
    item: "고추장",
    quantity: 20,
    unit: "kg",
    order_date: "2024-01-17",
    ordered_by: "박민수",
    ordered_by_id: 3,
    status: "pending",
    detail: "전통 고추장",
    memo: "이미 배송완료",
    supplier: "조미료공급업체",
    unit_price: 12000,
    total_cost: 240000,
    created_at: "2024-01-17T09:15:00Z"
  }
];

export const useOrderStore = create<OrderStore>()(
  devtools(
    (set, get) => ({
      // 초기 상태
      orders: [],
      loading: false,
      error: null,

      // 상태 설정
      setOrders: (orders) => set({ orders }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),

      // 발주 관리
      addOrder: (order) => set((state) => ({
        orders: [...state.orders, order]
      })),

      updateOrder: (id, updates) => set((state) => ({
        orders: state.orders.map(order =>
          order.id === id ? { ...order, ...updates } : order
        )
      })),

      deleteOrder: (id) => set((state) => ({
        orders: state.orders.filter(order => order.id !== id)
      })),

      updateOrderStatus: (id, status) => set((state) => ({
        orders: state.orders.map(order =>
          order.id === id ? { ...order, status } : order
        )
      })),

      // API 호출
      fetchOrders: async () => {
        set({ loading: true, error: null });
        try {
          const response = await fetch('/api/orders', {
            credentials: 'include'
          });
          const data = await response.json();
          
          if (data.success) {
            set({ orders: data.data, loading: false });
            console.log('발주 데이터 로드 성공:', data.data.length, '건');
          } else {
            console.error('발주 목록 로드 실패:', data.error);
            set({ orders: getDummyOrderData(), loading: false });
          }
        } catch (error) {
          console.error('발주 목록 로드 오류:', error);
          set({ orders: getDummyOrderData(), loading: false });
        }
      },

      createOrder: async (orderData) => {
        try {
          const response = await fetch('/api/orders', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(orderData)
          });

          const result = await response.json();

          if (result.success) {
            // 새 발주를 Store에 추가
            get().addOrder(result.data);
            console.log('발주 생성 성공');
            return true;
          } else {
            console.error('발주 생성 실패:', result.error);
            set({ error: result.error });
            return false;
          }
        } catch (error) {
          console.error('발주 생성 오류:', error);
          set({ error: '발주 생성 중 오류가 발생했습니다.' });
          return false;
        }
      },

      approveOrder: async (orderId) => {
        try {
          const response = await fetch(`/api/orders/${orderId}/approve`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include'
          });

          const result = await response.json();

          if (result.success) {
            get().updateOrderStatus(orderId, 'approved');
            console.log('발주 승인 성공');
            return true;
          } else {
            console.error('발주 승인 실패:', result.error);
            set({ error: result.error });
            return false;
          }
        } catch (error) {
          console.error('발주 승인 오류:', error);
          set({ error: '발주 승인 중 오류가 발생했습니다.' });
          return false;
        }
      },

      rejectOrder: async (orderId, reason = '관리자 거절') => {
        try {
          const response = await fetch(`/api/orders/${orderId}/reject`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ reason })
          });

          const result = await response.json();

          if (result.success) {
            get().updateOrderStatus(orderId, 'rejected');
            console.log('발주 거절 성공');
            return true;
          } else {
            console.error('발주 거절 실패:', result.error);
            set({ error: result.error });
            return false;
          }
        } catch (error) {
          console.error('발주 거절 오류:', error);
          set({ error: '발주 거절 중 오류가 발생했습니다.' });
          return false;
        }
      },

      deliverOrder: async (orderId) => {
        try {
          const response = await fetch(`/api/orders/${orderId}/deliver`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include'
          });

          const result = await response.json();

          if (result.success) {
            get().updateOrderStatus(orderId, 'delivered');
            console.log('발주 배송완료 성공');
            return true;
          } else {
            console.error('발주 배송완료 실패:', result.error);
            set({ error: result.error });
            return false;
          }
        } catch (error) {
          console.error('발주 배송완료 오류:', error);
          set({ error: '발주 배송완료 중 오류가 발생했습니다.' });
          return false;
        }
      },

      // 유틸리티
      getOrdersByStatus: (status) => {
        const { orders } = get();
        return orders.filter(order => order.status === status);
      },

      getOrderById: (id) => {
        const { orders } = get();
        return orders.find(order => order.id === id);
      },

      getOrdersByStaff: (staffId) => {
        const { orders } = get();
        return orders.filter(order => order.ordered_by_id === staffId);
      },

      getOrdersByDateRange: (startDate, endDate) => {
        const { orders } = get();
        return orders.filter(order => {
          const orderDate = new Date(order.order_date);
          const start = new Date(startDate);
          const end = new Date(endDate);
          return orderDate >= start && orderDate <= end;
        });
      },
    }),
    {
      name: 'order-store',
    }
  )
); 