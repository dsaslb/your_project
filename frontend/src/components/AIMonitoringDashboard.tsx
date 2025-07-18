import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  TrendingUp,
  TrendingDown,
  Brain,
  RefreshCw,
  Settings,
  Play,
  Pause,
  Zap,
  BarChart3,
  LineChart,
  Gauge
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

interface ModelPerformance {
  model_name: string;
  accuracy: number;
  prediction_count: number;
  error_count: number;
  avg_response_time: number;
  last_prediction: string;
  last_training: string;
  drift_score: number;
  status: 'healthy' | 'warning' | 'critical' | 'training';
}

interface PerformanceHistory {
  timestamp: string;
  accuracy: number;
  response_time: number;
  confidence: number;
  error_rate: number;
}

interface PerformanceSummary {
  total_models: number;
  total_predictions: number;
  avg_accuracy: number;
  avg_response_time: number;
  status_distribution: Record<string, number>;
  monitoring_active: boolean;
  auto_retrain_enabled: boolean;
}

interface AlertThresholds {
  accuracy_threshold: number;
  response_time_threshold: number;
  error_rate_threshold: number;
  drift_threshold: number;
}

const COLORS = {
  healthy: '#10b981',
  warning: '#f59e0b',
  critical: '#ef4444',
  training: '#3b82f6'
};

const STATUS_LABELS = {
  healthy: '정상',
  warning: '경고',
  critical: '위험',
  training: '훈련중'
};

