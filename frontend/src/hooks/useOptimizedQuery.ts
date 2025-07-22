import { useQuery, UseQueryOptions, UseQueryResult } from '@tanstack/react-query';
import { useMemo, useCallback } from 'react';

// 성능 최적화된 쿼리 훅
export function useOptimizedQuery<TData, TError = unknown>(
  queryKey: readonly unknown[],
  queryFn: () => Promise<TData>,
  options?: Omit<UseQueryOptions<TData, TError, TData>, 'queryKey' | 'queryFn'>
): UseQueryResult<TData, TError> {
  // 메모이제이션된 쿼리 키
  const memoizedQueryKey = useMemo(() => queryKey, [queryKey]);

  // 메모이제이션된 쿼리 함수
  const memoizedQueryFn = useCallback(queryFn, [queryFn]);

  // 메모이제이션된 옵션
  const memoizedOptions = useMemo(() => options, [options]);

  return useQuery({
    queryKey: memoizedQueryKey,
    queryFn: memoizedQueryFn,
    ...memoizedOptions,
  });
}

// 디바운스된 쿼리 훅
export function useDebouncedQuery<TData, TError = unknown>(
  queryKey: readonly unknown[],
  queryFn: () => Promise<TData>,
  delay: number = 300,
  options?: Omit<UseQueryOptions<TData, TError, TData>, 'queryKey' | 'queryFn'>
): UseQueryResult<TData, TError> {
  const memoizedQueryKey = useMemo(() => queryKey, [queryKey]);
  const memoizedQueryFn = useCallback(queryFn, [queryFn]);

  return useQuery({
    queryKey: memoizedQueryKey,
    queryFn: memoizedQueryFn,
    enabled: false, // 수동으로 활성화
    ...options,
  });
}

// 캐시 최적화된 쿼리 훅
export function useCachedQuery<TData, TError = unknown>(
  queryKey: readonly unknown[],
  queryFn: () => Promise<TData>,
  staleTime: number = 5 * 60 * 1000, // 5분
  cacheTime: number = 10 * 60 * 1000, // 10분
  options?: Omit<UseQueryOptions<TData, TError, TData>, 'queryKey' | 'queryFn'>
): UseQueryResult<TData, TError> {
  const memoizedQueryKey = useMemo(() => queryKey, [queryKey]);
  const memoizedQueryFn = useCallback(queryFn, [queryFn]);

  return useQuery({
    queryKey: memoizedQueryKey,
    queryFn: memoizedQueryFn,
    staleTime,
    gcTime: cacheTime, // React Query v5에서는 gcTime 사용
    ...options,
  });
}

// 백그라운드 리페치 쿼리 훅
export function useBackgroundQuery<TData, TError = unknown>(
  queryKey: readonly unknown[],
  queryFn: () => Promise<TData>,
  refetchInterval: number = 30 * 1000, // 30초
  options?: Omit<UseQueryOptions<TData, TError, TData>, 'queryKey' | 'queryFn'>
): UseQueryResult<TData, TError> {
  const memoizedQueryKey = useMemo(() => queryKey, [queryKey]);
  const memoizedQueryFn = useCallback(queryFn, [queryFn]);

  return useQuery({
    queryKey: memoizedQueryKey,
    queryFn: memoizedQueryFn,
    refetchInterval,
    refetchIntervalInBackground: true,
    ...options,
  });
}

// 조건부 쿼리 훅
export function useConditionalQuery<TData, TError = unknown>(
  queryKey: readonly unknown[],
  queryFn: () => Promise<TData>,
  enabled: boolean,
  options?: Omit<UseQueryOptions<TData, TError, TData>, 'queryKey' | 'queryFn' | 'enabled'>
): UseQueryResult<TData, TError> {
  const memoizedQueryKey = useMemo(() => queryKey, [queryKey]);
  const memoizedQueryFn = useCallback(queryFn, [queryFn]);

  return useQuery({
    queryKey: memoizedQueryKey,
    queryFn: memoizedQueryFn,
    enabled,
    ...options,
  });
}

// 에러 재시도 쿼리 훅
export function useRetryQuery<TData, TError = unknown>(
  queryKey: readonly unknown[],
  queryFn: () => Promise<TData>,
  retryCount: number = 3,
  retryDelay: number = 1000,
  options?: Omit<UseQueryOptions<TData, TError, TData>, 'queryKey' | 'queryFn'>
): UseQueryResult<TData, TError> {
  const memoizedQueryKey = useMemo(() => queryKey, [queryKey]);
  const memoizedQueryFn = useCallback(queryFn, [queryFn]);

  return useQuery({
    queryKey: memoizedQueryKey,
    queryFn: memoizedQueryFn,
    retry: retryCount,
    retryDelay,
    ...options,
  });
} 