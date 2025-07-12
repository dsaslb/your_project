import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';

// 시스템 상태 조회
export const useSystemStatus = () => {
  return useQuery({
    queryKey: ['system-status'],
    queryFn: () => Promise.resolve({ data: { status: 'healthy' } }), // 임시 더미 데이터
    staleTime: 30 * 1000, // 30초
    refetchInterval: 30000, // 30초마다 자동 갱신
  });
};

// 오류 로그 조회
export const useErrorLogs = (params?: {
  page?: number;
  per_page?: number;
  type?: string;
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
    queryKey: ['error-logs', params],
    // queryFn: () => apiClient.get(`/api/monitoring/logs/errors?${queryString}`),
    queryFn: () => Promise.resolve({ data: [] }), // 임시 더미 데이터
    staleTime: 60 * 1000, // 1분
  });
};

// 성능 로그 조회
export const usePerformanceLogs = (params?: {
  page?: number;
  per_page?: number;
  operation?: string;
  min_time?: number;
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
    queryKey: ['performance-logs', params],
    queryFn: () => Promise.resolve({ data: { cpu: 50, memory: 60 } }), // 임시 더미 데이터
    staleTime: 60 * 1000, // 1분
  });
};

// 알림 설정 조회
export const useAlertSettings = () => {
  return useQuery({
    queryKey: ['alert-settings'],
    queryFn: () => Promise.resolve({ data: [] }), // 임시 더미 데이터
    staleTime: 5 * 60 * 1000, // 5분
  });
};

// 알림 설정 업데이트
export const useUpdateAlertSettings = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (settings: {
      cpu_threshold?: number;
      memory_threshold?: number;
      disk_threshold?: number;
      email_notifications?: boolean;
      slack_notifications?: boolean;
    }) => Promise.resolve({ success: true }), // 임시 더미 응답
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alert-settings'] });
    },
  });
};

// 메트릭 수집
export const useCollectMetrics = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (metrics: {
      cpu_usage: number;
      memory_usage: number;
      disk_usage: number;
      active_connections: number;
      response_time: number;
    }) => Promise.resolve({ success: true }), // 임시 더미 응답
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['system-status'] });
    },
  });
};

// 로그 정리
export const useCleanupLogs = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (params: {
      days_to_keep: number;
      log_type: 'error' | 'performance' | 'all';
    }) => Promise.resolve({ success: true }), // 임시 더미 응답
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['error-logs'] });
      queryClient.invalidateQueries({ queryKey: ['performance-logs'] });
    },
  });
}; 