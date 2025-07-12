import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Brain, 
  TrendingUp, 
  TrendingDown, 
  Play, 
  Pause, 
  RefreshCw,
  BarChart3,
  Activity,
  Target,
  Lightbulb,
  Clock,
  CheckCircle,
  AlertTriangle,
  Info,
  Zap,
  Settings,
  Eye,
  Calendar,
  Users,
  Package
} from 'lucide-react';
import { toast } from 'sonner';

interface ModelStatus {
  type: string;
  version: string;
  last_trained: string;
  accuracy: number;
  status: string;
  parameters: any;
}

interface ModelPerformance {
  mae: number;
  mse: number;
  rmse: number;
  r2_score: number;
  accuracy: number;
  last_updated: string;
  training_samples: number;
  test_samples: number;
}

interface Prediction {
  timestamp: string;
  prediction_type: string;
  model_type: string;
  predicted_value: number;
  confidence: number;
  features: any;
  metadata: any;
}

interface AutoLearningHistory {
  id: number;
  timestamp: string;
  model_type: string;
  action: string;
  performance_before: number;
  performance_after: number;
  improvement: number;
  training_data_size: number;
  description: string;
}

interface Insight {
  id: number;
  timestamp: string;
  insight_type: string;
  title: string;
  description: string;
  confidence: number;
  impact_score: number;
  recommendations: string[];
  data_sources: string[];
}

interface DashboardData {
  models_status: {
    models: Record<string, ModelStatus>;
    performance: Record<string, ModelPerformance>;
    auto_learning_active: boolean;
    total_predictions: number;
    last_updated: string;
  };
  recent_predictions: Prediction[];
  learning_summary: {
    active: boolean;
    recent_improvements: number;
    total_models: number;
  };
  insights_summary: {
    total_insights: number;
    high_confidence_insights: number;
    high_impact_insights: number;
  };
  accuracy_summary: {
    sales_accuracy: number;
    overall_accuracy: number;
  };
  last_updated: string;
}

