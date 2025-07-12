import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader, // pyright: ignore
  CardTitle, // pyright: ignore
} from '@/components/ui/card'; // pyright: ignore
import { Button } from '@/components/ui/button'; // pyright: ignore
import { Badge } from '@/components/ui/badge'; // pyright: ignore
import { Progress } from '@/components/ui/progress'; // pyright: ignore
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'; // pyright: ignore
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'; // pyright: ignore
import { Separator } from '@/components/ui/separator'; // pyright: ignore
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts'; // pyright: ignore
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Cpu,
  HardDrive,
  TrendingUp,
  TrendingDown,
  Minus,
  Play,
  Square,
  RefreshCw,
  BarChart3,
  Target,
  Zap,
  Shield,
  Gauge,
  Database,
  Server, // pyright: ignore
  Network, // pyright: ignore
} from 'lucide-react'; // pyright: ignore

interface PerformanceMetric {
  timestamp: string;
  metric_type: string;
  value: number;
  plugin_id?: string;
  component?: string;
  metadata?: Record<string, any>;
}

interface PerformanceAnalysis {
  analysis_id: string;
  timestamp: string;
  period: string;
  metrics_summary: Record<string, any>;
  bottlenecks: Array<{
    type: string;
    severity: 'critical' | 'warning';
    avg_value: number;
    threshold: number;
    description: string;
    suggestions: Array<{
      action: string;
      priority: string;
    }>;
  }>;
  recommendations: Array<{
    type: string;
    priority: string;
    title: string;
    description: string;
    actions: string[];
  }>;
  trends: Record<string, {
    slope: number;
    trend: 'increasing' | 'decreasing' | 'stable';
    change_rate: number;
    volatility: number;
  }>;
  health_score: number;
}

interface OptimizationSuggestion {
  type: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  actions: string[];
}

// 플러그인별 상세/알림 로그 샘플 데이터 (실제 API 연동 시 교체)
const samplePluginStats = [
  { name: 'pluginA', responseTime: 1.2, errorRate: 0.5, memory: 40, cpu: 30 },
  { name: 'pluginB', responseTime: 2.8, errorRate: 3.2, memory: 70, cpu: 60 },
  { name: 'pluginC', responseTime: 0.9, errorRate: 0.1, memory: 35, cpu: 20 },
];
const sampleAlertLogs = [
  { time: '2024-07-12 15:00', level: 'critical', message: 'pluginB 응답시간 임계치 초과' },
  { time: '2024-07-12 14:30', level: 'warning', message: 'pluginA 에러율 경고' },
];

const PerformanceAnalytics: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [analysis, setAnalysis] = useState<PerformanceAnalysis | null>(null);
  const [suggestions, setSuggestions] = useState<OptimizationSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  // API 호출 함수들
  const startAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/performance/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await response.json();
      
      if (data.success) {
        setIsRunning(true);
        setError(null);
      } else {
        setError(data.error || '분석 시스템 시작 실패');
      }
    } catch (err) {
      setError('분석 시스템 시작 중 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  }, []);

  const stopAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/performance/stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await response.json();
      
      if (data.success) {
        setIsRunning(false);
        setError(null);
      } else {
        setError(data.error || '분석 시스템 중지 실패');
      }
    } catch (err) {
      setError('분석 시스템 중지 중 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  }, []);

  const performAnalysis = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/performance/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ period_hours: 24 }),
      });
      const data = await response.json();
      
      if (data.success) {
        setAnalysis(data.data);
        setError(null);
      } else {
        setError(data.error || '성능 분석 실패');
      }
    } catch (err) {
      setError('성능 분석 중 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSuggestions = useCallback(async () => {
    try {
      const response = await fetch('/api/performance/suggestions');
      const data = await response.json();
      
      if (data.success) {
        setSuggestions(data.data.suggestions);
      }
    } catch (err) {
      console.error('최적화 제안사항 조회 실패:', err);
    }
  }, []);

  const fetchLatestReport = useCallback(async () => {
    try {
      const response = await fetch('/api/performance/report');
      const data = await response.json();
      
      if (data.success) {
        setAnalysis(data.data);
      }
    } catch (err) {
      console.error('최신 리포트 조회 실패:', err);
    }
  }, []);

  // 초기 데이터 로드
  useEffect(() => {
    fetchLatestReport();
    fetchSuggestions();
  }, [fetchLatestReport, fetchSuggestions]);

  // 실시간 폴링 추가
  useEffect(() => {
    fetchLatestReport();
    fetchSuggestions();
    const interval = setInterval(() => {
      fetchLatestReport();
      fetchSuggestions();
    }, 10000); // 10초마다 갱신
    return () => clearInterval(interval);
  }, [fetchLatestReport, fetchSuggestions]);

  // 건강도 점수에 따른 색상
  const getHealthScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getHealthScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  // 트렌드 아이콘
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return <TrendingUp className="w-4 h-4 text-red-500" />;
      case 'decreasing':
        return <TrendingDown className="w-4 h-4 text-green-500" />;
      default:
        return <Minus className="w-4 h-4 text-gray-500" />;
    }
  };

  // 우선순위에 따른 색상
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  // 차트 데이터 생성
  const generateChartData = () => {
    if (!analysis) return [];
    
    const metrics = analysis.metrics_summary;
    return [
      {
        name: '응답 시간',
        value: metrics.avg_response_time || 0,
        target: 2.0,
        unit: '초',
      },
      {
        name: '메모리 사용량',
        value: metrics.avg_memory_usage || 0,
        target: 80.0,
        unit: '%',
      },
      {
        name: 'CPU 사용량',
        value: metrics.avg_cpu_usage || 0,
        target: 85.0,
        unit: '%',
      },
      {
        name: '에러율',
        value: metrics.avg_error_rate || 0,
        target: 5.0,
        unit: '%',
      },
    ];
  };

  const chartData = generateChartData();

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">성능 분석 대시보드</h1>
          <p className="text-muted-foreground">
            운영 데이터 기반 성능 분석 및 최적화 제안
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant={isRunning ? "destructive" : "default"}
            onClick={isRunning ? stopAnalytics : startAnalytics}
            disabled={loading}
          >
            {isRunning ? <Square className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
            {isRunning ? '중지' : '시작'}
          </Button>
          <Button variant="outline" onClick={performAnalysis} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            분석 실행
          </Button>
        </div>
      </div>

      {/* 오류 메시지 */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>오류</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 메인 대시보드 */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="metrics">메트릭</TabsTrigger>
          <TabsTrigger value="bottlenecks">병목 지점</TabsTrigger>
          <TabsTrigger value="trends">트렌드</TabsTrigger>
          <TabsTrigger value="suggestions">최적화 제안</TabsTrigger>
        </TabsList>

        {/* 개요 탭 */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {/* 시스템 건강도 */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">시스템 건강도</CardTitle>
                <Gauge className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analysis?.health_score ? (
                    <span className={getHealthScoreColor(analysis.health_score)}>
                      {analysis.health_score.toFixed(1)}
                    </span>
                  ) : (
                    'N/A'
                  )}
                </div>
                <p className="text-xs text-muted-foreground">
                  {analysis?.health_score ? (
                    <span className={getHealthScoreColor(analysis.health_score)}>
                      {analysis.health_score >= 80 ? '양호' : 
                       analysis.health_score >= 60 ? '주의' : '위험'}
                    </span>
                  ) : (
                    '데이터 없음'
                  )}
                </p>
              </CardContent>
            </Card>

            {/* 평균 응답 시간 */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">평균 응답 시간</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analysis?.metrics_summary?.avg_response_time?.toFixed(2) || 'N/A'}초
                </div>
                <p className="text-xs text-muted-foreground">
                  목표: 2.0초 이하
                </p>
              </CardContent>
            </Card>

            {/* 메모리 사용량 */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">메모리 사용량</CardTitle>
                <HardDrive className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analysis?.metrics_summary?.avg_memory_usage?.toFixed(1) || 'N/A'}%
                </div>
                <p className="text-xs text-muted-foreground">
                  목표: 80% 이하
                </p>
              </CardContent>
            </Card>

            {/* CPU 사용량 */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">CPU 사용량</CardTitle>
                <Cpu className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analysis?.metrics_summary?.avg_cpu_usage?.toFixed(1) || 'N/A'}%
                </div>
                <p className="text-xs text-muted-foreground">
                  목표: 85% 이하
                </p>
              </CardContent>
            </Card>
          </div>

          {/* 성능 차트 */}
          <Card>
            <CardHeader>
              <CardTitle>성능 메트릭 비교</CardTitle>
              <CardDescription>
                주요 성능 지표와 목표값 비교
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value: number, name: string) => [
                      `${value}${name === 'value' ? '' : '초'}`,
                      name === 'value' ? '현재값' : '목표값'
                    ]}
                  />
                  <Legend />
                  <Bar dataKey="value" fill="#3b82f6" name="현재값" />
                  <Bar dataKey="target" fill="#ef4444" name="목표값" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* 최근 분석 정보 */}
          {analysis && (
            <Card>
              <CardHeader>
                <CardTitle>최근 분석 정보</CardTitle>
                <CardDescription>
                  분석 ID: {analysis.analysis_id}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium">분석 기간</p>
                    <p className="text-sm text-muted-foreground">{analysis.period}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium">분석 시간</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(analysis.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
                <Separator />
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm font-medium">병목 지점</p>
                    <p className="text-2xl font-bold text-red-600">
                      {analysis.bottlenecks.length}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium">권장사항</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {analysis.recommendations.length}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium">트렌드</p>
                    <p className="text-2xl font-bold text-green-600">
                      {Object.keys(analysis.trends).length}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* 메트릭 탭 */}
        <TabsContent value="metrics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>상세 메트릭</CardTitle>
              <CardDescription>
                성능 메트릭의 상세 통계 정보
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analysis?.metrics_summary ? (
                <div className="space-y-6">
                  {Object.entries(analysis.metrics_summary).map(([key, value]) => (
                    <div key={key} className="space-y-2">
                      <h3 className="text-lg font-semibold capitalize">
                        {key.replace(/_/g, ' ')}
                      </h3>
                      {typeof value === 'object' && value !== null ? (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          {Object.entries(value).map(([stat, val]) => (
                            <div key={stat} className="text-center">
                              <p className="text-sm text-muted-foreground capitalize">
                                {stat.replace(/_/g, ' ')}
                              </p>
                              <p className="text-lg font-semibold">
                                {typeof val === 'number' ? val.toFixed(2) : val}
                              </p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-lg">{value}</p>
                      )}
                      <Separator />
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-muted-foreground">
                  메트릭 데이터가 없습니다
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 병목 지점 탭 */}
        <TabsContent value="bottlenecks" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>병목 지점 분석</CardTitle>
              <CardDescription>
                성능 병목 지점과 해결 방안
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analysis?.bottlenecks && analysis.bottlenecks.length > 0 ? (
                <div className="space-y-4">
                  {analysis.bottlenecks.map((bottleneck, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg font-semibold capitalize">
                          {bottleneck.type.replace(/_/g, ' ')}
                        </h3>
                        <Badge 
                          variant={bottleneck.severity === 'critical' ? 'destructive' : 'secondary'}
                        >
                          {bottleneck.severity === 'critical' ? '심각' : '경고'}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">
                        {bottleneck.description}
                      </p>
                      <div className="grid grid-cols-2 gap-4 mb-3">
                        <div>
                          <p className="text-sm font-medium">평균값</p>
                          <p className="text-lg font-semibold">
                            {bottleneck.avg_value.toFixed(2)}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm font-medium">임계값</p>
                          <p className="text-lg font-semibold">
                            {bottleneck.threshold.toFixed(2)}
                          </p>
                        </div>
                      </div>
                      {bottleneck.suggestions && bottleneck.suggestions.length > 0 && (
                        <div>
                          <p className="text-sm font-medium mb-2">해결 방안:</p>
                          <ul className="space-y-1">
                            {bottleneck.suggestions.map((suggestion, idx) => (
                              <li key={idx} className="text-sm flex items-center space-x-2">
                                <Zap className="w-3 h-3 text-blue-500" />
                                <span>{suggestion.action}</span>
                                <Badge variant="outline" className="text-xs">
                                  {suggestion.priority}
                                </Badge>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-muted-foreground">
                  병목 지점이 발견되지 않았습니다
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 트렌드 탭 */}
        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>성능 트렌드 분석</CardTitle>
              <CardDescription>
                시간에 따른 성능 지표 변화 추이
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analysis?.trends && Object.keys(analysis.trends).length > 0 ? (
                <div className="space-y-4">
                  {Object.entries(analysis.trends).map(([metric, trend]) => (
                    <div key={metric} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-lg font-semibold capitalize">
                          {metric.replace(/_/g, ' ')}
                        </h3>
                        <div className="flex items-center space-x-2">
                          {getTrendIcon(trend.trend)}
                          <Badge variant="outline">
                            {trend.trend === 'increasing' ? '증가' : 
                             trend.trend === 'decreasing' ? '감소' : '안정'}
                          </Badge>
                        </div>
                      </div>
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <p className="text-sm text-muted-foreground">변화율</p>
                          <p className="text-lg font-semibold">
                            {trend.change_rate.toFixed(2)}%
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">기울기</p>
                          <p className="text-lg font-semibold">
                            {trend.slope.toFixed(4)}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">변동성</p>
                          <p className="text-lg font-semibold">
                            {trend.volatility.toFixed(2)}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-muted-foreground">
                  트렌드 데이터가 없습니다
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 최적화 제안 탭 */}
        <TabsContent value="suggestions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>최적화 제안사항</CardTitle>
              <CardDescription>
                성능 개선을 위한 구체적인 제안사항
              </CardDescription>
            </CardHeader>
            <CardContent>
              {suggestions.length > 0 ? (
                <div className="space-y-4">
                  {suggestions.map((suggestion, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg font-semibold">
                          {suggestion.type.replace(/_/g, ' ')}
                        </h3>
                        <Badge className={getPriorityColor(suggestion.priority)}>
                          {suggestion.priority === 'critical' ? '긴급' :
                           suggestion.priority === 'high' ? '높음' :
                           suggestion.priority === 'medium' ? '보통' : '낮음'}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">
                        {suggestion.description}
                      </p>
                      {suggestion.actions && suggestion.actions.length > 0 && (
                        <div>
                          <p className="text-sm font-medium mb-2">권장 조치:</p>
                          <ul className="space-y-1">
                            {suggestion.actions.map((action, idx) => (
                              <li key={idx} className="text-sm flex items-center space-x-2">
                                <Target className="w-3 h-3 text-green-500" />
                                <span>{action}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-muted-foreground">
                  최적화 제안사항이 없습니다
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 대시보드 내에 플러그인별 상세/알림 로그/필터링 UI 추가 */}
        <TabsContent value="plugins" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>플러그인별 상세 성능</CardTitle>
              <CardDescription>각 플러그인별 실시간 성능 지표</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {samplePluginStats.map((plugin) => (
                  <div key={plugin.name} className="border rounded-lg p-4">
                    <h3 className="font-bold mb-2">{plugin.name}</h3>
                    <div>응답시간: {plugin.responseTime}초</div>
                    <div>에러율: {plugin.errorRate}%</div>
                    <div>메모리: {plugin.memory}%</div>
                    <div>CPU: {plugin.cpu}%</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>알림/이벤트 로그</CardTitle>
              <CardDescription>최근 임계치 초과, 튜닝, 장애 이벤트</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {sampleAlertLogs.map((log, idx) => (
                  <li key={idx} className="flex items-center space-x-2">
                    <Badge variant={log.level === 'critical' ? 'destructive' : 'secondary'}>{log.level}</Badge>
                    <span className="text-xs text-muted-foreground">{log.time}</span>
                    <span>{log.message}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </TabsContent>
        {/* 필터링 UI 예시 (탭 상단에 추가) */}
        <div className="flex space-x-2 mb-2">
          <select className="border rounded px-2 py-1">
            <option>전체 플러그인</option>
            <option>pluginA</option>
            <option>pluginB</option>
            <option>pluginC</option>
          </select>
          <select className="border rounded px-2 py-1">
            <option>전체 기간</option>
            <option>최근 1시간</option>
            <option>오늘</option>
            <option>이번주</option>
          </select>
        </div>
      </Tabs>
    </div>
  );
};

export default PerformanceAnalytics; 