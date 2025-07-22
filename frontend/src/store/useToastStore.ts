import { create } from 'zustand';
import { ToastProps } from '@/components/ui/Toast';

interface ToastState {
  toasts: ToastProps[];
}

interface ToastActions {
  addToast: (toast: Omit<ToastProps, 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

type ToastStore = ToastState & ToastActions;

export const useToastStore = create<ToastStore>((set, get) => ({
  // State
  toasts: [],

  // Actions
  addToast: (toast) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast: ToastProps = {
      ...toast,
      id,
    };

    set((state) => ({
      toasts: [...state.toasts, newToast],
    }));
  },

  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id),
    }));
  },

  clearToasts: () => {
    set({
      toasts: [],
    });
  },
}));

// 편의 함수들
export const toast = {
  success: (title: string, message?: string, duration?: number) => {
    useToastStore.getState().addToast({
      type: 'success',
      title,
      message,
      duration,
      onClose: useToastStore.getState().removeToast,
    });
  },

  error: (title: string, message?: string, duration?: number) => {
    useToastStore.getState().addToast({
      type: 'error',
      title,
      message,
      duration,
      onClose: useToastStore.getState().removeToast,
    });
  },

  warning: (title: string, message?: string, duration?: number) => {
    useToastStore.getState().addToast({
      type: 'warning',
      title,
      message,
      duration,
      onClose: useToastStore.getState().removeToast,
    });
  },

  info: (title: string, message?: string, duration?: number) => {
    useToastStore.getState().addToast({
      type: 'info',
      title,
      message,
      duration,
      onClose: useToastStore.getState().removeToast,
    });
  },
}; 