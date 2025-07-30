/**
 * 계층형 데이터 관리 React Hook
 * 업종/브랜드/매장/직원 데이터의 통합 관리와 자동 동기화를 제공합니다.
 * 
 * 특징:
 * - 자동 데이터 캐싱
 * - 실시간 동기화
 * - 에러 처리
 * - 로딩 상태 관리
 * - 권한별 데이터 필터링
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient, ApiResponse, Industry, Brand, Store, Employee, DashboardData, QueryParams } from '../src/lib/api-client';
import { dataSyncManager, DataSyncEvent } from '../src/lib/data-sync';

// Hook 타입 정의
interface UseDataResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  lastUpdated: Date | null;
}

interface UseListResult<T> extends UseDataResult<T[]> {
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
    has_prev: boolean;
    has_next: boolean;
  } | null;
  setPage: (page: number) => void;
  setPerPage: (perPage: number) => void;
  setSearch: (search: string) => void;
  setFilters: (filters: Partial<QueryParams>) => void;
}

// ==================== 기본 Hook 유틸리티 ====================

function useAsyncData<T>(
  fetchFn: () => Promise<ApiResponse<T>>,
  dependencies: any[] = [],
  options: {
    immediate?: boolean;
    refreshInterval?: number;
  } = {}
): UseDataResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  
  const { immediate = true, refreshInterval } = options;
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetchFn();
      
      if (response.success) {
        setData(response.data || null);
        setLastUpdated(new Date());
      } else {
        throw new Error(response.error || '데이터 로드 실패');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류';
      setError(errorMessage);
      console.error('데이터 로드 오류:', err);
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    if (immediate) {
      fetchData();
    }

    // 자동 새로고침 설정
    if (refreshInterval && refreshInterval > 0) {
      intervalRef.current = setInterval(fetchData, refreshInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchData, immediate, refreshInterval]);

  // API 클라이언트의 데이터 새로고침 이벤트 구독
  useEffect(() => {
    const unsubscribe = apiClient.onDataRefresh(fetchData);
    return unsubscribe;
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refresh: fetchData,
    lastUpdated,
  };
}

function useListData<T>(
  fetchFn: (params: QueryParams) => Promise<ApiResponse<T[]>>,
  initialParams: QueryParams = {},
  options: {
    immediate?: boolean;
    refreshInterval?: number;
  } = {}
): UseListResult<T> {
  const [params, setParams] = useState<QueryParams>({
    page: 1,
    per_page: 20,
    ...initialParams,
  });
  const [pagination, setPagination] = useState<UseListResult<T>['pagination']>(null);

  const fetchWithParams = useCallback(() => {
    return fetchFn(params).then(response => {
      if (response.success && response.pagination) {
        setPagination(response.pagination);
      }
      return response;
    });
  }, [fetchFn, params]);

  const result = useAsyncData(fetchWithParams, [params], options);

  const setPage = useCallback((page: number) => {
    setParams(prev => ({ ...prev, page }));
  }, []);

  const setPerPage = useCallback((per_page: number) => {
    setParams(prev => ({ ...prev, per_page, page: 1 }));
  }, []);

  const setSearch = useCallback((search: string) => {
    setParams(prev => ({ ...prev, search, page: 1 }));
  }, []);

  const setFilters = useCallback((filters: Partial<QueryParams>) => {
    setParams(prev => ({ ...prev, ...filters, page: 1 }));
  }, []);

  return {
    ...result,
    pagination,
    setPage,
    setPerPage,
    setSearch,
    setFilters,
  };
}

// ==================== 업종(Industry) Hook ====================

export function useIndustries(
  params: QueryParams = {},
  options: { immediate?: boolean; refreshInterval?: number } = {}
): UseListResult<Industry> {
  return useListData(
    (queryParams) => apiClient.getIndustries(queryParams),
    params,
    options
  );
}

export function useIndustryDetail(
  industryId: number | null,
  options: { immediate?: boolean; refreshInterval?: number } = {}
): UseDataResult<Industry & {
  stats: { total_brands: number; total_stores: number; total_employees: number };
  brands: Brand[];
}> {
  return useAsyncData(
    () => {
      if (!industryId) {
        return Promise.reject(new Error('업종 ID가 필요합니다'));
      }
      
      // 더미 데이터 반환
      const dummyData: Industry & {
        stats: { total_brands: number; total_stores: number; total_employees: number };
        brands: Brand[];
      } = {
        id: industryId,
        name: `업종 ${industryId}`,
        description: '더미 업종 데이터',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        stats: {
          total_brands: Math.floor(Math.random() * 10) + 3,
          total_stores: Math.floor(Math.random() * 50) + 10,
          total_employees: Math.floor(Math.random() * 200) + 50,
        },
        brands: [
          {
            id: 1,
            name: '브랜드 A',
            industry_id: industryId,
            description: '더미 브랜드',
            logo_url: '',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: 2,
            name: '브랜드 B',
            industry_id: industryId,
            description: '더미 브랜드',
            logo_url: '',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }
        ]
      };
      
      return Promise.resolve({ success: true, data: dummyData });
    },
    [industryId],
    { immediate: !!industryId, ...options }
  );
}

// ==================== 브랜드(Brand) Hook ====================

export function useBrands(
  params: QueryParams = {},
  options: { immediate?: boolean; refreshInterval?: number } = {}
): UseListResult<Brand> {
  return useListData(
    (queryParams) => apiClient.getBrands(queryParams),
    params,
    options
  );
}

export function useBrandDetail(
  brandId: number | null,
  options: { immediate?: boolean; refreshInterval?: number } = {}
): UseDataResult<Brand & {
  stats: {
    total_stores: number;
    total_employees: number;
    total_orders: number;
    today_orders: number;
    active_stores: number;
  };
  stores: Store[];
  recent_activities: {
    orders: any[];
    schedules: any[];
  };
}> {
  return useAsyncData(
    () => {
      if (!brandId) {
        return Promise.reject(new Error('브랜드 ID가 필요합니다'));
      }
      
      // 더미 데이터 반환
      const dummyData: Brand & {
        stats: {
          total_stores: number;
          total_employees: number;
          total_orders: number;
          today_orders: number;
          active_stores: number;
        };
        stores: Store[];
        recent_activities: {
          orders: any[];
          schedules: any[];
        };
      } = {
        id: brandId,
        name: `브랜드 ${brandId}`,
        industry_id: 1,
        description: '더미 브랜드 데이터',
        logo_url: '',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        stats: {
          total_stores: Math.floor(Math.random() * 20) + 5,
          total_employees: Math.floor(Math.random() * 100) + 20,
          total_orders: Math.floor(Math.random() * 1000) + 100,
          today_orders: Math.floor(Math.random() * 50) + 5,
          active_stores: Math.floor(Math.random() * 15) + 3,
        },
        stores: [
          {
            id: 1,
            name: '본점',
            brand_id: brandId,
            address: '서울시 강남구',
            phone: '02-1234-5678',
            manager_id: 1,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: 2,
            name: '강남점',
            brand_id: brandId,
            address: '서울시 강남구',
            phone: '02-2345-6789',
            manager_id: 2,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }
        ],
        recent_activities: {
          orders: [
            { id: 1, amount: 15000, status: 'completed', created_at: new Date().toISOString() },
            { id: 2, amount: 25000, status: 'pending', created_at: new Date().toISOString() }
          ],
          schedules: [
            { id: 1, title: '팀 미팅', date: new Date().toISOString() },
            { id: 2, title: '재고 점검', date: new Date().toISOString() }
          ]
        }
      };
      
      return Promise.resolve({ success: true, data: dummyData });
    },
    [brandId],
    { immediate: !!brandId, ...options }
  );
}

export function useBrandStores(
  brandId: number | null,
  params: QueryParams = {},
  options: { immediate?: boolean; refreshInterval?: number } = {}
): UseListResult<Store> {
  return useListData(
    (queryParams) => {
      if (!brandId) {
        return Promise.resolve({ success: true, data: [], timestamp: new Date().toISOString() });
      }
      
      // 더미 매장 데이터
      const dummyStores: Store[] = [
        {
          id: 1,
          name: '본점',
          brand_id: brandId,
          address: '서울시 강남구',
          phone: '02-1234-5678',
          manager_id: 1,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 2,
          name: '강남점',
          brand_id: brandId,
          address: '서울시 강남구',
          phone: '02-2345-6789',
          manager_id: 2,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 3,
          name: '홍대점',
          brand_id: brandId,
          address: '서울시 마포구',
          phone: '02-3456-7890',
          manager_id: 3,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }
      ];
      
      return Promise.resolve({ 
        success: true, 
        data: dummyStores,
        timestamp: new Date().toISOString()
      });
    },
    params,
    { immediate: !!brandId, ...options }
  );
}

export function useBrandEmployees(
  brandId: number | null,
  params: QueryParams = {},
  options: { immediate?: boolean; refreshInterval?: number } = {}
): UseListResult<Employee> {
  return useListData(
    (queryParams) => {
      if (!brandId) {
        return Promise.resolve({ success: true, data: [], timestamp: new Date().toISOString() });
      }
      
      // 더미 직원 데이터
      const dummyEmployees: Employee[] = [
        {
          id: 1,
          name: '김철수',
          email: 'kim@example.com',
          phone: '010-1234-5678',
          position: '매니저',
          store_id: 1,
          brand_id: brandId,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 2,
          name: '이영희',
          email: 'lee@example.com',
          phone: '010-2345-6789',
          position: '직원',
          store_id: 1,
          brand_id: brandId,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 3,
          name: '박민수',
          email: 'park@example.com',
          phone: '010-3456-7890',
          position: '매니저',
          store_id: 2,
          brand_id: brandId,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }
      ];
      
      return Promise.resolve({ 
        success: true, 
        data: dummyEmployees,
        timestamp: new Date().toISOString()
      });
    },
    params,
    { immediate: !!brandId, ...options }
  );
}

// ==================== 매장(Store) Hook ====================

export function useStores(
  params: QueryParams = {},
  options: { immediate?: boolean; refreshInterval?: number } = {}
): UseListResult<Store> {
  return useListData(
    (queryParams) => apiClient.getStores(queryParams),
    params,
    options
  );
}

export function useStoreDetail(
  storeId: number | null,
  options: { immediate?: boolean; refreshInterval?: number } = {}
): UseDataResult<Store & {
  stats: {
    total_employees: number;
    total_orders: number;
    today_orders: number;
    today_attendance: number;
    active_employees: number;
  };
  employees: Employee[];
  recent_activities: {
    orders: any[];
    schedules: any[];
    attendance: any[];
  };
}> {
  return useAsyncData(
    () => {
      if (!storeId) {
        return Promise.reject(new Error('매장 ID가 필요합니다'));
      }
      
      // 더미 데이터 반환
      const dummyData: Store & {
        stats: {
          total_employees: number;
          total_orders: number;
          today_orders: number;
          today_attendance: number;
          active_employees: number;
        };
        employees: Employee[];
        recent_activities: {
          orders: any[];
          schedules: any[];
          attendance: any[];
        };
      } = {
        id: storeId,
        name: `매장 ${storeId}`,
        brand_id: 1,
        address: '서울시 강남구',
        phone: '02-1234-5678',
        manager_id: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        stats: {
          total_employees: Math.floor(Math.random() * 20) + 5,
          total_orders: Math.floor(Math.random() * 500) + 100,
          today_orders: Math.floor(Math.random() * 30) + 5,
          today_attendance: Math.floor(Math.random() * 15) + 3,
          active_employees: Math.floor(Math.random() * 10) + 2,
        },
        employees: [
          {
            id: 1,
            name: '김철수',
            email: 'kim@example.com',
            phone: '010-1234-5678',
            position: '매니저',
            store_id: storeId,
            brand_id: 1,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: 2,
            name: '이영희',
            email: 'lee@example.com',
            phone: '010-2345-6789',
            position: '직원',
            store_id: storeId,
            brand_id: 1,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }
        ],
        recent_activities: {
          orders: [
            { id: 1, amount: 15000, status: 'completed', created_at: new Date().toISOString() },
            { id: 2, amount: 25000, status: 'pending', created_at: new Date().toISOString() }
          ],
          schedules: [
            { id: 1, title: '팀 미팅', date: new Date().toISOString() },
            { id: 2, title: '재고 점검', date: new Date().toISOString() }
          ],
          attendance: [
            { id: 1, employee_id: 1, check_in: new Date().toISOString(), check_out: new Date().toISOString() },
            { id: 2, employee_id: 2, check_in: new Date().toISOString(), check_out: null }
          ]
        }
      };
      
      return Promise.resolve({ success: true, data: dummyData });
    },
    [storeId],
    { immediate: !!storeId, ...options }
  );
}

export function useStoreEmployees(
  storeId: number | null,
  params: QueryParams = {},
  options: { immediate?: boolean; refreshInterval?: number } = {}
): UseListResult<Employee> {
  return useListData(
    (queryParams) => {
      if (!storeId) {
        return Promise.resolve({ success: true, data: [], timestamp: new Date().toISOString() });
      }
      return apiClient.getStoreEmployees(storeId);
    },
    params,
    { immediate: !!storeId, ...options }
  );
}

// ==================== 직원(Employee) Hook ====================

export function useEmployees(
  params: QueryParams = {},
  options: { immediate?: boolean; refreshInterval?: number } = {}
): UseListResult<Employee> {
  return useListData(
    (queryParams) => apiClient.getEmployees(queryParams),
    params,
    options
  );
}

// ==================== 통합 대시보드 Hook ====================

export function useDashboard(
  options: { immediate?: boolean; refreshInterval?: number } = {}
): UseDataResult<DashboardData> {
  return useAsyncData(
    () => apiClient.getDashboard(),
    [],
    { refreshInterval: 60000, ...options } // 기본 1분마다 새로고침
  );
}

// ==================== 데이터 동기화 Hook ====================

export function useDataSync() {
  const [refreshing, setRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [connectionStatus, setConnectionStatus] = useState(dataSyncManager.getConnectionStatus());
  const [syncEvents, setSyncEvents] = useState<DataSyncEvent[]>([]);

  // WebSocket 연결 상태 모니터링
  useEffect(() => {
    const unsubscribe = dataSyncManager.on('connection_status', (event) => {
      setConnectionStatus(event.payload.status);
    });

    return unsubscribe;
  }, []);

  // 데이터 업데이트 이벤트 모니터링
  useEffect(() => {
    const unsubscribe = dataSyncManager.on('data_updated', (event) => {
      setSyncEvents(prev => [event, ...prev.slice(0, 9)]); // 최근 10개만 유지
      setLastRefresh(new Date());
    });

    return unsubscribe;
  }, []);

  // 동기화 완료 이벤트 모니터링
  useEffect(() => {
    const unsubscribe = dataSyncManager.on('sync_complete', (event) => {
      setSyncEvents(prev => [event, ...prev.slice(0, 9)]);
      setLastRefresh(new Date());
    });

    return unsubscribe;
  }, []);

  const refreshAll = useCallback(async () => {
    try {
      setRefreshing(true);
      await apiClient.refreshData();
      setLastRefresh(new Date());
    } catch (error) {
      console.error('데이터 새로고침 실패:', error);
      throw error;
    } finally {
      setRefreshing(false);
    }
  }, []);

  const clearCache = useCallback(() => {
    dataSyncManager.clearCache();
  }, []);

  const connect = useCallback(() => {
    dataSyncManager.connect();
  }, []);

  const disconnect = useCallback(() => {
    dataSyncManager.disconnect();
  }, []);

  return {
    refreshing,
    lastRefresh,
    refreshAll,
    connectionStatus,
    syncEvents,
    clearCache,
    connect,
    disconnect,
    isConnected: connectionStatus === 'connected',
  };
}

// ==================== 레거시 호환성 Hook ====================

/**
 * 기존 코드와의 호환성을 위한 레거시 Hook
 * @deprecated 새로운 useDashboard Hook 사용 권장
 */
