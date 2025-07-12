import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { 
  Package, 
  Settings, 
  Activity, 
  FileText, 
  Download, 
  Upload, 
  Trash2, 
  RefreshCw,
  Play,
  Pause,
  AlertCircle,
  CheckCircle,
  Clock,
  BarChart3,
  History,
  Filter,
  Search,
  Plus,
  Eye,
  Edit,
  MoreHorizontal
} from 'lucide-react';
import { toast } from 'sonner';

interface Plugin {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  category: string;
  enabled: boolean;
  dependencies: string[];
  permissions: string[];
  routes_count: number;
  menus_count: number;
  health_status: {
    status: string;
    message: string;
    initialized: boolean;
  };
  performance_metrics: {
    cpu_usage: number;
    memory_usage: number;
    response_time: number;
    error_rate: number;
    last_updated: string;
  };
  installation_info: {
    installed_at: string;
    last_updated: string;
    update_count: number;
  };
  created_at: string;
  updated_at: string;
}

interface PluginLog {
  timestamp: string;
  action: string;
  message: string;
  level: string;
}

interface PluginMetrics {
  cpu_usage: {
    current: number;
    average: number;
    max: number;
    min: number;
    history: number[];
  };
  memory_usage: {
    current: number;
    average: number;
    max: number;
    min: number;
    history: number[];
  };
  response_time: {
    current: number;
    average: number;
    max: number;
    min: number;
    history: number[];
  };
  error_rate: number;
  last_updated: string;
}

interface InstallationHistory {
  plugin_id: string;
  action: string;
  version: string;
  timestamp: string;
  options?: any;
  metadata?: any;
}

