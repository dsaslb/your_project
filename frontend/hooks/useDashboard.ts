import { useState, useEffect, useCallback } from 'react';
import { ApiClient } from '@/utils/api-client';

const apiClient = new ApiClient();

// 대시보드 데이터 관련 훅
export const useDashboardData = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/admin/dashboard/stats');
      setStats(response.data || {});
      setError(null);
    } catch (err) {
      setError(err);
      console.error('대시보드 데이터 로드 실패:', err);
      // 오류 시 기본 데이터 설정
      setStats({
        total_brands: 0,
        total_stores: 0,
        total_employees: 0,
        total_revenue: 0,
        recent_activities: []
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return { stats, loading, error, refetch: fetchStats };
};

// 브랜드 관련 훅
export const useBrands = (page = 1, limit = 50) => {
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchBrands = useCallback(async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/admin/brands');
      setBrands(response.data || []);
      setError(null);
    } catch (err) {
      setError(err);
      console.error('브랜드 데이터 로드 실패:', err);
      setBrands([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBrands();
  }, [fetchBrands]);

  return { brands, loading, error, refetch: fetchBrands };
};

// 업종 관련 훅
export const useIndustries = (page = 1, limit = 50) => {
  const [industries, setIndustries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchIndustries = useCallback(async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/admin/industries');
      setIndustries(response.data || []);
      setError(null);
    } catch (err) {
      setError(err);
      console.error('업종 데이터 로드 실패:', err);
      setIndustries([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIndustries();
  }, [fetchIndustries]);

  return { industries, loading, error, refetch: fetchIndustries };
};

// 매장 관련 훅
export const useStores = (page = 1, limit = 50, search = '', sortBy = '', brandId?: number) => {
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStores = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
        search,
        sort_by: sortBy,
        ...(brandId && { brand_id: brandId.toString() })
      });
      
      const response = await apiClient.get(`/api/admin/stores?${params}`);
      setStores(response.data || []);
      setError(null);
    } catch (err) {
      setError(err);
      console.error('매장 데이터 로드 실패:', err);
    } finally {
      setLoading(false);
    }
  }, [page, limit, search, sortBy, brandId]);

  useEffect(() => {
    fetchStores();
  }, [fetchStores]);

  return { stores, loading, error, refetch: fetchStores };
};

// 직원 관련 훅
export const useEmployees = (page = 1, limit = 50, search = '', sortBy = '', storeId?: number, brandId?: number) => {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchEmployees = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
        search,
        sort_by: sortBy,
        ...(storeId && { store_id: storeId.toString() }),
        ...(brandId && { brand_id: brandId.toString() })
      });
      
      const response = await apiClient.get(`/api/admin/employees?${params}`);
      setEmployees(response.data || []);
      setError(null);
    } catch (err) {
      setError(err);
      console.error('직원 데이터 로드 실패:', err);
    } finally {
      setLoading(false);
    }
  }, [page, limit, search, sortBy, storeId, brandId]);

  useEffect(() => {
    fetchEmployees();
  }, [fetchEmployees]);

  return { employees, loading, error, refetch: fetchEmployees };
}; 