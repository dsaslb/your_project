import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import {
  Bell,
  Settings,
  BarChart3,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  MessageSquare,
  Mail,
  Smartphone,
  Zap,
  RefreshCw,
} from 'lucide-react';

interface AlertLog {
  id: number;
  timestamp: string;
  level: 'info' | 'warning' | 'critical';
  channel: string;
  message: string;
  recipient: string;
  status: 'sent' | 'failed' | 'pending';
  plugin_id?: string;
  metric_type?: string;
  threshold_value?: number;
  actual_value?: number;
}

interface AlertStats {
  total_alerts: number;
  level_stats: Record<string, number>;
  channel_stats: Record<string, number>;
  plugin_stats: Record<string, number>;
  hourly_stats: Array<{
    hour: string;
    count: number;
  }>;
}

interface AlertSettings {
  slack: {
    enabled: boolean;
    webhook_url: string;
  };
  email: {
    enabled: boolean;
    smtp_server: string;
    from_email: string;
    to_email: string;
  };
  sms: {
    enabled: boolean;
    provider: string;
  };
  kakao: {
    enabled: boolean;
    template_id: string;
    to_number: string;
  };
}

const AlertManagement: React.FC = () => {
  const [alertLogs, setAlertLogs] = useState<AlertLog[]>([]);
  const [alertStats, setAlertStats] = useState<AlertStats | null>(null);
  const [alertSettings, setAlertSettings] = useState<AlertSettings | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('logs');

  // API 호출 함수들
  const fetchAlertLogs = useCallback(async () => {
    try {
      const response = await fetch('/api/alerts/logs');
      const data = await response.json();
      
      if (data.success) {
        setAlertLogs(data.data.logs);
      } else {
        setError(data.error || '알림 로그 조회 실패');
      }
    } catch (err) {
      setError('알림 로그 조회 중 오류가 발생했습니다');
    }
  }, []);

  const fetchAlertStats = useCallback(async () => {
    try {
      const response = await fetch('/api/alerts/stats');
      const data = await response.json();
      
      if (data.success) {
        setAlertStats(data.data);
      } else {
        setError(data.error || '알림 통계 조회 실패');
      }
    } catch (err) {
      setError('알림 통계 조회 중 오류가 발생했습니다');
    }
  }, []);

  const fetchAlertSettings = useCallback(async () => {
    try {
      const response = await fetch('/api/alerts/settings');
      const data = await response.json();
      
      if (data.success) {
        setAlertSettings(data.data);
      } else {
        setError(data.error || '알림 설정 조회 실패');
      }
    } catch (err) {
      setError('알림 설정 조회 중 오류가 발생했습니다');
    }
  }, []);

  const testAlert = useCallback(async (channel: string, level: string) => {
    try {
      setLoading(true);
      const response = await fetch('/api/alerts/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          channel,
          level,
          message: `${channel} 채널 ${level} 레벨 테스트 알림입니다.`
        })
      });
      const data = await response.json();
      
      if (data.success) {
        alert('테스트 알림이 전송되었습니다.');
        fetchAlertLogs(); // 로그 새로고침
      } else {
        setError(data.error || '테스트 알림 전송 실패');
      }
    } catch (err) {
      setError('테스트 알림 전송 중 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  }, [fetchAlertLogs]);

  // 초기 데이터 로드
  useEffect(() => {
    fetchAlertLogs();
    fetchAlertStats();
    fetchAlertSettings();
  }, [fetchAlertLogs, fetchAlertStats, fetchAlertSettings]);

  // 실시간 갱신
  useEffect(() => {
    const interval = setInterval(() => {
      fetchAlertLogs();
      fetchAlertStats();
    }, 30000); // 30초마다 갱신
    return () => clearInterval(interval);
  }, [fetchAlertLogs, fetchAlertStats]);

  // 레벨별 색상
  const getLevelColor = (level: string) => {
    switch (level) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  // 채널별 아이콘
  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'slack':
        return <MessageSquare className="w-4 h-4" />;
      case 'email':
        return <Mail className="w-4 h-4" />;
      case 'sms':
      case 'kakao':
        return <Smartphone className="w-4 h-4" />;
      default:
        return <Bell className="w-4 h-4" />;
    }
  };

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'sent':
        return 'text-green-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-yellow-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">알림 관리 대시보드</h1>
          <p className="text-muted-foreground">
            알림 로그, 통계, 설정 관리
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={() => {
            fetchAlertLogs();
            fetchAlertStats();
            fetchAlertSettings();
          }}>
            <RefreshCw className="w-4 h-4 mr-2" />
            새로고침
          </Button>
        </div>
      </div>

      {/* 오류 메시지 */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>오류</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 메인 대시보드 */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="logs">알림 로그</TabsTrigger>
          <TabsTrigger value="stats">통계</TabsTrigger>
          <TabsTrigger value="settings">설정</TabsTrigger>
          <TabsTrigger value="test">테스트</TabsTrigger>
        </TabsList>

        {/* 알림 로그 탭 */}
        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>최근 알림 로그</CardTitle>
              <CardDescription>
                최근 7일간의 알림 전송 이력
              </CardDescription>
            </CardHeader>
            <CardContent>
              {alertLogs.length > 0 ? (
                <div className="space-y-4">
                  {alertLogs.map((log) => (
                    <div key={log.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          {getChannelIcon(log.channel)}
                          <Badge className={getLevelColor(log.level)}>
                            {log.level}
                          </Badge>
                          <span className="text-sm text-muted-foreground">
                            {new Date(log.timestamp).toLocaleString()}
                          </span>
                        </div>
                        <span className={getStatusColor(log.status)}>
                          {log.status}
                        </span>
                      </div>
                      <p className="text-sm mb-2">{log.message}</p>
                      {log.plugin_id && (
                        <p className="text-xs text-muted-foreground">
                          플러그인: {log.plugin_id}
                          {log.metric_type && ` | 메트릭: ${log.metric_type}`}
                          {log.threshold_value && ` | 임계값: ${log.threshold_value}`}
                          {log.actual_value && ` | 실제값: ${log.actual_value}`}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-muted-foreground">
                  알림 로그가 없습니다
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 통계 탭 */}
        <TabsContent value="stats" className="space-y-4">
          {alertStats && (
            <>
              {/* 요약 통계 */}
              <div className="grid gap-4 md:grid-cols-4">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">총 알림 수</CardTitle>
                    <Bell className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{alertStats.total_alerts}</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">치명적 알림</CardTitle>
                    <AlertTriangle className="h-4 w-4 text-red-500" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-red-600">
                      {alertStats.level_stats.critical || 0}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">경고 알림</CardTitle>
                    <AlertTriangle className="h-4 w-4 text-yellow-500" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-yellow-600">
                      {alertStats.level_stats.warning || 0}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">성공 전송</CardTitle>
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">
                      {alertStats.total_alerts - (alertStats.level_stats.critical || 0) - (alertStats.level_stats.warning || 0)}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* 시간대별 차트 */}
              <Card>
                <CardHeader>
                  <CardTitle>시간대별 알림 발생</CardTitle>
                  <CardDescription>
                    최근 24시간 알림 발생 추이
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={alertStats.hourly_stats}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="hour" 
                        tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                      />
                      <YAxis />
                      <Tooltip 
                        labelFormatter={(value) => new Date(value).toLocaleString()}
                      />
                      <Line type="monotone" dataKey="count" stroke="#3b82f6" />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* 채널별 통계 */}
              <div className="grid gap-4 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>채널별 알림 분포</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={200}>
                      <PieChart>
                        <Pie
                          data={Object.entries(alertStats.channel_stats).map(([channel, count]) => ({
                            name: channel,
                            value: count
                          }))}
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {Object.entries(alertStats.channel_stats).map(([channel, count], index) => (
                            <Cell key={`cell-${index}`} fill={['#0088FE', '#00C49F', '#FFBB28', '#FF8042'][index % 4]} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>플러그인별 알림 분포</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={Object.entries(alertStats.plugin_stats).map(([plugin, count]) => ({
                        plugin,
                        count
                      }))}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="plugin" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#8884d8" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>

        {/* 설정 탭 */}
        <TabsContent value="settings" className="space-y-4">
          {alertSettings && (
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Slack 설정</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Badge variant={alertSettings.slack.enabled ? 'default' : 'secondary'}>
                        {alertSettings.slack.enabled ? '활성화' : '비활성화'}
                      </Badge>
                    </div>
                    {alertSettings.slack.webhook_url && (
                      <p className="text-sm text-muted-foreground">
                        Webhook URL: {alertSettings.slack.webhook_url.substring(0, 50)}...
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>이메일 설정</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Badge variant={alertSettings.email.enabled ? 'default' : 'secondary'}>
                        {alertSettings.email.enabled ? '활성화' : '비활성화'}
                      </Badge>
                    </div>
                    {alertSettings.email.enabled && (
                      <div className="text-sm text-muted-foreground">
                        <p>SMTP: {alertSettings.email.smtp_server}</p>
                        <p>발신: {alertSettings.email.from_email}</p>
                        <p>수신: {alertSettings.email.to_email}</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>SMS 설정</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Badge variant={alertSettings.sms.enabled ? 'default' : 'secondary'}>
                        {alertSettings.sms.enabled ? '활성화' : '비활성화'}
                      </Badge>
                    </div>
                    {alertSettings.sms.enabled && (
                      <p className="text-sm text-muted-foreground">
                        제공업체: {alertSettings.sms.provider}
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>카카오톡 설정</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Badge variant={alertSettings.kakao.enabled ? 'default' : 'secondary'}>
                        {alertSettings.kakao.enabled ? '활성화' : '비활성화'}
                      </Badge>
                    </div>
                    {alertSettings.kakao.enabled && (
                      <div className="text-sm text-muted-foreground">
                        <p>템플릿 ID: {alertSettings.kakao.template_id}</p>
                        <p>수신번호: {alertSettings.kakao.to_number}</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* 테스트 탭 */}
        <TabsContent value="test" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>알림 테스트</CardTitle>
              <CardDescription>
                각 채널별로 테스트 알림을 전송할 수 있습니다
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-4">
                  <h3 className="font-semibold">Slack 테스트</h3>
                  <div className="space-y-2">
                    <Button 
                      onClick={() => testAlert('slack', 'info')}
                      disabled={loading}
                      variant="outline"
                    >
                      <MessageSquare className="w-4 h-4 mr-2" />
                      Info 레벨 테스트
                    </Button>
                    <Button 
                      onClick={() => testAlert('slack', 'warning')}
                      disabled={loading}
                      variant="outline"
                    >
                      <AlertTriangle className="w-4 h-4 mr-2" />
                      Warning 레벨 테스트
                    </Button>
                    <Button 
                      onClick={() => testAlert('slack', 'critical')}
                      disabled={loading}
                      variant="outline"
                    >
                      <XCircle className="w-4 h-4 mr-2" />
                      Critical 레벨 테스트
                    </Button>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-semibold">이메일 테스트</h3>
                  <div className="space-y-2">
                    <Button 
                      onClick={() => testAlert('email', 'warning')}
                      disabled={loading}
                      variant="outline"
                    >
                      <Mail className="w-4 h-4 mr-2" />
                      Warning 레벨 테스트
                    </Button>
                    <Button 
                      onClick={() => testAlert('email', 'critical')}
                      disabled={loading}
                      variant="outline"
                    >
                      <XCircle className="w-4 h-4 mr-2" />
                      Critical 레벨 테스트
                    </Button>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-semibold">SMS 테스트</h3>
                  <div className="space-y-2">
                    <Button 
                      onClick={() => testAlert('sms', 'critical')}
                      disabled={loading}
                      variant="outline"
                    >
                      <Smartphone className="w-4 h-4 mr-2" />
                      Critical 레벨 테스트
                    </Button>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-semibold">카카오톡 테스트</h3>
                  <div className="space-y-2">
                    <Button 
                      onClick={() => testAlert('kakao', 'critical')}
                      disabled={loading}
                      variant="outline"
                    >
                      <Zap className="w-4 h-4 mr-2" />
                      Critical 레벨 테스트
                    </Button>
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

export default AlertManagement; 