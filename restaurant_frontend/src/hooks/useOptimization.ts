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
    queryFn: () => Promise.resolve({ data: [] }), // 임시 더미 데이터
    staleTime: 2 * 60 * 1000, // 2분
    retry: false, // 인증 실패 시 재시도하지 않음
    enabled: true, // 임시로 항상 활성화
  });
};

// 최적화된 주문 통계
export const useOptimizedOrderStats = () => {
  return useQuery({
    queryKey: ['optimized-order-stats'],
    // queryFn: () => apiClient.get('/api/optimization/orders/stats/optimized'),
    queryFn: () => Promise.resolve({ data: { total: 0, completed: 0 } }), // 임시 더미 데이터
    staleTime: 5 * 60 * 1000, // 5분
    retry: false,
    enabled: true, // 임시로 항상 활성화
  });
};

// 지연 로딩 대시보드
export const useLazyDashboard = () => {
  return useQuery({
    queryKey: ['lazy-dashboard'],
    // queryFn: () => apiClient.get('/api/optimization/dashboard/lazy'),
    queryFn: () => Promise.resolve({ data: {} }), // 임시 더미 데이터
    staleTime: 1 * 60 * 1000, // 1분
    retry: false,
    enabled: true, // 임시로 항상 활성화
  });
};

// 캐시된 통계
export const useCachedStats = () => {
  return useQuery({
    queryKey: ['cached-stats'],
    // queryFn: () => apiClient.get('/api/optimization/stats/cached'),
    queryFn: () => Promise.resolve({ data: {} }), // 임시 더미 데이터
    staleTime: 5 * 60 * 1000, // 5분
    retry: false,
    enabled: true, // 임시로 항상 활성화
  });
};

// 성능 모니터링
export const usePerformanceMonitor = () => {
  return useQuery({
    queryKey: ['performance-monitor'],
    // queryFn: () => apiClient.get('/api/optimization/performance/monitor'),
    queryFn: () => Promise.resolve({ data: { cpu: 50, memory: 60 } }), // 임시 더미 데이터
    staleTime: 30 * 1000, // 30초
    refetchInterval: 30000, // 30초마다 자동 갱신
    retry: false,
    enabled: true, // 임시로 항상 활성화
  });
}; 