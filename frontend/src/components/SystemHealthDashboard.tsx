'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Activity, 
  Server, 
  Database, 
  HardDrive, 
  Cpu, 
  Activity as Memory, 
  Network, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  RefreshCw,
  Settings,
  BarChart3,
  Clock,
  Zap
} from 'lucide-react';

interface SystemHealth {
  overall_status: string;
  backend: {
    status: string;
    response_time: number;
    version?: string;
  };
  frontend: {
    status: string;
    response_time: number;
  };
  database: {
    status: string;
    total_size_mb: number;
    databases: Record<string, any>;
  };
  system_resources: {
    status: string;
    cpu_percent: number;
    memory_percent: number;
    disk_percent: number;
    memory_available_gb: number;
    disk_free_gb: number;
  };
  plugins: {
    status: string;
    plugin_count: number;
  };
  last_check: string;
  check_duration: number;
}

interface OptimizationResult {
  status: string;
  message: string;
  results?: {
    memory: any;
    temp_files: any;
  };
}

const SystemHealthDashboard: React.FC = () => {
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  const fetchSystemHealth = async () => {
    try {
              const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
        const response = await fetch(`${apiUrl}/api/system/health`);
      if (response.ok) {
        const data = await response.json();
        setSystemHealth(data);
        setLastUpdate(new Date().toLocaleString());
      }
    } catch (error) {
      console.error('시스템 상태 조회 실패:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const runOptimization = async () => {
    try {
      setRefreshing(true);
      const response = await fetch('/api/system/optimize', {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        setOptimizationResult(data);
        // 최적화 후 상태 다시 조회
        await fetchSystemHealth();
      }
    } catch (error) {
      console.error('최적화 실행 실패:', error);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchSystemHealth();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchSystemHealth, 30000); // 30초마다
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500';
      case 'warning':
        return 'bg-yellow-500';
      case 'unhealthy':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'unhealthy':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getResourceColor = (percent: number) => {
    if (percent < 50) return 'text-green-600';
    if (percent < 80) return 'text-yellow-600';
    return 'text-red-600';
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
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">시스템 상태 대시보드</h1>
          <p className="text-gray-600">실시간 시스템 모니터링 및 최적화</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={autoRefresh ? 'bg-green-50 border-green-200' : ''}
          >
            <Clock className="h-4 w-4 mr-2" />
            {autoRefresh ? '자동 새로고침 ON' : '자동 새로고침 OFF'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchSystemHealth}
            disabled={refreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            새로고침
          </Button>
          <Button
            onClick={runOptimization}
            disabled={refreshing}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Zap className="h-4 w-4 mr-2" />
            최적화 실행
          </Button>
        </div>
      </div>

      {/* 마지막 업데이트 */}
      {lastUpdate && (
        <div className="text-sm text-gray-500">
          마지막 업데이트: {lastUpdate}
        </div>
      )}

      {/* 최적화 결과 알림 */}
      {optimizationResult && (
        <Alert className={optimizationResult.status === 'success' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
          <AlertDescription>
            {optimizationResult.message}
          </AlertDescription>
        </Alert>
      )}

      {/* 전체 상태 */}
      {systemHealth && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Server className="h-5 w-5" />
              <span>전체 시스템 상태</span>
              {getStatusIcon(systemHealth.overall_status)}
              <Badge className={getStatusColor(systemHealth.overall_status)}>
                {systemHealth.overall_status === 'healthy' ? '정상' : 
                 systemHealth.overall_status === 'warning' ? '주의' : '문제'}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="overview">개요</TabsTrigger>
                <TabsTrigger value="servers">서버</TabsTrigger>
                <TabsTrigger value="resources">리소스</TabsTrigger>
                <TabsTrigger value="details">상세</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {/* 백엔드 서버 */}
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center space-x-2">
                        <Server className="h-4 w-4 text-blue-600" />
                        <span className="font-medium">백엔드</span>
                        {getStatusIcon(systemHealth.backend.status)}
                      </div>
                      <div className="mt-2">
                        <div className="text-sm text-gray-600">
                          응답시간: {systemHealth.backend.response_time}s
                        </div>
                        {systemHealth.backend.version && (
                          <div className="text-sm text-gray-600">
                            버전: {systemHealth.backend.version}
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  {/* 프론트엔드 서버 */}
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center space-x-2">
                        <Activity className="h-4 w-4 text-green-600" />
                        <span className="font-medium">프론트엔드</span>
                        {getStatusIcon(systemHealth.frontend.status)}
                      </div>
                      <div className="mt-2">
                        <div className="text-sm text-gray-600">
                          응답시간: {systemHealth.frontend.response_time}s
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* 데이터베이스 */}
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center space-x-2">
                        <Database className="h-4 w-4 text-purple-600" />
                        <span className="font-medium">데이터베이스</span>
                        {getStatusIcon(systemHealth.database.status)}
                      </div>
                      <div className="mt-2">
                        <div className="text-sm text-gray-600">
                          크기: {systemHealth.database.total_size_mb}MB
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* 플러그인 */}
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center space-x-2">
                        <Settings className="h-4 w-4 text-orange-600" />
                        <span className="font-medium">플러그인</span>
                        {getStatusIcon(systemHealth.plugins.status)}
                      </div>
                      <div className="mt-2">
                        <div className="text-sm text-gray-600">
                          개수: {systemHealth.plugins.plugin_count}개
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="servers" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* 백엔드 서버 상세 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <Server className="h-5 w-5" />
                        <span>백엔드 서버</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span>상태:</span>
                          <Badge className={getStatusColor(systemHealth.backend.status)}>
                            {systemHealth.backend.status === 'healthy' ? '정상' : '문제'}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>응답시간:</span>
                          <span className={getResourceColor(systemHealth.backend.response_time * 50)}>
                            {systemHealth.backend.response_time}s
                          </span>
                        </div>
                        {systemHealth.backend.version && (
                          <div className="flex justify-between">
                            <span>버전:</span>
                            <span>{systemHealth.backend.version}</span>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  {/* 프론트엔드 서버 상세 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <Activity className="h-5 w-5" />
                        <span>프론트엔드 서버</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span>상태:</span>
                          <Badge className={getStatusColor(systemHealth.frontend.status)}>
                            {systemHealth.frontend.status === 'healthy' ? '정상' : '문제'}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>응답시간:</span>
                          <span className={getResourceColor(systemHealth.frontend.response_time * 1000)}>
                            {systemHealth.frontend.response_time}s
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="resources" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* CPU 사용률 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <Cpu className="h-5 w-5" />
                        <span>CPU 사용률</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">현재 사용률</span>
                          <span className={`font-medium ${getResourceColor(systemHealth.system_resources.cpu_percent)}`}>
                            {systemHealth.system_resources.cpu_percent}%
                          </span>
                        </div>
                        <Progress value={systemHealth.system_resources.cpu_percent} className="h-2" />
                      </div>
                    </CardContent>
                  </Card>

                  {/* 메모리 사용률 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <Activity className="h-5 w-5" />
                        <span>메모리 사용률</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">현재 사용률</span>
                          <span className={`font-medium ${getResourceColor(systemHealth.system_resources.memory_percent)}`}>
                            {systemHealth.system_resources.memory_percent}%
                          </span>
                        </div>
                        <Progress value={systemHealth.system_resources.memory_percent} className="h-2" />
                        <div className="text-sm text-gray-600">
                          가용: {systemHealth.system_resources.memory_available_gb}GB
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* 디스크 사용률 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <HardDrive className="h-5 w-5" />
                        <span>디스크 사용률</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">현재 사용률</span>
                          <span className={`font-medium ${getResourceColor(systemHealth.system_resources.disk_percent)}`}>
                            {systemHealth.system_resources.disk_percent}%
                          </span>
                        </div>
                        <Progress value={systemHealth.system_resources.disk_percent} className="h-2" />
                        <div className="text-sm text-gray-600">
                          가용: {systemHealth.system_resources.disk_free_gb}GB
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="details" className="space-y-4">
                <div className="grid grid-cols-1 gap-4">
                  {/* 데이터베이스 상세 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <Database className="h-5 w-5" />
                        <span>데이터베이스 상세</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span>전체 크기:</span>
                          <span>{systemHealth.database.total_size_mb}MB</span>
                        </div>
                        <div className="flex justify-between">
                          <span>상태:</span>
                          <Badge className={getStatusColor(systemHealth.database.status)}>
                            {systemHealth.database.status === 'healthy' ? '정상' : '문제'}
                          </Badge>
                        </div>
                        <div>
                          <span className="text-sm font-medium">개별 데이터베이스:</span>
                          <div className="mt-2 space-y-1">
                            {Object.entries(systemHealth.database.databases).map(([name, info]: [string, any]) => (
                              <div key={name} className="flex justify-between text-sm">
                                <span className="text-gray-600">{name}:</span>
                                <span>{info.size_mb}MB ({info.table_count}개 테이블)</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* 시스템 정보 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <BarChart3 className="h-5 w-5" />
                        <span>시스템 정보</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>마지막 점검:</span>
                          <span>{new Date(systemHealth.last_check).toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>점검 소요시간:</span>
                          <span>{systemHealth.check_duration}초</span>
                        </div>
                        <div className="flex justify-between">
                          <span>플러그인 개수:</span>
                          <span>{systemHealth.plugins.plugin_count}개</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SystemHealthDashboard; 