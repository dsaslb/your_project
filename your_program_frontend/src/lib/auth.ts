// 사용자 역할 정의
export enum UserRole {
  SUPER_ADMIN = 'super_admin',
  BRAND_MANAGER = 'brand_manager',
  STORE_MANAGER = 'store_manager',
  EMPLOYEE = 'employee'
}

// 사용자 권한 정의
export enum Permission {
  // 대시보드
  VIEW_DASHBOARD = 'view_dashboard',
  
  // 직원 관리
  VIEW_EMPLOYEES = 'view_employees',
  CREATE_EMPLOYEES = 'create_employees',
  EDIT_EMPLOYEES = 'edit_employees',
  DELETE_EMPLOYEES = 'delete_employees',
  APPROVE_EMPLOYEES = 'approve_employees',
  
  // 스케줄 관리
  VIEW_SCHEDULES = 'view_schedules',
  CREATE_SCHEDULES = 'create_schedules',
  EDIT_SCHEDULES = 'edit_schedules',
  DELETE_SCHEDULES = 'delete_schedules',
  
  // 주문 관리
  VIEW_ORDERS = 'view_orders',
  CREATE_ORDERS = 'create_orders',
  EDIT_ORDERS = 'edit_orders',
  DELETE_ORDERS = 'delete_orders',
  
  // 재고 관리
  VIEW_INVENTORY = 'view_inventory',
  CREATE_INVENTORY = 'create_inventory',
  EDIT_INVENTORY = 'edit_inventory',
  DELETE_INVENTORY = 'delete_inventory',
  
  // 출퇴근 관리
  VIEW_ATTENDANCE = 'view_attendance',
  CREATE_ATTENDANCE = 'create_attendance',
  EDIT_ATTENDANCE = 'edit_attendance',
  
  // 알림 관리
  VIEW_NOTIFICATIONS = 'view_notifications',
  SEND_NOTIFICATIONS = 'send_notifications',
  
  // 리포트
  VIEW_REPORTS = 'view_reports',
  EXPORT_REPORTS = 'export_reports',
  
  // 시스템 관리
  VIEW_SYSTEM = 'view_system',
  MANAGE_SYSTEM = 'manage_system'
}

// 역할별 기본 권한 매핑
export const ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
  [UserRole.SUPER_ADMIN]: [
    // 모든 권한
    ...Object.values(Permission)
  ],
  
  [UserRole.BRAND_MANAGER]: [
    // 대시보드
    Permission.VIEW_DASHBOARD,
    
    // 직원 관리 (제한적)
    Permission.VIEW_EMPLOYEES,
    Permission.APPROVE_EMPLOYEES,
    
    // 스케줄 관리
    Permission.VIEW_SCHEDULES,
    Permission.CREATE_SCHEDULES,
    Permission.EDIT_SCHEDULES,
    
    // 주문 관리
    Permission.VIEW_ORDERS,
    
    // 재고 관리
    Permission.VIEW_INVENTORY,
    
    // 출퇴근 관리
    Permission.VIEW_ATTENDANCE,
    
    // 알림 관리
    Permission.VIEW_NOTIFICATIONS,
    Permission.SEND_NOTIFICATIONS,
    
    // 리포트
    Permission.VIEW_REPORTS,
    Permission.EXPORT_REPORTS
  ],
  
  [UserRole.STORE_MANAGER]: [
    // 대시보드
    Permission.VIEW_DASHBOARD,
    
    // 직원 관리 (자신의 매장만)
    Permission.VIEW_EMPLOYEES,
    Permission.CREATE_EMPLOYEES,
    Permission.EDIT_EMPLOYEES,
    
    // 스케줄 관리
    Permission.VIEW_SCHEDULES,
    Permission.CREATE_SCHEDULES,
    Permission.EDIT_SCHEDULES,
    Permission.DELETE_SCHEDULES,
    
    // 주문 관리
    Permission.VIEW_ORDERS,
    Permission.CREATE_ORDERS,
    Permission.EDIT_ORDERS,
    
    // 재고 관리
    Permission.VIEW_INVENTORY,
    Permission.CREATE_INVENTORY,
    Permission.EDIT_INVENTORY,
    
    // 출퇴근 관리
    Permission.VIEW_ATTENDANCE,
    Permission.CREATE_ATTENDANCE,
    Permission.EDIT_ATTENDANCE,
    
    // 알림 관리
    Permission.VIEW_NOTIFICATIONS,
    Permission.SEND_NOTIFICATIONS,
    
    // 리포트
    Permission.VIEW_REPORTS
  ],
  
  [UserRole.EMPLOYEE]: [
    // 대시보드
    Permission.VIEW_DASHBOARD,
    
    // 스케줄 관리 (자신의 스케줄만)
    Permission.VIEW_SCHEDULES,
    
    // 주문 관리 (처리만)
    Permission.VIEW_ORDERS,
    Permission.EDIT_ORDERS,
    
    // 재고 관리 (조회만)
    Permission.VIEW_INVENTORY,
    
    // 출퇴근 관리 (자신의 출퇴근만)
    Permission.VIEW_ATTENDANCE,
    Permission.CREATE_ATTENDANCE,
    
    // 알림 관리 (조회만)
    Permission.VIEW_NOTIFICATIONS
  ]
};

