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
import { toast } from 'sonner';

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

// 샘플 데이터
const sampleSystemStats: SystemStats = {
  current_cpu: 45.2,
  current_memory: 78.5,
  current_disk: 62.3,
  avg_cpu_1h: 42.1,
  avg_memory_1h: 76.8,
  avg_disk_1h: 61.9,
  uptime_hours: 168.5,
  load_average: [1.2, 1.1, 0.9],
  active_alerts: 3
};

const sampleApplicationStats: ApplicationStats = {
  current_response_time: 245,
  current_status_code: 200,
  avg_response_time_1h: 234,
  total_requests_1h: 15420,
  total_errors_1h: 23,
  error_rate_1h: 0.15,
  active_sessions: 1250,
  database_connections: 45
};

const sampleAlerts: Alert[] = [
  {
    alert_id: '1',
    rule_id: 'cpu_high',
    metric_type: 'system',
    metric_name: 'cpu_usage',
    current_value: 85.2,
    threshold: 80.0,
    severity: 'warning',
    message: 'CPU 사용률이 임계값을 초과했습니다',
    timestamp: '2024-01-15T10:30:00Z',
    status: 'active'
  },
  {
    alert_id: '2',
    rule_id: 'memory_high',
    metric_type: 'system',
    metric_name: 'memory_usage',
    current_value: 92.1,
    threshold: 90.0,
    severity: 'critical',
    message: '메모리 사용률이 임계값을 초과했습니다',
    timestamp: '2024-01-15T10:25:00Z',
    status: 'active'
  },
  {
    alert_id: '3',
    rule_id: 'disk_high',
    metric_type: 'system',
    metric_name: 'disk_usage',
    current_value: 88.7,
    threshold: 85.0,
    severity: 'warning',
    message: '디스크 사용률이 임계값을 초과했습니다',
    timestamp: '2024-01-15T10:20:00Z',
    status: 'acknowledged',
    acknowledged_by: 'admin'
  }
];

const sampleAlertRules: AlertRule[] = [
  {
    rule_id: 'cpu_high',
    name: 'CPU 사용률 높음',
    metric_type: 'system',
    metric_name: 'cpu_usage',
    operator: '>',
    threshold: 80.0,
    duration: 5,
    severity: 'warning',
    enabled: true,
    created_at: '2024-01-01T00:00:00Z'
  },
  {
    rule_id: 'memory_high',
    name: '메모리 사용률 높음',
    metric_type: 'system',
    metric_name: 'memory_usage',
    operator: '>',
    threshold: 90.0,
    duration: 3,
    severity: 'critical',
    enabled: true,
    created_at: '2024-01-01T00:00:00Z'
  },
  {
    rule_id: 'disk_high',
    name: '디스크 사용률 높음',
    metric_type: 'system',
    metric_name: 'disk_usage',
    operator: '>',
    threshold: 85.0,
    duration: 10,
    severity: 'warning',
    enabled: false,
    created_at: '2024-01-01T00:00:00Z'
  }
];

