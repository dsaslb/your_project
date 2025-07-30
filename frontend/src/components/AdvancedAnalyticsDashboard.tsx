'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { 
  TrendingUp, 
  TrendingDown, 
  Brain, 
  BarChart3, 
  Clock, 
  Zap,
  Target,
  AlertTriangle,
  CheckCircle,
  Info,
  RefreshCw,
  Play,
  Pause,
  Download,
  Upload
} from 'lucide-react';

interface PerformancePrediction {
  cpu_percent: number[];
  memory_percent: number[];
  response_time: number[];
}

interface PerformanceTrends {
  hourly_averages: Record<string, Record<string, number>>;
  daily_averages: Record<string, Record<string, number>>;
  recent_statistics: Record<string, Record<string, number>>;
  patterns: {
    peak_hours: { cpu: number; memory: number };
    performance_issues: {
      high_cpu_count: number;
      high_memory_count: number;
      high_cpu_hours: Record<string, number>;
      high_memory_hours: Record<string, number>;
    };
    correlations: Record<string, Record<string, number>>;
  };
}

interface OptimizationRecommendation {
  type: 'warning' | 'success' | 'info' | 'error';
  category: string;
  message: string;
  current_value: string;
  recommendation: string;
}

interface PerformanceAnalysis {
  trends: PerformanceTrends;
  recommendations: OptimizationRecommendation[];
  timestamp: string;
}

