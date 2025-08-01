import React from 'react';

// 보안 유틸리티 함수들
export class SecurityUtils {
  // XSS 방지를 위한 HTML 이스케이프
  static escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // SQL 인젝션 방지를 위한 입력 검증
  static sanitizeInput(input: string): string {
    return input
      .replace(/[<>'"]/g, '')
      .trim()
      .substring(0, 1000); // 최대 길이 제한
  }

  // CSRF 토큰 생성
  static generateCSRFToken(): string {
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }

  // 비밀번호 강도 검증
  static validatePassword(password: string): {
    isValid: boolean;
    score: number;
    feedback: string[];
  } {
    const feedback: string[] = [];
    let score = 0;

    // 최소 길이 검증
    if (password.length < 8) {
      feedback.push('비밀번호는 최소 8자 이상이어야 합니다.');
    } else {
      score += 1;
    }

    // 대문자 포함 검증
    if (!/[A-Z]/.test(password)) {
      feedback.push('대문자를 포함해야 합니다.');
    } else {
      score += 1;
    }

    // 소문자 포함 검증
    if (!/[a-z]/.test(password)) {
      feedback.push('소문자를 포함해야 합니다.');
    } else {
      score += 1;
    }

    // 숫자 포함 검증
    if (!/\d/.test(password)) {
      feedback.push('숫자를 포함해야 합니다.');
    } else {
      score += 1;
    }

    // 특수문자 포함 검증
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      feedback.push('특수문자를 포함해야 합니다.');
    } else {
      score += 1;
    }

    return {
      isValid: score >= 4,
      score,
      feedback
    };
  }

  // 이메일 형식 검증
  static validateEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // 전화번호 형식 검증
  static validatePhone(phone: string): boolean {
    const phoneRegex = /^[0-9-+\s()]{10,15}$/;
    return phoneRegex.test(phone);
  }

  // 파일 업로드 보안 검증
  static validateFileUpload(file: File): {
    isValid: boolean;
    error?: string;
  } {
    // 파일 크기 제한 (10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      return {
        isValid: false,
        error: '파일 크기는 10MB를 초과할 수 없습니다.'
      };
    }

    // 허용된 파일 타입
    const allowedTypes = [
      'image/jpeg',
      'image/png',
      'image/gif',
      'image/webp',
      'application/pdf',
      'text/plain',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];

    if (!allowedTypes.includes(file.type)) {
      return {
        isValid: false,
        error: '허용되지 않는 파일 형식입니다.'
      };
    }

    return { isValid: true };
  }

  // 세션 하이재킹 방지를 위한 세션 ID 검증
  static validateSessionId(sessionId: string): boolean {
    return /^[a-zA-Z0-9]{32,64}$/.test(sessionId);
  }

  // Rate Limiting을 위한 간단한 구현
  static createRateLimiter(maxRequests: number, windowMs: number) {
    const requests = new Map<string, number[]>();

    return (identifier: string): boolean => {
      const now = Date.now();
      const windowStart = now - windowMs;

      if (!requests.has(identifier)) {
        requests.set(identifier, [now]);
        return true;
      }

      const userRequests = requests.get(identifier)!;
      const recentRequests = userRequests.filter(time => time > windowStart);

      if (recentRequests.length >= maxRequests) {
        return false;
      }

      recentRequests.push(now);
      requests.set(identifier, recentRequests);
      return true;
    };
  }

  // 로그인 시도 제한
  static createLoginAttemptLimiter(maxAttempts: number, lockoutDuration: number) {
    const attempts = new Map<string, { count: number; lastAttempt: number; lockedUntil?: number }>();

    return {
      recordAttempt: (identifier: string): boolean => {
        const now = Date.now();
        const userAttempts = attempts.get(identifier);

        if (!userAttempts) {
          attempts.set(identifier, { count: 1, lastAttempt: now });
          return true;
        }

        // 잠금 해제 확인
        if (userAttempts.lockedUntil && now > userAttempts.lockedUntil) {
          attempts.set(identifier, { count: 1, lastAttempt: now });
          return true;
        }

        // 잠금 상태 확인
        if (userAttempts.lockedUntil && now < userAttempts.lockedUntil) {
          return false;
        }

        // 시도 횟수 증가
        const newCount = userAttempts.count + 1;
        const isLocked = newCount >= maxAttempts;

        attempts.set(identifier, {
          count: newCount,
          lastAttempt: now,
          lockedUntil: isLocked ? now + lockoutDuration : undefined
        });

        return !isLocked;
      },

      isLocked: (identifier: string): boolean => {
        const userAttempts = attempts.get(identifier);
        if (!userAttempts) return false;

        const now = Date.now();
        return !!(userAttempts.lockedUntil && now < userAttempts.lockedUntil);
      },

      getRemainingLockTime: (identifier: string): number => {
        const userAttempts = attempts.get(identifier);
        if (!userAttempts || !userAttempts.lockedUntil) return 0;

        const now = Date.now();
        return Math.max(0, userAttempts.lockedUntil - now);
      },

      reset: (identifier: string): void => {
        attempts.delete(identifier);
      }
    };
  }

  // 보안 헤더 설정
  static getSecurityHeaders(): Record<string, string> {
    return {
      'X-Frame-Options': 'DENY',
      'X-Content-Type-Options': 'nosniff',
      'X-XSS-Protection': '1; mode=block',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
      'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
      'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'none';"
    };
  }

  // 민감한 데이터 마스킹
  static maskSensitiveData(data: string, type: 'email' | 'phone' | 'creditCard'): string {
    switch (type) {
      case 'email':
        const [local, domain] = data.split('@');
        return `${local.substring(0, 2)}***@${domain}`;
      
      case 'phone':
        return data.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
      
      case 'creditCard':
        return data.replace(/\d(?=\d{4})/g, '*');
      
      default:
        return data;
    }
  }

  // 보안 로그 생성
  static createSecurityLog(
    event: string,
    userId?: string,
    details?: Record<string, any>
  ): void {
    const logEntry = {
      timestamp: new Date().toISOString(),
      event,
      userId,
      userAgent: typeof window !== 'undefined' ? window.navigator.userAgent : 'server',
      ip: 'client-ip', // 실제로는 서버에서 설정
      details
    };

    // 개발 환경에서는 콘솔에 출력
    if (process.env.NODE_ENV === 'development') {
      console.log('🔒 Security Log:', logEntry);
    }

    // 프로덕션에서는 보안 로그 서비스로 전송
    // TODO: 실제 보안 로그 서비스 연동
  }

  // 보안 이벤트 타입
  static readonly SECURITY_EVENTS = {
    LOGIN_ATTEMPT: 'login_attempt',
    LOGIN_SUCCESS: 'login_success',
    LOGIN_FAILURE: 'login_failure',
    LOGOUT: 'logout',
    PASSWORD_CHANGE: 'password_change',
    PERMISSION_CHANGE: 'permission_change',
    SUSPICIOUS_ACTIVITY: 'suspicious_activity',
    FILE_UPLOAD: 'file_upload',
    API_ACCESS: 'api_access'
  } as const;
}

