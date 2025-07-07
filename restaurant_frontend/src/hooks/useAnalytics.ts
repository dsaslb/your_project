import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';

// 매출 분석 조회
export const useSalesAnalytics = (params?: {
  start_date?: string;
  end_date?: string;
  group_by?: 'day' | 'week' | 'month';
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
    queryKey: ['sales-analytics', params],
    queryFn: () => apiClient.get(`/api/analytics/sales?${queryString}`),
    staleTime: 5 * 60 * 1000, // 5분
  });
};

// 직원 분석 조회
export const useStaffAnalytics = (params?: {
  start_date?: string;
  end_date?: string;
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
    queryKey: ['staff-analytics', params],
    queryFn: () => apiClient.get(`/api/analytics/staff?${queryString}`),
    staleTime: 5 * 60 * 1000, // 5분
  });
};

// 재고 분석 조회
export const useInventoryAnalytics = () => {
  return useQuery({
    queryKey: ['inventory-analytics'],
    queryFn: () => apiClient.get('/api/analytics/inventory'),
    staleTime: 15 * 60 * 1000, // 15분
  });
};

// 분석 대시보드 조회
export const useAnalyticsDashboard = () => {
  return useQuery({
    queryKey: ['analytics-dashboard'],
    queryFn: () => apiClient.get('/api/analytics/dashboard'),
    staleTime: 5 * 60 * 1000, // 5분
    refetchInterval: 300000, // 5분마다 자동 갱신
  });
};

// 커스텀 리포트 생성
export const useCreateCustomReport = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: {
      type: 'sales_summary' | 'staff_performance' | 'inventory_status' | 'comprehensive';
      filters?: {
        start_date?: string;
        end_date?: string;
        group_by?: string;
      };
    }) => apiClient.post('/api/analytics/reports/custom', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sales-analytics'] });
      queryClient.invalidateQueries({ queryKey: ['staff-analytics'] });
      queryClient.invalidateQueries({ queryKey: ['inventory-analytics'] });
      queryClient.invalidateQueries({ queryKey: ['analytics-dashboard'] });
    },
  });
};

// 분석 캐시 정리
export const useClearAnalyticsCache = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: () => apiClient.post('/api/analytics/cache/clear'),
    onSuccess: () => {
      // 모든 분석 관련 쿼리 무효화
      queryClient.invalidateQueries({ queryKey: ['sales-analytics'] });
      queryClient.invalidateQueries({ queryKey: ['staff-analytics'] });
      queryClient.invalidateQueries({ queryKey: ['inventory-analytics'] });
      queryClient.invalidateQueries({ queryKey: ['analytics-dashboard'] });
    },
  });
}; 