const AdvancedAnalyticsDashboard: React.FC = () => {
  const [predictions, setPredictions] = useState<PerformancePrediction | null>(null);
  const [analysis, setAnalysis] = useState<PerformanceAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [training, setTraining] = useState(false);
  const [predictionHours, setPredictionHours] = useState(24);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/ai/predict?hours=${predictionHours}`);
      if (response.ok) {
        const data = await response.json();
        setPredictions(data);
      }
    } catch (error) {
      console.error('예측 데이터 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalysis = async () => {
    try {
      const response = await fetch('/api/ai/analysis');
      if (response.ok) {
        const data = await response.json();
        setAnalysis(data);
      }
    } catch (error) {
      console.error('분석 데이터 조회 실패:', error);
    }
  };

  const trainModels = async () => {
    try {
      setTraining(true);
      const response = await fetch('/api/ai/train', { method: 'POST' });
      if (response.ok) {
        const result = await response.json();
        if (result.status === 'success') {
          // 모델 훈련 후 예측 및 분석 새로고침
          await fetchPredictions();
          await fetchAnalysis();
        }
      }
    } catch (error) {
      console.error('모델 훈련 실패:', error);
    } finally {
      setTraining(false);
    }
  };

  useEffect(() => {
    fetchAnalysis();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchAnalysis();
      }, 60000); // 1분마다
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'info':
        return <Info className="h-4 w-4 text-blue-500" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return <Info className="h-4 w-4 text-gray-500" />;
    }
  };

  const getRecommendationColor = (type: string) => {
    switch (type) {
      case 'warning':
        return 'border-yellow-200 bg-yellow-50';
      case 'success':
        return 'border-green-200 bg-green-50';
      case 'info':
        return 'border-blue-200 bg-blue-50';
      case 'error':
        return 'border-red-200 bg-red-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const formatHour = (hour: number) => {
    return `${hour.toString().padStart(2, '0')}:00`;
  };

  const formatDay = (day: number) => {
    const days = ['월', '화', '수', '목', '금', '토', '일'];
    return days[day];
  };

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">고급 분석 대시보드</h1>
          <p className="text-gray-600">AI 기반 성능 예측 및 최적화 분석</p>
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
            onClick={fetchAnalysis}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            새로고침
          </Button>
          <Button
            onClick={trainModels}
            disabled={training}
            className="bg-purple-600 hover:bg-purple-700"
          >
            <Brain className="h-4 w-4 mr-2" />
            {training ? '훈련 중...' : 'AI 모델 훈련'}
          </Button>
        </div>
      </div>

      {/* 예측 설정 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Target className="h-5 w-5" />
            <span>성능 예측 설정</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <div>
              <label className="text-sm font-medium">예측 시간 (시간)</label>
              <select
                value={predictionHours}
                onChange={(e) => setPredictionHours(Number(e.target.value))}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value={6}>6시간</option>
                <option value={12}>12시간</option>
                <option value={24}>24시간</option>
                <option value={48}>48시간</option>
                <option value={72}>72시간</option>
              </select>
            </div>
            <Button
              onClick={fetchPredictions}
              disabled={loading}
              className="mt-6"
            >
              <Zap className="h-4 w-4 mr-2" />
              예측 실행
            </Button>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="predictions" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="predictions">성능 예측</TabsTrigger>
          <TabsTrigger value="trends">트렌드 분석</TabsTrigger>
          <TabsTrigger value="recommendations">최적화 권장</TabsTrigger>
          <TabsTrigger value="patterns">패턴 분석</TabsTrigger>
        </TabsList>

        <TabsContent value="predictions" className="space-y-4">
          {predictions ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* CPU 예측 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <TrendingUp className="h-5 w-5" />
                    <span>CPU 사용률 예측</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {predictions.cpu_percent.slice(0, 6).map((value, index) => (
                      <div key={index} className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">
                          {formatHour(index)}
                        </span>
                        <div className="flex items-center space-x-2">
                          <Progress value={Math.min(value, 100)} className="w-20 h-2" />
                          <span className="text-sm font-medium">
                            {value.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* 메모리 예측 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <TrendingUp className="h-5 w-5" />
                    <span>메모리 사용률 예측</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {predictions.memory_percent.slice(0, 6).map((value, index) => (
                      <div key={index} className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">
                          {formatHour(index)}
                        </span>
                        <div className="flex items-center space-x-2">
                          <Progress value={Math.min(value, 100)} className="w-20 h-2" />
                          <span className="text-sm font-medium">
                            {value.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* 응답시간 예측 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <TrendingUp className="h-5 w-5" />
                    <span>응답시간 예측</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {predictions.response_time.slice(0, 6).map((value, index) => (
                      <div key={index} className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">
                          {formatHour(index)}
                        </span>
                        <div className="flex items-center space-x-2">
                          <Progress 
                            value={Math.min((value / 5) * 100, 100)} 
                            className="w-20 h-2" 
                          />
                          <span className="text-sm font-medium">
                            {value.toFixed(3)}s
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Brain className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600">예측을 실행하여 AI 기반 성능 예측을 확인하세요.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="trends" className="space-y-4">
          {analysis?.trends ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* 시간대별 평균 */}
              <Card>
                <CardHeader>
                  <CardTitle>시간대별 평균 성능</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {Object.entries(analysis.trends.hourly_averages.cpu_percent || {}).slice(0, 8).map(([hour, value]) => (
                      <div key={hour} className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">
                          {formatHour(Number(hour))}
                        </span>
                        <span className="text-sm font-medium">
                          {value}%
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* 요일별 평균 */}
              <Card>
                <CardHeader>
                  <CardTitle>요일별 평균 성능</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {Object.entries(analysis.trends.daily_averages.cpu_percent || {}).map(([day, value]) => (
                      <div key={day} className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">
                          {formatDay(Number(day))}
                        </span>
                        <span className="text-sm font-medium">
                          {value}%
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <BarChart3 className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600">트렌드 분석 데이터를 불러오는 중...</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-4">
          {analysis?.recommendations ? (
            <div className="space-y-4">
              {analysis.recommendations.map((rec, index) => (
                <Alert key={index} className={getRecommendationColor(rec.type)}>
                  <div className="flex items-start space-x-3">
                    {getRecommendationIcon(rec.type)}
                    <div className="flex-1">
                      <AlertDescription>
                        <div className="font-medium mb-1">{rec.message}</div>
                        <div className="text-sm text-gray-600 mb-2">
                          현재 값: {rec.current_value}
                        </div>
                        <div className="text-sm">
                          <strong>권장사항:</strong> {rec.recommendation}
                        </div>
                      </AlertDescription>
                    </div>
                    <Badge variant="outline" className="ml-2">
                      {rec.category}
                    </Badge>
                  </div>
                </Alert>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Target className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600">최적화 권장사항을 불러오는 중...</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="patterns" className="space-y-4">
          {analysis?.trends?.patterns ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* 피크 시간 */}
              <Card>
                <CardHeader>
                  <CardTitle>성능 피크 시간</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">CPU 피크 시간</span>
                      <span className="font-medium">
                        {formatHour(analysis.trends.patterns.peak_hours.cpu)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">메모리 피크 시간</span>
                      <span className="font-medium">
                        {formatHour(analysis.trends.patterns.peak_hours.memory)}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* 성능 이슈 */}
              <Card>
                <CardHeader>
                  <CardTitle>성능 이슈 통계</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">높은 CPU 사용 횟수</span>
                      <Badge variant="outline">
                        {analysis.trends.patterns.performance_issues.high_cpu_count}회
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">높은 메모리 사용 횟수</span>
                      <Badge variant="outline">
                        {analysis.trends.patterns.performance_issues.high_memory_count}회
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <BarChart3 className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600">패턴 분석 데이터를 불러오는 중...</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdvancedAnalyticsDashboard; 