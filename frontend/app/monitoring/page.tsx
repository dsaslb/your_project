'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Settings, 
  Play, 
  Square, 
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Minus,
  Database,
  Cpu,
  HardDrive,
  Network,
  Bell,
  Shield,
  Zap,
  Users,
  BarChart3
} from 'lucide-react';
import { useLoadingState } from '@/hooks/useLoadingState';
import { useErrorHandler } from '@/hooks/useErrorHandler';
import { apiClient } from '@/lib/api-client';

interface SystemStats {
  current_cpu: number;
  current_memory: number;
  current_disk: number;
  avg_cpu_1h: number;
  avg_memory_1h: number;
  avg_disk_1h: number;
  uptime_hours: number;
  load_average: [number, number, number];
  active_alerts: number;
}

interface ApplicationStats {
  current_response_time: number;
  current_status_code: number;
  avg_response_time_1h: number;
  total_requests_1h: number;
  total_errors_1h: number;
  error_rate_1h: number;
  active_sessions: number;
  database_connections: number;
}

interface Alert {
  alert_id: string;
  rule_id: string;
  metric_type: string;
  metric_name: string;
  current_value: number;
  threshold: number;
  severity: string;
  message: string;
  timestamp: string;
  status: string;
  acknowledged_by?: string;
  resolved_at?: string;
}

interface AlertRule {
  rule_id: string;
  name: string;
  metric_type: string;
  metric_name: string;
  operator: string;
  threshold: number;
  duration: number;
  severity: string;
  enabled: boolean;
  created_at?: string;
}

interface MetricHistory {
  metric_name: string;
  hours: number;
  history: Array<{
    timestamp: string;
    value: number;
  }>;
}

