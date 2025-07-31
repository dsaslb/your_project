'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useDataCache } from './useDataCache';
import { useLoadingState } from './useLoadingState';
import { useErrorHandler } from './useErrorHandler';
import { apiClient } from '@/lib/api-client';

export interface UseOptimizedDataOptions<T> {
  key: string;
  fetchFunction: () => Promise<T>;
  ttl?: number;
  staleWhileRevalidate?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
  dependencies?: any[];
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
}

export function useOptimizedData<T>(options: UseOptimizedDataOptions<T>) {
  const {
    key,
    fetchFunction,
    ttl = 5 * 60 * 1000, // 5분
    staleWhileRevalidate = 30 * 1000, // 30초
    autoRefresh = false,
    refreshInterval = 60 * 1000, // 1분
    dependencies = [],
    onSuccess,
    onError
  } = options;

  const {
    data,
    isLoading,
    error,
    lastUpdated,
    refreshData,
    invalidateCache
  } = useDataCache<T>({
    key,
    ttl,
    staleWhileRevalidate,
    autoRefresh,
    refreshInterval
  });

  const { withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();
  const abortControllerRef = useRef<AbortController | null>(null);

  // 데이터 로드
  const loadData = useCallback(async (force = false) => {
    return await withLoading(async () => {
      try {
        // 이전 요청 취소
        if (abortControllerRef.current) {
          abortControllerRef.current.abort();
        }

        abortControllerRef.current = new AbortController();
        
        const result = await refreshData(fetchFunction, force);
        
        if (onSuccess && result) {
          onSuccess(result);
        }
        
        return result;
      } catch (error) {
        const err = error as Error;
        handleError(err);
        if (onError) {
          onError(err);
        }
        throw err;
      }
    });
  }, [fetchFunction, withLoading, handleError, onSuccess, onError, refreshData]);

  // 의존성 변경 시 자동 새로고침
  useEffect(() => {
    loadData();
  }, [...dependencies, loadData]);

  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    data,
    isLoading,
    error,
    lastUpdated,
    loadData,
    invalidateCache,
    refreshData: () => loadData(true)
  };
}

// 특정 데이터 타입별 최적화된 훅들
export function useIndustries() {
  return useOptimizedData({
    key: 'industries',
    fetchFunction: async () => {
      const response = await (apiClient as any).getIndustries();
      return response.data || [];
    },
    ttl: 10 * 60 * 1000, // 10분
    autoRefresh: true,
    refreshInterval: 5 * 60 * 1000 // 5분
  });
}

export function useBrands(industryId?: number) {
  return useOptimizedData({
    key: `brands-${industryId || 'all'}`,
    fetchFunction: async () => {
      const params = industryId ? { industry_id: industryId } : {};
      const response = await (apiClient as any).getBrands(params);
      return response.data || [];
    },
    ttl: 10 * 60 * 1000,
    autoRefresh: true,
    refreshInterval: 5 * 60 * 1000,
    dependencies: [industryId]
  });
}

export function useStores(brandId?: number) {
  return useOptimizedData({
    key: `stores-${brandId || 'all'}`,
    fetchFunction: async () => {
      const params = brandId ? { brand_id: brandId } : {};
      const response = await (apiClient as any).getStores(params);
      return response.data || [];
    },
    ttl: 10 * 60 * 1000,
    autoRefresh: true,
    refreshInterval: 5 * 60 * 1000,
    dependencies: [brandId]
  });
}

export function useEmployees(storeId?: number) {
  return useOptimizedData({
    key: `employees-${storeId || 'all'}`,
    fetchFunction: async () => {
      const params = storeId ? { store_id: storeId } : {};
      const response = await (apiClient as any).getEmployees(params);
      return response.data || [];
    },
    ttl: 10 * 60 * 1000,
    autoRefresh: true,
    refreshInterval: 5 * 60 * 1000,
    dependencies: [storeId]
  });
} 