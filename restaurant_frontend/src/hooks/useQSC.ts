import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';

// QSC 항목 조회
export const useQSCItems = (category?: string) => {
  return useQuery({
    queryKey: ['qsc-items', category],
    queryFn: () => Promise.resolve({ data: [] }), // 임시 더미 데이터
    staleTime: 5 * 60 * 1000, // 5분
  });
};

// QSC 점검 목록 조회
export const useQSCInspections = (params?: {
  page?: number;
  per_page?: number;
  store_id?: number;
  category?: string;
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
    queryKey: ['qsc-inspections', params],
    queryFn: () => Promise.resolve({ data: [] }), // 임시 더미 데이터
    staleTime: 2 * 60 * 1000, // 2분
  });
};

// QSC 점검 상세 조회
export const useQSCInspection = (inspectionId: number) => {
  return useQuery({
    queryKey: ['qsc-inspection', inspectionId],
    queryFn: () => Promise.resolve({ data: {} }), // 임시 더미 데이터
    enabled: !!inspectionId,
  });
};

// QSC 점검 생성
export const useCreateQSCInspection = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      store_id: number;
      inspection_date: string;
      category: string;
      items: Array<{
        item_id: number;
        is_passed: boolean;
        notes?: string;
        photos?: string[];
      }>;
      notes?: string;
    }) => Promise.resolve({ success: true }), // 임시 더미 응답
    onSuccess: () => {
      // 관련 쿼리 무효화
      queryClient.invalidateQueries({ queryKey: ['qsc-inspections'] });
      queryClient.invalidateQueries({ queryKey: ['qsc-stats'] });
    },
  });
};

// QSC 통계 조회
export const useQSCStats = () => {
  return useQuery({
    queryKey: ['qsc-stats'],
    queryFn: () => Promise.resolve({ data: { total: 0, completed: 0 } }), // 임시 더미 데이터
    staleTime: 5 * 60 * 1000, // 5분
  });
}; 