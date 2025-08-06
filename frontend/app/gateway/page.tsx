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
import { ApiClient } from '@/lib/api-client';
import { useLoadingState } from '@/hooks/useLoadingState';
import { useErrorHandler } from '@/hooks/useErrorHandler';

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

export default function GatewayPage() {
  // 상태 관리
  const [routes, setRoutes] = useState<APIRoute[]>([]);
  const [stats, setStats] = useState<GatewayStats | null>(null);
  const [config, setConfig] = useState<GatewayConfig | null>(null);
  
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
  
  // 로딩 및 에러 처리
  const { loading, setLoading } = useLoadingState();
  const { error, handleError, clearError } = useErrorHandler();
  
  // API 클라이언트
    // 데이터 로드
  useEffect(() => {
    loadGatewayData();
  }, []);
  
  const loadGatewayData = async () => {
    try {
      setLoading(true);
      clearError();
      
      const [statsRes, routesRes, configRes] = await Promise.all([
        apiClient.get('/api/gateway/stats'),
        apiClient.get('/api/gateway/routes'),
        apiClient.get('/api/gateway/config')
      ]);
      
      setStats(statsRes.data);
      setRoutes(routesRes.data);
      setConfig(configRes.data);
      
    } catch (err) {
      handleError(err, '게이트웨이 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };
  
  // 라우트 생성
  const createRoute = async () => {
    try {
      setLoading(true);
      clearError();
      
      await apiClient.post('/api/gateway/routes', newRoute);
      
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
      
      await loadGatewayData();
      
    } catch (err) {
      handleError(err, '라우트 생성 실패');
    } finally {
      setLoading(false);
    }
  };
  
  // 라우트 삭제
  const deleteRoute = async (routeId: string) => {
    if (!confirm('정말로 이 라우트를 삭제하시겠습니까?')) return;
    
    try {
      setLoading(true);
      clearError();
      
      await apiClient.delete(`/api/gateway/routes/${routeId}`);
      await loadGatewayData();
      
    } catch (err) {
      handleError(err, '라우트 삭제 실패');
    } finally {
      setLoading(false);
    }
  };
  
  // 설정 업데이트
  const updateConfig = async (updates: Partial<GatewayConfig>) => {
    if (!config) return;
    
    try {
      setLoading(true);
      clearError();
      
      const updatedConfig = { ...config, ...updates };
      await apiClient.put('/api/gateway/config', updatedConfig);
      setConfig(updatedConfig);
      
    } catch (err) {
      handleError(err, '설정 업데이트 실패');
    } finally {
      setLoading(false);
    }
  };
  
  // 캐시 정리
  const clearCache = async () => {
    try {
      setLoading(true);
      clearError();
      
      await apiClient.post('/api/gateway/cache/clear');
      alert('캐시가 정리되었습니다.');
      
    } catch (err) {
      handleError(err, '캐시 정리 실패');
    } finally {
      setLoading(false);
    }
  };
  
  // HTTP 메서드 색상
  const getMethodColor = (method: string) => {
    switch (method.toUpperCase()) {
      case 'GET': return 'bg-green-100 text-green-800';
      case 'POST': return 'bg-blue-100 text-blue-800';
      case 'PUT': return 'bg-yellow-100 text-yellow-800';
      case 'DELETE': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };
  
  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">API 게이트웨이 관리</h1>
          <p className="text-gray-600 mt-2">API 라우팅, 인증, 속도 제한, 모니터링을 관리합니다</p>
        </div>
        <Button onClick={loadGatewayData} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          새로고침
        </Button>
      </div>
      
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 라우트</CardTitle>
            <Route className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_routes || 0}</div>
            <p className="text-xs text-muted-foreground">
              활성: {stats?.active_routes || 0}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 요청</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_metrics || 0}</div>
            <p className="text-xs text-muted-foreground">
              최근 1시간: {stats?.requests_last_hour || 0}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평균 응답 시간</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.avg_response_time ? `${stats.avg_response_time.toFixed(2)}ms` : '0ms'}
            </div>
            <p className="text-xs text-muted-foreground">
              성공률: {stats?.success_rate ? `${stats.success_rate.toFixed(1)}%` : '0%'}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">시스템 상태</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium">정상</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              모든 서비스 운영 중
            </p>
          </CardContent>
        </Card>
      </div>
      
      {/* 메인 탭 */}
      <Tabs defaultValue="routes" className="space-y-6">
        <TabsList>
          <TabsTrigger value="routes">라우트 관리</TabsTrigger>
          <TabsTrigger value="settings">설정</TabsTrigger>
        </TabsList>
        
        {/* 라우트 관리 탭 */}
        <TabsContent value="routes" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>API 라우트</CardTitle>
                  <CardDescription>등록된 API 라우트를 관리합니다</CardDescription>
                </div>
                <Dialog open={isCreateRouteOpen} onOpenChange={setIsCreateRouteOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="w-4 h-4 mr-2" />
                      새 라우트
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[500px]">
                    <DialogHeader>
                      <DialogTitle>새 API 라우트 생성</DialogTitle>
                      <DialogDescription>
                        새로운 API 라우트를 생성합니다
                      </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="name" className="text-right">이름</Label>
                        <Input
                          id="name"
                          value={newRoute.name}
                          onChange={(e) => setNewRoute({...newRoute, name: e.target.value})}
                          className="col-span-3"
                        />
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="path" className="text-right">경로</Label>
                        <Input
                          id="path"
                          value={newRoute.path}
                          onChange={(e) => setNewRoute({...newRoute, path: e.target.value})}
                          className="col-span-3"
                          placeholder="/api/example"
                        />
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="method" className="text-right">메서드</Label>
                        <Select value={newRoute.method} onValueChange={(value) => setNewRoute({...newRoute, method: value})}>
                          <SelectTrigger className="col-span-3">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="GET">GET</SelectItem>
                            <SelectItem value="POST">POST</SelectItem>
                            <SelectItem value="PUT">PUT</SelectItem>
                            <SelectItem value="DELETE">DELETE</SelectItem>
                            <SelectItem value="PATCH">PATCH</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="target_url" className="text-right">대상 URL</Label>
                        <Input
                          id="target_url"
                          value={newRoute.target_url}
                          onChange={(e) => setNewRoute({...newRoute, target_url: e.target.value})}
                          className="col-span-3"
                          placeholder="http://localhost:5001/api/service"
                        />
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="service_name" className="text-right">서비스명</Label>
                        <Input
                          id="service_name"
                          value={newRoute.service_name}
                          onChange={(e) => setNewRoute({...newRoute, service_name: e.target.value})}
                          className="col-span-3"
                        />
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label className="text-right">활성화</Label>
                        <div className="col-span-3 flex items-center space-x-2">
                          <Switch
                            checked={newRoute.is_active}
                            onCheckedChange={(checked) => setNewRoute({...newRoute, is_active: checked})}
                          />
                          <Label>라우트 활성화</Label>
                        </div>
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label className="text-right">인증 필요</Label>
                        <div className="col-span-3 flex items-center space-x-2">
                          <Switch
                            checked={newRoute.requires_auth}
                            onCheckedChange={(checked) => setNewRoute({...newRoute, requires_auth: checked})}
                          />
                          <Label>인증 토큰 필요</Label>
                        </div>
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsCreateRouteOpen(false)}>
                        취소
                      </Button>
                      <Button onClick={createRoute} disabled={loading}>
                        생성
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>이름</TableHead>
                    <TableHead>경로</TableHead>
                    <TableHead>메서드</TableHead>
                    <TableHead>대상 URL</TableHead>
                    <TableHead>상태</TableHead>
                    <TableHead>인증</TableHead>
                    <TableHead>작업</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {routes.map((route) => (
                    <TableRow key={route.route_id}>
                      <TableCell className="font-medium">{route.name}</TableCell>
                      <TableCell className="font-mono text-sm">{route.path}</TableCell>
                      <TableCell>
                        <Badge className={getMethodColor(route.method)}>
                          {route.method}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-sm max-w-[200px] truncate">
                        {route.target_url}
                      </TableCell>
                      <TableCell>
                        {route.is_active ? (
                          <Badge variant="default">활성</Badge>
                        ) : (
                          <Badge variant="secondary">비활성</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        {route.requires_auth ? (
                          <Shield className="h-4 w-4 text-blue-600" />
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => deleteRoute(route.route_id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* 설정 탭 */}
        <TabsContent value="settings" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 게이트웨이 설정 */}
            <Card>
              <CardHeader>
                <CardTitle>게이트웨이 설정</CardTitle>
                <CardDescription>게이트웨이 동작 설정을 관리합니다</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {config && (
                  <>
                    <div className="space-y-2">
                      <Label>속도 제한 윈도우 (초)</Label>
                      <Input
                        type="number"
                        value={config.rate_limit_window}
                        onChange={(e) => updateConfig({rate_limit_window: parseInt(e.target.value)})}
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label>최대 요청 수</Label>
                      <Input
                        type="number"
                        value={config.rate_limit_max_requests}
                        onChange={(e) => updateConfig({rate_limit_max_requests: parseInt(e.target.value)})}
                      />
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Switch
                        checked={config.enable_rate_limiting}
                        onCheckedChange={(checked) => updateConfig({enable_rate_limiting: checked})}
                      />
                      <Label>속도 제한 활성화</Label>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Switch
                        checked={config.enable_logging}
                        onCheckedChange={(checked) => updateConfig({enable_logging: checked})}
                      />
                      <Label>로깅 활성화</Label>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
            
            {/* 시스템 관리 */}
            <Card>
              <CardHeader>
                <CardTitle>시스템 관리</CardTitle>
                <CardDescription>캐시 및 속도 제한 데이터를 관리합니다</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>캐시 관리</Label>
                  <Button variant="outline" onClick={clearCache} disabled={loading}>
                    <Database className="w-4 h-4 mr-2" />
                    캐시 정리
                  </Button>
                </div>
                
                <div className="pt-4 border-t">
                  <p className="text-sm text-muted-foreground">
                    데이터 디렉토리: {config?.data_dir}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
} 