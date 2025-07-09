import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

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
    // queryFn: () => apiClient.get(`/api/notifications?${queryString}`),
    queryFn: () => Promise.resolve({ data: [] }), // 임시 더미 데이터
    staleTime: 30 * 1000, // 30초
    refetchInterval: 30000, // 30초마다 자동 갱신
  });
};

// 알림 읽음 처리
export const useMarkNotificationRead = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    // mutationFn: (notificationId: number) => apiClient.put(`/api/notifications/${notificationId}/read`),
    mutationFn: (notificationId: number) => Promise.resolve({ success: true }), // 임시 더미 응답
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};

// 모든 알림 읽음 처리
export const useMarkAllNotificationsRead = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    // mutationFn: (notificationIds: number[]) => apiClient.put('/api/notifications/read-all', { ids: notificationIds }),
    mutationFn: (notificationIds: number[]) => Promise.resolve({ success: true }), // 임시 더미 응답
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};

// 알림 삭제
export const useDeleteNotification = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    // mutationFn: (notificationId: number) => apiClient.delete(`/api/notifications/${notificationId}`),
    mutationFn: (notificationId: number) => Promise.resolve({ success: true }), // 임시 더미 응답
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};

// 알림 설정 조회
export const useNotificationSettings = () => {
  return useQuery({
    queryKey: ['notification-settings'],
    // queryFn: () => apiClient.get('/api/notifications/settings'),
    queryFn: () => Promise.resolve({ data: {} }), // 임시 더미 데이터
    staleTime: 5 * 60 * 1000, // 5분
  });
};

// 알림 설정 업데이트
export const useUpdateNotificationSettings = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    // mutationFn: (settings: any) => apiClient.put('/api/notifications/settings', settings),
    mutationFn: (settings: any) => Promise.resolve({ success: true }), // 임시 더미 응답
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notification-settings'] });
    },
  });
};

// 테스트 알림 전송
export const useSendTestNotification = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    // mutationFn: (notification: any) => apiClient.post('/api/notifications', notification),
    mutationFn: (notification: any) => Promise.resolve({ success: true }), // 임시 더미 응답
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};

// 알림 통계 조회
export const useNotificationStats = () => {
  return useQuery({
    queryKey: ['notification-stats'],
    // queryFn: () => apiClient.get('/api/notifications/stats'),
    queryFn: () => Promise.resolve({ data: { total: 0, unread: 0 } }), // 임시 더미 데이터
    staleTime: 60 * 1000, // 1분
  });
};

// 미읽은 알림 개수 조회
export const useUnreadNotificationCount = () => {
  return useQuery({
    queryKey: ['unread-notification-count'],
    queryFn: async () => {
      try {
        const response = await apiClient.get('/api/notifications/unread-count');
        return response;
      } catch (error) {
        console.warn('알림 카운트 조회 실패:', error);
        // 백엔드 연결 실패 시 기본값 반환
        return { data: { count: 0 } };
      }
    },
    staleTime: 30 * 1000, // 30초
    refetchInterval: 30000, // 30초마다 자동 갱신
  });
}; 