'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import {
  BarChart3,
  TrendingUp,
  Brain,
  Lightbulb,
  Activity,
  RefreshCw,
  DollarSign,
  Users,
  AlertTriangle,
} from 'lucide-react';
import { useLoadingState } from '@/hooks/useLoadingState';
import { useErrorHandler } from '@/hooks/useErrorHandler';
import { apiClient } from '@/lib/api-client';

interface AnalyticsSummary {
  total_analyses: number;
  total_models: number;
  total_insights: number;
  realtime_metrics: number;
  analysis_types: {
    trend: number;
    prediction: number;
    correlation: number;
    clustering: number;
    anomaly: number;
  };
  insight_categories: {
    sales: number;
    customer: number;
    anomaly: number;
  };
  model_accuracy: Record<string, number>;
}

interface SalesPrediction {
  predictions: number[];
  dates: string[];
  model_accuracy: number;
  total_predicted_sales: number;
  avg_daily_sales: number;
}

const AnalyticsPage: React.FC = () => {
  const { isLoading, startLoading, stopLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 상태 관리
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [salesPrediction, setSalesPrediction] = useState<SalesPrediction | null>(null);

  // 데이터 로드 함수들
  const loadSummary = useCallback(async () => {
    try {
      // 임시로 샘플 데이터 사용
      const sampleSummary = {
        totalRevenue: 15000000,
        totalOrders: 1250,
        totalCustomers: 850,
        growthRate: 12.5,
        topProducts: [
          { name: '아메리카노', sales: 450, revenue: 2250000 },
          { name: '카페라떼', sales: 380, revenue: 1900000 },
          { name: '카푸치노', sales: 320, revenue: 1600000 }
        ],
        recentTrends: [
          { date: '2024-01-10', revenue: 1200000, orders: 95 },
          { date: '2024-01-11', revenue: 1350000, orders: 108 },
          { date: '2024-01-12', revenue: 1420000, orders: 115 }
        ]
      };
      setSummary(sampleSummary);
    } catch (error) {
      handleError(error as Error);
    }
  }, [handleError]);

  const loadSalesPrediction = useCallback(async () => {
    try {
      const response = await apiClient.post('/api/analytics/predictions/sales', { days_ahead: 30 });
      setSalesPrediction(response.data);
    } catch (error) {
      handleError(error as Error);
    }
  }, [handleError]);

  // 초기 데이터 로드
  useEffect(() => {
    const loadAllData = async () => {
      startLoading();
      try {
        await Promise.all([
          loadSummary(),
          loadSalesPrediction()
        ]);
      } catch (error) {
        handleError(error as Error);
      } finally {
        stopLoading();
      }
    };
    
    loadAllData();
  }, [loadSummary, loadSalesPrediction, startLoading, stopLoading, handleError]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p>로딩 중...</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 flex items-center">
        <BarChart3 className="w-8 h-8 mr-3" />
        데이터 분석 시스템
      </h1>

      <div className="flex justify-between items-center mb-6">
        <p className="text-gray-600">고급 데이터 분석 및 비즈니스 인텔리전스를 제공합니다.</p>
        <Button>
          <RefreshCw className="w-4 h-4 mr-2" />
          새로고침
        </Button>
      </div>

      {/* 분석 요약 */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 분석</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.total_analyses}</div>
              <p className="text-xs text-muted-foreground">
                {summary.analysis_types.trend + summary.analysis_types.prediction + summary.analysis_types.correlation + summary.analysis_types.clustering + summary.analysis_types.anomaly}개 유형
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">예측 모델</CardTitle>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.total_models}</div>
              <p className="text-xs text-muted-foreground">
                평균 정확도 {Object.values(summary.model_accuracy).length > 0 ? 
                  (Object.values(summary.model_accuracy).reduce((a, b) => a + b, 0) / Object.values(summary.model_accuracy).length * 100).toFixed(1) : 0}%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">인사이트</CardTitle>
              <Lightbulb className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.total_insights}</div>
              <p className="text-xs text-muted-foreground">
                {summary.insight_categories.sales + summary.insight_categories.customer + summary.insight_categories.anomaly}개 카테고리
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">실시간 메트릭</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.realtime_metrics}</div>
              <p className="text-xs text-muted-foreground">
                실시간 모니터링 중
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 매출 예측 카드 */}
      {salesPrediction && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <DollarSign className="w-5 h-5 mr-2" />
              매출 예측 (30일)
            </CardTitle>
            <CardDescription>
              향후 30일간의 매출 예측 및 분석
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {salesPrediction.total_predicted_sales.toLocaleString()}원
                </div>
                <p className="text-sm text-gray-600">총 예측 매출</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {salesPrediction.avg_daily_sales.toLocaleString()}원
                </div>
                <p className="text-sm text-gray-600">일평균 매출</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {(salesPrediction.model_accuracy * 100).toFixed(1)}%
                </div>
                <p className="text-sm text-gray-600">모델 정확도</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 메인 탭 */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="trends">트렌드</TabsTrigger>
          <TabsTrigger value="predictions">예측</TabsTrigger>
          <TabsTrigger value="insights">인사이트</TabsTrigger>
        </TabsList>

        {/* 개요 탭 */}
        <TabsContent value="overview" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>분석 시스템 개요</CardTitle>
              <CardDescription>
                데이터 분석 시스템의 주요 기능과 성능 지표
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-3">분석 유형별 통계</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>트렌드 분석</span>
                      <Badge variant="outline">{summary?.analysis_types.trend || 0}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>예측 분석</span>
                      <Badge variant="outline">{summary?.analysis_types.prediction || 0}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>상관관계 분석</span>
                      <Badge variant="outline">{summary?.analysis_types.correlation || 0}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>클러스터링</span>
                      <Badge variant="outline">{summary?.analysis_types.clustering || 0}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>이상 탐지</span>
                      <Badge variant="outline">{summary?.analysis_types.anomaly || 0}</Badge>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold mb-3">인사이트 카테고리</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>매출 관련</span>
                      <Badge variant="outline">{summary?.insight_categories.sales || 0}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>고객 관련</span>
                      <Badge variant="outline">{summary?.insight_categories.customer || 0}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>이상 탐지</span>
                      <Badge variant="outline">{summary?.insight_categories.anomaly || 0}</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 트렌드 탭 */}
        <TabsContent value="trends" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="w-5 h-5 mr-2" />
                트렌드 분석
              </CardTitle>
              <CardDescription>
                시계열 데이터의 트렌드와 패턴 분석
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                트렌드 분석 기능을 통해 매출, 고객 행동, 시스템 성능 등의 시계열 데이터에서 
                패턴과 트렌드를 발견할 수 있습니다.
              </p>
              <div className="mt-4">
                <Button>
                  <TrendingUp className="w-4 h-4 mr-2" />
                  트렌드 분석 시작
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 예측 탭 */}
        <TabsContent value="predictions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Brain className="w-5 h-5 mr-2" />
                예측 모델
              </CardTitle>
              <CardDescription>
                머신러닝을 활용한 비즈니스 예측
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-3">매출 예측</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    과거 매출 데이터를 기반으로 향후 매출을 예측합니다.
                  </p>
                  <Button variant="outline" size="sm">
                    매출 예측 실행
                  </Button>
                </div>
                <div>
                  <h4 className="font-semibold mb-3">고객 행동 예측</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    고객의 구매 패턴과 행동을 분석하여 예측합니다.
                  </p>
                  <Button variant="outline" size="sm">
                    고객 분석 실행
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 인사이트 탭 */}
        <TabsContent value="insights" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Lightbulb className="w-5 h-5 mr-2" />
                비즈니스 인사이트
              </CardTitle>
              <CardDescription>
                데이터에서 발견된 중요한 인사이트와 권장사항
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-4 h-4 text-green-600" />
                    <h4 className="font-semibold">매출 상승 트렌드</h4>
                    <Badge className="bg-green-100 text-green-800">높음</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    최근 30일간 매출이 지속적으로 상승하고 있습니다.
                  </p>
                  <div className="text-xs text-gray-500">
                    신뢰도: 85% • 생성일: 2024-01-15
                  </div>
                </div>

                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Users className="w-4 h-4 text-blue-600" />
                    <h4 className="font-semibold">고가치 고객 세그먼트</h4>
                    <Badge className="bg-blue-100 text-blue-800">중간</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    평균 주문 금액이 높은 고객 세그먼트가 확인되었습니다.
                  </p>
                  <div className="text-xs text-gray-500">
                    신뢰도: 78% • 생성일: 2024-01-14
                  </div>
                </div>

                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="w-4 h-4 text-red-600" />
                    <h4 className="font-semibold">이상 패턴 감지</h4>
                    <Badge className="bg-red-100 text-red-800">높음</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    정상 범위를 벗어나는 매출 패턴이 감지되었습니다.
                  </p>
                  <div className="text-xs text-gray-500">
                    신뢰도: 92% • 생성일: 2024-01-13
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AnalyticsPage; 