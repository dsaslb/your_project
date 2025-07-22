import { create } from 'zustand';

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

export interface Modal {
  id: string;
  isOpen: boolean;
  title?: string;
  content?: React.ReactNode;
}

export interface UIState {
  // 상태
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark' | 'system';
  toasts: Toast[];
  modals: Modal[];
  loadingStates: Record<string, boolean>;

  // 액션
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  
  // 토스트 관리
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
  
  // 모달 관리
  openModal: (modal: Omit<Modal, 'isOpen'>) => void;
  closeModal: (id: string) => void;
  closeAllModals: () => void;
  
  // 로딩 상태 관리
  setLoading: (key: string, loading: boolean) => void;
  clearLoading: (key: string) => void;
}

export const useUIStore = create<UIState>((set, get) => ({
  // 초기 상태
  sidebarCollapsed: false,
  theme: 'system',
  toasts: [],
  modals: [],
  loadingStates: {},

  // 사이드바 액션
  toggleSidebar: () => {
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
  },

  setSidebarCollapsed: (collapsed: boolean) => {
    set({ sidebarCollapsed: collapsed });
  },

  // 테마 액션
  setTheme: (theme: 'light' | 'dark' | 'system') => {
    set({ theme });
  },

  // 토스트 액션
  addToast: (toastData) => {
    const id = Math.random().toString(36).substr(2, 9);
    const toast: Toast = {
      id,
      duration: 5000,
      ...toastData,
    };

    set((state) => ({
      toasts: [...state.toasts, toast],
    }));

    // 자동 제거
    if (toast.duration && toast.duration > 0) {
      setTimeout(() => {
        get().removeToast(id);
      }, toast.duration);
    }
  },

  removeToast: (id: string) => {
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id),
    }));
  },

  clearToasts: () => {
    set({ toasts: [] });
  },

  // 모달 액션
  openModal: (modalData) => {
    const modalId = modalData.id || Math.random().toString(36).substr(2, 9);
    const modal: Modal = {
      isOpen: true,
      ...modalData,
      id: modalId,
    };

    set((state) => ({
      modals: [...state.modals.filter((m) => m.id !== modalId), modal],
    }));
  },

  closeModal: (id: string) => {
    set((state) => ({
      modals: state.modals.map((modal) =>
        modal.id === id ? { ...modal, isOpen: false } : modal
      ),
    }));
  },

  closeAllModals: () => {
    set((state) => ({
      modals: state.modals.map((modal) => ({ ...modal, isOpen: false })),
    }));
  },

  // 로딩 상태 액션
  setLoading: (key: string, loading: boolean) => {
    set((state) => ({
      loadingStates: {
        ...state.loadingStates,
        [key]: loading,
      },
    }));
  },

  clearLoading: (key: string) => {
    set((state) => {
      const newLoadingStates = { ...state.loadingStates };
      delete newLoadingStates[key];
      return { loadingStates: newLoadingStates };
    });
  },
})); 