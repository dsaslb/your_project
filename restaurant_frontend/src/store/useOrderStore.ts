import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { apiGet, apiPost, apiPut, apiDelete } from '../lib/api';

export interface OrderItem {
  name: string;
  quantity: number;
  price: number;
}

export interface Order {
  id: number;
  order_number: string;
  customer_name: string;
  items: OrderItem[];
  total_amount: number;
  status: 'pending' | 'preparing' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
  notes?: string;
  table_number?: number;
  estimated_time?: number;
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
  
  // 주문 관리
  addOrder: (order: Order) => void;
  updateOrder: (id: number, updates: Partial<Order>) => void;
  deleteOrder: (id: number) => void;
  updateOrderStatus: (id: number, status: string) => Promise<void>;
  
  // API 호출
  fetchOrders: () => Promise<void>;
  createOrder: (orderData: Partial<Order>) => Promise<void>;
  
  // 유틸리티
  getOrderById: (id: number) => Order | undefined;
  getOrdersByStatus: (status: string) => Order[];
  getPendingOrders: () => Order[];
  getPreparingOrders: () => Order[];
  getCompletedOrders: () => Order[];
}

// 더미 주문 데이터
const getDummyOrderData = (): Order[] => [
  {
    id: 1,
    order_number: 'ORD-2024-001',
    customer_name: '김고객',
    items: [
      { name: '불고기', quantity: 2, price: 15000 },
      { name: '김치찌개', quantity: 1, price: 12000 }
    ],
    total_amount: 42000,
    status: 'pending',
    created_at: '2024-01-15T10:30:00Z',
    updated_at: '2024-01-15T10:30:00Z',
    notes: '매운맛으로 해주세요',
    table_number: 5,
    estimated_time: 20
  },
  {
    id: 2,
    order_number: 'ORD-2024-002',
    customer_name: '이고객',
    items: [
      { name: '제육볶음', quantity: 1, price: 14000 },
      { name: '된장찌개', quantity: 1, price: 11000 },
      { name: '공기밥', quantity: 2, price: 2000 }
    ],
    total_amount: 29000,
    status: 'preparing',
    created_at: '2024-01-15T11:15:00Z',
    updated_at: '2024-01-15T11:20:00Z',
    notes: '',
    table_number: 3,
    estimated_time: 15
  },
  {
    id: 3,
    order_number: 'ORD-2024-003',
    customer_name: '박고객',
    items: [
      { name: '삼겹살', quantity: 2, price: 18000 },
      { name: '소주', quantity: 2, price: 5000 }
    ],
    total_amount: 46000,
    status: 'completed',
    created_at: '2024-01-15T12:00:00Z',
    updated_at: '2024-01-15T12:45:00Z',
    notes: '양념장 많이 주세요',
    table_number: 8,
    estimated_time: 30
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

      // 주문 관리
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

      // API 호출
      fetchOrders: async () => {
        set({ loading: true, error: null });
        
        try {
          const result = await apiGet<Order[]>('/api/orders');
          
          if (result.error) {
            // 백엔드 연결 안 됨 - 더미 데이터 사용
            console.log('백엔드 연결 안 됨, 더미 주문 데이터 사용');
            const dummyData = getDummyOrderData();
            set({ 
              orders: dummyData,
              loading: false 
            });
            return;
          }
          
          set({ orders: result.data || [], loading: false });
        } catch (error) {
          console.error('주문 데이터 가져오기 오류:', error);
          // 오류 시에도 더미 데이터 사용
          const dummyData = getDummyOrderData();
          set({ 
            orders: dummyData,
            loading: false,
            error: '데이터를 가져올 수 없어 더미 데이터를 표시합니다.'
          });
        }
      },

      createOrder: async (orderData) => {
        set({ loading: true, error: null });
        
        try {
          const result = await apiPost<Order>('/api/orders', orderData);
          
          if (result.error) {
            set({ 
              loading: false,
              error: '백엔드 서버에 연결할 수 없어 주문을 생성할 수 없습니다.'
            });
            return;
          }
          
          if (result.data) {
            set((state) => ({
              orders: [...state.orders, result.data!],
              loading: false
            }));
          }
        } catch (error) {
          console.error('주문 생성 오류:', error);
          set({ 
            loading: false,
            error: '주문 생성 중 오류가 발생했습니다.'
          });
        }
      },

      updateOrderStatus: async (id, status) => {
        set({ loading: true, error: null });
        
        try {
          const result = await apiPut<Order>(`/api/orders/${id}`, { status });
          
          if (result.error) {
            set({ 
              loading: false,
              error: '백엔드 서버에 연결할 수 없어 주문 상태를 업데이트할 수 없습니다.'
            });
            return;
          }
          
          if (result.data) {
            set((state) => ({
              orders: state.orders.map(order =>
                order.id === id ? { ...order, status: result.data!.status } : order
              ),
              loading: false
            }));
          }
        } catch (error) {
          console.error('주문 상태 업데이트 오류:', error);
          set({ 
            loading: false,
            error: '주문 상태 업데이트 중 오류가 발생했습니다.'
          });
        }
      },

      // 유틸리티
      getOrderById: (id: number) => {
        const { orders } = get();
        return orders.find(order => order.id === id);
      },

      getOrdersByStatus: (status: string) => {
        const { orders } = get();
        return orders.filter(order => order.status === status);
      },

      getPendingOrders: () => {
        const { orders } = get();
        return orders.filter(order => order.status === 'pending');
      },

      getPreparingOrders: () => {
        const { orders } = get();
        return orders.filter(order => order.status === 'preparing');
      },

      getCompletedOrders: () => {
        const { orders } = get();
        return orders.filter(order => order.status === 'completed');
      }
    }),
    {
      name: 'order-store'
    }
  )
); 