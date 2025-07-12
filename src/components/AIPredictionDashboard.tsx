'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  RefreshCw,
  Brain,
  Target,
  Users,
  Package,
  DollarSign,
  Clock, // pyright: ignore
  Activity // pyright: ignore
} from 'lucide-react'; // pyright: ignore
import { toast } from 'sonner'; // pyright: ignore

interface PredictionData {
  date: string;
  predicted_value: number;
  confidence: number;
  model_type: string;
  features: any;
}

interface InventoryPrediction {
  item_name: string;
  current_stock: number;
  min_stock: number;
  days_until_stockout: number;
  risk_level: string;
  recommended_order: number;
}

interface CustomerFlowPrediction {
  tomorrow_predictions: Record<string, number>;
  peak_hours: [number, number][];
  total_predicted_customers: number;
}

interface StaffingPrediction {
  needed_staff: number;
  current_staff: number;
  shortage: number;
  surplus: number;
  recommendation: string;
}

interface AIInsight {
  type: string;
  title: string;
  description: string;
  trend?: string;
  change_percent?: number;
  priority: string;
  [key: string]: any;
}

interface PredictionAlert {
  type: string;
  title: string;
  description: string;
  severity: string;
  action_required: boolean;
  [key: string]: any;
}

interface ModelPerformance {
  mae: number;
  mse: number;
  rmse: number;
  r2_score: number;
  accuracy: number;
  last_updated: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export default function AIPredictionDashboard() {
  const [predictions, setPredictions] = useState<{
    sales: PredictionData[];
    inventory: InventoryPrediction[];
    customer_flow: CustomerFlowPrediction;
    staffing: StaffingPrediction;
  } | null>(null);
  
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [alerts, setAlerts] = useState<PredictionAlert[]>([]);
  const [modelPerformance, setModelPerformance] = useState<Record<string, ModelPerformance>>({});
  const [accuracyTrends, setAccuracyTrends] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  // 데이터 로드 함수
  const loadPredictionData = useCallback(async () => {
    try {
      setLoading(true);
      
      // 실시간 예측 데이터
      const predictionsResponse = await fetch('/api/ai/prediction/real-time');
      if (predictionsResponse.ok) {
        const predictionsData = await predictionsResponse.json();
        setPredictions(predictionsData.predictions);
      }
      
      // AI 인사이트
      const insightsResponse = await fetch('/api/ai/prediction/insights');
      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json();
        setInsights(insightsData.insights);
      }
      
      // 예측 알림
      const alertsResponse = await fetch('/api/ai/prediction/alerts');
      if (alertsResponse.ok) {
        const alertsData = await alertsResponse.json();
        setAlerts(alertsData.alerts);
      }
      
      // 모델 성능
      const accuracyResponse = await fetch('/api/ai/prediction/accuracy');
      if (accuracyResponse.ok) {
        const accuracyData = await accuracyResponse.json();
        setModelPerformance(accuracyData.model_performance);
        setAccuracyTrends(accuracyData.accuracy_trends);
      }
      
    } catch (error) {
      console.error('AI 예측 데이터 로드 실패:', error);
      toast.error('예측 데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }, []);

  // 모델 재훈련
  const retrainModel = async (modelType: string) => {
    try {
      setRefreshing(true);
      const response = await fetch('/api/ai/prediction/model/retrain', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ model_type: modelType }),
      });
      
      if (response.ok) {
        toast.success(`${modelType} 모델 재훈련이 완료되었습니다.`);
        await loadPredictionData(); // 데이터 새로고침
      } else {
        toast.error('모델 재훈련에 실패했습니다.');
      }
    } catch (error) {
      console.error('모델 재훈련 실패:', error);
      toast.error('모델 재훈련 중 오류가 발생했습니다.');
    } finally {
      setRefreshing(false);
    }
  };

  // 초기 로드 및 주기적 업데이트
  useEffect(() => {
    loadPredictionData();
    
    // 5분마다 자동 새로고침
    const interval = setInterval(loadPredictionData, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [loadPredictionData]);

  // 위험도별 색상
  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  // 우선순위별 색상
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // 심각도별 색상
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'border-red-500 bg-red-50';
      case 'medium': return 'border-yellow-500 bg-yellow-50';
      case 'low': return 'border-green-500 bg-green-50';
      default: return 'border-gray-500 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span>AI 예측 데이터를 분석 중...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center space-x-2">
            <Brain className="h-8 w-8 text-blue-600" />
            <span>AI 예측 분석 대시보드</span>
          </h1>
          <p className="text-gray-600 mt-2">
            머신러닝 기반 실시간 예측 및 인사이트
          </p>
        </div>
        <Button 
          onClick={loadPredictionData} 
          disabled={refreshing}
          className="flex items-center space-x-2"
        >
          <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span>새로고침</span>
        </Button>
      </div>

      {/* 알림 섹션 */}
      {alerts.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-xl font-semibold flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            <span>예측 기반 알림 ({alerts.length})</span>
          </h2>
          <div className="grid gap-3">
            {alerts.map((alert, index) => (
              <Alert key={index} className={getSeverityColor(alert.severity)}>
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>{alert.title}</AlertTitle>
                <AlertDescription>{alert.description}</AlertDescription>
                {alert.action_required && (
                  <Badge variant="destructive" className="mt-2">
                    조치 필요
                  </Badge>
                )}
              </Alert>
            ))}
          </div>
        </div>
      )}

      {/* 메인 탭 */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="sales">매출 예측</TabsTrigger>
          <TabsTrigger value="inventory">재고 예측</TabsTrigger>
          <TabsTrigger value="staffing">인력 예측</TabsTrigger>
          <TabsTrigger value="performance">모델 성능</TabsTrigger>
        </TabsList>

        {/* 개요 탭 */}
        <TabsContent value="overview" className="space-y-6">
          {/* 핵심 지표 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">예상 매출 (7일)</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {predictions?.sales ? 
                    `${Math.round(predictions.sales.reduce((sum, p) => sum + p.predicted_value, 0) / 10000)}만원` : 
                    'N/A'
                  }
                </div>
                <p className="text-xs text-muted-foreground">
                  평균 신뢰도: {predictions?.sales ? 
                    `${Math.round(predictions.sales.reduce((sum, p) => sum + p.confidence, 0) / predictions.sales.length * 100)}%` : 
                    'N/A'
                  }
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">예상 고객 수</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {predictions?.customer_flow?.total_predicted_customers || 'N/A'}
                </div>
                <p className="text-xs text-muted-foreground">
                  피크 시간: {predictions?.customer_flow?.peak_hours?.[0]?.[0] || 'N/A'}시
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">필요 인력</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {predictions?.staffing?.needed_staff || 'N/A'}
                </div>
                <p className="text-xs text-muted-foreground">
                  {predictions?.staffing?.shortage ? 
                    `${predictions.staffing.shortage}명 부족` : 
                    predictions?.staffing?.surplus ? 
                    `${predictions.staffing.surplus}명 과다` : 
                    '적정'
                  }
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">재고 위험</CardTitle>
                <Package className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {predictions?.inventory?.filter(item => item.risk_level === 'critical').length || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  위험 품목 수
                </p>
              </CardContent>
            </Card>
          </div>

          {/* AI 인사이트 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="h-5 w-5" />
                <span>AI 인사이트</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {insights.map((insight, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 border rounded-lg">
                    <div className="flex-shrink-0">
                      {insight.trend === 'increasing' ? (
                        <TrendingUp className="h-5 w-5 text-green-500" />
                      ) : insight.trend === 'decreasing' ? (
                        <TrendingDown className="h-5 w-5 text-red-500" />
                      ) : (
                        <Activity className="h-5 w-5 text-blue-500" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h4 className="font-medium">{insight.title}</h4>
                        <Badge className={getPriorityColor(insight.priority)}>
                          {insight.priority}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
                      {insight.change_percent && (
                        <p className="text-xs text-gray-500 mt-1">
                          변화율: {insight.change_percent > 0 ? '+' : ''}{insight.change_percent}%
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 매출 예측 탭 */}
        <TabsContent value="sales" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <DollarSign className="h-5 w-5" />
                <span>7일 매출 예측</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {predictions?.sales && (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={predictions.sales}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip 
                      formatter={(value: any) => [`${Math.round(value).toLocaleString()}원`, '예상 매출']}
                      labelFormatter={(label) => `날짜: ${label}`}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="predicted_value" 
                      stroke="#8884d8" 
                      strokeWidth={2}
                      dot={{ fill: '#8884d8', strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>신뢰도 분석</CardTitle>
              </CardHeader>
              <CardContent>
                {predictions?.sales && (
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={predictions.sales}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip formatter={(value: any) => [`${(value * 100).toFixed(1)}%`, '신뢰도']} />
                      <Bar dataKey="confidence" fill="#82ca9d" />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>모델 정보</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {predictions?.sales?.[0] && (
                    <>
                      <div className="flex justify-between">
                        <span>모델 타입:</span>
                        <Badge variant="outline">{predictions.sales[0].model_type}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span>평균 신뢰도:</span>
                        <span className="font-medium">
                          {(predictions.sales.reduce((sum, p) => sum + p.confidence, 0) / predictions.sales.length * 100).toFixed(1)}%
                        </span>
                      </div>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 재고 예측 탭 */}
        <TabsContent value="inventory" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Package className="h-5 w-5" />
                <span>재고 부족 예측</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {predictions?.inventory?.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h4 className="font-medium">{item.item_name}</h4>
                        <Badge className={getRiskColor(item.risk_level)}>
                          {item.risk_level}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-3 gap-4 mt-2 text-sm">
                        <div>
                          <span className="text-gray-500">현재 재고:</span>
                          <span className="ml-2 font-medium">{item.current_stock}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">소진까지:</span>
                          <span className="ml-2 font-medium">{item.days_until_stockout.toFixed(1)}일</span>
                        </div>
                        <div>
                          <span className="text-gray-500">권장 발주:</span>
                          <span className="ml-2 font-medium">{item.recommended_order}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex-shrink-0">
                      <Progress 
                        value={Math.min(100, (item.current_stock / item.min_stock) * 100)} 
                        className="w-20"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 인력 예측 탭 */}
        <TabsContent value="staffing" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>인력 필요 예측</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {predictions?.staffing && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {predictions.staffing.needed_staff}
                      </div>
                      <div className="text-sm text-gray-600">필요 인력</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {predictions.staffing.current_staff}
                      </div>
                      <div className="text-sm text-gray-600">현재 인력</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className={`text-2xl font-bold ${
                        predictions.staffing.shortage > 0 ? 'text-red-600' : 
                        predictions.staffing.surplus > 0 ? 'text-yellow-600' : 'text-green-600'
                      }`}>
                        {predictions.staffing.shortage > 0 ? predictions.staffing.shortage : 
                         predictions.staffing.surplus > 0 ? predictions.staffing.surplus : 0}
                      </div>
                      <div className="text-sm text-gray-600">
                        {predictions.staffing.shortage > 0 ? '부족' : 
                         predictions.staffing.surplus > 0 ? '과다' : '적정'}
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-medium mb-2">AI 권장사항</h4>
                    <p className="text-gray-600">{predictions.staffing.recommendation}</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 모델 성능 탭 */}
        <TabsContent value="performance" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {Object.entries(modelPerformance).map(([modelType, performance]) => (
              <Card key={modelType}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="capitalize">{modelType} 모델</CardTitle>
                    <Button 
                      size="sm" 
                      onClick={() => retrainModel(modelType)}
                      disabled={refreshing}
                    >
                      <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                      재훈련
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span>정확도:</span>
                      <span className="font-medium">{(performance.accuracy * 100).toFixed(1)}%</span>
                    </div>
                    <Progress value={performance.accuracy * 100} />
                    
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-gray-500">MAE:</span>
                        <span className="ml-1">{performance.mae.toFixed(4)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">RMSE:</span>
                        <span className="ml-1">{performance.rmse.toFixed(4)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">R²:</span>
                        <span className="ml-1">{performance.r2_score.toFixed(4)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">MSE:</span>
                        <span className="ml-1">{performance.mse.toFixed(4)}</span>
                      </div>
                    </div>
                    
                    <div className="text-xs text-gray-500">
                      마지막 업데이트: {new Date(performance.last_updated).toLocaleString()}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {accuracyTrends.overall_accuracy && (
            <Card>
              <CardHeader>
                <CardTitle>전체 모델 성능 트렌드</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {(accuracyTrends.overall_accuracy * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">
                    전체 평균 정확도 ({accuracyTrends.total_predictions}개 예측)
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
} 