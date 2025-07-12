'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useVisualization } from '@/hooks/useVisualization';
import { 
  BarChart3, 
  LineChart, 
  PieChart, 
  TrendingUp, 
  Users, 
  Package, 
  DollarSign,
  Activity,
  Clock,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';

// 차트 라이브러리 (실제 프로젝트에서는 react-apexcharts 또는 recharts 사용)
const Chart = ({ data, type, options }: any) => {
  // 실제 차트 라이브러리로 교체 필요
  return (
    <div className="w-full h-64 bg-gray-50 rounded-lg flex items-center justify-center">
      <div className="text-center">
        <div className="text-2xl font-bold text-gray-600">{type.toUpperCase()} Chart</div>
        <div className="text-sm text-gray-500 mt-2">데이터 포인트: {data?.length || 0}</div>
      </div>
    </div>
  );
};

export const AdvancedVisualization = () => {
  const {
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
  } = useVisualization();

  const [salesData, setSalesData] = useState<any[]>([]);
  const [employeeData, setEmployeeData] = useState<any>({});
  const [inventoryData, setInventoryData] = useState<any>({});
  const [realTimeData, setRealTimeData] = useState<any>(null);
  const [selectedPeriod, setSelectedPeriod] = useState('monthly');
  const [selectedBranch, setSelectedBranch] = useState<number | undefined>();
  const [customChartConfig, setCustomChartConfig] = useState({
    chart_type: 'line' as const,
    metrics: ['sales'],
    filters: {},
  });

  // 데이터 로드
  useEffect(() => {
    loadAllData();
  }, [selectedPeriod, selectedBranch]);

  const loadAllData = async () => {
    // 매출 차트 데이터
    const sales = await getSalesChart(selectedPeriod, selectedBranch);
    setSalesData(formatSalesChartData(sales));

    // 직원 성과 데이터
    const employees = await getEmployeePerformance(selectedBranch);
    setEmployeeData(employees);

    // 재고 트렌드 데이터
    const inventory = await getInventoryTrends();
    setInventoryData(inventory);

    // 실시간 메트릭
    const realTime = await getRealTimeMetrics();
    setRealTimeData(realTime);
  };

  // 실시간 메트릭 자동 업데이트
  useEffect(() => {
    const interval = setInterval(async () => {
      const realTime = await getRealTimeMetrics();
      setRealTimeData(realTime);
    }, 30000); // 30초마다 업데이트

    return () => clearInterval(interval);
  }, []);

  // 커스텀 차트 생성
  const handleCustomChart = async () => {
    const data = await getCustomChart(customChartConfig);
    console.log('Custom chart data:', data);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="h-8 w-8 text-red-500 mx-auto" />
          <p className="mt-2 text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">고급 데이터 시각화</h1>
          <p className="text-gray-600">실시간 데이터 분석 및 인사이트</p>
        </div>
        <div className="flex gap-2">
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="daily">일별</SelectItem>
              <SelectItem value="weekly">주별</SelectItem>
              <SelectItem value="monthly">월별</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={loadAllData}>
            새로고침
          </Button>
        </div>
      </div>

      {/* 실시간 메트릭 */}
      {realTimeData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">활성 사용자</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{realTimeData.active_users}</div>
              <p className="text-xs text-muted-foreground">
                마지막 업데이트: {new Date(realTimeData.last_updated).toLocaleTimeString()}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">오늘 주문</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{realTimeData.today_orders.total}</div>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="secondary">{realTimeData.today_orders.pending} 대기</Badge>
                <Badge variant="default">{realTimeData.today_orders.completed} 완료</Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">오늘 매출</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ₩{realTimeData.today_orders.total_sales.toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground">
                평균 주문액: ₩{(realTimeData.today_orders.total_sales / realTimeData.today_orders.total || 0).toLocaleString()}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">시스템 상태</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>CPU</span>
                  <span>{realTimeData.system_status.cpu_usage}%</span>
                </div>
                <Progress value={realTimeData.system_status.cpu_usage} className="h-2" />
                <div className="flex justify-between text-sm">
                  <span>메모리</span>
                  <span>{realTimeData.system_status.memory_usage}%</span>
                </div>
                <Progress value={realTimeData.system_status.memory_usage} className="h-2" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 메인 차트 섹션 */}
      <Tabs defaultValue="sales" className="space-y-4">
        <TabsList>
          <TabsTrigger value="sales">매출 분석</TabsTrigger>
          <TabsTrigger value="employees">직원 성과</TabsTrigger>
          <TabsTrigger value="inventory">재고 트렌드</TabsTrigger>
          <TabsTrigger value="custom">커스텀 차트</TabsTrigger>
        </TabsList>

        <TabsContent value="sales" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>매출 트렌드</CardTitle>
                <CardDescription>
                  {selectedPeriod === 'daily' ? '일별' : selectedPeriod === 'weekly' ? '주별' : '월별'} 매출 추이
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Chart 
                  data={salesData} 
                  type="line" 
                  options={createChartOptions('매출 트렌드', 'line')}
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>주문 수량</CardTitle>
                <CardDescription>주문 수량 분포</CardDescription>
              </CardHeader>
              <CardContent>
                <Chart 
                  data={salesData} 
                  type="bar" 
                  options={createChartOptions('주문 수량', 'bar')}
                />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="employees" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>직원 주문 성과</CardTitle>
                <CardDescription>직원별 주문 처리 성과</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {employeeData.order_performance?.slice(0, 5).map((emp: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium">{emp.employee_name}</div>
                        <div className="text-sm text-gray-600">
                          {emp.completed_orders}/{emp.total_orders} 주문 완료
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold">{emp.completion_rate.toFixed(1)}%</div>
                        <div className="text-sm text-gray-600">
                          ₩{emp.avg_order_amount.toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>근무 성과</CardTitle>
                <CardDescription>직원별 근무 완료율</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {employeeData.schedule_performance?.slice(0, 5).map((emp: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium">{emp.employee_name}</div>
                        <div className="text-sm text-gray-600">
                          {emp.completed_shifts}/{emp.total_shifts} 근무 완료
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold">{emp.completion_rate.toFixed(1)}%</div>
                        <div className="text-sm text-gray-600">
                          평균 {emp.avg_hours.toFixed(1)}시간
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="inventory" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>카테고리별 재고</CardTitle>
                <CardDescription>카테고리별 재고 분포</CardDescription>
              </CardHeader>
              <CardContent>
                <Chart 
                  data={inventoryData.category_distribution} 
                  type="pie" 
                  options={createChartOptions('카테고리별 재고', 'pie')}
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>재고 상태</CardTitle>
                <CardDescription>재고 상태별 분포</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {inventoryData.status_distribution?.map((item: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-2">
                        {item.status === 'low_stock' && <AlertCircle className="h-4 w-4 text-red-500" />}
                        {item.status === 'normal' && <CheckCircle className="h-4 w-4 text-green-500" />}
                        {item.status === 'overstock' && <XCircle className="h-4 w-4 text-yellow-500" />}
                        <span className="font-medium">
                          {item.status === 'low_stock' ? '부족' : 
                           item.status === 'normal' ? '정상' : '과다'}
                        </span>
                      </div>
                      <div className="text-right">
                        <div className="font-bold">{item.item_count}개</div>
                        <div className="text-sm text-gray-600">
                          ₩{item.total_value.toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="custom" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>커스텀 차트 생성</CardTitle>
              <CardDescription>원하는 데이터로 차트를 생성하세요</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium">차트 타입</label>
                  <Select 
                    value={customChartConfig.chart_type} 
                    onValueChange={(value: any) => setCustomChartConfig(prev => ({ ...prev, chart_type: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="line">라인 차트</SelectItem>
                      <SelectItem value="bar">바 차트</SelectItem>
                      <SelectItem value="pie">파이 차트</SelectItem>
                      <SelectItem value="scatter">스캐터 차트</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium">기간</label>
                  <Select 
                    value={(customChartConfig.filters && (customChartConfig.filters as any).date_range) || '30d'} 
                    onValueChange={(value) => setCustomChartConfig(prev => ({ 
                      ...prev, 
                      filters: { ...prev.filters, date_range: value }
                    }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="7d">최근 7일</SelectItem>
                      <SelectItem value="30d">최근 30일</SelectItem>
                      <SelectItem value="90d">최근 90일</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-end">
                  <Button onClick={handleCustomChart} className="w-full">
                    차트 생성
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}; 