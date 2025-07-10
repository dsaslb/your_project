"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Server, 
  Database, 
  Activity, 
  Users, 
  Settings, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Cpu,
  HardDrive,
  Network,
  Shield,
  Zap,
  TrendingUp,
  BarChart3,
  RefreshCw
} from "lucide-react";

interface SystemStatus {
  server: 'online' | 'offline' | 'warning';
  database: 'online' | 'offline' | 'warning';
  api: 'online' | 'offline' | 'warning';
  memory: number;
  cpu: number;
  disk: number;
  activeConnections: number;
  uptime: string;
}

interface ApiMetrics {
  totalRequests: number;
  successRate: number;
  averageResponseTime: number;
  errorRate: number;
  endpoints: Array<{
    name: string;
    requests: number;
    errors: number;
    avgTime: number;
  }>;
}

export default function BackendDashboard() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    server: 'online',
    database: 'online',
    api: 'online',
    memory: 65,
    cpu: 45,
    disk: 78,
    activeConnections: 127,
    uptime: '15일 7시간 32분'
  });

  const [apiMetrics, setApiMetrics] = useState<ApiMetrics>({
    totalRequests: 15420,
    successRate: 98.5,
    averageResponseTime: 245,
    errorRate: 1.5,
    endpoints: [
      { name: '/api/auth/login', requests: 2340, errors: 12, avgTime: 180 },
      { name: '/api/dashboard/stats', requests: 1890, errors: 5, avgTime: 320 },
      { name: '/api/notifications', requests: 1560, errors: 8, avgTime: 210 },
      { name: '/api/orders', requests: 2890, errors: 15, avgTime: 450 },
      { name: '/api/staff', requests: 980, errors: 3, avgTime: 280 }
    ]
  });

  const [isRefreshing, setIsRefreshing] = useState(false);

  const refreshData = async () => {
    setIsRefreshing(true);
    // 실제 API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsRefreshing(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'offline': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'online': return '정상';
      case 'warning': return '주의';
      case 'offline': return '오프라인';
      default: return '알 수 없음';
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">백엔드 대시보드</h1>
          <p className="text-gray-600 dark:text-gray-400">시스템 전체 상태 및 성능 모니터링</p>
        </div>
        <Button onClick={refreshData} disabled={isRefreshing}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
          새로고침
        </Button>
      </div>

      {/* 시스템 상태 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">서버 상태</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${getStatusColor(systemStatus.server)}`} />
              <span className="text-2xl font-bold">{getStatusText(systemStatus.server)}</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">마지막 업데이트: 1분 전</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">데이터베이스</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${getStatusColor(systemStatus.database)}`} />
              <span className="text-2xl font-bold">{getStatusText(systemStatus.database)}</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">연결 풀: 15/20</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API 서비스</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${getStatusColor(systemStatus.api)}`} />
              <span className="text-2xl font-bold">{getStatusText(systemStatus.api)}</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">응답률: {apiMetrics.successRate}%</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">활성 연결</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStatus.activeConnections}</div>
            <p className="text-xs text-muted-foreground mt-1">동시 사용자</p>
          </CardContent>
        </Card>
      </div>

      {/* 시스템 리소스 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Cpu className="h-5 w-5 mr-2" />
              CPU 사용률
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>현재 사용률</span>
                <span>{systemStatus.cpu}%</span>
              </div>
              <Progress value={systemStatus.cpu} className="h-2" />
              <p className="text-xs text-muted-foreground">임계값: 80%</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <HardDrive className="h-5 w-5 mr-2" />
              메모리 사용률
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>현재 사용률</span>
                <span>{systemStatus.memory}%</span>
              </div>
              <Progress value={systemStatus.memory} className="h-2" />
              <p className="text-xs text-muted-foreground">사용 중: 8.2GB / 12.8GB</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Network className="h-5 w-5 mr-2" />
              디스크 사용률
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>현재 사용률</span>
                <span>{systemStatus.disk}%</span>
              </div>
              <Progress value={systemStatus.disk} className="h-2" />
              <p className="text-xs text-muted-foreground">사용 중: 156GB / 200GB</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* API 메트릭스 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="h-5 w-5 mr-2" />
            API 성능 메트릭스
          </CardTitle>
          <CardDescription>실시간 API 호출 통계 및 성능 지표</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{apiMetrics.totalRequests.toLocaleString()}</div>
              <p className="text-sm text-muted-foreground">총 요청 수</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{apiMetrics.successRate}%</div>
              <p className="text-sm text-muted-foreground">성공률</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{apiMetrics.averageResponseTime}ms</div>
              <p className="text-sm text-muted-foreground">평균 응답시간</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{apiMetrics.errorRate}%</div>
              <p className="text-sm text-muted-foreground">오류율</p>
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="font-semibold">엔드포인트별 통계</h4>
            {apiMetrics.endpoints.map((endpoint, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex-1">
                  <p className="font-medium">{endpoint.name}</p>
                  <p className="text-sm text-muted-foreground">
                    요청: {endpoint.requests.toLocaleString()} | 
                    오류: {endpoint.errors} | 
                    평균: {endpoint.avgTime}ms
                  </p>
                </div>
                <Badge variant={endpoint.errors > 10 ? "destructive" : "secondary"}>
                  {((endpoint.errors / endpoint.requests) * 100).toFixed(1)}% 오류
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 시스템 정보 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Settings className="h-5 w-5 mr-2" />
              시스템 정보
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">서버 가동시간</span>
              <span className="font-medium">{systemStatus.uptime}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">서버 버전</span>
              <span className="font-medium">v2.1.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Python 버전</span>
              <span className="font-medium">3.10.4</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Flask 버전</span>
              <span className="font-medium">2.3.3</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">데이터베이스</span>
              <span className="font-medium">PostgreSQL 14.8</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Shield className="h-5 w-5 mr-2" />
              보안 상태
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-sm">SSL 인증서 유효</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-sm">방화벽 활성화</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-sm">백업 시스템 정상</span>
            </div>
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-4 w-4 text-yellow-500" />
              <span className="text-sm">로그 모니터링 필요</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-sm">자동 업데이트 활성</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 