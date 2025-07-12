import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Activity, 
  AlertTriangle, 
  BarChart3, 
  Cpu, 
  HardDrive, 
  Memory, 
  Network, 
  Play, 
  Pause, 
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Settings,
  Lightbulb,
  Clock,
  CheckCircle,
  XCircle,
  Info
} from 'lucide-react';
import { toast } from 'sonner';

interface PerformanceMetrics {
  timestamp: string;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_io_sent: number;
  network_io_recv: number;
  active_connections: number;
  response_time: number;
  error_rate: number;
  active_requests: number;
  cache_hit_rate: number;
  database_connections: number;
  plugin_count: number;
  system_load: number;
}

interface PerformanceAlert {
  timestamp: string;
  type: string;
  severity: 'warning' | 'critical';
  message: string;
  metric_name: string;
  metric_value: number;
  threshold_value: number;
}

interface PerformancePrediction {
  id: number;
  timestamp: string;
  prediction_type: string;
  predicted_value: number;
  confidence: number;
  time_horizon: string;
  factors: any;
}

interface TuningSuggestion {
  id: number;
  timestamp: string;
  tuning_type: string;
  before_value: number;
  after_value: number;
  improvement: number;
  description: string;
  applied: boolean;
}

interface DashboardData {
  current_metrics: PerformanceMetrics;
  alerts_summary: {
    total: number;
    critical: number;
    warning: number;
  };
  predictions_summary: {
    total: number;
    cpu_predictions: number;
    memory_predictions: number;
  };
  tuning_summary: {
    total_suggestions: number;
    applied_suggestions: number;
    pending_suggestions: number;
  };
  monitoring_status: {
    active: boolean;
    last_update: string;
  };
}

