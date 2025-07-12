import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// 사용자 정보 타입
export interface User {
  id: number;
  username: string;
  email: string;
  name: string;
  role: 'admin' | 'brand_admin' | 'store_admin' | 'manager' | 'employee';
  grade: 'ceo' | 'director' | 'manager' | 'staff';
  status: 'approved' | 'pending' | 'rejected' | 'suspended';
  branch_id?: number;
  brand_id?: number;
  industry_id?: number;
  team_id?: number;
  position?: string;
  department?: string;
  permissions: Record<string, any>;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

// 매장 정보 타입
export interface Branch {
  id: number;
  name: string;
  address: string;
  phone: string;
  store_code: string;
  store_type: 'franchise' | 'corporate' | 'independent';
  business_hours: Record<string, any>;
  capacity: number;
  status: 'active' | 'inactive' | 'maintenance';
  industry_id?: number;
  brand_id?: number;
  created_at: string;
  updated_at: string;
}

// 브랜드 정보 타입
export interface Brand {
  id: number;
  name: string;
  code: string;
  industry_id?: number;
  description?: string;
  logo_url?: string;
  website?: string;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
  status: 'active' | 'inactive' | 'suspended';
  created_at: string;
  updated_at: string;
}

// 직원 정보 타입
export interface Staff {
  id: number;
  user_id: number;
  name: string;
  position: string;
  department: string;
  hire_date: string;
  salary_base: number;
  salary_allowance: number;
  salary_bonus: number;
  work_days: string[];
  work_hours_start: string;
  work_hours_end: string;
  benefits: string[];
  status: 'active' | 'inactive' | 'suspended';
  branch_id: number;
  created_at: string;
  updated_at: string;
}

// 주문 정보 타입
export interface Order {
  id: number;
  order_number: string;
  customer_name: string;
  customer_phone: string;
  items: OrderItem[];
  total_amount: number;
  status: 'pending' | 'confirmed' | 'preparing' | 'ready' | 'completed' | 'cancelled';
  payment_method: string;
  payment_status: 'pending' | 'paid' | 'failed';
  branch_id: number;
  created_by: number;
  created_at: string;
  updated_at: string;
}

// 주문 아이템 타입
export interface OrderItem {
  id: number;
  order_id: number;
  menu_id: number;
  quantity: number;
  unit_price: number;
  total_price: number;
  notes?: string;
}

// 재고 정보 타입
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
  description?: string;
  location?: string;
  status: 'active' | 'inactive';
  branch_id: number;
  created_at: string;
  updated_at: string;
}

// 스케줄 정보 타입
export interface Schedule {
  id: number;
  user_id: number;
  date: string;
  start_time: string;
  end_time: string;
  break_start?: string;
  break_end?: string;
  position: string;
  notes?: string;
  status: 'scheduled' | 'confirmed' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
}

// 알림 정보 타입
export interface Notification {
  id: number;
  user_id: number;
  title: string;
  content: string;
  category: string;
  priority: 'urgent' | 'important' | 'normal';
  is_read: boolean;
  related_url?: string;
  created_at: string;
}

// 중앙 데이터 스토어
interface DataStore {
  // 사용자 관련
  currentUser: User | null;
  users: User[];
  setCurrentUser: (user: User | null) => void;
  setUsers: (users: User[]) => void;
  updateUser: (id: number, updates: Partial<User>) => void;
  addUser: (user: User) => void;
  removeUser: (id: number) => void;

  // 매장 관련
  branches: Branch[];
  currentBranch: Branch | null;
  setBranches: (branches: Branch[]) => void;
  setCurrentBranch: (branch: Branch | null) => void;
  updateBranch: (id: number, updates: Partial<Branch>) => void;
  addBranch: (branch: Branch) => void;
  removeBranch: (id: number) => void;

  // 브랜드 관련
  brands: Brand[];
  currentBrand: Brand | null;
  setBrands: (brands: Brand[]) => void;
  setCurrentBrand: (brand: Brand | null) => void;
  updateBrand: (id: number, updates: Partial<Brand>) => void;
  addBrand: (brand: Brand) => void;
  removeBrand: (id: number) => void;

  // 직원 관련
  staff: Staff[];
  setStaff: (staff: Staff[]) => void;
  updateStaff: (id: number, updates: Partial<Staff>) => void;
  addStaff: (staff: Staff) => void;
  removeStaff: (id: number) => void;

  // 주문 관련
  orders: Order[];
  setOrders: (orders: Order[]) => void;
  updateOrder: (id: number, updates: Partial<Order>) => void;
  addOrder: (order: Order) => void;
  removeOrder: (id: number) => void;

  // 재고 관련
  inventory: InventoryItem[];
  setInventory: (inventory: InventoryItem[]) => void;
  updateInventoryItem: (id: number, updates: Partial<InventoryItem>) => void;
  addInventoryItem: (item: InventoryItem) => void;
  removeInventoryItem: (id: number) => void;

  // 스케줄 관련
  schedules: Schedule[];
  setSchedules: (schedules: Schedule[]) => void;
  updateSchedule: (id: number, updates: Partial<Schedule>) => void;
  addSchedule: (schedule: Schedule) => void;
  removeSchedule: (id: number) => void;

  // 알림 관련
  notifications: Notification[];
  setNotifications: (notifications: Notification[]) => void;
  updateNotification: (id: number, updates: Partial<Notification>) => void;
  addNotification: (notification: Notification) => void;
  removeNotification: (id: number) => void;
  markAsRead: (id: number) => void;

