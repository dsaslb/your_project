'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient } from '@/lib/api-client';

export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}

export interface CacheOptions {
  ttl?: number; // Time to live in milliseconds
  staleWhileRevalidate?: number; // Stale while revalidate time in milliseconds
  maxAge?: number; // Maximum age in milliseconds
}

export interface UseDataCacheOptions extends CacheOptions {
  key: string;
  initialData?: any;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export const useDataCache = <T>(
  options: UseDataCacheOptions
) => {
  const {
    key,
    initialData,
    ttl = 5 * 60 * 1000, // 5 minutes
    staleWhileRevalidate = 30 * 1000, // 30 seconds
    maxAge = 30 * 60 * 1000, // 30 minutes
    autoRefresh = false,
    refreshInterval = 60 * 1000, // 1 minute
  } = options;

  const [data, setData] = useState<T | null>(initialData || null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<number | null>(null);

  const cacheRef = useRef<Map<string, CacheEntry<T>>>(new Map());
  const refreshTimeoutRef = useRef<NodeJS.Timeout>();
  const abortControllerRef = useRef<AbortController | null>(null);

  // 캐시에서 데이터 가져오기
  const getFromCache = useCallback((cacheKey: string): T | null => {
    const entry = cacheRef.current.get(cacheKey);
    if (!entry) return null;

    const now = Date.now();

    // 만료된 데이터
    if (now > entry.expiresAt) {
      cacheRef.current.delete(cacheKey);
      return null;
    }

    // stale while revalidate: 캐시된 데이터를 반환하되 백그라운드에서 새로고침
    if (now > entry.timestamp + staleWhileRevalidate) {
      // 백그라운드에서 새로고침 (사용자에게는 캐시된 데이터 표시)
      return entry.data;
    }

    return entry.data;
  }, [staleWhileRevalidate]);

  // 캐시에 데이터 저장
  const setCache = useCallback((cacheKey: string, data: T) => {
    const now = Date.now();
    const expiresAt = now + ttl;

    cacheRef.current.set(cacheKey, {
      data,
      timestamp: now,
      expiresAt,
    });

    // maxAge 초과 시 캐시 정리
    setTimeout(() => {
      cacheRef.current.delete(cacheKey);
    }, maxAge);
  }, [ttl, maxAge]);

  // 캐시 무효화
  const invalidateCache = useCallback((cacheKey?: string) => {
    if (cacheKey) {
      cacheRef.current.delete(cacheKey);
    } else {
      cacheRef.current.clear();
    }
  }, []);

  // 데이터 새로고침
  const refreshData = useCallback(async (fetchFunction: () => Promise<T>, force = false) => {
    const cacheKey = key;
    
    // 강제 새로고침이 아니고 캐시된 데이터가 있으면 사용
    if (!force) {
      const cachedData = getFromCache(cacheKey);
      if (cachedData) {
        setData(cachedData);
        setLastUpdated(Date.now());
        return cachedData;
      }
    }

    // 이전 요청 취소
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    setIsLoading(true);
    setError(null);

    try {
      const result = await fetchFunction();
      
      // 캐시에 저장
      setCache(cacheKey, result);
      
      setData(result);
      setLastUpdated(Date.now());
      
      return result;
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        return null; // 요청이 취소됨
      }
      
      setError(error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.');
      throw error;
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [key, getFromCache, setCache]);

  // 자동 새로고침 설정
  useEffect(() => {
    if (!autoRefresh || !refreshInterval) return;

    const startAutoRefresh = () => {
      refreshTimeoutRef.current = setInterval(() => {
        // 백그라운드에서 새로고침 (로딩 상태 변경 없음)
        refreshData(async () => {
          // 여기서는 실제 fetch 함수를 전달해야 함
          // 이 훅을 사용하는 컴포넌트에서 구현
          throw new Error('Auto refresh requires manual implementation');
        }, true).catch(() => {
          // 자동 새로고침 실패는 조용히 무시
        });
      }, refreshInterval);
    };

    startAutoRefresh();

    return () => {
      if (refreshTimeoutRef.current) {
        clearInterval(refreshTimeoutRef.current);
      }
    };
  }, [autoRefresh, refreshInterval, refreshData]);

  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (refreshTimeoutRef.current) {
        clearInterval(refreshTimeoutRef.current);
      }
    };
  }, []);

  // API 클라이언트의 데이터 새로고침 이벤트 구독은 현재 구현되지 않음
  // useEffect(() => {
  //   const unsubscribe = apiClient.onDataRefresh(() => {
  //     // API 데이터 변경 시 캐시 무효화
  //     invalidateCache(key);
  //   });

  //   return unsubscribe;
  // }, [key, invalidateCache]);

  return {
    data,
    isLoading,
    error,
    lastUpdated,
    refreshData,
    invalidateCache,
    getFromCache,
    setCache,
  };
};

export default useDataCache; 