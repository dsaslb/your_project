'use client';

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
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
} from 'recharts';
import {
  Activity,
  TrendingUp,
  AlertTriangle,
  Lightbulb,
  Download,
  RefreshCw,
  Brain,
  Target,
  Zap,
  Shield,
  BarChart3,
  Clock,
} from 'lucide-react';

interface PluginMetrics {
  plugin_id: string;
  timestamp: string;
  cpu_usage: number;
  memory_usage: number;
  response_time: number;
  error_rate: number;
  request_count: number;
  active_users: number;
  uptime: number;
}

interface PredictionResult {
  prediction_type: string;
  predicted_value: number;
  confidence: number;
  timestamp: string;
  factors: Record<string, any>;
}

interface AnomalyDetection {
  anomaly_type: string;
  severity: string;
  detected_at: string;
  description: string;
  recommendations: string[];
}

interface OptimizationSuggestion {
  suggestion_type: string;
  priority: string;
  description: string;
  expected_improvement: number;
  implementation_steps: string[];
}

interface AnalyticsSummary {
  plugin_id: string;
  total_metrics: number;
  analysis_period: string;
  current_status: string;
  performance_metrics: {
    avg_cpu_usage: number;
    avg_memory_usage: number;
    avg_response_time: number;
    avg_error_rate: number;
    total_requests: number;
    avg_uptime: number;
  };
  trends: {
    cpu_trend: string;
    memory_trend: string;
    response_trend: string;
    error_trend: string;
  };
  predictions_count: number;
  anomalies_count: number;
  suggestions_count: number;
  last_updated: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export default function PluginAIAnalyticsDashboard() {
  const [selectedPlugin, setSelectedPlugin] = useState<string>('');
  const [plugins, setPlugins] = useState<string[]>([]);
  const [metrics, setMetrics] = useState<PluginMetrics[]>([]);
  const [predictions, setPredictions] = useState<PredictionResult[]>([]);
  const [anomalies, setAnomalies] = useState<AnomalyDetection[]>([]);
  const [suggestions, setSuggestions] = useState<OptimizationSuggestion[]>([]);
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  // 플러그인 목록 로드
  useEffect(() => {
    loadPlugins();
  }, []);

  // 선택된 플러그인 변경 시 데이터 로드
  useEffect(() => {
    if (selectedPlugin) {
      loadAnalyticsData();
    }
  }, [selectedPlugin]);

  const loadPlugins = async () => {
    try {
      const response = await fetch('/api/plugins/list');
      const data = await response.json();
      if (data.success) {
        const pluginIds = data.plugins.map((p: any) => p.id);
        setPlugins(pluginIds);
        if (pluginIds.length > 0) {
          setSelectedPlugin(pluginIds[0]);
        }
      }
    } catch (error) {
      console.error('플러그인 목록 로드 실패:', error);
      setError('플러그인 목록을 불러올 수 없습니다.');
    }
  };

  const loadAnalyticsData = async () => {
    if (!selectedPlugin) return;

    setLoading(true);
    setError('');

    try {
      // 메트릭 수집
      await fetch(`/api/plugin-ai-analytics/collect-metrics/${selectedPlugin}`, {
        method: 'POST',
      });

      // 모델 학습
      await fetch(`/api/plugin-ai-analytics/train-models/${selectedPlugin}`, {
        method: 'POST',
      });

      // 성능 예측
      const predictionsResponse = await fetch(
        `/api/plugin-ai-analytics/predict/${selectedPlugin}`
      );
      const predictionsData = await predictionsResponse.json();
      if (predictionsData.success) {
        setPredictions(predictionsData.data.predictions);
      }

      // 이상 탐지
      const anomaliesResponse = await fetch(
        `/api/plugin-ai-analytics/detect-anomalies/${selectedPlugin}`
      );
      const anomaliesData = await anomaliesResponse.json();
      if (anomaliesData.success) {
        setAnomalies(anomaliesData.data.anomalies);
      }

      // 최적화 제안
      const suggestionsResponse = await fetch(
        `/api/plugin-ai-analytics/optimization-suggestions/${selectedPlugin}`
      );
      const suggestionsData = await suggestionsResponse.json();
      if (suggestionsData.success) {
        setSuggestions(suggestionsData.data.suggestions);
      }

      // 분석 요약
      const summaryResponse = await fetch(
        `/api/plugin-ai-analytics/analytics-summary/${selectedPlugin}`
      );
      const summaryData = await summaryResponse.json();
      if (summaryData.success) {
        setSummary(summaryData.data);
      }

      // 메트릭 히스토리
      const metricsResponse = await fetch(
        `/api/plugin-ai-analytics/metrics-history/${selectedPlugin}?hours=168`
      );
      const metricsData = await metricsResponse.json();
      if (metricsData.success) {
        setMetrics(metricsData.data.metrics);
      }
    } catch (error) {
      console.error('분석 데이터 로드 실패:', error);
      setError('분석 데이터를 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  const exportData = async () => {
    if (!selectedPlugin) return;

    try {
      const response = await fetch(
        `/api/plugin-ai-analytics/export-data/${selectedPlugin}?format=json`
      );
      const data = await response.json();
      if (data.success) {
        // 파일 다운로드 시뮬레이션
        const link = document.createElement('a');
        link.href = data.data.filepath;
        link.download = `analytics_${selectedPlugin}.json`;
        link.click();
      }
    } catch (error) {
      console.error('데이터 내보내기 실패:', error);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'destructive';
      case 'medium':
        return 'secondary';
      case 'low':
        return 'default';
      default:
        return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high':
        return 'destructive';
      case 'medium':
        return 'secondary';
      case 'low':
        return 'default';
      default:
        return 'default';
    }
  };

  const formatChartData = (metrics: PluginMetrics[]) => {
    return metrics.map((metric) => ({
      time: new Date(metric.timestamp).toLocaleTimeString(),
      cpu: metric.cpu_usage,
      memory: metric.memory_usage,
      response: metric.response_time,
      error: metric.error_rate,
    }));
  };

  const formatPredictionsData = (predictions: PredictionResult[]) => {
    return predictions.map((pred) => ({
      type: pred.prediction_type,
      value: pred.predicted_value,
      confidence: pred.confidence,
    }));
  };

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Brain className="h-8 w-8 text-blue-600" />
            플러그인 AI 분석 대시보드
          </h1>
          <p className="text-muted-foreground">
            AI 기반 성능 예측, 이상 탐지, 최적화 제안
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={loadAnalyticsData} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            새로고침
          </Button>
          <Button onClick={exportData} variant="outline">
            <Download className="h-4 w-4 mr-2" />
            내보내기
          </Button>
        </div>
      </div>

      {/* 플러그인 선택 */}
      <Card>
        <CardHeader>
          <CardTitle>분석 대상 플러그인</CardTitle>
        </CardHeader>
        <CardContent>
          <select
            value={selectedPlugin}
            onChange={(e) => setSelectedPlugin(e.target.value)}
            className="w-full p-2 border rounded-md"
          >
            {plugins.map((plugin) => (
              <option key={plugin} value={plugin}>
                {plugin}
              </option>
            ))}
          </select>
        </CardContent>
      </Card>

      {selectedPlugin && (
        <>
          {/* 요약 정보 */}
          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">총 메트릭</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{summary.total_metrics}</div>
                  <p className="text-xs text-muted-foreground">
                    분석 기간: {summary.analysis_period}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">예측 수</CardTitle>
                  <Target className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{summary.predictions_count}</div>
                  <p className="text-xs text-muted-foreground">
                    AI 모델 기반
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">이상 탐지</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{summary.anomalies_count}</div>
                  <p className="text-xs text-muted-foreground">
                    자동 감지됨
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">최적화 제안</CardTitle>
                  <Lightbulb className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{summary.suggestions_count}</div>
                  <p className="text-xs text-muted-foreground">
                    AI 제안
                  </p>
                </CardContent>
              </Card>
            </div>
          )}

          {/* 성능 메트릭 */}
          {summary && (
            <Card>
              <CardHeader>
                <CardTitle>성능 메트릭</CardTitle>
                <CardDescription>
                  평균 성능 지표 및 트렌드
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">CPU 사용률</span>
                      <span className="text-sm text-muted-foreground">
                        {summary.performance_metrics.avg_cpu_usage.toFixed(1)}%
                      </span>
                    </div>
                    <Progress value={summary.performance_metrics.avg_cpu_usage} />
                    <Badge variant="outline" className="mt-1">
                      {summary.trends.cpu_trend}
                    </Badge>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">메모리 사용률</span>
                      <span className="text-sm text-muted-foreground">
                        {summary.performance_metrics.avg_memory_usage.toFixed(1)}%
                      </span>
                    </div>
                    <Progress value={summary.performance_metrics.avg_memory_usage} />
                    <Badge variant="outline" className="mt-1">
                      {summary.trends.memory_trend}
                    </Badge>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">응답시간</span>
                      <span className="text-sm text-muted-foreground">
                        {summary.performance_metrics.avg_response_time.toFixed(0)}ms
                      </span>
                    </div>
                    <Progress 
                      value={Math.min(100, summary.performance_metrics.avg_response_time / 10)} 
                    />
                    <Badge variant="outline" className="mt-1">
                      {summary.trends.response_trend}
                    </Badge>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">에러율</span>
                      <span className="text-sm text-muted-foreground">
                        {summary.performance_metrics.avg_error_rate.toFixed(2)}%
                      </span>
                    </div>
                    <Progress value={summary.performance_metrics.avg_error_rate} />
                    <Badge variant="outline" className="mt-1">
                      {summary.trends.error_trend}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 메인 탭 */}
          <Tabs defaultValue="metrics" className="space-y-4">
            <TabsList>
              <TabsTrigger value="metrics">실시간 메트릭</TabsTrigger>
              <TabsTrigger value="predictions">AI 예측</TabsTrigger>
              <TabsTrigger value="anomalies">이상 탐지</TabsTrigger>
              <TabsTrigger value="suggestions">최적화 제안</TabsTrigger>
            </TabsList>

            {/* 실시간 메트릭 탭 */}
            <TabsContent value="metrics" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>실시간 성능 메트릭</CardTitle>
                  <CardDescription>
                    최근 7일간의 성능 변화 추이
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={formatChartData(metrics)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="cpu"
                        stroke="#8884d8"
                        name="CPU 사용률 (%)"
                      />
                      <Line
                        type="monotone"
                        dataKey="memory"
                        stroke="#82ca9d"
                        name="메모리 사용률 (%)"
                      />
                      <Line
                        type="monotone"
                        dataKey="response"
                        stroke="#ffc658"
                        name="응답시간 (ms)"
                      />
                      <Line
                        type="monotone"
                        dataKey="error"
                        stroke="#ff7300"
                        name="에러율 (%)"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </TabsContent>

            {/* AI 예측 탭 */}
            <TabsContent value="predictions" className="space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle>성능 예측 결과</CardTitle>
                    <CardDescription>
                      AI 모델 기반 24시간 예측
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={formatPredictionsData(predictions)}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="type" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" fill="#8884d8" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>예측 신뢰도</CardTitle>
                    <CardDescription>
                      각 예측의 신뢰도 수준
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {predictions.map((pred, index) => (
                        <div key={index}>
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium">
                              {pred.prediction_type}
                            </span>
                            <span className="text-sm text-muted-foreground">
                              {pred.confidence.toFixed(1)}%
                            </span>
                          </div>
                          <Progress value={pred.confidence} />
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* 이상 탐지 탭 */}
            <TabsContent value="anomalies" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>이상 탐지 결과</CardTitle>
                  <CardDescription>
                    자동 감지된 성능 이상 사항
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {anomalies.length === 0 ? (
                    <div className="text-center py-8">
                      <Shield className="h-12 w-12 text-green-500 mx-auto mb-4" />
                      <p className="text-muted-foreground">감지된 이상이 없습니다.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {anomalies.map((anomaly, index) => (
                        <Alert key={index} variant={getSeverityColor(anomaly.severity) as any}>
                          <AlertTriangle className="h-4 w-4" />
                          <AlertDescription>
                            <div className="space-y-2">
                              <div className="flex items-center gap-2">
                                <Badge variant={getSeverityColor(anomaly.severity) as any}>
                                  {anomaly.severity}
                                </Badge>
                                <span className="font-medium">{anomaly.anomaly_type}</span>
                              </div>
                              <p>{anomaly.description}</p>
                              <div>
                                <p className="text-sm font-medium mb-1">권장 조치:</p>
                                <ul className="text-sm space-y-1">
                                  {anomaly.recommendations.map((rec, recIndex) => (
                                    <li key={recIndex}>• {rec}</li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          </AlertDescription>
                        </Alert>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* 최적화 제안 탭 */}
            <TabsContent value="suggestions" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>AI 최적화 제안</CardTitle>
                  <CardDescription>
                    성능 개선을 위한 AI 제안사항
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {suggestions.length === 0 ? (
                    <div className="text-center py-8">
                      <Lightbulb className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
                      <p className="text-muted-foreground">현재 최적화 제안이 없습니다.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {suggestions.map((suggestion, index) => (
                        <Card key={index}>
                          <CardHeader>
                            <div className="flex items-center justify-between">
                              <CardTitle className="text-lg">{suggestion.suggestion_type}</CardTitle>
                              <Badge variant={getPriorityColor(suggestion.priority) as any}>
                                {suggestion.priority}
                              </Badge>
                            </div>
                          </CardHeader>
                          <CardContent>
                            <p className="mb-4">{suggestion.description}</p>
                            <div className="flex items-center gap-2 mb-4">
                              <Zap className="h-4 w-4 text-yellow-500" />
                              <span className="text-sm font-medium">
                                예상 개선 효과: {suggestion.expected_improvement}%
                              </span>
                            </div>
                            <div>
                              <p className="text-sm font-medium mb-2">구현 단계:</p>
                              <ol className="text-sm space-y-1">
                                {suggestion.implementation_steps.map((step, stepIndex) => (
                                  <li key={stepIndex}>{stepIndex + 1}. {step}</li>
                                ))}
                              </ol>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  );
} 