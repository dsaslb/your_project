import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiClient as _apiClient } from '@/lib/api-client';

const apiClient: any = _apiClient;

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
          const result = await apiClient.login(username, password);
          const user = result.user;
          const redirect_to = result.redirect_to;
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          return { success: true, redirectTo: redirect_to };
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || error.message || '로그인에 실패했습니다';
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
            user: null,
          });
          // 백엔드 연결 실패 시 특별 처리
          if (errorMessage.includes('서버에 연결할 수 없습니다')) {
            console.warn('백엔드 서버가 실행되지 않았습니다. 프론트엔드만으로 UI 테스트를 진행합니다.');
          }
          return { success: false };
        }
      },

      logout: () => {
        try {
          apiClient.logout();
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          set({
            user: null,
            isAuthenticated: false,
            error: null,
          });
        }
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
          console.error('Auth check error:', error);
          
          // 백엔드 연결 실패 시 토큰을 유지하되 인증 상태만 false로 설정
          if (error.message?.includes('서버에 연결할 수 없습니다') || 
              error.code === 'ERR_NETWORK' || 
              error.response?.status >= 500) {
            console.warn('백엔드 연결 실패. 토큰은 유지하되 인증 상태를 false로 설정합니다.');
            set({
              isAuthenticated: false,
              isLoading: false,
              error: '백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.',
            });
            return false;
          }
          
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