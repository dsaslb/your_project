// @ts-nocheck
"use client";

import React, { useState, useEffect, useRef } from 'react'; // @ts-ignore
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AlertTriangle, Activity, Cpu, Memory, Clock, AlertCircle, CheckCircle, XCircle, TrendingUp, TrendingDown, Minus, Download, BarChart3 } from 'lucide-react'; // @ts-ignore
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, AreaChart, Area, PieChart, Pie, Cell } from 'recharts'; // @ts-ignore

interface DetailedMetrics {
  timestamp: string;
  cpu_usage: number;
  memory_usage: number;
  memory_rss: number;
  memory_vms: number;
  response_time_p50: number;
  response_time_p95: number;
  response_time_p99: number;
  error_rate: number;
  throughput: number;
  active_connections: number;
  total_connections: number;
  disk_read_bytes: number;
  disk_write_bytes: number;
  network_rx_bytes: number;
  network_tx_bytes: number;
}

interface PerformanceTrend {
  current_value: number;
  change_percent: number;
  trend_direction: string;
  trend_strength: string;
}

interface UsagePattern {
  peak_hours: number[];
  low_usage_hours: number[];
  daily_usage_pattern: Record<string, number>;
}

interface AnalyticsData {
  metrics: DetailedMetrics[];
  trends: Record<string, PerformanceTrend>;
  patterns: UsagePattern | null;
  statistics: {
    cpu: { average: number; max: number; min: number; current: number };
    memory: { average: number; max: number; min: number; current: number };
    response_time: { average: number; max: number; min: number; current: number };
    error_rate: { average: number; max: number; min: number; current: number };
  };
}

