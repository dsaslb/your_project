import { useState, useEffect, useCallback } from 'react';
import { apiClient, API_ENDPOINTS, ApiResponse, PaginatedResponse, DashboardStats } from '@/lib/api-client';
import { toast } from 'sonner';

// 대시보드 데이터 훅
export function useDashboardData() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.get<ApiResponse<DashboardStats>>(API_ENDPOINTS.DASHBOARD.STATS);
      setStats(response.data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '데이터를 불러오는데 실패했습니다.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  };
}

// 브랜드 데이터 훅
export function useBrands(page = 1, perPage = 10, search = '', status = '') {
  const [brands, setBrands] = useState<PaginatedResponse<any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBrands = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params: Record<string, any> = { page, per_page: perPage };
      if (search) params.search = search;
      if (status) params.status = status;
      
      const response = await apiClient.get<ApiResponse<PaginatedResponse<any>>>(API_ENDPOINTS.BRAND.LIST, params);
      setBrands(response.data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '브랜드 데이터를 불러오는데 실패했습니다.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [page, perPage, search, status]);

  useEffect(() => {
    fetchBrands();
  }, [fetchBrands]);

  return {
    brands: brands?.items || [],
    pagination: brands ? {
      total: brands.total,
      page: brands.page,
      perPage: brands.per_page,
      totalPages: brands.total_pages,
    } : null,
    loading,
    error,
    refetch: fetchBrands,
  };
}

// 업종 데이터 훅
export function useIndustries(page = 1, perPage = 10, search = '', status = '') {
  const [industries, setIndustries] = useState<PaginatedResponse<any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchIndustries = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params: Record<string, any> = { page, per_page: perPage };
      if (search) params.search = search;
      if (status) params.status = status;
      
      const response = await apiClient.get<ApiResponse<PaginatedResponse<any>>>(API_ENDPOINTS.INDUSTRY.LIST, params);
      setIndustries(response.data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '업종 데이터를 불러오는데 실패했습니다.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [page, perPage, search, status]);

  useEffect(() => {
    fetchIndustries();
  }, [fetchIndustries]);

  return {
    industries: industries?.items || [],
    pagination: industries ? {
      total: industries.total,
      page: industries.page,
      perPage: industries.per_page,
      totalPages: industries.total_pages,
    } : null,
    loading,
    error,
    refetch: fetchIndustries,
  };
}

// 매장 데이터 훅
export function useStores(page = 1, perPage = 10, search = '', status = '', brandId?: number) {
  const [stores, setStores] = useState<PaginatedResponse<any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStores = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const endpoint = brandId ? API_ENDPOINTS.BRAND.STORES(brandId) : API_ENDPOINTS.STORE.LIST;
      const params: Record<string, any> = { page, per_page: perPage };
      if (search) params.search = search;
      if (status) params.status = status;
      
      const response = await apiClient.get<ApiResponse<PaginatedResponse<any>>>(endpoint, params);
      setStores(response.data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '매장 데이터를 불러오는데 실패했습니다.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [page, perPage, search, status, brandId]);

  useEffect(() => {
    fetchStores();
  }, [fetchStores]);

  return {
    stores: stores?.items || [],
    pagination: stores ? {
      total: stores.total,
      page: stores.page,
      perPage: stores.per_page,
      totalPages: stores.total_pages,
    } : null,
    loading,
    error,
    refetch: fetchStores,
  };
}

// 직원 데이터 훅
export function useEmployees(page = 1, perPage = 10, search = '', status = '', storeId?: number, brandId?: number) {
  const [employees, setEmployees] = useState<PaginatedResponse<any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEmployees = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      let endpoint = API_ENDPOINTS.EMPLOYEE.LIST;
      if (storeId) {
        endpoint = API_ENDPOINTS.STORE.EMPLOYEES(storeId);
      } else if (brandId) {
        endpoint = API_ENDPOINTS.BRAND.EMPLOYEES(brandId);
      }
      
      const params: Record<string, any> = { page, per_page: perPage };
      if (search) params.search = search;
      if (status) params.status = status;
      
      const response = await apiClient.get<ApiResponse<PaginatedResponse<any>>>(endpoint, params);
      setEmployees(response.data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '직원 데이터를 불러오는데 실패했습니다.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [page, perPage, search, status, storeId, brandId]);

  useEffect(() => {
    fetchEmployees();
  }, [fetchEmployees]);

  return {
    employees: employees?.items || [],
    pagination: employees ? {
      total: employees.total,
      page: employees.page,
      perPage: employees.per_page,
      totalPages: employees.total_pages,
    } : null,
    loading,
    error,
    refetch: fetchEmployees,
  };
}

// 주문 데이터 훅
export function useOrders(page = 1, perPage = 10, search = '', status = '', storeId?: number) {
  const [orders, setOrders] = useState<PaginatedResponse<any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOrders = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const endpoint = storeId ? API_ENDPOINTS.ORDER.BY_STORE(storeId) : API_ENDPOINTS.ORDER.LIST;
      const params: Record<string, any> = { page, per_page: perPage };
      if (search) params.search = search;
      if (status) params.status = status;
      
      const response = await apiClient.get<ApiResponse<PaginatedResponse<any>>>(endpoint, params);
      setOrders(response.data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '주문 데이터를 불러오는데 실패했습니다.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [page, perPage, search, status, storeId]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  return {
    orders: orders?.items || [],
    pagination: orders ? {
      total: orders.total,
      page: orders.page,
      perPage: orders.per_page,
      totalPages: orders.total_pages,
    } : null,
    loading,
    error,
    refetch: fetchOrders,
  };
}

// 재고 데이터 훅
export function useInventory(page = 1, perPage = 10, search = '', status = '', storeId?: number) {
  const [inventory, setInventory] = useState<PaginatedResponse<any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInventory = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const endpoint = storeId ? API_ENDPOINTS.INVENTORY.BY_STORE(storeId) : API_ENDPOINTS.INVENTORY.LIST;
      const params: Record<string, any> = { page, per_page: perPage };
      if (search) params.search = search;
      if (status) params.status = status;
      
      const response = await apiClient.get<ApiResponse<PaginatedResponse<any>>>(endpoint, params);
      setInventory(response.data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '재고 데이터를 불러오는데 실패했습니다.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [page, perPage, search, status, storeId]);

  useEffect(() => {
    fetchInventory();
  }, [fetchInventory]);

  return {
    inventory: inventory?.items || [],
    pagination: inventory ? {
      total: inventory.total,
      page: inventory.page,
      perPage: inventory.per_page,
      totalPages: inventory.total_pages,
    } : null,
    loading,
    error,
    refetch: fetchInventory,
  };
}

// 근무 일정 데이터 훅
export function useSchedules(page = 1, perPage = 10, date?: string, storeId?: number, employeeId?: number) {
  const [schedules, setSchedules] = useState<PaginatedResponse<any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSchedules = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      let endpoint = API_ENDPOINTS.SCHEDULE.LIST;
      if (storeId) {
        endpoint = API_ENDPOINTS.SCHEDULE.BY_STORE(storeId);
      } else if (employeeId) {
        endpoint = API_ENDPOINTS.SCHEDULE.BY_EMPLOYEE(employeeId);
      }
      
      const params: Record<string, any> = { page, per_page: perPage };
      if (date) params.date = date;
      
      const response = await apiClient.get<ApiResponse<PaginatedResponse<any>>>(endpoint, params);
      setSchedules(response.data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '근무 일정 데이터를 불러오는데 실패했습니다.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [page, perPage, date, storeId, employeeId]);

  useEffect(() => {
    fetchSchedules();
  }, [fetchSchedules]);

  return {
    schedules: schedules?.items || [],
    pagination: schedules ? {
      total: schedules.total,
      page: schedules.page,
      perPage: schedules.per_page,
      totalPages: schedules.total_pages,
    } : null,
    loading,
    error,
    refetch: fetchSchedules,
  };
}

// 출근 데이터 훅
export function useAttendance(page = 1, perPage = 10, date?: string, storeId?: number, employeeId?: number) {
  const [attendance, setAttendance] = useState<PaginatedResponse<any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAttendance = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      let endpoint = API_ENDPOINTS.ATTENDANCE.LIST;
      if (storeId) {
        endpoint = API_ENDPOINTS.ATTENDANCE.BY_STORE(storeId);
      } else if (employeeId) {
        endpoint = API_ENDPOINTS.ATTENDANCE.BY_EMPLOYEE(employeeId);
      }
      
      const params: Record<string, any> = { page, per_page: perPage };
      if (date) params.date = date;
      
      const response = await apiClient.get<ApiResponse<PaginatedResponse<any>>>(endpoint, params);
      setAttendance(response.data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '출근 데이터를 불러오는데 실패했습니다.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [page, perPage, date, storeId, employeeId]);

  useEffect(() => {
    fetchAttendance();
  }, [fetchAttendance]);

  return {
    attendance: attendance?.items || [],
    pagination: attendance ? {
      total: attendance.total,
      page: attendance.page,
      perPage: attendance.per_page,
      totalPages: attendance.total_pages,
    } : null,
    loading,
    error,
    refetch: fetchAttendance,
  };
} 