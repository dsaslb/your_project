'use client';

import React from 'react';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiClient } from './apiClient';
import { User, UserRole, Permission, AuthContextType, ROLE_PERMISSIONS } from './auth';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  hasPermission: (permission: Permission) => boolean;
  hasRole: (role: UserRole) => boolean;
  refreshUser: () => Promise<void>;
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
}

// 인증 상태 관리 스토어
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isLoading: false,
      isAuthenticated: false,

      // 로그인
      login: async (username: string, password: string) => {
        set({ isLoading: true });
        
        try {
          const response = await apiClient.post<{ user: User; token: string }>('/auth/login', {
            username,
            password,
          });

          if (response.success && response.data) {
            const { user, token } = response.data;
            
            // 사용자 권한 설정
            const userWithPermissions = {
              ...user,
              permissions: ROLE_PERMISSIONS[user.role] || []
            };

            // 토큰을 로컬 스토리지에 저장
            localStorage.setItem('auth_token', token);
            
            set({
              user: userWithPermissions,
              isAuthenticated: true,
              isLoading: false,
            });
            
            return true;
          } else {
            set({ isLoading: false });
            return false;
          }
        } catch (error) {
          console.error('Login error:', error);
          set({ isLoading: false });
          return false;
        }
      },

      // 로그아웃
      logout: () => {
        localStorage.removeItem('auth_token');
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        });
        
        // 로그인 페이지로 리다이렉트
        window.location.href = '/login';
      },

      // 권한 확인
      hasPermission: (permission: Permission) => {
        const { user } = get();
        if (!user) return false;
        return user.permissions.includes(permission);
      },

      // 역할 확인
      hasRole: (role: UserRole) => {
        const { user } = get();
        if (!user) return false;
        return user.role === role;
      },

      // 사용자 정보 새로고침
      refreshUser: async () => {
        const { user } = get();
        if (!user) return;

        set({ isLoading: true });
        
        try {
          const response = await apiClient.get<User>('/api/auth/me');
          
          if (response.success && response.data) {
            const updatedUser = {
              ...response.data,
              permissions: ROLE_PERMISSIONS[response.data.role] || []
            };
            
            set({
              user: updatedUser,
              isLoading: false,
            });
          } else {
            // 토큰이 만료되었거나 인증에 실패한 경우
            get().logout();
          }
        } catch (error) {
          console.error('Refresh user error:', error);
          get().logout();
        }
      },

      // 사용자 설정
      setUser: (user: User | null) => {
        set({
          user,
          isAuthenticated: !!user,
        });
      },

      // 로딩 상태 설정
      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// 인증 훅
export const useAuth = (): AuthContextType => {
  const {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    hasPermission,
    hasRole,
    refreshUser,
  } = useAuthStore();

  return {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    hasPermission,
    hasRole,
    refreshUser,
  };
};

// 권한 체크 유틸리티 훅
export const usePermissions = () => {
  const { user, hasPermission, hasRole } = useAuth();

  // 특정 역할들 중 하나라도 있는지 확인하는 함수
  const hasAnyRole = (roles: UserRole[]) => {
    return roles.some(role => hasRole(role));
  };

  return {
    user,
    hasPermission,
    hasRole,
    
    // 특정 권한들 중 하나라도 있는지 확인
    hasAnyPermission: (permissions: Permission[]) => {
      return permissions.some(permission => hasPermission(permission));
    },
    
    // 모든 권한이 있는지 확인
    hasAllPermissions: (permissions: Permission[]) => {
      return permissions.every(permission => hasPermission(permission));
    },
    
    // 특정 역할들 중 하나라도 있는지 확인
    hasAnyRole,
    
    // 슈퍼 관리자인지 확인
    isSuperAdmin: () => hasRole(UserRole.SUPER_ADMIN),
    
    // 브랜드 관리자인지 확인
    isBrandManager: () => hasRole(UserRole.BRAND_MANAGER),
    
    // 매장 관리자인지 확인
    isStoreManager: () => hasRole(UserRole.STORE_MANAGER),
    
    // 직원인지 확인
    isEmployee: () => hasRole(UserRole.EMPLOYEE),
    
    // 관리자 역할인지 확인
    isManager: () => hasAnyRole([UserRole.SUPER_ADMIN, UserRole.BRAND_MANAGER, UserRole.STORE_MANAGER]),
    
    // 백엔드 접근 권한이 있는지 확인
    canAccessBackend: () => hasRole(UserRole.SUPER_ADMIN),
    
    // 프론트 접근 권한이 있는지 확인
    canAccessFrontend: () => !hasRole(UserRole.SUPER_ADMIN),
  };
};

// 자동 토큰 갱신
export const useAutoRefresh = () => {
  const { refreshUser, isAuthenticated } = useAuth();

  React.useEffect(() => {
    if (!isAuthenticated) return;

    // 5분마다 사용자 정보 새로고침
    const interval = setInterval(() => {
      refreshUser();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, [isAuthenticated, refreshUser]);
}; 