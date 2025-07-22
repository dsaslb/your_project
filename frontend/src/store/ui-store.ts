import { create } from 'zustand';

// 모달 타입
export interface Modal {
  id: string;
  isOpen: boolean;
  title?: string;
  content?: any; // React.ReactNode 대신 any 사용
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  onClose?: () => void;
}

// 사이드바 상태
interface SidebarState {
  isOpen: boolean;
  isCollapsed: boolean;
}

// 테마 타입
export type Theme = 'light' | 'dark' | 'system';

// UI 상태 타입
interface UIState {
  // 사이드바
  sidebar: SidebarState;
  
  // 모달
  modals: Modal[];
  
  // 테마
  theme: Theme;
  
  // 로딩 상태
  globalLoading: boolean;
  
  // 토스트 알림
  toasts: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    duration?: number;
  }>;
  
  // 액션들
  // 사이드바
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  
  // 모달
  openModal: (modal: Omit<Modal, 'isOpen'>) => void;
  closeModal: (id: string) => void;
  closeAllModals: () => void;
  
  // 테마
  setTheme: (theme: Theme) => void;
  
  // 로딩
  setGlobalLoading: (loading: boolean) => void;
  
  // 토스트
  addToast: (toast: Omit<UIState['toasts'][0], 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

// UI 스토어 생성
export const useUIStore = create<UIState>((set, get) => ({
  // 초기 상태
  sidebar: {
    isOpen: true,
    isCollapsed: false,
  },
  modals: [],
  theme: 'system',
  globalLoading: false,
  toasts: [],

  // 사이드바 액션
  toggleSidebar: () => set((state) => ({
    sidebar: { ...state.sidebar, isOpen: !state.sidebar.isOpen }
  })),
  
  setSidebarOpen: (open) => set((state) => ({
    sidebar: { ...state.sidebar, isOpen: open }
  })),
  
  setSidebarCollapsed: (collapsed) => set((state) => ({
    sidebar: { ...state.sidebar, isCollapsed: collapsed }
  })),

  // 모달 액션
  openModal: (modal) => set((state) => ({
    modals: [...state.modals, { ...modal, isOpen: true }]
  })),
  
  closeModal: (id) => set((state) => ({
    modals: state.modals.filter(modal => modal.id !== id)
  })),
  
  closeAllModals: () => set({ modals: [] }),

  // 테마 액션
  setTheme: (theme) => set({ theme }),

  // 로딩 액션
  setGlobalLoading: (loading) => set({ globalLoading: loading }),

  // 토스트 액션
  addToast: (toast) => {
    const id = Math.random().toString(36).substr(2, 9);
    set((state) => ({
      toasts: [...state.toasts, { ...toast, id }]
    }));
    
    // 자동 제거
    if (toast.duration !== 0) {
      setTimeout(() => {
        get().removeToast(id);
      }, toast.duration || 5000);
    }
  },
  
  removeToast: (id) => set((state) => ({
    toasts: state.toasts.filter(toast => toast.id !== id)
  })),
  
  clearToasts: () => set({ toasts: [] }),
})); 