const AdvancedAIPrediction: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [recentPredictions, setRecentPredictions] = useState<Prediction[]>([]);
  const [autoLearningHistory, setAutoLearningHistory] = useState<AutoLearningHistory[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoLearningActive, setAutoLearningActive] = useState(false);

  // 대시보드 데이터 조회
  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/advanced-ai/dashboard');
      const data = await response.json();

      if (data.success) {
        setDashboardData(data.data);
        setAutoLearningActive(data.data.learning_summary.active);
      } else {
        toast.error('대시보드 데이터 조회 실패');
      }
    } catch (error) {
      console.error('대시보드 데이터 조회 오류:', error);
      toast.error('대시보드 데이터 조회 중 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  };

  // 최근 예측 조회
  const fetchRecentPredictions = async () => {
    try {
      const response = await fetch('/api/advanced-ai/predictions/recent?limit=20');
      const data = await response.json();

      if (data.success) {
        setRecentPredictions(data.data.predictions);
      } else {
        toast.error('최근 예측 조회 실패');
      }
    } catch (error) {
      console.error('최근 예측 조회 오류:', error);
      toast.error('최근 예측 조회 중 오류가 발생했습니다');
    }
  };

  // 자동 학습 이력 조회
  const fetchAutoLearningHistory = async () => {
    try {
      const response = await fetch('/api/advanced-ai/auto-learning/history');
      const data = await response.json();

      if (data.success) {
        setAutoLearningHistory(data.data.history);
      } else {
        toast.error('자동 학습 이력 조회 실패');
      }
    } catch (error) {
      console.error('자동 학습 이력 조회 오류:', error);
      toast.error('자동 학습 이력 조회 중 오류가 발생했습니다');
    }
  };

  // 인사이트 조회
  const fetchInsights = async () => {
    try {
      const response = await fetch('/api/advanced-ai/insights');
      const data = await response.json();

      if (data.success) {
        setInsights(data.data.insights);
      } else {
        toast.error('인사이트 조회 실패');
      }
    } catch (error) {
      console.error('인사이트 조회 오류:', error);
      toast.error('인사이트 조회 중 오류가 발생했습니다');
    }
  };

  // 자동 학습 시작/중지
  const toggleAutoLearning = async () => {
    try {
      const action = autoLearningActive ? 'stop' : 'start';
      const response = await fetch(`/api/advanced-ai/${action}-auto-learning`, {
        method: 'POST'
      });
      const data = await response.json();

      if (data.success) {
        setAutoLearningActive(!autoLearningActive);
        toast.success(`자동 학습이 ${autoLearningActive ? '중지' : '시작'}되었습니다`);
        fetchDashboardData();
      } else {
        toast.error(data.error);
      }
    } catch (error) {
      console.error('자동 학습 토글 오류:', error);
      toast.error('자동 학습 상태 변경 중 오류가 발생했습니다');
    }
  };

  // 고도화된 매출 예측
  const predictSalesAdvanced = async () => {
    try {
      const response = await fetch('/api/advanced-ai/predict/sales', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ days_ahead: 7 })
      });
      const data = await response.json();

      if (data.success) {
        toast.success('매출 예측이 완료되었습니다');
        fetchRecentPredictions();
      } else {
        toast.error(data.error);
      }
    } catch (error) {
      console.error('매출 예측 오류:', error);
      toast.error('매출 예측 중 오류가 발생했습니다');
    }
  };

  // 고도화된 재고 예측
  const predictInventoryAdvanced = async () => {
    try {
      const response = await fetch('/api/advanced-ai/predict/inventory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items: ['item1', 'item2', 'item3', 'item4', 'item5'] })
      });
      const data = await response.json();

      if (data.success) {
        toast.success('재고 예측이 완료되었습니다');
        fetchRecentPredictions();
      } else {
        toast.error(data.error);
      }
    } catch (error) {
      console.error('재고 예측 오류:', error);
      toast.error('재고 예측 중 오류가 발생했습니다');
    }
  };

  // 고도화된 인력 예측
  const predictStaffingAdvanced = async () => {
    try {
      const targetDate = new Date();
      targetDate.setDate(targetDate.getDate() + 7);
      
      const response = await fetch('/api/advanced-ai/predict/staffing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_date: targetDate.toISOString() })
      });
      const data = await response.json();

      if (data.success) {
        toast.success('인력 예측이 완료되었습니다');
        fetchRecentPredictions();
      } else {
        toast.error(data.error);
      }
    } catch (error) {
      console.error('인력 예측 오류:', error);
      toast.error('인력 예측 중 오류가 발생했습니다');
    }
  };

  // 데이터 새로고침
  const refreshData = async () => {
    setLoading(true);
    await Promise.all([
      fetchDashboardData(),
      fetchRecentPredictions(),
      fetchAutoLearningHistory(),
      fetchInsights()
    ]);
    setLoading(false);
  };

  useEffect(() => {
    refreshData();
    
    // 30초마다 자동 새로고침
    const interval = setInterval(refreshData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getPredictionTypeIcon = (type: string) => {
    switch (type) {
      case 'sales': return <TrendingUp className="w-4 h-4" />;
      case 'inventory': return <Package className="w-4 h-4" />;
      case 'staffing': return <Users className="w-4 h-4" />;
      case 'customer_flow': return <Activity className="w-4 h-4" />;
      default: return <Target className="w-4 h-4" />;
    }
  };

  const getInsightTypeIcon = (type: string) => {
    switch (type) {
      case 'trend_analysis': return <TrendingUp className="w-4 h-4" />;
      case 'anomaly_detection': return <AlertTriangle className="w-4 h-4" />;
      case 'seasonal_pattern': return <Calendar className="w-4 h-4" />;
      default: return <Lightbulb className="w-4 h-4" />;
    }
  };

  const formatValue = (value: number, type: string) => {
    switch (type) {
      case 'sales':
        return `₩${value.toLocaleString()}`;
      case 'inventory':
        return `${Math.round(value)}개`;
      case 'staffing':
        return `${Math.round(value)}명`;
      case 'customer_flow':
        return `${Math.round(value)}명`;
      default:
        return value.toLocaleString();
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">고도화된 AI 예측 시스템</h1>
          <p className="text-muted-foreground">
            머신러닝 기반 실시간 예측, 자동 학습, 인사이트 분석
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={refreshData} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            새로고침
          </Button>
          <Button 
            onClick={toggleAutoLearning} 
            variant={autoLearningActive ? "destructive" : "default"}
          >
            {autoLearningActive ? (
              <>
                <Pause className="w-4 h-4 mr-2" />
                자동 학습 중지
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                자동 학습 시작
              </>
            )}
          </Button>
        </div>
      </div>

      {/* 자동 학습 상태 */}
      <Alert>
        <Brain className="h-4 w-4" />
        <AlertDescription>
          자동 학습 상태: {autoLearningActive ? '활성화' : '비활성화'} | 
          마지막 업데이트: {dashboardData?.last_updated ? 
            new Date(dashboardData.last_updated).toLocaleString() : 'N/A'}
        </AlertDescription>
      </Alert>

      {/* 주요 메트릭 카드 */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">전체 모델 수</CardTitle>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.learning_summary.total_models}</div>
              <div className="text-xs text-muted-foreground mt-1">
                활성 모델: {Object.values(dashboardData.models_status.models).filter(m => m.status === 'active').length}개
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">전체 예측 수</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.models_status.total_predictions}</div>
              <div className="text-xs text-muted-foreground mt-1">
                최근 24시간: {recentPredictions.length}개
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">전체 정확도</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{(dashboardData.accuracy_summary.overall_accuracy * 100).toFixed(1)}%</div>
              <Progress value={dashboardData.accuracy_summary.overall_accuracy * 100} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">인사이트 수</CardTitle>
              <Lightbulb className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.insights_summary.total_insights}</div>
              <div className="text-xs text-muted-foreground mt-1">
                고신뢰도: {dashboardData.insights_summary.high_confidence_insights}개
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 예측 실행 버튼 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5" />
            예측 실행
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Button onClick={predictSalesAdvanced} variant="outline">
              <TrendingUp className="w-4 h-4 mr-2" />
              매출 예측 (7일)
            </Button>
            <Button onClick={predictInventoryAdvanced} variant="outline">
              <Package className="w-4 h-4 mr-2" />
              재고 예측
            </Button>
            <Button onClick={predictStaffingAdvanced} variant="outline">
              <Users className="w-4 h-4 mr-2" />
              인력 예측 (1주 후)
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 상세 분석 탭 */}
      <Tabs defaultValue="models" className="w-full">
        <TabsList>
          <TabsTrigger value="models">모델 관리</TabsTrigger>
          <TabsTrigger value="predictions">예측 결과</TabsTrigger>
          <TabsTrigger value="learning">자동 학습</TabsTrigger>
          <TabsTrigger value="insights">인사이트</TabsTrigger>
        </TabsList>

        <TabsContent value="models" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                모델 상태
              </CardTitle>
            </CardHeader>
            <CardContent>
              {dashboardData && (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>모델</TableHead>
                      <TableHead>버전</TableHead>
                      <TableHead>상태</TableHead>
                      <TableHead>정확도</TableHead>
                      <TableHead>마지막 학습</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {Object.entries(dashboardData.models_status.models).map(([key, model]) => (
                      <TableRow key={key}>
                        <TableCell className="font-medium">{model.type}</TableCell>
                        <TableCell>{model.version}</TableCell>
                        <TableCell>
                          <Badge variant={model.status === 'active' ? 'default' : 'secondary'}>
                            {model.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Progress value={model.accuracy * 100} className="w-20" />
                            <span className="text-sm">{(model.accuracy * 100).toFixed(1)}%</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          {new Date(model.last_trained).toLocaleDateString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="predictions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                최근 예측 결과
              </CardTitle>
            </CardHeader>
            <CardContent>
              {recentPredictions.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>시간</TableHead>
                      <TableHead>예측 유형</TableHead>
                      <TableHead>예측값</TableHead>
                      <TableHead>신뢰도</TableHead>
                      <TableHead>모델</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {recentPredictions.slice(0, 10).map((prediction, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          {new Date(prediction.timestamp).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getPredictionTypeIcon(prediction.prediction_type)}
                            <Badge variant="outline">{prediction.prediction_type}</Badge>
                          </div>
                        </TableCell>
                        <TableCell className="font-bold">
                          {formatValue(prediction.predicted_value, prediction.prediction_type)}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Progress value={prediction.confidence * 100} className="w-20" />
                            <span className="text-sm">{(prediction.confidence * 100).toFixed(0)}%</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary">{prediction.model_type}</Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  예측 결과가 없습니다. 예측을 실행해보세요.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="learning" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5" />
                자동 학습 이력
              </CardTitle>
            </CardHeader>
            <CardContent>
              {autoLearningHistory.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>시간</TableHead>
                      <TableHead>모델</TableHead>
                      <TableHead>동작</TableHead>
                      <TableHead>성능 변화</TableHead>
                      <TableHead>개선도</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {autoLearningHistory.slice(0, 10).map((history) => (
                      <TableRow key={history.id}>
                        <TableCell>
                          {new Date(history.timestamp).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{history.model_type}</Badge>
                        </TableCell>
                        <TableCell>{history.action}</TableCell>
                        <TableCell>
                          <div className="text-sm">
                            {history.performance_before.toFixed(3)} → {history.performance_after.toFixed(3)}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {history.improvement > 0 ? (
                              <TrendingUp className="w-4 h-4 text-green-500" />
                            ) : (
                              <TrendingDown className="w-4 h-4 text-red-500" />
                            )}
                            <Badge variant={history.improvement > 0 ? 'default' : 'destructive'}>
                              {history.improvement > 0 ? '+' : ''}{history.improvement.toFixed(3)}
                            </Badge>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  자동 학습 이력이 없습니다.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="w-5 h-5" />
                AI 인사이트
              </CardTitle>
            </CardHeader>
            <CardContent>
              {insights.length > 0 ? (
                <div className="space-y-4">
                  {insights.slice(0, 5).map((insight) => (
                    <div key={insight.id} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          {getInsightTypeIcon(insight.insight_type)}
                          <h4 className="font-semibold">{insight.title}</h4>
                          <Badge variant="outline">{insight.insight_type}</Badge>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {new Date(insight.timestamp).toLocaleString()}
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground mt-2">
                        {insight.description}
                      </p>
                      <div className="flex items-center gap-4 mt-3">
                        <div className="flex items-center gap-2">
                          <span className="text-sm">신뢰도:</span>
                          <Progress value={insight.confidence * 100} className="w-20" />
                          <span className="text-sm">{(insight.confidence * 100).toFixed(0)}%</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm">영향도:</span>
                          <Progress value={insight.impact_score * 100} className="w-20" />
                          <span className="text-sm">{(insight.impact_score * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                      {insight.recommendations.length > 0 && (
                        <div className="mt-3">
                          <div className="text-sm font-medium mb-1">권장사항:</div>
                          <ul className="text-sm text-muted-foreground space-y-1">
                            {insight.recommendations.map((rec, index) => (
                              <li key={index} className="flex items-center gap-2">
                                <CheckCircle className="w-3 h-3 text-green-500" />
                                {rec}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  AI 인사이트가 없습니다.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdvancedAIPrediction; 