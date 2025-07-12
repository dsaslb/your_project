import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';

interface DashboardData {
  success: boolean;
  user: {
    id: number;
    username: string;
    role: string;
    email: string;
  };
  stats: {
    total_users: number;
    total_orders: number;
    total_schedules: number;
    today_orders: number;
    today_schedules: number;
    weekly_orders: number;
    monthly_orders: number;
    total_revenue: number;
    low_stock_items: number;
  };
  last_updated: string;
}

export const useDashboard = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const dashboardData = await apiClient.getDashboardData();
      setData(dashboardData);
    } catch (err: any) {
      console.error('Dashboard data fetch error:', err);
      setError(err.message || '대시보드 데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const refresh = () => {
    fetchDashboardData();
  };

  return {
    data,
    loading,
    error,
    refresh
  };
}; 