export default function MonitoringPage() {
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [applicationStats, setApplicationStats] = useState<ApplicationStats | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [alertRules, setAlertRules] = useState<AlertRule[]>([]);
  const [isMonitoringActive, setIsMonitoringActive] = useState(true);
  const [showCreateRuleDialog, setShowCreateRuleDialog] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [newRule, setNewRule] = useState({
    name: '',
    metric_type: 'system',
    metric_name: '',
    operator: '>',
    threshold: 0,
    duration: 5,
    severity: 'warning'
  });

  // 데이터 로드 함수들
  const loadSystemStats = useCallback(async () => {
    try {
      setSystemStats(sampleSystemStats);
    } catch (error) {
      toast.error('시스템 통계를 불러오는데 실패했습니다');
    }
  }, []);

  const loadApplicationStats = useCallback(async () => {
    try {
      setApplicationStats(sampleApplicationStats);
    } catch (error) {
      toast.error('애플리케이션 통계를 불러오는데 실패했습니다');
    }
  }, []);

  const loadAlerts = useCallback(async () => {
    try {
      setAlerts(sampleAlerts);
    } catch (error) {
      toast.error('알림을 불러오는데 실패했습니다');
    }
  }, []);

  const loadAlertRules = useCallback(async () => {
    try {
      setAlertRules(sampleAlertRules);
    } catch (error) {
      toast.error('알림 규칙을 불러오는데 실패했습니다');
    }
  }, []);

  // 모니터링 제어
  const handleStartMonitoring = async () => {
    setIsLoading(true);
    try {
      setIsMonitoringActive(true);
      toast.success('모니터링이 시작되었습니다');
    } catch (error) {
      toast.error('모니터링 시작에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStopMonitoring = async () => {
    setIsLoading(true);
    try {
      setIsMonitoringActive(false);
      toast.success('모니터링이 중지되었습니다');
    } catch (error) {
      toast.error('모니터링 중지에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCollectMetrics = async () => {
    setIsLoading(true);
    try {
      await loadSystemStats();
      await loadApplicationStats();
      toast.success('메트릭이 수집되었습니다');
    } catch (error) {
      toast.error('메트릭 수집에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // 알림 관리
  const handleAcknowledgeAlert = async (alertId: string) => {
    setIsLoading(true);
    try {
      setAlerts(prev => prev.map(alert => 
        alert.alert_id === alertId 
          ? { ...alert, status: 'acknowledged', acknowledged_by: 'admin' }
          : alert
      ));
      toast.success('알림이 확인되었습니다');
    } catch (error) {
      toast.error('알림 확인에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateAlertRule = async () => {
    if (!newRule.name || !newRule.metric_name) {
      toast.error('필수 필드를 입력해주세요');
      return;
    }

    setIsLoading(true);
    try {
      const rule: AlertRule = {
        rule_id: `rule_${Date.now()}`,
        name: newRule.name,
        metric_type: newRule.metric_type,
        metric_name: newRule.metric_name,
        operator: newRule.operator,
        threshold: newRule.threshold,
        duration: newRule.duration,
        severity: newRule.severity,
        enabled: true,
        created_at: new Date().toISOString()
      };
      
      setAlertRules(prev => [...prev, rule]);
      setShowCreateRuleDialog(false);
      setNewRule({
        name: '',
        metric_type: 'system',
        metric_name: '',
        operator: '>',
        threshold: 0,
        duration: 5,
        severity: 'warning'
      });
      toast.success('알림 규칙이 생성되었습니다');
    } catch (error) {
      toast.error('알림 규칙 생성에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleRule = async (ruleId: string, enabled: boolean) => {
    setIsLoading(true);
    try {
      setAlertRules(prev => prev.map(rule => 
        rule.rule_id === ruleId ? { ...rule, enabled } : rule
      ));
      toast.success(`알림 규칙이 ${enabled ? '활성화' : '비활성화'}되었습니다`);
    } catch (error) {
      toast.error('알림 규칙 상태 변경에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteRule = async (ruleId: string) => {
    setIsLoading(true);
    try {
      setAlertRules(prev => prev.filter(rule => rule.rule_id !== ruleId));
      toast.success('알림 규칙이 삭제되었습니다');
    } catch (error) {
      toast.error('알림 규칙 삭제에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // 유틸리티 함수들
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500/20 text-red-400';
      case 'warning': return 'bg-yellow-500/20 text-yellow-400';
      case 'info': return 'bg-blue-500/20 text-blue-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <XCircle className="w-4 h-4" />;
      case 'warning': return <AlertTriangle className="w-4 h-4" />;
      case 'info': return <Bell className="w-4 h-4" />;
      default: return <Minus className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-red-500/20 text-red-400';
      case 'acknowledged': return 'bg-yellow-500/20 text-yellow-400';
      case 'resolved': return 'bg-green-500/20 text-green-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const formatUptime = (hours: number) => {
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;
    return `${days}일 ${remainingHours}시간`;
  };

  const formatBytes = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  // 초기 데이터 로드
  useEffect(() => {
    const loadAllData = async () => {
      await loadSystemStats();
      await loadApplicationStats();
      await loadAlerts();
      await loadAlertRules();
    };
    loadAllData();
  }, [loadSystemStats, loadApplicationStats, loadAlerts, loadAlertRules]);

  return (
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Activity className="w-8 h-8 text-green-400" />
          시스템 모니터링
        </h1>
        <p className="text-gray-300 mt-2">시스템 및 애플리케이션 상태를 실시간으로 모니터링합니다</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-3 mb-6">
        {isMonitoringActive ? (
          <Button 
            onClick={handleStopMonitoring}
            className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
          >
            <Square className="w-4 h-4 mr-2" />
            모니터링 중지
          </Button>
        ) : (
          <Button 
            onClick={handleStartMonitoring}
            className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
          >
            <Play className="w-4 h-4 mr-2" />
            모니터링 시작
          </Button>
        )}
        <Button 
          onClick={handleCollectMetrics}
          variant="outline"
          className="border-white/20 text-white hover:bg-white/10"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          메트릭 수집
        </Button>
        <Button 
          onClick={() => setShowCreateRuleDialog(true)}
          variant="outline"
          className="border-white/20 text-white hover:bg-white/10"
        >
          <Settings className="w-4 h-4 mr-2" />
          알림 규칙 생성
        </Button>
      </div>

      {/* 시스템 통계 */}
      {systemStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">CPU 사용률</CardTitle>
              <Cpu className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{systemStats.current_cpu.toFixed(1)}%</div>
              <Progress value={systemStats.current_cpu} className="mt-2" />
              <p className="text-xs text-gray-300 mt-1">1시간 평균: {systemStats.avg_cpu_1h.toFixed(1)}%</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">메모리 사용률</CardTitle>
              <HardDrive className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{systemStats.current_memory.toFixed(1)}%</div>
              <Progress value={systemStats.current_memory} className="mt-2" />
              <p className="text-xs text-gray-300 mt-1">1시간 평균: {systemStats.avg_memory_1h.toFixed(1)}%</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">디스크 사용률</CardTitle>
              <Database className="h-4 w-4 text-orange-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{systemStats.current_disk.toFixed(1)}%</div>
              <Progress value={systemStats.current_disk} className="mt-2" />
              <p className="text-xs text-gray-300 mt-1">1시간 평균: {systemStats.avg_disk_1h.toFixed(1)}%</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">가동 시간</CardTitle>
              <Clock className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{formatUptime(systemStats.uptime_hours)}</div>
              <p className="text-xs text-gray-300">부하: {systemStats.load_average.join(', ')}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 애플리케이션 통계 */}
      {applicationStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">응답 시간</CardTitle>
              <Network className="h-4 w-4 text-cyan-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{applicationStats.current_response_time}ms</div>
              <p className="text-xs text-gray-300">1시간 평균: {applicationStats.avg_response_time_1h}ms</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">요청 수</CardTitle>
              <BarChart3 className="h-4 w-4 text-indigo-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{applicationStats.total_requests_1h.toLocaleString()}</div>
              <p className="text-xs text-gray-300">1시간 동안</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">오류율</CardTitle>
              <XCircle className="h-4 w-4 text-red-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{applicationStats.error_rate_1h.toFixed(2)}%</div>
              <p className="text-xs text-gray-300">오류: {applicationStats.total_errors_1h}개</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">활성 세션</CardTitle>
              <Users className="h-4 w-4 text-pink-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{applicationStats.active_sessions.toLocaleString()}</div>
              <p className="text-xs text-gray-300">DB 연결: {applicationStats.database_connections}개</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 메인 탭 */}
      <Tabs defaultValue="alerts" className="space-y-4">
        <TabsList className="bg-white/10 border border-white/20">
          <TabsTrigger value="alerts" className="text-white data-[state=active]:bg-white/20">알림</TabsTrigger>
          <TabsTrigger value="rules" className="text-white data-[state=active]:bg-white/20">알림 규칙</TabsTrigger>
        </TabsList>

        {/* 알림 탭 */}
        <TabsContent value="alerts" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <CardTitle className="text-white">활성 알림</CardTitle>
              <CardDescription className="text-gray-300">시스템에서 발생한 알림을 확인합니다</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {alerts.map((alert) => (
                  <div key={alert.alert_id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-medium text-white">{alert.message}</h3>
                          <Badge className={getSeverityColor(alert.severity)}>
                            {getSeverityIcon(alert.severity)}
                            <span className="ml-1">{alert.severity}</span>
                          </Badge>
                          <Badge className={getStatusColor(alert.status)}>
                            {alert.status === 'active' ? '활성' : 
                             alert.status === 'acknowledged' ? '확인됨' : '해결됨'}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-300 space-y-1">
                          <div>메트릭: {alert.metric_name} ({alert.current_value} / {alert.threshold})</div>
                          <div>발생 시간: {new Date(alert.timestamp).toLocaleString('ko-KR')}</div>
                          {alert.acknowledged_by && (
                            <div>확인자: {alert.acknowledged_by}</div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {alert.status === 'active' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleAcknowledgeAlert(alert.alert_id)}
                            className="border-white/20 text-white hover:bg-white/10"
                          >
                            확인
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                
                {alerts.length === 0 && (
                  <div className="text-center py-8 text-gray-300">
                    활성 알림이 없습니다.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 알림 규칙 탭 */}
        <TabsContent value="rules" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <CardTitle className="text-white">알림 규칙</CardTitle>
              <CardDescription className="text-gray-300">시스템 모니터링 규칙을 관리합니다</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {alertRules.map((rule) => (
                  <div key={rule.rule_id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-medium text-white">{rule.name}</h3>
                          <Badge className={getSeverityColor(rule.severity)}>
                            {rule.severity}
                          </Badge>
                          <Badge className={rule.enabled ? "bg-green-500/20 text-green-400" : "bg-gray-500/20 text-gray-400"}>
                            {rule.enabled ? '활성' : '비활성'}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-300 space-y-1">
                          <div>조건: {rule.metric_name} {rule.operator} {rule.threshold}</div>
                          <div>지속 시간: {rule.duration}분</div>
                          <div>메트릭 타입: {rule.metric_type}</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={rule.enabled}
                          onCheckedChange={(enabled) => handleToggleRule(rule.rule_id, enabled)}
                        />
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleDeleteRule(rule.rule_id)}
                          className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                        >
                          <XCircle className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
                
                {alertRules.length === 0 && (
                  <div className="text-center py-8 text-gray-300">
                    알림 규칙이 없습니다.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 알림 규칙 생성 다이얼로그 */}
      <Dialog open={showCreateRuleDialog} onOpenChange={setShowCreateRuleDialog}>
        <DialogContent className="max-w-md bg-white/10 backdrop-blur-sm border border-white/20">
          <DialogHeader>
            <DialogTitle className="text-white">알림 규칙 생성</DialogTitle>
            <DialogDescription className="text-gray-300">새로운 모니터링 규칙을 생성합니다</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-300">규칙 이름</label>
              <Input
                value={newRule.name}
                onChange={(e) => setNewRule(prev => ({ ...prev, name: e.target.value }))}
                placeholder="규칙 이름을 입력하세요"
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              />
            </div>
            
            <div>
              <label className="text-sm font-medium text-gray-300">메트릭 이름</label>
              <Input
                value={newRule.metric_name}
                onChange={(e) => setNewRule(prev => ({ ...prev, metric_name: e.target.value }))}
                placeholder="cpu_usage, memory_usage 등"
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-300">임계값</label>
                <Input
                  type="number"
                  value={newRule.threshold}
                  onChange={(e) => setNewRule(prev => ({ ...prev, threshold: parseFloat(e.target.value) }))}
                  className="bg-white/10 border-white/20 text-white"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-300">지속 시간 (분)</label>
                <Input
                  type="number"
                  value={newRule.duration}
                  onChange={(e) => setNewRule(prev => ({ ...prev, duration: parseInt(e.target.value) }))}
                  className="bg-white/10 border-white/20 text-white"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button 
                onClick={handleCreateAlertRule}
                disabled={isLoading}
                className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
              >
                {isLoading ? "생성 중..." : "규칙 생성"}
              </Button>
              <Button 
                variant="outline" 
                onClick={() => setShowCreateRuleDialog(false)}
                className="border-white/20 text-white hover:bg-white/10"
              >
                취소
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
} 