'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  ShoppingCart, 
  Package,
  Download,
  Calendar,
  BarChart3,
  PieChart,
  LineChart,
  DollarSign,
  Clock,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';
import { useReporting } from '@/hooks/useReporting';
import { cn } from '@/lib/utils';

interface AdvancedReportsProps {
  className?: string;
}

const AdvancedReports: React.FC<AdvancedReportsProps> = ({ className }) => {
  const {
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
  } = useReporting();

  const [activeTab, setActiveTab] = useState('sales');
  const [dateRange, setDateRange] = useState(getDateRange(30));
  const [salesData, setSalesData] = useState<any>(null);
  const [staffData, setStaffData] = useState<any>(null);
  const [inventoryData, setInventoryData] = useState<any>(null);
  const [operationalData, setOperationalData] = useState<any>(null);

  // 초기 데이터 로드
  useEffect(() => {
    loadReportData();
  }, [dateRange]);

  const loadReportData = async () => {
    // 매출 보고서
    const salesResult = await fetchSalesReport(dateRange.startDate, dateRange.endDate);
    if (salesResult.success) {
      setSalesData(salesResult.data);
    }

    // 직원 보고서
    const staffResult = await fetchStaffReport(dateRange.startDate, dateRange.endDate);
    if (staffResult.success) {
      setStaffData(staffResult.data);
    }

    // 재고 보고서
    const inventoryResult = await fetchInventoryReport();
    if (inventoryResult.success) {
      setInventoryData(inventoryResult.data);
    }

    // 운영 보고서
    const operationalResult = await fetchOperationalReport(dateRange.startDate, dateRange.endDate);
    if (operationalResult.success) {
      setOperationalData(operationalResult.data);
    }
  };

  const handleExport = async (reportType: 'sales' | 'staff' | 'inventory' | 'operational') => {
    await exportReport(reportType, dateRange.startDate, dateRange.endDate);
  };

  const StatCard = ({ title, value, change, icon: Icon, trend = 'neutral' }: any) => (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            {change && (
              <div className={cn(
                "flex items-center mt-1 text-sm",
                trend === 'up' ? "text-green-600" : 
                trend === 'down' ? "text-red-600" : "text-gray-600"
              )}>
                {trend === 'up' ? <TrendingUp className="w-4 h-4 mr-1" /> :
                 trend === 'down' ? <TrendingDown className="w-4 h-4 mr-1" /> : null}
                {change}
              </div>
            )}
          </div>
          <div className="p-3 bg-blue-50 rounded-lg">
            <Icon className="w-6 h-6 text-blue-600" />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className={cn("space-y-6", className)}>
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">고급 보고서</h1>
          <p className="text-gray-600">상세한 분석 및 인사이트</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-gray-500" />
            <Input
              type="date"
              value={dateRange.startDate}
              onChange={(e) => setDateRange(prev => ({ ...prev, startDate: e.target.value }))}
              className="w-32"
            />
            <span className="text-gray-500">~</span>
            <Input
              type="date"
              value={dateRange.endDate}
              onChange={(e) => setDateRange(prev => ({ ...prev, endDate: e.target.value }))}
              className="w-32"
            />
          </div>
          <Button onClick={loadReportData} disabled={loading}>
            새로고침
          </Button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
            <span className="text-red-800">{error}</span>
          </div>
        </div>
      )}

      {/* 탭 네비게이션 */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="sales" className="flex items-center space-x-2">
            <DollarSign className="w-4 h-4" />
            <span>매출</span>
          </TabsTrigger>
          <TabsTrigger value="staff" className="flex items-center space-x-2">
            <Users className="w-4 h-4" />
            <span>직원</span>
          </TabsTrigger>
          <TabsTrigger value="inventory" className="flex items-center space-x-2">
            <Package className="w-4 h-4" />
            <span>재고</span>
          </TabsTrigger>
          <TabsTrigger value="operational" className="flex items-center space-x-2">
            <BarChart3 className="w-4 h-4" />
            <span>운영</span>
          </TabsTrigger>
        </TabsList>

        {/* 매출 보고서 */}
        <TabsContent value="sales" className="space-y-6">
          {salesData && (
            <>
              {/* 주요 지표 */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <StatCard
                  title="총 매출"
                  value={formatCurrency(salesData.total_sales)}
                  change="+12.5%"
                  trend="up"
                  icon={DollarSign}
                />
                <StatCard
                  title="총 주문"
                  value={salesData.total_orders.toLocaleString()}
                  change="+8.2%"
                  trend="up"
                  icon={ShoppingCart}
                />
                <StatCard
                  title="평균 주문액"
                  value={formatCurrency(salesData.avg_order_value)}
                  change="+3.1%"
                  trend="up"
                  icon={TrendingUp}
                />
                <StatCard
                  title="일평균 매출"
                  value={formatCurrency(salesData.total_sales / 30)}
                  change="+5.7%"
                  trend="up"
                  icon={BarChart3}
                />
              </div>

              {/* 상세 분석 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 일별 매출 추이 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>일별 매출 추이</span>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleExport('sales')}
                      >
                        <Download className="w-4 h-4 mr-2" />
                        내보내기
                      </Button>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {salesData.daily_sales.slice(-7).map((day: any, index: number) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <p className="font-medium">{day.date}</p>
                            <p className="text-sm text-gray-600">{day.orders}주문</p>
                          </div>
                          <div className="text-right">
                            <p className="font-bold">{formatCurrency(day.sales)}</p>
                            <p className="text-sm text-gray-600">
                              평균 {formatCurrency(day.sales / day.orders)}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* 인기 상품 */}
                <Card>
                  <CardHeader>
                    <CardTitle>인기 상품 TOP 5</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {salesData.top_products.map((product: any, index: number) => (
                        <div key={index} className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <Badge variant="secondary">{index + 1}</Badge>
                            <div>
                              <p className="font-medium">{product.name}</p>
                              <p className="text-sm text-gray-600">{product.quantity}개 판매</p>
                            </div>
                          </div>
                          <p className="font-bold">{formatCurrency(product.sales)}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>

        {/* 직원 보고서 */}
        <TabsContent value="staff" className="space-y-6">
          {staffData && (
            <>
              {/* 주요 지표 */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <StatCard
                  title="총 직원"
                  value={staffData.attendance_overview.total_staff}
                  icon={Users}
                />
                <StatCard
                  title="활성 직원"
                  value={staffData.attendance_overview.active_staff}
                  change="+2"
                  trend="up"
                  icon={CheckCircle}
                />
                <StatCard
                  title="평균 출근률"
                  value={formatPercentage(staffData.attendance_overview.avg_attendance_rate)}
                  change="+1.2%"
                  trend="up"
                  icon={TrendingUp}
                />
                <StatCard
                  title="초과근무"
                  value={`${staffData.attendance_overview.overtime_hours}시간`}
                  change="+5시간"
                  trend="down"
                  icon={Clock}
                />
              </div>

              {/* 직원 성과 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>직원별 성과</span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleExport('staff')}
                    >
                      <Download className="w-4 h-4 mr-2" />
                      내보내기
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left p-2">이름</th>
                          <th className="text-left p-2">역할</th>
                          <th className="text-left p-2">출근률</th>
                          <th className="text-left p-2">처리 주문</th>
                          <th className="text-left p-2">고객 만족도</th>
                          <th className="text-left p-2">효율성</th>
                        </tr>
                      </thead>
                      <tbody>
                        {staffData.staff_performance.map((staff: any, index: number) => (
                          <tr key={index} className="border-b hover:bg-gray-50">
                            <td className="p-2 font-medium">{staff.name}</td>
                            <td className="p-2">
                              <Badge variant="outline">{staff.role}</Badge>
                            </td>
                            <td className="p-2">{formatPercentage(staff.attendance_rate)}</td>
                            <td className="p-2">{staff.orders_processed}</td>
                            <td className="p-2">{staff.customer_satisfaction.toFixed(1)}/5.0</td>
                            <td className="p-2">{formatPercentage(staff.efficiency_score)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* 재고 보고서 */}
        <TabsContent value="inventory" className="space-y-6">
          {inventoryData && (
            <>
              {/* 주요 지표 */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <StatCard
                  title="총 재고 항목"
                  value={inventoryData.inventory_overview.total_items}
                  icon={Package}
                />
                <StatCard
                  title="부족 재고"
                  value={inventoryData.inventory_overview.low_stock_items}
                  change="+2"
                  trend="down"
                  icon={AlertTriangle}
                />
                <StatCard
                  title="총 재고 가치"
                  value={formatCurrency(inventoryData.inventory_overview.total_value)}
                  icon={DollarSign}
                />
                <StatCard
                  title="평균 회전율"
                  value={`${inventoryData.inventory_overview.avg_turnover_rate}회`}
                  icon={TrendingUp}
                />
              </div>

              {/* 재고 현황 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>재고 현황</span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleExport('inventory')}
                    >
                      <Download className="w-4 h-4 mr-2" />
                      내보내기
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {inventoryData.inventory_items.map((item: any, index: number) => (
                      <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <h3 className="font-medium">{item.name}</h3>
                            {item.current_stock <= item.min_stock && (
                              <Badge variant="destructive">부족</Badge>
                            )}
                          </div>
                          <p className="text-sm text-gray-600">
                            현재: {item.current_stock}{item.unit} / 최소: {item.min_stock}{item.unit}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold">{formatCurrency(item.value)}</p>
                          <div className="w-32 bg-gray-200 rounded-full h-2 mt-2">
                            <div
                              className={cn(
                                "h-2 rounded-full",
                                item.current_stock <= item.min_stock ? "bg-red-500" : "bg-green-500"
                              )}
                              style={{
                                width: `${Math.min((item.current_stock / item.min_stock) * 100, 100)}%`
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* 운영 보고서 */}
        <TabsContent value="operational" className="space-y-6">
          {operationalData && (
            <>
              {/* 주요 지표 */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <StatCard
                  title="고객 만족도"
                  value={`${operationalData.operational_metrics.quality_metrics.customer_satisfaction}/5.0`}
                  change="+0.2"
                  trend="up"
                  icon={TrendingUp}
                />
                <StatCard
                  title="평균 대기시간"
                  value={`${operationalData.operational_metrics.service_times.avg_wait_time}분`}
                  change="-0.5분"
                  trend="up"
                  icon={Clock}
                />
                <StatCard
                  title="시간당 주문"
                  value={operationalData.operational_metrics.efficiency_metrics.orders_per_hour}
                  change="+1.2"
                  trend="up"
                  icon={ShoppingCart}
                />
                <StatCard
                  title="직원당 매출"
                  value={formatCurrency(operationalData.operational_metrics.efficiency_metrics.revenue_per_employee)}
                  change="+5.3%"
                  trend="up"
                  icon={DollarSign}
                />
              </div>

              {/* 피크 타임 분석 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>피크 타임 분석</span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleExport('operational')}
                    >
                      <Download className="w-4 h-4 mr-2" />
                      내보내기
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(operationalData.operational_metrics.peak_hours).map(([time, data]: [string, any]) => (
                      <div key={time} className="p-4 border rounded-lg text-center">
                        <h3 className="font-medium capitalize">{time}</h3>
                        <p className="text-2xl font-bold text-blue-600">{data.orders}</p>
                        <p className="text-sm text-gray-600">
                          {data.start} - {data.end}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdvancedReports; 