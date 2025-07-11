'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Activity, 
  Cpu, 
  HardDrive, 
  Clock, 
  AlertTriangle, 
  CheckCircle,
  Play,
  Square,
  RefreshCw
} from 'lucide-react';

interface PerformanceData {
  plugin_name: string;
  cpu_usage: number;
  memory_usage: number;
  response_time: number;
  status: 'healthy' | 'warning' | 'error';
  last_updated: string;
}

interface SystemMetrics {
  total_plugins: number;
  active_plugins: number;
  monitoring_active: boolean;
  alerts: Array<{
    plugin_name: string;
    type: string;
    message: string;
    severity: 'low' | 'medium' | 'high';
  }>;
}

export default function PluginPerformancePage() {
  const [performanceData, setPerformanceData] = useState<PerformanceData[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 성능 데이터 조회
  const fetchPerformanceData = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/plugins/performance');
      if (response.ok) {
        const data = await response.json();
        setPerformanceData(data.data || []);
      }
    } catch (err) {
      console.error('성능 데이터 조회 실패:', err);
    }
  };

  // 시스템 메트릭 조회
  const fetchSystemMetrics = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/plugins/status');
      if (response.ok) {
        const data = await response.json();
        setSystemMetrics(data.data || null);
      }
    } catch (err) {
      console.error('시스템 메트릭 조회 실패:', err);
    }
  };

  // 모니터링 시작
  const startMonitoring = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/plugins/monitoring/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        setIsMonitoring(true);
        fetchPerformanceData();
      }
    } catch (err) {
      setError('모니터링 시작 실패');
    }
  };

  // 모니터링 중지
  const stopMonitoring = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/plugins/monitoring/stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        setIsMonitoring(false);
      }
    } catch (err) {
      setError('모니터링 중지 실패');
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([
        fetchPerformanceData(),
        fetchSystemMetrics()
      ]);
      setLoading(false);
    };
    loadData();
  }, []);

  // 실시간 업데이트 (모니터링 활성화 시)
  useEffect(() => {
    if (!isMonitoring) return;

    const interval = setInterval(() => {
      fetchPerformanceData();
      fetchSystemMetrics();
    }, 5000); // 5초마다 업데이트

    return () => clearInterval(interval);
  }, [isMonitoring]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="w-4 h-4" />;
      case 'warning': return <AlertTriangle className="w-4 h-4" />;
      case 'error': return <AlertTriangle className="w-4 h-4 text-red-500" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin" />
        <span className="ml-2">데이터 로딩 중...</span>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">플러그인 성능 모니터링</h1>
        <div className="flex gap-2">
          <Button
            onClick={isMonitoring ? stopMonitoring : startMonitoring}
            variant={isMonitoring ? "destructive" : "default"}
          >
            {isMonitoring ? <Square className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
            {isMonitoring ? '모니터링 중지' : '모니터링 시작'}
          </Button>
          <Button onClick={fetchPerformanceData} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            새로고침
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 시스템 개요 */}
      {systemMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 플러그인</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{systemMetrics.total_plugins}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">활성 플러그인</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{systemMetrics.active_plugins}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">모니터링 상태</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <Badge variant={systemMetrics.monitoring_active ? "default" : "secondary"}>
                {systemMetrics.monitoring_active ? '활성' : '비활성'}
              </Badge>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">알림</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{systemMetrics.alerts?.length || 0}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 플러그인별 성능 데이터 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {performanceData.map((plugin) => (
          <Card key={plugin.plugin_name}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{plugin.plugin_name}</CardTitle>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${getStatusColor(plugin.status)}`} />
                  {getStatusIcon(plugin.status)}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* CPU 사용률 */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium flex items-center">
                    <Cpu className="w-4 h-4 mr-1" />
                    CPU 사용률
                  </span>
                  <span className="text-sm text-muted-foreground">{plugin.cpu_usage}%</span>
                </div>
                <Progress value={plugin.cpu_usage} className="h-2" />
              </div>

              {/* 메모리 사용률 */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium flex items-center">
                    <HardDrive className="w-4 h-4 mr-1" />
                    메모리 사용률
                  </span>
                  <span className="text-sm text-muted-foreground">{plugin.memory_usage}%</span>
                </div>
                <Progress value={plugin.memory_usage} className="h-2" />
              </div>

              {/* 응답 시간 */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium flex items-center">
                    <Clock className="w-4 h-4 mr-1" />
                    응답 시간
                  </span>
                  <span className="text-sm text-muted-foreground">{plugin.response_time}ms</span>
                </div>
                <div className="h-2 bg-gray-200 rounded">
                  <div 
                    className={`h-2 rounded ${
                      plugin.response_time < 100 ? 'bg-green-500' :
                      plugin.response_time < 500 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${Math.min(plugin.response_time / 10, 100)}%` }}
                  />
                </div>
              </div>

              <div className="text-xs text-muted-foreground">
                마지막 업데이트: {new Date(plugin.last_updated).toLocaleString()}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 알림 목록 */}
      {systemMetrics?.alerts && systemMetrics.alerts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2" />
              시스템 알림
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {systemMetrics.alerts.map((alert, index) => (
                <Alert key={index} variant={alert.severity === 'high' ? 'destructive' : 'default'}>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    <strong>{alert.plugin_name}</strong>: {alert.message}
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 