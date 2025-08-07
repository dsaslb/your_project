'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { 
  Activity, 
  Route, 
  Settings, 
  BarChart3, 
  Plus, 
  Edit, 
  Trash2, 
  RefreshCw, 
  Shield, 
  Zap,
  Clock,
  Database,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';
import { toast } from 'sonner';

// 인터페이스 정의
interface APIRoute {
  route_id: string;
  name: string;
  path: string;
  method: string;
  target_url: string;
  service_name: string;
  is_active: boolean;
  requires_auth: boolean;
  created_at: string;
}

interface GatewayStats {
  total_routes: number;
  active_routes: number;
  total_metrics: number;
  requests_last_hour?: number;
  avg_response_time?: number;
  success_rate?: number;
}

interface GatewayConfig {
  data_dir: string;
  rate_limit_window: number;
  rate_limit_max_requests: number;
  enable_rate_limiting: boolean;
  enable_logging: boolean;
}

// 샘플 데이터
const sampleRoutes: APIRoute[] = [
  {
    route_id: '1',
    name: '사용자 API',
    path: '/api/users',
    method: 'GET',
    target_url: 'http://user-service:3001',
    service_name: 'user-service',
    is_active: true,
    requires_auth: true,
    created_at: '2024-01-01T00:00:00Z'
  },
  {
    route_id: '2',
    name: '주문 API',
    path: '/api/orders',
    method: 'POST',
    target_url: 'http://order-service:3002',
    service_name: 'order-service',
    is_active: true,
    requires_auth: true,
    created_at: '2024-01-01T00:00:00Z'
  },
  {
    route_id: '3',
    name: '상품 API',
    path: '/api/products',
    method: 'GET',
    target_url: 'http://product-service:3003',
    service_name: 'product-service',
    is_active: false,
    requires_auth: false,
    created_at: '2024-01-01T00:00:00Z'
  }
];

const sampleStats: GatewayStats = {
  total_routes: 3,
  active_routes: 2,
  total_metrics: 45,
  requests_last_hour: 1250,
  avg_response_time: 245,
  success_rate: 98.5
};

const sampleConfig: GatewayConfig = {
  data_dir: '/var/lib/gateway',
  rate_limit_window: 3600,
  rate_limit_max_requests: 1000,
  enable_rate_limiting: true,
  enable_logging: true
};

export default function GatewayPage() {
  // 상태 관리
  const [routes, setRoutes] = useState<APIRoute[]>([]);
  const [stats, setStats] = useState<GatewayStats | null>(null);
  const [config, setConfig] = useState<GatewayConfig | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // 다이얼로그 상태
  const [isCreateRouteOpen, setIsCreateRouteOpen] = useState(false);
  
  // 폼 상태
  const [newRoute, setNewRoute] = useState({
    name: '',
    path: '',
    method: 'GET',
    target_url: '',
    service_name: '',
    is_active: true,
    requires_auth: true
  });
  
  // 데이터 로드
  useEffect(() => {
    loadGatewayData();
  }, []);
  
  const loadGatewayData = async () => {
    try {
      setIsLoading(true);
      setRoutes(sampleRoutes);
      setStats(sampleStats);
      setConfig(sampleConfig);
    } catch (error) {
      toast.error('게이트웨이 데이터를 불러오는데 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };
  
  const createRoute = async () => {
    if (!newRoute.name || !newRoute.path || !newRoute.target_url || !newRoute.service_name) {
      toast.error('필수 필드를 입력해주세요');
      return;
    }

    try {
      setIsLoading(true);
      const route: APIRoute = {
        route_id: (routes.length + 1).toString(),
        name: newRoute.name,
        path: newRoute.path,
        method: newRoute.method,
        target_url: newRoute.target_url,
        service_name: newRoute.service_name,
        is_active: newRoute.is_active,
        requires_auth: newRoute.requires_auth,
        created_at: new Date().toISOString()
      };
      
      setRoutes(prev => [...prev, route]);
      setIsCreateRouteOpen(false);
      setNewRoute({
        name: '',
        path: '',
        method: 'GET',
        target_url: '',
        service_name: '',
        is_active: true,
        requires_auth: true
      });
      toast.success('API 라우트가 생성되었습니다');
    } catch (error) {
      toast.error('API 라우트 생성에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };
  
  const deleteRoute = async (routeId: string) => {
    try {
      setIsLoading(true);
      setRoutes(prev => prev.filter(route => route.route_id !== routeId));
      toast.success('API 라우트가 삭제되었습니다');
    } catch (error) {
      toast.error('API 라우트 삭제에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };
  
  const updateConfig = async (updates: Partial<GatewayConfig>) => {
    try {
      setIsLoading(true);
      setConfig(prev => prev ? { ...prev, ...updates } : null);
      toast.success('설정이 업데이트되었습니다');
    } catch (error) {
      toast.error('설정 업데이트에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };
  
  const clearCache = async () => {
    try {
      setIsLoading(true);
      toast.success('캐시가 정리되었습니다');
    } catch (error) {
      toast.error('캐시 정리에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };
  
  const getMethodColor = (method: string) => {
    switch (method) {
      case 'GET': return 'bg-green-500/20 text-green-400';
      case 'POST': return 'bg-blue-500/20 text-blue-400';
      case 'PUT': return 'bg-yellow-500/20 text-yellow-400';
      case 'DELETE': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ko-KR');
  };

  return (
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Route className="w-8 h-8 text-blue-400" />
          API 게이트웨이
        </h1>
        <p className="text-gray-300 mt-2">API 라우팅 및 요청 관리를 담당합니다</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-3 mb-6">
        <Button 
          onClick={() => setIsCreateRouteOpen(true)}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          라우트 생성
        </Button>
        <Button 
          onClick={clearCache}
          variant="outline"
          className="border-white/20 text-white hover:bg-white/10"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          캐시 정리
        </Button>
        <Button 
          onClick={loadGatewayData}
          variant="outline"
          className="border-white/20 text-white hover:bg-white/10"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          새로고침
        </Button>
      </div>

      {/* 게이트웨이 통계 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">총 라우트</CardTitle>
              <Route className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.total_routes}</div>
              <p className="text-xs text-gray-300">활성: {stats.active_routes}개</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">요청 수</CardTitle>
              <Activity className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.requests_last_hour?.toLocaleString()}</div>
              <p className="text-xs text-gray-300">지난 1시간</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">응답 시간</CardTitle>
              <Clock className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.avg_response_time}ms</div>
              <p className="text-xs text-gray-300">평균 응답 시간</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white">성공률</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.success_rate?.toFixed(1)}%</div>
              <Progress value={stats.success_rate || 0} className="mt-2" />
            </CardContent>
          </Card>
        </div>
      )}

      {/* 메인 탭 */}
      <Tabs defaultValue="routes" className="space-y-4">
        <TabsList className="bg-white/10 border border-white/20">
          <TabsTrigger value="routes" className="text-white data-[state=active]:bg-white/20">라우트</TabsTrigger>
          <TabsTrigger value="config" className="text-white data-[state=active]:bg-white/20">설정</TabsTrigger>
        </TabsList>

        {/* 라우트 탭 */}
        <TabsContent value="routes" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <CardTitle className="text-white">API 라우트</CardTitle>
              <CardDescription className="text-gray-300">등록된 API 라우트를 관리합니다</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {routes.map((route) => (
                  <div key={route.route_id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-medium text-white">{route.name}</h3>
                          <Badge className={getMethodColor(route.method)}>
                            {route.method}
                          </Badge>
                          <Badge className={route.is_active ? "bg-green-500/20 text-green-400" : "bg-gray-500/20 text-gray-400"}>
                            {route.is_active ? '활성' : '비활성'}
                          </Badge>
                          {route.requires_auth && (
                            <Badge className="bg-blue-500/20 text-blue-400">
                              인증 필요
                            </Badge>
                          )}
                        </div>
                        <div className="text-sm text-gray-300 space-y-1">
                          <div>경로: {route.path}</div>
                          <div>대상: {route.target_url}</div>
                          <div>서비스: {route.service_name}</div>
                          <div>생성일: {formatDate(route.created_at)}</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setRoutes(prev => prev.map(r => 
                              r.route_id === route.route_id ? { ...r, is_active: !r.is_active } : r
                            ));
                            toast.success(`라우트가 ${!route.is_active ? '활성화' : '비활성화'}되었습니다`);
                          }}
                          className="border-white/20 text-white hover:bg-white/10"
                        >
                          {route.is_active ? '비활성화' : '활성화'}
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => deleteRoute(route.route_id)}
                          className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
                
                {routes.length === 0 && (
                  <div className="text-center py-8 text-gray-300">
                    등록된 API 라우트가 없습니다.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 설정 탭 */}
        <TabsContent value="config" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <CardTitle className="text-white">게이트웨이 설정</CardTitle>
              <CardDescription className="text-gray-300">게이트웨이 동작 설정을 관리합니다</CardDescription>
            </CardHeader>
            <CardContent>
              {config && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label className="text-gray-300">데이터 디렉토리</Label>
                      <Input
                        value={config.data_dir}
                        onChange={(e) => updateConfig({ data_dir: e.target.value })}
                        className="bg-white/10 border-white/20 text-white"
                      />
                    </div>
                    <div>
                      <Label className="text-gray-300">속도 제한 창 (초)</Label>
                      <Input
                        type="number"
                        value={config.rate_limit_window}
                        onChange={(e) => updateConfig({ rate_limit_window: parseInt(e.target.value) })}
                        className="bg-white/10 border-white/20 text-white"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label className="text-gray-300">최대 요청 수</Label>
                      <Input
                        type="number"
                        value={config.rate_limit_max_requests}
                        onChange={(e) => updateConfig({ rate_limit_max_requests: parseInt(e.target.value) })}
                        className="bg-white/10 border-white/20 text-white"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label className="text-gray-300">속도 제한 활성화</Label>
                        <p className="text-sm text-gray-400">API 요청 속도 제한을 활성화합니다</p>
                      </div>
                      <Switch
                        checked={config.enable_rate_limiting}
                        onCheckedChange={(checked) => updateConfig({ enable_rate_limiting: checked })}
                      />
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <Label className="text-gray-300">로깅 활성화</Label>
                        <p className="text-sm text-gray-400">API 요청 로깅을 활성화합니다</p>
                      </div>
                      <Switch
                        checked={config.enable_logging}
                        onCheckedChange={(checked) => updateConfig({ enable_logging: checked })}
                      />
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 라우트 생성 다이얼로그 */}
      <Dialog open={isCreateRouteOpen} onOpenChange={setIsCreateRouteOpen}>
        <DialogContent className="max-w-md bg-white/10 backdrop-blur-sm border border-white/20">
          <DialogHeader>
            <DialogTitle className="text-white">API 라우트 생성</DialogTitle>
            <DialogDescription className="text-gray-300">새로운 API 라우트를 생성합니다</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label className="text-gray-300">라우트 이름</Label>
              <Input
                value={newRoute.name}
                onChange={(e) => setNewRoute(prev => ({ ...prev, name: e.target.value }))}
                placeholder="라우트 이름을 입력하세요"
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              />
            </div>
            
            <div>
              <Label className="text-gray-300">경로</Label>
              <Input
                value={newRoute.path}
                onChange={(e) => setNewRoute(prev => ({ ...prev, path: e.target.value }))}
                placeholder="/api/example"
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              />
            </div>
            
            <div>
              <Label className="text-gray-300">HTTP 메서드</Label>
              <Select value={newRoute.method} onValueChange={(value) => setNewRoute(prev => ({ ...prev, method: value }))}>
                <SelectTrigger className="bg-white/10 border-white/20 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white/10 border-white/20">
                  <SelectItem value="GET">GET</SelectItem>
                  <SelectItem value="POST">POST</SelectItem>
                  <SelectItem value="PUT">PUT</SelectItem>
                  <SelectItem value="DELETE">DELETE</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label className="text-gray-300">대상 URL</Label>
              <Input
                value={newRoute.target_url}
                onChange={(e) => setNewRoute(prev => ({ ...prev, target_url: e.target.value }))}
                placeholder="http://service:port"
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              />
            </div>
            
            <div>
              <Label className="text-gray-300">서비스 이름</Label>
              <Input
                value={newRoute.service_name}
                onChange={(e) => setNewRoute(prev => ({ ...prev, service_name: e.target.value }))}
                placeholder="service-name"
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              />
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-gray-300">활성화</Label>
                  <p className="text-sm text-gray-400">라우트를 즉시 활성화합니다</p>
                </div>
                <Switch
                  checked={newRoute.is_active}
                  onCheckedChange={(checked) => setNewRoute(prev => ({ ...prev, is_active: checked }))}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-gray-300">인증 필요</Label>
                  <p className="text-sm text-gray-400">이 라우트에 인증이 필요합니다</p>
                </div>
                <Switch
                  checked={newRoute.requires_auth}
                  onCheckedChange={(checked) => setNewRoute(prev => ({ ...prev, requires_auth: checked }))}
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button 
                onClick={createRoute}
                disabled={isLoading}
                className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
              >
                {isLoading ? "생성 중..." : "라우트 생성"}
              </Button>
              <Button 
                variant="outline" 
                onClick={() => setIsCreateRouteOpen(false)}
                className="border-white/20 text-white hover:bg-white/10"
              >
                취소
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
} 