export default function MonitoringPage() {
  const { isLoading, error, withLoading } = useLoadingState();
  const { showError, showSuccess } = useErrorHandler();
  
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [applicationStats, setApplicationStats] = useState<ApplicationStats | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [alertRules, setAlertRules] = useState<AlertRule[]>([]);
  const [metricHistory, setMetricHistory] = useState<MetricHistory | null>(null);
  const [monitoringStatus, setMonitoringStatus] = useState<{
    is_running: boolean;
    collection_interval: number;
    retention_days: number;
    alert_enabled: boolean;
  } | null>(null);
  
  const [selectedMetric, setSelectedMetric] = useState('cpu_percent');
  const [showCreateRuleDialog, setShowCreateRuleDialog] = useState(false);
  const [showAlertDetails, setShowAlertDetails] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  
  const [newRule, setNewRule] = useState({
    name: '',
    metric_type: 'system',
    metric_name: 'cpu_percent',
    operator: '>',
    threshold: 80,
    duration: 300,
    severity: 'high'
  });

  // 데이터 로딩 함수들
  const loadSystemStats = useCallback(async () => {
    try {
      const response = await ApiClient.get('/api/monitoring/stats/system');
      if (response.status === 'success') {
        setSystemStats(response.data);
      }
    } catch (error) {
      console.error('시스템 통계 로딩 오류:', error);
    }
  }, []);

  const loadApplicationStats = useCallback(async () => {
    try {
      const response = await ApiClient.get('/api/monitoring/stats/application');
      if (response.status === 'success') {
        setApplicationStats(response.data);
      }
    } catch (error) {
      console.error('애플리케이션 통계 로딩 오류:', error);
    }
  }, []);

  const loadAlerts = useCallback(async () => {
    try {
      const response = await ApiClient.get('/api/monitoring/alerts?limit=50');
      if (response.status === 'success') {
        setAlerts(response.data);
      }
    } catch (error) {
      console.error('알림 로딩 오류:', error);
    }
  }, []);

  const loadAlertRules = useCallback(async () => {
    try {
      const response = await ApiClient.get('/api/monitoring/rules');
      if (response.status === 'success') {
        setAlertRules(response.data);
      }
    } catch (error) {
      console.error('알림 규칙 로딩 오류:', error);
    }
  }, []);

  const loadMetricHistory = useCallback(async (metric: string, hours: number = 24) => {
    try {
      const response = await ApiClient.get(`/api/monitoring/metrics/history?metric=${metric}&hours=${hours}`);
      if (response.status === 'success') {
        setMetricHistory(response.data);
      }
    } catch (error) {
      console.error('메트릭 히스토리 로딩 오류:', error);
    }
  }, []);

  const loadMonitoringStatus = useCallback(async () => {
    try {
      const response = await ApiClient.get('/api/monitoring/control/status');
      if (response.status === 'success') {
        setMonitoringStatus(response.data);
      }
    } catch (error) {
      console.error('모니터링 상태 로딩 오류:', error);
    }
  }, []);

  // 이벤트 핸들러들
  const handleStartMonitoring = async () => {
    await withLoading(async () => {
      const response = await ApiClient.post('/api/monitoring/control/start');
      if (response.status === 'success') {
        showSuccess('모니터링이 시작되었습니다');
        await loadMonitoringStatus();
      }
    });
  };

  const handleStopMonitoring = async () => {
    await withLoading(async () => {
      const response = await ApiClient.post('/api/monitoring/control/stop');
      if (response.status === 'success') {
        showSuccess('모니터링이 중지되었습니다');
        await loadMonitoringStatus();
      }
    });
  };

  const handleCollectMetrics = async () => {
    await withLoading(async () => {
      const response = await ApiClient.post('/api/monitoring/metrics/collect', {
        type: 'all'
      });
      if (response.status === 'success') {
        showSuccess('메트릭 수집이 완료되었습니다');
        await loadSystemStats();
        await loadApplicationStats();
      }
    });
  };

  const handleAcknowledgeAlert = async (alertId: string) => {
    await withLoading(async () => {
      const response = await ApiClient.post(`/api/monitoring/alerts/${alertId}/acknowledge`, {
        user: 'admin'
      });
      if (response.status === 'success') {
        showSuccess('알림이 승인되었습니다');
        await loadAlerts();
      }
    });
  };

  const handleCreateAlertRule = async () => {
    await withLoading(async () => {
      const response = await ApiClient.post('/api/monitoring/rules', newRule);
      if (response.status === 'success') {
        showSuccess('알림 규칙이 생성되었습니다');
        setShowCreateRuleDialog(false);
        setNewRule({
          name: '',
          metric_type: 'system',
          metric_name: 'cpu_percent',
          operator: '>',
          threshold: 80,
          duration: 300,
          severity: 'high'
        });
        await loadAlertRules();
      }
    });
  };

  const handleToggleRule = async (ruleId: string, enabled: boolean) => {
    await withLoading(async () => {
      const response = await ApiClient.put(`/api/monitoring/rules/${ruleId}`, {
        enabled
      });
      if (response.status === 'success') {
        showSuccess('알림 규칙이 수정되었습니다');
        await loadAlertRules();
      }
    });
  };

  const handleDeleteRule = async (ruleId: string) => {
    if (!confirm('이 알림 규칙을 삭제하시겠습니까?')) return;
    
    await withLoading(async () => {
      const response = await ApiClient.delete(`/api/monitoring/rules/${ruleId}`);
      if (response.status === 'success') {
        showSuccess('알림 규칙이 삭제되었습니다');
        await loadAlertRules();
      }
    });
  };

  // 유틸리티 함수들
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <XCircle className="w-4 h-4" />;
      case 'high': return <AlertTriangle className="w-4 h-4" />;
      case 'medium': return <AlertTriangle className="w-4 h-4" />;
      case 'low': return <Bell className="w-4 h-4" />;
      default: return <Bell className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-red-100 text-red-800';
      case 'acknowledged': return 'bg-yellow-100 text-yellow-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatUptime = (hours: number) => {
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;
    return `${days}일 ${remainingHours}시간`;
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // 초기 데이터 로딩
  useEffect(() => {
    const loadAllData = async () => {
      await Promise.all([
        loadSystemStats(),
        loadApplicationStats(),
        loadAlerts(),
        loadAlertRules(),
        loadMonitoringStatus(),
        loadMetricHistory(selectedMetric)
      ]);
    };

    loadAllData();

    // 30초마다 데이터 새로고침
    const interval = setInterval(loadAllData, 30000);
    return () => clearInterval(interval);
  }, [loadSystemStats, loadApplicationStats, loadAlerts, loadAlertRules, loadMonitoringStatus, loadMetricHistory, selectedMetric]);

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">시스템 모니터링</h1>
          <p className="text-gray-600">실시간 시스템 성능 및 상태 모니터링</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleCollectMetrics}
            disabled={isLoading}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            메트릭 수집
          </Button>
          {monitoringStatus?.is_running ? (
            <Button
              variant="destructive"
              size="sm"
              onClick={handleStopMonitoring}
              disabled={isLoading}
            >
              <Square className="w-4 h-4 mr-2" />
              모니터링 중지
            </Button>
          ) : (
            <Button
              variant="default"
              size="sm"
              onClick={handleStartMonitoring}
              disabled={isLoading}
            >
              <Play className="w-4 h-4 mr-2" />
              모니터링 시작
            </Button>
          )}
        </div>
      </div>

      {/* 모니터링 상태 */}
      {monitoringStatus && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              모니터링 상태
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${monitoringStatus.is_running ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm">
                  {monitoringStatus.is_running ? '실행 중' : '중지됨'}
                </span>
              </div>
              <div className="text-sm">
                수집 간격: {monitoringStatus.collection_interval}초
              </div>
              <div className="text-sm">
                보존 기간: {monitoringStatus.retention_days}일
              </div>
              <div className="text-sm">
                알림: {monitoringStatus.alert_enabled ? '활성화' : '비활성화'}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 시스템 통계 */}
      {systemStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">CPU 사용률</CardTitle>
              <Cpu className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{systemStats.current_cpu.toFixed(1)}%</div>
              <Progress value={systemStats.current_cpu} className="mt-2" />
              <p className="text-xs text-muted-foreground mt-2">
                1시간 평균: {systemStats.avg_cpu_1h.toFixed(1)}%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">메모리 사용률</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{systemStats.current_memory.toFixed(1)}%</div>
              <Progress value={systemStats.current_memory} className="mt-2" />
              <p className="text-xs text-muted-foreground mt-2">
                1시간 평균: {systemStats.avg_memory_1h.toFixed(1)}%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">디스크 사용률</CardTitle>
              <HardDrive className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{systemStats.current_disk.toFixed(1)}%</div>
              <Progress value={systemStats.current_disk} className="mt-2" />
              <p className="text-xs text-muted-foreground mt-2">
                1시간 평균: {systemStats.avg_disk_1h.toFixed(1)}%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">시스템 업타임</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatUptime(systemStats.uptime_hours)}</div>
              <p className="text-xs text-muted-foreground mt-2">
                로드 평균: {systemStats.load_average[0].toFixed(2)}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 애플리케이션 통계 */}
      {applicationStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">응답 시간</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{applicationStats.current_response_time.toFixed(0)}ms</div>
              <p className="text-xs text-muted-foreground mt-2">
                1시간 평균: {applicationStats.avg_response_time_1h.toFixed(0)}ms
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">요청 수</CardTitle>
              <Network className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{applicationStats.total_requests_1h}</div>
              <p className="text-xs text-muted-foreground mt-2">
                에러율: {applicationStats.error_rate_1h.toFixed(2)}%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">활성 세션</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{applicationStats.active_sessions}</div>
              <p className="text-xs text-muted-foreground mt-2">
                DB 연결: {applicationStats.database_connections}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">활성 알림</CardTitle>
              <Bell className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{systemStats?.active_alerts || 0}</div>
              <p className="text-xs text-muted-foreground mt-2">
                실시간 모니터링
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 메인 탭 */}
      <Tabs defaultValue="alerts" className="space-y-4">
        <TabsList>
          <TabsTrigger value="alerts">알림 관리</TabsTrigger>
          <TabsTrigger value="rules">알림 규칙</TabsTrigger>
          <TabsTrigger value="metrics">메트릭 히스토리</TabsTrigger>
        </TabsList>

        {/* 알림 관리 탭 */}
        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>시스템 알림</CardTitle>
              <CardDescription>
                실시간 시스템 알림 및 경고 관리
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {alerts.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
                    <p>현재 활성 알림이 없습니다</p>
                  </div>
                ) : (
                  alerts.map((alert) => (
                    <div
                      key={alert.alert_id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-full ${getSeverityColor(alert.severity)}`}>
                          {getSeverityIcon(alert.severity)}
                        </div>
                        <div>
                          <div className="font-medium">{alert.message}</div>
                          <div className="text-sm text-gray-500">
                            {new Date(alert.timestamp).toLocaleString()}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getStatusColor(alert.status)}>
                          {alert.status === 'active' ? '활성' : 
                           alert.status === 'acknowledged' ? '승인됨' : '해결됨'}
                        </Badge>
                        {alert.status === 'active' && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleAcknowledgeAlert(alert.alert_id)}
                          >
                            승인
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedAlert(alert);
                            setShowAlertDetails(true);
                          }}
                        >
                          상세
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 알림 규칙 탭 */}
        <TabsContent value="rules" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>알림 규칙</CardTitle>
                  <CardDescription>
                    시스템 알림 규칙 관리
                  </CardDescription>
                </div>
                <Button onClick={() => setShowCreateRuleDialog(true)}>
                  규칙 생성
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {alertRules.map((rule) => (
                  <div
                    key={rule.rule_id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <Switch
                        checked={rule.enabled}
                        onCheckedChange={(enabled) => handleToggleRule(rule.rule_id, enabled)}
                      />
                      <div>
                        <div className="font-medium">{rule.name}</div>
                        <div className="text-sm text-gray-500">
                          {rule.metric_type} - {rule.metric_name} {rule.operator} {rule.threshold}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getSeverityColor(rule.severity)}>
                        {rule.severity}
                      </Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteRule(rule.rule_id)}
                      >
                        삭제
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 메트릭 히스토리 탭 */}
        <TabsContent value="metrics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>메트릭 히스토리</CardTitle>
              <CardDescription>
                시스템 메트릭 변화 추이
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <select
                    value={selectedMetric}
                    onChange={(e) => setSelectedMetric(e.target.value)}
                    className="border rounded px-3 py-2"
                  >
                    <option value="cpu_percent">CPU 사용률</option>
                    <option value="memory_percent">메모리 사용률</option>
                    <option value="disk_percent">디스크 사용률</option>
                    <option value="response_time">응답 시간</option>
                  </select>
                </div>
                
                {metricHistory && (
                  <div className="h-64 bg-gray-50 rounded-lg p-4">
                    <div className="text-center text-gray-500">
                      차트 영역 (실제 구현에서는 Recharts 등 사용)
                    </div>
                    <div className="text-sm text-gray-400 mt-2">
                      {metricHistory.history.length}개 데이터 포인트
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 알림 규칙 생성 다이얼로그 */}
      <Dialog open={showCreateRuleDialog} onOpenChange={setShowCreateRuleDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>알림 규칙 생성</DialogTitle>
            <DialogDescription>
              새로운 알림 규칙을 생성합니다
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">규칙 이름</label>
              <Input
                value={newRule.name}
                onChange={(e) => setNewRule({...newRule, name: e.target.value})}
                placeholder="예: CPU 사용률 높음"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">메트릭 유형</label>
                <select
                  value={newRule.metric_type}
                  onChange={(e) => setNewRule({...newRule, metric_type: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="system">시스템</option>
                  <option value="application">애플리케이션</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">메트릭</label>
                <select
                  value={newRule.metric_name}
                  onChange={(e) => setNewRule({...newRule, metric_name: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="cpu_percent">CPU 사용률</option>
                  <option value="memory_percent">메모리 사용률</option>
                  <option value="disk_percent">디스크 사용률</option>
                  <option value="response_time">응답 시간</option>
                </select>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium">연산자</label>
                <select
                  value={newRule.operator}
                  onChange={(e) => setNewRule({...newRule, operator: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value=">">&gt;</option>
                  <option value=">=">&gt;=</option>
                  <option value="<">&lt;</option>
                  <option value="<=">&lt;=</option>
                  <option value="==">=</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">임계값</label>
                <Input
                  type="number"
                  value={newRule.threshold}
                  onChange={(e) => setNewRule({...newRule, threshold: parseFloat(e.target.value)})}
                />
              </div>
              <div>
                <label className="text-sm font-medium">심각도</label>
                <select
                  value={newRule.severity}
                  onChange={(e) => setNewRule({...newRule, severity: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="low">낮음</option>
                  <option value="medium">보통</option>
                  <option value="high">높음</option>
                  <option value="critical">치명적</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowCreateRuleDialog(false)}>
                취소
              </Button>
              <Button onClick={handleCreateAlertRule}>
                생성
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* 알림 상세 다이얼로그 */}
      <Dialog open={showAlertDetails} onOpenChange={setShowAlertDetails}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>알림 상세 정보</DialogTitle>
          </DialogHeader>
          {selectedAlert && (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">메시지</label>
                <p className="text-sm">{selectedAlert.message}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">현재 값</label>
                  <p className="text-sm">{selectedAlert.current_value}</p>
                </div>
                <div>
                  <label className="text-sm font-medium">임계값</label>
                  <p className="text-sm">{selectedAlert.threshold}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">심각도</label>
                  <Badge className={getSeverityColor(selectedAlert.severity)}>
                    {selectedAlert.severity}
                  </Badge>
                </div>
                <div>
                  <label className="text-sm font-medium">상태</label>
                  <Badge className={getStatusColor(selectedAlert.status)}>
                    {selectedAlert.status}
                  </Badge>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium">발생 시간</label>
                <p className="text-sm">{new Date(selectedAlert.timestamp).toLocaleString()}</p>
              </div>
              {selectedAlert.resolved_at && (
                <div>
                  <label className="text-sm font-medium">해결 시간</label>
                  <p className="text-sm">{new Date(selectedAlert.resolved_at).toLocaleString()}</p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
} 