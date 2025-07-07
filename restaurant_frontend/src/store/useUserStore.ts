import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import apiClient from '@/lib/api-client';

export interface User {
  id: number;
  username: string;
  name: string;
  email: string;
  role: 'super_admin' | 'brand_manager' | 'store_manager' | 'employee';
  is_active: boolean;
}

interface UserState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // 액션들
  login: (username: string, password: string) => Promise<{ success: boolean; redirectTo?: string }>;
  logout: () => void;
  checkAuth: () => Promise<boolean>;
  updateProfile: (data: { name?: string; email?: string }) => Promise<boolean>;
  clearError: () => void;
  
  // 역할별 접근 제어
  hasRole: (roles: string | string[]) => boolean;
  isSuperAdmin: () => boolean;
  isBrandManager: () => boolean;
  isStoreManager: () => boolean;
  isEmployee: () => boolean;
}

const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (username: string, password: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const { user, redirect_to } = await apiClient.login(username, password);
          
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });

          return { success: true, redirectTo: redirect_to };
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || '로그인에 실패했습니다';
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
            user: null,
          });
          return { success: false };
        }
      },

      logout: () => {
        apiClient.logout();
        set({
          user: null,
          isAuthenticated: false,
          error: null,
        });
      },

      checkAuth: async () => {
        // 토큰이 없으면 인증되지 않음
        if (!apiClient.isAuthenticated()) {
          set({ isAuthenticated: false, user: null });
          return false;
        }

        set({ isLoading: true });
        
        try {
          const user = await apiClient.getProfile();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          return true;
        } catch (error: any) {
          // 토큰이 유효하지 않으면 로그아웃
          apiClient.logout();
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
          return false;
        }
      },

      updateProfile: async (data: { name?: string; email?: string }) => {
        try {
          const updatedUser = await apiClient.updateProfile(data);
          set({ user: updatedUser.user });
          return true;
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || '프로필 업데이트에 실패했습니다';
          set({ error: errorMessage });
          return false;
        }
      },

      clearError: () => {
        set({ error: null });
      },

      // 역할별 접근 제어
      hasRole: (roles: string | string[]) => {
        const { user } = get();
        if (!user) return false;
        
        const roleArray = Array.isArray(roles) ? roles : [roles];
        return roleArray.includes(user.role);
      },

      isSuperAdmin: () => {
        return get().hasRole('super_admin');
      },

      isBrandManager: () => {
        return get().hasRole(['super_admin', 'brand_manager']);
      },

      isStoreManager: () => {
        return get().hasRole(['super_admin', 'brand_manager', 'store_manager']);
      },

      isEmployee: () => {
        return get().hasRole(['super_admin', 'brand_manager', 'store_manager', 'employee']);
      },
    }),
    {
      name: 'user-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useUserStore; 