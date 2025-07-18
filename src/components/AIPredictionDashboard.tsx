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
  Cell,
  AreaChart,
  Area,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
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
  Clock,
  Activity,
  Server,
  Heart,
  Zap,
  Shield,
  Settings,
  BarChart3,
  Gauge,
  Thermometer
} from 'lucide-react';
import { toast } from 'sonner';

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

interface SystemHealth {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_latency: number;
  error_rate: number;
  status: string;
  last_check: string;
}

interface SatisfactionMetrics {
  employee_satisfaction: number;
  customer_satisfaction: number;
  health_score: number;
  stress_level: number;
  teamwork_score: number;
  trend: string;
  recommendations: string[];
}

interface DeploymentStatus {
  environment: string;
  status: string;
  last_deployment: string;
  deployment_time: number;
  success_rate: number;
  health_status: string;
  alerts: string[];
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#FF6B6B', '#4ECDC4', '#45B7D1'];

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
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [satisfactionMetrics, setSatisfactionMetrics] = useState<SatisfactionMetrics | null>(null);
  const [deploymentStatus, setDeploymentStatus] = useState<DeploymentStatus[]>([]);
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
      
      // 시스템 건강 상태
      const healthResponse = await fetch('/api/system/health');
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        setSystemHealth(healthData);
      }
      
      // 만족도 메트릭
      const satisfactionResponse = await fetch('/api/satisfaction/ai-analysis');
      if (satisfactionResponse.ok) {
        const satisfactionData = await satisfactionResponse.json();
        setSatisfactionMetrics(satisfactionData);
      }
      
      // 배포 상태
      const deploymentResponse = await fetch('/api/deployment/status');
      if (deploymentResponse.ok) {
        const deploymentData = await deploymentResponse.json();
        setDeploymentStatus(deploymentData.environments);
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

  // 시스템 복구 실행
  const executeSystemRecovery = async (recoveryType: string) => {
    try {
      const response = await fetch('/api/system/recovery', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ recovery_type: recoveryType }),
      });
      
      if (response.ok) {
        toast.success(`${recoveryType} 복구가 실행되었습니다.`);
        await loadPredictionData();
      } else {
        toast.error('시스템 복구에 실패했습니다.');
      }
    } catch (error) {
      console.error('시스템 복구 실패:', error);
      toast.error('시스템 복구 중 오류가 발생했습니다.');
    }
  };

  // 배포 롤백
  const rollbackDeployment = async (environment: string) => {
    try {
      const response = await fetch('/api/deployment/rollback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ environment }),
      });
      
      if (response.ok) {
        toast.success(`${environment} 환경 롤백이 완료되었습니다.`);
        await loadPredictionData();
      } else {
        toast.error('배포 롤백에 실패했습니다.');
      }
    } catch (error) {
      console.error('배포 롤백 실패:', error);
      toast.error('배포 롤백 중 오류가 발생했습니다.');
    }
  };

  // 초기 로드 및 주기적 업데이트
  useEffect(() => {
    loadPredictionData();
    
    // 2분마다 자동 새로고침 (더 빠른 업데이트)
    const interval = setInterval(loadPredictionData, 2 * 60 * 1000);
    
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
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  // 심각도별 색상
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'border-red-500 bg-red-50';
      case 'high': return 'border-orange-500 bg-orange-50';
      case 'medium': return 'border-yellow-500 bg-yellow-50';
      case 'low': return 'border-green-500 bg-green-50';
      default: return 'border-gray-500 bg-gray-50';
    }
  };

  // 시스템 상태 색상
  const getSystemStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  // 배포 상태 색상
  const getDeploymentStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-600';
      case 'in_progress': return 'text-blue-600';
      case 'failed': return 'text-red-600';
      case 'rollback': return 'text-orange-600';
      default: return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI 예측 대시보드</h1>
          <p className="text-gray-600">실시간 AI 분석 및 예측 모니터링</p>
        </div>
        <Button 
          onClick={() => loadPredictionData()} 
          disabled={refreshing}
          className="flex items-center gap-2"
        >
          <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          새로고침
        </Button>
      </div>

      {/* 시스템 상태 요약 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">시스템 상태</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {systemHealth ? (
                <span className={getSystemStatusColor(systemHealth.status)}>
                  {systemHealth.status.toUpperCase()}
                </span>
              ) : (
                'N/A'
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              CPU: {systemHealth?.cpu_usage?.toFixed(1)}% | 
              메모리: {systemHealth?.memory_usage?.toFixed(1)}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">만족도</CardTitle>
            <Heart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {satisfactionMetrics ? (
                <span className={satisfactionMetrics.trend === 'improving' ? 'text-green-600' : 'text-red-600'}>
                  {satisfactionMetrics.employee_satisfaction?.toFixed(1)}%
                </span>
              ) : (
                'N/A'
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              {satisfactionMetrics?.trend === 'improving' ? '향상 중' : '하락 중'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">배포 상태</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {deploymentStatus.length > 0 ? (
                <span className={getDeploymentStatusColor(deploymentStatus[0]?.status)}>
                  {deploymentStatus[0]?.status?.toUpperCase()}
                </span>
              ) : (
                'N/A'
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              {deploymentStatus.length}개 환경 모니터링 중
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI 모델 성능</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.keys(modelPerformance).length > 0 ? (
                <span className="text-blue-600">
                  {Object.values(modelPerformance)[0]?.accuracy?.toFixed(1)}%
                </span>
              ) : (
                'N/A'
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              평균 정확도
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 탭 네비게이션 */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="predictions">예측</TabsTrigger>
          <TabsTrigger value="system">시스템</TabsTrigger>
          <TabsTrigger value="satisfaction">만족도</TabsTrigger>
          <TabsTrigger value="deployment">배포</TabsTrigger>
          <TabsTrigger value="alerts">알림</TabsTrigger>
        </TabsList>

        {/* 개요 탭 */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* AI 인사이트 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  AI 인사이트
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {insights.slice(0, 5).map((insight, index) => (
                  <div key={index} className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{insight.title}</h4>
                      <Badge className={getPriorityColor(insight.priority)}>
                        {insight.priority}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{insight.description}</p>
                    {insight.trend && (
                      <div className="flex items-center gap-1 text-sm">
                        {insight.trend === 'up' ? (
                          <TrendingUp className="h-4 w-4 text-green-600" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-red-600" />
                        )}
                        <span className={insight.trend === 'up' ? 'text-green-600' : 'text-red-600'}>
                          {insight.change_percent}%
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* 시스템 건강 상태 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  시스템 건강 상태
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {systemHealth && (
                  <>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>CPU 사용률</span>
                        <span>{systemHealth.cpu_usage?.toFixed(1)}%</span>
                      </div>
                      <Progress 
                        value={systemHealth.cpu_usage} 
                        className={systemHealth.cpu_usage > 80 ? 'bg-red-100' : ''}
                      />
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>메모리 사용률</span>
                        <span>{systemHealth.memory_usage?.toFixed(1)}%</span>
                      </div>
                      <Progress 
                        value={systemHealth.memory_usage} 
                        className={systemHealth.memory_usage > 85 ? 'bg-red-100' : ''}
                      />
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>디스크 사용률</span>
                        <span>{systemHealth.disk_usage?.toFixed(1)}%</span>
                      </div>
                      <Progress 
                        value={systemHealth.disk_usage} 
                        className={systemHealth.disk_usage > 90 ? 'bg-red-100' : ''}
                      />
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>오류율</span>
                        <span>{(systemHealth.error_rate * 100).toFixed(2)}%</span>
                      </div>
                      <Progress 
                        value={systemHealth.error_rate * 100} 
                        className={systemHealth.error_rate > 0.05 ? 'bg-red-100' : ''}
                      />
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 예측 탭 */}
        <TabsContent value="predictions" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 매출 예측 차트 */}
            <Card>
              <CardHeader>
                <CardTitle>매출 예측</CardTitle>
              </CardHeader>
              <CardContent>
                {predictions?.sales && (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={predictions.sales}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line 
                        type="monotone" 
                        dataKey="predicted_value" 
                        stroke="#8884d8" 
                        strokeWidth={2}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>

            {/* 재고 예측 */}
            <Card>
              <CardHeader>
                <CardTitle>재고 부족 위험</CardTitle>
              </CardHeader>
              <CardContent>
                {predictions?.inventory && (
                  <div className="space-y-3">
                    {predictions.inventory
                      .filter(item => item.risk_level === 'high' || item.risk_level === 'critical')
                      .slice(0, 5)
                      .map((item, index) => (
                        <div key={index} className="flex items-center justify-between p-3 border rounded">
                          <div>
                            <p className="font-medium">{item.item_name}</p>
                            <p className="text-sm text-gray-600">
                              {item.days_until_stockout}일 후 재고 부족
                            </p>
                          </div>
                          <Badge className={getRiskColor(item.risk_level)}>
                            {item.risk_level}
                          </Badge>
                        </div>
                      ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 시스템 탭 */}
        <TabsContent value="system" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 시스템 메트릭 차트 */}
            <Card>
              <CardHeader>
                <CardTitle>시스템 메트릭 트렌드</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={[
                    { time: '00:00', cpu: 45, memory: 60, disk: 75 },
                    { time: '04:00', cpu: 35, memory: 55, disk: 75 },
                    { time: '08:00', cpu: 65, memory: 70, disk: 76 },
                    { time: '12:00', cpu: 80, memory: 85, disk: 77 },
                    { time: '16:00', cpu: 75, memory: 80, disk: 78 },
                    { time: '20:00', cpu: 60, memory: 65, disk: 78 },
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="cpu" stackId="1" stroke="#8884d8" fill="#8884d8" />
                    <Area type="monotone" dataKey="memory" stackId="1" stroke="#82ca9d" fill="#82ca9d" />
                    <Area type="monotone" dataKey="disk" stackId="1" stroke="#ffc658" fill="#ffc658" />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* 시스템 복구 액션 */}
            <Card>
              <CardHeader>
                <CardTitle>시스템 복구 액션</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  onClick={() => executeSystemRecovery('memory_cleanup')}
                  className="w-full justify-start"
                  variant="outline"
                >
                  <Shield className="h-4 w-4 mr-2" />
                  메모리 캐시 정리
                </Button>
                <Button 
                  onClick={() => executeSystemRecovery('disk_cleanup')}
                  className="w-full justify-start"
                  variant="outline"
                >
                  <Package className="h-4 w-4 mr-2" />
                  디스크 정리
                </Button>
                <Button 
                  onClick={() => executeSystemRecovery('process_restart')}
                  className="w-full justify-start"
                  variant="outline"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  프로세스 재시작
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 만족도 탭 */}
        <TabsContent value="satisfaction" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 만족도 레이더 차트 */}
            <Card>
              <CardHeader>
                <CardTitle>만족도 분석</CardTitle>
              </CardHeader>
              <CardContent>
                {satisfactionMetrics && (
                  <ResponsiveContainer width="100%" height={300}>
                    <RadarChart data={[
                      {
                        subject: '직원 만족도',
                        A: satisfactionMetrics.employee_satisfaction,
                        B: 100,
                      },
                      {
                        subject: '고객 만족도',
                        A: satisfactionMetrics.customer_satisfaction,
                        B: 100,
                      },
                      {
                        subject: '건강 점수',
                        A: satisfactionMetrics.health_score,
                        B: 100,
                      },
                      {
                        subject: '팀워크',
                        A: satisfactionMetrics.teamwork_score,
                        B: 100,
                      },
                      {
                        subject: '스트레스 관리',
                        A: 100 - satisfactionMetrics.stress_level * 20,
                        B: 100,
                      },
                    ]}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="subject" />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} />
                      <Radar name="현재" dataKey="A" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                      <Radar name="목표" dataKey="B" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.3} />
                    </RadarChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>

            {/* 개선 권고사항 */}
            <Card>
              <CardHeader>
                <CardTitle>개선 권고사항</CardTitle>
              </CardHeader>
              <CardContent>
                {satisfactionMetrics?.recommendations && (
                  <div className="space-y-3">
                    {satisfactionMetrics.recommendations.slice(0, 5).map((rec, index) => (
                      <div key={index} className="p-3 border rounded-lg bg-blue-50">
                        <p className="text-sm font-medium">{rec}</p>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 배포 탭 */}
        <TabsContent value="deployment" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 배포 상태 */}
            <Card>
              <CardHeader>
                <CardTitle>환경별 배포 상태</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {deploymentStatus.map((env, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{env.environment}</h4>
                        <Badge className={getDeploymentStatusColor(env.status)}>
                          {env.status}
                        </Badge>
                      </div>
                      <div className="text-sm text-gray-600 space-y-1">
                        <p>마지막 배포: {env.last_deployment}</p>
                        <p>배포 시간: {env.deployment_time}초</p>
                        <p>성공률: {env.success_rate}%</p>
                        <p>상태: {env.health_status}</p>
                      </div>
                      {env.status === 'failed' && (
                        <Button 
                          onClick={() => rollbackDeployment(env.environment)}
                          size="sm"
                          variant="outline"
                          className="mt-2"
                        >
                          롤백
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* 배포 성능 차트 */}
            <Card>
              <CardHeader>
                <CardTitle>배포 성능 트렌드</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={[
                    { month: '1월', success: 95, time: 120 },
                    { month: '2월', success: 92, time: 135 },
                    { month: '3월', success: 98, time: 110 },
                    { month: '4월', success: 89, time: 150 },
                    { month: '5월', success: 96, time: 125 },
                    { month: '6월', success: 94, time: 130 },
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="success" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 알림 탭 */}
        <TabsContent value="alerts" className="space-y-4">
          <div className="space-y-4">
            {alerts.map((alert, index) => (
              <Alert key={index} className={getSeverityColor(alert.severity)}>
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>{alert.title}</AlertTitle>
                <AlertDescription>
                  {alert.description}
                  {alert.action_required && (
                    <div className="mt-2">
                      <Badge variant="destructive">액션 필요</Badge>
                    </div>
                  )}
                </AlertDescription>
              </Alert>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
} 