// 사용자 정보 인터페이스
export interface User {
  id: number;
  username: string;
  email: string;
  name: string;
  role: UserRole;
  branch_id?: number;
  permissions: Permission[];
  created_at: string;
  last_login?: string;
}

// 인증 컨텍스트 타입
export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  hasPermission: (permission: Permission) => boolean;
  hasRole: (role: UserRole) => boolean;
  refreshUser: () => Promise<void>;
}

// 권한 체크 유틸리티
export class PermissionChecker {
  private user: User | null;

  constructor(user: User | null) {
    this.user = user;
  }

  // 특정 권한 확인
  hasPermission(permission: Permission): boolean {
    if (!this.user) return false;
    return this.user.permissions.includes(permission);
  }

  // 여러 권한 중 하나라도 있는지 확인
  hasAnyPermission(permissions: Permission[]): boolean {
    return permissions.some(permission => this.hasPermission(permission));
  }

  // 모든 권한이 있는지 확인
  hasAllPermissions(permissions: Permission[]): boolean {
    return permissions.every(permission => this.hasPermission(permission));
  }

  // 특정 역할 확인
  hasRole(role: UserRole): boolean {
    if (!this.user) return false;
    return this.user.role === role;
  }

  // 여러 역할 중 하나라도 있는지 확인
  hasAnyRole(roles: UserRole[]): boolean {
    return roles.some(role => this.hasRole(role));
  }

  // 슈퍼 관리자인지 확인
  isSuperAdmin(): boolean {
    return this.hasRole(UserRole.SUPER_ADMIN);
  }

  // 브랜드 관리자인지 확인
  isBrandManager(): boolean {
    return this.hasRole(UserRole.BRAND_MANAGER);
  }

  // 매장 관리자인지 확인
  isStoreManager(): boolean {
    return this.hasRole(UserRole.STORE_MANAGER);
  }

  // 직원인지 확인
  isEmployee(): boolean {
    return this.hasRole(UserRole.EMPLOYEE);
  }

  // 관리자 역할인지 확인 (슈퍼 관리자, 브랜드 관리자, 매장 관리자)
  isManager(): boolean {
    return this.hasAnyRole([UserRole.SUPER_ADMIN, UserRole.BRAND_MANAGER, UserRole.STORE_MANAGER]);
  }

  // 백엔드 접근 권한이 있는지 확인
  canAccessBackend(): boolean {
    return this.isSuperAdmin();
  }

  // 프론트 접근 권한이 있는지 확인
  canAccessFrontend(): boolean {
    return !this.isSuperAdmin();
  }
}

// 라우트 보호 컴포넌트를 위한 타입
export interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermissions?: Permission[];
  requiredRoles?: UserRole[];
  fallback?: React.ReactNode;
  redirectTo?: string;
}

// 권한 기반 컴포넌트 렌더링을 위한 타입
export interface PermissionGuardProps {
  children: React.ReactNode;
  permission?: Permission;
  permissions?: Permission[];
  role?: UserRole;
  roles?: UserRole[];
  fallback?: React.ReactNode;
} 