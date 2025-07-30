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
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, TrendingUp, TrendingDown, Users, Package, DollarSign, Brain, Activity } from 'lucide-react';

interface AIModel {
  name: string;
  type: string;
  performance: {
    r2_score: number;
    mse: number;
    mae: number;
  };
  feature_count: number;
  trained_at: string;
}

interface SystemStatus {
  ai_engine_status: string;
  models_loaded: number;
  total_predictions: number;
  memory_usage: string;
}

interface RecentActivity {
  action: string;
  model_name: string;
  timestamp: string;
  status: string;
}

interface AIDashboardData {
  system_status: SystemStatus;
  performance_summary: Record<string, any>;
  recent_activity: RecentActivity[];
}

const AdvancedAIDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<AIDashboardData | null>(null);
  const [models, setModels] = useState<AIModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [predictionData, setPredictionData] = useState<any>(null);
  const [testData, setTestData] = useState<any>(null);

  // API 기본 URL
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

  useEffect(() => {
    fetchDashboardData();
    fetchModels();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v2/ai/analytics/dashboard`);
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      } else {
        throw new Error('대시보드 데이터를 불러올 수 없습니다');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  };

  const fetchModels = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v2/ai/models/list`);
      if (response.ok) {
        const data = await response.json();
        const modelList = Object.entries(data.models).map(([name, model]: [string, any]) => ({
          name,
          type: model.model_type,
          performance: model.performance,
          feature_count: model.feature_count,
          trained_at: model.trained_at
        }));
        setModels(modelList);
      }
    } catch (err) {
      console.error('모델 목록을 불러올 수 없습니다:', err);
    }
  };

  const generateTestData = async (type: string, samples: number = 1000) => {
    try {
      const response = await fetch(`${API_BASE}/api/v2/ai/test/generate-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type,
          n_samples: samples
        })
      });

      if (response.ok) {
        const data = await response.json();
        setTestData(data.test_data);
        return data.test_data;
      } else {
        throw new Error('테스트 데이터 생성에 실패했습니다');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '테스트 데이터 생성 중 오류가 발생했습니다');
    }
  };

  const analyzeSalesTrends = async () => {
    if (!testData?.sales_data) {
      await generateTestData('sales', 100);
    }

    try {
      const response = await fetch(`${API_BASE}/api/v2/ai/sales/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sales_data: testData?.sales_data || []
        })
      });

      if (response.ok) {
        const data = await response.json();
        setPredictionData(data.analysis);
      } else {
        throw new Error('매출 분석에 실패했습니다');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '매출 분석 중 오류가 발생했습니다');
    }
  };

  const predictCustomerChurn = async () => {
    if (!testData?.customer_data) {
      await generateTestData('customer', 100);
    }

    try {
      const response = await fetch(`${API_BASE}/api/v2/ai/customer/churn`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          customer_data: testData?.customer_data || []
        })
      });

      if (response.ok) {
        const data = await response.json();
        setPredictionData(data.analysis);
      } else {
        throw new Error('고객 이탈 예측에 실패했습니다');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '고객 이탈 예측 중 오류가 발생했습니다');
    }
  };

  const optimizeInventory = async () => {
    if (!testData?.inventory_data) {
      await generateTestData('inventory', 100);
    }

    try {
      const response = await fetch(`${API_BASE}/api/v2/ai/inventory/optimize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          inventory_data: testData?.inventory_data || []
        })
      });

      if (response.ok) {
        const data = await response.json();
        setPredictionData(data.analysis);
      } else {
        throw new Error('재고 최적화에 실패했습니다');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '재고 최적화 중 오류가 발생했습니다');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational':
        return 'bg-green-500';
      case 'warning':
        return 'bg-yellow-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'operational':
        return '정상';
      case 'warning':
        return '경고';
      case 'error':
        return '오류';
      default:
        return '알 수 없음';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">AI 대시보드 로딩 중...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert className="mb-4">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">고급 AI 분석 대시보드</h1>
          <p className="text-muted-foreground">
            엔터프라이즈급 AI 분석 및 예측 시스템
          </p>
        </div>
        <Badge variant="outline" className="flex items-center gap-2">
          <Brain className="h-4 w-4" />
          AI 엔진 v2.0
        </Badge>
      </div>

      {/* 시스템 상태 카드 */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">AI 엔진 상태</CardTitle>
              <div className={`h-2 w-2 rounded-full ${getStatusColor(dashboardData.system_status.ai_engine_status)}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{getStatusText(dashboardData.system_status.ai_engine_status)}</div>
              <p className="text-xs text-muted-foreground">
                메모리 사용량: {dashboardData.system_status.memory_usage}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">로드된 모델</CardTitle>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.system_status.models_loaded}</div>
              <p className="text-xs text-muted-foreground">
                활성 모델 수
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 예측 수</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.system_status.total_predictions}</div>
              <p className="text-xs text-muted-foreground">
                누적 예측 횟수
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">시스템 성능</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">98%</div>
              <p className="text-xs text-muted-foreground">
                평균 응답 시간: 120ms
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs defaultValue="analytics" className="space-y-4">
        <TabsList>
          <TabsTrigger value="analytics">AI 분석</TabsTrigger>
          <TabsTrigger value="models">모델 관리</TabsTrigger>
          <TabsTrigger value="predictions">예측 결과</TabsTrigger>
          <TabsTrigger value="activity">활동 로그</TabsTrigger>
        </TabsList>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="h-5 w-5" />
                  매출 분석
                </CardTitle>
                <CardDescription>
                  매출 트렌드 분석 및 예측
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={analyzeSalesTrends} className="w-full">
                  매출 분석 실행
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  고객 이탈 예측
                </CardTitle>
                <CardDescription>
                  고객 이탈 위험도 분석
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={predictCustomerChurn} className="w-full">
                  이탈 예측 실행
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Package className="h-5 w-5" />
                  재고 최적화
                </CardTitle>
                <CardDescription>
                  재고 수준 최적화 분석
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={optimizeInventory} className="w-full">
                  재고 최적화 실행
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* 테스트 데이터 생성 */}
          <Card>
            <CardHeader>
              <CardTitle>테스트 데이터 생성</CardTitle>
              <CardDescription>
                AI 분석을 위한 샘플 데이터를 생성합니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-1">
                  <Label htmlFor="dataType">데이터 타입</Label>
                  <Select onValueChange={(value) => console.log(value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="데이터 타입 선택" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sales">매출 데이터</SelectItem>
                      <SelectItem value="customer">고객 데이터</SelectItem>
                      <SelectItem value="inventory">재고 데이터</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex-1">
                  <Label htmlFor="samples">샘플 수</Label>
                  <Input
                    id="samples"
                    type="number"
                    placeholder="1000"
                    defaultValue={1000}
                  />
                </div>
                <div className="flex items-end">
                  <Button onClick={() => generateTestData('sales', 1000)}>
                    데이터 생성
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="models" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>훈련된 모델 목록</CardTitle>
              <CardDescription>
                현재 시스템에 로드된 AI 모델들
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {models.map((model) => (
                  <div key={model.name} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <h3 className="font-semibold">{model.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        타입: {model.type} | 특성 수: {model.feature_count}
                      </p>
                      <div className="flex gap-4 mt-2">
                        <span className="text-xs">
                          R²: {(model.performance.r2_score * 100).toFixed(1)}%
                        </span>
                        <span className="text-xs">
                          MSE: {model.performance.mse.toFixed(4)}
                        </span>
                        <span className="text-xs">
                          MAE: {model.performance.mae.toFixed(4)}
                        </span>
                      </div>
                    </div>
                    <Badge variant="outline">
                      {new Date(model.trained_at).toLocaleDateString()}
                    </Badge>
                  </div>
                ))}
                {models.length === 0 && (
                  <p className="text-center text-muted-foreground py-8">
                    훈련된 모델이 없습니다
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="predictions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>예측 결과</CardTitle>
              <CardDescription>
                AI 분석 결과 및 예측 데이터
              </CardDescription>
            </CardHeader>
            <CardContent>
              {predictionData ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {predictionData.model_performance && (
                      <div className="p-4 border rounded-lg">
                        <h4 className="font-semibold mb-2">모델 성능</h4>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span>R² 점수:</span>
                            <span>{(predictionData.model_performance.r2 * 100).toFixed(1)}%</span>
                          </div>
                          <Progress value={predictionData.model_performance.r2 * 100} className="h-2" />
                        </div>
                      </div>
                    )}
                    
                    {predictionData.cost_savings && (
                      <div className="p-4 border rounded-lg">
                        <h4 className="font-semibold mb-2">비용 절감</h4>
                        <div className="text-2xl font-bold text-green-600">
                          {predictionData.cost_savings.toLocaleString()}원
                        </div>
                      </div>
                    )}
                    
                    {predictionData.high_risk_customers && (
                      <div className="p-4 border rounded-lg">
                        <h4 className="font-semibold mb-2">고위험 고객</h4>
                        <div className="text-2xl font-bold text-red-600">
                          {predictionData.high_risk_customers.length}명
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {predictionData.recommendations && (
                    <div className="p-4 border rounded-lg">
                      <h4 className="font-semibold mb-2">권장사항</h4>
                      <ul className="space-y-1">
                        {predictionData.recommendations.map((rec: string, index: number) => (
                          <li key={index} className="text-sm">• {rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-center text-muted-foreground py-8">
                  분석을 실행하여 결과를 확인하세요
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>최근 활동</CardTitle>
              <CardDescription>
                AI 시스템의 최근 활동 로그
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboardData?.recent_activity.map((activity, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`h-2 w-2 rounded-full ${
                        activity.status === 'completed' ? 'bg-green-500' : 'bg-yellow-500'
                      }`} />
                      <div>
                        <p className="font-medium">{activity.action}</p>
                        <p className="text-sm text-muted-foreground">
                          모델: {activity.model_name}
                        </p>
                      </div>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {new Date(activity.timestamp).toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdvancedAIDashboard; 