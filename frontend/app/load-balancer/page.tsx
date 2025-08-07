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
import { useLoadingState } from '@/hooks/useLoadingState';
import { useErrorHandler } from '@/hooks/useErrorHandler';
import { apiClient } from '@/lib/api-client';
import { 
  Activity, 
  Server, 
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
  CheckCircle,
  Network,
  Users,
  Globe
} from 'lucide-react';
import { toast } from 'sonner';

// 인터페이스 정의
interface Server {
  server_id: string;
  name: string;
  host: string;
  port: number;
  protocol: string;
  weight: number;
  max_connections: number;
  is_active: boolean;
  status: string;
  health_check_url: string;
  created_at: string;
  updated_at: string;
}

interface ServerGroup {
  group_id: string;
  name: string;
  algorithm: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  servers: Server[];
}

interface LoadBalancerStats {
  total_groups: number;
  active_groups: number;
  total_servers: number;
  healthy_servers: number;
  unhealthy_servers: number;
  total_connections: number;
  total_metrics: number;
  active_sessions: number;
  requests_last_hour?: number;
  avg_response_time?: number;
  success_rate?: number;
  group_stats?: Array<{
    group_id: string;
    name: string;
    algorithm: string;
    healthy_servers: number;
    total_servers: number;
    health_rate: number;
  }>;
}

interface LoadBalancerConfig {
  data_dir: string;
  health_check_interval: number;
  health_check_timeout: number;
  max_failures: number;
  enable_sticky_sessions: boolean;
  session_timeout: number;
}

// 샘플 데이터
const sampleServers: Server[] = [
  {
    server_id: '1',
    name: '웹서버-01',
    host: '192.168.1.10',
    port: 8080,
    protocol: 'http',
    weight: 1,
    max_connections: 1000,
    is_active: true,
    status: 'healthy',
    health_check_url: '/health',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-15T10:30:00Z'
  },
  {
    server_id: '2',
    name: '웹서버-02',
    host: '192.168.1.11',
    port: 8080,
    protocol: 'http',
    weight: 1,
    max_connections: 1000,
    is_active: true,
    status: 'healthy',
    health_check_url: '/health',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-15T10:30:00Z'
  },
  {
    server_id: '3',
    name: '웹서버-03',
    host: '192.168.1.12',
    port: 8080,
    protocol: 'http',
    weight: 1,
    max_connections: 1000,
    is_active: false,
    status: 'unhealthy',
    health_check_url: '/health',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-15T10:30:00Z'
  }
];

const sampleServerGroups: ServerGroup[] = [
  {
    group_id: '1',
    name: '웹서버 그룹',
    algorithm: 'round_robin',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-15T10:30:00Z',
    servers: sampleServers.slice(0, 2)
  },
  {
    group_id: '2',
    name: 'API 서버 그룹',
    algorithm: 'least_connections',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-15T10:30:00Z',
    servers: sampleServers.slice(1, 3)
  }
];

const sampleStats: LoadBalancerStats = {
  total_groups: 2,
  active_groups: 2,
  total_servers: 3,
  healthy_servers: 2,
  unhealthy_servers: 1,
  total_connections: 1250,
  total_metrics: 45,
  active_sessions: 850,
  requests_last_hour: 15420,
  avg_response_time: 245,
  success_rate: 98.5,
  group_stats: [
    {
      group_id: '1',
      name: '웹서버 그룹',
      algorithm: 'round_robin',
      healthy_servers: 2,
      total_servers: 2,
      health_rate: 100
    },
    {
      group_id: '2',
      name: 'API 서버 그룹',
      algorithm: 'least_connections',
      healthy_servers: 1,
      total_servers: 2,
      health_rate: 50
    }
  ]
};

const sampleConfig: LoadBalancerConfig = {
  data_dir: '/var/lib/loadbalancer',
  health_check_interval: 30,
  health_check_timeout: 5,
  max_failures: 3,
  enable_sticky_sessions: true,
  session_timeout: 3600
};

