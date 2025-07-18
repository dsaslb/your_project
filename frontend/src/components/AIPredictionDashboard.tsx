import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Users,
  ShoppingCart,
  Package,
  BarChart3,
  Brain,
  RefreshCw,
  Play,
  Pause
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

interface SalesPrediction {
  date: string;
  predicted_sales: number;
  confidence: number;
}

interface InventoryPrediction {
  item_id: number;
  item_name: string;
  current_stock: number;
  daily_usage: number;
  days_until_stockout: number;
  reorder_quantity: number;
  urgency: 'critical' | 'high' | 'medium' | 'low';
  recommended_action: string;
}

interface CustomerChurn {
  user_id: number;
  churn_probability: number;
  risk_level: 'high' | 'medium' | 'low';
  recommendations: string[];
}

interface StaffPrediction {
  date: string;
  day_of_week: string;
  predicted_staff: number;
  avg_demand: number;
  season_factor: number;
  event_factor: number;
}

interface AIInsight {
  type: 'positive' | 'warning' | 'critical';
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
}

interface ModelStatus {
  last_trained: string | null;
  accuracy: number;
  training_samples: number;
  is_trained: boolean;
}

interface AIPredictionData {
  sales_forecast: {
    success: boolean;
    predictions: SalesPrediction[];
    total_predicted_sales: number;
    avg_daily_sales: number;
    model_accuracy: number;
  };
  inventory_needs: {
    success: boolean;
    predictions: InventoryPrediction[];
    total_reorder_value: number;
    critical_items_count: number;
  };
  customer_churn: {
    success: boolean;
    high_risk_customers: number;
    medium_risk_customers: number;
    total_customers: number;
    avg_churn_probability: number;
    recommendations: CustomerChurn[];
  };
  staff_requirements: {
    success: boolean;
    predictions: StaffPrediction[];
    total_staff_days: number;
    avg_daily_staff: number;
    peak_days: StaffPrediction[];
  };
  insights: AIInsight[];
}

const COLORS = {
  critical: '#ef4444',
  high: '#f59e0b',
  medium: '#3b82f6',
  low: '#10b981',
  positive: '#10b981',
  warning: '#f59e0b',
  negative: '#ef4444'
};

