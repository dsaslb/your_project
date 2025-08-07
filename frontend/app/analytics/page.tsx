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
import { toast } from 'sonner';

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

// 샘플 데이터
const sampleAnalyticsSummary: AnalyticsSummary = {
  total_analyses: 156,
  total_models: 12,
  total_insights: 89,
  realtime_metrics: 45,
  analysis_types: {
    trend: 45,
    prediction: 32,
    correlation: 28,
    clustering: 23,
    anomaly: 18
  },
  insight_categories: {
    sales: 52,
    customer: 31,
    anomaly: 6
  },
  model_accuracy: {
    'sales_prediction': 87.5,
    'customer_segmentation': 92.3,
    'anomaly_detection': 94.1,
    'trend_analysis': 89.7
  }
};

const sampleSalesPrediction: SalesPrediction = {
  predictions: [1250000, 1320000, 1280000, 1350000, 1400000, 1380000, 1450000, 1420000, 1480000, 1500000],
  dates: ['2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19', '2024-01-20', '2024-01-21', '2024-01-22', '2024-01-23', '2024-01-24', '2024-01-25'],
  model_accuracy: 87.5,
  total_predicted_sales: 13850000,
  avg_daily_sales: 1385000
};

const AnalyticsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [salesPrediction, setSalesPrediction] = useState<SalesPrediction | null>(null);

  // 데이터 로드 함수들
  const loadSummary = useCallback(async () => {
    try {
      setSummary(sampleAnalyticsSummary);
    } catch (error) {
      toast.error('분석 요약을 불러오는데 실패했습니다');
    }
  }, []);

  const loadSalesPrediction = useCallback(async () => {
    try {
      setSalesPrediction(sampleSalesPrediction);
    } catch (error) {
      toast.error('매출 예측을 불러오는데 실패했습니다');
    }
  }, []);

  // 초기 데이터 로드
  useEffect(() => {
    const loadAllData = async () => {
      setIsLoading(true);
      try {
        await Promise.all([
          loadSummary(),
          loadSalesPrediction()
        ]);
      } catch (error) {
        toast.error('데이터 로드에 실패했습니다');
      } finally {
        setIsLoading(false);
      }
    };
    loadAllData();
  }, [loadSummary, loadSalesPrediction]);

  const handleRefresh = async () => {
    setIsLoading(true);
    try {
      await Promise.all([
        loadSummary(),
        loadSalesPrediction()
      ]);
      toast.success('데이터가 새로고침되었습니다');
    } catch (error) {
      toast.error('새로고침에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('ko-KR').format(num);
  };

  return (
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Brain className="w-8 h-8 text-purple-400" />
          데이터 분석
        </h1>
        <p className="text-gray-300 mt-2">AI 기반 데이터 분석 및 인사이트를 제공합니다</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-3 mb-6">
        <Button 
          onClick={handleRefresh}
          disabled={isLoading}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          새로고침
        </Button>
      </div>

      {/* 분석 요약 */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">총 분석</CardTitle>
              <BarChart3 className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{formatNumber(summary.total_analyses)}</div>
              <p className="text-xs text-gray-300">완료된 분석 수</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">AI 모델</CardTitle>
              <Brain className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{formatNumber(summary.total_models)}</div>
              <p className="text-xs text-gray-300">활성 AI 모델</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">인사이트</CardTitle>
              <Lightbulb className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{formatNumber(summary.total_insights)}</div>
              <p className="text-xs text-gray-300">발견된 인사이트</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">실시간 메트릭</CardTitle>
              <Activity className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{formatNumber(summary.realtime_metrics)}</div>
              <p className="text-xs text-gray-300">모니터링 중</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 메인 탭 */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="bg-white/10 border border-white/20">
          <TabsTrigger value="overview" className="text-white data-[state=active]:bg-white/20">개요</TabsTrigger>
          <TabsTrigger value="predictions" className="text-white data-[state=active]:bg-white/20">예측</TabsTrigger>
          <TabsTrigger value="insights" className="text-white data-[state=active]:bg-white/20">인사이트</TabsTrigger>
        </TabsList>

        {/* 개요 탭 */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 분석 유형 */}
            <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
              <CardHeader>
                <CardTitle className="text-white">분석 유형별 통계</CardTitle>
                <CardDescription className="text-gray-300">다양한 분석 유형의 사용 현황</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-blue-400" />
                      <span className="text-white">트렌드 분석</span>
                    </div>
                    <Badge className="bg-blue-500/20 text-blue-400">
                      {summary?.analysis_types.trend}회
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Brain className="w-4 h-4 text-purple-400" />
                      <span className="text-white">예측 분석</span>
                    </div>
                    <Badge className="bg-purple-500/20 text-purple-400">
                      {summary?.analysis_types.prediction}회
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-green-400" />
                      <span className="text-white">상관관계 분석</span>
                    </div>
                    <Badge className="bg-green-500/20 text-green-400">
                      {summary?.analysis_types.correlation}회
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4 text-orange-400" />
                      <span className="text-white">클러스터링</span>
                    </div>
                    <Badge className="bg-orange-500/20 text-orange-400">
                      {summary?.analysis_types.clustering}회
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-red-400" />
                      <span className="text-white">이상 탐지</span>
                    </div>
                    <Badge className="bg-red-500/20 text-red-400">
                      {summary?.analysis_types.anomaly}회
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 모델 정확도 */}
            <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
              <CardHeader>
                <CardTitle className="text-white">AI 모델 정확도</CardTitle>
                <CardDescription className="text-gray-300">각 AI 모델의 성능 지표</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {summary && Object.entries(summary.model_accuracy).map(([model, accuracy]) => (
                    <div key={model} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Brain className="w-4 h-4 text-purple-400" />
                        <span className="text-white capitalize">
                          {model.replace('_', ' ')}
                        </span>
                      </div>
                      <Badge className="bg-purple-500/20 text-purple-400">
                        {accuracy.toFixed(1)}%
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 예측 탭 */}
        <TabsContent value="predictions" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <CardTitle className="text-white">매출 예측</CardTitle>
              <CardDescription className="text-gray-300">AI 기반 매출 예측 결과</CardDescription>
            </CardHeader>
            <CardContent>
              {salesPrediction ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <DollarSign className="w-4 h-4 text-green-400" />
                        <span className="text-white font-medium">예측 정확도</span>
                      </div>
                      <div className="text-2xl font-bold text-white">{salesPrediction.model_accuracy.toFixed(1)}%</div>
                    </div>
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-4 h-4 text-blue-400" />
                        <span className="text-white font-medium">총 예측 매출</span>
                      </div>
                      <div className="text-2xl font-bold text-white">{formatCurrency(salesPrediction.total_predicted_sales)}</div>
                    </div>
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Activity className="w-4 h-4 text-purple-400" />
                        <span className="text-white font-medium">일평균 매출</span>
                      </div>
                      <div className="text-2xl font-bold text-white">{formatCurrency(salesPrediction.avg_daily_sales)}</div>
                    </div>
                  </div>
                  
                  <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                    <h4 className="text-white font-medium mb-4">10일간 매출 예측</h4>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                      {salesPrediction.predictions.slice(0, 10).map((prediction, index) => (
                        <div key={index} className="text-center">
                          <div className="text-sm text-gray-300 mb-1">
                            {new Date(salesPrediction.dates[index]).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
                          </div>
                          <div className="text-lg font-bold text-white">
                            {formatCurrency(prediction)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-300">
                  예측 데이터를 불러오는 중...
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 인사이트 탭 */}
        <TabsContent value="insights" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <CardTitle className="text-white">주요 인사이트</CardTitle>
              <CardDescription className="text-gray-300">AI가 발견한 중요한 인사이트</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-4 h-4 text-green-400" />
                    <span className="text-white font-medium">매출 트렌드</span>
                  </div>
                  <p className="text-gray-300">
                    주말 매출이 평일 대비 평균 25% 높게 나타나며, 특히 오후 2-4시 시간대에 매출이 집중됩니다.
                  </p>
                </div>
                
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Users className="w-4 h-4 text-blue-400" />
                    <span className="text-white font-medium">고객 행동</span>
                  </div>
                  <p className="text-gray-300">
                    신규 고객의 60%가 첫 구매 후 30일 내에 재방문하며, 이는 고객 유지 전략의 효과를 보여줍니다.
                  </p>
                </div>
                
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-400" />
                    <span className="text-white font-medium">이상 패턴</span>
                  </div>
                  <p className="text-gray-300">
                    지난 주 화요일 오전 매출이 평소 대비 40% 감소한 이상 패턴이 감지되었습니다.
                  </p>
                </div>
                
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Brain className="w-4 h-4 text-purple-400" />
                    <span className="text-white font-medium">예측 인사이트</span>
                  </div>
                  <p className="text-gray-300">
                    다음 달 매출은 현재 트렌드를 기반으로 8-12% 증가할 것으로 예측되며, 특히 온라인 주문이 증가할 것으로 보입니다.
                  </p>
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