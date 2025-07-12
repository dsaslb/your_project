'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Activity, 
  AlertTriangle, 
  BarChart3, 
  Clock, 
  Database, 
  FileText, 
  HardDrive, 
  Network, 
  Play, 
  Pause, 
  RefreshCw, 
  Settings, 
  TrendingUp, 
  Users,
  Zap,
  Cpu,
  Memory,
  Timer,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';

interface PluginSummary {
  plugin_id: string;
  status: string;
  last_update?: string;
  metrics_count: number;
  logs_count: number;
  error_logs_count: number;
  events_count: number;
  current_metrics: Record<string, any>;
  recent_errors: string[];
}

interface MetricData {
  plugin_id: string;
  metric_type: string;
  value: number;
  timestamp: string;
  metadata: Record<string, any>;
}

interface LogData {
  plugin_id: string;
  level: string;
  message: string;
  timestamp: string;
  context: Record<string, any>;
  traceback?: string;
}

interface EventData {
  plugin_id: string;
  event_type: string;
  description: string;
  timestamp: string;
  severity: string;
  data: Record<string, any>;
}

interface SnapshotData {
  plugin_id: string;
  timestamp: string;
  cpu_usage: number;
  memory_usage: number;
  response_time: number;
  error_rate: number;
  request_count: number;
  throughput: number;
  disk_io: Record<string, number>;
  network_io: Record<string, number>;
  custom_metrics: Record<string, number>;
}

interface MonitoringStatus {
  monitoring_active: boolean;
  total_plugins: number;
  active_plugins: number;
  inactive_plugins: number;
  total_metrics: number;
  total_logs: number;
  total_events: number;
}

