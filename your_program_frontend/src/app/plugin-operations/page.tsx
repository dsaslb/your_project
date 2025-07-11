'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Play, 
  Square, 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Settings,
  BarChart3,
  FileText,
  Shield
} from 'lucide-react';

interface OperationsStatus {
  operations_status: {
    running: boolean;
    start_time: string;
    uptime: number;
    total_operations: number;
    successful_operations: number;
    failed_operations: number;
  };
  performance_summary: {
    total_operations: number;
    success_rate: number;
    avg_response_time: number;
    current_memory_usage: number;
    current_cpu_usage: number;
    current_error_rate: number;
  };
  recent_alerts: Array<{
    timestamp: string;
    level: string;
    title: string;
    message: string;
  }>;
  system_health: {
    overall_status: string;
    components: Record<string, any>;
    issues: string[];
  };
}

interface Alert {
  timestamp: string;
  level: string;
  title: string;
  message: string;
}

interface Threshold {
  max_response_time: number;
  max_memory_usage: number;
  max_cpu_usage: number;
  max_error_rate: number;
  max_plugin_load_time: number;
}

export default function PluginOperationsPage() {
  const [status, setStatus] = useState<OperationsStatus | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [thresholds, setThresholds] = useState<Threshold | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 상태 조회
  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/plugin-operations/status');
      const data = await response.json();
      
      if (data.status === 'success') {
        setStatus(data.data);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('상태 조회 실패');
    } finally {
      setLoading(false);
    }
  };

  // 알림 조회
  const fetchAlerts = async () => {
    try {
      const response = await fetch('/api/plugin-operations/alerts');
      const data = await response.json();
      
      if (data.status === 'success') {
        setAlerts(data.data);
      }
    } catch (err) {
      console.error('알림 조회 실패:', err);
    }
  };

  // 임계값 조회
  const fetchThresholds = async () => {
    try {
      const response = await fetch('/api/plugin-operations/thresholds');
      const data = await response.json();
      
      if (data.status === 'success') {
        setThresholds(data.data);
      }
    } catch (err) {
      console.error('임계값 조회 실패:', err);
    }
  };

  // 운영 시작
  const startOperations = async () => {
    try {
      const response = await fetch('/api/plugin-operations/start', {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        fetchStatus();
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('운영 시작 실패');
    }
  };

  // 운영 중지
  const stopOperations = async () => {
    try {
      const response = await fetch('/api/plugin-operations/stop', {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        fetchStatus();
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('운영 중지 실패');
    }
  };

  // 알림 정리
  const clearAlerts = async (level: string = 'all') => {
    try {
      const response = await fetch('/api/plugin-operations/alerts/clear', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ level })
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        fetchAlerts();
      }
    } catch (err) {
      console.error('알림 정리 실패:', err);
    }
  };

  // 임계값 설정
  const setThreshold = async (name: string, value: number) => {
    try {
      const response = await fetch('/api/plugin-operations/thresholds', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, value })
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        fetchThresholds();
      }
    } catch (err) {
      console.error('임계값 설정 실패:', err);
    }
  };

  // 초기 로드
  useEffect(() => {
    fetchStatus();
    fetchAlerts();
    fetchThresholds();
  }, []);

  // 주기적 업데이트
  useEffect(() => {
    const interval = setInterval(() => {
      fetchStatus();
      fetchAlerts();
    }, 30000); // 30초마다 업데이트

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Activity className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>플러그인 운영 상태를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'critical': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getAlertColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'info': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">플러그인 운영 및 모니터링</h1>
          <p className="text-muted-foreground">
            플러그인 시스템의 안정성과 성능을 실시간으로 모니터링합니다
          </p>
        </div>
        <div className="flex gap-2">
          {status?.operations_status.running ? (
            <Button onClick={stopOperations} variant="destructive">
              <Square className="h-4 w-4 mr-2" />
              운영 중지
            </Button>
          ) : (
            <Button onClick={startOperations}>
              <Play className="h-4 w-4 mr-2" />
              운영 시작
            </Button>
          )}
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="performance">성능</TabsTrigger>
          <TabsTrigger value="alerts">알림</TabsTrigger>
          <TabsTrigger value="settings">설정</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* 운영 상태 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                운영 상태
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold">
                    {status?.operations_status.running ? (
                      <Badge className="bg-green-500">실행 중</Badge>
                    ) : (
                      <Badge variant="secondary">중지됨</Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">상태</p>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold">
                    {status?.operations_status.start_time ? 
                      formatUptime(status.operations_status.uptime) : 
                      '00:00:00'
                    }
                  </div>
                  <p className="text-sm text-muted-foreground">가동 시간</p>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold">
                    {status?.operations_status.total_operations || 0}
                  </div>
                  <p className="text-sm text-muted-foreground">총 운영 수</p>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold">
                    {status?.performance_summary.success_rate.toFixed(1) || 0}%
                  </div>
                  <p className="text-sm text-muted-foreground">성공률</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 시스템 헬스 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                시스템 헬스
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span>전체 상태</span>
                  <Badge className={getStatusColor(status?.system_health.overall_status || 'unknown')}>
                    {status?.system_health.overall_status || 'unknown'}
                  </Badge>
                </div>
                
                {status?.system_health.components && Object.entries(status.system_health.components).map(([name, component]) => (
                  <div key={name} className="flex items-center justify-between">
                    <span className="capitalize">{name.replace('_', ' ')}</span>
                    <div className="flex items-center gap-2">
                      <Badge className={getStatusColor(component.status)}>
                        {component.status}
                      </Badge>
                      {component.usage && (
                        <span className="text-sm text-muted-foreground">
                          {component.usage.toFixed(1)}%
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 최근 알림 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                최근 알림
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {alerts.slice(0, 5).map((alert, index) => (
                  <Alert key={index} className={getAlertColor(alert.level)}>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      <div className="font-medium">{alert.title}</div>
                      <div className="text-sm">{alert.message}</div>
                      <div className="text-xs mt-1">
                        {new Date(alert.timestamp).toLocaleString()}
                      </div>
                    </AlertDescription>
                  </Alert>
                ))}
                {alerts.length === 0 && (
                  <p className="text-muted-foreground text-center py-4">
                    알림이 없습니다
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          {/* 성능 메트릭 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                성능 메트릭
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>메모리 사용량</span>
                      <span>{status?.performance_summary.current_memory_usage.toFixed(1) || 0}%</span>
                    </div>
                    <Progress 
                      value={status?.performance_summary.current_memory_usage || 0} 
                      className="h-2"
                    />
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>CPU 사용량</span>
                      <span>{status?.performance_summary.current_cpu_usage.toFixed(1) || 0}%</span>
                    </div>
                    <Progress 
                      value={status?.performance_summary.current_cpu_usage || 0} 
                      className="h-2"
                    />
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>에러율</span>
                      <span>{status?.performance_summary.current_error_rate.toFixed(1) || 0}%</span>
                    </div>
                    <Progress 
                      value={status?.performance_summary.current_error_rate || 0} 
                      className="h-2"
                    />
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold">
                      {status?.performance_summary.avg_response_time.toFixed(2) || 0}초
                    </div>
                    <p className="text-sm text-muted-foreground">평균 응답 시간</p>
                  </div>
                  
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold">
                      {status?.performance_summary.success_rate.toFixed(1) || 0}%
                    </div>
                    <p className="text-sm text-muted-foreground">성공률</p>
                  </div>
                  
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold">
                      {status?.operations_status.total_operations || 0}
                    </div>
                    <p className="text-sm text-muted-foreground">총 운영 수</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          {/* 알림 관리 */}
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  알림 관리
                </CardTitle>
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => clearAlerts('critical')}
                  >
                    Critical 정리
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => clearAlerts('warning')}
                  >
                    Warning 정리
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => clearAlerts()}
                  >
                    전체 정리
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {alerts.map((alert, index) => (
                  <Alert key={index} className={getAlertColor(alert.level)}>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-medium">{alert.title}</div>
                          <div className="text-sm">{alert.message}</div>
                        </div>
                        <Badge variant="outline" className="ml-2">
                          {alert.level}
                        </Badge>
                      </div>
                      <div className="text-xs mt-2">
                        {new Date(alert.timestamp).toLocaleString()}
                      </div>
                    </AlertDescription>
                  </Alert>
                ))}
                {alerts.length === 0 && (
                  <p className="text-muted-foreground text-center py-8">
                    알림이 없습니다
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          {/* 임계값 설정 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                임계값 설정
              </CardTitle>
              <CardDescription>
                시스템 모니터링을 위한 임계값을 설정합니다
              </CardDescription>
            </CardHeader>
            <CardContent>
              {thresholds && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium">최대 응답 시간 (초)</label>
                      <div className="flex gap-2 mt-1">
                        <input
                          type="number"
                          value={thresholds.max_response_time}
                          onChange={(e) => setThreshold('max_response_time', parseFloat(e.target.value))}
                          className="flex-1 px-3 py-2 border rounded-md"
                          step="0.1"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium">최대 메모리 사용량 (%)</label>
                      <div className="flex gap-2 mt-1">
                        <input
                          type="number"
                          value={thresholds.max_memory_usage}
                          onChange={(e) => setThreshold('max_memory_usage', parseFloat(e.target.value))}
                          className="flex-1 px-3 py-2 border rounded-md"
                          step="1"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium">최대 CPU 사용량 (%)</label>
                      <div className="flex gap-2 mt-1">
                        <input
                          type="number"
                          value={thresholds.max_cpu_usage}
                          onChange={(e) => setThreshold('max_cpu_usage', parseFloat(e.target.value))}
                          className="flex-1 px-3 py-2 border rounded-md"
                          step="1"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium">최대 에러율 (%)</label>
                      <div className="flex gap-2 mt-1">
                        <input
                          type="number"
                          value={thresholds.max_error_rate}
                          onChange={(e) => setThreshold('max_error_rate', parseFloat(e.target.value))}
                          className="flex-1 px-3 py-2 border rounded-md"
                          step="0.1"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium">최대 플러그인 로드 시간 (초)</label>
                      <div className="flex gap-2 mt-1">
                        <input
                          type="number"
                          value={thresholds.max_plugin_load_time}
                          onChange={(e) => setThreshold('max_plugin_load_time', parseFloat(e.target.value))}
                          className="flex-1 px-3 py-2 border rounded-md"
                          step="0.1"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 