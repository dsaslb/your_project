'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { 
  Activity, 
  Cpu, 
  HardDrive, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  TrendingUp,
  Settings,
  RefreshCw,
  Play,
  Pause,
  Square
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

interface PluginMetrics {
  plugin_id: string;
  plugin_name: string;
  cpu_usage: number;
  memory_usage: number;
  response_time: number;
  error_rate: number;
  request_count: number;
  uptime: number;
  last_activity: string;
  status: 'active' | 'inactive' | 'error';
  timestamp: string;
}

interface Alert {
  id: string;
  type: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  message: string;
  plugin_id?: string;
  plugin_name?: string;
  current_value?: number;
  threshold_value?: number;
  timestamp: string;
  resolved: boolean;
}

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_io: {
    bytes_sent: number;
    bytes_recv: number;
  };
  active_connections: number;
  process_count: number;
  timestamp: string;
}

const PluginMonitoringDashboard: React.FC = () => {
  const [plugins, setPlugins] = useState<Record<string, PluginMetrics>>({});
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [selectedPlugin, setSelectedPlugin] = useState<string>('');
  const [timeRange, setTimeRange] = useState<string>('1h');
  const [isMonitoring, setIsMonitoring] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [thresholds, setThresholds] = useState({
    cpu_threshold: 80,
    memory_threshold: 85,
    error_rate_threshold: 10,
    response_time_threshold: 5
  });

  // 차트 데이터 상태
  const [cpuHistory, setCpuHistory] = useState<any[]>([]);
  const [memoryHistory, setMemoryHistory] = useState<any[]>([]);
  const [errorRateHistory, setErrorRateHistory] = useState<any[]>([]);
  const [responseTimeHistory, setResponseTimeHistory] = useState<any[]>([]);

  useEffect(() => {
    initializeMonitoring();
    const interval = setInterval(loadMetrics, 10000); // 10초마다 업데이트
    
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedPlugin) {
      loadPluginHistory(selectedPlugin);
    }
  }, [selectedPlugin, timeRange]);

  const initializeMonitoring = async () => {
    try {
      setIsLoading(true);
      await Promise.all([
        loadPlugins(),
        loadAlerts(),
        loadSystemMetrics(),
        loadThresholds()
      ]);
    } catch (error) {
      console.error('모니터링 초기화 실패:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadPlugins = async () => {
    try {
      const response = await fetch('/api/enhanced-alerts/plugins/metrics');
      const data = await response.json();
      
      if (data.success) {
        setPlugins(data.metrics);
        if (!selectedPlugin && Object.keys(data.metrics).length > 0) {
          setSelectedPlugin(Object.keys(data.metrics)[0]);
        }
      }
    } catch (error) {
      console.error('플러그인 메트릭 로드 실패:', error);
    }
  };

  const loadAlerts = async () => {
    try {
      const response = await fetch('/api/enhanced-alerts/alerts?limit=100');
      const data = await response.json();
      
      if (data.success) {
        setAlerts(data.alerts);
      }
    } catch (error) {
      console.error('알림 로드 실패:', error);
    }
  };

  const loadSystemMetrics = async () => {
    try {
      const response = await fetch('/api/realtime/system-metrics');
      const data = await response.json();
      
      if (data.success) {
        setSystemMetrics(data.metrics);
      }
    } catch (error) {
      console.error('시스템 메트릭 로드 실패:', error);
    }
  };

  const loadThresholds = async () => {
    try {
      const response = await fetch('/api/enhanced-alerts/thresholds');
      const data = await response.json();
      
      if (data.success) {
        setThresholds({
          cpu_threshold: data.thresholds.plugin_cpu_threshold,
          memory_threshold: data.thresholds.plugin_memory_threshold,
          error_rate_threshold: data.thresholds.plugin_error_rate_threshold,
          response_time_threshold: data.thresholds.plugin_response_time_threshold
        });
      }
    } catch (error) {
      console.error('임계값 로드 실패:', error);
    }
  };

  const loadPluginHistory = async (pluginId: string) => {
    try {
      const response = await fetch(`/api/enhanced-alerts/plugins/${pluginId}/history?range=${timeRange}`);
      const data = await response.json();
      
      if (data.success) {
        setCpuHistory(data.history.cpu || []);
        setMemoryHistory(data.history.memory || []);
        setErrorRateHistory(data.history.error_rate || []);
        setResponseTimeHistory(data.history.response_time || []);
      }
    } catch (error) {
      console.error('플러그인 히스토리 로드 실패:', error);
    }
  };

  const loadMetrics = async () => {
    if (!isMonitoring) return;
    
    await Promise.all([
      loadPlugins(),
      loadAlerts(),
      loadSystemMetrics()
    ]);
  };

  const updateThresholds = async (newThresholds: typeof thresholds) => {
    try {
      const response = await fetch('/api/enhanced-alerts/thresholds', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plugin_cpu_threshold: newThresholds.cpu_threshold,
          plugin_memory_threshold: newThresholds.memory_threshold,
          plugin_error_rate_threshold: newThresholds.error_rate_threshold,
          plugin_response_time_threshold: newThresholds.response_time_threshold
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setThresholds(newThresholds);
      }
    } catch (error) {
      console.error('임계값 업데이트 실패:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'inactive': return 'bg-gray-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '활성';
      case 'inactive': return '비활성';
      case 'error': return '오류';
      default: return '알 수 없음';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-600';
      case 'error': return 'bg-red-500';
      case 'warning': return 'bg-yellow-500';
      case 'info': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}시간 ${minutes}분`;
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const pluginList = Object.values(plugins);
  const activeAlerts = alerts.filter(alert => !alert.resolved);
  const criticalAlerts = activeAlerts.filter(alert => alert.severity === 'critical');
  const warningAlerts = activeAlerts.filter(alert => alert.severity === 'warning');

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <span className="ml-4 text-lg">모니터링 시스템 로딩 중...</span>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">플러그인 모니터링 대시보드</h1>
          <p className="text-gray-600 mt-2">실시간 플러그인 성능 및 상태 모니터링</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Switch
              checked={isMonitoring}
              onCheckedChange={setIsMonitoring}
            />
            <Label>실시간 모니터링</Label>
          </div>
          <Button
            onClick={loadMetrics}
            variant="outline"
            size="sm"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            새로고침
          </Button>
        </div>
      </div>

      {/* 시스템 개요 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">시스템 CPU</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {systemMetrics?.cpu_usage?.toFixed(1) || 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              임계값: {thresholds.cpu_threshold}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">시스템 메모리</CardTitle>
                            <HardDrive className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {systemMetrics?.memory_usage?.toFixed(1) || 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              임계값: {thresholds.memory_threshold}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">활성 플러그인</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {pluginList.filter(p => p.status === 'active').length}
            </div>
            <p className="text-xs text-muted-foreground">
              총 {pluginList.length}개
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">활성 알림</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {activeAlerts.length}
            </div>
            <p className="text-xs text-muted-foreground">
              심각: {criticalAlerts.length}개
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 플러그인 목록 */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>플러그인 목록</CardTitle>
              <CardDescription>
                활성 플러그인 및 상태 정보
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {pluginList.map((plugin) => (
                <div
                  key={plugin.plugin_id}
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    selectedPlugin === plugin.plugin_id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedPlugin(plugin.plugin_id)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900">
                      {plugin.plugin_name || plugin.plugin_id}
                    </h3>
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${getStatusColor(plugin.status)}`}></div>
                      <Badge variant="outline" className="text-xs">
                        {getStatusText(plugin.status)}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-500">CPU:</span>
                      <span className={`ml-1 font-medium ${
                        plugin.cpu_usage > thresholds.cpu_threshold ? 'text-red-600' : 'text-gray-900'
                      }`}>
                        {plugin.cpu_usage.toFixed(1)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500">메모리:</span>
                      <span className={`ml-1 font-medium ${
                        plugin.memory_usage > thresholds.memory_threshold ? 'text-red-600' : 'text-gray-900'
                      }`}>
                        {plugin.memory_usage.toFixed(1)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500">에러율:</span>
                      <span className={`ml-1 font-medium ${
                        plugin.error_rate > thresholds.error_rate_threshold ? 'text-red-600' : 'text-gray-900'
                      }`}>
                        {plugin.error_rate.toFixed(1)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500">응답시간:</span>
                      <span className={`ml-1 font-medium ${
                        plugin.response_time > thresholds.response_time_threshold ? 'text-red-600' : 'text-gray-900'
                      }`}>
                        {plugin.response_time.toFixed(2)}s
                      </span>
                    </div>
                  </div>
                  
                  <div className="mt-2 text-xs text-gray-500">
                    <Clock className="inline h-3 w-3 mr-1" />
                    {formatUptime(plugin.uptime)}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* 선택된 플러그인 상세 정보 */}
        <div className="lg:col-span-2">
          {selectedPlugin && plugins[selectedPlugin] ? (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{plugins[selectedPlugin].plugin_name || selectedPlugin}</CardTitle>
                    <CardDescription>
                      플러그인 ID: {selectedPlugin}
                    </CardDescription>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(plugins[selectedPlugin].status)}`}></div>
                    <Badge variant="outline">
                      {getStatusText(plugins[selectedPlugin].status)}
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="overview" className="w-full">
                  <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="overview">개요</TabsTrigger>
                    <TabsTrigger value="charts">차트</TabsTrigger>
                    <TabsTrigger value="alerts">알림</TabsTrigger>
                    <TabsTrigger value="settings">설정</TabsTrigger>
                  </TabsList>

                  <TabsContent value="overview" className="space-y-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">
                          {plugins[selectedPlugin].cpu_usage.toFixed(1)}%
                        </div>
                        <div className="text-sm text-gray-600">CPU 사용률</div>
                      </div>
                      <div className="text-center p-4 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">
                          {plugins[selectedPlugin].memory_usage.toFixed(1)}%
                        </div>
                        <div className="text-sm text-gray-600">메모리 사용률</div>
                      </div>
                      <div className="text-center p-4 bg-yellow-50 rounded-lg">
                        <div className="text-2xl font-bold text-yellow-600">
                          {plugins[selectedPlugin].error_rate.toFixed(1)}%
                        </div>
                        <div className="text-sm text-gray-600">에러율</div>
                      </div>
                      <div className="text-center p-4 bg-purple-50 rounded-lg">
                        <div className="text-2xl font-bold text-purple-600">
                          {plugins[selectedPlugin].response_time.toFixed(2)}s
                        </div>
                        <div className="text-sm text-gray-600">응답시간</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-4 border rounded-lg">
                        <h4 className="font-medium mb-2">요청 통계</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span>총 요청 수:</span>
                            <span className="font-medium">{plugins[selectedPlugin].request_count.toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>성공률:</span>
                            <span className="font-medium">
                              {((100 - plugins[selectedPlugin].error_rate)).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="p-4 border rounded-lg">
                        <h4 className="font-medium mb-2">시스템 정보</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span>가동시간:</span>
                            <span className="font-medium">{formatUptime(plugins[selectedPlugin].uptime)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>마지막 활동:</span>
                            <span className="font-medium">
                              {new Date(plugins[selectedPlugin].last_activity).toLocaleString('ko-KR')}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="charts" className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium">성능 트렌드</h4>
                      <Select value={timeRange} onValueChange={setTimeRange}>
                        <SelectTrigger className="w-32">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1h">1시간</SelectItem>
                          <SelectItem value="6h">6시간</SelectItem>
                          <SelectItem value="24h">24시간</SelectItem>
                          <SelectItem value="7d">7일</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-6">
                      <div>
                        <h5 className="text-sm font-medium mb-2">CPU 사용률</h5>
                        <ResponsiveContainer width="100%" height={200}>
                          <LineChart data={cpuHistory}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="timestamp" />
                            <YAxis />
                            <Tooltip />
                            <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>

                      <div>
                        <h5 className="text-sm font-medium mb-2">메모리 사용률</h5>
                        <ResponsiveContainer width="100%" height={200}>
                          <LineChart data={memoryHistory}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="timestamp" />
                            <YAxis />
                            <Tooltip />
                            <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={2} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>

                      <div>
                        <h5 className="text-sm font-medium mb-2">에러율</h5>
                        <ResponsiveContainer width="100%" height={200}>
                          <LineChart data={errorRateHistory}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="timestamp" />
                            <YAxis />
                            <Tooltip />
                            <Line type="monotone" dataKey="value" stroke="#f59e0b" strokeWidth={2} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="alerts" className="space-y-4">
                    <h4 className="font-medium">플러그인 관련 알림</h4>
                    <div className="space-y-2">
                      {alerts
                        .filter(alert => alert.plugin_id === selectedPlugin)
                        .map(alert => (
                          <div
                            key={alert.id}
                            className={`p-4 border rounded-lg ${
                              alert.severity === 'critical' ? 'border-red-200 bg-red-50' :
                              alert.severity === 'error' ? 'border-red-200 bg-red-50' :
                              alert.severity === 'warning' ? 'border-yellow-200 bg-yellow-50' :
                              'border-blue-200 bg-blue-50'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <div>
                                <h5 className="font-medium">{alert.title}</h5>
                                <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                                <p className="text-xs text-gray-500 mt-2">
                                  {new Date(alert.timestamp).toLocaleString('ko-KR')}
                                </p>
                              </div>
                              <Badge className={`${getSeverityColor(alert.severity)} text-white`}>
                                {alert.severity}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      {alerts.filter(alert => alert.plugin_id === selectedPlugin).length === 0 && (
                        <div className="text-center py-8 text-gray-500">
                          이 플러그인에 대한 알림이 없습니다.
                        </div>
                      )}
                    </div>
                  </TabsContent>

                  <TabsContent value="settings" className="space-y-4">
                    <h4 className="font-medium">임계값 설정</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="cpu-threshold">CPU 임계값 (%)</Label>
                        <Input
                          id="cpu-threshold"
                          type="number"
                          value={thresholds.cpu_threshold}
                          onChange={(e) => setThresholds(prev => ({
                            ...prev,
                            cpu_threshold: parseFloat(e.target.value)
                          }))}
                        />
                      </div>
                      <div>
                        <Label htmlFor="memory-threshold">메모리 임계값 (%)</Label>
                        <Input
                          id="memory-threshold"
                          type="number"
                          value={thresholds.memory_threshold}
                          onChange={(e) => setThresholds(prev => ({
                            ...prev,
                            memory_threshold: parseFloat(e.target.value)
                          }))}
                        />
                      </div>
                      <div>
                        <Label htmlFor="error-threshold">에러율 임계값 (%)</Label>
                        <Input
                          id="error-threshold"
                          type="number"
                          value={thresholds.error_rate_threshold}
                          onChange={(e) => setThresholds(prev => ({
                            ...prev,
                            error_rate_threshold: parseFloat(e.target.value)
                          }))}
                        />
                      </div>
                      <div>
                        <Label htmlFor="response-threshold">응답시간 임계값 (초)</Label>
                        <Input
                          id="response-threshold"
                          type="number"
                          step="0.1"
                          value={thresholds.response_time_threshold}
                          onChange={(e) => setThresholds(prev => ({
                            ...prev,
                            response_time_threshold: parseFloat(e.target.value)
                          }))}
                        />
                      </div>
                    </div>
                    <Button
                      onClick={() => updateThresholds(thresholds)}
                      className="w-full"
                    >
                      <Settings className="h-4 w-4 mr-2" />
                      임계값 업데이트
                    </Button>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="flex items-center justify-center h-64">
                <div className="text-center text-gray-500">
                  <Activity className="h-12 w-12 mx-auto mb-4" />
                  <p>플러그인을 선택하여 상세 정보를 확인하세요.</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default PluginMonitoringDashboard; 