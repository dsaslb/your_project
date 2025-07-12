import { useDataStore } from '@/store';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

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

export interface Permission {
  module: string;
  action: string;
  value: boolean;
}

export interface UserPermissions {
  dashboard: { view: boolean; edit: boolean; admin_only: boolean };
  brand_management: {
    view: boolean;
    create: boolean;
    edit: boolean;
    delete: boolean;
    approve: boolean;
    monitor: boolean;
  };
  store_management: {
    view: boolean;
    create: boolean;
    edit: boolean;
    delete: boolean;
    approve: boolean;
    monitor: boolean;
  };
  employee_management: {
    view: boolean;
    create: boolean;
    edit: boolean;
    delete: boolean;
    approve: boolean;
    assign_roles: boolean;
  };
  schedule_management: {
    view: boolean;
    create: boolean;
    edit: boolean;
    delete: boolean;
    approve: boolean;
  };
  order_management: {
    view: boolean;
    create: boolean;
    edit: boolean;
    delete: boolean;
    approve: boolean;
  };
  inventory_management: {
    view: boolean;
    create: boolean;
    edit: boolean;
    delete: boolean;
  };
  notification_management: {
    view: boolean;
    send: boolean;
    delete: boolean;
  };
  system_management: {
    view: boolean;
    backup: boolean;
    restore: boolean;
    settings: boolean;
    monitoring: boolean;
  };
  ai_management: {
    view: boolean;
    create: boolean;
    edit: boolean;
    delete: boolean;
    approve: boolean;
    monitor: boolean;
  };
  reports: {
    view: boolean;
    export: boolean;
    admin_only: boolean;
  };
}

