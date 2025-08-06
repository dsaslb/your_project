import { useState, useCallback } from 'react';

export interface LoadingState {
  isLoading: boolean;
  error: string | null;
  startLoading: () => void;
  stopLoading: () => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

export const useLoadingState = (): LoadingState => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setErrorState] = useState<string | null>(null);

  const startLoading = useCallback(() => {
    setIsLoading(true);
    setErrorState(null);
  }, []);

  const stopLoading = useCallback(() => {
    setIsLoading(false);
  }, []);

  const setError = useCallback((error: string | null) => {
    setErrorState(error);
    setIsLoading(false);
  }, []);

  const clearError = useCallback(() => {
    setErrorState(null);
  }, []);

  return {
    isLoading,
    error,
    startLoading,
    stopLoading,
    setError,
    clearError,
  };
}; 