const PluginManagement: React.FC = () => {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPlugin, setSelectedPlugin] = useState<Plugin | null>(null);
  const [pluginLogs, setPluginLogs] = useState<PluginLog[]>([]);
  const [pluginMetrics, setPluginMetrics] = useState<PluginMetrics | null>(null);
  const [installationHistory, setInstallationHistory] = useState<InstallationHistory[]>([]);
  const [filters, setFilters] = useState({
    category: '',
    enabled: '',
    status: '',
    search: ''
  });
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 10,
    total_count: 0,
    total_pages: 0
  });

  // 플러그인 목록 조회
  const fetchPlugins = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        per_page: pagination.per_page.toString(),
        ...filters
      });

      const response = await fetch(`/api/plugins?${params}`);
      const data = await response.json();

      if (data.success) {
        setPlugins(data.plugins);
        setPagination(data.pagination);
      } else {
        toast.error('플러그인 목록 조회 실패');
      }
    } catch (error) {
      console.error('플러그인 목록 조회 오류:', error);
      toast.error('플러그인 목록 조회 중 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  };

  // 플러그인 활성화/비활성화
  const togglePlugin = async (pluginId: string, enabled: boolean) => {
    try {
      const action = enabled ? 'enable' : 'disable';
      const response = await fetch(`/api/plugins/${pluginId}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();

      if (data.success) {
        toast.success(data.message);
        fetchPlugins();
      } else {
        toast.error(data.error);
      }
    } catch (error) {
      console.error('플러그인 상태 변경 오류:', error);
      toast.error('플러그인 상태 변경 중 오류가 발생했습니다');
    }
  };

  // 플러그인 재로드
  const reloadPlugin = async (pluginId: string) => {
    try {
      const response = await fetch(`/api/plugins/${pluginId}/reload`, {
        method: 'POST'
      });
      const data = await response.json();

      if (data.success) {
        toast.success(data.message);
        fetchPlugins();
      } else {
        toast.error(data.error);
      }
    } catch (error) {
      console.error('플러그인 재로드 오류:', error);
      toast.error('플러그인 재로드 중 오류가 발생했습니다');
    }
  };

  // 플러그인 로그 조회
  const fetchPluginLogs = async (pluginId: string) => {
    try {
      const response = await fetch(`/api/plugins/${pluginId}/logs`);
      const data = await response.json();

      if (data.success) {
        setPluginLogs(data.logs);
      } else {
        toast.error('플러그인 로그 조회 실패');
      }
    } catch (error) {
      console.error('플러그인 로그 조회 오류:', error);
      toast.error('플러그인 로그 조회 중 오류가 발생했습니다');
    }
  };

  // 플러그인 메트릭 조회
  const fetchPluginMetrics = async (pluginId: string) => {
    try {
      const response = await fetch(`/api/plugins/${pluginId}/metrics`);
      const data = await response.json();

      if (data.success) {
        setPluginMetrics(data.metrics);
      } else {
        toast.error('플러그인 메트릭 조회 실패');
      }
    } catch (error) {
      console.error('플러그인 메트릭 조회 오류:', error);
      toast.error('플러그인 메트릭 조회 중 오류가 발생했습니다');
    }
  };

  // 설치 이력 조회
  const fetchInstallationHistory = async () => {
    try {
      const response = await fetch('/api/plugins/history');
      const data = await response.json();

      if (data.success) {
        setInstallationHistory(data.history);
      } else {
        toast.error('설치 이력 조회 실패');
      }
    } catch (error) {
      console.error('설치 이력 조회 오류:', error);
      toast.error('설치 이력 조회 중 오류가 발생했습니다');
    }
  };

  // 플러그인 스캔
  const scanPlugins = async () => {
    try {
      const response = await fetch('/api/plugins/scan', {
        method: 'POST'
      });
      const data = await response.json();

      if (data.success) {
        toast.success(data.message);
        fetchPlugins();
      } else {
        toast.error(data.error);
      }
    } catch (error) {
      console.error('플러그인 스캔 오류:', error);
      toast.error('플러그인 스캔 중 오류가 발생했습니다');
    }
  };

  useEffect(() => {
    fetchPlugins();
    fetchInstallationHistory();
  }, [pagination.page, filters]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'warning': return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case 'error': return <AlertCircle className="w-4 h-4 text-red-500" />;
      default: return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">플러그인 관리</h1>
          <p className="text-muted-foreground">
            시스템 플러그인의 설치, 설정, 모니터링을 관리합니다
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={scanPlugins} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            플러그인 스캔
          </Button>
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            새 플러그인 등록
          </Button>
        </div>
      </div>

      {/* 필터 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4 items-center">
            <div className="flex-1">
              <Input
                placeholder="플러그인 검색..."
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                className="max-w-sm"
              />
            </div>
            <Select value={filters.category} onValueChange={(value) => setFilters({ ...filters, category: value })}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="카테고리" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">전체</SelectItem>
                <SelectItem value="management">관리</SelectItem>
                <SelectItem value="analytics">분석</SelectItem>
                <SelectItem value="integration">통합</SelectItem>
                <SelectItem value="security">보안</SelectItem>
              </SelectContent>
            </Select>
            <Select value={filters.enabled} onValueChange={(value) => setFilters({ ...filters, enabled: value })}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="상태" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">전체</SelectItem>
                <SelectItem value="true">활성화</SelectItem>
                <SelectItem value="false">비활성화</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="sm">
              <Filter className="w-4 h-4 mr-2" />
              필터 적용
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 플러그인 목록 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="w-5 h-5" />
            플러그인 목록
            <Badge variant="secondary">{pagination.total_count}개</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>플러그인</TableHead>
                  <TableHead>카테고리</TableHead>
                  <TableHead>상태</TableHead>
                  <TableHead>성능</TableHead>
                  <TableHead>업데이트</TableHead>
                  <TableHead>작업</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {plugins.map((plugin) => (
                  <TableRow key={plugin.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{plugin.name}</div>
                        <div className="text-sm text-muted-foreground">
                          v{plugin.version} • {plugin.author}
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {plugin.description}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{plugin.category}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(plugin.health_status.status)}
                        <Badge 
                          variant={plugin.enabled ? "default" : "secondary"}
                          className={getStatusColor(plugin.health_status.status)}
                        >
                          {plugin.enabled ? '활성화' : '비활성화'}
                        </Badge>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 text-xs">
                          <BarChart3 className="w-3 h-3" />
                          CPU: {plugin.performance_metrics.cpu_usage.toFixed(1)}%
                        </div>
                        <div className="flex items-center gap-2 text-xs">
                          <Activity className="w-3 h-3" />
                          메모리: {plugin.performance_metrics.memory_usage.toFixed(1)}MB
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-xs text-muted-foreground">
                        {new Date(plugin.installation_info.last_updated).toLocaleDateString()}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setSelectedPlugin(plugin);
                            fetchPluginLogs(plugin.id);
                            fetchPluginMetrics(plugin.id);
                          }}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => togglePlugin(plugin.id, !plugin.enabled)}
                        >
                          {plugin.enabled ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => reloadPlugin(plugin.id)}
                        >
                          <RefreshCw className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* 플러그인 상세 정보 */}
      {selectedPlugin && (
        <Dialog open={!!selectedPlugin} onOpenChange={() => setSelectedPlugin(null)}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Package className="w-5 h-5" />
                {selectedPlugin.name} 상세 정보
              </DialogTitle>
            </DialogHeader>
            
            <Tabs defaultValue="overview" className="w-full">
              <TabsList>
                <TabsTrigger value="overview">개요</TabsTrigger>
                <TabsTrigger value="logs">로그</TabsTrigger>
                <TabsTrigger value="metrics">성능</TabsTrigger>
                <TabsTrigger value="settings">설정</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">기본 정보</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <div><strong>ID:</strong> {selectedPlugin.id}</div>
                      <div><strong>버전:</strong> {selectedPlugin.version}</div>
                      <div><strong>작성자:</strong> {selectedPlugin.author}</div>
                      <div><strong>카테고리:</strong> {selectedPlugin.category}</div>
                      <div><strong>설명:</strong> {selectedPlugin.description}</div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">상태 정보</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <div><strong>상태:</strong> {selectedPlugin.health_status.status}</div>
                      <div><strong>초기화:</strong> {selectedPlugin.health_status.initialized ? '완료' : '실패'}</div>
                      <div><strong>라우트 수:</strong> {selectedPlugin.routes_count}</div>
                      <div><strong>메뉴 수:</strong> {selectedPlugin.menus_count}</div>
                      <div><strong>의존성:</strong> {selectedPlugin.dependencies.length}개</div>
                    </CardContent>
                  </Card>
                </div>

                {selectedPlugin.dependencies.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">의존성</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex gap-2">
                        {selectedPlugin.dependencies.map((dep) => (
                          <Badge key={dep} variant="outline">{dep}</Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="logs" className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold">플러그인 로그</h3>
                  <Button size="sm" onClick={() => fetchPluginLogs(selectedPlugin.id)}>
                    <RefreshCw className="w-4 h-4 mr-2" />
                    새로고침
                  </Button>
                </div>
                
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {pluginLogs.map((log, index) => (
                    <div key={index} className="p-3 border rounded-lg">
                      <div className="flex justify-between items-start">
                        <div className="flex items-center gap-2">
                          <Badge variant={log.level === 'error' ? 'destructive' : 'secondary'}>
                            {log.level}
                          </Badge>
                          <span className="font-medium">{log.action}</span>
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {new Date(log.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm mt-1">{log.message}</p>
                    </div>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="metrics" className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold">성능 메트릭</h3>
                  <Button size="sm" onClick={() => fetchPluginMetrics(selectedPlugin.id)}>
                    <RefreshCw className="w-4 h-4 mr-2" />
                    새로고침
                  </Button>
                </div>

                {pluginMetrics && (
                  <div className="grid grid-cols-3 gap-4">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-sm">CPU 사용률</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{pluginMetrics.cpu_usage.current.toFixed(1)}%</div>
                        <Progress value={pluginMetrics.cpu_usage.current} className="mt-2" />
                        <div className="text-xs text-muted-foreground mt-1">
                          평균: {pluginMetrics.cpu_usage.average.toFixed(1)}%
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-sm">메모리 사용률</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{pluginMetrics.memory_usage.current.toFixed(1)}MB</div>
                        <Progress value={(pluginMetrics.memory_usage.current / 512) * 100} className="mt-2" />
                        <div className="text-xs text-muted-foreground mt-1">
                          평균: {pluginMetrics.memory_usage.average.toFixed(1)}MB
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-sm">응답 시간</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{pluginMetrics.response_time.current.toFixed(0)}ms</div>
                        <Progress value={(pluginMetrics.response_time.current / 1000) * 100} className="mt-2" />
                        <div className="text-xs text-muted-foreground mt-1">
                          평균: {pluginMetrics.response_time.average.toFixed(0)}ms
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="settings" className="space-y-4">
                <h3 className="text-lg font-semibold">플러그인 설정</h3>
                <Alert>
                  <Settings className="h-4 w-4" />
                  <AlertDescription>
                    플러그인 설정은 별도의 설정 페이지에서 관리할 수 있습니다.
                  </AlertDescription>
                </Alert>
              </TabsContent>
            </Tabs>
          </DialogContent>
        </Dialog>
      )}

      {/* 설치 이력 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="w-5 h-5" />
            설치 이력
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>플러그인</TableHead>
                <TableHead>작업</TableHead>
                <TableHead>버전</TableHead>
                <TableHead>시간</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {installationHistory.map((history, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{history.plugin_id}</TableCell>
                  <TableCell>
                    <Badge variant={
                      history.action === 'install' ? 'default' : 
                      history.action === 'uninstall' ? 'destructive' : 'secondary'
                    }>
                      {history.action}
                    </Badge>
                  </TableCell>
                  <TableCell>{history.version}</TableCell>
                  <TableCell>
                    {new Date(history.timestamp).toLocaleString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default PluginManagement; 