const AdvancedPerformanceAnalytics: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [metricsHistory, setMetricsHistory] = useState<PerformanceMetrics[]>([]);
  const [alerts, setAlerts] = useState<PerformanceAlert[]>([]);
  const [predictions, setPredictions] = useState<PerformancePrediction[]>([]);
  const [tuningSuggestions, setTuningSuggestions] = useState<TuningSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [monitoringActive, setMonitoringActive] = useState(false);

  // 대시보드 데이터 조회
  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/advanced-performance/dashboard');
      const data = await response.json();

      if (data.success) {
        setDashboardData(data.data);
        setMonitoringActive(data.data.monitoring_status.active);
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

  // 메트릭 이력 조회
  const fetchMetricsHistory = async () => {
    try {
      const response = await fetch('/api/advanced-performance/metrics/history?hours=24');
      const data = await response.json();

      if (data.success) {
        setMetricsHistory(data.data.history);
      } else {
        toast.error('메트릭 이력 조회 실패');
      }
    } catch (error) {
      console.error('메트릭 이력 조회 오류:', error);
      toast.error('메트릭 이력 조회 중 오류가 발생했습니다');
    }
  };

  // 알림 조회
  const fetchAlerts = async () => {
    try {
      const response = await fetch('/api/advanced-performance/alerts');
      const data = await response.json();

      if (data.success) {
        setAlerts(data.data.alerts);
      } else {
        toast.error('알림 조회 실패');
      }
    } catch (error) {
      console.error('알림 조회 오류:', error);
      toast.error('알림 조회 중 오류가 발생했습니다');
    }
  };

  // 예측 조회
  const fetchPredictions = async () => {
    try {
      const response = await fetch('/api/advanced-performance/predictions');
      const data = await response.json();

      if (data.success) {
        setPredictions(data.data.predictions);
      } else {
        toast.error('예측 조회 실패');
      }
    } catch (error) {
      console.error('예측 조회 오류:', error);
      toast.error('예측 조회 중 오류가 발생했습니다');
    }
  };

  // 튜닝 제안 조회
  const fetchTuningSuggestions = async () => {
    try {
      const response = await fetch('/api/advanced-performance/tuning/suggestions');
      const data = await response.json();

      if (data.success) {
        setTuningSuggestions(data.data.suggestions);
      } else {
        toast.error('튜닝 제안 조회 실패');
      }
    } catch (error) {
      console.error('튜닝 제안 조회 오류:', error);
      toast.error('튜닝 제안 조회 중 오류가 발생했습니다');
    }
  };

  // 모니터링 시작/중지
  const toggleMonitoring = async () => {
    try {
      const action = monitoringActive ? 'stop' : 'start';
      const response = await fetch(`/api/advanced-performance/${action}`, {
        method: 'POST'
      });
      const data = await response.json();

      if (data.success) {
        setMonitoringActive(!monitoringActive);
        toast.success(`모니터링이 ${monitoringActive ? '중지' : '시작'}되었습니다`);
        fetchDashboardData();
      } else {
        toast.error(data.error);
      }
    } catch (error) {
      console.error('모니터링 토글 오류:', error);
      toast.error('모니터링 상태 변경 중 오류가 발생했습니다');
    }
  };

  // 데이터 새로고침
  const refreshData = async () => {
    setLoading(true);
    await Promise.all([
      fetchDashboardData(),
      fetchMetricsHistory(),
      fetchAlerts(),
      fetchPredictions(),
      fetchTuningSuggestions()
    ]);
    setLoading(false);
  };

  useEffect(() => {
    refreshData();
    
    // 30초마다 자동 새로고침
    const interval = setInterval(refreshData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500';
      case 'warning': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      default: return <Info className="w-4 h-4 text-gray-500" />;
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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
          <h1 className="text-3xl font-bold">고도화된 성능 분석</h1>
          <p className="text-muted-foreground">
            실시간 성능 모니터링, 예측 분석, 자동 튜닝을 통한 시스템 최적화
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={refreshData} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            새로고침
          </Button>
          <Button 
            onClick={toggleMonitoring} 
            variant={monitoringActive ? "destructive" : "default"}
          >
            {monitoringActive ? (
              <>
                <Pause className="w-4 h-4 mr-2" />
                모니터링 중지
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                모니터링 시작
              </>
            )}
          </Button>
        </div>
      </div>

      {/* 모니터링 상태 */}
      <Alert>
        <Activity className="h-4 w-4" />
        <AlertDescription>
          모니터링 상태: {monitoringActive ? '활성화' : '비활성화'} | 
          마지막 업데이트: {dashboardData?.monitoring_status.last_update ? 
            new Date(dashboardData.monitoring_status.last_update).toLocaleString() : 'N/A'}
        </AlertDescription>
      </Alert>

      {/* 주요 메트릭 카드 */}
      {dashboardData?.current_metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">CPU 사용률</CardTitle>
              <Cpu className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.current_metrics.cpu_usage.toFixed(1)}%</div>
              <Progress value={dashboardData.current_metrics.cpu_usage} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">메모리 사용률</CardTitle>
              <Memory className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.current_metrics.memory_usage.toFixed(1)}%</div>
              <Progress value={dashboardData.current_metrics.memory_usage} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">디스크 사용률</CardTitle>
              <HardDrive className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.current_metrics.disk_usage.toFixed(1)}%</div>
              <Progress value={dashboardData.current_metrics.disk_usage} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">응답 시간</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.current_metrics.response_time.toFixed(0)}ms</div>
              <div className="text-xs text-muted-foreground mt-1">
                오류율: {dashboardData.current_metrics.error_rate.toFixed(2)}%
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 상세 분석 탭 */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList>
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="alerts">알림</TabsTrigger>
          <TabsTrigger value="predictions">예측</TabsTrigger>
          <TabsTrigger value="tuning">튜닝</TabsTrigger>
          <TabsTrigger value="history">이력</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 알림 요약 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  알림 요약
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>전체 알림</span>
                    <Badge variant="secondary">{dashboardData?.alerts_summary.total || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>심각한 알림</span>
                    <Badge variant="destructive">{dashboardData?.alerts_summary.critical || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>경고 알림</span>
                    <Badge variant="outline">{dashboardData?.alerts_summary.warning || 0}</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 예측 요약 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  예측 요약
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>전체 예측</span>
                    <Badge variant="secondary">{dashboardData?.predictions_summary.total || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>CPU 예측</span>
                    <Badge variant="outline">{dashboardData?.predictions_summary.cpu_predictions || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>메모리 예측</span>
                    <Badge variant="outline">{dashboardData?.predictions_summary.memory_predictions || 0}</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 네트워크 및 시스템 정보 */}
          {dashboardData?.current_metrics && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Network className="w-5 h-5" />
                  시스템 상세 정보
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <div className="text-sm font-medium">네트워크 송신</div>
                    <div className="text-lg font-bold">
                      {formatBytes(dashboardData.current_metrics.network_io_sent)}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium">네트워크 수신</div>
                    <div className="text-lg font-bold">
                      {formatBytes(dashboardData.current_metrics.network_io_recv)}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium">활성 연결</div>
                    <div className="text-lg font-bold">
                      {dashboardData.current_metrics.active_connections}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium">시스템 로드</div>
                    <div className="text-lg font-bold">
                      {dashboardData.current_metrics.system_load.toFixed(2)}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                성능 알림
              </CardTitle>
            </CardHeader>
            <CardContent>
              {alerts.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>시간</TableHead>
                      <TableHead>유형</TableHead>
                      <TableHead>심각도</TableHead>
                      <TableHead>메시지</TableHead>
                      <TableHead>값</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {alerts.map((alert, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          {new Date(alert.timestamp).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{alert.type}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getSeverityIcon(alert.severity)}
                            <Badge className={getSeverityColor(alert.severity)}>
                              {alert.severity}
                            </Badge>
                          </div>
                        </TableCell>
                        <TableCell>{alert.message}</TableCell>
                        <TableCell>
                          {alert.metric_value.toFixed(1)} / {alert.threshold_value.toFixed(1)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  현재 활성화된 알림이 없습니다.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="predictions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                성능 예측
              </CardTitle>
            </CardHeader>
            <CardContent>
              {predictions.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>시간</TableHead>
                      <TableHead>예측 유형</TableHead>
                      <TableHead>예측값</TableHead>
                      <TableHead>신뢰도</TableHead>
                      <TableHead>시간 범위</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {predictions.map((prediction) => (
                      <TableRow key={prediction.id}>
                        <TableCell>
                          {new Date(prediction.timestamp).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{prediction.prediction_type}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="font-bold">
                            {prediction.predicted_value.toFixed(1)}
                            {prediction.prediction_type.includes('usage') ? '%' : 
                             prediction.prediction_type.includes('time') ? 'ms' : ''}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Progress value={prediction.confidence * 100} className="w-20" />
                            <span className="text-sm">{(prediction.confidence * 100).toFixed(0)}%</span>
                          </div>
                        </TableCell>
                        <TableCell>{prediction.time_horizon}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  현재 예측 데이터가 없습니다.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tuning" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="w-5 h-5" />
                튜닝 제안
              </CardTitle>
            </CardHeader>
            <CardContent>
              {tuningSuggestions.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>시간</TableHead>
                      <TableHead>튜닝 유형</TableHead>
                      <TableHead>개선 효과</TableHead>
                      <TableHead>설명</TableHead>
                      <TableHead>상태</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {tuningSuggestions.map((suggestion) => (
                      <TableRow key={suggestion.id}>
                        <TableCell>
                          {new Date(suggestion.timestamp).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{suggestion.tuning_type}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <span className="text-sm">
                              {suggestion.before_value.toFixed(1)} → {suggestion.after_value.toFixed(1)}
                            </span>
                            <Badge variant="default" className="bg-green-500">
                              +{suggestion.improvement.toFixed(1)}%
                            </Badge>
                          </div>
                        </TableCell>
                        <TableCell className="max-w-xs truncate">
                          {suggestion.description}
                        </TableCell>
                        <TableCell>
                          {suggestion.applied ? (
                            <Badge variant="default" className="bg-green-500">
                              <CheckCircle className="w-3 h-3 mr-1" />
                              적용됨
                            </Badge>
                          ) : (
                            <Badge variant="outline">
                              대기중
                            </Badge>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  현재 튜닝 제안이 없습니다.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                성능 이력 (24시간)
              </CardTitle>
            </CardHeader>
            <CardContent>
              {metricsHistory.length > 0 ? (
                <div className="space-y-4">
                  {/* CPU 사용률 트렌드 */}
                  <div>
                    <h4 className="font-medium mb-2">CPU 사용률 트렌드</h4>
                    <div className="h-32 bg-muted rounded-lg p-4">
                      <div className="flex items-end justify-between h-full">
                        {metricsHistory.slice(-12).map((metric, index) => (
                          <div
                            key={index}
                            className="bg-primary rounded-t"
                            style={{
                              width: '8px',
                              height: `${(metric.cpu_usage / 100) * 100}%`,
                              minHeight: '4px'
                            }}
                            title={`${new Date(metric.timestamp).toLocaleTimeString()}: ${metric.cpu_usage.toFixed(1)}%`}
                          />
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* 메모리 사용률 트렌드 */}
                  <div>
                    <h4 className="font-medium mb-2">메모리 사용률 트렌드</h4>
                    <div className="h-32 bg-muted rounded-lg p-4">
                      <div className="flex items-end justify-between h-full">
                        {metricsHistory.slice(-12).map((metric, index) => (
                          <div
                            key={index}
                            className="bg-blue-500 rounded-t"
                            style={{
                              width: '8px',
                              height: `${(metric.memory_usage / 100) * 100}%`,
                              minHeight: '4px'
                            }}
                            title={`${new Date(metric.timestamp).toLocaleTimeString()}: ${metric.memory_usage.toFixed(1)}%`}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  성능 이력 데이터가 없습니다.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdvancedPerformanceAnalytics; 