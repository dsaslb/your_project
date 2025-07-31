'use client';

import { useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api-client';

// ApiError 클래스 정의
export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public details?: any,
    public status?: number
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export interface ErrorHandlerOptions {
  showToast?: boolean;
  logToConsole?: boolean;
  redirectOnAuthError?: boolean;
}

export const useErrorHandler = (options: ErrorHandlerOptions = {}) => {
  const {
    showToast = true,
    logToConsole = true,
    redirectOnAuthError = true,
  } = options;

  const handleError = useCallback((error: ApiError | Error) => {
    // 콘솔 로깅
    if (logToConsole) {
      console.error('Error caught by useErrorHandler:', error);
    }

    // API 에러 타입 확인
    if (error instanceof ApiError) {
      const { code, message, status } = error;

      // 특정 에러 코드별 처리
      switch (code) {
        case 'AUTH_REQUIRED':
        case 'TOKEN_EXPIRED':
          if (redirectOnAuthError) {
            window.location.href = '/login';
          }
          break;

        case 'FORBIDDEN':
          if (showToast) {
            toast.error('접근 권한이 없습니다.');
          }
          break;

        case 'NOT_FOUND':
          if (showToast) {
            toast.error('요청한 리소스를 찾을 수 없습니다.');
          }
          break;

        case 'NETWORK_ERROR':
          if (showToast) {
            toast.error('네트워크 연결을 확인해주세요.');
          }
          break;

        case 'SERVER_ERROR':
          if (showToast) {
            toast.error('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
          }
          break;

        default:
          if (showToast) {
            toast.error(message || '알 수 없는 오류가 발생했습니다.');
          }
      }
    } else {
      // 일반 JavaScript 에러
      if (showToast) {
        toast.error(error.message || '알 수 없는 오류가 발생했습니다.');
      }
    }
  }, [showToast, logToConsole, redirectOnAuthError]);

  // 전역 에러 리스너 등록
  useEffect(() => {
    // API 클라이언트의 전역 에러 구독은 현재 구현되지 않음
    // const unsubscribe = apiClient.onError(handleError);

    // 전역 window 에러 핸들러
    const handleGlobalError = (event: ErrorEvent) => {
      handleError(new Error(event.message));
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      handleError(new Error(event.reason?.message || 'Promise rejection'));
    };

    window.addEventListener('error', handleGlobalError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      // unsubscribe();
      window.removeEventListener('error', handleGlobalError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, [handleError]);

  return { handleError };
};

export default useErrorHandler; 