export function useAdminDashboard() {
  return useAsyncData(
    () => apiClient.getAdminDashboard(),
    [],
    { refreshInterval: 60000 }
  );
}

/**
 * 기존 코드와의 호환성을 위한 레거시 Hook
 * @deprecated 새로운 useBrands Hook 사용 권장  
 */
export function useBrandStats() {
  return useAsyncData(
    () => apiClient.getBrandStatsReal(),
    [],
    { refreshInterval: 60000 }
  );
}

// ==================== 유틸리티 Hook ====================

/**
 * 자동 새로고침 기능
 */
export function useAutoRefresh(refreshFn: () => void, interval: number = 60000) {
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    if (enabled && interval > 0) {
      intervalRef.current = setInterval(refreshFn, interval);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [enabled, interval, refreshFn]);

  return {
    enabled,
    setEnabled,
    toggle: () => setEnabled(prev => !prev),
  };
}

/**
 * 에러 처리 유틸리티
 */
export function useErrorHandler() {
  const [errors, setErrors] = useState<string[]>([]);

  const addError = useCallback((error: string) => {
    setErrors(prev => [...prev, error]);
  }, []);

  const removeError = useCallback((index: number) => {
    setErrors(prev => prev.filter((_, i) => i !== index));
  }, []);

  const clearErrors = useCallback(() => {
    setErrors([]);
  }, []);

  return {
    errors,
    addError,
    removeError,
    clearErrors,
  };
}