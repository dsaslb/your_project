import { useState, useCallback } from 'react';

interface ReportData {
  success: boolean;
  data: any;
  error?: string;
}

interface ChartData {
  title: string;
  data: any[];
  type: 'line' | 'bar' | 'pie';
}

export const useReporting = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 매출 보고서 조회
  const fetchSalesReport = useCallback(async (
    startDate: string,
    endDate: string,
    branchId?: number
  ): Promise<ReportData> => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
      });

      if (branchId) {
        params.append('branch_id', branchId.toString());
      }

      const response = await fetch(`/api/reporting/sales-report?${params}`, {
        credentials: 'include',
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || '매출 보고서를 불러올 수 없습니다.');
      }

      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  // 직원 보고서 조회
  const fetchStaffReport = useCallback(async (
    startDate: string,
    endDate: string,
    branchId?: number
  ): Promise<ReportData> => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
      });

      if (branchId) {
        params.append('branch_id', branchId.toString());
      }

      const response = await fetch(`/api/reporting/staff-report?${params}`, {
        credentials: 'include',
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || '직원 보고서를 불러올 수 없습니다.');
      }

      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  // 재고 보고서 조회
  const fetchInventoryReport = useCallback(async (
    branchId?: number
  ): Promise<ReportData> => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (branchId) {
        params.append('branch_id', branchId.toString());
      }

      const response = await fetch(`/api/reporting/inventory-report?${params}`, {
        credentials: 'include',
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || '재고 보고서를 불러올 수 없습니다.');
      }

      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  // 운영 보고서 조회
  const fetchOperationalReport = useCallback(async (
    startDate: string,
    endDate: string,
    branchId?: number
  ): Promise<ReportData> => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
      });

      if (branchId) {
        params.append('branch_id', branchId.toString());
      }

      const response = await fetch(`/api/reporting/operational-report?${params}`, {
        credentials: 'include',
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || '운영 보고서를 불러올 수 없습니다.');
      }

      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  // 차트 이미지 생성
  const generateChart = useCallback(async (
    chartData: ChartData
  ): Promise<string | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/reporting/chart/${chartData.type}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(chartData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || '차트 생성에 실패했습니다.');
      }

      return data.image;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // 보고서 엑셀 내보내기
  const exportReport = useCallback(async (
    reportType: 'sales' | 'staff' | 'inventory' | 'operational',
    startDate?: string,
    endDate?: string,
    branchId?: number
  ): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      
      if (startDate && endDate) {
        params.append('start_date', startDate);
        params.append('end_date', endDate);
      }
      
      if (branchId) {
        params.append('branch_id', branchId.toString());
      }

      const response = await fetch(`/api/reporting/export/${reportType}?${params}`, {
        credentials: 'include',
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || '보고서 내보내기에 실패했습니다.');
      }

      // 파일 다운로드
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportType}_report_${startDate}_${endDate}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.';
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // 날짜 포맷팅 유틸리티
  const formatDate = (date: Date): string => {
    return date.toISOString().split('T')[0];
  };

  // 날짜 범위 계산 유틸리티
  const getDateRange = (days: number): { startDate: string; endDate: string } => {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    return {
      startDate: formatDate(startDate),
      endDate: formatDate(endDate),
    };
  };

  // 금액 포맷팅
  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
    }).format(amount);
  };

  // 퍼센트 포맷팅
  const formatPercentage = (value: number): string => {
    return `${value.toFixed(1)}%`;
  };

  return {
    loading,
    error,
    fetchSalesReport,
    fetchStaffReport,
    fetchInventoryReport,
    fetchOperationalReport,
    generateChart,
    exportReport,
    formatDate,
    getDateRange,
    formatCurrency,
    formatPercentage,
  };
}; 