export const useAuth = () => {
  const { currentUser, setCurrentUser } = useDataStore();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  // 권한 확인 함수
  const hasPermission = (module: string, action: string): boolean => {
    if (!currentUser || !currentUser.permissions) {
      return false;
    }

    const modulePermissions = currentUser.permissions[module];
    if (!modulePermissions) {
      return false;
    }

    // admin_only 체크
    if (modulePermissions.admin_only && currentUser.role !== 'admin') {
      return false;
    }

    return modulePermissions[action] || false;
  };

  // 모듈 접근 권한 확인
  const canAccessModule = (module: string): boolean => {
    return hasPermission(module, 'view');
  };

  // 모듈 편집 권한 확인
  const canEditModule = (module: string): boolean => {
    return hasPermission(module, 'edit');
  };

  // 모듈 내 생성 권한 확인
  const canCreateInModule = (module: string): boolean => {
    return hasPermission(module, 'create');
  };

  // 모듈 내 삭제 권한 확인
  const canDeleteInModule = (module: string): boolean => {
    return hasPermission(module, 'delete');
  };

  // 모듈 내 승인 권한 확인
  const canApproveInModule = (module: string): boolean => {
    return hasPermission(module, 'approve');
  };

  // 역할 기반 권한 확인
  const isAdmin = (): boolean => {
    return currentUser?.role === 'admin';
  };

  const isBrandAdmin = (): boolean => {
    return currentUser?.role === 'brand_admin';
  };

  const isStoreAdmin = (): boolean => {
    return currentUser?.role === 'store_admin';
  };

  const isEmployee = (): boolean => {
    return currentUser?.role === 'employee';
  };

  const isManager = (): boolean => {
    return currentUser?.role === 'manager';
  };

  // 1인 사장님 모드 확인
  const isOwner = (): boolean => {
    return currentUser?.role === 'admin' && !isGroupAdmin();
  };

  // 그룹/프랜차이즈 최고관리자 확인
  const isGroupAdmin = (): boolean => {
    return currentUser?.role === 'admin' && hasPermission('group_admin', 'view');
  };

  // 1인 사장님 모드 (모든 메뉴 접근 가능)
  const isSoloMode = (): boolean => {
    return isOwner() || hasPermission('solo_mode', 'view');
  };

  // 그룹/프랜차이즈 모드 (최고관리자 메뉴만 접근 가능)
  const isFranchiseMode = (): boolean => {
    return isGroupAdmin() || hasPermission('franchise_mode', 'view');
  };

  // 모든 메뉴 접근 가능 여부 (1인 사장님 모드)
  const canAccessAllMenus = (): boolean => {
    return isSoloMode();
  };

  // 최고관리자 전용 메뉴 접근 가능 여부 (그룹/프랜차이즈 모드)
  const canAccessAdminOnlyMenus = (): boolean => {
    return isFranchiseMode();
  };

  // 현재 사용자의 대시보드 모드 반환
  const getDashboardMode = (): 'solo' | 'franchise' | 'employee' => {
    if (isSoloMode()) {
      return 'solo';
    } else if (isFranchiseMode()) {
      return 'franchise';
    } else {
      return 'employee';
    }
  };

  // 권한 요약 정보
  const getPermissionSummary = () => {
    if (!currentUser) {
      return { role: 'anonymous', grade: 'none', modules: {} };
    }

    const modules: Record<string, any> = {};
    const permissions = currentUser.permissions || {};

    Object.keys(permissions).forEach((module) => {
      const modulePerms = permissions[module];
      modules[module] = {
        can_access: modulePerms.view || false,
        can_edit: modulePerms.edit || false,
        can_create: modulePerms.create || false,
        can_delete: modulePerms.delete || false,
        can_approve: modulePerms.approve || false,
      };
    });

    return {
      role: currentUser.role,
      grade: currentUser.grade,
      modules,
    };
  };

  // 로그인 상태 확인
  const isAuthenticated = (): boolean => {
    return !!currentUser;
  };

  // 로그인 체크 및 리다이렉트
  const requireAuth = (redirectTo: string = '/login') => {
    if (!isAuthenticated()) {
      router.push(redirectTo);
      return false;
    }
    return true;
  };

  // 권한 체크 및 리다이렉트
  const requirePermission = (module: string, action: string, redirectTo: string = '/unauthorized') => {
    if (!requireAuth()) {
      return false;
    }

    if (!hasPermission(module, action)) {
      router.push(redirectTo);
      return false;
    }
    return true;
  };

  // 로그아웃
  const logout = () => {
    setCurrentUser(null);
    router.push('/login');
  };

  // 초기 로딩 상태 관리
  useEffect(() => {
    // 사용자 정보 로드 로직
    const loadUser = async () => {
      try {
        // API에서 사용자 정보 가져오기
        const response = await fetch('/api/auth/me');
        if (response.ok) {
          const userData = await response.json();
          setCurrentUser(userData);
        } else {
          setCurrentUser(null);
        }
      } catch (error) {
        console.error('사용자 정보 로드 실패:', error);
        setCurrentUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
  }, [setCurrentUser]);

  return {
    // 상태
    currentUser,
    isLoading,
    isAuthenticated: isAuthenticated(),

    // 권한 확인
    hasPermission,
    canAccessModule,
    canEditModule,
    canCreateInModule,
    canDeleteInModule,
    canApproveInModule,

    // 역할 확인
    isAdmin: isAdmin(),
    isBrandAdmin: isBrandAdmin(),
    isStoreAdmin: isStoreAdmin(),
    isEmployee: isEmployee(),
    isManager: isManager(),
    isOwner: isOwner(),
    isGroupAdmin: isGroupAdmin(),

    // 모드 확인
    isSoloMode: isSoloMode(),
    isFranchiseMode: isFranchiseMode(),
    canAccessAllMenus: canAccessAllMenus(),
    canAccessAdminOnlyMenus: canAccessAdminOnlyMenus(),
    getDashboardMode,

    // 권한 요약
    getPermissionSummary,

    // 인증 관리
    requireAuth,
    requirePermission,
    logout,
  };
}; 