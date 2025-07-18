import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Activity, 
  AlertTriangle, 
  BarChart3, 
  Cpu, 
  Database, 
  HardDrive, 
  Network, 
  Users, 
  ShoppingCart, 
  Clock,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  XCircle,
  Info
} from 'lucide-react';

interface DashboardData {
  timestamp: string;
  system_status: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    network_io: {
      bytes_sent: number;
      bytes_recv: number;
    };
    active_connections: number;
    uptime: string;
    database_status: string;
    api_response_time: number;
  };
  performance_metrics: {
    today_orders: {
      total: number;
      pending: number;
      completed: number;
      total_sales: number;
    };
    today_attendance: {
      total: number;
      on_time: number;
      late: number;
    };
    active_users: number;
    system_performance: {
      response_time: number;
      throughput: number;
      error_rate: number;
    };
  };
  active_alerts: Array<{
    type: string;
    severity: 'info' | 'warning' | 'critical';
    message: string;
    timestamp: string;
  }>;
  user_activity: {
    recent_orders: number;
    recent_logins: number;
    active_sessions: number;
    peak_hours: number[];
  };
  ai_insights: {
    recommendations: Array<{
      type: string;
      title: string;
      description: string;
      priority: string;
      action: string;
    }>;
  };
  iot_data?: {
    total_devices: number;
    online_devices: number;
    error_devices: number;
  };
  notifications: Array<{
    id: string;
    title: string;
    message: string;
    type: string;
    created_at: string;
    read: boolean;
  }>;
}

interface SystemStatusCardProps {
  title: string;
  value: number | string;
  unit?: string;
  icon: React.ReactNode;
  status?: 'good' | 'warning' | 'critical';
  trend?: 'up' | 'down' | 'stable';
}

const SystemStatusCard: React.FC<SystemStatusCardProps> = ({
  title,
  value,
  unit,
  icon,
  status = 'good',
  trend
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'good': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'down': return <TrendingDown className="w-4 h-4 text-red-600" />;
      default: return null;
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className={`${getStatusColor()}`}>
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="text-2xl font-bold">
            {typeof value === 'number' ? value.toLocaleString() : value}
            {unit && <span className="text-sm text-muted-foreground ml-1">{unit}</span>}
          </div>
          {getTrendIcon()}
        </div>
      </CardContent>
    </Card>
  );
};

interface AlertCardProps {
  alerts: Array<{
    type: string;
    severity: 'info' | 'warning' | 'critical';
    message: string;
    timestamp: string;
  }>;
}

const AlertCard: React.FC<AlertCardProps> = ({ alerts }) => {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <XCircle className="w-4 h-4 text-red-600" />;
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      case 'info': return <Info className="w-4 h-4 text-blue-600" />;
      default: return <Info className="w-4 h-4 text-gray-600" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'border-red-200 bg-red-50';
      case 'warning': return 'border-yellow-200 bg-yellow-50';
      case 'info': return 'border-blue-200 bg-blue-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5" />
          활성 알림 ({alerts.length})
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {alerts.length === 0 ? (
          <div className="text-center text-muted-foreground py-4">
            활성 알림이 없습니다.
          </div>
        ) : (
          alerts.slice(0, 5).map((alert, index) => (
            <Alert key={index} className={getSeverityColor(alert.severity)}>
              <div className="flex items-start gap-2">
                {getSeverityIcon(alert.severity)}
                <AlertDescription className="flex-1">
                  <div className="font-medium">{alert.message}</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {new Date(alert.timestamp).toLocaleString()}
                  </div>
                </AlertDescription>
              </div>
            </Alert>
          ))
        )}
      </CardContent>
    </Card>
  );
};

interface PerformanceMetricsProps {
  metrics: DashboardData['performance_metrics'];
}

const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({ metrics }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <SystemStatusCard
        title="오늘 주문"
        value={metrics.today_orders.total}
        icon={<ShoppingCart className="w-4 h-4" />}
        status={metrics.today_orders.total > 50 ? 'good' : 'warning'}
      />
      <SystemStatusCard
        title="대기 주문"
        value={metrics.today_orders.pending}
        icon={<Clock className="w-4 h-4" />}
        status={metrics.today_orders.pending > 10 ? 'critical' : 'good'}
      />
      <SystemStatusCard
        title="완료 주문"
        value={metrics.today_orders.completed}
        icon={<CheckCircle className="w-4 h-4" />}
        status="good"
      />
      <SystemStatusCard
        title="총 매출"
        value={metrics.today_orders.total_sales}
        unit="원"
        icon={<BarChart3 className="w-4 h-4" />}
        status={metrics.today_orders.total_sales > 1000000 ? 'good' : 'warning'}
      />
    </div>
  );
};