const AIPredictionDashboard: React.FC = () => {
  const [predictionData, setPredictionData] = useState<AIPredictionData | null>(null);
  const [modelStatus, setModelStatus] = useState<Record<string, ModelStatus>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isTraining, setIsTraining] = useState(false);
  const [error, setError] = useState<string>('');
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    fetchModelStatus();
    fetchPredictions();
  }, []);

  const fetchModelStatus = async () => {
    try {
      const response = await fetch('/api/ai/models/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setModelStatus(data.models);
      }
    } catch (err) {
      console.error('모델 상태 조회 실패:', err);
    }
  };

  const fetchPredictions = async () => {
    try {
      setIsLoading(true);
      setError('');

      const response = await fetch('/api/ai/predict/comprehensive', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('예측 데이터를 불러올 수 없습니다.');
      }

      const data = await response.json();
      if (data.success) {
        setPredictionData(data);
        setLastUpdate(new Date().toLocaleString());
      } else {
        setError(data.error || '예측에 실패했습니다.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류');
    } finally {
      setIsLoading(false);
    }
  };

  const trainSalesModel = async () => {
    try {
      setIsTraining(true);
      setError('');

      const response = await fetch('/api/ai/train/sales', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('모델 훈련에 실패했습니다.');
      }

      const data = await response.json();
      if (data.success) {
        // 모델 상태 업데이트
        await fetchModelStatus();
        // 예측 데이터 새로고침
        await fetchPredictions();
      } else {
        setError(data.error || '훈련에 실패했습니다.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '훈련 중 오류 발생');
    } finally {
      setIsTraining(false);
    }
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'positive': return <CheckCircle className="w-4 h-4" />;
      case 'warning': return <AlertTriangle className="w-4 h-4" />;
      case 'critical': return <AlertTriangle className="w-4 h-4" />;
      default: return <Brain className="w-4 h-4" />;
    }
  };

  const getInsightColor = (type: string) => {
    return COLORS[type as keyof typeof COLORS] || COLORS.medium;
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p>AI 예측 데이터를 불러오는 중...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI 예측 대시보드</h1>
          <p className="text-muted-foreground">
            마지막 업데이트: {lastUpdate}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            onClick={fetchPredictions}
            disabled={isLoading}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            새로고침
          </Button>
          <Button 
            onClick={trainSalesModel}
            disabled={isTraining}
          >
            {isTraining ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                훈련 중...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                모델 훈련
              </>
            )}
          </Button>
        </div>
      </div>

      {/* 모델 상태 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5" />
            AI 모델 상태
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(modelStatus).map(([modelName, status]) => (
              <div key={modelName} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <div className="font-medium capitalize">
                    {modelName.replace('_', ' ')}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    정확도: {status.accuracy ? `${(status.accuracy * 100).toFixed(1)}%` : 'N/A'}
                  </div>
                </div>
                <Badge variant={status.is_trained ? 'default' : 'secondary'}>
                  {status.is_trained ? '훈련됨' : '미훈련'}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* AI 인사이트 */}
      {predictionData?.insights && predictionData.insights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5" />
              AI 인사이트
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {predictionData.insights.map((insight, index) => (
                <Alert key={index} className="border-l-4" style={{ borderLeftColor: getInsightColor(insight.type) }}>
                  <div className="flex items-start gap-2">
                    <div style={{ color: getInsightColor(insight.type) }}>
                      {getInsightIcon(insight.type)}
                    </div>
                    <AlertDescription className="flex-1">
                      <div className="font-medium">{insight.title}</div>
                      <div className="text-sm text-muted-foreground mt-1">
                        {insight.description}
                      </div>
                      <Badge variant="outline" className="mt-2">
                        {insight.priority}
                      </Badge>
                    </AlertDescription>
                  </div>
                </Alert>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 예측 데이터 */}
      <Tabs defaultValue="sales" className="space-y-4">
        <TabsList>
          <TabsTrigger value="sales">매출 예측</TabsTrigger>
          <TabsTrigger value="inventory">재고 예측</TabsTrigger>
          <TabsTrigger value="customers">고객 이탈</TabsTrigger>
          <TabsTrigger value="staff">인력 예측</TabsTrigger>
        </TabsList>

        {/* 매출 예측 */}
        <TabsContent value="sales" className="space-y-6">
          {predictionData?.sales_forecast.success && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4" />
                      총 예측 매출
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {predictionData.sales_forecast.total_predicted_sales.toLocaleString()}원
                    </div>
                    <div className="text-sm text-muted-foreground">
                      30일 예측
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="w-4 h-4" />
                      일평균 매출
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {predictionData.sales_forecast.avg_daily_sales.toLocaleString()}원
                    </div>
                    <div className="text-sm text-muted-foreground">
                      일일 평균
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Brain className="w-4 h-4" />
                      모델 정확도
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {(predictionData.sales_forecast.model_accuracy * 100).toFixed(1)}%
                    </div>
                    <div className="text-sm text-muted-foreground">
                      R² 점수
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>매출 예측 트렌드</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={predictionData.sales_forecast.predictions}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip formatter={(value) => `${Number(value).toLocaleString()}원`} />
                      <Line 
                        type="monotone" 
                        dataKey="predicted_sales" 
                        stroke="#3b82f6" 
                        strokeWidth={2}
                        name="예측 매출"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* 재고 예측 */}
        <TabsContent value="inventory" className="space-y-6">
          {predictionData?.inventory_needs.success && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Package className="w-4 h-4" />
                      총 재주문 금액
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {predictionData.inventory_needs.total_reorder_value.toLocaleString()}원
                    </div>
                    <div className="text-sm text-muted-foreground">
                      필요 재고 금액
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" />
                      긴급 품목
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-red-600">
                      {predictionData.inventory_needs.critical_items_count}개
                    </div>
                    <div className="text-sm text-muted-foreground">
                      즉시 주문 필요
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <ShoppingCart className="w-4 h-4" />
                      총 품목 수
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {predictionData.inventory_needs.predictions.length}개
                    </div>
                    <div className="text-sm text-muted-foreground">
                      재고 관리 품목
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>재고 긴급도 분포</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {['critical', 'high', 'medium', 'low'].map((urgency) => {
                      const items = predictionData.inventory_needs.predictions.filter(
                        item => item.urgency === urgency
                      );
                      return (
                        <div key={urgency} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div 
                              className="w-3 h-3 rounded-full"
                              style={{ backgroundColor: COLORS[urgency as keyof typeof COLORS] }}
                            />
                            <span className="capitalize">{urgency}</span>
                          </div>
                          <div className="flex items-center gap-4">
                            <span className="font-medium">{items.length}개</span>
                            <Progress 
                              value={(items.length / predictionData.inventory_needs.predictions.length) * 100} 
                              className="w-24"
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>긴급 재고 품목</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {predictionData.inventory_needs.predictions
                      .filter(item => item.urgency === 'critical')
                      .slice(0, 5)
                      .map((item) => (
                        <div key={item.item_id} className="flex items-center justify-between p-3 border rounded-lg">
                          <div>
                            <div className="font-medium">{item.item_name}</div>
                            <div className="text-sm text-muted-foreground">
                              현재: {item.current_stock}개 | 필요: {item.reorder_quantity}개
                            </div>
                          </div>
                          <Badge variant="destructive">
                            {item.days_until_stockout.toFixed(1)}일 후 소진
                          </Badge>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* 고객 이탈 */}
        <TabsContent value="customers" className="space-y-6">
          {predictionData?.customer_churn.success && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Users className="w-4 h-4" />
                      총 고객
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {predictionData.customer_churn.total_customers}명
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" />
                      고위험 고객
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-red-600">
                      {predictionData.customer_churn.high_risk_customers}명
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {((predictionData.customer_churn.high_risk_customers / predictionData.customer_churn.total_customers) * 100).toFixed(1)}%
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      중위험 고객
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-yellow-600">
                      {predictionData.customer_churn.medium_risk_customers}명
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {((predictionData.customer_churn.medium_risk_customers / predictionData.customer_churn.total_customers) * 100).toFixed(1)}%
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingDown className="w-4 h-4" />
                      평균 이탈 확률
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {(predictionData.customer_churn.avg_churn_probability * 100).toFixed(1)}%
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>고위험 고객 목록</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {predictionData.customer_churn.recommendations
                      .filter(customer => customer.risk_level === 'high')
                      .slice(0, 5)
                      .map((customer) => (
                        <div key={customer.user_id} className="p-3 border rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">고객 #{customer.user_id}</span>
                            <Badge variant="destructive">
                              {(customer.churn_probability * 100).toFixed(1)}% 이탈 위험
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground">
                            권장사항: {customer.recommendations.join(', ')}
                          </div>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* 인력 예측 */}
        <TabsContent value="staff" className="space-y-6">
          {predictionData?.staff_requirements.success && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Users className="w-4 h-4" />
                      일평균 필요 인력
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {predictionData.staff_requirements.avg_daily_staff.toFixed(1)}명
                    </div>
                    <div className="text-sm text-muted-foreground">
                      14일 평균
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4" />
                      총 필요 인력일
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {predictionData.staff_requirements.total_staff_days}일
                    </div>
                    <div className="text-sm text-muted-foreground">
                      14일 합계
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" />
                      피크 일수
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {predictionData.staff_requirements.peak_days.length}일
                    </div>
                    <div className="text-sm text-muted-foreground">
                      인력 부족 예상
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>일별 필요 인력 예측</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={predictionData.staff_requirements.predictions}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="day_of_week" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="predicted_staff" fill="#3b82f6" name="필요 인력" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AIPredictionDashboard; 