const AdvancedMonitoringPage: React.FC = () => {
  const [selectedPlugin, setSelectedPlugin] = useState<string>('');
  const [timeRange, setTimeRange] = useState<number>(24);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [plugins, setPlugins] = useState<string[]>([]);

  // 데이터 로드
  const loadAnalyticsData = async (pluginId: string, hours: number) => {
    if (!pluginId) return;
    
    setLoading(true);
    try {
      const response = await fetch(`/api/advanced-monitoring/analytics/${pluginId}?hours=${hours}`);
      const data = await response.json();
      
      if (data.success) {
        setAnalyticsData(data.analytics);
      } else {
        console.error('분석 데이터 로드 실패:', data.error);
      }
    } catch (error) {
      console.error('분석 데이터 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  // 플러그인 목록 로드
  const loadPlugins = async () => {
    try {
      const response = await fetch('/api/advanced-monitoring/status');
      const data = await response.json();
      
      if (data.success) {
        // 실제로는 플러그인 목록 API가 필요하지만, 임시로 샘플 데이터 사용
        setPlugins(['analytics_plugin', 'notification_plugin', 'reporting_plugin', 'security_plugin', 'backup_plugin']);
      }
    } catch (error) {
      console.error('플러그인 목록 로드 오류:', error);
    }
  };

  // 데이터 내보내기
  const exportData = async (format: 'json' | 'csv') => {
    if (!selectedPlugin) return;
    
    try {
      const response = await fetch(`/api/advanced-monitoring/export/${selectedPlugin}?hours=${timeRange}&format=${format}`);
      
      if (format === 'csv') {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${selectedPlugin}_metrics.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        const data = await response.json();
        if (data.success) {
          const blob = new Blob([JSON.stringify(data.data, null, 2)], { type: 'application/json' });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${selectedPlugin}_metrics.json`;
          a.click();
          window.URL.revokeObjectURL(url);
        }
      }
    } catch (error) {
      console.error('데이터 내보내기 오류:', error);
    }
  };

  // 트렌드 아이콘 반환
  const getTrendIcon = (direction: string, strength: string) => {
    const color = direction === 'up' ? 'text-red-500' : direction === 'down' ? 'text-green-500' : 'text-gray-500';
    const size = strength === 'strong' ? 'h-5 w-5' : 'h-4 w-4';
    
    if (direction === 'up') return <TrendingUp className={`${size} ${color}`} />;
    if (direction === 'down') return <TrendingDown className={`${size} ${color}`} />;
    return <Minus className={`${size} ${color}`} />;
  };

  // 트렌드 색상 반환
  const getTrendColor = (direction: string) => {
    switch (direction) {
      case 'up': return 'text-red-600';
      case 'down': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  // 초기화
  useEffect(() => {
    loadPlugins();
  }, []);

  // 플러그인 선택 시 데이터 로드
  useEffect(() => {
    if (selectedPlugin) {
      loadAnalyticsData(selectedPlugin, timeRange);
    }
  }, [selectedPlugin, timeRange]);

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">고급 플러그인 모니터링</h1>
          <p className="text-gray-600 dark:text-gray-400">
            상세 메트릭, 트렌드 분석, 사용량 패턴 분석
          </p>
        </div>
        
        {/* 컨트롤 */}
        <div className="flex items-center gap-4">
          <Select value={selectedPlugin} onValueChange={setSelectedPlugin}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="플러그인 선택" />
            </SelectTrigger>
            <SelectContent>
              {plugins.map((plugin) => (
                <SelectItem key={plugin} value={plugin}>
                  {plugin.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Select value={timeRange.toString()} onValueChange={(value) => setTimeRange(Number(value))}>
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
          
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => exportData('json')}>
              <Download className="h-4 w-4 mr-2" />
              JSON
            </Button>
            <Button variant="outline" size="sm" onClick={() => exportData('csv')}>
              <Download className="h-4 w-4 mr-2" />
              CSV
            </Button>
          </div>
        </div>
      </div>

      {!selectedPlugin ? (
        <Card>
          <CardContent className="flex items-center justify-center h-64">
            <div className="text-center">
              <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">분석할 플러그인을 선택해주세요.</p>
            </div>
          </CardContent>
        </Card>
      ) : loading ? (
        <Card>
          <CardContent className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-500">데이터를 로드하는 중...</p>
            </div>
          </CardContent>
        </Card>
      ) : analyticsData ? (
        <>
          {/* 통계 요약 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">CPU 사용률</CardTitle>
                <Cpu className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analyticsData.statistics.cpu.current.toFixed(1)}%</div>
                <div className="flex items-center text-xs text-muted-foreground">
                  평균: {analyticsData.statistics.cpu.average.toFixed(1)}%
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">메모리 사용률</CardTitle>
                <Memory className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analyticsData.statistics.memory.current.toFixed(1)}%</div>
                <div className="flex items-center text-xs text-muted-foreground">
                  평균: {analyticsData.statistics.memory.average.toFixed(1)}%
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">응답 시간 (P95)</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analyticsData.statistics.response_time.current.toFixed(2)}s</div>
                <div className="flex items-center text-xs text-muted-foreground">
                  평균: {analyticsData.statistics.response_time.average.toFixed(2)}s
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">에러율</CardTitle>
                <AlertCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analyticsData.statistics.error_rate.current.toFixed(2)}%</div>
                <div className="flex items-center text-xs text-muted-foreground">
                  평균: {analyticsData.statistics.error_rate.average.toFixed(2)}%
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 메인 콘텐츠 */}
          <Tabs defaultValue="metrics" className="space-y-4">
            <TabsList>
              <TabsTrigger value="metrics">실시간 메트릭</TabsTrigger>
              <TabsTrigger value="trends">성능 트렌드</TabsTrigger>
              <TabsTrigger value="patterns">사용량 패턴</TabsTrigger>
              <TabsTrigger value="analytics">종합 분석</TabsTrigger>
            </TabsList>

            <TabsContent value="metrics" className="space-y-4">
              {/* 실시간 메트릭 차트 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>CPU & 메모리 사용률</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={analyticsData.metrics}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="timestamp" 
                          tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                        />
                        <YAxis />
                        <Tooltip 
                          labelFormatter={(value) => new Date(value).toLocaleString()}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="cpu_usage" 
                          stroke="#3b82f6" 
                          strokeWidth={2}
                          name="CPU 사용률"
                        />
                        <Line 
                          type="monotone" 
                          dataKey="memory_usage" 
                          stroke="#10b981" 
                          strokeWidth={2}
                          name="메모리 사용률"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>응답 시간 분포</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={analyticsData.metrics}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="timestamp" 
                          tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                        />
                        <YAxis />
                        <Tooltip 
                          labelFormatter={(value) => new Date(value).toLocaleString()}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="response_time_p50" 
                          stroke="#3b82f6" 
                          strokeWidth={2}
                          name="P50"
                        />
                        <Line 
                          type="monotone" 
                          dataKey="response_time_p95" 
                          stroke="#f59e0b" 
                          strokeWidth={2}
                          name="P95"
                        />
                        <Line 
                          type="monotone" 
                          dataKey="response_time_p99" 
                          stroke="#ef4444" 
                          strokeWidth={2}
                          name="P99"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>네트워크 I/O</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={analyticsData.metrics}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="timestamp" 
                          tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                        />
                        <YAxis />
                        <Tooltip 
                          labelFormatter={(value) => new Date(value).toLocaleString()}
                        />
                        <Area 
                          type="monotone" 
                          dataKey="network_rx_bytes" 
                          stackId="1"
                          stroke="#3b82f6" 
                          fill="#3b82f6" 
                          fillOpacity={0.6}
                          name="수신"
                        />
                        <Area 
                          type="monotone" 
                          dataKey="network_tx_bytes" 
                          stackId="1"
                          stroke="#10b981" 
                          fill="#10b981" 
                          fillOpacity={0.6}
                          name="송신"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>디스크 I/O</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={analyticsData.metrics}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="timestamp" 
                          tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                        />
                        <YAxis />
                        <Tooltip 
                          labelFormatter={(value) => new Date(value).toLocaleString()}
                        />
                        <Area 
                          type="monotone" 
                          dataKey="disk_read_bytes" 
                          stackId="1"
                          stroke="#8b5cf6" 
                          fill="#8b5cf6" 
                          fillOpacity={0.6}
                          name="읽기"
                        />
                        <Area 
                          type="monotone" 
                          dataKey="disk_write_bytes" 
                          stackId="1"
                          stroke="#f59e0b" 
                          fill="#f59e0b" 
                          fillOpacity={0.6}
                          name="쓰기"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="trends" className="space-y-4">
              {/* 성능 트렌드 */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(analyticsData.trends).map(([metricType, trend]) => (
                  <Card key={metricType}>
                    <CardHeader>
                      <CardTitle className="text-lg flex items-center gap-2">
                        {getTrendIcon(trend.trend_direction, trend.trend_strength)}
                        {metricType === 'cpu' ? 'CPU 사용률' :
                         metricType === 'memory' ? '메모리 사용률' :
                         metricType === 'response_time' ? '응답 시간' :
                         metricType === 'error_rate' ? '에러율' :
                         metricType === 'throughput' ? '처리량' : metricType}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold mb-2">
                        {trend.current_value.toFixed(2)}
                        {metricType.includes('rate') || metricType.includes('usage') ? '%' : 
                         metricType.includes('time') ? 's' : ''}
                      </div>
                      <div className={`text-sm font-medium ${getTrendColor(trend.trend_direction)}`}>
                        {trend.change_percent > 0 ? '+' : ''}{trend.change_percent.toFixed(1)}%
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {trend.trend_direction === 'up' ? '증가' : 
                         trend.trend_direction === 'down' ? '감소' : '안정'}
                        {' '}({trend.trend_strength === 'strong' ? '강함' : 
                              trend.trend_strength === 'moderate' ? '보통' : '약함'})
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="patterns" className="space-y-4">
              {/* 사용량 패턴 */}
              {analyticsData.patterns && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>시간대별 사용량 패턴</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div>
                          <h4 className="text-sm font-medium mb-2">피크 시간</h4>
                          <div className="flex flex-wrap gap-2">
                            {analyticsData.patterns.peak_hours.map((hour) => (
                              <Badge key={hour} variant="destructive">
                                {hour}시
                              </Badge>
                            ))}
                          </div>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium mb-2">저사용 시간</h4>
                          <div className="flex flex-wrap gap-2">
                            {analyticsData.patterns.low_usage_hours.map((hour) => (
                              <Badge key={hour} variant="secondary">
                                {hour}시
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>일별 사용량 패턴</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={Object.entries(analyticsData.patterns.daily_usage_pattern).map(([day, value]) => ({
                          day: day.slice(0, 3),
                          usage: value
                        }))}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="day" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="usage" fill="#3b82f6" />
                        </BarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </div>
              )}
            </TabsContent>

            <TabsContent value="analytics" className="space-y-4">
              {/* 종합 분석 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>성능 통계 요약</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {Object.entries(analyticsData.statistics).map(([metric, stats]) => (
                        <div key={metric}>
                          <h4 className="text-sm font-medium mb-2 capitalize">
                            {metric === 'cpu' ? 'CPU 사용률' :
                             metric === 'memory' ? '메모리 사용률' :
                             metric === 'response_time' ? '응답 시간' :
                             metric === 'error_rate' ? '에러율' : metric}
                          </h4>
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="text-gray-500">현재:</span>
                              <span className="ml-2 font-medium">
                                {stats.current.toFixed(2)}
                                {metric.includes('rate') || metric.includes('usage') ? '%' : 
                                 metric.includes('time') ? 's' : ''}
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-500">평균:</span>
                              <span className="ml-2 font-medium">
                                {stats.average.toFixed(2)}
                                {metric.includes('rate') || metric.includes('usage') ? '%' : 
                                 metric.includes('time') ? 's' : ''}
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-500">최대:</span>
                              <span className="ml-2 font-medium">
                                {stats.max.toFixed(2)}
                                {metric.includes('rate') || metric.includes('usage') ? '%' : 
                                 metric.includes('time') ? 's' : ''}
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-500">최소:</span>
                              <span className="ml-2 font-medium">
                                {stats.min.toFixed(2)}
                                {metric.includes('rate') || metric.includes('usage') ? '%' : 
                                 metric.includes('time') ? 's' : ''}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>성능 권장사항</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {analyticsData.statistics.cpu.current > 80 && (
                        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                          <div className="flex items-center gap-2">
                            <AlertTriangle className="h-4 w-4 text-red-600" />
                            <span className="text-sm font-medium text-red-800">CPU 사용률이 높습니다</span>
                          </div>
                          <p className="text-xs text-red-600 mt-1">
                            현재 CPU 사용률이 {analyticsData.statistics.cpu.current.toFixed(1)}%로 높습니다. 
                            리소스 사용량을 최적화하거나 스케일링을 고려해보세요.
                          </p>
                        </div>
                      )}
                      
                      {analyticsData.statistics.memory.current > 85 && (
                        <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                          <div className="flex items-center gap-2">
                            <AlertTriangle className="h-4 w-4 text-orange-600" />
                            <span className="text-sm font-medium text-orange-800">메모리 사용률이 높습니다</span>
                          </div>
                          <p className="text-xs text-orange-600 mt-1">
                            현재 메모리 사용률이 {analyticsData.statistics.memory.current.toFixed(1)}%로 높습니다. 
                            메모리 누수를 확인하거나 메모리 할당을 늘려보세요.
                          </p>
                        </div>
                      )}
                      
                      {analyticsData.statistics.error_rate.current > 5 && (
                        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                          <div className="flex items-center gap-2">
                            <AlertCircle className="h-4 w-4 text-red-600" />
                            <span className="text-sm font-medium text-red-800">에러율이 높습니다</span>
                          </div>
                          <p className="text-xs text-red-600 mt-1">
                            현재 에러율이 {analyticsData.statistics.error_rate.current.toFixed(2)}%로 높습니다. 
                            로그를 확인하여 오류 원인을 파악하세요.
                          </p>
                        </div>
                      )}
                      
                      {analyticsData.statistics.response_time.current > 2 && (
                        <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-yellow-600" />
                            <span className="text-sm font-medium text-yellow-800">응답 시간이 느립니다</span>
                          </div>
                          <p className="text-xs text-yellow-600 mt-1">
                            현재 응답 시간이 {analyticsData.statistics.response_time.current.toFixed(2)}초로 느립니다. 
                            성능 최적화를 고려해보세요.
                          </p>
                        </div>
                      )}
                      
                      {analyticsData.statistics.cpu.current <= 50 && 
                       analyticsData.statistics.memory.current <= 70 && 
                       analyticsData.statistics.error_rate.current <= 1 && (
                        <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                          <div className="flex items-center gap-2">
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            <span className="text-sm font-medium text-green-800">성능이 양호합니다</span>
                          </div>
                          <p className="text-xs text-green-600 mt-1">
                            모든 주요 메트릭이 정상 범위 내에 있습니다. 
                            현재 성능 상태가 양호합니다.
                          </p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </>
      ) : (
        <Card>
          <CardContent className="flex items-center justify-center h-64">
            <div className="text-center">
              <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">데이터를 불러올 수 없습니다.</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AdvancedMonitoringPage; 