const AdvancedPluginMonitoring: React.FC = () => {
  const [status, setStatus] = useState<MonitoringStatus | null>(null);
  const [plugins, setPlugins] = useState<PluginSummary[]>([]);
  const [selectedPlugin, setSelectedPlugin] = useState<string>('');
  const [selectedTab, setSelectedTab] = useState('overview');
  const [metrics, setMetrics] = useState<MetricData[]>([]);
  const [logs, setLogs] = useState<LogData[]>([]);
  const [events, setEvents] = useState<EventData[]>([]);
  const [snapshots, setSnapshots] = useState<SnapshotData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [timeRange, setTimeRange] = useState('24');
  const [metricType, setMetricType] = useState('cpu_usage');
  const [logLevel, setLogLevel] = useState('all');

  // 상태 조회
  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch('/api/advanced-monitoring/status');
      const data = await response.json();
      
      if (data.success) {
        setStatus(data.data);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('상태 조회 중 오류가 발생했습니다.');
    }
  }, []);

  // 플러그인 목록 조회
  const fetchPlugins = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/advanced-monitoring/plugins');
      const data = await response.json();
      
      if (data.success) {
        setPlugins(data.data);
        if (data.data.length > 0 && !selectedPlugin) {
          setSelectedPlugin(data.data[0].plugin_id);
        }
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('플러그인 목록 조회 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  }, [selectedPlugin]);

  // 메트릭 조회
  const fetchMetrics = useCallback(async () => {
    if (!selectedPlugin) return;
    
    try {
      const params = new URLSearchParams({
        hours: timeRange,
        ...(metricType !== 'all' && { metric_type: metricType })
      });
      
      const response = await fetch(`/api/advanced-monitoring/plugins/${selectedPlugin}/metrics?${params}`);
      const data = await response.json();
      
      if (data.success) {
        setMetrics(data.data);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('메트릭 조회 중 오류가 발생했습니다.');
    }
  }, [selectedPlugin, timeRange, metricType]);

  // 로그 조회
  const fetchLogs = useCallback(async () => {
    if (!selectedPlugin) return;
    
    try {
      const params = new URLSearchParams({
        hours: timeRange,
        ...(logLevel !== 'all' && { level: logLevel })
      });
      
      const response = await fetch(`/api/advanced-monitoring/plugins/${selectedPlugin}/logs?${params}`);
      const data = await response.json();
      
      if (data.success) {
        setLogs(data.data);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('로그 조회 중 오류가 발생했습니다.');
    }
  }, [selectedPlugin, timeRange, logLevel]);

  // 이벤트 조회
  const fetchEvents = useCallback(async () => {
    if (!selectedPlugin) return;
    
    try {
      const params = new URLSearchParams({ hours: timeRange });
      const response = await fetch(`/api/advanced-monitoring/plugins/${selectedPlugin}/events?${params}`);
      const data = await response.json();
      
      if (data.success) {
        setEvents(data.data);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('이벤트 조회 중 오류가 발생했습니다.');
    }
  }, [selectedPlugin, timeRange]);

  // 스냅샷 조회
  const fetchSnapshots = useCallback(async () => {
    if (!selectedPlugin) return;
    
    try {
      const params = new URLSearchParams({ hours: timeRange });
      const response = await fetch(`/api/advanced-monitoring/plugins/${selectedPlugin}/snapshots?${params}`);
      const data = await response.json();
      
      if (data.success) {
        setSnapshots(data.data);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('스냅샷 조회 중 오류가 발생했습니다.');
    }
  }, [selectedPlugin, timeRange]);

  // 데이터 새로고침
  const refreshData = useCallback(() => {
    fetchStatus();
    fetchPlugins();
    if (selectedPlugin) {
      fetchMetrics();
      fetchLogs();
      fetchEvents();
      fetchSnapshots();
    }
  }, [fetchStatus, fetchPlugins, fetchMetrics, fetchLogs, fetchEvents, fetchSnapshots, selectedPlugin]);

  // 초기 로드
  useEffect(() => {
    fetchStatus();
    fetchPlugins();
  }, [fetchStatus, fetchPlugins]);

  // 선택된 플러그인 변경 시 데이터 조회
  useEffect(() => {
    if (selectedPlugin) {
      fetchMetrics();
      fetchLogs();
      fetchEvents();
      fetchSnapshots();
    }
  }, [selectedPlugin, fetchMetrics, fetchLogs, fetchEvents, fetchSnapshots]);

  // 자동 새로고침 (30초마다)
  useEffect(() => {
    const interval = setInterval(refreshData, 30000);
    return () => clearInterval(interval);
  }, [refreshData]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'inactive':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'inactive':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'error':
      case 'critical':
        return 'bg-red-100 text-red-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'info':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('ko-KR');
  };

  const formatValue = (value: number, type: string) => {
    switch (type) {
      case 'cpu_usage':
      case 'memory_usage':
      case 'error_rate':
        return `${(value * 100).toFixed(2)}%`;
      case 'response_time':
        return `${value.toFixed(2)}ms`;
      case 'throughput':
        return `${value.toFixed(2)} req/s`;
      default:
        return value.toString();
    }
  };

  if (loading && !status) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">로딩 중...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">고도화된 플러그인 모니터링</h1>
          <p className="text-muted-foreground">
            실시간 그래프/차트, 상세 로그/이벤트 추적, 드릴다운 보기
          </p>
        </div>
        <Button onClick={refreshData} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          새로고침
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 시스템 상태 */}
      {status && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="h-5 w-5 mr-2" />
              시스템 상태
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{status.total_plugins}</div>
                <div className="text-sm text-muted-foreground">전체 플러그인</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{status.active_plugins}</div>
                <div className="text-sm text-muted-foreground">활성 플러그인</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{status.inactive_plugins}</div>
                <div className="text-sm text-muted-foreground">비활성 플러그인</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{status.total_metrics}</div>
                <div className="text-sm text-muted-foreground">총 메트릭</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 플러그인 선택 */}
      <Card>
        <CardHeader>
          <CardTitle>플러그인 선택</CardTitle>
        </CardHeader>
        <CardContent>
          <Select value={selectedPlugin} onValueChange={setSelectedPlugin}>
            <SelectTrigger>
              <SelectValue placeholder="플러그인을 선택하세요" />
            </SelectTrigger>
            <SelectContent>
              {plugins.map((plugin) => (
                <SelectItem key={plugin.plugin_id} value={plugin.plugin_id}>
                  <div className="flex items-center">
                    {getStatusIcon(plugin.status)}
                    <span className="ml-2">{plugin.plugin_id}</span>
                    <Badge className={`ml-2 ${getStatusColor(plugin.status)}`}>
                      {plugin.status}
                    </Badge>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* 선택된 플러그인 정보 */}
      {selectedPlugin && (
        <Tabs value={selectedTab} onValueChange={setSelectedTab}>
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">개요</TabsTrigger>
            <TabsTrigger value="metrics">메트릭</TabsTrigger>
            <TabsTrigger value="logs">로그</TabsTrigger>
            <TabsTrigger value="events">이벤트</TabsTrigger>
            <TabsTrigger value="snapshots">스냅샷</TabsTrigger>
          </TabsList>

          {/* 개요 탭 */}
          <TabsContent value="overview" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>플러그인 요약</CardTitle>
              </CardHeader>
              <CardContent>
                {(() => {
                  const plugin = plugins.find(p => p.plugin_id === selectedPlugin);
                  if (!plugin) return <div>플러그인 정보를 찾을 수 없습니다.</div>;

                  return (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold">{plugin.metrics_count}</div>
                          <div className="text-sm text-muted-foreground">메트릭</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold">{plugin.logs_count}</div>
                          <div className="text-sm text-muted-foreground">로그</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-red-600">{plugin.error_logs_count}</div>
                          <div className="text-sm text-muted-foreground">에러</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold">{plugin.events_count}</div>
                          <div className="text-sm text-muted-foreground">이벤트</div>
                        </div>
                      </div>

                      {plugin.recent_errors.length > 0 && (
                        <div>
                          <h4 className="font-semibold mb-2">최근 에러</h4>
                          <div className="space-y-2">
                            {plugin.recent_errors.map((error, index) => (
                              <div key={index} className="text-sm text-red-600 bg-red-50 p-2 rounded">
                                {error}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })()}
              </CardContent>
            </Card>
          </TabsContent>

          {/* 메트릭 탭 */}
          <TabsContent value="metrics" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>메트릭 데이터</CardTitle>
                <CardDescription>
                  플러그인의 성능 메트릭을 실시간으로 모니터링합니다.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4 mb-4">
                  <div className="flex items-center space-x-2">
                    <Label htmlFor="timeRange">시간 범위:</Label>
                    <Select value={timeRange} onValueChange={setTimeRange}>
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">1시간</SelectItem>
                        <SelectItem value="6">6시간</SelectItem>
                        <SelectItem value="24">24시간</SelectItem>
                        <SelectItem value="168">7일</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Label htmlFor="metricType">메트릭 타입:</Label>
                    <Select value={metricType} onValueChange={setMetricType}>
                      <SelectTrigger className="w-40">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">모든 메트릭</SelectItem>
                        <SelectItem value="cpu_usage">CPU 사용률</SelectItem>
                        <SelectItem value="memory_usage">메모리 사용률</SelectItem>
                        <SelectItem value="response_time">응답 시간</SelectItem>
                        <SelectItem value="error_rate">에러율</SelectItem>
                        <SelectItem value="throughput">처리량</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <ScrollArea className="h-96">
                  <div className="space-y-2">
                    {metrics.map((metric, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded">
                        <div className="flex items-center space-x-4">
                          <div className="flex items-center space-x-2">
                            {metric.metric_type === 'cpu_usage' && <Cpu className="h-4 w-4" />}
                            {metric.metric_type === 'memory_usage' && <Memory className="h-4 w-4" />}
                            {metric.metric_type === 'response_time' && <Timer className="h-4 w-4" />}
                            {metric.metric_type === 'error_rate' && <AlertTriangle className="h-4 w-4" />}
                            {metric.metric_type === 'throughput' && <Zap className="h-4 w-4" />}
                            <span className="font-medium">{metric.metric_type}</span>
                          </div>
                          <span className="text-lg font-bold">
                            {formatValue(metric.value, metric.metric_type)}
                          </span>
                        </div>
                        <span className="text-sm text-muted-foreground">
                          {formatTimestamp(metric.timestamp)}
                        </span>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 로그 탭 */}
          <TabsContent value="logs" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>로그 데이터</CardTitle>
                <CardDescription>
                  플러그인의 상세 로그를 확인합니다.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4 mb-4">
                  <div className="flex items-center space-x-2">
                    <Label htmlFor="timeRange">시간 범위:</Label>
                    <Select value={timeRange} onValueChange={setTimeRange}>
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">1시간</SelectItem>
                        <SelectItem value="6">6시간</SelectItem>
                        <SelectItem value="24">24시간</SelectItem>
                        <SelectItem value="168">7일</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Label htmlFor="logLevel">로그 레벨:</Label>
                    <Select value={logLevel} onValueChange={setLogLevel}>
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">모든 레벨</SelectItem>
                        <SelectItem value="debug">Debug</SelectItem>
                        <SelectItem value="info">Info</SelectItem>
                        <SelectItem value="warning">Warning</SelectItem>
                        <SelectItem value="error">Error</SelectItem>
                        <SelectItem value="critical">Critical</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <ScrollArea className="h-96">
                  <div className="space-y-2">
                    {logs.map((log, index) => (
                      <div key={index} className="p-3 border rounded">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <Badge className={getLogLevelColor(log.level)}>
                              {log.level.toUpperCase()}
                            </Badge>
                            <span className="text-sm text-muted-foreground">
                              {formatTimestamp(log.timestamp)}
                            </span>
                          </div>
                        </div>
                        <div className="text-sm">{log.message}</div>
                        {log.traceback && (
                          <details className="mt-2">
                            <summary className="cursor-pointer text-sm text-muted-foreground">
                              스택 트레이스 보기
                            </summary>
                            <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                              {log.traceback}
                            </pre>
                          </details>
                        )}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 이벤트 탭 */}
          <TabsContent value="events" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>이벤트 데이터</CardTitle>
                <CardDescription>
                  플러그인의 중요 이벤트를 확인합니다.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4 mb-4">
                  <div className="flex items-center space-x-2">
                    <Label htmlFor="timeRange">시간 범위:</Label>
                    <Select value={timeRange} onValueChange={setTimeRange}>
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">1시간</SelectItem>
                        <SelectItem value="6">6시간</SelectItem>
                        <SelectItem value="24">24시간</SelectItem>
                        <SelectItem value="168">7일</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <ScrollArea className="h-96">
                  <div className="space-y-2">
                    {events.map((event, index) => (
                      <div key={index} className="p-3 border rounded">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <Badge className={getSeverityColor(event.severity)}>
                              {event.severity.toUpperCase()}
                            </Badge>
                            <span className="font-medium">{event.event_type}</span>
                          </div>
                          <span className="text-sm text-muted-foreground">
                            {formatTimestamp(event.timestamp)}
                          </span>
                        </div>
                        <div className="text-sm">{event.description}</div>
                        {Object.keys(event.data).length > 0 && (
                          <details className="mt-2">
                            <summary className="cursor-pointer text-sm text-muted-foreground">
                              이벤트 데이터 보기
                            </summary>
                            <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                              {JSON.stringify(event.data, null, 2)}
                            </pre>
                          </details>
                        )}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 스냅샷 탭 */}
          <TabsContent value="snapshots" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>성능 스냅샷</CardTitle>
                <CardDescription>
                  플러그인의 성능 스냅샷을 확인합니다.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4 mb-4">
                  <div className="flex items-center space-x-2">
                    <Label htmlFor="timeRange">시간 범위:</Label>
                    <Select value={timeRange} onValueChange={setTimeRange}>
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">1시간</SelectItem>
                        <SelectItem value="6">6시간</SelectItem>
                        <SelectItem value="24">24시간</SelectItem>
                        <SelectItem value="168">7일</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <ScrollArea className="h-96">
                  <div className="space-y-4">
                    {snapshots.map((snapshot, index) => (
                      <div key={index} className="p-4 border rounded">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-semibold">스냅샷 #{index + 1}</h4>
                          <span className="text-sm text-muted-foreground">
                            {formatTimestamp(snapshot.timestamp)}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="text-center">
                            <div className="text-lg font-bold text-blue-600">
                              {formatValue(snapshot.cpu_usage, 'cpu_usage')}
                            </div>
                            <div className="text-sm text-muted-foreground">CPU</div>
                          </div>
                          <div className="text-center">
                            <div className="text-lg font-bold text-green-600">
                              {formatValue(snapshot.memory_usage, 'memory_usage')}
                            </div>
                            <div className="text-sm text-muted-foreground">메모리</div>
                          </div>
                          <div className="text-center">
                            <div className="text-lg font-bold text-orange-600">
                              {formatValue(snapshot.response_time, 'response_time')}
                            </div>
                            <div className="text-sm text-muted-foreground">응답시간</div>
                          </div>
                          <div className="text-center">
                            <div className="text-lg font-bold text-red-600">
                              {formatValue(snapshot.error_rate, 'error_rate')}
                            </div>
                            <div className="text-sm text-muted-foreground">에러율</div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mt-4">
                          <div className="text-center">
                            <div className="text-lg font-bold text-purple-600">
                              {snapshot.request_count}
                            </div>
                            <div className="text-sm text-muted-foreground">요청 수</div>
                          </div>
                          <div className="text-center">
                            <div className="text-lg font-bold text-indigo-600">
                              {formatValue(snapshot.throughput, 'throughput')}
                            </div>
                            <div className="text-sm text-muted-foreground">처리량</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
};

export default AdvancedPluginMonitoring; 