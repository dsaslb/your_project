'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { 
  Thermometer, 
  Droplets, 
  Scale, 
  Activity, 
  Lightbulb, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Settings
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface IoTDevice {
  device_id: string;
  device_type: string;
  location: string;
  status: string;
  is_running: boolean;
  last_update: string;
}

interface SensorData {
  device_id: string;
  device_type: string;
  timestamp: string;
  value: number;
  unit: string;
  status: string;
  location: string;
  metadata: any;
}

interface IoTAlert {
  type: string;
  severity: 'high' | 'medium' | 'low';
  message: string;
  device_id: string;
  location: string;
  value: number | null;
  timestamp: string;
}

interface DashboardData {
  total_devices: number;
  online_devices: number;
  error_devices: number;
  temperature_summary: {
    average: number;
    min: number;
    max: number;
  };
  humidity_summary: {
    average: number;
    min: number;
    max: number;
  };
  inventory_summary: {
    total_weight: number;
    low_stock_count: number;
  };
  active_areas: string[];
  recent_alerts: any[];
}

const IoTDashboard: React.FC = () => {
  const [devices, setDevices] = useState<IoTDevice[]>([]);
  const [latestData, setLatestData] = useState<SensorData[]>([]);
  const [alerts, setAlerts] = useState<IoTAlert[]>([]);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  // 데이터 로드 함수
  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 병렬로 데이터 로드
      const [devicesRes, dataRes, alertsRes, dashboardRes] = await Promise.all([
        apiClient.get('/api/iot/devices'),
        apiClient.get('/api/iot/data/latest'),
        apiClient.get('/api/iot/alerts'),
        apiClient.get('/api/iot/dashboard')
      ]);

      if (devicesRes.data.success) setDevices(devicesRes.data.data);
      if (dataRes.data.success) setLatestData(dataRes.data.data);
      if (alertsRes.data.success) setAlerts(alertsRes.data.data);
      if (dashboardRes.data.success) setDashboardData(dashboardRes.data.data);

    } catch (err: any) {
      setError(err.response?.data?.error || '데이터 로드 중 오류가 발생했습니다.');
      console.error('IoT 데이터 로드 오류:', err);
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 시 데이터 로드
  useEffect(() => {
    loadData();
    
    // 30초마다 자동 새로고침
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  // 기기 타입별 아이콘
  const getDeviceIcon = (deviceType: string) => {
    switch (deviceType) {
      case 'temperature_sensor':
      case 'refrigerator':
        return <Thermometer className="h-4 w-4" />;
      case 'humidity_sensor':
        return <Droplets className="h-4 w-4" />;
      case 'weight_sensor':
        return <Scale className="h-4 w-4" />;
      case 'motion_sensor':
        return <Activity className="h-4 w-4" />;
      case 'light_controller':
        return <Lightbulb className="h-4 w-4" />;
      default:
        return <Settings className="h-4 w-4" />;
    }
  };

  // 상태별 배지 색상
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'online':
        return <Badge variant="default" className="bg-green-500">온라인</Badge>;
      case 'offline':
        return <Badge variant="secondary">오프라인</Badge>;
      case 'error':
        return <Badge variant="destructive">오류</Badge>;
      case 'maintenance':
        return <Badge variant="outline">점검중</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  // 알림 심각도별 색상
  const getAlertSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'border-red-500 bg-red-50';
      case 'medium':
        return 'border-yellow-500 bg-yellow-50';
      case 'low':
        return 'border-blue-500 bg-blue-50';
      default:
        return 'border-gray-500 bg-gray-50';
    }
  };

  // 기기별 최신 데이터 찾기
  const getDeviceLatestData = (deviceId: string) => {
    return latestData.find(data => data.device_id === deviceId);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">IoT 데이터 로딩 중...</span>
      </div>
    );
  }

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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">IoT 대시보드</h1>
          <p className="text-muted-foreground">
            스마트 레스토랑 IoT 기기 모니터링 및 제어
          </p>
        </div>
        <Button onClick={loadData} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          새로고침
        </Button>
      </div>

      {/* 대시보드 요약 */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 기기</CardTitle>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.total_devices}</div>
              <p className="text-xs text-muted-foreground">
                온라인: {dashboardData.online_devices} | 오류: {dashboardData.error_devices}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">평균 온도</CardTitle>
              <Thermometer className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.temperature_summary.average}°C</div>
              <p className="text-xs text-muted-foreground">
                {dashboardData.temperature_summary.min}°C ~ {dashboardData.temperature_summary.max}°C
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">평균 습도</CardTitle>
              <Droplets className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.humidity_summary.average}%</div>
              <p className="text-xs text-muted-foreground">
                {dashboardData.humidity_summary.min}% ~ {dashboardData.humidity_summary.max}%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 재고</CardTitle>
              <Scale className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.inventory_summary.total_weight}kg</div>
              <p className="text-xs text-muted-foreground">
                부족: {dashboardData.inventory_summary.low_stock_count}개
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 탭 인터페이스 */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="devices">기기 상태</TabsTrigger>
          <TabsTrigger value="alerts">알림</TabsTrigger>
          <TabsTrigger value="analytics">분석</TabsTrigger>
        </TabsList>

        {/* 개요 탭 */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 활성 영역 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  활성 영역
                </CardTitle>
                <CardDescription>
                  현재 활동이 감지된 영역
                </CardDescription>
              </CardHeader>
              <CardContent>
                {dashboardData?.active_areas.length ? (
                  <div className="space-y-2">
                    {dashboardData.active_areas.map((area, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span>{area}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">현재 활성 영역이 없습니다.</p>
                )}
              </CardContent>
            </Card>

            {/* 최근 알림 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  최근 알림
                </CardTitle>
                <CardDescription>
                  최근 발생한 IoT 알림
                </CardDescription>
              </CardHeader>
              <CardContent>
                {alerts.slice(0, 5).map((alert, index) => (
                  <div key={index} className={`p-3 rounded-lg border mb-2 ${getAlertSeverityColor(alert.severity)}`}>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{alert.message}</span>
                      <Badge variant={alert.severity === 'high' ? 'destructive' : 'secondary'}>
                        {alert.severity}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {alert.location} • {new Date(alert.timestamp).toLocaleString()}
                    </p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 기기 상태 탭 */}
        <TabsContent value="devices" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {devices.map((device) => {
              const deviceData = getDeviceLatestData(device.device_id);
              return (
                <Card key={device.device_id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getDeviceIcon(device.device_type)}
                        <CardTitle className="text-sm">{device.device_id}</CardTitle>
                      </div>
                      {getStatusBadge(device.status)}
                    </div>
                    <CardDescription>{device.location}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {deviceData ? (
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">현재 값:</span>
                          <span className="font-medium">
                            {deviceData.value} {deviceData.unit}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">마지막 업데이트:</span>
                          <span className="text-xs text-muted-foreground">
                            {new Date(deviceData.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">데이터 없음</p>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* 알림 탭 */}
        <TabsContent value="alerts" className="space-y-4">
          <div className="space-y-4">
            {alerts.length > 0 ? (
              alerts.map((alert, index) => (
                <Card key={index} className={`border-l-4 ${getAlertSeverityColor(alert.severity)}`}>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {alert.severity === 'high' ? (
                          <AlertTriangle className="h-5 w-5 text-red-500" />
                        ) : alert.severity === 'medium' ? (
                          <AlertTriangle className="h-5 w-5 text-yellow-500" />
                        ) : (
                          <AlertTriangle className="h-5 w-5 text-blue-500" />
                        )}
                        <div>
                          <p className="font-medium">{alert.message}</p>
                          <p className="text-sm text-muted-foreground">
                            {alert.location} • {alert.device_id}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge variant={alert.severity === 'high' ? 'destructive' : 'secondary'}>
                          {alert.severity}
                        </Badge>
                        <p className="text-xs text-muted-foreground mt-1">
                          {new Date(alert.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-center py-8">
                    <CheckCircle className="h-8 w-8 text-green-500 mr-2" />
                    <span className="text-muted-foreground">현재 알림이 없습니다.</span>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* 분석 탭 */}
        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 온도 분석 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Thermometer className="h-5 w-5" />
                  온도 분석
                </CardTitle>
              </CardHeader>
              <CardContent>
                {dashboardData && (
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span>평균 온도</span>
                      <span className="font-medium">{dashboardData.temperature_summary.average}°C</span>
                    </div>
                    <Progress 
                      value={(dashboardData.temperature_summary.average / 40) * 100} 
                      className="w-full" 
                    />
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">최저:</span>
                        <span className="ml-2 font-medium">{dashboardData.temperature_summary.min}°C</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">최고:</span>
                        <span className="ml-2 font-medium">{dashboardData.temperature_summary.max}°C</span>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* 습도 분석 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Droplets className="h-5 w-5" />
                  습도 분석
                </CardTitle>
              </CardHeader>
              <CardContent>
                {dashboardData && (
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span>평균 습도</span>
                      <span className="font-medium">{dashboardData.humidity_summary.average}%</span>
                    </div>
                    <Progress 
                      value={dashboardData.humidity_summary.average} 
                      className="w-full" 
                    />
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">최저:</span>
                        <span className="ml-2 font-medium">{dashboardData.humidity_summary.min}%</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">최고:</span>
                        <span className="ml-2 font-medium">{dashboardData.humidity_summary.max}%</span>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* 재고 분석 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Scale className="h-5 w-5" />
                  재고 분석
                </CardTitle>
              </CardHeader>
              <CardContent>
                {dashboardData && (
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span>총 재고량</span>
                      <span className="font-medium">{dashboardData.inventory_summary.total_weight}kg</span>
                    </div>
                    <div className="flex justify-between">
                      <span>부족 재고</span>
                      <span className="font-medium">{dashboardData.inventory_summary.low_stock_count}개</span>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>재고 상태</span>
                        <span className="text-muted-foreground">
                          {dashboardData.inventory_summary.low_stock_count > 0 ? '주의' : '정상'}
                        </span>
                      </div>
                      {dashboardData.inventory_summary.low_stock_count > 0 && (
                        <Alert>
                          <AlertTriangle className="h-4 w-4" />
                          <AlertDescription>
                            {dashboardData.inventory_summary.low_stock_count}개의 재고가 부족합니다.
                          </AlertDescription>
                        </Alert>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* 기기 상태 분석 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  기기 상태
                </CardTitle>
              </CardHeader>
              <CardContent>
                {dashboardData && (
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span>온라인 기기</span>
                      <span className="font-medium text-green-600">{dashboardData.online_devices}개</span>
                    </div>
                    <div className="flex justify-between">
                      <span>오류 기기</span>
                      <span className="font-medium text-red-600">{dashboardData.error_devices}개</span>
                    </div>
                    <Progress 
                      value={(dashboardData.online_devices / dashboardData.total_devices) * 100} 
                      className="w-full" 
                    />
                    <div className="text-sm text-muted-foreground">
                      가동률: {((dashboardData.online_devices / dashboardData.total_devices) * 100).toFixed(1)}%
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default IoTDashboard; 