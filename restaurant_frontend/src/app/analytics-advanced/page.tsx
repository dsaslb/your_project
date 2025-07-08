"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  Package, 
  ShoppingCart, 
  Clock,
  Brain,
  Target,
  AlertTriangle,
  CheckCircle,
  Info
} from "lucide-react";

interface PredictiveSales {
  current_trend: {
    trend: string;
    change_percent: number;
  };
  predictions: {
    next_7_days: number[];
    confidence: number;
  };
  insights: {
    peak_days: [string, number][];
    average_daily_sales: number;
    total_monthly_sales: number;
  };
}

interface WorkforceOptimization {
  work_patterns: {
    average_hours_by_day: Record<string, number>;
    orders_by_day: Record<string, number>;
    efficiency_scores: Record<string, number>;
  };
  recommendations: {
    peak_days: [string, number][];
    understaffed_days: [string, number][];
    optimal_staffing: {
      high_demand: string[];
      low_demand: string[];
    };
  };
}

interface InventoryPrediction {
  predictions: Array<{
    item_name: string;
    current_stock: number;
    daily_consumption: number;
    days_until_stockout: number | null;
    recommended_order: number;
    ai_score: number;
    priority: string;
  }>;
  summary: {
    high_priority_items: number;
    total_recommended_order: number;
    average_ai_score: number;
  };
}

interface CustomerBehavior {
  customer_segments: {
    vip: Array<{
      customer: string;
      order_count: number;
      total_spent: number;
      avg_order_value: number;
    }>;
    regular: any[];
    occasional: any[];
    new: any[];
  };
  insights: {
    total_customers: number;
    vip_customers: number;
    peak_hours: [number, number][];
    peak_days: [string, number][];
    average_order_value: number;
  };
}

interface OperationalEfficiency {
  efficiency_metrics: {
    average_processing_time: number;
    average_work_hours: number;
    orders_per_hour: number;
    attendance_rate: number;
    efficiency_score: number;
  };
  recommendations: {
    improve_processing_time: boolean;
    increase_staffing: boolean;
    attendance_improvement: boolean;
    suggested_actions: string[];
  };
}

interface AIInsight {
  type: string;
  category: string;
  title: string;
  description: string;
  action: string;
  priority: string;
}

interface AIInsights {
  insights: AIInsight[];
  summary: {
    total_insights: number;
    critical_insights: number;
    high_priority_insights: number;
    categories: string[];
  };
}