// 보안 설정 상수
export const SECURITY_CONFIG = {
  // 토큰 관련
  TOKEN_REFRESH_THRESHOLD: 5 * 60 * 1000, // 5분
  SESSION_TIMEOUT: 30 * 60 * 1000, // 30분
  
  // 로그인 시도 제한
  MAX_LOGIN_ATTEMPTS: 5,
  LOCKOUT_DURATION: 15 * 60 * 1000, // 15분
  
  // Rate Limiting
  API_RATE_LIMIT: {
    requests: 100,
    windowMs: 15 * 60 * 1000 // 15분
  },
  
  // 파일 업로드
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_FILE_TYPES: [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'application/pdf'
  ],
  
  // 입력 검증
  MAX_INPUT_LENGTH: 1000,
  MIN_PASSWORD_LENGTH: 8,
  
  // 세션 관리
  SESSION_CHECK_INTERVAL: 60 * 1000, // 1분
  INACTIVE_TIMEOUT: 20 * 60 * 1000 // 20분
} as const;

// 보안 미들웨어
export class SecurityMiddleware {
  private static rateLimiter = SecurityUtils.createRateLimiter(
    SECURITY_CONFIG.API_RATE_LIMIT.requests,
    SECURITY_CONFIG.API_RATE_LIMIT.windowMs
  );

  private static loginLimiter = SecurityUtils.createLoginAttemptLimiter(
    SECURITY_CONFIG.MAX_LOGIN_ATTEMPTS,
    SECURITY_CONFIG.LOCKOUT_DURATION
  );

  // API 요청 보안 검증
  static validateApiRequest(identifier: string): boolean {
    return this.rateLimiter(identifier);
  }

  // 로그인 시도 검증
  static validateLoginAttempt(identifier: string): boolean {
    return this.loginLimiter.recordAttempt(identifier);
  }

  // 로그인 잠금 상태 확인
  static isLoginLocked(identifier: string): boolean {
    return this.loginLimiter.isLocked(identifier);
  }

  // 잠금 해제 시간 확인
  static getLoginLockRemainingTime(identifier: string): number {
    return this.loginLimiter.getRemainingLockTime(identifier);
  }

  // 로그인 성공 시 리셋
  static resetLoginAttempts(identifier: string): void {
    this.loginLimiter.reset(identifier);
  }
}

// 보안 훅
export const useSecurity = () => {
  const createSecureApiCall = React.useCallback(async (
    endpoint: string,
    options: RequestInit = {}
  ) => {
    const identifier = 'api-call'; // 실제로는 사용자 ID나 IP 사용
    
    if (!SecurityMiddleware.validateApiRequest(identifier)) {
      throw new Error('요청이 너무 많습니다. 잠시 후 다시 시도해주세요.');
    }

    try {
      const response = await fetch(endpoint, {
        ...options,
        headers: {
          ...SecurityUtils.getSecurityHeaders(),
          ...options.headers,
        },
      });

      if (!response.ok) {
        SecurityUtils.createSecurityLog(
          SecurityUtils.SECURITY_EVENTS.API_ACCESS,
          undefined,
          { endpoint, status: response.status }
        );
      }

      return response;
    } catch (error) {
      SecurityUtils.createSecurityLog(
        SecurityUtils.SECURITY_EVENTS.SUSPICIOUS_ACTIVITY,
        undefined,
        { endpoint, error: error instanceof Error ? error.message : String(error) }
      );
      throw error;
    }
  }, []);

  return {
    createSecureApiCall,
    validatePassword: SecurityUtils.validatePassword,
    validateEmail: SecurityUtils.validateEmail,
    validatePhone: SecurityUtils.validatePhone,
    validateFileUpload: SecurityUtils.validateFileUpload,
    maskSensitiveData: SecurityUtils.maskSensitiveData,
    escapeHtml: SecurityUtils.escapeHtml,
    sanitizeInput: SecurityUtils.sanitizeInput,
    generateCSRFToken: SecurityUtils.generateCSRFToken,
    createSecurityLog: SecurityUtils.createSecurityLog,
    SECURITY_CONFIG,
    SECURITY_EVENTS: SecurityUtils.SECURITY_EVENTS
  };
}; 