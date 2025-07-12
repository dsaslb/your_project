"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiClient } from '@/lib/api-client';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Cpu,
  HardDrive,
  Network,
  Clock,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Settings,
  Zap,
  Database,
  Server
} from 'lucide-react';

interface PerformanceData {
  health?: any;
  metrics?: any;
  stats?: any;
  alerts?: any;
  apiStats?: any;
  cacheStats?: any;
  summary?: any;
}

const PerformanceDashboard: React.FC = () => {
  const [data, setData] = useState<PerformanceData>({});
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    fetchPerformanceData();
    
    if (autoRefresh) {
      const interval = setInterval(fetchPerformanceData, 30000); // 30초마다 갱신
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const fetchPerformanceData = async () => {
    try {
      setLoading(true);
      
      const endpoints = [
        '/api/performance/health',
        '/api/performance/metrics',
        '/api/performance/stats',
        '/api/performance/alerts',
        '/api/performance/api-stats',
        '/api/performance/cache-stats',
        '/api/performance/summary'
      ];

      const responses = await Promise.all(
        endpoints.map(endpoint => 
          apiClient.get(endpoint).catch(() => ({ success: false }))
        )
      );

      const performanceData: PerformanceData = {};
      
      if (responses[0].success) performanceData.health = responses[0].data;
      if (responses[1].success) performanceData.metrics = responses[1].data;
      if (responses[2].success) performanceData.stats = responses[2].data;
      if (responses[3].success) performanceData.alerts = responses[3].data;
      if (responses[4].success) performanceData.apiStats = responses[4].data;
      if (responses[5].success) performanceData.cacheStats = responses[5].data;
      if (responses[6].success) performanceData.summary = responses[6].data;

      setData(performanceData);
    } catch (error) {
      console.error('Performance data fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'critical':
        return <XCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Activity className="h-5 w-5 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600';
      case 'warning':
        return 'text-yellow-600';
      case 'critical':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getPerformanceLevelColor = (level: string) => {
    switch (level) {
      case 'good':
        return 'text-green-600';
      case 'fair':
        return 'text-yellow-600';
      case 'poor':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            성능 모니터링
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            시스템 성능 및 리소스 모니터링
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant={autoRefresh ? "default" : "outline"}
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
            자동 갱신 {autoRefresh ? 'ON' : 'OFF'}
          </Button>
          <Button onClick={fetchPerformanceData} variant="outline">
            <Activity className="h-4 w-4 mr-2" />
            새로고침
          </Button>
        </div>
      </div>

      {/* 시스템 상태 요약 */}
      {data.summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">시스템 상태</CardTitle>
              {getStatusIcon(data.summary.system_status)}
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${getStatusColor(data.summary.system_status)}`}>
                {data.summary.system_status === 'healthy' ? '정상' : 
                 data.summary.system_status === 'warning' ? '주의' : '위험'}
              </div>
              <p className="text-xs text-muted-foreground">
                성능 점수: {data.summary.performance_score}/100
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">활성 알림</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{data.summary.active_alerts}</div>
              <p className="text-xs text-muted-foreground">
                위험: {data.summary.critical_alerts} | 주의: {data.summary.warning_alerts}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">활성 요청</CardTitle>
              <Server className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{data.summary.system_stats.active_requests}</div>
              <p className="text-xs text-muted-foreground">
                총 요청: {data.summary.system_stats.total_requests}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">캐시 상태</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${data.summary.cache_status.connected ? 'text-green-600' : 'text-red-600'}`}>
                {data.summary.cache_status.connected ? '연결됨' : '연결 안됨'}
              </div>
              <p className="text-xs text-muted-foreground">
                타입: {data.summary.cache_status.cache_type}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 탭 네비게이션 */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="resources">리소스</TabsTrigger>
          <TabsTrigger value="apis">API 성능</TabsTrigger>
          <TabsTrigger value="alerts">알림</TabsTrigger>
          <TabsTrigger value="cache">캐시</TabsTrigger>
        </TabsList>

        {/* 개요 탭 */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 시스템 리소스 */}
            {data.stats && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Cpu className="h-5 w-5" />
                    시스템 리소스
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Cpu className="h-4 w-4" />
                        <span>CPU 사용률</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">{data.stats.cpu_usage}%</span>
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              data.stats.cpu_usage > 80 ? 'bg-red-600' :
                              data.stats.cpu_usage > 60 ? 'bg-yellow-600' : 'bg-green-600'
                            }`}
                            style={{ width: `${Math.min(data.stats.cpu_usage, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <HardDrive className="h-4 w-4" />
                        <span>디스크 사용률</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">{data.stats.disk_usage}%</span>
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              data.stats.disk_usage > 90 ? 'bg-red-600' :
                              data.stats.disk_usage > 80 ? 'bg-yellow-600' : 'bg-green-600'
                            }`}
                            style={{ width: `${Math.min(data.stats.disk_usage, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 성능 점수 */}
            {data.metrics && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    성능 점수
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center space-y-4">
                    <div className={`text-6xl font-bold ${
                      data.metrics.performance_score >= 80 ? 'text-green-600' :
                      data.metrics.performance_score >= 60 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {data.metrics.performance_score}
                    </div>
                    <div className="text-sm text-muted-foreground">/ 100</div>
                    
                    {data.metrics.recommendations && data.metrics.recommendations.length > 0 && (
                      <div className="text-left">
                        <h4 className="font-semibold mb-2">권장사항:</h4>
                        <ul className="text-sm space-y-1">
                          {data.metrics.recommendations.slice(0, 3).map((rec: string, index: number) => (
                            <li key={index} className="text-gray-600">• {rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* 리소스 탭 */}
        <TabsContent value="resources" className="space-y-6">
          {data.stats && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Cpu className="h-5 w-5" />
                    CPU 정보
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span>현재 사용률</span>
                      <span className="font-semibold">{data.stats.cpu_usage}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>활성 요청</span>
                      <span className="font-semibold">{data.stats.active_requests}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>총 요청</span>
                      <span className="font-semibold">{data.stats.total_requests}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <HardDrive className="h-5 w-5" />
                    디스크 정보
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span>사용률</span>
                      <span className="font-semibold">{data.stats.disk_usage}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>사용 가능</span>
                      <span className="font-semibold">{data.stats.disk_available_gb.toFixed(1)} GB</span>
                    </div>
                    <div className="flex justify-between">
                      <span>가동 시간</span>
                      <span className="font-semibold">{data.stats.uptime}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* API 성능 탭 */}
        <TabsContent value="apis" className="space-y-6">
          {data.apiStats && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  API 성능 분석
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">
                      총 {data.apiStats.total_apis}개 API, {data.apiStats.slow_apis}개 느린 API
                    </span>
                    <span className="text-sm text-muted-foreground">
                      총 {data.apiStats.total_calls}회 호출
                    </span>
                  </div>
                  
                  <div className="space-y-3">
                    {data.apiStats.api_stats.map((api: any, index: number) => (
                      <div key={index} className="border rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium">{api.endpoint}</span>
                          <Badge variant={
                            api.performance_level === 'good' ? 'default' :
                            api.performance_level === 'fair' ? 'secondary' : 'destructive'
                          }>
                            {api.performance_level === 'good' ? '좋음' :
                             api.performance_level === 'fair' ? '보통' : '나쁨'}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                          <div>
                            <span className="text-muted-foreground">호출 수:</span>
                            <span className="ml-1 font-semibold">{api.call_count}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">평균 응답:</span>
                            <span className={`ml-1 font-semibold ${getPerformanceLevelColor(api.performance_level)}`}>
                              {api.avg_response_time.toFixed(2)}s
                            </span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">최소:</span>
                            <span className="ml-1 font-semibold">{api.min_response_time.toFixed(2)}s</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">최대:</span>
                            <span className="ml-1 font-semibold">{api.max_response_time.toFixed(2)}s</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* 알림 탭 */}
        <TabsContent value="alerts" className="space-y-6">
          {data.alerts && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  성능 알림
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">
                      총 {data.alerts.count}개 알림
                    </span>
                    <div className="flex gap-2">
                      <Badge variant="destructive">
                        위험: {data.alerts.critical_count}
                      </Badge>
                      <Badge variant="secondary">
                        주의: {data.alerts.warning_count}
                      </Badge>
                    </div>
                  </div>
                  
                  {data.alerts.alerts.length > 0 ? (
                    <div className="space-y-3">
                      {data.alerts.alerts.map((alert: any, index: number) => (
                        <div key={index} className={`border rounded-lg p-3 ${
                          alert.severity === 'error' ? 'border-red-200 bg-red-50' :
                          alert.severity === 'warning' ? 'border-yellow-200 bg-yellow-50' :
                          'border-gray-200 bg-gray-50'
                        }`}>
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              {alert.severity === 'error' ? <XCircle className="h-4 w-4 text-red-600" /> :
                               alert.severity === 'warning' ? <AlertTriangle className="h-4 w-4 text-yellow-600" /> :
                               <Activity className="h-4 w-4 text-gray-600" />}
                              <span className="font-medium">{alert.type}</span>
                            </div>
                            <Badge variant={
                              alert.severity === 'error' ? 'destructive' :
                              alert.severity === 'warning' ? 'secondary' : 'default'
                            }>
                              {alert.severity === 'error' ? '위험' :
                               alert.severity === 'warning' ? '주의' : '정보'}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-700">{alert.message}</p>
                          {alert.value && (
                            <p className="text-xs text-gray-500 mt-1">
                              값: {alert.value} (임계값: {alert.threshold})
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-2" />
                      <p className="text-gray-600">현재 활성 알림이 없습니다.</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* 캐시 탭 */}
        <TabsContent value="cache" className="space-y-6">
          {data.cacheStats && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  캐시 상태
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>연결 상태</span>
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${
                        data.cacheStats.connected ? 'bg-green-500' : 'bg-red-500'
                      }`}></div>
                      <span className="font-semibold">
                        {data.cacheStats.connected ? '연결됨' : '연결 안됨'}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span>캐시 타입</span>
                    <span className="font-semibold">{data.cacheStats.cache_type}</span>
                  </div>
                  
                  {data.cacheStats.connected && (
                    <>
                      <div className="flex items-center justify-between">
                        <span>사용 메모리</span>
                        <span className="font-semibold">{data.cacheStats.used_memory}</span>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span>연결된 클라이언트</span>
                        <span className="font-semibold">{data.cacheStats.connected_clients}</span>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span>캐시 히트율</span>
                        <span className="font-semibold">
                          {data.cacheStats.keyspace_hits && data.cacheStats.keyspace_misses ?
                            `${((data.cacheStats.keyspace_hits / (data.cacheStats.keyspace_hits + data.cacheStats.keyspace_misses)) * 100).toFixed(1)}%` :
                            'N/A'}
                        </span>
                      </div>
                    </>
                  )}
                  
                  <div className="pt-4">
                    <Button 
                      onClick={async () => {
                        try {
                          await fetch('/api/performance/cache/clear', {
                            method: 'POST',
                            credentials: 'include',
                            headers: {
                              'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                              'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ pattern: '*' })
                          });
                          fetchPerformanceData();
                        } catch (error) {
                          console.error('Cache clear error:', error);
                        }
                      }}
                      variant="outline"
                      className="w-full"
                    >
                      <Zap className="h-4 w-4 mr-2" />
                      전체 캐시 삭제
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PerformanceDashboard; 