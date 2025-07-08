"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  ShoppingCart, 
  Package, 
  Clock,
  BarChart3,
  PieChart,
  Activity,
  Target,
  Calendar,
  DollarSign
} from 'lucide-react';

interface AnalyticsData {
  sales?: any;
  staff?: any;
  inventory?: any;
  customers?: any;
  realTime?: any;
  predictions?: any;
  comparison?: any;
}

const AdvancedAnalytics: React.FC = () => {
  const [data, setData] = useState<AnalyticsData>({});
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // 모든 분석 데이터를 병렬로 가져오기
      const endpoints = [
        '/api/analytics/sales',
        '/api/analytics/staff',
        '/api/analytics/inventory',
        '/api/analytics/customers',
        '/api/analytics/real-time',
        '/api/analytics/predictions',
        '/api/analytics/comparison'
      ];

      const responses = await Promise.all(
        endpoints.map(endpoint => 
          fetch(endpoint, {
            credentials: 'include',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
          }).then(res => res.json()).catch(() => ({ success: false }))
        )
      );

      const analyticsData: AnalyticsData = {};
      
      if (responses[0].success) analyticsData.sales = responses[0].data;
      if (responses[1].success) analyticsData.staff = responses[1].data;
      if (responses[2].success) analyticsData.inventory = responses[2].data;
      if (responses[3].success) analyticsData.customers = responses[3].data;
      if (responses[4].success) analyticsData.realTime = responses[4].data;
      if (responses[5].success) analyticsData.predictions = responses[5].data;
      if (responses[6].success) analyticsData.comparison = responses[6].data;

      setData(analyticsData);
    } catch (error) {
      console.error('Analytics data fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            고급 분석
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            실시간 데이터 분석 및 예측 인사이트
          </p>
        </div>
        <Button onClick={fetchAnalyticsData} variant="outline">
          <Activity className="h-4 w-4 mr-2" />
          새로고침
        </Button>
      </div>

      {/* 탭 네비게이션 */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="sales">매출 분석</TabsTrigger>
          <TabsTrigger value="staff">직원 성과</TabsTrigger>
          <TabsTrigger value="inventory">재고 분석</TabsTrigger>
          <TabsTrigger value="customers">고객 분석</TabsTrigger>
          <TabsTrigger value="predictions">예측</TabsTrigger>
        </TabsList>

        {/* 개요 탭 */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* 실시간 메트릭 */}
            {data.realTime && (
              <>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">현재 주문</CardTitle>
                    <ShoppingCart className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{data.realTime.current_orders}</div>
                    <p className="text-xs text-muted-foreground">
                      대기: {data.realTime.pending_orders}건
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">근무 직원</CardTitle>
                    <Users className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{data.realTime.working_staff}명</div>
                    <p className="text-xs text-muted-foreground">
                      예상 대기: {data.realTime.estimated_wait_time}분
                    </p>
                  </CardContent>
                </Card>
              </>
            )}

            {/* 성장률 */}
            {data.comparison && (
              <>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">전월 대비</CardTitle>
                    {data.comparison.growth_rates.month_over_month_sales > 0 ? (
                      <TrendingUp className="h-4 w-4 text-green-600" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-red-600" />
                    )}
                  </CardHeader>
                  <CardContent>
                    <div className={`text-2xl font-bold ${
                      data.comparison.growth_rates.month_over_month_sales > 0 
                        ? 'text-green-600' 
                        : 'text-red-600'
                    }`}>
                      {data.comparison.growth_rates.month_over_month_sales}%
                    </div>
                    <p className="text-xs text-muted-foreground">
                      매출 성장률
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">전년 대비</CardTitle>
                    {data.comparison.growth_rates.year_over_year_sales > 0 ? (
                      <TrendingUp className="h-4 w-4 text-green-600" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-red-600" />
                    )}
                  </CardHeader>
                  <CardContent>
                    <div className={`text-2xl font-bold ${
                      data.comparison.growth_rates.year_over_year_sales > 0 
                        ? 'text-green-600' 
                        : 'text-red-600'
                    }`}>
                      {data.comparison.growth_rates.year_over_year_sales}%
                    </div>
                    <p className="text-xs text-muted-foreground">
                      연간 성장률
                    </p>
                  </CardContent>
                </Card>
              </>
            )}
          </div>

          {/* 요약 차트 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {data.sales && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    매출 트렌드
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">총 매출</span>
                      <span className="font-semibold">
                        ₩{data.sales.summary.total_sales.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">총 주문</span>
                      <span className="font-semibold">
                        {data.sales.summary.total_orders.toLocaleString()}건
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">평균 주문</span>
                      <span className="font-semibold">
                        ₩{data.sales.summary.average_order_value.toLocaleString()}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {data.staff && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    직원 성과
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">총 근무시간</span>
                      <span className="font-semibold">
                        {data.staff.summary.total_hours}시간
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">처리 주문</span>
                      <span className="font-semibold">
                        {data.staff.summary.total_orders.toLocaleString()}건
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">평균 평가</span>
                      <span className="font-semibold">
                        {data.staff.summary.average_rating}/5.0
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* 매출 분석 탭 */}
        <TabsContent value="sales" className="space-y-6">
          {data.sales && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <DollarSign className="h-5 w-5" />
                      매출 요약
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between">
                        <span>총 매출</span>
                        <span className="font-semibold">
                          ₩{data.sales.summary.total_sales.toLocaleString()}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>총 주문</span>
                        <span className="font-semibold">
                          {data.sales.summary.total_orders.toLocaleString()}건
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>평균 주문</span>
                        <span className="font-semibold">
                          ₩{data.sales.summary.average_order_value.toLocaleString()}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>성장률</span>
                        <Badge variant={data.sales.summary.growth_rate > 0 ? "default" : "destructive"}>
                          {data.sales.summary.growth_rate}%
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Calendar className="h-5 w-5" />
                      일별 매출
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {data.sales.sales_data.slice(-7).map((item: any, index: number) => (
                        <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                          <span className="text-sm">{item.date}</span>
                          <span className="font-semibold">₩{item.sales.toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="h-5 w-5" />
                      목표 대비
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">
                          {Math.round((data.sales.summary.total_sales / 15000000) * 100)}%
                        </div>
                        <p className="text-sm text-gray-600">월 목표 달성률</p>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>목표</span>
                          <span>₩15,000,000</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>실적</span>
                          <span>₩{data.sales.summary.total_sales.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>

        {/* 직원 성과 탭 */}
        <TabsContent value="staff" className="space-y-6">
          {data.staff && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Users className="h-5 w-5" />
                      직원별 성과
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {data.staff.staff_data.map((staff: any, index: number) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                          <div>
                            <div className="font-semibold">{staff.name}</div>
                            <div className="text-sm text-gray-600">{staff.role}</div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold">{staff.orders_processed}건</div>
                            <div className="text-sm text-gray-600">{staff.hours_worked}시간</div>
                            <Badge variant="outline">{staff.rating}/5.0</Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="h-5 w-5" />
                      성과 요약
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between">
                        <span>총 근무시간</span>
                        <span className="font-semibold">{data.staff.summary.total_hours}시간</span>
                      </div>
                      <div className="flex justify-between">
                        <span>총 처리 주문</span>
                        <span className="font-semibold">{data.staff.summary.total_orders}건</span>
                      </div>
                      <div className="flex justify-between">
                        <span>평균 평가</span>
                        <span className="font-semibold">{data.staff.summary.average_rating}/5.0</span>
                      </div>
                      <div className="flex justify-between">
                        <span>직원 수</span>
                        <span className="font-semibold">{data.staff.summary.staff_count}명</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>

        {/* 재고 분석 탭 */}
        <TabsContent value="inventory" className="space-y-6">
          {data.inventory && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Package className="h-5 w-5" />
                      카테고리별 재고
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {data.inventory.inventory_data.map((category: any, index: number) => (
                        <div key={index} className="space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="font-medium">{category.category}</span>
                            <Badge variant={category.stock_level > 70 ? "default" : "destructive"}>
                              {category.stock_level}%
                            </Badge>
                          </div>
                          <div className="flex justify-between text-sm text-gray-600">
                            <span>총 {category.total_items}개</span>
                            <span>부족 {category.low_stock}개</span>
                            <span>품절 {category.out_of_stock}개</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <PieChart className="h-5 w-5" />
                      재고 요약
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between">
                        <span>총 품목</span>
                        <span className="font-semibold">{data.inventory.summary.total_items}개</span>
                      </div>
                      <div className="flex justify-between">
                        <span>부족 품목</span>
                        <span className="font-semibold text-orange-600">
                          {data.inventory.summary.low_stock}개
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>품절 품목</span>
                        <span className="font-semibold text-red-600">
                          {data.inventory.summary.out_of_stock}개
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>평균 재고율</span>
                        <span className="font-semibold">
                          {data.inventory.summary.average_stock_level}%
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>

        {/* 고객 분석 탭 */}
        <TabsContent value="customers" className="space-y-6">
          {data.customers && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Users className="h-5 w-5" />
                      고객 유형 분포
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {data.customers.customer_types.map((type: any, index: number) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                          <div>
                            <div className="font-semibold">{type.type}</div>
                            <div className="text-sm text-gray-600">{type.count}명</div>
                          </div>
                          <Badge variant="outline">{type.percentage}%</Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Clock className="h-5 w-5" />
                      시간대별 주문
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {data.customers.hourly_orders
                        .filter((hour: any) => hour.orders > 0)
                        .map((hour: any, index: number) => (
                          <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                            <span className="text-sm">{hour.hour}:00</span>
                            <span className="font-semibold">{hour.orders}건</span>
                          </div>
                        ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>

        {/* 예측 탭 */}
        <TabsContent value="predictions" className="space-y-6">
          {data.predictions && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="h-5 w-5" />
                      다음 7일 예측
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {data.predictions.predictions.map((prediction: any, index: number) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                          <div>
                            <div className="font-semibold">{prediction.date}</div>
                            <div className="text-sm text-gray-600">
                              {prediction.predicted_orders}건 예상
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold">
                              ₩{prediction.predicted_sales.toLocaleString()}
                            </div>
                            <Badge variant="outline">
                              {Math.round(prediction.confidence * 100)}% 신뢰도
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="h-5 w-5" />
                      예측 요약
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between">
                        <span>총 예상 매출</span>
                        <span className="font-semibold">
                          ₩{data.predictions.summary.total_predicted_sales.toLocaleString()}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>총 예상 주문</span>
                        <span className="font-semibold">
                          {data.predictions.summary.total_predicted_orders}건
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>평균 신뢰도</span>
                        <span className="font-semibold">
                          {Math.round(data.predictions.summary.average_confidence * 100)}%
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdvancedAnalytics; 