'use client';

import { useEffect } from 'react';
import useErrorHandler from '@/hooks/useErrorHandler';

export default function GlobalErrorHandler() {
  const { handleError } = useErrorHandler({
    showToast: true,
    logToConsole: true,
    redirectOnAuthError: true,
  });

  useEffect(() => {
    // 전역 에러 이벤트 리스너
    const handleGlobalError = (event: ErrorEvent) => {
      handleError(new Error(event.message));
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      handleError(new Error(event.reason?.message || 'Promise rejection'));
    };

    // 전역 에러 이벤트 등록
    window.addEventListener('error', handleGlobalError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleGlobalError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, [handleError]);

  // 이 컴포넌트는 UI를 렌더링하지 않음
  return null;
} 