import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Switch } from './ui/switch';
import { Textarea } from './ui/textarea';
import { 
  Bell, 
  Settings, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Info,
  Zap,
  Mail,
  MessageSquare,
  Smartphone,
  Activity,
  BarChart3,
  Clock,
  Users
} from 'lucide-react';
import { toast } from 'sonner';
import { saveAs } from 'file-saver';

interface AlertData {
  id: string;
  rule_id: string;
  plugin_id?: string;
  plugin_name?: string;
  severity: 'info' | 'warning' | 'error' | 'critical' | 'emergency';
  message: string;
  details: any;
  timestamp: string;
  channels: string[];
  acknowledged: boolean;
  acknowledged_by?: string;
  acknowledged_at?: string;
  resolved: boolean;
  resolved_at?: string;
}

interface AlertRule {
  id: string;
  name: string;
  description: string;
  plugin_id?: string;
  metric: string;
  operator: string;
  threshold: number;
  severity: string;
  channels: string[];
  cooldown_minutes: number;
  enabled: boolean;
  created_at: string;
}

interface ChannelConfig {
  enabled: boolean;
  configured: boolean;
  [key: string]: any;
}

interface SystemStatus {
  monitoring_active: boolean;
  active_alerts_count: number;
  total_alerts_24h: number;
  alert_rules_count: number;
  channels_configured: Record<string, boolean>;
}

interface AlertStatistics {
  total_alerts_24h: number;
  active_alerts: number;
  severity_distribution: Record<string, number>;
  plugin_distribution: Record<string, any>;
  hourly_distribution: Record<string, number>;
}

const severityColors = {
  info: 'bg-blue-100 text-blue-800 border-blue-200',
  warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  error: 'bg-red-100 text-red-800 border-red-200',
  critical: 'bg-orange-100 text-orange-800 border-orange-200',
  emergency: 'bg-red-100 text-red-800 border-red-200'
};

const severityIcons = {
  info: Info,
  warning: AlertTriangle,
  error: XCircle,
  critical: Zap,
  emergency: Zap
};

// CSV 변환 및 다운로드 함수 (초보자용 설명)
function exportAlertsToCSV(alerts: AlertData[], filename: string) {
  // 1. CSV 헤더 정의
  const headers = [
    'ID', '플러그인', '메시지', '심각도', '채널', '발생시각', '승인', '해결'
  ];
  // 2. 데이터 행 변환
  const rows = alerts.map(alert => [
    alert.id,
    alert.plugin_name || '시스템',
    alert.message.replace(/\n/g, ' '),
    alert.severity,
    alert.channels.join(','),
    alert.timestamp,
    alert.acknowledged ? 'O' : '',
    alert.resolved ? 'O' : ''
  ]);
  // 3. CSV 문자열 생성
  const csv = [headers, ...rows].map(row => row.map(field => `"${String(field).replace(/"/g, '""')}"`).join(',')).join('\n');
  // 4. Blob으로 변환 후 다운로드
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  saveAs(blob, filename);
}

