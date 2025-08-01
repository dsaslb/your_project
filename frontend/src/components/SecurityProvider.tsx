'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { SecurityUtils, SecurityMiddleware, SECURITY_CONFIG } from '@/utils/security';

// 보안 컨텍스트 타입
interface SecurityContextType {
  // 보안 상태
  isSecure: boolean;
  securityLevel: 'low' | 'medium' | 'high';
  
  // 보안 기능
  validateInput: (input: string) => string;
  validatePassword: (password: string) => { isValid: boolean; score: number; feedback: string[] };
  validateEmail: (email: string) => boolean;
  validatePhone: (phone: string) => boolean;
  validateFileUpload: (file: File) => { isValid: boolean; error?: string };
  
  // 민감한 데이터 처리
  maskSensitiveData: (data: string, type: 'email' | 'phone' | 'creditCard') => string;
  escapeHtml: (text: string) => string;
  
  // 보안 로그
  logSecurityEvent: (event: string, details?: Record<string, any>) => void;
  
  // Rate Limiting
  checkRateLimit: (identifier: string) => boolean;
  
  // 로그인 보안
  checkLoginAttempts: (identifier: string) => boolean;
  isLoginLocked: (identifier: string) => boolean;
  getLoginLockRemainingTime: (identifier: string) => number;
  resetLoginAttempts: (identifier: string) => void;
  
  // 세션 보안
  checkSessionSecurity: () => boolean;
  refreshSession: () => void;
  
  // 보안 설정
  securityConfig: typeof SECURITY_CONFIG;
}

// 보안 컨텍스트 생성
const SecurityContext = createContext<SecurityContextType | undefined>(undefined);

// 보안 프로바이더 컴포넌트
export const SecurityProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isSecure, setIsSecure] = useState(true);
  const [securityLevel, setSecurityLevel] = useState<'low' | 'medium' | 'high'>('medium');
  const [lastActivity, setLastActivity] = useState(Date.now());

  // 보안 레벨 설정
  useEffect(() => {
    const determineSecurityLevel = () => {
      const isHttps = typeof window !== 'undefined' && window.location.protocol === 'https:';
      const isLocalhost = typeof window !== 'undefined' && window.location.hostname === 'localhost';
      
      if (isHttps && !isLocalhost) {
        setSecurityLevel('high');
      } else if (isHttps || isLocalhost) {
        setSecurityLevel('medium');
      } else {
        setSecurityLevel('low');
      }
    };

    determineSecurityLevel();
  }, []);

  // 사용자 활동 모니터링
  useEffect(() => {
    const updateActivity = () => {
      setLastActivity(Date.now());
    };

    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    events.forEach(event => {
      document.addEventListener(event, updateActivity, true);
    });

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, updateActivity, true);
      });
    };
  }, []);

  // 세션 보안 체크
  const checkSessionSecurity = useCallback(() => {
    const now = Date.now();
    const inactiveTime = now - lastActivity;
    
    // 비활성 시간 체크
    if (inactiveTime > SECURITY_CONFIG.INACTIVE_TIMEOUT) {
      setIsSecure(false);
      return false;
    }
    
    // HTTPS 체크
    if (typeof window !== 'undefined' && window.location.protocol !== 'https:' && window.location.hostname !== 'localhost') {
      setIsSecure(false);
      return false;
    }
    
    setIsSecure(true);
    return true;
  }, [lastActivity]);

  // 세션 새로고침
  const refreshSession = useCallback(() => {
    setLastActivity(Date.now());
    setIsSecure(true);
  }, []);

  // 입력 검증
  const validateInput = useCallback((input: string): string => {
    return SecurityUtils.sanitizeInput(input);
  }, []);

  // 비밀번호 검증
  const validatePassword = useCallback((password: string) => {
    return SecurityUtils.validatePassword(password);
  }, []);

  // 이메일 검증
  const validateEmail = useCallback((email: string): boolean => {
    return SecurityUtils.validateEmail(email);
  }, []);

  // 전화번호 검증
  const validatePhone = useCallback((phone: string): boolean => {
    return SecurityUtils.validatePhone(phone);
  }, []);

  // 파일 업로드 검증
  const validateFileUpload = useCallback((file: File) => {
    return SecurityUtils.validateFileUpload(file);
  }, []);

  // 민감한 데이터 마스킹
  const maskSensitiveData = useCallback((data: string, type: 'email' | 'phone' | 'creditCard'): string => {
    return SecurityUtils.maskSensitiveData(data, type);
  }, []);

  // HTML 이스케이프
  const escapeHtml = useCallback((text: string): string => {
    return SecurityUtils.escapeHtml(text);
  }, []);

  // 보안 로그
  const logSecurityEvent = useCallback((event: string, details?: Record<string, any>) => {
    SecurityUtils.createSecurityLog(event, undefined, details);
  }, []);

  // Rate Limiting 체크
  const checkRateLimit = useCallback((identifier: string): boolean => {
    return SecurityMiddleware.validateApiRequest(identifier);
  }, []);

  // 로그인 시도 체크
  const checkLoginAttempts = useCallback((identifier: string): boolean => {
    return SecurityMiddleware.validateLoginAttempt(identifier);
  }, []);

  // 로그인 잠금 상태 확인
  const isLoginLocked = useCallback((identifier: string): boolean => {
    return SecurityMiddleware.isLoginLocked(identifier);
  }, []);

  // 로그인 잠금 해제 시간 확인
  const getLoginLockRemainingTime = useCallback((identifier: string): number => {
    return SecurityMiddleware.getLoginLockRemainingTime(identifier);
  }, []);

  // 로그인 시도 리셋
  const resetLoginAttempts = useCallback((identifier: string): void => {
    SecurityMiddleware.resetLoginAttempts(identifier);
  }, []);

  // 주기적 보안 체크
  useEffect(() => {
    const securityCheckInterval = setInterval(() => {
      checkSessionSecurity();
    }, SECURITY_CONFIG.SESSION_CHECK_INTERVAL);

    return () => clearInterval(securityCheckInterval);
  }, [checkSessionSecurity]);

  // 보안 컨텍스트 값
  const contextValue: SecurityContextType = {
    isSecure,
    securityLevel,
    validateInput,
    validatePassword,
    validateEmail,
    validatePhone,
    validateFileUpload,
    maskSensitiveData,
    escapeHtml,
    logSecurityEvent,
    checkRateLimit,
    checkLoginAttempts,
    isLoginLocked,
    getLoginLockRemainingTime,
    resetLoginAttempts,
    checkSessionSecurity,
    refreshSession,
    securityConfig: SECURITY_CONFIG,
  };

  return (
    <SecurityContext.Provider value={contextValue}>
      {children}
    </SecurityContext.Provider>
  );
};

