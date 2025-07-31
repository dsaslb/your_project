'use client';

import { useState, useCallback, useRef } from 'react';

export interface LoadingState {
  isLoading: boolean;
  error: string | null;
  retryCount: number;
}

export interface UseLoadingStateOptions {
  initialLoading?: boolean;
  maxRetries?: number;
  retryDelay?: number;
}

export const useLoadingState = (options: UseLoadingStateOptions = {}) => {
  const {
    initialLoading = false,
    maxRetries = 3,
    retryDelay = 1000,
  } = options;

  const [state, setState] = useState<LoadingState>({
    isLoading: initialLoading,
    error: null,
    retryCount: 0,
  });

  const retryTimeoutRef = useRef<NodeJS.Timeout>();

  const setLoading = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, isLoading: loading }));
  }, []);

  const setError = useCallback((error: string | null) => {
    setState(prev => ({ ...prev, error, isLoading: false }));
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  const reset = useCallback(() => {
    setState({
      isLoading: false,
      error: null,
      retryCount: 0,
    });
  }, []);

  const retry = useCallback((operation: () => Promise<void>) => {
    if (state.retryCount >= maxRetries) {
      setError(`최대 재시도 횟수(${maxRetries})를 초과했습니다.`);
      return;
    }

    setState(prev => ({ ...prev, retryCount: prev.retryCount + 1, isLoading: true, error: null }));

    // 지연 후 재시도
    retryTimeoutRef.current = setTimeout(async () => {
      try {
        await operation();
        setState(prev => ({ ...prev, isLoading: false, error: null, retryCount: 0 }));
      } catch (error) {
        setError(error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.');
      }
    }, retryDelay);
  }, [state.retryCount, maxRetries, retryDelay, setError]);

  const withLoading = useCallback(async <T>(
    operation: () => Promise<T>,
    options: { showError?: boolean; errorMessage?: string } = {}
  ): Promise<T | null> => {
    const { showError = true, errorMessage } = options;

    setLoading(true);
    clearError();

    try {
      const result = await operation();
      setLoading(false);
      return result;
    } catch (error) {
      const message = errorMessage || (error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.');
      setError(message);
      
      if (showError) {
        console.error('Operation failed:', error);
      }
      
      return null;
    }
  }, [setLoading, clearError, setError]);

  // 컴포넌트 언마운트 시 타이머 정리
  const cleanup = useCallback(() => {
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
    }
  }, []);

  return {
    ...state,
    setLoading,
    setError,
    clearError,
    reset,
    retry,
    withLoading,
    cleanup,
  };
};

export default useLoadingState; 