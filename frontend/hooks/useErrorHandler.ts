import { useCallback } from 'react';

export interface ErrorHandler {
  handleError: (error: unknown, context?: string) => void;
  handleApiError: (error: unknown, context?: string) => void;
  handleValidationError: (errors: Record<string, string[]>) => void;
}

export const useErrorHandler = (): ErrorHandler => {
  const handleError = useCallback((error: unknown, context?: string) => {
    console.error(`❌ ${context || '오류 발생'}:`, error);
    
    let message = '알 수 없는 오류가 발생했습니다.';
    
    if (error instanceof Error) {
      message = error.message;
    } else if (typeof error === 'string') {
      message = error;
    } else if (error && typeof error === 'object' && 'message' in error) {
      message = String(error.message);
    }
    
    // 토스트 알림이나 알림 시스템에 표시
    if (typeof window !== 'undefined' && window.toast) {
      window.toast.error(message);
    }
  }, []);

  const handleApiError = useCallback((error: unknown, context?: string) => {
    console.error(`❌ API ${context || '오류'}:`, error);
    
    let message = '서버 연결에 실패했습니다.';
    
    if (error && typeof error === 'object') {
      if ('status' in error) {
        const status = (error as any).status;
        if (status === 401) {
          message = '인증이 필요합니다. 다시 로그인해주세요.';
        } else if (status === 403) {
          message = '접근 권한이 없습니다.';
        } else if (status === 404) {
          message = '요청한 리소스를 찾을 수 없습니다.';
        } else if (status >= 500) {
          message = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
        }
      }
      
      if ('data' in error && error.data && typeof error.data === 'object') {
        if ('message' in error.data) {
          message = String(error.data.message);
        } else if ('error' in error.data) {
          message = String(error.data.error);
        }
      }
    }
    
    // 토스트 알림 표시
    if (typeof window !== 'undefined' && window.toast) {
      window.toast.error(message);
    }
  }, []);

  const handleValidationError = useCallback((errors: Record<string, string[]>) => {
    console.error('❌ 유효성 검사 오류:', errors);
    
    const messages = Object.values(errors).flat();
    const message = messages.length > 0 ? messages[0] : '입력 데이터가 올바르지 않습니다.';
    
    // 토스트 알림 표시
    if (typeof window !== 'undefined' && window.toast) {
      window.toast.error(message);
    }
  }, []);

  return {
    handleError,
    handleApiError,
    handleValidationError,
  };
}; 