  // 데이터 동기화
  lastSync: Record<string, string>;
  setLastSync: (key: string, timestamp: string) => void;
  clearAllData: () => void;
}

export const useDataStore = create<DataStore>()(
  persist(
    (set, get) => ({
      // 초기 상태
      currentUser: null,
      users: [],
      branches: [],
      currentBranch: null,
      brands: [],
      currentBrand: null,
      staff: [],
      orders: [],
      inventory: [],
      schedules: [],
      notifications: [],
      lastSync: {},

      // 사용자 관련 액션
      setCurrentUser: (user) => set({ currentUser: user }),
      setUsers: (users) => set({ users }),
      updateUser: (id, updates) =>
        set((state) => ({
          users: state.users.map((user) =>
            user.id === id ? { ...user, ...updates } : user
          ),
        })),
      addUser: (user) =>
        set((state) => ({ users: [...state.users, user] })),
      removeUser: (id) =>
        set((state) => ({
          users: state.users.filter((user) => user.id !== id),
        })),

      // 매장 관련 액션
      setBranches: (branches) => set({ branches }),
      setCurrentBranch: (branch) => set({ currentBranch: branch }),
      updateBranch: (id, updates) =>
        set((state) => ({
          branches: state.branches.map((branch) =>
            branch.id === id ? { ...branch, ...updates } : branch
          ),
        })),
      addBranch: (branch) =>
        set((state) => ({ branches: [...state.branches, branch] })),
      removeBranch: (id) =>
        set((state) => ({
          branches: state.branches.filter((branch) => branch.id !== id),
        })),

      // 브랜드 관련 액션
      setBrands: (brands) => set({ brands }),
      setCurrentBrand: (brand) => set({ currentBrand: brand }),
      updateBrand: (id, updates) =>
        set((state) => ({
          brands: state.brands.map((brand) =>
            brand.id === id ? { ...brand, ...updates } : brand
          ),
        })),
      addBrand: (brand) =>
        set((state) => ({ brands: [...state.brands, brand] })),
      removeBrand: (id) =>
        set((state) => ({
          brands: state.brands.filter((brand) => brand.id !== id),
        })),

      // 직원 관련 액션
      setStaff: (staff) => set({ staff }),
      updateStaff: (id, updates) =>
        set((state) => ({
          staff: state.staff.map((member) =>
            member.id === id ? { ...member, ...updates } : member
          ),
        })),
      addStaff: (member) =>
        set((state) => ({ staff: [...state.staff, member] })),
      removeStaff: (id) =>
        set((state) => ({
          staff: state.staff.filter((member) => member.id !== id),
        })),

      // 주문 관련 액션
      setOrders: (orders) => set({ orders }),
      updateOrder: (id, updates) =>
        set((state) => ({
          orders: state.orders.map((order) =>
            order.id === id ? { ...order, ...updates } : order
          ),
        })),
      addOrder: (order) =>
        set((state) => ({ orders: [...state.orders, order] })),
      removeOrder: (id) =>
        set((state) => ({
          orders: state.orders.filter((order) => order.id !== id),
        })),

      // 재고 관련 액션
      setInventory: (inventory) => set({ inventory }),
      updateInventoryItem: (id, updates) =>
        set((state) => ({
          inventory: state.inventory.map((item) =>
            item.id === id ? { ...item, ...updates } : item
          ),
        })),
      addInventoryItem: (item) =>
        set((state) => ({ inventory: [...state.inventory, item] })),
      removeInventoryItem: (id) =>
        set((state) => ({
          inventory: state.inventory.filter((item) => item.id !== id),
        })),

      // 스케줄 관련 액션
      setSchedules: (schedules) => set({ schedules }),
      updateSchedule: (id, updates) =>
        set((state) => ({
          schedules: state.schedules.map((schedule) =>
            schedule.id === id ? { ...schedule, ...updates } : schedule
          ),
        })),
      addSchedule: (schedule) =>
        set((state) => ({ schedules: [...state.schedules, schedule] })),
      removeSchedule: (id) =>
        set((state) => ({
          schedules: state.schedules.filter((schedule) => schedule.id !== id),
        })),

      // 알림 관련 액션
      setNotifications: (notifications) => set({ notifications }),
      updateNotification: (id, updates) =>
        set((state) => ({
          notifications: state.notifications.map((notification) =>
            notification.id === id ? { ...notification, ...updates } : notification
          ),
        })),
      addNotification: (notification) =>
        set((state) => ({ notifications: [...state.notifications, notification] })),
      removeNotification: (id) =>
        set((state) => ({
          notifications: state.notifications.filter((notification) => notification.id !== id),
        })),
      markAsRead: (id) =>
        set((state) => ({
          notifications: state.notifications.map((notification) =>
            notification.id === id ? { ...notification, is_read: true } : notification
          ),
        })),

      // 데이터 동기화 액션
      setLastSync: (key, timestamp) =>
        set((state) => ({
          lastSync: { ...state.lastSync, [key]: timestamp },
        })),
      clearAllData: () =>
        set({
          currentUser: null,
          users: [],
          branches: [],
          currentBranch: null,
          brands: [],
          currentBrand: null,
          staff: [],
          orders: [],
          inventory: [],
          schedules: [],
          notifications: [],
          lastSync: {},
        }),
    }),
    {
      name: 'your_program-data-store',
      partialize: (state) => ({
        currentUser: state.currentUser,
        currentBranch: state.currentBranch,
        currentBrand: state.currentBrand,
        lastSync: state.lastSync,
      }),
    }
  )
); 