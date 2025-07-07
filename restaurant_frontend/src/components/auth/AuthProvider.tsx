'use client';

import React, { createContext, useContext, useEffect } from 'react';
import { useAuth, useAutoRefresh } from '@/lib/useAuth';
import { AuthContextType } from '@/lib/auth';

// 인증 컨텍스트 생성
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 인증 컨텍스트 사용 훅
export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const auth = useAuth();
  
  // 자동 토큰 갱신 활성화
  useAutoRefresh();

  // 초기 인증 상태 확인
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token && !auth.isAuthenticated) {
      // 토큰이 있지만 인증 상태가 아닌 경우 사용자 정보 새로고침
      auth.refreshUser();
    }
  }, []);

  return (
    <AuthContext.Provider value={auth}>
      {children}
    </AuthContext.Provider>
  );
}; 