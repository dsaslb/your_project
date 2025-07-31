/**
 * 실시간 모니터링 대시보드
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Activity, 
  Cpu, 
  HardDrive, 
  Network, 
  Clock, 
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Download,
  Settings
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { useWebSocket } from '@/hooks/useWebSocket';

interface PerformanceMetric {
  timestamp: string;
  cpu_percent: number;
  memory_percent: number;
  memory_used: number;
  memory_available: number;
  disk_usage_percent: number;
  network_bytes_sent: number;
  network_bytes_recv: number;
  active_connections: number;
  request_count: number;
  response_time_avg: number;
  error_count: number;
}

interface CacheStats {
  l1_cache: {
    total_items: number;
    total_size: number;
    hit_count: number;
    miss_count: number;
    hit_rate: number;
    eviction_count: number;
    memory_usage: number;
  };
  l2_cache: {
    redis_info: {
      used_memory: number;
      used_memory_peak: number;
      connected_clients: number;
      total_commands_processed: number;
    };
    cache_stats: {
      hits: number;
      misses: number;
      errors: number;
      hit_rate: number;
    };
  };
  multi_cache: {
    overall: {
      l1_hits: number;
      l2_hits: number;
      misses: number;
      overall_hit_rate: number;
    };
  };
}

interface DatabaseStats {
  tables: Array<{
    name: string;
    row_count: number;
    size_bytes: number;
    fragmentation_percent: number;
  }>;
  total_size: number;
  index_count: number;
  optimization_needed: string[];
}

interface SystemHealth {
  status: 'healthy' | 'warning' | 'error';
  alerts: string[];
  recommendations: string[];
}

const MonitoringDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [currentMetric, setCurrentMetric] = useState<PerformanceMetric | null>(null);
  const [cacheStats, setCacheStats] = useState<CacheStats | null>(null);
  const [databaseStats, setDatabaseStats] = useState<DatabaseStats | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // WebSocket 연결
  const { status, connect, disconnect } = useWebSocket();

  // 메트릭 처리
  const handleNewMetric = useCallback((metric: PerformanceMetric) => {
    setCurrentMetric(metric);
    setMetrics(prev => {
      const newMetrics = [...prev, metric];
      // 최근 50개만 유지
      return newMetrics.slice(-50);
    });
    setLastUpdate(new Date());
  }, []);

  // 시스템 알림 처리
  const handleSystemAlert = useCallback((alert: any) => {
    setSystemHealth(prev => ({
      status: alert.severity === 'high' ? 'error' : 'warning',
      alerts: prev ? [...prev.alerts, alert.message] : [alert.message],
      recommendations: prev ? prev.recommendations : []
    }));
  }, []);

  // 데이터 로드
  const loadData = useCallback(async () => {
    try {
      setIsLoading(true);
      
      // 성능 메트릭 로드
      const metricsResponse = await fetch('/api/monitoring/metrics');
      if (metricsResponse.ok) {
        const metricsData = await metricsResponse.json();
        setMetrics(metricsData.metrics || []);
        if (metricsData.current) {
          setCurrentMetric(metricsData.current);
        }
      }

      // 캐시 통계 로드
      const cacheResponse = await fetch('/api/monitoring/cache-stats');
      if (cacheResponse.ok) {
        const cacheData = await cacheResponse.json();
        setCacheStats(cacheData);
      }

      // 데이터베이스 통계 로드
      const dbResponse = await fetch('/api/monitoring/database-stats');
      if (dbResponse.ok) {
        const dbData = await dbResponse.json();
        setDatabaseStats(dbData);
      }

      // 시스템 상태 로드
      const healthResponse = await fetch('/api/monitoring/health');
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        setSystemHealth(healthData);
      }

    } catch (error) {
      console.error('모니터링 데이터 로드 실패:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 초기 로드
  useEffect(() => {
    loadData();
    
    // 30초마다 데이터 새로고침
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [loadData]);

  // 실시간 업데이트 요청
  const requestRealTimeUpdates = useCallback(() => {
    if (status.connected) {
      // WebSocket 메시지 전송 로직
    }
  }, [status]);

  // 데이터 내보내기
  const exportData = useCallback(async () => {
    try {
      const data = {
        metrics,
        cacheStats,
        databaseStats,
        systemHealth,
        exportTime: new Date().toISOString()
      };

      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `monitoring-data-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('데이터 내보내기 실패:', error);
    }
  }, [metrics, cacheStats, databaseStats, systemHealth]);

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  // 성능 지표 카드
  const PerformanceCard: React.FC<{ title: string; value: number; unit: string; icon: React.ReactNode; color: string }> = ({ 
    title, value, unit, icon, color 
  }) => (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className={`p-2 rounded-full ${color}`}>
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value.toFixed(1)}{unit}</div>
      </CardContent>
    </Card>
  );

  // 차트 데이터 준비
  const chartData = metrics.map(metric => ({
    time: new Date(metric.timestamp).toLocaleTimeString(),
    cpu: metric.cpu_percent,
    memory: metric.memory_percent,
    disk: metric.disk_usage_percent,
    response_time: metric.response_time_avg
  }));

  const cachePieData = cacheStats ? [
    { name: 'L1 히트', value: cacheStats.multi_cache.overall.l1_hits, color: '#10b981' },
    { name: 'L2 히트', value: cacheStats.multi_cache.overall.l2_hits, color: '#3b82f6' },
    { name: '미스', value: cacheStats.multi_cache.overall.misses, color: '#ef4444' }
  ] : [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">모니터링 데이터 로드 중...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">시스템 모니터링</h1>
          <p className="text-muted-foreground">
            실시간 성능 모니터링 및 시스템 상태 대시보드
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant={status.connected ? "default" : "secondary"}>
            {status.connected ? "실시간 연결됨" : "연결 끊김"}
          </Badge>
          <Button variant="outline" size="sm" onClick={loadData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            새로고침
          </Button>
          <Button variant="outline" size="sm" onClick={requestRealTimeUpdates}>
            실시간 업데이트
          </Button>
          <Button variant="outline" size="sm" onClick={exportData}>
            <Download className="h-4 w-4 mr-2" />
            내보내기
          </Button>
        </div>
      </div>

      {/* 시스템 상태 알림 */}
      {systemHealth && systemHealth.alerts.length > 0 && (
        <Alert className={systemHealth.status === 'error' ? 'border-red-500' : 'border-yellow-500'}>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            {systemHealth.alerts[systemHealth.alerts.length - 1]}
          </AlertDescription>
        </Alert>
      )}

      {/* 실시간 성능 지표 */}
      {currentMetric && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <PerformanceCard
            title="CPU 사용률"
            value={currentMetric.cpu_percent}
            unit="%"
            icon={<Cpu className="h-4 w-4 text-white" />}
            color="bg-blue-500"
          />
          <PerformanceCard
            title="메모리 사용률"
            value={currentMetric.memory_percent}
            unit="%"
                          icon={<Activity className="h-4 w-4 text-white" />}
            color="bg-green-500"
          />
          <PerformanceCard
            title="디스크 사용률"
            value={currentMetric.disk_usage_percent}
            unit="%"
            icon={<HardDrive className="h-4 w-4 text-white" />}
            color="bg-purple-500"
          />
          <PerformanceCard
            title="평균 응답시간"
            value={currentMetric.response_time_avg}
            unit="ms"
            icon={<Clock className="h-4 w-4 text-white" />}
            color="bg-orange-500"
          />
        </div>
      )}

      {/* 상세 모니터링 탭 */}
      <Tabs defaultValue="performance" className="space-y-4">
        <TabsList>
          <TabsTrigger value="performance">성능 모니터링</TabsTrigger>
          <TabsTrigger value="cache">캐시 통계</TabsTrigger>
          <TabsTrigger value="database">데이터베이스</TabsTrigger>
          <TabsTrigger value="network">네트워크</TabsTrigger>
        </TabsList>

        {/* 성능 모니터링 탭 */}
        <TabsContent value="performance" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* CPU 사용률 차트 */}
            <Card>
              <CardHeader>
                <CardTitle>CPU 사용률 추이</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="cpu" stroke="#3b82f6" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* 메모리 사용률 차트 */}
            <Card>
              <CardHeader>
                <CardTitle>메모리 사용률 추이</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="memory" stroke="#10b981" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* 요청 통계 */}
          {currentMetric && (
            <Card>
              <CardHeader>
                <CardTitle>요청 통계</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">총 요청 수</p>
                    <p className="text-2xl font-bold">{currentMetric.request_count}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">활성 연결</p>
                    <p className="text-2xl font-bold">{currentMetric.active_connections}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">오류 수</p>
                    <p className="text-2xl font-bold text-red-500">{currentMetric.error_count}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* 캐시 통계 탭 */}
        <TabsContent value="cache" className="space-y-4">
          {cacheStats && (
            <>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* 캐시 히트율 차트 */}
                <Card>
                  <CardHeader>
                    <CardTitle>캐시 히트율 분포</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={cachePieData}
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          dataKey="value"
                          label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                        >
                          {cachePieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                {/* 캐시 통계 */}
                <Card>
                  <CardHeader>
                    <CardTitle>캐시 상세 통계</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm text-muted-foreground">전체 히트율</p>
                      <p className="text-2xl font-bold">
                        {cacheStats.multi_cache.overall.overall_hit_rate.toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">L1 캐시 아이템 수</p>
                      <p className="text-xl font-semibold">{cacheStats.l1_cache.total_items}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">L1 캐시 메모리 사용량</p>
                      <p className="text-xl font-semibold">
                        {(cacheStats.l1_cache.memory_usage / 1024 / 1024).toFixed(1)} MB
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Redis 연결 클라이언트</p>
                      <p className="text-xl font-semibold">
                        {cacheStats.l2_cache.redis_info.connected_clients}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* 캐시 성능 지표 */}
              <Card>
                <CardHeader>
                  <CardTitle>캐시 성능 지표</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">L1 히트율</p>
                      <Progress value={cacheStats.l1_cache.hit_rate} className="h-2" />
                      <p className="text-sm mt-1">{cacheStats.l1_cache.hit_rate.toFixed(1)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">L2 히트율</p>
                      <Progress value={cacheStats.l2_cache.cache_stats.hit_rate} className="h-2" />
                      <p className="text-sm mt-1">{cacheStats.l2_cache.cache_stats.hit_rate.toFixed(1)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">제거된 아이템</p>
                      <p className="text-xl font-semibold text-orange-500">
                        {cacheStats.l1_cache.eviction_count}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">Redis 오류</p>
                      <p className="text-xl font-semibold text-red-500">
                        {cacheStats.l2_cache.cache_stats.errors}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* 데이터베이스 탭 */}
        <TabsContent value="database" className="space-y-4">
          {databaseStats && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle>데이터베이스 개요</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm text-muted-foreground">총 테이블 수</p>
                        <p className="text-2xl font-bold">{databaseStats.tables.length}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">총 크기</p>
                        <p className="text-xl font-semibold">
                          {(databaseStats.total_size / 1024 / 1024).toFixed(1)} MB
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">총 인덱스 수</p>
                        <p className="text-xl font-semibold">{databaseStats.index_count}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>테이블별 크기</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={databaseStats.tables}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="size_bytes" fill="#3b82f6" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>최적화 필요 테이블</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {databaseStats.optimization_needed.length > 0 ? (
                      <div className="space-y-2">
                        {databaseStats.optimization_needed.map((table, index) => (
                          <Badge key={index} variant="destructive">
                            {table}
                          </Badge>
                        ))}
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2 text-green-600">
                        <CheckCircle className="h-4 w-4" />
                        <span>모든 테이블이 최적화되어 있습니다.</span>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* 테이블 상세 정보 */}
              <Card>
                <CardHeader>
                  <CardTitle>테이블 상세 정보</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr>
                          <th className="text-left p-2">테이블명</th>
                          <th className="text-left p-2">행 수</th>
                          <th className="text-left p-2">크기</th>
                          <th className="text-left p-2">조각화율</th>
                        </tr>
                      </thead>
                      <tbody>
                        {databaseStats.tables.map((table, index) => (
                          <tr key={index} className="border-t">
                            <td className="p-2 font-medium">{table.name}</td>
                            <td className="p-2">{table.row_count.toLocaleString()}</td>
                            <td className="p-2">{(table.size_bytes / 1024).toFixed(1)} KB</td>
                            <td className="p-2">
                              <Badge variant={table.fragmentation_percent > 10 ? "destructive" : "default"}>
                                {table.fragmentation_percent.toFixed(1)}%
                              </Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* 네트워크 탭 */}
        <TabsContent value="network" className="space-y-4">
          {currentMetric && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>네트워크 트래픽</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-muted-foreground">송신 속도</p>
                      <p className="text-2xl font-bold">
                        {(currentMetric.network_bytes_sent / 1024 / 1024).toFixed(2)} MB/s
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">수신 속도</p>
                      <p className="text-2xl font-bold">
                        {(currentMetric.network_bytes_recv / 1024 / 1024).toFixed(2)} MB/s
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>네트워크 사용량 추이</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="response_time" stroke="#8b5cf6" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* 마지막 업데이트 시간 */}
      <div className="text-center text-sm text-muted-foreground">
        마지막 업데이트: {lastUpdate.toLocaleString()}
      </div>
    </div>
  );
};

export default MonitoringDashboard; 