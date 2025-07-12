import { useState, useEffect, useCallback } from 'react';

interface ChartData {
  period?: string;
  sales?: number;
  order_count?: number;
  date?: string;
  orders?: number;
  category?: string;
  value?: number;
  x?: string;
  y?: number;
}

interface EmployeePerformance {
  employee_name: string;
  total_orders: number;
  completed_orders: number;
  completion_rate: number;
  avg_order_amount: number;
  total_sales: number;
  total_shifts: number;
  completed_shifts: number;
  avg_hours: number;
}

interface InventoryTrend {
  category: string;
  item_count: number;
  total_quantity: number;
  avg_quantity: number;
  total_value: number;
  status: string;
  change_count: number;
  net_change: number;
}

interface RealTimeMetrics {
  active_users: number;
  today_orders: {
    total: number;
    pending: number;
    completed: number;
    total_sales: number;
  };
  today_schedules: {
    total: number;
    completed: number;
    pending: number;
  };
  system_status: {
    database_health: string;
    api_response_time: number;
    memory_usage: number;
    cpu_usage: number;
  };
  last_updated: string;
}

interface CustomChartConfig {
  chart_type: 'line' | 'bar' | 'pie' | 'scatter';
  metrics: string[];
  filters: {
    branch_id?: number;
    date_range?: string;
  };
}

export const useVisualization = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 매출 차트 데이터
  const getSalesChart = useCallback(async (period: string = 'monthly', branch_id?: number) => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({ period });
      if (branch_id) params.append('branch_id', branch_id.toString());
      
      const response = await fetch(`/api/visualization/sales-chart?${params}`, {
        credentials: 'include',
      });
      
      if (!response.ok) {
        throw new Error('매출 차트 데이터를 불러올 수 없습니다.');
      }
      
      const data = await response.json();
      return data.data.chart_data as ChartData[];
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // 직원 성과 차트
  const getEmployeePerformance = useCallback(async (branch_id?: number) => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      if (branch_id) params.append('branch_id', branch_id.toString());
      
      const response = await fetch(`/api/visualization/employee-performance?${params}`, {
        credentials: 'include',
      });
      
      if (!response.ok) {
        throw new Error('직원 성과 데이터를 불러올 수 없습니다.');
      }
      
      const data = await response.json();
      return {
        order_performance: data.data.order_performance as EmployeePerformance[],
        schedule_performance: data.data.schedule_performance as EmployeePerformance[],
      };
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      return { order_performance: [], schedule_performance: [] };
    } finally {
      setLoading(false);
    }
  }, []);

  // 재고 트렌드 차트
  const getInventoryTrends = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/visualization/inventory-trends', {
        credentials: 'include',
      });
      
      if (!response.ok) {
        throw new Error('재고 트렌드 데이터를 불러올 수 없습니다.');
      }
      
      const data = await response.json();
      return {
        category_distribution: data.data.category_distribution as InventoryTrend[],
        status_distribution: data.data.status_distribution as InventoryTrend[],
        recent_changes: data.data.recent_changes as InventoryTrend[],
      };
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      return { category_distribution: [], status_distribution: [], recent_changes: [] };
    } finally {
      setLoading(false);
    }
  }, []);

  // 실시간 메트릭
  const getRealTimeMetrics = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/visualization/real-time-metrics', {
        credentials: 'include',
      });
      
      if (!response.ok) {
        throw new Error('실시간 메트릭을 불러올 수 없습니다.');
      }
      
      const data = await response.json();
      return data.data as RealTimeMetrics;
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // 커스텀 차트
  const getCustomChart = useCallback(async (config: CustomChartConfig) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/visualization/custom-chart', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(config),
      });
      
      if (!response.ok) {
        throw new Error('커스텀 차트 데이터를 불러올 수 없습니다.');
      }
      
      const data = await response.json();
      return data.data.chart_data as ChartData[];
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // 차트 데이터 포맷팅 헬퍼 함수들
  const formatSalesChartData = useCallback((data: ChartData[]) => {
    return data.map(item => ({
      name: item.period || item.date || '',
      sales: item.sales || 0,
      orders: item.order_count || item.orders || 0,
    }));
  }, []);

  const formatEmployeeChartData = useCallback((data: EmployeePerformance[]) => {
    return data.map(item => ({
      name: item.employee_name,
      total_orders: item.total_orders,
      completed_orders: item.completed_orders,
      completion_rate: item.completion_rate,
      avg_order_amount: item.avg_order_amount,
      total_sales: item.total_sales,
    }));
  }, []);

  const formatInventoryChartData = useCallback((data: InventoryTrend[]) => {
    return data.map(item => ({
      name: item.category || item.status || '',
      value: item.total_value || item.item_count || 0,
      quantity: item.total_quantity || 0,
    }));
  }, []);

  // 차트 색상 팔레트
  const chartColors = {
    primary: '#3B82F6',
    secondary: '#10B981',
    accent: '#F59E0B',
    danger: '#EF4444',
    warning: '#F97316',
    info: '#06B6D4',
    success: '#22C55E',
    purple: '#8B5CF6',
    pink: '#EC4899',
    gray: '#6B7280',
  };

  // 차트 옵션 생성
  const createChartOptions = useCallback((title: string, type: 'line' | 'bar' | 'pie' | 'area') => {
    const baseOptions = {
      chart: {
        type,
        height: 350,
        toolbar: {
          show: true,
          tools: {
            download: true,
            selection: true,
            zoom: true,
            zoomin: true,
            zoomout: true,
            pan: true,
            reset: true,
          },
        },
      },
      title: {
        text: title,
        align: 'left',
        style: {
          fontSize: '16px',
          fontWeight: 'bold',
        },
      },
      colors: [chartColors.primary, chartColors.secondary, chartColors.accent],
      grid: {
        borderColor: '#E5E7EB',
        strokeDashArray: 4,
      },
      tooltip: {
        enabled: true,
        theme: 'light',
      },
      legend: {
        position: 'top',
        horizontalAlign: 'right',
      },
    };

    return baseOptions;
  }, [chartColors]);

  return {
    loading,
    error,
    getSalesChart,
    getEmployeePerformance,
    getInventoryTrends,
    getRealTimeMetrics,
    getCustomChart,
    formatSalesChartData,
    formatEmployeeChartData,
    formatInventoryChartData,
    createChartOptions,
    chartColors,
  };
}; 