export default function AnalyticsAdvancedPage() {
  const [activeTab, setActiveTab] = useState("predictive");
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<{
    predictive?: PredictiveSales;
    workforce?: WorkforceOptimization;
    inventory?: InventoryPrediction;
    customer?: CustomerBehavior;
    efficiency?: OperationalEfficiency;
    insights?: AIInsights;
  }>({});

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const endpoints = [
        'predictive/sales',
        'workforce/optimization',
        'inventory/ai-prediction',
        'customer/behavior',
        'operational/efficiency',
        'ai/insights'
      ];

      const results = await Promise.all(
        endpoints.map(endpoint =>
          fetch(`/api/analytics/${endpoint}`)
            .then(res => res.json())
            .catch(() => null)
        )
      );

      setData({
        predictive: results[0],
        workforce: results[1],
        inventory: results[2],
        customer: results[3],
        efficiency: results[4],
        insights: results[5]
      });
    } catch (error) {
      console.error('Analytics data fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend: string) => {
    return trend === 'increasing' ? <TrendingUp className="text-green-500" /> : 
           trend === 'decreasing' ? <TrendingDown className="text-red-500" /> : 
           <TrendingUp className="text-gray-500" />;
  };

  const getPriorityColor = (priority: string) => {
    return priority === 'critical' ? 'destructive' :
           priority === 'high' ? 'default' :
           priority === 'medium' ? 'secondary' : 'outline';
  };

  const getInsightIcon = (type: string) => {
    return type === 'positive' ? <CheckCircle className="text-green-500" /> :
           type === 'warning' ? <AlertTriangle className="text-yellow-500" /> :
           type === 'info' ? <Info className="text-blue-500" /> :
           <Target className="text-purple-500" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">고급 분석 & AI 인사이트</h1>
          <p className="text-muted-foreground">
            AI 기반 예측 분석과 운영 최적화 인사이트
          </p>
        </div>
        <Button onClick={fetchAnalyticsData} variant="outline">
          데이터 새로고침
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="predictive">매출 예측</TabsTrigger>
          <TabsTrigger value="workforce">인력 최적화</TabsTrigger>
          <TabsTrigger value="inventory">재고 AI</TabsTrigger>
          <TabsTrigger value="customer">고객 행동</TabsTrigger>
          <TabsTrigger value="efficiency">운영 효율성</TabsTrigger>
          <TabsTrigger value="insights">AI 인사이트</TabsTrigger>
        </TabsList>

        <TabsContent value="predictive" className="space-y-4">
          {data.predictive && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      {getTrendIcon(data.predictive.current_trend.trend)}
                      매출 트렌드
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {data.predictive.current_trend.change_percent}%
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {data.predictive.current_trend.trend === 'increasing' ? '증가' : 
                       data.predictive.current_trend.trend === 'decreasing' ? '감소' : '안정'}
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>예측 신뢰도</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {data.predictive.predictions.confidence}%
                    </div>
                    <Progress value={data.predictive.predictions.confidence} className="mt-2" />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>월 매출</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {data.predictive.insights.total_monthly_sales.toLocaleString()}원
                    </div>
                    <p className="text-sm text-muted-foreground">
                      일평균 {data.predictive.insights.average_daily_sales.toLocaleString()}원
                    </p>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>향후 7일 매출 예측</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-7 gap-2">
                    {data.predictive.predictions.next_7_days.map((prediction, index) => (
                      <div key={index} className="text-center p-2 border rounded">
                        <div className="text-sm text-muted-foreground">D+{index + 1}</div>
                        <div className="font-bold">{prediction.toLocaleString()}원</div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        <TabsContent value="workforce" className="space-y-4">
          {data.workforce && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle>요일별 효율성</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {Object.entries(data.workforce.work_patterns.efficiency_scores).map(([day, score]) => (
                      <div key={day} className="flex justify-between items-center py-2">
                        <span>{day}</span>
                        <Badge variant={score > 2 ? "default" : "secondary"}>
                          {score}
                        </Badge>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>인력 배치 권장사항</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-semibold text-green-600">고수요 요일</h4>
                        <div className="flex gap-2 mt-1">
                          {data.workforce.recommendations.optimal_staffing.high_demand.map(day => (
                            <Badge key={day} variant="default">{day}</Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-semibold text-orange-600">저수요 요일</h4>
                        <div className="flex gap-2 mt-1">
                          {data.workforce.recommendations.optimal_staffing.low_demand.map(day => (
                            <Badge key={day} variant="secondary">{day}</Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>

        <TabsContent value="inventory" className="space-y-4">
          {data.inventory && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle>재고 현황</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>고우선순위 품목</span>
                        <Badge variant="destructive">{data.inventory.summary.high_priority_items}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span>총 발주 권장량</span>
                        <span className="font-bold">{data.inventory.summary.total_recommended_order}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>평균 AI 점수</span>
                        <span className="font-bold">{data.inventory.summary.average_ai_score}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>재고 예측 상세</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {data.inventory.predictions.slice(0, 10).map((item, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded">
                        <div>
                          <div className="font-semibold">{item.item_name}</div>
                          <div className="text-sm text-muted-foreground">
                            현재: {item.current_stock} | 소비: {item.daily_consumption}/일
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge variant={getPriorityColor(item.priority)}>
                            {item.priority}
                          </Badge>
                          <div className="text-sm mt-1">
                            {item.days_until_stockout ? 
                              `${item.days_until_stockout}일 후 소진` : 
                              '재고 충분'}
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

        <TabsContent value="customer" className="space-y-4">
          {data.customer && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle>총 고객 수</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{data.customer.insights.total_customers}</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>VIP 고객</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-purple-600">{data.customer.insights.vip_customers}</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>평균 주문 금액</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {data.customer.insights.average_order_value.toLocaleString()}원
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>피크 시간대</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-1">
                      {data.customer.insights.peak_hours.map(([hour, count]) => (
                        <div key={hour} className="flex justify-between text-sm">
                          <span>{hour}시</span>
                          <span>{count}주문</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>VIP 고객 상세</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {data.customer.customer_segments.vip.map((customer, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded">
                        <div>
                          <div className="font-semibold">{customer.customer}</div>
                          <div className="text-sm text-muted-foreground">
                            {customer.order_count}주문 | 평균 {customer.avg_order_value.toLocaleString()}원
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-purple-600">
                            {customer.total_spent.toLocaleString()}원
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

        <TabsContent value="efficiency" className="space-y-4">
          {data.efficiency && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle>평균 처리 시간</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {data.efficiency.efficiency_metrics.average_processing_time}분
                    </div>
                    <Progress 
                      value={Math.min(100, (data.efficiency.efficiency_metrics.average_processing_time / 30) * 100)} 
                      className="mt-2" 
                    />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>시간당 주문</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {data.efficiency.efficiency_metrics.orders_per_hour}
                    </div>
                    <Progress 
                      value={Math.min(100, (data.efficiency.efficiency_metrics.orders_per_hour / 3) * 100)} 
                      className="mt-2" 
                    />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>출근률</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {data.efficiency.efficiency_metrics.attendance_rate}%
                    </div>
                    <Progress 
                      value={data.efficiency.efficiency_metrics.attendance_rate} 
                      className="mt-2" 
                    />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>종합 효율성</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {data.efficiency.efficiency_metrics.efficiency_score}%
                    </div>
                    <Progress 
                      value={data.efficiency.efficiency_metrics.efficiency_score} 
                      className="mt-2" 
                    />
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>개선 권장사항</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {data.efficiency.recommendations.suggested_actions.map((action, index) => (
                      <Alert key={index}>
                        <AlertDescription>{action}</AlertDescription>
                      </Alert>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          {data.insights && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle>총 인사이트</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{data.insights.summary.total_insights}</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>긴급</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-red-600">{data.insights.summary.critical_insights}</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>높은 우선순위</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-orange-600">{data.insights.summary.high_priority_insights}</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>분석 카테고리</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-1">
                      {data.insights.summary.categories.map(category => (
                        <Badge key={category} variant="outline">{category}</Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>AI 생성 인사이트</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {data.insights.insights.map((insight, index) => (
                      <Alert key={index}>
                        <div className="flex items-start gap-3">
                          {getInsightIcon(insight.type)}
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-semibold">{insight.title}</h4>
                              <Badge variant={getPriorityColor(insight.priority)}>
                                {insight.priority}
                              </Badge>
                            </div>
                            <p className="text-sm mb-2">{insight.description}</p>
                            <p className="text-sm font-medium text-blue-600">{insight.action}</p>
                          </div>
                        </div>
                      </Alert>
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
} 