export const EnhancedAlertSystem: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [activeAlerts, setActiveAlerts] = useState<AlertData[]>([]);
  const [alertHistory, setAlertHistory] = useState<AlertData[]>([]);
  const [alertRules, setAlertRules] = useState<AlertRule[]>([]);
  const [channelConfigs, setChannelConfigs] = useState<Record<string, ChannelConfig>>({});
  const [statistics, setStatistics] = useState<AlertStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState('overview');

  // 실시간 업데이트를 위한 WebSocket 연결
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8765');
    
    ws.onopen = () => {
      console.log('WebSocket 연결됨');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'alert') {
          // 새로운 알림이 오면 활성 알림 목록 업데이트
          fetchActiveAlerts();
          toast(data.data.message, {
            description: `${data.data.plugin_name} - ${data.data.severity}`,
            action: {
              label: '확인',
              onClick: () => setSelectedTab('alerts')
            }
          });
        }
      } catch (error) {
        console.error('WebSocket 메시지 파싱 오류:', error);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket 오류:', error);
    };
    
    return () => {
      ws.close();
    };
  }, []);

  // 초기 데이터 로드
  useEffect(() => {
    loadAllData();
    const interval = setInterval(loadAllData, 30000); // 30초마다 업데이트
    return () => clearInterval(interval);
  }, []);

  const loadAllData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchSystemStatus(),
        fetchActiveAlerts(),
        fetchAlertHistory(),
        fetchAlertRules(),
        fetchChannelConfigs(),
        fetchStatistics()
      ]);
    } catch (error) {
      console.error('데이터 로드 오류:', error);
      toast.error('데이터 로드 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const fetchSystemStatus = async () => {
    const response = await fetch('/api/enhanced-alerts/status');
    const data = await response.json();
    if (data.success) {
      setSystemStatus(data.data);
    }
  };

  const fetchActiveAlerts = async () => {
    const response = await fetch('/api/enhanced-alerts/alerts/active');
    const data = await response.json();
    if (data.success) {
      setActiveAlerts(data.data);
    }
  };

  const fetchAlertHistory = async () => {
    const response = await fetch('/api/enhanced-alerts/alerts/history?hours=24');
    const data = await response.json();
    if (data.success) {
      setAlertHistory(data.data);
    }
  };

  const fetchAlertRules = async () => {
    const response = await fetch('/api/enhanced-alerts/rules');
    const data = await response.json();
    if (data.success) {
      setAlertRules(data.data);
    }
  };

  const fetchChannelConfigs = async () => {
    const response = await fetch('/api/enhanced-alerts/channels/config');
    const data = await response.json();
    if (data.success) {
      setChannelConfigs(data.data);
    }
  };

  const fetchStatistics = async () => {
    const response = await fetch('/api/enhanced-alerts/statistics');
    const data = await response.json();
    if (data.success) {
      setStatistics(data.data);
    }
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      const response = await fetch(`/api/enhanced-alerts/alerts/${alertId}/acknowledge`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        toast.success('알림이 승인되었습니다.');
        fetchActiveAlerts();
      }
    } catch (error) {
      toast.error('알림 승인 중 오류가 발생했습니다.');
    }
  };

  const resolveAlert = async (alertId: string) => {
    try {
      const response = await fetch(`/api/enhanced-alerts/alerts/${alertId}/resolve`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        toast.success('알림이 해결되었습니다.');
        fetchActiveAlerts();
      }
    } catch (error) {
      toast.error('알림 해결 중 오류가 발생했습니다.');
    }
  };

  const testChannel = async (channelName: string) => {
    try {
      const response = await fetch(`/api/enhanced-alerts/test/${channelName}`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        toast.success(`${channelName} 채널 테스트가 완료되었습니다.`);
      }
    } catch (error) {
      toast.error('채널 테스트 중 오류가 발생했습니다.');
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('ko-KR');
  };

  const getSeverityIcon = (severity: string) => {
    const Icon = severityIcons[severity as keyof typeof severityIcons] || Info;
    return <Icon className="w-4 h-4" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">고도화된 알림 시스템</h1>
          <p className="text-muted-foreground">
            실시간 플러그인 모니터링 및 알림 관리
          </p>
        </div>
        <Button onClick={loadAllData} variant="outline">
          <Activity className="w-4 h-4 mr-2" />
          새로고침
        </Button>
      </div>

      {/* 시스템 상태 카드 */}
      {systemStatus && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">모니터링 상태</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {systemStatus.monitoring_active ? '활성' : '비활성'}
              </div>
              <p className="text-xs text-muted-foreground">
                실시간 모니터링
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">활성 알림</CardTitle>
              <Bell className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{systemStatus.active_alerts_count}</div>
              <p className="text-xs text-muted-foreground">
                현재 활성 알림
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">24시간 알림</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{systemStatus.total_alerts_24h}</div>
              <p className="text-xs text-muted-foreground">
                최근 24시간
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">알림 규칙</CardTitle>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{systemStatus.alert_rules_count}</div>
              <p className="text-xs text-muted-foreground">
                설정된 규칙
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 메인 탭 */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="alerts">알림</TabsTrigger>
          <TabsTrigger value="rules">규칙</TabsTrigger>
          <TabsTrigger value="channels">채널</TabsTrigger>
          <TabsTrigger value="statistics">통계</TabsTrigger>
        </TabsList>

        {/* 개요 탭 */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 최근 알림 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Bell className="w-5 h-5 mr-2" />
                  최근 알림
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {activeAlerts.slice(0, 5).map((alert) => (
                    <Alert key={alert.id} className={severityColors[alert.severity as keyof typeof severityColors]}>
                      <div className="flex items-center justify-between w-full">
                        <div className="flex items-center space-x-2">
                          {getSeverityIcon(alert.severity)}
                          <AlertTitle className="text-sm">{alert.plugin_name}</AlertTitle>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {alert.severity}
                        </Badge>
                      </div>
                      <AlertDescription className="text-sm mt-1">
                        {alert.message}
                      </AlertDescription>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-muted-foreground">
                          {formatTimestamp(alert.timestamp)}
                        </span>
                        <div className="space-x-2">
                          {!alert.acknowledged && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => acknowledgeAlert(alert.id)}
                            >
                              승인
                            </Button>
                          )}
                          {!alert.resolved && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => resolveAlert(alert.id)}
                            >
                              해결
                            </Button>
                          )}
                        </div>
                      </div>
                    </Alert>
                  ))}
                  {activeAlerts.length === 0 && (
                    <div className="text-center text-muted-foreground py-8">
                      활성 알림이 없습니다.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* 채널 상태 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Settings className="w-5 h-5 mr-2" />
                  알림 채널 상태
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(channelConfigs).map(([channel, config]) => (
                    <div key={channel} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        {channel === 'email' && <Mail className="w-4 h-4" />}
                        {channel === 'slack' && <MessageSquare className="w-4 h-4" />}
                        {channel === 'telegram' && <MessageSquare className="w-4 h-4" />}
                        {channel === 'sms' && <Smartphone className="w-4 h-4" />}
                        {channel === 'web' && <Activity className="w-4 h-4" />}
                        <span className="font-medium capitalize">{channel}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant={config.enabled ? "default" : "secondary"}>
                          {config.enabled ? '활성' : '비활성'}
                        </Badge>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => testChannel(channel)}
                          disabled={!config.enabled}
                        >
                          테스트
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 알림 탭 */}
        <TabsContent value="alerts" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">활성 알림</h2>
            <Button variant="outline" onClick={() => exportAlertsToCSV(activeAlerts, 'active_alerts.csv')}>
              엑셀/CSV 다운로드
            </Button>
            <Button variant="outline" onClick={fetchActiveAlerts}>
              새로고침
            </Button>
          </div>

          <div className="space-y-3">
            {activeAlerts.map((alert) => (
              <Alert key={alert.id} className={severityColors[alert.severity as keyof typeof severityColors]}>
                <div className="flex items-center justify-between w-full">
                  <div className="flex items-center space-x-3">
                    {getSeverityIcon(alert.severity)}
                    <div>
                      <AlertTitle>{alert.plugin_name || '시스템'}</AlertTitle>
                      <AlertDescription>{alert.message}</AlertDescription>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant="outline">{alert.severity}</Badge>
                    <span className="text-sm text-muted-foreground">
                      {formatTimestamp(alert.timestamp)}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between mt-4">
                  <div className="text-sm text-muted-foreground">
                    채널: {alert.channels.join(', ')}
                  </div>
                  <div className="space-x-2">
                    {!alert.acknowledged && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => acknowledgeAlert(alert.id)}
                      >
                        승인
                      </Button>
                    )}
                    {!alert.resolved && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => resolveAlert(alert.id)}
                      >
                        해결
                      </Button>
                    )}
                  </div>
                </div>
              </Alert>
            ))}
            {activeAlerts.length === 0 && (
              <div className="text-center text-muted-foreground py-8">
                활성 알림이 없습니다.
              </div>
            )}
          </div>
        </TabsContent>

        {/* 규칙 탭 */}
        <TabsContent value="rules" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">알림 규칙</h2>
            <Button onClick={() => setSelectedTab('rules')}>
              <Settings className="w-4 h-4 mr-2" />
              규칙 관리
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {alertRules.map((rule) => (
              <Card key={rule.id}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="text-sm">{rule.name}</span>
                    <Badge variant={rule.enabled ? "default" : "secondary"}>
                      {rule.enabled ? '활성' : '비활성'}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">
                    {rule.description}
                  </p>
                  <div className="space-y-2 text-sm">
                    <div>메트릭: {rule.metric}</div>
                    <div>조건: {rule.operator} {rule.threshold}</div>
                    <div>심각도: {rule.severity}</div>
                    <div>쿨다운: {rule.cooldown_minutes}분</div>
                    <div>채널: {rule.channels.join(', ')}</div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* 채널 탭 */}
        <TabsContent value="channels" className="space-y-4">
          <h2 className="text-xl font-semibold">알림 채널 설정</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {Object.entries(channelConfigs).map(([channel, config]) => (
              <Card key={channel}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {channel === 'email' && <Mail className="w-5 h-5" />}
                      {channel === 'slack' && <MessageSquare className="w-5 h-5" />}
                      {channel === 'telegram' && <MessageSquare className="w-5 h-5" />}
                      {channel === 'sms' && <Smartphone className="w-5 h-5" />}
                      {channel === 'web' && <Activity className="w-5 h-5" />}
                      <span className="capitalize">{channel}</span>
                    </div>
                    <Switch checked={config.enabled} />
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">상태</span>
                      <Badge variant={config.enabled ? "default" : "secondary"}>
                        {config.enabled ? '활성' : '비활성'}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">설정</span>
                      <Badge variant={config.configured ? "default" : "destructive"}>
                        {config.configured ? '완료' : '미설정'}
                      </Badge>
                    </div>
                    <Button
                      variant="outline"
                      onClick={() => testChannel(channel)}
                      disabled={!config.enabled}
                      className="w-full"
                    >
                      채널 테스트
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* 통계 탭 */}
        <TabsContent value="statistics" className="space-y-4">
          <h2 className="text-xl font-semibold">알림 통계</h2>
          
          {statistics && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* 심각도별 분포 */}
              <Card>
                <CardHeader>
                  <CardTitle>심각도별 분포 (24시간)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {Object.entries(statistics.severity_distribution).map(([severity, count]) => (
                      <div key={severity} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          {getSeverityIcon(severity)}
                          <span className="capitalize">{severity}</span>
                        </div>
                        <Badge variant="outline">{count}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* 플러그인별 분포 */}
              <Card>
                <CardHeader>
                  <CardTitle>플러그인별 분포 (24시간)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {Object.entries(statistics.plugin_distribution)
                      .sort(([,a], [,b]) => b.total_alerts - a.total_alerts)
                      .slice(0, 5)
                      .map(([pluginId, data]) => (
                        <div key={pluginId} className="flex items-center justify-between">
                          <span className="text-sm">{data.name}</span>
                          <Badge variant="outline">{data.total_alerts}</Badge>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default EnhancedAlertSystem; 