// 보안 훅
export const useSecurity = (): SecurityContextType => {
  const context = useContext(SecurityContext);
  if (context === undefined) {
    throw new Error('useSecurity must be used within a SecurityProvider');
  }
  return context;
};

// 보안 경고 컴포넌트
export const SecurityWarning: React.FC<{ message: string; onDismiss?: () => void }> = ({ 
  message, 
  onDismiss 
}) => {
  const { logSecurityEvent } = useSecurity();

  useEffect(() => {
    logSecurityEvent('security_warning', { message });
  }, [message, logSecurityEvent]);

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <p className="text-sm text-yellow-800">{message}</p>
        </div>
        {onDismiss && (
          <div className="ml-auto pl-3">
            <button
              onClick={onDismiss}
              className="inline-flex text-yellow-400 hover:text-yellow-500"
            >
              <span className="sr-only">닫기</span>
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// 보안 상태 표시 컴포넌트
export const SecurityStatus: React.FC = () => {
  const { isSecure, securityLevel } = useSecurity();

  const getStatusColor = () => {
    if (!isSecure) return 'text-red-600 bg-red-100';
    switch (securityLevel) {
      case 'high': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = () => {
    if (!isSecure) return '보안 위험';
    switch (securityLevel) {
      case 'high': return '보안 양호';
      case 'medium': return '보안 주의';
      case 'low': return '보안 위험';
      default: return '보안 상태 확인 중';
    }
  };

  return (
    <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor()}`}>
      <div className={`w-2 h-2 rounded-full mr-1 ${isSecure ? 'bg-current' : 'bg-red-500'}`}></div>
      {getStatusText()}
    </div>
  );
}; 