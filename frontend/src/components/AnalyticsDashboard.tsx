"use client";

import { useState } from "react";
import { useAnalyticsDashboard, useClearAnalyticsCache } from "@/hooks/useAnalytics";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  ShoppingCart, 
  Users, 
  Package,
  BarChart3,
  RefreshCw,
  Calendar,
  Target,
  Activity,
  AlertTriangle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface AnalyticsDashboardProps {
  className?: string;
}

export default function AnalyticsDashboard({ className = "" }: AnalyticsDashboardProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  const { data: dashboardData, isLoading, error, refetch } = useAnalyticsDashboard();
  const clearCache = useClearAnalyticsCache();

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await clearCache.mutateAsync();
    await refetch();
    setIsRefreshing(false);
  };

  if (isLoading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
        <h2 className="text-xl font-semibold text-gray-900 mb-6">분석 대시보드</h2>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-12 bg-gray-200 rounded-lg"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
        <h2 className="text-xl font-semibold text-gray-900 mb-6">분석 대시보드</h2>
        <div className="flex items-center space-x-2 text-red-600">
          <AlertTriangle className="h-5 w-5" />
          <span>분석 데이터를 불러올 수 없습니다</span>
        </div>
      </div>
    );
  }

  const kpis = {
    total_revenue: 0,
    total_orders: 0,
    avg_order_value: 0,
    total_customers: 0,
    active_staff: 0,
    low_stock_items: 0,
    out_of_stock_items: 0
  }; // 임시 더미 데이터
  const growthMetrics = {
    revenue_growth: 0,
    order_growth: 0,
    customer_growth: 0,
    efficiency_growth: 0
  }; // 임시 더미 데이터
  const salesSummary = {
    total_revenue: 0,
    revenue_growth: 0,
    total_orders: 0,
    order_growth: 0,
    avg_order_value: 0,
    top_items: []
  }; // 임시 더미 데이터
  const staffSummary = {
    total_staff: 0,
    active_staff: 0,
    attendance_rate: 0,
    avg_hours_per_day: 0,
    total_attendance_days: 0,
    staff_performance: []
  }; // 임시 더미 데이터
  const inventorySummary = {
    total_items: 0,
    low_stock_items: 0,
    out_of_stock_items: 0,
    total_value: 0,
    low_stock_count: 0,
    turnover_data: []
  }; // 임시 더미 데이터

  const getGrowthIcon = (value: number) => {
    return value >= 0 ? (
      <TrendingUp className="h-4 w-4 text-green-600" />
    ) : (
      <TrendingDown className="h-4 w-4 text-red-600" />
    );
  };

  const getGrowthColor = (value: number) => {
    return value >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  const lastUpdated = new Date().toISOString(); // 임시 더미 데이터

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">분석 대시보드</h2>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            새로고침
          </Button>
          <Badge variant="secondary" className="text-xs">
            실시간
          </Badge>
        </div>
      </div>

      {/* KPI 카드 */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 매출</CardTitle>
            <DollarSign className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(kpis.total_revenue || 0)}</div>
            <div className="flex items-center space-x-1 text-xs text-gray-500">
              {getGrowthIcon(growthMetrics.revenue_growth || 0)}
              <span className={getGrowthColor(growthMetrics.revenue_growth || 0)}>
                {Math.abs(growthMetrics.revenue_growth || 0)}%
              </span>
              <span>전월 대비</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 주문</CardTitle>
            <ShoppingCart className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.total_orders || 0}건</div>
            <div className="flex items-center space-x-1 text-xs text-gray-500">
              {getGrowthIcon(growthMetrics.order_growth || 0)}
              <span className={getGrowthColor(growthMetrics.order_growth || 0)}>
                {Math.abs(growthMetrics.order_growth || 0)}%
              </span>
              <span>전월 대비</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평균 주문액</CardTitle>
            <Target className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(kpis.avg_order_value || 0)}</div>
            <div className="text-xs text-gray-500">
              주문당 평균
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">활성 직원</CardTitle>
            <Users className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.active_staff || 0}명</div>
            <div className="text-xs text-gray-500">
              현재 근무 중
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">재고 부족</CardTitle>
            <Package className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.low_stock_items || 0}개</div>
            <div className="text-xs text-gray-500">
              발주 필요
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">품절 상품</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.out_of_stock_items || 0}개</div>
            <div className="text-xs text-gray-500">
              즉시 발주 필요
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 상세 분석 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 매출 분석 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-blue-600" />
              <span>매출 분석</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">총 매출</span>
                <span className="font-semibold">{formatCurrency(salesSummary.total_revenue || 0)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">총 주문</span>
                <span className="font-semibold">{salesSummary.total_orders || 0}건</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">평균 주문액</span>
                <span className="font-semibold">{formatCurrency(salesSummary.avg_order_value || 0)}</span>
              </div>
              
              {/* 인기 상품 */}
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">인기 상품</h4>
                <div className="space-y-2">
                  {salesSummary.top_items?.slice(0, 3).map((item: any, index: number) => (
                    <div key={index} className="flex justify-between items-center text-sm">
                      <span className="text-gray-600">{item.name}</span>
                      <span className="font-medium">{formatCurrency(item.revenue)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 직원 성과 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5 text-green-600" />
              <span>직원 성과</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">총 직원</span>
                <span className="font-semibold">{staffSummary.total_staff || 0}명</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">평균 근무시간</span>
                <span className="font-semibold">{staffSummary.avg_hours_per_day || 0}시간</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">총 출근일</span>
                <span className="font-semibold">{staffSummary.total_attendance_days || 0}일</span>
              </div>
              
              {/* 직원별 성과 */}
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">직원별 성과</h4>
                <div className="space-y-2">
                  {staffSummary.staff_performance?.slice(0, 3).map((staff: any, index: number) => (
                    <div key={index} className="flex justify-between items-center text-sm">
                      <div>
                        <span className="font-medium">{staff.name}</span>
                        <span className="text-gray-500 ml-2">({staff.position})</span>
                      </div>
                      <span className="text-green-600 font-medium">{staff.efficiency_score}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 재고 현황 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Package className="h-5 w-5 text-orange-600" />
              <span>재고 현황</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">총 상품</span>
                <span className="font-semibold">{inventorySummary.total_items || 0}개</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">총 재고 가치</span>
                <span className="font-semibold">{formatCurrency(inventorySummary.total_value || 0)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">재고 부족</span>
                <span className="font-semibold text-orange-600">{inventorySummary.low_stock_count || 0}개</span>
              </div>
              
              {/* 재고 회전율 */}
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">재고 회전율</h4>
                <div className="space-y-2">
                  {inventorySummary.turnover_data?.slice(0, 3).map((item: any, index: number) => (
                    <div key={index} className="flex justify-between items-center text-sm">
                      <span className="text-gray-600">{item.item}</span>
                      <span className="font-medium">{item.turnover_rate}회/월</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 성장 지표 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-purple-600" />
              <span>성장 지표</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">매출 성장률</span>
                <div className="flex items-center space-x-1">
                  {getGrowthIcon(growthMetrics.revenue_growth || 0)}
                  <span className={`font-semibold ${getGrowthColor(growthMetrics.revenue_growth || 0)}`}>
                    {Math.abs(growthMetrics.revenue_growth || 0)}%
                  </span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">주문 성장률</span>
                <div className="flex items-center space-x-1">
                  {getGrowthIcon(growthMetrics.order_growth || 0)}
                  <span className={`font-semibold ${getGrowthColor(growthMetrics.order_growth || 0)}`}>
                    {Math.abs(growthMetrics.order_growth || 0)}%
                  </span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">고객 성장률</span>
                <div className="flex items-center space-x-1">
                  {getGrowthIcon(growthMetrics.customer_growth || 0)}
                  <span className={`font-semibold ${getGrowthColor(growthMetrics.customer_growth || 0)}`}>
                    {Math.abs(growthMetrics.customer_growth || 0)}%
                  </span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">효율성 성장률</span>
                <div className="flex items-center space-x-1">
                  {getGrowthIcon(growthMetrics.efficiency_growth || 0)}
                  <span className={`font-semibold ${getGrowthColor(growthMetrics.efficiency_growth || 0)}`}>
                    {Math.abs(growthMetrics.efficiency_growth || 0)}%
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 마지막 업데이트 */}
      <div className="mt-6 text-xs text-gray-500 text-center">
        마지막 업데이트: {lastUpdated ? 
          new Date(lastUpdated).toLocaleString('ko-KR') : 
          '알 수 없음'
        }
      </div>
    </div>
  );
} 