const AIMonitoringDashboard: React.FC = () => {
  const [performances, setPerformances] = useState<Record<string, ModelPerformance>>({});
  const [summary, setSummary] = useState<PerformanceSummary | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [modelHistory, setModelHistory] = useState<PerformanceHistory[]>([]);
  const [thresholds, setThresholds] = useState<AlertThresholds>({
    accuracy_threshold: 0.7,
    response_time_threshold: 2.0,
    error_rate_threshold: 0.1,
    drift_threshold: 0.2
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    fetchMonitoringData();
    const interval = setInterval(fetchMonitoringData, 30000); // 30초마다 업데이트
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedModel) {
      fetchModelHistory(selectedModel);
    }
  }, [selectedModel]);

  const fetchMonitoringData = async () => {
    try {
      setIsLoading(true);
      setError('');

      // 성능 요약 조회
      const summaryResponse = await fetch('/api/ai/monitoring/summary', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (summaryResponse.ok) {
        const summaryData = await summaryResponse.json();
        if (summaryData.success) {
          setSummary(summaryData.summary);
        }
      }

      // 모든 모델 성능 조회
      const performanceResponse = await fetch('/api/ai/monitoring/performance', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (performanceResponse.ok) {
        const performanceData = await performanceResponse.json();
        if (performanceData.success) {
          setPerformances(performanceData.performances);
        }
      }

      setLastUpdate(new Date().toLocaleString());
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchModelHistory = async (modelName: string) => {
    try {
      const response = await fetch(`/api/ai/monitoring/performance?model_name=${modelName}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.history) {
          setModelHistory(data.history);
        }
      }
    } catch (err) {
      console.error('모델 이력 조회 실패:', err);
    }
  };

  const updateThresholds = async (newThresholds: AlertThresholds) => {
    try {
      const response = await fetch('/api/ai/monitoring/thresholds', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newThresholds),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setThresholds(newThresholds);
        }
      }
    } catch (err) {
      console.error('임계값 업데이트 실패:', err);
    }
  };

  const getStatusColor = (status: string) => {
    return COLORS[status as keyof typeof COLORS] || COLORS.healthy;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="w-4 h-4" />;
      case 'warning': return <AlertTriangle className="w-4 h-4" />;
      case 'critical': return <AlertTriangle className="w-4 h-4" />;
      case 'training': return <Clock className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const formatResponseTime = (time: number) => {
    return `${(time * 1000).toFixed(0)}ms`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (isLoading && !summary) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p>AI 모니터링 데이터를 불러오는 중...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI 모니터링 대시보드</h1>
          <p className="text-muted-foreground">
            마지막 업데이트: {lastUpdate}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            onClick={fetchMonitoringData}
            disabled={isLoading}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            새로고침
          </Button>
          <Button variant="outline">
            <Settings className="w-4 h-4 mr-2" />
            설정
          </Button>
        </div>
      </div>

      {/* 전체 요약 */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-4 h-4" />
                총 모델 수
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {summary.total_models}개
              </div>
              <div className="text-sm text-muted-foreground">
                활성 AI 모델
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4" />
                총 예측 수
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {summary.total_predictions.toLocaleString()}회
              </div>
              <div className="text-sm text-muted-foreground">
                누적 예측 횟수
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gauge className="w-4 h-4" />
                평균 정확도
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {(summary.avg_accuracy * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-muted-foreground">
                전체 모델 평균
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                평균 응답시간
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatResponseTime(summary.avg_response_time)}
              </div>
              <div className="text-sm text-muted-foreground">
                전체 모델 평균
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 모델 상태 분포 */}
      {summary && (
        <Card>
          <CardHeader>
            <CardTitle>모델 상태 분포</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(summary.status_distribution).map(([status, count]) => (
                <div key={status} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: getStatusColor(status) }}
                    />
                    <span className="font-medium">{STATUS_LABELS[status as keyof typeof STATUS_LABELS]}</span>
                  </div>
                  <Badge variant="outline">{count}개</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 모델별 성능 */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">전체 개요</TabsTrigger>
          <TabsTrigger value="details">상세 분석</TabsTrigger>
          <TabsTrigger value="history">성능 이력</TabsTrigger>
        </TabsList>

        {/* 전체 개요 */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(performances).map(([modelName, performance]) => (
              <Card key={modelName} className="cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => setSelectedModel(modelName)}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="text-lg">{modelName}</span>
                    <Badge 
                      style={{ backgroundColor: getStatusColor(performance.status) }}
                      className="text-white"
                    >
                      {STATUS_LABELS[performance.status]}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span>정확도</span>
                    <span className="font-medium">{(performance.accuracy * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={performance.accuracy * 100} className="h-2" />
                  
                  <div className="flex justify-between">
                    <span>예측 횟수</span>
                    <span className="font-medium">{performance.prediction_count.toLocaleString()}</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span>응답시간</span>
                    <span className="font-medium">{formatResponseTime(performance.avg_response_time)}</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span>드리프트 점수</span>
                    <span className="font-medium">{performance.drift_score.toFixed(3)}</span>
                  </div>
                  
                  <div className="text-xs text-muted-foreground">
                    마지막 예측: {formatDate(performance.last_prediction)}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* 상세 분석 */}
        <TabsContent value="details" className="space-y-4">
          {selectedModel && performances[selectedModel] && (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>{selectedModel} 상세 성능</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium mb-2">정확도 분석</h4>
                        <div className="flex items-center gap-2">
                          <Progress value={performances[selectedModel].accuracy * 100} className="flex-1" />
                          <span className="text-sm font-medium">
                            {(performances[selectedModel].accuracy * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          임계값: {(thresholds.accuracy_threshold * 100).toFixed(0)}%
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="font-medium mb-2">응답시간 분석</h4>
                        <div className="flex items-center gap-2">
                          <Progress 
                            value={(performances[selectedModel].avg_response_time / thresholds.response_time_threshold) * 100} 
                            className="flex-1" 
                          />
                          <span className="text-sm font-medium">
                            {formatResponseTime(performances[selectedModel].avg_response_time)}
                          </span>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          임계값: {formatResponseTime(thresholds.response_time_threshold)}
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="font-medium mb-2">에러율 분석</h4>
                        <div className="flex items-center gap-2">
                          <Progress 
                            value={(performances[selectedModel].error_count / performances[selectedModel].prediction_count) * 100} 
                            className="flex-1" 
                          />
                          <span className="text-sm font-medium">
                            {((performances[selectedModel].error_count / performances[selectedModel].prediction_count) * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          임계값: {(thresholds.error_rate_threshold * 100).toFixed(0)}%
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium mb-2">드리프트 분석</h4>
                        <div className="flex items-center gap-2">
                          <Progress 
                            value={(performances[selectedModel].drift_score / thresholds.drift_threshold) * 100} 
                            className="flex-1" 
                          />
                          <span className="text-sm font-medium">
                            {performances[selectedModel].drift_score.toFixed(3)}
                          </span>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          임계값: {thresholds.drift_threshold.toFixed(3)}
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="font-medium mb-2">상태 정보</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span>현재 상태:</span>
                            <Badge style={{ backgroundColor: getStatusColor(performances[selectedModel].status) }}>
                              {STATUS_LABELS[performances[selectedModel].status]}
                            </Badge>
                          </div>
                          <div className="flex justify-between">
                            <span>마지막 예측:</span>
                            <span>{formatDate(performances[selectedModel].last_prediction)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>마지막 훈련:</span>
                            <span>{formatDate(performances[selectedModel].last_training)}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* 성능 이력 */}
        <TabsContent value="history" className="space-y-4">
          {selectedModel && modelHistory.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>{selectedModel} 성능 이력</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={modelHistory}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="timestamp" 
                      tickFormatter={(value) => new Date(value).toLocaleDateString()}
                    />
                    <YAxis />
                    <Tooltip 
                      labelFormatter={(value) => new Date(value).toLocaleString()}
                      formatter={(value, name) => [
                        name === 'accuracy' ? `${(Number(value) * 100).toFixed(1)}%` : 
                        name === 'response_time' ? formatResponseTime(Number(value)) :
                        name === 'error_rate' ? `${(Number(value) * 100).toFixed(1)}%` :
                        Number(value).toFixed(3),
                        name === 'accuracy' ? '정확도' :
                        name === 'response_time' ? '응답시간' :
                        name === 'confidence' ? '신뢰도' :
                        name === 'error_rate' ? '에러율' : name
                      ]}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="accuracy" 
                      stroke="#3b82f6" 
                      strokeWidth={2}
                      name="정확도"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="confidence" 
                      stroke="#10b981" 
                      strokeWidth={2}
                      name="신뢰도"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* 알림 설정 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            알림 임계값 설정
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">정확도 임계값 (%)</label>
              <input
                type="number"
                min="0"
                max="100"
                value={Math.round(thresholds.accuracy_threshold * 100)}
                onChange={(e) => updateThresholds({
                  ...thresholds,
                  accuracy_threshold: Number(e.target.value) / 100
                })}
                className="w-full mt-1 px-3 py-2 border rounded-md"
              />
            </div>
            
            <div>
              <label className="text-sm font-medium">응답시간 임계값 (초)</label>
              <input
                type="number"
                min="0.1"
                max="10"
                step="0.1"
                value={thresholds.response_time_threshold}
                onChange={(e) => updateThresholds({
                  ...thresholds,
                  response_time_threshold: Number(e.target.value)
                })}
                className="w-full mt-1 px-3 py-2 border rounded-md"
              />
            </div>
            
            <div>
              <label className="text-sm font-medium">에러율 임계값 (%)</label>
              <input
                type="number"
                min="0"
                max="100"
                value={Math.round(thresholds.error_rate_threshold * 100)}
                onChange={(e) => updateThresholds({
                  ...thresholds,
                  error_rate_threshold: Number(e.target.value) / 100
                })}
                className="w-full mt-1 px-3 py-2 border rounded-md"
              />
            </div>
            
            <div>
              <label className="text-sm font-medium">드리프트 임계값</label>
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={thresholds.drift_threshold}
                onChange={(e) => updateThresholds({
                  ...thresholds,
                  drift_threshold: Number(e.target.value)
                })}
                className="w-full mt-1 px-3 py-2 border rounded-md"
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AIMonitoringDashboard; 