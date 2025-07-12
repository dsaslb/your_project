'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';

// 사용자 타입 정의
interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'manager' | 'employee' | 'super_admin';
  permissions: string[];
  branch_id?: string;
  brand_id?: string;
}

// 인증 컨텍스트 타입
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
}

// 기본값
const defaultAuthContext: AuthContextType = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  login: async () => false,
  logout: async () => {},
  refreshToken: async () => {},
  hasPermission: () => false,
  hasRole: () => false,
};

// 컨텍스트 생성
const AuthContext = createContext<AuthContextType>(defaultAuthContext);

// 인증 프로바이더 컴포넌트
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 토큰 관리
  const getToken = (): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  };

  const setToken = (token: string): void => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  };

  const removeToken = (): void => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  };

  // API 호출 함수
  const apiCall = async (endpoint: string, options: RequestInit = {}) => {
    const token = getToken();
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
    
    const response = await fetch(`${baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API 호출 실패: ${response.status}`);
    }

    return response.json();
  };

  // 로그인 함수
  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      
      const response = await apiCall('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });

      if (response.token) {
        setToken(response.token);
        setUser(response.user);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('로그인 실패:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // 로그아웃 함수
  const logout = async (): Promise<void> => {
    try {
      await apiCall('/api/auth/logout', { method: 'POST' });
    } catch (error) {
      console.error('로그아웃 API 호출 실패:', error);
    } finally {
      removeToken();
      setUser(null);
    }
  };

  // 토큰 갱신 함수
  const refreshToken = async (): Promise<void> => {
    try {
      const response = await apiCall('/api/auth/refresh', { method: 'POST' });
      if (response.token) {
        setToken(response.token);
        setUser(response.user);
      }
    } catch (error) {
      console.error('토큰 갱신 실패:', error);
      await logout();
    }
  };

  // 권한 확인 함수
  const hasPermission = (permission: string): boolean => {
    if (!user) return false;
    return user.permissions.includes(permission) || user.role === 'super_admin';
  };

  // 역할 확인 함수
  const hasRole = (role: string): boolean => {
    if (!user) return false;
    return user.role === role || user.role === 'super_admin';
  };

  // 초기 인증 상태 확인
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = getToken();
        if (token) {
          const response = await apiCall('/api/auth/me');
          setUser(response.user);
        }
      } catch (error) {
        console.error('인증 상태 확인 실패:', error);
        removeToken();
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  // 토큰 자동 갱신
  useEffect(() => {
    if (!user) return;

    const interval = setInterval(() => {
      refreshToken();
    }, 14 * 60 * 1000); // 14분마다 갱신

    return () => clearInterval(interval);
  }, [user]);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    refreshToken,
    hasPermission,
    hasRole,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// 커스텀 훅
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth는 AuthProvider 내에서 사용되어야 합니다');
  }
  return context;
};

export default AuthProvider; 