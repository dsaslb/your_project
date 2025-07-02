'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';

// 권한 타입 정의
export type UserRole = 'admin' | 'manager' | 'staff' | 'employee';
export type Permission = 
  | 'manage_staff' 
  | 'manage_orders' 
  | 'manage_inventory' 
  | 'manage_schedule' 
  | 'view_reports' 
  | 'manage_notices'
  | 'view_orders'
  | 'view_schedule'
  | 'process_payment'
  | 'manage_menu';

// 사용자 타입 정의
export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  permissions: Permission[];
  restaurantId?: number;
  avatar?: string;
  storeName?: string;
}

// 권한별 메뉴 설정
export const MENU_PERMISSIONS = {
  dashboard: ['admin', 'manager', 'staff', 'employee'],
  staff: ['admin', 'manager'],
  orders: ['admin', 'manager', 'staff'],
  inventory: ['admin', 'manager', 'staff'],
  schedule: ['admin', 'manager', 'staff'],
  notices: ['admin', 'manager', 'staff', 'employee'],
  reports: ['admin', 'manager'],
  settings: ['admin']
} as const;

// 권한별 액션 설정
export const ACTION_PERMISSIONS = {
  // 직원 관리
  'staff.create': ['admin', 'manager'],
  'staff.edit': ['admin', 'manager'],
  'staff.delete': ['admin', 'manager'],
  'staff.view': ['admin', 'manager', 'staff'],
  
  // 발주 관리
  'orders.create': ['admin', 'manager', 'staff'],
  'orders.approve': ['admin', 'manager'],
  'orders.reject': ['admin', 'manager'],
  'orders.delete': ['admin', 'manager'],
  'orders.view': ['admin', 'manager', 'staff'],
  
  // 재고 관리
  'inventory.create': ['admin', 'manager', 'staff'],
  'inventory.edit': ['admin', 'manager', 'staff'],
  'inventory.delete': ['admin', 'manager'],
  'inventory.view': ['admin', 'manager', 'staff'],
  
  // 스케줄 관리
  'schedule.create': ['admin', 'manager', 'staff'],
  'schedule.edit': ['admin', 'manager', 'staff'],
  'schedule.delete': ['admin', 'manager'],
  'schedule.view': ['admin', 'manager', 'staff', 'employee'],
  
  // 공지사항 관리
  'notices.create': ['admin', 'manager', 'staff'],
  'notices.edit': ['admin', 'manager'],
  'notices.delete': ['admin', 'manager'],
  'notices.view': ['admin', 'manager', 'staff', 'employee'],
  
  // 보고서 관리
  'reports.view': ['admin', 'manager'],
  'reports.export': ['admin', 'manager'],
  
  // 시스템 설정
  'settings.view': ['admin'],
  'settings.edit': ['admin']
} as const;

interface UserContextType {
  user: User | null;
  login: (userData: User) => void;
  logout: () => void;
  switchToAdmin: () => void;
  switchToManager: () => void;
  hasPermission: (permission: Permission) => boolean;
  hasRole: (role: UserRole) => boolean;
  canAccessMenu: (menu: keyof typeof MENU_PERMISSIONS) => boolean;
  canPerformAction: (action: keyof typeof ACTION_PERMISSIONS) => boolean;
  isAdmin: boolean;
  isManager: boolean;
  isStaff: boolean;
  isEmployee: boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  // 로그인
  const login = (userData: User) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  // 로그아웃
  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  // 최고관리자 모드로 전환
  const switchToAdmin = () => {
    if (user && user.role === 'manager') {
      const adminUser = {
        ...user,
        role: 'admin' as UserRole,
        permissions: ['manage_staff', 'manage_orders', 'manage_inventory', 'manage_schedule', 'view_reports', 'manage_notices', 'view_orders', 'view_schedule', 'process_payment', 'manage_menu']
      };
      setUser(adminUser);
      localStorage.setItem('user', JSON.stringify(adminUser));
    }
  };

  // 매장관리자 모드로 전환
  const switchToManager = () => {
    if (user && user.role === 'admin') {
      const managerUser = {
        ...user,
        role: 'manager' as UserRole,
        permissions: ['manage_staff', 'manage_orders', 'manage_inventory', 'manage_schedule', 'view_reports', 'manage_notices', 'view_orders', 'view_schedule', 'process_payment', 'manage_menu']
      };
      setUser(managerUser);
      localStorage.setItem('user', JSON.stringify(managerUser));
    }
  };

  // 권한 체크 함수
  const hasPermission = (permission: Permission): boolean => {
    if (!user) return false;
    return user.permissions.includes(permission);
  };

  // 역할 체크 함수
  const hasRole = (role: UserRole): boolean => {
    if (!user) return false;
    return user.role === role;
  };

  // 메뉴 접근 권한 체크
  const canAccessMenu = (menu: keyof typeof MENU_PERMISSIONS): boolean => {
    if (!user) return false;
    const allowedRoles = MENU_PERMISSIONS[menu];
    return allowedRoles.includes(user.role);
  };

  // 액션 수행 권한 체크
  const canPerformAction = (action: keyof typeof ACTION_PERMISSIONS): boolean => {
    if (!user) return false;
    const allowedRoles = ACTION_PERMISSIONS[action];
    return allowedRoles.includes(user.role);
  };

  // 역할별 편의 함수들
  const isAdmin = hasRole('admin');
  const isManager = hasRole('manager');
  const isStaff = hasRole('staff');
  const isEmployee = hasRole('employee');

  // 초기 로드 시 저장된 사용자 정보 복원
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
      } catch (error) {
        console.error('Failed to parse saved user data:', error);
        localStorage.removeItem('user');
      }
    }
  }, []);

  const value: UserContextType = {
    user,
    login,
    logout,
    switchToAdmin,
    switchToManager,
    hasPermission,
    hasRole,
    canAccessMenu,
    canPerformAction,
    isAdmin,
    isManager,
    isStaff,
    isEmployee
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}

// 권한 체크 훅
export function usePermission(permission: Permission) {
  const { hasPermission } = useUser();
  return hasPermission(permission);
}

// 메뉴 접근 권한 체크 훅
export function useMenuAccess(menu: keyof typeof MENU_PERMISSIONS) {
  const { canAccessMenu } = useUser();
  return canAccessMenu(menu);
}

// 액션 수행 권한 체크 훅
export function useActionPermission(action: keyof typeof ACTION_PERMISSIONS) {
  const { canPerformAction } = useUser();
  return canPerformAction(action);
}

// 권한별 컴포넌트 래퍼
interface PermissionGuardProps {
  permission: Permission;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function PermissionGuard({ permission, children, fallback = null }: PermissionGuardProps) {
  const hasPermission = usePermission(permission);
  return hasPermission ? <>{children}</> : <>{fallback}</>;
}

// 메뉴 접근 권한 가드
interface MenuGuardProps {
  menu: keyof typeof MENU_PERMISSIONS;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function MenuGuard({ menu, children, fallback = null }: MenuGuardProps) {
  const canAccess = useMenuAccess(menu);
  return canAccess ? <>{children}</> : <>{fallback}</>;
}

// 액션 권한 가드
interface ActionGuardProps {
  action: keyof typeof ACTION_PERMISSIONS;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function ActionGuard({ action, children, fallback = null }: ActionGuardProps) {
  const canPerform = useActionPermission(action);
  return canPerform ? <>{children}</> : <>{fallback}</>;
} 