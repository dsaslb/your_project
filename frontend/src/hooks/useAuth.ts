import { useDataStore } from '@/store';
import { useRouter } from 'next/navigation';
import { useEffect, useState, useCallback } from 'react';

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

// JWT 토큰 관리
class TokenManager {
  private static readonly TOKEN_KEY = 'auth_token';
  private static readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private static readonly TOKEN_EXPIRY_KEY = 'token_expiry';

  static setTokens(accessToken: string, refreshToken?: string, expiresIn?: number) {
    localStorage.setItem(this.TOKEN_KEY, accessToken);
    if (refreshToken) {
      localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
    }
    if (expiresIn) {
      const expiryTime = Date.now() + expiresIn * 1000;
      localStorage.setItem(this.TOKEN_EXPIRY_KEY, expiryTime.toString());
    }
  }

  static getAccessToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  static getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  static isTokenExpired(): boolean {
    const expiryTime = localStorage.getItem(this.TOKEN_EXPIRY_KEY);
    if (!expiryTime) return true;
    
    // 5분 전에 만료로 간주 (새로고침 여유 시간)
    const bufferTime = 5 * 60 * 1000;
    return Date.now() > parseInt(expiryTime) - bufferTime;
  }

  static clearTokens() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    localStorage.removeItem(this.TOKEN_EXPIRY_KEY);
  }

  static decodeToken(token: string) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error('Token decode error:', error);
      return null;
    }
  }
}

// 보안 설정
const SECURITY_CONFIG = {
  API_BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
  TOKEN_REFRESH_THRESHOLD: 5 * 60 * 1000, // 5분
  MAX_LOGIN_ATTEMPTS: 5,
  LOCKOUT_DURATION: 15 * 60 * 1000, // 15분
  SESSION_TIMEOUT: 30 * 60 * 1000, // 30분
};

