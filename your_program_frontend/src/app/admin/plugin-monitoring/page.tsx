"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertTriangle, Activity, Cpu, Memory, Clock, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

interface PluginMetrics {
  plugin_id: string;
  plugin_name: string;
  cpu_usage: number;
  memory_usage: number;
  response_time: number;
  error_count: number;
  request_count: number;
  last_activity: string;
  status: string;
  uptime: number;
}

interface PluginAlert {
  id: string;
  plugin_id: string;
  plugin_name: string;
  level: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  details: Record<string, any>;
  timestamp: string;
  resolved: boolean;
  resolved_at?: string;
}

const PluginMonitoringPage: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [metrics, setMetrics] = useState<Record<string, PluginMetrics>>({});
  const [alerts, setAlerts] = useState<PluginAlert[]>([]);
  const [metricsHistory, setMetricsHistory] = useState<Record<string, any[]>>({});
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // WebSocket 연결
  const connectWebSocket = () => {
    try {
      const ws = new WebSocket('ws://localhost:8765');
      
      ws.onopen = () => {
        setIsConnected(true);
        console.log('플러그인 모니터링 WebSocket 연결됨');
        
        // 인증 정보 전송
        ws.send(JSON.stringify({
          type: 'auth',
          user_id: 'admin',
          role: 'admin'
        }));
        
        // 초기 데이터 요청
        ws.send(JSON.stringify({ type: 'get_all_metrics' }));
        ws.send(JSON.stringify({ type: 'get_active_alerts' }));
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('WebSocket 메시지 파싱 오류:', error);
        }
      };
      
      ws.onclose = () => {
        setIsConnected(false);
        console.log('플러그인 모니터링 WebSocket 연결 끊어짐');
        
        // 재연결 시도
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 5000);
      };
      
      ws.onerror = (error) => {
        console.error('플러그인 모니터링 WebSocket 오류:', error);
        setIsConnected(false);
      };
      
      wsRef.current = ws;
    } catch (error) {
      console.error('플러그인 모니터링 WebSocket 연결 실패:', error);
      setIsConnected(false);
    }
  };

  // WebSocket 메시지 처리
  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'all_metrics':
        setMetrics(data.data);
        updateMetricsHistory(data.data);
        break;
        
      case 'metrics':
        setMetrics(prev => ({
          ...prev,
          [data.plugin_id]: data.data
        }));
        updateMetricsHistory({ [data.plugin_id]: data.data });
        break;
        
      case 'active_alerts':
        setAlerts(data.data);
        break;
        
      case 'alert':
        const newAlert = data.data;
        setAlerts(prev => [newAlert, ...prev]);
        break;
    }
  };

  // 메트릭 히스토리 업데이트
  const updateMetricsHistory = (newMetrics: Record<string, PluginMetrics>) => {
    setMetricsHistory(prev => {
      const updated = { ...prev };
      const timestamp = new Date().toISOString();
      
      Object.entries(newMetrics).forEach(([pluginId, metric]) => {
        if (!updated[pluginId]) {
          updated[pluginId] = [];
        }
        
        updated[pluginId].push({
          timestamp,
          cpu_usage: metric.cpu_usage,
          memory_usage: metric.memory_usage,
          response_time: metric.response_time,
          error_count: metric.error_count,
          request_count: metric.request_count
        });
        
        // 최근 50개 데이터만 유지
        if (updated[pluginId].length > 50) {
          updated[pluginId] = updated[pluginId].slice(-50);
        }
      });
      
      return updated;
    });
  };

  // 알림 해결 처리
  const resolveAlert = (alertId: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'resolve_alert',
        alert_id: alertId
      }));
    }
    
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  // 상태별 색상 반환
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-red-100 text-red-800';
      case 'warning': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // 알림 레벨별 색상 반환
  const getAlertLevelColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'error': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  // 알림 레벨별 아이콘 반환
  const getAlertLevelIcon = (level: string) => {
    switch (level) {
      case 'critical': return <XCircle className="h-4 w-4" />;
      case 'error': return <AlertCircle className="h-4 w-4" />;
      case 'warning': return <AlertTriangle className="h-4 w-4" />;
      default: return <CheckCircle className="h-4 w-4" />;
    }
  };

  // 에러율 계산
  const getErrorRate = (metric: PluginMetrics) => {
    if (metric.request_count === 0) return 0;
    return (metric.error_count / metric.request_count) * 100;
  };

  // 연결 상태 표시
  useEffect(() => {
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  const activeAlerts = alerts.filter(alert => !alert.resolved);
  const resolvedAlerts = alerts.filter(alert => alert.resolved);

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">플러그인 모니터링</h1>
          <p className="text-gray-600 dark:text-gray-400">
            실시간 플러그인 성능 및 상태 모니터링
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            isConnected 
              ? 'bg-green-100 text-green-800' 
              : 'bg-red-100 text-red-800'
          }`}>
            {isConnected ? '🔗 연결됨' : '❌ 연결 끊어짐'}
          </div>
        </div>
      </div>

      {/* 요약 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">모니터링 중인 플러그인</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Object.keys(metrics).length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">활성 알림</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{activeAlerts.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평균 CPU 사용률</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.keys(metrics).length > 0 
                ? Math.round(Object.values(metrics).reduce((sum, m) => sum + m.cpu_usage, 0) / Object.keys(metrics).length)
                : 0}%
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평균 메모리 사용률</CardTitle>
            <Memory className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.keys(metrics).length > 0 
                ? Math.round(Object.values(metrics).reduce((sum, m) => sum + m.memory_usage, 0) / Object.keys(metrics).length)
                : 0}%
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 메인 콘텐츠 */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="alerts">알림</TabsTrigger>
          <TabsTrigger value="details">상세 메트릭</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* 플러그인 목록 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(metrics).map(([pluginId, metric]) => (
              <Card key={pluginId}>
                <CardHeader>
                  <CardTitle className="text-lg">{metric.plugin_name}</CardTitle>
                  <CardDescription>
                    <Badge className={getStatusColor(metric.status)}>
                      {metric.status}
                    </Badge>
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* CPU 사용률 */}
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>CPU 사용률</span>
                      <span>{metric.cpu_usage.toFixed(1)}%</span>
                    </div>
                    <Progress 
                      value={metric.cpu_usage} 
                      className={metric.cpu_usage > 80 ? 'bg-red-100' : ''}
                    />
                  </div>

                  {/* 메모리 사용률 */}
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>메모리 사용률</span>
                      <span>{metric.memory_usage.toFixed(1)}%</span>
                    </div>
                    <Progress 
                      value={metric.memory_usage} 
                      className={metric.memory_usage > 85 ? 'bg-red-100' : ''}
                    />
                  </div>

                  {/* 응답 시간 */}
                  <div className="flex justify-between text-sm">
                    <span>응답 시간</span>
                    <span>{metric.response_time.toFixed(2)}초</span>
                  </div>

                  {/* 에러율 */}
                  <div className="flex justify-between text-sm">
                    <span>에러율</span>
                    <span className={getErrorRate(metric) > 10 ? 'text-red-600' : ''}>
                      {getErrorRate(metric).toFixed(1)}%
                    </span>
                  </div>

                  {/* 마지막 활동 */}
                  <div className="text-xs text-gray-500">
                    마지막 활동: {new Date(metric.last_activity).toLocaleString()}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          {/* 활성 알림 */}
          <Card>
            <CardHeader>
              <CardTitle>활성 알림 ({activeAlerts.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {activeAlerts.length === 0 ? (
                <p className="text-gray-500">활성 알림이 없습니다.</p>
              ) : (
                <div className="space-y-3">
                  {activeAlerts.map((alert) => (
                    <div 
                      key={alert.id} 
                      className={`p-4 rounded-lg border ${getAlertLevelColor(alert.level)}`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          {getAlertLevelIcon(alert.level)}
                          <div className="flex-1">
                            <div className="font-medium">{alert.plugin_name}</div>
                            <div className="text-sm mt-1">{alert.message}</div>
                            <div className="text-xs mt-2">
                              {new Date(alert.timestamp).toLocaleString()}
                            </div>
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => resolveAlert(alert.id)}
                        >
                          해결
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* 해결된 알림 */}
          {resolvedAlerts.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>해결된 알림 ({resolvedAlerts.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {resolvedAlerts.slice(0, 10).map((alert) => (
                    <div 
                      key={alert.id} 
                      className="p-4 rounded-lg border bg-gray-50 dark:bg-gray-800"
                    >
                      <div className="flex items-start gap-3">
                        <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                        <div className="flex-1">
                          <div className="font-medium">{alert.plugin_name}</div>
                          <div className="text-sm mt-1">{alert.message}</div>
                          <div className="text-xs mt-2 text-gray-500">
                            해결됨: {alert.resolved_at && new Date(alert.resolved_at).toLocaleString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="details" className="space-y-4">
          {/* 상세 메트릭 차트 */}
          {Object.entries(metricsHistory).map(([pluginId, history]) => {
            const plugin = metrics[pluginId];
            if (!plugin || history.length < 2) return null;

            return (
              <Card key={pluginId}>
                <CardHeader>
                  <CardTitle>{plugin.plugin_name} - 상세 메트릭</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* CPU 사용률 차트 */}
                    <div>
                      <h4 className="text-sm font-medium mb-2">CPU 사용률 추이</h4>
                      <ResponsiveContainer width="100%" height={200}>
                        <LineChart data={history}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis 
                            dataKey="timestamp" 
                            tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                          />
                          <YAxis />
                          <Tooltip 
                            labelFormatter={(value) => new Date(value).toLocaleString()}
                            formatter={(value) => [`${value}%`, 'CPU 사용률']}
                          />
                          <Line 
                            type="monotone" 
                            dataKey="cpu_usage" 
                            stroke="#3b82f6" 
                            strokeWidth={2}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>

                    {/* 메모리 사용률 차트 */}
                    <div>
                      <h4 className="text-sm font-medium mb-2">메모리 사용률 추이</h4>
                      <ResponsiveContainer width="100%" height={200}>
                        <LineChart data={history}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis 
                            dataKey="timestamp" 
                            tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                          />
                          <YAxis />
                          <Tooltip 
                            labelFormatter={(value) => new Date(value).toLocaleString()}
                            formatter={(value) => [`${value}%`, '메모리 사용률']}
                          />
                          <Line 
                            type="monotone" 
                            dataKey="memory_usage" 
                            stroke="#10b981" 
                            strokeWidth={2}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PluginMonitoringPage; 