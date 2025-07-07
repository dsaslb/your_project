import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';

// 자동화 규칙 조회
export const useAutomationRules = (params?: {
  enabled_only?: boolean;
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
    queryKey: ['automation-rules', params],
    queryFn: () => apiClient.get(`/api/automation/rules?${queryString}`),
    staleTime: 60 * 1000, // 1분
  });
};

// 자동화 규칙 생성
export const useCreateAutomationRule = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (rule: {
      name: string;
      description?: string;
      trigger_type: string;
      trigger_conditions?: any[];
      actions: any[];
      enabled?: boolean;
      priority?: string;
    }) => apiClient.post('/api/automation/rules', rule),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automation-rules'] });
    },
  });
};

// 자동화 규칙 업데이트
export const useUpdateAutomationRule = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ ruleId, rule }: {
      ruleId: number;
      rule: {
        name?: string;
        description?: string;
        trigger_type?: string;
        trigger_conditions?: any[];
        actions?: any[];
        enabled?: boolean;
        priority?: string;
      };
    }) => apiClient.put(`/api/automation/rules/${ruleId}`, rule),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automation-rules'] });
    },
  });
};

// 자동화 규칙 삭제
export const useDeleteAutomationRule = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (ruleId: number) => 
      apiClient.delete(`/api/automation/rules/${ruleId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automation-rules'] });
    },
  });
};

// 자동화 규칙 실행
export const useExecuteAutomationRule = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ ruleId, context }: {
      ruleId: number;
      context?: any;
    }) => apiClient.post(`/api/automation/rules/${ruleId}/execute`, { context }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['automation-jobs'] });
    },
  });
};

// 자동화 작업 로그 조회
export const useAutomationJobs = (params?: {
  page?: number;
  per_page?: number;
  status?: string;
  rule_id?: number;
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
    queryKey: ['automation-jobs', params],
    queryFn: () => apiClient.get(`/api/automation/jobs?${queryString}`),
    staleTime: 30 * 1000, // 30초
  });
};

// 자동화 통계 조회
export const useAutomationStats = () => {
  return useQuery({
    queryKey: ['automation-stats'],
    queryFn: () => apiClient.get('/api/automation/stats'),
    staleTime: 60 * 1000, // 1분
  });
}; 