export const useAuth = () => {
  const { currentUser, setCurrentUser } = useDataStore();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [loginAttempts, setLoginAttempts] = useState(0);
  const [lockoutUntil, setLockoutUntil] = useState<number | null>(null);

  // 보안 설정
  const SECURITY_CONFIG = {
    API_BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
    MAX_LOGIN_ATTEMPTS: 5,
    LOCKOUT_DURATION: 15 * 60 * 1000, // 15분
    API_RATE_LIMIT: {
      requests: 100,
      windowMs: 15 * 60 * 1000 // 15분
    }
  };

  // 개발용: 인증 우회 더미 유저
  const dummyUser: User = {
    id: 1,
    username: 'devuser',
    email: 'devuser@example.com',
    name: '개발자',
    role: 'admin',
    grade: 'ceo',
    status: 'approved',
    permissions: { all: { view: true, edit: true, create: true, delete: true, approve: true } },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  // 보안 API 호출 함수
  const secureApiCall = useCallback(async (endpoint: string, options: RequestInit = {}) => {
    const token = TokenManager.getAccessToken();
    
    // 토큰이 만료되었거나 없으면 새로고침 시도
    if (token && TokenManager.isTokenExpired()) {
      const refreshResult = await refreshToken();
      if (!refreshResult.success) {
        // 새로고침 실패 시 로그아웃
        logout();
        throw new Error('세션이 만료되었습니다. 다시 로그인해주세요.');
      }
    }

    const currentToken = TokenManager.getAccessToken();
    const response = await fetch(`${SECURITY_CONFIG.API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(currentToken && { 'Authorization': `Bearer ${currentToken}` }),
        ...options.headers,
      },
    });

    // 401 에러 시 토큰 새로고침 시도
    if (response.status === 401) {
      const refreshResult = await refreshToken();
      if (refreshResult.success) {
        // 새로고침 성공 시 원래 요청 재시도
        const newToken = TokenManager.getAccessToken();
        const retryResponse = await fetch(`${SECURITY_CONFIG.API_BASE_URL}${endpoint}`, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...(newToken && { 'Authorization': `Bearer ${newToken}` }),
            ...options.headers,
          },
        });
        return retryResponse.json();
      } else {
        logout();
        throw new Error('인증이 만료되었습니다.');
      }
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }, []);

  // 토큰 새로고침
  const refreshToken = useCallback(async () => {
    const refreshToken = TokenManager.getRefreshToken();
    if (!refreshToken) {
      return { success: false, error: '새로고침 토큰이 없습니다.' };
    }

    try {
      const response = await fetch(`${SECURITY_CONFIG.API_BASE_URL}/api/security/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data?.access_token) {
          TokenManager.setTokens(
            data.data.access_token,
            data.data.refresh_token,
            data.data.expires_in
          );
          return { success: true };
        }
      }
      
      return { success: false, error: '토큰 새로고침에 실패했습니다.' };
    } catch (error) {
      console.error('Token refresh error:', error);
      return { success: false, error: '토큰 새로고침 중 오류가 발생했습니다.' };
    }
  }, []);

  // 로그인 시도 제한 확인
  const checkLoginAttempts = useCallback(() => {
    if (lockoutUntil && Date.now() < lockoutUntil) {
      const remainingTime = Math.ceil((lockoutUntil - Date.now()) / 1000 / 60);
      throw new Error(`로그인이 일시적으로 차단되었습니다. ${remainingTime}분 후 다시 시도해주세요.`);
    }
  }, [lockoutUntil]);

  // 로그인 실패 처리
  const handleLoginFailure = useCallback(() => {
    const newAttempts = loginAttempts + 1;
    setLoginAttempts(newAttempts);
    
    if (newAttempts >= SECURITY_CONFIG.MAX_LOGIN_ATTEMPTS) {
      const lockoutTime = Date.now() + SECURITY_CONFIG.LOCKOUT_DURATION;
      setLockoutUntil(lockoutTime);
      setLoginAttempts(0);
    }
  }, [loginAttempts]);

  // 권한 확인 함수 (보안 강화)
  const hasPermission = useCallback((module: string, action: string): boolean => {
    if (!currentUser || !currentUser.permissions) {
      return false;
    }

    // 토큰 검증
    const token = TokenManager.getAccessToken();
    if (!token) {
      return false;
    }

    const decodedToken = TokenManager.decodeToken(token);
    if (!decodedToken || decodedToken.exp * 1000 < Date.now()) {
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
  }, [currentUser]);

  // 모듈 접근 권한 확인
  const canAccessModule = useCallback((module: string): boolean => {
    return hasPermission(module, 'view');
  }, [hasPermission]);

  // 모듈 편집 권한 확인
  const canEditModule = useCallback((module: string): boolean => {
    return hasPermission(module, 'edit');
  }, [hasPermission]);

  // 모듈 내 생성 권한 확인
  const canCreateInModule = useCallback((module: string): boolean => {
    return hasPermission(module, 'create');
  }, [hasPermission]);

  // 모듈 내 삭제 권한 확인
  const canDeleteInModule = useCallback((module: string): boolean => {
    return hasPermission(module, 'delete');
  }, [hasPermission]);

  // 모듈 내 승인 권한 확인
  const canApproveInModule = useCallback((module: string): boolean => {
    return hasPermission(module, 'approve');
  }, [hasPermission]);

  // 역할 기반 권한 확인
  const isAdmin = useCallback((): boolean => {
    return currentUser?.role === 'admin';
  }, [currentUser]);

  const isBrandAdmin = useCallback((): boolean => {
    return currentUser?.role === 'brand_admin';
  }, [currentUser]);

  const isStoreAdmin = useCallback((): boolean => {
    return currentUser?.role === 'store_admin';
  }, [currentUser]);

  const isEmployee = useCallback((): boolean => {
    return currentUser?.role === 'employee';
  }, [currentUser]);

  const isManager = useCallback((): boolean => {
    return currentUser?.role === 'manager';
  }, [currentUser]);

  // 그룹/프랜차이즈 최고관리자 확인
  const isGroupAdmin = useCallback((): boolean => {
    return currentUser?.role === 'admin' && hasPermission('group_admin', 'view');
  }, [currentUser, hasPermission]);

  // 1인 사장님 모드 확인
  const isOwner = useCallback((): boolean => {
    return currentUser?.role === 'admin' && !isGroupAdmin();
  }, [currentUser, isGroupAdmin]);

  // 1인 사장님 모드 (모든 메뉴 접근 가능)
  const isSoloMode = useCallback((): boolean => {
    return isOwner() || hasPermission('solo_mode', 'view');
  }, [isOwner, hasPermission]);

  // 그룹/프랜차이즈 모드 (최고관리자 메뉴만 접근 가능)
  const isFranchiseMode = useCallback((): boolean => {
    return isGroupAdmin() || hasPermission('franchise_mode', 'view');
  }, [isGroupAdmin, hasPermission]);

  // 모든 메뉴 접근 가능 여부 (1인 사장님 모드)
  const canAccessAllMenus = useCallback((): boolean => {
    return isSoloMode();
  }, [isSoloMode]);

  // 최고관리자 전용 메뉴 접근 가능 여부 (그룹/프랜차이즈 모드)
  const canAccessAdminOnlyMenus = useCallback((): boolean => {
    return isFranchiseMode();
  }, [isFranchiseMode]);

  // 현재 사용자의 대시보드 모드 반환
  const getDashboardMode = useCallback((): 'solo' | 'franchise' | 'employee' => {
    if (isSoloMode()) {
      return 'solo';
    } else if (isFranchiseMode()) {
      return 'franchise';
    } else {
      return 'employee';
    }
  }, [isSoloMode, isFranchiseMode]);

  // 권한 요약 정보
  const getPermissionSummary = useCallback(() => {
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
  }, [currentUser]);

  // 로그인 상태 확인 (보안 강화)
  const isAuthenticated = useCallback((): boolean => {
    if (!currentUser) return false;
    
    const token = TokenManager.getAccessToken();
    if (!token) return false;
    
    // 토큰 만료 확인
    if (TokenManager.isTokenExpired()) {
      return false;
    }
    
    return true;
  }, [currentUser]);

  // 로그인 체크 및 리다이렉트
  const requireAuth = useCallback((redirectTo: string = '/login') => {
    if (!isAuthenticated()) {
      router.push(redirectTo);
      return false;
    }
    return true;
  }, [isAuthenticated, router]);

  // 권한 체크 및 리다이렉트
  const requirePermission = useCallback((module: string, action: string, redirectTo: string = '/unauthorized') => {
    if (!isAuthenticated()) {
      router.push('/login');
      return false;
    }

    if (!hasPermission(module, action)) {
      router.push(redirectTo);
      return false;
    }

    return true;
  }, [isAuthenticated, hasPermission, router]);

  // 안전한 로그아웃
  const logout = useCallback(() => {
    // 서버에 로그아웃 요청
    const token = TokenManager.getAccessToken();
    if (token) {
      fetch(`${SECURITY_CONFIG.API_BASE_URL}/api/security/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }).catch(error => {
        console.error('Logout API error:', error);
      });
    }
    
    // 로컬 상태 정리
    TokenManager.clearTokens();
    setCurrentUser(null);
    setLoginAttempts(0);
    setLockoutUntil(null);
    
    // 페이지 이동
    router.push('/login');
  }, [setCurrentUser, router]);

  // 보안 강화된 로그인 함수
  const login = useCallback(async ({ username, password }: { username: string; password: string }) => {
    setIsLoading(true);
    
    try {
      // 로그인 시도 제한 확인
      checkLoginAttempts();
      
      // 백엔드 로그인 API 호출
      const response = await fetch(`${SECURITY_CONFIG.API_BASE_URL}/api/security/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok && data.success && data.data?.user) {
        // 로그인 성공 시 토큰 저장
        if (data.data.access_token) {
          TokenManager.setTokens(
            data.data.access_token,
            data.data.refresh_token,
            data.data.expires_in
          );
        }
        
        // 사용자 정보를 스토어에 저장
        setCurrentUser(data.data.user);
        setLoginAttempts(0);
        setLockoutUntil(null);
        
        return { success: true, data: data.data };
      } else {
        // 로그인 실패 처리
        handleLoginFailure();
        return { success: false, error: data.error || '로그인에 실패했습니다.' };
      }
    } catch (error: any) {
      console.error('Login error:', error);
      
      // 개발용: 백엔드 연결 실패 시 더미 로그인 허용
      if (username === 'admin' && password === 'admin') {
        setCurrentUser(dummyUser);
        setLoginAttempts(0);
        setLockoutUntil(null);
        return { success: true, data: { user: dummyUser } };
      }
      
      handleLoginFailure();
      return { success: false, error: '서버 연결에 실패했습니다. 다시 시도해주세요.' };
    } finally {
      setIsLoading(false);
    }
  }, [checkLoginAttempts, handleLoginFailure, setCurrentUser]);

  // 세션 모니터링
  useEffect(() => {
    const checkSession = () => {
      if (currentUser && TokenManager.isTokenExpired()) {
        // 토큰이 만료되었으면 새로고침 시도
        refreshToken().then(result => {
          if (!result.success) {
            logout();
          }
        });
      }
    };

    // 주기적으로 세션 확인 (5분마다)
    const interval = setInterval(checkSession, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [currentUser, refreshToken, logout]);

  // 초기 로드 시 사용자 정보 확인
  useEffect(() => {
    const initializeAuth = async () => {
      // 개발용: 항상 더미 유저로 자동 로그인
      if (!currentUser) {
        setCurrentUser(dummyUser);
        console.log('개발 모드: 자동 로그인 완료');
      }
      
      setIsLoading(false);
    };

    initializeAuth();
  }, [currentUser, setCurrentUser]);

  return {
    currentUser: currentUser || dummyUser,
    isLoading,
    isAuthenticated,
    hasPermission,
    canAccessModule,
    canEditModule,
    canCreateInModule,
    canDeleteInModule,
    canApproveInModule,
    isAdmin,
    isBrandAdmin,
    isStoreAdmin,
    isEmployee,
    isManager,
    isOwner,
    isGroupAdmin,
    isSoloMode,
    isFranchiseMode,
    canAccessAllMenus,
    canAccessAdminOnlyMenus,
    getDashboardMode,
    getPermissionSummary,
    requireAuth,
    requirePermission,
    logout,
    login,
    secureApiCall,
    loginAttempts,
    lockoutUntil,
  };
}; 