interface SystemStatusProps {
  status: DashboardData['system_status'];
}

const SystemStatus: React.FC<SystemStatusProps> = ({ status }) => {
  const getStatusColor = (value: number, thresholds: { warning: number; critical: number }) => {
    if (value >= thresholds.critical) return 'critical';
    if (value >= thresholds.warning) return 'warning';
    return 'good';
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <SystemStatusCard
        title="CPU 사용률"
        value={status.cpu_usage}
        unit="%"
        icon={<Cpu className="w-4 h-4" />}
        status={getStatusColor(status.cpu_usage, { warning: 70, critical: 90 })}
      />
      <SystemStatusCard
        title="메모리 사용률"
        value={status.memory_usage}
        unit="%"
        icon={<Database className="w-4 h-4" />}
        status={getStatusColor(status.memory_usage, { warning: 80, critical: 95 })}
      />
      <SystemStatusCard
        title="디스크 사용률"
        value={status.disk_usage}
        unit="%"
        icon={<HardDrive className="w-4 h-4" />}
        status={getStatusColor(status.disk_usage, { warning: 85, critical: 95 })}
      />
      <SystemStatusCard
        title="응답 시간"
        value={status.api_response_time}
        unit="ms"
        icon={<Activity className="w-4 h-4" />}
        status={getStatusColor(status.api_response_time, { warning: 500, critical: 1000 })}
      />
    </div>
  );
};

interface AIInsightsProps {
  insights: DashboardData['ai_insights'];
}

