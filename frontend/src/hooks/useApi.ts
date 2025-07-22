import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiCall, ApiResponse } from '@/utils/api';
import { toast } from '@/store/useToastStore';

// 브랜드 관련 훅들
export const useBrands = () => {
  return useQuery({
    queryKey: ['brands'],
    queryFn: () => apiCall('/api/admin/brands'),
    staleTime: 2 * 60 * 1000, // 2분
  });
};

export const useBrand = (id: number) => {
  return useQuery({
    queryKey: ['brands', id],
    queryFn: () => apiCall(`/api/admin/brands/${id}`),
    enabled: !!id,
  });
};

export const useCreateBrand = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: any) => apiCall('/api/admin/brands', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brands'] });
      toast.success('브랜드가 성공적으로 생성되었습니다.');
    },
    onError: (error: any) => {
      toast.error('브랜드 생성에 실패했습니다.', error.message);
    },
  });
};

export const useUpdateBrand = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      apiCall(`/api/admin/brands/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['brands'] });
      queryClient.invalidateQueries({ queryKey: ['brands', id] });
      toast.success('브랜드가 성공적으로 업데이트되었습니다.');
    },
    onError: (error: any) => {
      toast.error('브랜드 업데이트에 실패했습니다.', error.message);
    },
  });
};

// 매장 관련 훅들
export const useStores = () => {
  return useQuery({
    queryKey: ['stores'],
    queryFn: () => apiCall('/api/admin/stores'),
    staleTime: 2 * 60 * 1000,
  });
};

export const useStore = (id: number) => {
  return useQuery({
    queryKey: ['stores', id],
    queryFn: () => apiCall(`/api/admin/stores/${id}`),
    enabled: !!id,
  });
};

export const useCreateStore = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: any) => apiCall('/api/admin/stores', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stores'] });
      toast.success('매장이 성공적으로 생성되었습니다.');
    },
    onError: (error: any) => {
      toast.error('매장 생성에 실패했습니다.', error.message);
    },
  });
};

// 직원 관련 훅들
export const useEmployees = () => {
  return useQuery({
    queryKey: ['employees'],
    queryFn: () => apiCall('/api/admin/employees'),
    staleTime: 2 * 60 * 1000,
  });
};

export const useEmployee = (id: number) => {
  return useQuery({
    queryKey: ['employees', id],
    queryFn: () => apiCall(`/api/admin/employees/${id}`),
    enabled: !!id,
  });
};

// 통계 관련 훅들
export const useBrandStats = () => {
  return useQuery({
    queryKey: ['brand-stats'],
    queryFn: () => apiCall('/api/admin/brand_stats'),
    staleTime: 1 * 60 * 1000, // 1분
  });
};

export const useStoreStats = () => {
  return useQuery({
    queryKey: ['store-stats'],
    queryFn: () => apiCall('/api/admin/store_stats'),
    staleTime: 1 * 60 * 1000,
  });
};

// 시스템 로그 관련 훅들
export const useSystemLogs = () => {
  return useQuery({
    queryKey: ['system-logs'],
    queryFn: () => apiCall('/api/admin/system-logs'),
    staleTime: 30 * 1000, // 30초
  });
};

// 캐시 관련 훅들
export const useClearCache = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: () => apiCall('/api/admin/clear-cache', {
      method: 'POST',
    }),
    onSuccess: () => {
      // 모든 쿼리 캐시 무효화
      queryClient.invalidateQueries();
      toast.success('캐시가 성공적으로 정리되었습니다.');
    },
    onError: (error: any) => {
      toast.error('캐시 정리에 실패했습니다.', error.message);
    },
  });
};

// 사용자 관련 훅들
export const useUsers = () => {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => apiCall('/api/admin/users'),
    staleTime: 5 * 60 * 1000,
  });
};

export const useUpdateUserStatus = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      apiCall(`/api/admin/user/${id}/status`, {
        method: 'POST',
        body: JSON.stringify({ status }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('사용자 상태가 업데이트되었습니다.');
    },
    onError: (error: any) => {
      toast.error('사용자 상태 업데이트에 실패했습니다.', error.message);
    },
  });
}; 

// 임시 더미 훅들 (빌드 오류 방지용)
export const useBranches = () => {
  return useBrands(); // 실제로는 useBrands와 동일하게 동작
};

export const useEmployeeDashboard = () => {
  return { data: null, loading: false, error: null, refresh: () => {} };
};

export const useEmployeeClockIn = () => {
  return { mutate: () => {}, isLoading: false, isSuccess: false, isError: false };
};

export const useEmployeeClockOut = () => {
  return { mutate: () => {}, isLoading: false, isSuccess: false, isError: false };
}; 