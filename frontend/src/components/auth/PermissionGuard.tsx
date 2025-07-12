'use client';

import React from 'react';
import { Permission, UserRole, PermissionGuardProps } from '@/lib/auth';

export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  children,
  permission,
  permissions,
  role,
  roles,
  fallback = null,
}) => {
  const { user, hasPermission, hasRole } = useAuth();

  // 사용자가 로그인하지 않은 경우
  if (!user) {
    return <>{fallback}</>;
  }

  // 권한 체크
  if (permission && !hasPermission(permission)) {
    return <>{fallback}</>;
  }

  if (permissions && permissions.length > 0) {
    const hasAnyPermission = permissions.some(p => hasPermission(p));
    if (!hasAnyPermission) {
      return <>{fallback}</>;
    }
  }

  // 역할 체크
  if (role && !hasRole(role)) {
    return <>{fallback}</>;
  }

  if (roles && roles.length > 0) {
    const hasAnyRole = roles.some(r => hasRole(r));
    if (!hasAnyRole) {
      return <>{fallback}</>;
    }
  }

  // 모든 조건을 만족하면 children 렌더링
  return <>{children}</>;
};

// 특정 권한이 있는 경우에만 렌더링
export const WithPermission: React.FC<{
  permission: Permission;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ permission, children, fallback }) => (
  <PermissionGuard permission={permission} fallback={fallback}>
    {children}
  </PermissionGuard>
);

// 특정 역할인 경우에만 렌더링
export const WithRole: React.FC<{
  role: UserRole;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ role, children, fallback }) => (
  <PermissionGuard role={role} fallback={fallback}>
    {children}
  </PermissionGuard>
);

// 슈퍼 관리자만 렌더링
export const SuperAdminOnly: React.FC<{
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ children, fallback }) => (
  <WithRole role={UserRole.SUPER_ADMIN} fallback={fallback}>
    {children}
  </WithRole>
);

// 브랜드 관리자만 렌더링
export const BrandManagerOnly: React.FC<{
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ children, fallback }) => (
  <WithRole role={UserRole.BRAND_MANAGER} fallback={fallback}>
    {children}
  </WithRole>
);

// 매장 관리자만 렌더링
export const StoreManagerOnly: React.FC<{
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ children, fallback }) => (
  <WithRole role={UserRole.STORE_MANAGER} fallback={fallback}>
    {children}
  </WithRole>
);

// 직원만 렌더링
export const EmployeeOnly: React.FC<{
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ children, fallback }) => (
  <WithRole role={UserRole.EMPLOYEE} fallback={fallback}>
    {children}
  </WithRole>
);

// 관리자(슈퍼, 브랜드, 매장)만 렌더링
export const ManagerOnly: React.FC<{
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ children, fallback }) => (
  <PermissionGuard 
    roles={[UserRole.SUPER_ADMIN, UserRole.BRAND_MANAGER, UserRole.STORE_MANAGER]} 
    fallback={fallback}
  >
    {children}
  </PermissionGuard>
);

// 백엔드 접근 권한이 있는 경우만 렌더링
export const BackendAccessOnly: React.FC<{
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ children, fallback }) => (
  <SuperAdminOnly fallback={fallback}>
    {children}
  </SuperAdminOnly>
);

// 프론트 접근 권한이 있는 경우만 렌더링
export const FrontendAccessOnly: React.FC<{
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ children, fallback }) => {
  const { user } = useAuth();
  
  if (!user || user.role === UserRole.SUPER_ADMIN) {
    return <>{fallback}</>;
  }
  
  return <>{children}</>;
}; 
