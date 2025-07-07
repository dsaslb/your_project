import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';

// 최적화된 사용자 목록 조회
export const useOptimizedUsers = (params?: {
  page?: number;
  per_page?: number;
  role?: string;
  search?: string;
}) => {
  const queryString = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        queryString.append(key, value.toString());
      }
    });
  }

  return useQuery({
    queryKey: ['optimized-users', params],
    queryFn: () => apiClient.get(`/api/modules/optimization/users/optimized?${queryString}`),
    staleTime: 2 * 60 * 1000, // 2분
  });
};

// 최적화된 주문 통계
export const useOptimizedOrderStats = () => {
  return useQuery({
    queryKey: ['optimized-order-stats'],
    queryFn: () => apiClient.get('/api/modules/optimization/orders/stats/optimized'),
    staleTime: 5 * 60 * 1000, // 5분
  });
};

// 지연 로딩 대시보드
export const useLazyDashboard = () => {
  return useQuery({
    queryKey: ['lazy-dashboard'],
    queryFn: () => apiClient.get('/api/modules/optimization/dashboard/lazy'),
    staleTime: 1 * 60 * 1000, // 1분
  });
};

// 캐시된 통계
export const useCachedStats = () => {
  return useQuery({
    queryKey: ['cached-stats'],
    queryFn: () => apiClient.get('/api/modules/optimization/stats/cached'),
    staleTime: 5 * 60 * 1000, // 5분
  });
};

// 성능 모니터링
export const usePerformanceMonitor = () => {
  return useQuery({
    queryKey: ['performance-monitor'],
    queryFn: () => apiClient.get('/api/modules/optimization/performance/monitor'),
    staleTime: 30 * 1000, // 30초
    refetchInterval: 30000, // 30초마다 자동 갱신
  });
}; 