import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiClient as _apiClient } from '@/lib/api-client';

const apiClient: any = _apiClient;

export interface User {
  id: number;
  username: string;
  name: string;
  email: string;
  role: 'admin' | 'brand_admin' | 'store_admin' | 'employee';
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
  
  // 실시간 동기화 관련
  subscribeToChanges: (callback: (state: UserState) => void) => () => void;
  broadcastChange: (action: string, data?: any) => void;
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
          
          // 실시간 동기화: 로그인 이벤트 브로드캐스트
          get().broadcastChange('login', { user, timestamp: new Date().toISOString() });
          
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
          
          // 실시간 동기화: 로그아웃 이벤트 브로드캐스트
          get().broadcastChange('logout', { timestamp: new Date().toISOString() });
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
          
          // 실시간 동기화: 프로필 업데이트 이벤트 브로드캐스트
          get().broadcastChange('profile_update', { user: updatedUser.user, timestamp: new Date().toISOString() });
          
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
        return get().hasRole('admin');
      },

      isBrandManager: () => {
        return get().hasRole(['admin', 'brand_admin']);
      },

      isStoreManager: () => {
        return get().hasRole(['admin', 'brand_admin', 'store_admin']);
      },

      isEmployee: () => {
        return get().hasRole(['admin', 'brand_admin', 'store_admin', 'employee']);
      },
      
      // 실시간 동기화: 구독자 관리
      subscribeToChanges: (callback: (state: UserState) => void) => {
        // localStorage 이벤트 리스너로 다른 탭의 변경사항 감지
        const handleStorageChange = (e: StorageEvent) => {
          if (e.key === 'user-storage') {
            try {
              const newState = JSON.parse(e.newValue || '{}');
              callback(newState);
            } catch (error) {
              console.error('User store state 파싱 오류:', error);
            }
          }
        };
        
        window.addEventListener('storage', handleStorageChange);
        
        // 구독 해제 함수 반환
        return () => {
          window.removeEventListener('storage', handleStorageChange);
        };
      },
      
      // 실시간 동기화: 변경사항 브로드캐스트
      broadcastChange: (action: string, data?: any) => {
        const currentState = get();
        const broadcastData = {
          action,
          data,
          state: {
            user: currentState.user,
            isAuthenticated: currentState.isAuthenticated,
            timestamp: new Date().toISOString()
          }
        };
        
        // localStorage를 통한 다른 탭에 브로드캐스트
        localStorage.setItem('user-store-broadcast', JSON.stringify(broadcastData));
        localStorage.removeItem('user-store-broadcast'); // 즉시 제거하여 중복 방지
        
        // WebSocket을 통한 실시간 브로드캐스트 (선택사항)
        if (typeof window !== 'undefined' && (window as any).notificationWebSocket) {
          try {
            (window as any).notificationWebSocket.send(JSON.stringify({
              type: 'user_store_update',
              ...broadcastData
            }));
          } catch (error) {
            console.warn('WebSocket 브로드캐스트 실패:', error);
          }
        }
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