export default function LoadBalancerPage() {
  // 상태 관리
  const [serverGroups, setServerGroups] = useState<ServerGroup[]>([]);
  const [stats, setStats] = useState<LoadBalancerStats | null>(null);
  const [config, setConfig] = useState<LoadBalancerConfig | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // 다이얼로그 상태
  const [isCreateGroupOpen, setIsCreateGroupOpen] = useState(false);
  const [isAddServerOpen, setIsAddServerOpen] = useState(false);
  const [selectedGroupId, setSelectedGroupId] = useState<string>('');
  
  // 폼 상태
  const [newGroup, setNewGroup] = useState({
    name: '',
    algorithm: 'round_robin',
    is_active: true
  });
  
  const [newServer, setNewServer] = useState({
    name: '',
    host: '',
    port: 80,
    protocol: 'http',
    weight: 100,
    max_connections: 1000,
    health_check_url: '/health'
  });
  
  // 로딩 및 에러 처리
  const { loading, setLoading } = useLoadingState();
  const { error, handleError, clearError } = useErrorHandler();
  
  // API 클라이언트
    // 데이터 로드
  useEffect(() => {
    loadLoadBalancerData();
  }, []);
  
  const loadLoadBalancerData = async () => {
    try {
      setLoading(true);
      clearError();
      
      const [statsRes, groupsRes, configRes] = await Promise.all([
        apiClient.get('/api/load-balancer/stats'),
        apiClient.get('/api/load-balancer/groups'),
        apiClient.get('/api/load-balancer/config')
      ]);
      
      setStats(statsRes.data);
      setServerGroups(groupsRes.data);
      setConfig(configRes.data);
      
    } catch (err) {
      handleError(err, '로드 밸런서 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };
  
  // 서버 그룹 관리
  const createServerGroup = async () => {
    try {
      setLoading(true);
      clearError();
      
      await apiClient.post('/api/load-balancer/groups', newGroup);
      
      setIsCreateGroupOpen(false);
      setNewGroup({
        name: '',
        algorithm: 'round_robin',
        is_active: true
      });
      
      await loadLoadBalancerData();
      
    } catch (err) {
      handleError(err, '서버 그룹 생성 실패');
    } finally {
      setLoading(false);
    }
  };
  
  const deleteServerGroup = async (groupId: string) => {
    if (!confirm('정말로 이 서버 그룹을 삭제하시겠습니까? 모든 서버도 함께 삭제됩니다.')) return;
    
    try {
      setLoading(true);
      clearError();
      
      await apiClient.delete(`/api/load-balancer/groups/${groupId}`);
      await loadLoadBalancerData();
      
    } catch (err) {
      handleError(err, '서버 그룹 삭제 실패');
    } finally {
      setLoading(false);
    }
  };
  
  const addServerToGroup = async () => {
    try {
      setLoading(true);
      clearError();
      
      await apiClient.post(`/api/load-balancer/groups/${selectedGroupId}/servers`, newServer);
      
      setIsAddServerOpen(false);
      setNewServer({
        name: '',
        host: '',
        port: 80,
        protocol: 'http',
        weight: 100,
        max_connections: 1000,
        health_check_url: '/health'
      });
      
      await loadLoadBalancerData();
      
    } catch (err) {
      handleError(err, '서버 추가 실패');
    } finally {
      setLoading(false);
    }
  };
  
  const deleteServer = async (serverId: string) => {
    if (!confirm('정말로 이 서버를 삭제하시겠습니까?')) return;
    
    try {
      setLoading(true);
      clearError();
      
      await apiClient.delete(`/api/load-balancer/servers/${serverId}`);
      await loadLoadBalancerData();
      
    } catch (err) {
      handleError(err, '서버 삭제 실패');
    } finally {
      setLoading(false);
    }
  };
  
  const performHealthCheck = async (serverId: string) => {
    try {
      setLoading(true);
      clearError();
      
      await apiClient.post(`/api/load-balancer/servers/${serverId}/health`);
      await loadLoadBalancerData();
      
    } catch (err) {
      handleError(err, '헬스 체크 수행 실패');
    } finally {
      setLoading(false);
    }
  };
  
  // 설정 관리
  const updateConfig = async (updates: Partial<LoadBalancerConfig>) => {
    if (!config) return;
    
    try {
      setLoading(true);
      clearError();
      
      const updatedConfig = { ...config, ...updates };
      await apiClient.put('/api/load-balancer/config', updatedConfig);
      setConfig(updatedConfig);
      
    } catch (err) {
      handleError(err, '설정 업데이트 실패');
    } finally {
      setLoading(false);
    }
  };
  
  // 세션 및 연결 정리
  const clearSessions = async () => {
    try {
      setLoading(true);
      clearError();
      
      await apiClient.post('/api/load-balancer/sessions/clear');
      alert('세션 매핑이 정리되었습니다.');
      
    } catch (err) {
      handleError(err, '세션 정리 실패');
    } finally {
      setLoading(false);
    }
  };
  
  const clearConnections = async () => {
    try {
      setLoading(true);
      clearError();
      
      await apiClient.post('/api/load-balancer/connections/clear');
      alert('연결 수 카운터가 정리되었습니다.');
      
    } catch (err) {
      handleError(err, '연결 수 정리 실패');
    } finally {
      setLoading(false);
    }
  };
  
  // 상태 색상
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'healthy': return <Badge variant="default">정상</Badge>;
      case 'unhealthy': return <Badge variant="destructive">비정상</Badge>;
      case 'maintenance': return <Badge variant="secondary">점검</Badge>;
      case 'offline': return <Badge variant="outline">오프라인</Badge>;
      default: return <Badge variant="outline">알 수 없음</Badge>;
    }
  };
  
  // 알고리즘 이름
  const getAlgorithmName = (algorithm: string) => {
    switch (algorithm) {
      case 'round_robin': return '라운드 로빈';
      case 'weighted_round_robin': return '가중치 라운드 로빈';
      case 'least_connections': return '최소 연결';
      case 'ip_hash': return 'IP 해시';
      default: return algorithm;
    }
  };
  
  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">로드 밸런서 관리</h1>
          <p className="text-gray-600 mt-2">서버 그룹, 로드 밸런싱, 헬스 체크를 관리합니다</p>
        </div>
        <Button onClick={loadLoadBalancerData} disabled={loading}>
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
            <CardTitle className="text-sm font-medium">총 그룹</CardTitle>
            <Network className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_groups || 0}</div>
            <p className="text-xs text-muted-foreground">
              활성: {stats?.active_groups || 0}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 서버</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_servers || 0}</div>
            <p className="text-xs text-muted-foreground">
              정상: {stats?.healthy_servers || 0} | 비정상: {stats?.unhealthy_servers || 0}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 연결</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_connections || 0}</div>
            <p className="text-xs text-muted-foreground">
              활성 세션: {stats?.active_sessions || 0}
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
              모든 서버 운영 중
            </p>
          </CardContent>
        </Card>
      </div>
      
      {/* 메인 탭 */}
      <Tabs defaultValue="groups" className="space-y-6">
        <TabsList>
          <TabsTrigger value="groups">서버 그룹</TabsTrigger>
          <TabsTrigger value="settings">설정</TabsTrigger>
        </TabsList>
        
        {/* 서버 그룹 탭 */}
        <TabsContent value="groups" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>서버 그룹</CardTitle>
                  <CardDescription>로드 밸런싱을 위한 서버 그룹을 관리합니다</CardDescription>
                </div>
                <Dialog open={isCreateGroupOpen} onOpenChange={setIsCreateGroupOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="w-4 h-4 mr-2" />
                      새 그룹
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[500px]">
                    <DialogHeader>
                      <DialogTitle>새 서버 그룹 생성</DialogTitle>
                      <DialogDescription>
                        새로운 서버 그룹을 생성합니다
                      </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="group-name" className="text-right">그룹명</Label>
                        <Input
                          id="group-name"
                          value={newGroup.name}
                          onChange={(e) => setNewGroup({...newGroup, name: e.target.value})}
                          className="col-span-3"
                        />
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="algorithm" className="text-right">알고리즘</Label>
                        <Select value={newGroup.algorithm} onValueChange={(value) => setNewGroup({...newGroup, algorithm: value})}>
                          <SelectTrigger className="col-span-3">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="round_robin">라운드 로빈</SelectItem>
                            <SelectItem value="weighted_round_robin">가중치 라운드 로빈</SelectItem>
                            <SelectItem value="least_connections">최소 연결</SelectItem>
                            <SelectItem value="ip_hash">IP 해시</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label className="text-right">활성화</Label>
                        <div className="col-span-3 flex items-center space-x-2">
                          <Switch
                            checked={newGroup.is_active}
                            onCheckedChange={(checked) => setNewGroup({...newGroup, is_active: checked})}
                          />
                          <Label>그룹 활성화</Label>
                        </div>
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsCreateGroupOpen(false)}>
                        취소
                      </Button>
                      <Button onClick={createServerGroup} disabled={loading}>
                        생성
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {serverGroups.map((group) => (
                  <div key={group.group_id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-semibold">{group.name}</h3>
                        <p className="text-sm text-muted-foreground">
                          알고리즘: {getAlgorithmName(group.algorithm)} | 
                          서버: {group.servers.length}개
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        {group.is_active ? (
                          <Badge variant="default">활성</Badge>
                        ) : (
                          <Badge variant="secondary">비활성</Badge>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => deleteServerGroup(group.group_id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    
                    {/* 서버 목록 */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-medium">서버 목록</h4>
                        <Dialog open={isAddServerOpen && selectedGroupId === group.group_id} 
                                onOpenChange={(open) => {
                                  setIsAddServerOpen(open);
                                  if (open) setSelectedGroupId(group.group_id);
                                }}>
                          <DialogTrigger asChild>
                            <Button size="sm" variant="outline">
                              <Plus className="w-4 h-4 mr-1" />
                              서버 추가
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="sm:max-w-[500px]">
                            <DialogHeader>
                              <DialogTitle>서버 추가</DialogTitle>
                              <DialogDescription>
                                {group.name} 그룹에 새 서버를 추가합니다
                              </DialogDescription>
                            </DialogHeader>
                            <div className="grid gap-4 py-4">
                              <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="server-name" className="text-right">서버명</Label>
                                <Input
                                  id="server-name"
                                  value={newServer.name}
                                  onChange={(e) => setNewServer({...newServer, name: e.target.value})}
                                  className="col-span-3"
                                />
                              </div>
                              <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="server-host" className="text-right">호스트</Label>
                                <Input
                                  id="server-host"
                                  value={newServer.host}
                                  onChange={(e) => setNewServer({...newServer, host: e.target.value})}
                                  className="col-span-3"
                                />
                              </div>
                              <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="server-port" className="text-right">포트</Label>
                                <Input
                                  id="server-port"
                                  type="number"
                                  value={newServer.port}
                                  onChange={(e) => setNewServer({...newServer, port: parseInt(e.target.value)})}
                                  className="col-span-3"
                                />
                              </div>
                              <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="server-protocol" className="text-right">프로토콜</Label>
                                <Select value={newServer.protocol} onValueChange={(value) => setNewServer({...newServer, protocol: value})}>
                                  <SelectTrigger className="col-span-3">
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    <SelectItem value="http">HTTP</SelectItem>
                                    <SelectItem value="https">HTTPS</SelectItem>
                                    <SelectItem value="tcp">TCP</SelectItem>
                                  </SelectContent>
                                </Select>
                              </div>
                              <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="server-weight" className="text-right">가중치</Label>
                                <Input
                                  id="server-weight"
                                  type="number"
                                  value={newServer.weight}
                                  onChange={(e) => setNewServer({...newServer, weight: parseInt(e.target.value)})}
                                  className="col-span-3"
                                />
                              </div>
                              <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="health-check-url" className="text-right">헬스 체크 URL</Label>
                                <Input
                                  id="health-check-url"
                                  value={newServer.health_check_url}
                                  onChange={(e) => setNewServer({...newServer, health_check_url: e.target.value})}
                                  className="col-span-3"
                                />
                              </div>
                            </div>
                            <DialogFooter>
                              <Button variant="outline" onClick={() => setIsAddServerOpen(false)}>
                                취소
                              </Button>
                              <Button onClick={addServerToGroup} disabled={loading}>
                                추가
                              </Button>
                            </DialogFooter>
                          </DialogContent>
                        </Dialog>
                      </div>
                      
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>서버명</TableHead>
                            <TableHead>호스트:포트</TableHead>
                            <TableHead>프로토콜</TableHead>
                            <TableHead>가중치</TableHead>
                            <TableHead>상태</TableHead>
                            <TableHead>작업</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {group.servers.map((server) => (
                            <TableRow key={server.server_id}>
                              <TableCell className="font-medium">{server.name}</TableCell>
                              <TableCell className="font-mono text-sm">
                                {server.host}:{server.port}
                              </TableCell>
                              <TableCell>
                                <Badge variant="outline">{server.protocol.toUpperCase()}</Badge>
                              </TableCell>
                              <TableCell>{server.weight}</TableCell>
                              <TableCell>
                                {getStatusBadge(server.status)}
                              </TableCell>
                              <TableCell>
                                <div className="flex space-x-2">
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => performHealthCheck(server.server_id)}
                                  >
                                    <RefreshCw className="h-4 w-4" />
                                  </Button>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => deleteServer(server.server_id)}
                                  >
                                    <Trash2 className="h-4 w-4" />
                                  </Button>
                                </div>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* 설정 탭 */}
        <TabsContent value="settings" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 로드 밸런서 설정 */}
            <Card>
              <CardHeader>
                <CardTitle>로드 밸런서 설정</CardTitle>
                <CardDescription>로드 밸런서 동작 설정을 관리합니다</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {config && (
                  <>
                    <div className="space-y-2">
                      <Label>헬스 체크 간격 (초)</Label>
                      <Input
                        type="number"
                        value={config.health_check_interval}
                        onChange={(e) => updateConfig({health_check_interval: parseInt(e.target.value)})}
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label>헬스 체크 타임아웃 (초)</Label>
                      <Input
                        type="number"
                        value={config.health_check_timeout}
                        onChange={(e) => updateConfig({health_check_timeout: parseInt(e.target.value)})}
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label>최대 실패 횟수</Label>
                      <Input
                        type="number"
                        value={config.max_failures}
                        onChange={(e) => updateConfig({max_failures: parseInt(e.target.value)})}
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label>세션 타임아웃 (초)</Label>
                      <Input
                        type="number"
                        value={config.session_timeout}
                        onChange={(e) => updateConfig({session_timeout: parseInt(e.target.value)})}
                      />
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Switch
                        checked={config.enable_sticky_sessions}
                        onCheckedChange={(checked) => updateConfig({enable_sticky_sessions: checked})}
                      />
                      <Label>세션 고정 활성화</Label>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
            
            {/* 시스템 관리 */}
            <Card>
              <CardHeader>
                <CardTitle>시스템 관리</CardTitle>
                <CardDescription>세션 및 연결 데이터를 관리합니다</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>세션 관리</Label>
                  <Button variant="outline" onClick={clearSessions} disabled={loading}>
                    <Globe className="w-4 h-4 mr-2" />
                    세션 매핑 정리
                  </Button>
                </div>
                
                <div className="space-y-2">
                  <Label>연결 관리</Label>
                  <Button variant="outline" onClick={clearConnections} disabled={loading}>
                    <Users className="w-4 h-4 mr-2" />
                    연결 수 카운터 정리
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