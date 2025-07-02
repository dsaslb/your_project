"use client"

import React from 'react';
import { useUser } from './UserContext';

interface PermissionGuardProps {
  children: React.ReactNode;
  permissions?: string[];
  roles?: string[];
  fallback?: React.ReactNode;
  requireAll?: boolean; // true: 모든 권한 필요, false: 하나라도 있으면 허용
}

export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  children,
  permissions = [],
  roles = [],
  fallback = null,
  requireAll = false
}) => {
  const { user } = useUser();

  if (!user) {
    return <>{fallback}</>;
  }

  // 역할 체크
  const hasRequiredRole = roles.length === 0 || roles.includes(user.role);

  // 권한 체크
  const hasRequiredPermissions = permissions.length === 0 || (() => {
    if (requireAll) {
      // 모든 권한이 필요
      return permissions.every(permission => 
        user.permissions?.includes(permission)
      );
    } else {
      // 하나라도 있으면 허용
      return permissions.some(permission => 
        user.permissions?.includes(permission)
      );
    }
  })();

  // 관리자는 모든 권한을 가짐
  const isAdmin = user.role === 'admin';

  if (isAdmin || (hasRequiredRole && hasRequiredPermissions)) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
};

// 특정 권한을 가진 사용자만 렌더링하는 컴포넌트
export const withPermission = <P extends object>(
  Component: React.ComponentType<P>,
  requiredPermissions: string[],
  fallback?: React.ReactNode
) => {
  return (props: P) => (
    <PermissionGuard permissions={requiredPermissions} fallback={fallback}>
      <Component {...props} />
    </PermissionGuard>
  );
};

// 특정 역할을 가진 사용자만 렌더링하는 컴포넌트
export const withRole = <P extends object>(
  Component: React.ComponentType<P>,
  requiredRoles: string[],
  fallback?: React.ReactNode
) => {
  return (props: P) => (
    <PermissionGuard roles={requiredRoles} fallback={fallback}>
      <Component {...props} />
    </PermissionGuard>
  );
};

// 권한 훅
export const usePermission = () => {
  const { user } = useUser();

  const hasPermission = (permission: string): boolean => {
    if (!user) return false;
    if (user.role === 'admin') return true;
    return user.permissions?.includes(permission) || false;
  };

  const hasAnyPermission = (permissions: string[]): boolean => {
    if (!user) return false;
    if (user.role === 'admin') return true;
    return permissions.some(permission => 
      user.permissions?.includes(permission)
    );
  };

  const hasAllPermissions = (permissions: string[]): boolean => {
    if (!user) return false;
    if (user.role === 'admin') return true;
    return permissions.every(permission => 
      user.permissions?.includes(permission)
    );
  };

  const hasRole = (role: string): boolean => {
    if (!user) return false;
    return user.role === role;
  };

  const hasAnyRole = (roles: string[]): boolean => {
    if (!user) return false;
    return roles.includes(user.role);
  };

  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    hasAnyRole,
    user
  };
};

// 권한별 액션 버튼 컴포넌트
interface PermissionButtonProps {
  permission: string;
  onClick: () => void;
  children: React.ReactNode;
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
  size?: "default" | "sm" | "lg" | "icon";
  disabled?: boolean;
  className?: string;
  fallback?: React.ReactNode;
}

export const PermissionButton: React.FC<PermissionButtonProps> = ({
  permission,
  onClick,
  children,
  variant = "default",
  size = "default",
  disabled = false,
  className,
  fallback
}) => {
  const { hasPermission } = usePermission();

  if (!hasPermission(permission)) {
    return fallback ? <>{fallback}</> : null;
  }

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={className}
      data-variant={variant}
      data-size={size}
    >
      {children}
    </button>
  );
};

// 권한별 링크 컴포넌트
interface PermissionLinkProps {
  permission: string;
  href: string;
  children: React.ReactNode;
  className?: string;
  fallback?: React.ReactNode;
}

export const PermissionLink: React.FC<PermissionLinkProps> = ({
  permission,
  href,
  children,
  className,
  fallback
}) => {
  const { hasPermission } = usePermission();

  if (!hasPermission(permission)) {
    return fallback ? <>{fallback}</> : null;
  }

  return (
    <a href={href} className={className}>
      {children}
    </a>
  );
};

// 권한별 메뉴 아이템 컴포넌트
interface PermissionMenuItemProps {
  permission: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const PermissionMenuItem: React.FC<PermissionMenuItemProps> = ({
  permission,
  children,
  fallback
}) => {
  const { hasPermission } = usePermission();

  if (!hasPermission(permission)) {
    return fallback ? <>{fallback}</> : null;
  }

  return <>{children}</>;
};

// 권한별 섹션 컴포넌트
interface PermissionSectionProps {
  permission: string;
  title: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const PermissionSection: React.FC<PermissionSectionProps> = ({
  permission,
  title,
  children,
  fallback
}) => {
  const { hasPermission } = usePermission();

  if (!hasPermission(permission)) {
    return fallback ? <>{fallback}</> : null;
  }

  return (
    <section>
      <h2>{title}</h2>
      {children}
    </section>
  );
}; 