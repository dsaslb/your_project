'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { apiClient } from '@/lib/api-client';

interface PredictionResult {
  predicted_sales?: number;
  predicted_staff_count?: number;
  predicted_quantity?: number;
  confidence: number;
  features_used: string[];
}

interface ModelStatus {
  total_models: number;
  available_models: string[];
  model_metadata: Record<string, any>;
}

const MLDashboard: React.FC = () => {
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);
  const [predictionResult, setPredictionResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // 예측 입력 데이터
  const [salesFeatures, setSalesFeatures] = useState({
    day_of_week: 1,
    month: new Date().getMonth() + 1,
    is_holiday: 0,
    temperature: 20,
    precipitation: 0,
    previous_sales: 0,
    staff_count: 5,
    special_event: 0
  });
  
  const [staffFeatures, setStaffFeatures] = useState({
    expected_sales: 1000000,
    day_of_week: 1,
    is_holiday: 0,
    special_event: 0,
    current_staff: 5,
    avg_order_time: 15
  });
  
  const [inventoryFeatures, setInventoryFeatures] = useState({
    current_stock: 100,
    daily_usage: 10,
    lead_time: 3,
    safety_stock: 20,
    seasonal_factor: 1.0
  });

  useEffect(() => {
    fetchModelStatus();
  }, []);

  const fetchModelStatus = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/ml/status');
      setModelStatus(response.data.status);
    } catch (err) {
      setError('모델 상태를 불러오는데 실패했습니다.');
      console.error('Model status error:', err);
    } finally {
      setLoading(false);
    }
  };

  const predictSales = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.post('/api/ml/predict/sales', salesFeatures);
      setPredictionResult(response.data.prediction);
    } catch (err: any) {
      setError(err.response?.data?.error || '매출 예측에 실패했습니다.');
      console.error('Sales prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  const predictStaff = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.post('/api/ml/predict/staff', staffFeatures);
      setPredictionResult(response.data.prediction);
    } catch (err: any) {
      setError(err.response?.data?.error || '직원 예측에 실패했습니다.');
      console.error('Staff prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  const predictInventory = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.post('/api/ml/predict/inventory', inventoryFeatures);
      setPredictionResult(response.data.prediction);
    } catch (err: any) {
      setError(err.response?.data?.error || '재고 예측에 실패했습니다.');
      console.error('Inventory prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-500';
    if (confidence >= 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">머신러닝 대시보드</h1>
          <p className="text-muted-foreground">
            AI 기반 예측 및 분석 도구
          </p>
        </div>
        <Button onClick={fetchModelStatus} disabled={loading}>
          {loading ? '로딩 중...' : '새로고침'}
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 모델 상태 */}
      <Card>
        <CardHeader>
          <CardTitle>모델 상태</CardTitle>
          <CardDescription>
            현재 사용 가능한 머신러닝 모델들의 상태
          </CardDescription>
        </CardHeader>
        <CardContent>
          {modelStatus ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold">{modelStatus.total_models}</div>
                <div className="text-sm text-muted-foreground">총 모델 수</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {modelStatus.available_models.length}
                </div>
                <div className="text-sm text-muted-foreground">사용 가능한 모델</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {Object.keys(modelStatus.model_metadata).length}
                </div>
                <div className="text-sm text-muted-foreground">훈련된 모델</div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-muted-foreground">모델 상태를 불러오는 중...</div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 예측 도구 */}
      <Tabs defaultValue="sales" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="sales">매출 예측</TabsTrigger>
          <TabsTrigger value="staff">직원 예측</TabsTrigger>
          <TabsTrigger value="inventory">재고 예측</TabsTrigger>
        </TabsList>

        <TabsContent value="sales" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>매출 예측</CardTitle>
              <CardDescription>
                다양한 요인을 기반으로 한 매출 예측
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="day_of_week">요일</Label>
                  <Select
                    value={salesFeatures.day_of_week.toString()}
                    onValueChange={(value) => setSalesFeatures({
                      ...salesFeatures,
                      day_of_week: parseInt(value)
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">월요일</SelectItem>
                      <SelectItem value="2">화요일</SelectItem>
                      <SelectItem value="3">수요일</SelectItem>
                      <SelectItem value="4">목요일</SelectItem>
                      <SelectItem value="5">금요일</SelectItem>
                      <SelectItem value="6">토요일</SelectItem>
                      <SelectItem value="7">일요일</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="temperature">온도 (°C)</Label>
                  <Input
                    type="number"
                    value={salesFeatures.temperature}
                    onChange={(e) => setSalesFeatures({
                      ...salesFeatures,
                      temperature: parseFloat(e.target.value)
                    })}
                  />
                </div>
                
                <div>
                  <Label htmlFor="staff_count">직원 수</Label>
                  <Input
                    type="number"
                    value={salesFeatures.staff_count}
                    onChange={(e) => setSalesFeatures({
                      ...salesFeatures,
                      staff_count: parseInt(e.target.value)
                    })}
                  />
                </div>
                
                <div>
                  <Label htmlFor="previous_sales">이전 매출</Label>
                  <Input
                    type="number"
                    value={salesFeatures.previous_sales}
                    onChange={(e) => setSalesFeatures({
                      ...salesFeatures,
                      previous_sales: parseFloat(e.target.value)
                    })}
                  />
                </div>
              </div>
              
              <Button onClick={predictSales} disabled={loading} className="w-full">
                {loading ? '예측 중...' : '매출 예측'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="staff" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>직원 필요 인원 예측</CardTitle>
              <CardDescription>
                예상 매출과 기타 요인을 기반으로 한 필요 직원 수 예측
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="expected_sales">예상 매출</Label>
                  <Input
                    type="number"
                    value={staffFeatures.expected_sales}
                    onChange={(e) => setStaffFeatures({
                      ...staffFeatures,
                      expected_sales: parseFloat(e.target.value)
                    })}
                  />
                </div>
                
                <div>
                  <Label htmlFor="current_staff">현재 직원 수</Label>
                  <Input
                    type="number"
                    value={staffFeatures.current_staff}
                    onChange={(e) => setStaffFeatures({
                      ...staffFeatures,
                      current_staff: parseInt(e.target.value)
                    })}
                  />
                </div>
              </div>
              
              <Button onClick={predictStaff} disabled={loading} className="w-full">
                {loading ? '예측 중...' : '직원 수 예측'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="inventory" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>재고 필요량 예측</CardTitle>
              <CardDescription>
                현재 재고와 사용량을 기반으로 한 필요 재고량 예측
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="current_stock">현재 재고</Label>
                  <Input
                    type="number"
                    value={inventoryFeatures.current_stock}
                    onChange={(e) => setInventoryFeatures({
                      ...inventoryFeatures,
                      current_stock: parseFloat(e.target.value)
                    })}
                  />
                </div>
                
                <div>
                  <Label htmlFor="daily_usage">일일 사용량</Label>
                  <Input
                    type="number"
                    value={inventoryFeatures.daily_usage}
                    onChange={(e) => setInventoryFeatures({
                      ...inventoryFeatures,
                      daily_usage: parseFloat(e.target.value)
                    })}
                  />
                </div>
              </div>
              
              <Button onClick={predictInventory} disabled={loading} className="w-full">
                {loading ? '예측 중...' : '재고 예측'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 예측 결과 */}
      {predictionResult && (
        <Card>
          <CardHeader>
            <CardTitle>예측 결과</CardTitle>
            <CardDescription>
              AI 모델의 예측 결과 및 신뢰도
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>예측값</Label>
                <div className="text-2xl font-bold">
                  {predictionResult.predicted_sales && formatCurrency(predictionResult.predicted_sales)}
                  {predictionResult.predicted_staff_count && `${predictionResult.predicted_staff_count}명`}
                  {predictionResult.predicted_quantity && `${predictionResult.predicted_quantity}개`}
                </div>
              </div>
              
              <div>
                <Label>신뢰도</Label>
                <div className="flex items-center space-x-2">
                  <Progress value={predictionResult.confidence * 100} className="flex-1" />
                  <Badge className={getConfidenceColor(predictionResult.confidence)}>
                    {(predictionResult.confidence * 100).toFixed(1)}%
                  </Badge>
                </div>
              </div>
            </div>
            
            <div>
              <Label>사용된 특성</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {predictionResult.features_used.map((feature, index) => (
                  <Badge key={index} variant="outline">
                    {feature}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 예측 히스토리 차트 */}
      <Card>
        <CardHeader>
          <CardTitle>예측 히스토리</CardTitle>
          <CardDescription>
            최근 예측 결과들의 추이
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={[
              { date: '2024-01', sales: 1200000, staff: 8, inventory: 150 },
              { date: '2024-02', sales: 1350000, staff: 9, inventory: 180 },
              { date: '2024-03', sales: 1100000, staff: 7, inventory: 120 },
              { date: '2024-04', sales: 1400000, staff: 10, inventory: 200 },
              { date: '2024-05', sales: 1250000, staff: 8, inventory: 160 }
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="sales" stroke="#8884d8" name="매출" />
              <Line type="monotone" dataKey="staff" stroke="#82ca9d" name="직원수" />
              <Line type="monotone" dataKey="inventory" stroke="#ffc658" name="재고" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default MLDashboard; 