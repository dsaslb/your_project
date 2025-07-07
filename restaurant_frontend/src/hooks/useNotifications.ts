import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';

// 알림 조회
export const useNotifications = (params?: {
  page?: number;
  per_page?: number;
  unread_only?: boolean;
  type?: string;
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
    queryKey: ['notifications', params],
    queryFn: () => apiClient.get(`/api/notification-system/notifications?${queryString}`),
    staleTime: 30 * 1000, // 30초
    refetchInterval: 30000, // 30초마다 자동 갱신
  });
};

// 알림 읽음 처리
export const useMarkNotificationRead = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (notificationId: number) => 
      apiClient.put(`/api/notification-system/notifications/${notificationId}/read`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};

// 모든 알림 읽음 처리
export const useMarkAllNotificationsRead = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: () => 
      apiClient.put('/api/notification-system/notifications/read-all'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};

// 알림 삭제
export const useDeleteNotification = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (notificationId: number) => 
      apiClient.delete(`/api/notification-system/notifications/${notificationId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};

// 알림 설정 조회
export const useNotificationSettings = () => {
  return useQuery({
    queryKey: ['notification-settings'],
    queryFn: () => apiClient.get('/api/notification-system/settings'),
    staleTime: 5 * 60 * 1000, // 5분
  });
};

// 알림 설정 업데이트
export const useUpdateNotificationSettings = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (settings: {
      email_notifications?: boolean;
      push_notifications?: boolean;
      sound_enabled?: boolean;
      notification_types?: Record<string, boolean>;
      quiet_hours?: {
        enabled: boolean;
        start: string;
        end: string;
      };
    }) => apiClient.put('/api/notification-system/settings', settings),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notification-settings'] });
    },
  });
};

// 테스트 알림 전송
export const useSendTestNotification = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: {
      type?: string;
      message?: string;
    }) => apiClient.post('/api/notification-system/test', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};

// 알림 통계 조회
export const useNotificationStats = () => {
  return useQuery({
    queryKey: ['notification-stats'],
    queryFn: () => apiClient.get('/api/notification-system/stats'),
    staleTime: 60 * 1000, // 1분
  });
}; 