// 권한 타입 정의
export type Permission = 
  | 'user:read'
  | 'user:write'
  | 'user:delete'
  | 'admin:read'
  | 'admin:write'
  | 'admin:delete'
  | 'plugin:read'
  | 'plugin:write'
  | 'plugin:delete'
  | 'analytics:read'
  | 'analytics:write'
  | 'monitoring:read'
  | 'monitoring:write'
  | 'system:read'
  | 'system:write'
  | 'system:delete';

// 역할 타입 정의
export type Role = 'super_admin' | 'admin' | 'manager' | 'employee';

// 권한 관리 훅
export const usePermissions = () => {
  const { user, hasPermission, hasRole } = useAuth();

  // 특정 권한 확인
  const can = (permission: Permission): boolean => {
    return hasPermission(permission);
  };

  // 여러 권한 중 하나라도 있는지 확인
  const canAny = (permissions: Permission[]): boolean => {
    return permissions.some(permission => hasPermission(permission));
  };

  // 모든 권한이 있는지 확인
  const canAll = (permissions: Permission[]): boolean => {
    return permissions.every(permission => hasPermission(permission));
  };

  // 특정 역할 확인
  const isRole = (role: Role): boolean => {
    return hasRole(role);
  };

  // 역할 기반 접근 제어
  const requireRole = (role: Role): boolean => {
    return hasRole(role);
  };

  // 관리자 권한 확인
  const isAdmin = (): boolean => {
    return hasRole('admin') || hasRole('super_admin');
  };

  // 슈퍼 관리자 권한 확인
  const isSuperAdmin = (): boolean => {
    return hasRole('super_admin');
  };

  // 사용자 권한 확인
  const isUser = (): boolean => {
    return !!user;
  };

  return {
    user,
    can,
    canAny,
    canAll,
    isRole,
    requireRole,
    isAdmin,
    isSuperAdmin,
    isUser,
  };
};

// 권한 보호 컴포넌트 타입
export interface PermissionGuardProps {
  permission?: Permission;
  permissions?: Permission[];
  requireAll?: boolean;
  role?: Role;
  fallback?: React.ReactNode;
  children: React.ReactNode;
}

// 권한 보호 컴포넌트
export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  permission,
  permissions,
  requireAll = false,
  role,
  fallback = null,
  children,
}) => {
  const { can, canAny, canAll, isRole } = usePermissions();

  // 권한 확인 로직
  let hasAccess = false;

  if (role) {
    hasAccess = isRole(role);
  } else if (permission) {
    hasAccess = can(permission);
  } else if (permissions) {
    hasAccess = requireAll ? canAll(permissions) : canAny(permissions);
  } else {
    hasAccess = true; // 권한 요구사항이 없으면 접근 허용
  }

  return hasAccess ? <>{children}</> : <>{fallback}</>;
};

export default usePermissions; 
