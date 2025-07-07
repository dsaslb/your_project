import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';

// 사용자 입력 검증
export const useValidateUserInput = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: {
      username?: string;
      email?: string;
      password?: string;
      name?: string;
      phone?: string;
    }) => apiClient.post('/api/security/validate/user', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-validation'] });
    },
  });
};

// 파일 업로드 검증
export const useValidateFile = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return apiClient.post('/api/security/validate/file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['file-validation'] });
    },
  });
};

// 보안 이벤트 조회
export const useSecurityEvents = (params?: {
  page?: number;
  per_page?: number;
  event_type?: string;
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
    queryKey: ['security-events', params],
    queryFn: () => apiClient.get(`/api/security/security/events?${queryString}`),
    staleTime: 30 * 1000, // 30초
  });
};

// Rate Limit 상태 확인
export const useRateLimitStatus = () => {
  return useQuery({
    queryKey: ['rate-limit-status'],
    queryFn: () => apiClient.get('/api/security/rate-limit/status'),
    staleTime: 60 * 1000, // 1분
  });
};

// 보안 설정 조회
export const useSecuritySettings = () => {
  return useQuery({
    queryKey: ['security-settings'],
    queryFn: () => apiClient.get('/api/security/settings'),
    staleTime: 5 * 60 * 1000, // 5분
  });
};

// 보안 설정 업데이트
export const useUpdateSecuritySettings = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (settings: {
      max_login_attempts?: number;
      session_timeout?: number;
      password_expiry_days?: number;
      require_2fa?: boolean;
    }) => apiClient.put('/api/security/settings', settings),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['security-settings'] });
    },
  });
}; 