const AIInsights: React.FC<AIInsightsProps> = ({ insights }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5" />
          AI 인사이트
        </CardTitle>
      </CardHeader>
      <CardContent>
        {insights.recommendations && insights.recommendations.length > 0 ? (
          <div className="space-y-3">
            {insights.recommendations.slice(0, 3).map((rec, index) => (
              <div key={index} className="flex items-start gap-3 p-3 border rounded-lg">
                <div className={`w-2 h-2 rounded-full mt-2 ${
                  rec.priority === 'critical' ? 'bg-red-500' :
                  rec.priority === 'high' ? 'bg-yellow-500' : 'bg-blue-500'
                }`} />
                <div className="flex-1">
                  <div className="font-medium">{rec.title}</div>
                  <div className="text-sm text-muted-foreground">{rec.description}</div>
                  <Badge variant="outline" className="mt-2">
                    {rec.priority}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-muted-foreground py-4">
            현재 AI 인사이트가 없습니다.
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const IntegratedDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const [error, setError] = useState<string>('');
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    // 초기 데이터 로드
    fetchDashboardData();

    // SSE 연결 설정
    setupSSEConnection();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/dashboard/integrated', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('대시보드 데이터를 불러올 수 없습니다.');
      }

      const data = await response.json();
      if (data.success) {
        setDashboardData(data.data);
        setLastUpdate(new Date().toLocaleString());
      } else {
        setError(data.error || '데이터 로드 실패');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류');
    }
  };

  const setupSSEConnection = () => {
    try {
      const eventSource = new EventSource('/api/dashboard/stream', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      eventSource.onopen = () => {
        setIsConnected(true);
        setError('');
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'dashboard_update') {
            setDashboardData(data.data);
            setLastUpdate(new Date().toLocaleString());
          } else if (data.type === 'heartbeat') {
            // 연결 유지 확인
            setIsConnected(true);
          }
        } catch (err) {
          console.error('SSE 데이터 파싱 오류:', err);
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE 연결 오류:', error);
        setIsConnected(false);
        setError('실시간 연결이 끊어졌습니다. 재연결을 시도합니다...');
        
        // 재연결 시도
        setTimeout(() => {
          if (eventSourceRef.current) {
            eventSourceRef.current.close();
          }
          setupSSEConnection();
        }, 5000);
      };

      eventSourceRef.current = eventSource;
    } catch (err) {
      setError('실시간 연결을 설정할 수 없습니다.');
    }
  };

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

  if (!dashboardData) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p>대시보드 데이터를 불러오는 중...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">통합 대시보드</h1>
          <p className="text-muted-foreground">
            마지막 업데이트: {lastUpdate}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-muted-foreground">
            {isConnected ? '실시간 연결됨' : '연결 끊어짐'}
          </span>
          <Button variant="outline" size="sm" onClick={fetchDashboardData}>
            새로고침
          </Button>
        </div>
      </div>

      {/* 메인 대시보드 */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="performance">성능</TabsTrigger>
          <TabsTrigger value="system">시스템</TabsTrigger>
          <TabsTrigger value="alerts">알림</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* 성능 메트릭 */}
          <div>
            <h2 className="text-xl font-semibold mb-4">오늘의 성과</h2>
            <PerformanceMetrics metrics={dashboardData.performance_metrics} />
          </div>

          {/* 시스템 상태 */}
          <div>
            <h2 className="text-xl font-semibold mb-4">시스템 상태</h2>
            <SystemStatus status={dashboardData.system_status} />
          </div>

          {/* AI 인사이트 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AIInsights insights={dashboardData.ai_insights} />
            
            {/* 사용자 활동 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  사용자 활동
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span>최근 주문</span>
                    <span className="font-medium">{dashboardData.user_activity.recent_orders}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>최근 로그인</span>
                    <span className="font-medium">{dashboardData.user_activity.recent_logins}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>활성 세션</span>
                    <span className="font-medium">{dashboardData.user_activity.active_sessions}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>피크 시간대</span>
                    <span className="font-medium">
                      {dashboardData.user_activity.peak_hours.join(', ')}시
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 상세 성능 메트릭 */}
            <Card>
              <CardHeader>
                <CardTitle>주문 성과</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>완료율</span>
                      <span>{((dashboardData.performance_metrics.today_orders.completed / dashboardData.performance_metrics.today_orders.total) * 100).toFixed(1)}%</span>
                    </div>
                    <Progress value={(dashboardData.performance_metrics.today_orders.completed / dashboardData.performance_metrics.today_orders.total) * 100} />
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>대기율</span>
                      <span>{((dashboardData.performance_metrics.today_orders.pending / dashboardData.performance_metrics.today_orders.total) * 100).toFixed(1)}%</span>
                    </div>
                    <Progress value={(dashboardData.performance_metrics.today_orders.pending / dashboardData.performance_metrics.today_orders.total) * 100} />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 근무 현황 */}
            <Card>
              <CardHeader>
                <CardTitle>근무 현황</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>정시 출근</span>
                      <span>{((dashboardData.performance_metrics.today_attendance.on_time / dashboardData.performance_metrics.today_attendance.total) * 100).toFixed(1)}%</span>
                    </div>
                    <Progress value={(dashboardData.performance_metrics.today_attendance.on_time / dashboardData.performance_metrics.today_attendance.total) * 100} />
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>지각</span>
                      <span>{((dashboardData.performance_metrics.today_attendance.late / dashboardData.performance_metrics.today_attendance.total) * 100).toFixed(1)}%</span>
                    </div>
                    <Progress value={(dashboardData.performance_metrics.today_attendance.late / dashboardData.performance_metrics.today_attendance.total) * 100} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="system" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 시스템 리소스 */}
            <Card>
              <CardHeader>
                <CardTitle>시스템 리소스</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>CPU 사용률</span>
                      <span>{dashboardData.system_status.cpu_usage}%</span>
                    </div>
                    <Progress value={dashboardData.system_status.cpu_usage} />
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>메모리 사용률</span>
                      <span>{dashboardData.system_status.memory_usage}%</span>
                    </div>
                    <Progress value={dashboardData.system_status.memory_usage} />
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>디스크 사용률</span>
                      <span>{dashboardData.system_status.disk_usage}%</span>
                    </div>
                    <Progress value={dashboardData.system_status.disk_usage} />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 네트워크 정보 */}
            <Card>
              <CardHeader>
                <CardTitle>네트워크 정보</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span>전송된 데이터</span>
                    <span>{(dashboardData.system_status.network_io.bytes_sent / 1024 / 1024).toFixed(2)} MB</span>
                  </div>
                  <div className="flex justify-between">
                    <span>수신된 데이터</span>
                    <span>{(dashboardData.system_status.network_io.bytes_recv / 1024 / 1024).toFixed(2)} MB</span>
                  </div>
                  <div className="flex justify-between">
                    <span>활성 연결</span>
                    <span>{dashboardData.system_status.active_connections}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>업타임</span>
                    <span>{dashboardData.system_status.uptime}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-6">
          <AlertCard alerts={dashboardData.active_alerts} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default IntegratedDashboard; 