'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
// @ts-expect-error: 모듈이 없다는 lint 경고 무시  # pyright: ignore
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Play, 
  Square, 
  RefreshCw, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Settings,
  History,
  BarChart3,
  Zap,
  Eye,
  Trash2,
  Plus,
  Edit,
  Copy,
  Download,
  Upload,
  Server,
  Network,
  Cpu,
  Activity,
  Globe,
  Shield,
  Clock
} from 'lucide-react';
import { toast } from 'sonner';

interface ServiceInstance {
  id: string;
  name: string;
  plugin_id: string;
  service_type: string;
  status: string;
  health_status: string;
  port: number;
  host_port: number;
  start_time: string | null;
  last_health_check: string | null;
  resource_usage: Record<string, any>;
  error_message: string | null;
}

interface ServiceTemplate {
  id: string;
  name: string;
  description: string;
  service_type: string;
  port: number;
  template: Record<string, any>;
}

interface ServiceDiscovery {
  services: ServiceInstance[];
  networks: Array<{
    name: string;
    id: string;
    driver: string;
    scope: string;
  }>;
  total_services: number;
  healthy_services: number;
  unhealthy_services: number;
}

const PluginMicroserviceDashboard: React.FC = () => {
  const [services, setServices] = useState<ServiceInstance[]>([]);
  const [templates, setTemplates] = useState<ServiceTemplate[]>([]);
  const [discovery, setDiscovery] = useState<ServiceDiscovery | null>(null);
  const [selectedService, setSelectedService] = useState<ServiceInstance | null>(null);
  const [serviceLogs, setServiceLogs] = useState<string[]>([]);
  const [serviceMetrics, setServiceMetrics] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  
  // 새 서비스 생성 상태
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showTemplateForm, setShowTemplateForm] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [newService, setNewService] = useState({
    plugin_id: '',
    name: '',
    service_type: 'rest_api',
    port: 8080,
    host: '0.0.0.0',
    environment: {},
    volumes: [],
    networks: ['plugin_network'],
    depends_on: [],
    restart_policy: 'unless-stopped',
    version: 'latest'
  });

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

  // 데이터 로드 함수들
  const loadServices = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/plugin-microservice/services`);
      const data = await response.json();
      if (data.success) {
        setServices(data.data);
      }
    } catch (error) {
      console.error('서비스 로드 실패:', error);
      toast.error('서비스 목록을 불러오는데 실패했습니다.');
    }
  }, [API_BASE]);

  const loadTemplates = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/plugin-microservice/templates`);
      const data = await response.json();
      if (data.success) {
        setTemplates(data.data);
      }
    } catch (error) {
      console.error('템플릿 로드 실패:', error);
      toast.error('서비스 템플릿을 불러오는데 실패했습니다.');
    }
  }, [API_BASE]);

  const loadDiscovery = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/plugin-microservice/discovery`);
      const data = await response.json();
      if (data.success) {
        setDiscovery(data.data);
      }
    } catch (error) {
      console.error('디스커버리 로드 실패:', error);
      toast.error('서비스 디스커버리 정보를 불러오는데 실패했습니다.');
    }
  }, [API_BASE]);

  const loadServiceLogs = useCallback(async (serviceId: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/plugin-microservice/services/${serviceId}/logs?lines=100`);
      const data = await response.json();
      if (data.success) {
        setServiceLogs(data.data);
      }
    } catch (error) {
      console.error('서비스 로그 로드 실패:', error);
      toast.error('서비스 로그를 불러오는데 실패했습니다.');
    }
  }, [API_BASE]);

  const loadServiceMetrics = useCallback(async (serviceId: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/plugin-microservice/services/${serviceId}/metrics`);
      const data = await response.json();
      if (data.success) {
        setServiceMetrics(data.data);
      }
    } catch (error) {
      console.error('서비스 메트릭 로드 실패:', error);
      toast.error('서비스 메트릭을 불러오는데 실패했습니다.');
    }
  }, [API_BASE]);

  // 초기 데이터 로드
  useEffect(() => {
    loadServices();
    loadTemplates();
    loadDiscovery();
  }, [loadServices, loadTemplates, loadDiscovery]);

  // 서비스 생성
  const createService = async () => {
    if (!newService.plugin_id || !newService.name) {
      toast.error('필수 필드를 모두 입력해주세요.');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/plugin-microservice/services`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newService),
      });

      const data = await response.json();
      if (data.success) {
        toast.success('서비스가 성공적으로 생성되었습니다.');
        setShowCreateForm(false);
        setNewService({
          plugin_id: '',
          name: '',
          service_type: 'rest_api',
          port: 8080,
          host: '0.0.0.0',
          environment: {},
          volumes: [],
          networks: ['plugin_network'],
          depends_on: [],
          restart_policy: 'unless-stopped',
          version: 'latest'
        });
        loadServices();
        loadDiscovery();
      } else {
        toast.error(data.message || '서비스 생성에 실패했습니다.');
      }
    } catch (error) {
      console.error('서비스 생성 실패:', error);
      toast.error('서비스 생성 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 템플릿으로 서비스 생성
  const createServiceFromTemplate = async () => {
    if (!selectedTemplate || !newService.plugin_id) {
      toast.error('템플릿과 플러그인 ID를 선택해주세요.');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/plugin-microservice/templates/${selectedTemplate}/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plugin_id: newService.plugin_id,
          name: newService.name || undefined
        }),
      });

      const data = await response.json();
      if (data.success) {
        toast.success('템플릿을 사용하여 서비스가 성공적으로 생성되었습니다.');
        setShowTemplateForm(false);
        setSelectedTemplate('');
        setNewService({
          plugin_id: '',
          name: '',
          service_type: 'rest_api',
          port: 8080,
          host: '0.0.0.0',
          environment: {},
          volumes: [],
          networks: ['plugin_network'],
          depends_on: [],
          restart_policy: 'unless-stopped',
          version: 'latest'
        });
        loadServices();
        loadDiscovery();
      } else {
        toast.error(data.message || '템플릿 서비스 생성에 실패했습니다.');
      }
    } catch (error) {
      console.error('템플릿 서비스 생성 실패:', error);
      toast.error('템플릿 서비스 생성 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 서비스 제어
  const controlService = async (serviceId: string, action: 'start' | 'stop' | 'restart' | 'delete') => {
    setLoading(true);
    try {
      let url = '';
      let method = 'POST';
      
      switch (action) {
        case 'start':
          url = `${API_BASE}/api/plugin-microservice/services/${serviceId}/start`;
          break;
        case 'stop':
          url = `${API_BASE}/api/plugin-microservice/services/${serviceId}/stop`;
          break;
        case 'restart':
          url = `${API_BASE}/api/plugin-microservice/services/${serviceId}/restart`;
          break;
        case 'delete':
          url = `${API_BASE}/api/plugin-microservice/services/${serviceId}`;
          method = 'DELETE';
          break;
      }

      const response = await fetch(url, { method });
      const data = await response.json();
      
      if (data.success) {
        toast.success(`서비스 ${action} 완료`);
        loadServices();
        loadDiscovery();
      } else {
        toast.error(data.message || `서비스 ${action} 실패`);
      }
    } catch (error) {
      console.error(`서비스 ${action} 실패:`, error);
      toast.error(`서비스 ${action} 중 오류가 발생했습니다.`);
    } finally {
      setLoading(false);
    }
  };

  // 서비스 상세 정보 조회
  const viewServiceDetails = async (service: ServiceInstance) => {
    setSelectedService(service);
    await loadServiceLogs(service.id);
    await loadServiceMetrics(service.id);
    setActiveTab('details');
  };

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-green-100 text-green-800';
      case 'stopped': return 'bg-gray-100 text-gray-800';
      case 'starting': return 'bg-blue-100 text-blue-800';
      case 'stopping': return 'bg-yellow-100 text-yellow-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return 'bg-green-100 text-green-800';
      case 'unhealthy': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // 상태별 아이콘
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <CheckCircle className="w-4 h-4" />;
      case 'stopped': return <Square className="w-4 h-4" />;
      case 'starting': return <RefreshCw className="w-4 h-4 animate-spin" />;
      case 'stopping': return <Clock className="w-4 h-4" />;
      case 'error': return <XCircle className="w-4 h-4" />;
      default: return <AlertTriangle className="w-4 h-4" />;
    }
  };

  // 시간 포맷팅
  const formatTime = (timeString: string | null) => {
    if (!timeString) return 'N/A';
    return new Date(timeString).toLocaleString('ko-KR');
  };

  // 서비스 타입별 아이콘
  const getServiceTypeIcon = (type: string) => {
    switch (type) {
      case 'rest_api': return <Globe className="w-4 h-4" />;
      case 'websocket': return <Network className="w-4 h-4" />;
      case 'background': return <Server className="w-4 h-4" />;
      case 'scheduler': return <Clock className="w-4 h-4" />;
      case 'worker': return <Activity className="w-4 h-4" />;
      default: return <Server className="w-4 h-4" />;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">플러그인 마이크로서비스 대시보드</h1>
          <p className="text-gray-600 mt-2">
            플러그인을 독립적인 마이크로서비스로 관리하고 모니터링
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setShowTemplateForm(true)}>
            <Plus className="w-4 h-4 mr-2" />
            템플릿으로 생성
          </Button>
          <Button onClick={() => setShowCreateForm(true)}>
            <Plus className="w-4 h-4 mr-2" />
            새 서비스
          </Button>
          <Button variant="outline" onClick={() => {
            loadServices();
            loadTemplates();
            loadDiscovery();
          }}>
            <RefreshCw className="w-4 h-4 mr-2" />
            새로고침
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="services">서비스</TabsTrigger>
          <TabsTrigger value="templates">템플릿</TabsTrigger>
          <TabsTrigger value="details">상세 정보</TabsTrigger>
          <TabsTrigger value="discovery">디스커버리</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* 통계 카드 */}
          {discovery && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">총 서비스</CardTitle>
                  <Server className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{discovery.total_services}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">정상 서비스</CardTitle>
                  <CheckCircle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">{discovery.healthy_services}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">비정상 서비스</CardTitle>
                  <XCircle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-red-600">{discovery.unhealthy_services}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">네트워크</CardTitle>
                  <Network className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{discovery.networks.length}</div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* 최근 서비스 */}
          <Card>
            <CardHeader>
              <CardTitle>최근 서비스</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {services.slice(0, 5).map((service) => (
                  <div key={service.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      {getServiceTypeIcon(service.service_type)}
                      <div>
                        <div className="font-medium">{service.name}</div>
                        <div className="text-sm text-gray-500">
                          {service.plugin_id} • 포트: {service.host_port}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getStatusColor(service.status)}>
                        {service.status}
                      </Badge>
                      <Badge className={getHealthColor(service.health_status)}>
                        {service.health_status}
                      </Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => viewServiceDetails(service)}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="services" className="space-y-6">
          {/* 서비스 목록 */}
          <Card>
            <CardHeader>
              <CardTitle>서비스 목록</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {services.map((service) => (
                  <div key={service.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getServiceTypeIcon(service.service_type)}
                        <div>
                          <div className="font-medium">{service.name}</div>
                          <div className="text-sm text-gray-500">ID: {service.id}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(service.status)}>
                          {service.status}
                        </Badge>
                        <Badge className={getHealthColor(service.health_status)}>
                          {service.health_status}
                        </Badge>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">플러그인:</span>
                        <span className="ml-1 font-medium">{service.plugin_id}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">포트:</span>
                        <span className="ml-1">{service.host_port}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">시작 시간:</span>
                        <span className="ml-1">{formatTime(service.start_time)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">타입:</span>
                        <span className="ml-1 capitalize">{service.service_type}</span>
                      </div>
                    </div>

                    {service.error_message && (
                      <Alert className="mt-3">
                        <AlertTriangle className="h-4 w-4" />
                        <AlertDescription>{service.error_message}</AlertDescription>
                      </Alert>
                    )}

                    <div className="flex gap-2 mt-3">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => viewServiceDetails(service)}
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        상세 정보
                      </Button>
                      {service.status === 'stopped' && (
                        <Button
                          size="sm"
                          onClick={() => controlService(service.id, 'start')}
                        >
                          <Play className="w-4 h-4 mr-1" />
                          시작
                        </Button>
                      )}
                      {service.status === 'running' && (
                        <>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => controlService(service.id, 'restart')}
                          >
                            <RefreshCw className="w-4 h-4 mr-1" />
                            재시작
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => controlService(service.id, 'stop')}
                          >
                            <Square className="w-4 h-4 mr-1" />
                            중지
                          </Button>
                        </>
                      )}
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => controlService(service.id, 'delete')}
                      >
                        <Trash2 className="w-4 h-4 mr-1" />
                        삭제
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="templates" className="space-y-6">
          {/* 서비스 템플릿 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map((template) => (
              <Card key={template.id}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    {template.name}
                    <Badge variant="outline">{template.service_type}</Badge>
                  </CardTitle>
                  <CardDescription>{template.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <Label className="text-sm font-medium">포트</Label>
                      <div className="text-sm text-gray-600">{template.port}</div>
                    </div>

                    <div>
                      <Label className="text-sm font-medium">설정</Label>
                      <div className="text-xs text-gray-500 mt-1">
                        <div>환경 변수: {Object.keys(template.template.environment || {}).length}개</div>
                        <div>리소스 제한: {template.template.resource_limits ? '설정됨' : '기본값'}</div>
                        <div>헬스 체크: {template.template.health_check ? '활성화' : '비활성화'}</div>
                      </div>
                    </div>

                    <Button 
                      size="sm" 
                      className="w-full"
                      onClick={() => {
                        setSelectedTemplate(template.id);
                        setShowTemplateForm(true);
                      }}
                    >
                      <Plus className="w-4 h-4 mr-1" />
                      이 템플릿 사용
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="details" className="space-y-6">
          {/* 서비스 상세 정보 */}
          {selectedService ? (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>서비스 상세 정보 - {selectedService.name}</CardTitle>
                  <CardDescription>
                    {selectedService.plugin_id} • 포트: {selectedService.host_port}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="font-medium mb-3">기본 정보</h3>
                      <div className="space-y-2 text-sm">
                        <div><span className="text-gray-500">서비스 ID:</span> {selectedService.id}</div>
                        <div><span className="text-gray-500">플러그인 ID:</span> {selectedService.plugin_id}</div>
                        <div><span className="text-gray-500">서비스 타입:</span> {selectedService.service_type}</div>
                        <div><span className="text-gray-500">상태:</span> 
                          <Badge className={`ml-2 ${getStatusColor(selectedService.status)}`}>
                            {selectedService.status}
                          </Badge>
                        </div>
                        <div><span className="text-gray-500">헬스 상태:</span>
                          <Badge className={`ml-2 ${getHealthColor(selectedService.health_status)}`}>
                            {selectedService.health_status}
                          </Badge>
                        </div>
                        <div><span className="text-gray-500">포트:</span> {selectedService.host_port}</div>
                        <div><span className="text-gray-500">시작 시간:</span> {formatTime(selectedService.start_time)}</div>
                        <div><span className="text-gray-500">마지막 헬스 체크:</span> {formatTime(selectedService.last_health_check)}</div>
                      </div>
                    </div>

                    <div>
                      <h3 className="font-medium mb-3">리소스 사용량</h3>
                      {serviceMetrics ? (
                        <div className="space-y-3">
                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span>CPU 사용률</span>
                              <span>{serviceMetrics.cpu_percent}%</span>
                            </div>
                            <Progress value={serviceMetrics.cpu_percent} />
                          </div>
                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span>메모리 사용률</span>
                              <span>{serviceMetrics.memory_percent}%</span>
                            </div>
                            <Progress value={serviceMetrics.memory_percent} />
                          </div>
                          <div className="text-sm">
                            <div>메모리 사용량: {serviceMetrics.memory_usage_mb}MB / {serviceMetrics.memory_limit_mb}MB</div>
                            <div>네트워크 수신: {serviceMetrics.network_rx_mb}MB</div>
                            <div>네트워크 송신: {serviceMetrics.network_tx_mb}MB</div>
                          </div>
                        </div>
                      ) : (
                        <div className="text-sm text-gray-500">메트릭 정보를 불러올 수 없습니다.</div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>서비스 로그</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-64">
                    <div className="space-y-1">
                      {serviceLogs.map((log, index) => (
                        <div key={index} className="text-sm font-mono bg-gray-50 p-2 rounded">
                          {log}
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="flex items-center justify-center h-32">
                <p className="text-gray-500">서비스를 선택하여 상세 정보를 확인하세요.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="discovery" className="space-y-6">
          {/* 서비스 디스커버리 */}
          {discovery && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>서비스 디스커버리</CardTitle>
                  <CardDescription>
                    모든 마이크로서비스의 상태 및 네트워크 정보
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="font-medium mb-3">서비스 상태</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>총 서비스:</span>
                          <span className="font-medium">{discovery.total_services}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>정상 서비스:</span>
                          <span className="font-medium text-green-600">{discovery.healthy_services}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>비정상 서비스:</span>
                          <span className="font-medium text-red-600">{discovery.unhealthy_services}</span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="font-medium mb-3">네트워크 정보</h3>
                      <div className="space-y-2">
                        {discovery.networks.map((network) => (
                          <div key={network.id} className="border rounded p-2">
                            <div className="font-medium">{network.name}</div>
                            <div className="text-sm text-gray-500">
                              드라이버: {network.driver} • 범위: {network.scope}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>서비스 엔드포인트</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {discovery.services.map((service) => (
                      <div key={service.id} className="flex items-center justify-between p-3 border rounded">
                        <div>
                          <div className="font-medium">{service.name}</div>
                          {/* 'endpoint' 속성이 ServiceInstance 타입에 없으므로, 만약 endpoint가 실제로 존재하지 않는다면 아래와 같이 대체하거나, 백엔드에서 해당 필드를 추가해야 합니다. 
                              여기서는 endpoint 대신 service.address 또는 service.url 등 실제 존재하는 필드를 사용하거나, 임시로 표시하지 않도록 처리합니다. */}
                          <div className="text-sm text-gray-500">
                            {/* @ts-expect-error: endpoint 속성이 타입에 없으나, 백엔드에서 제공된다면 무시합니다. */}
                            {service.endpoint ?? '엔드포인트 정보 없음'} {/* lint 경고 무시용 주석 추가 # pyright: ignore */}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getStatusColor(service.status)}>
                            {service.status}
                          </Badge>
                          {/* 
                            'health' 속성이 ServiceInstance 타입에 없어서 타입 에러가 발생합니다.
                            만약 백엔드에서 실제로 health 값을 내려주고 있다면, 타입 정의를 수정해야 합니다.
                            그렇지 않으면 아래와 같이 타입 무시 주석을 추가해 임시로 에러를 무시할 수 있습니다.
                          */}
                          <Badge className={getHealthColor(
                            // @ts-expect-error: health 속성이 타입에 없지만 백엔드에서 제공된다면 무시합니다. # pyright: ignore
                            service.health
                          )}>
                            {/* @ts-expect-error: health 속성이 타입에 없지만 백엔드에서 제공된다면 무시합니다. # pyright: ignore */}
                            {service.health}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>
      </Tabs>

      {/* 새 서비스 생성 모달 */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle>새 서비스 생성</CardTitle>
              <CardDescription>
                새로운 마이크로서비스를 생성합니다.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="plugin-id">플러그인 ID</Label>
                  <Input
                    id="plugin-id"
                    placeholder="plugin_id"
                    value={newService.plugin_id}
                    onChange={(e) => setNewService(prev => ({ ...prev, plugin_id: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="service-name">서비스 이름</Label>
                  <Input
                    id="service-name"
                    placeholder="service_name"
                    value={newService.name}
                    onChange={(e) => setNewService(prev => ({ ...prev, name: e.target.value }))}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="service-type">서비스 타입</Label>
                  <Select value={newService.service_type} onValueChange={(value) => 
                    setNewService(prev => ({ ...prev, service_type: value }))
                  }>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="rest_api">REST API</SelectItem>
                      <SelectItem value="websocket">WebSocket</SelectItem>
                      <SelectItem value="background">Background Worker</SelectItem>
                      <SelectItem value="scheduler">Scheduler</SelectItem>
                      <SelectItem value="worker">Worker</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="port">포트</Label>
                  <Input
                    id="port"
                    type="number"
                    placeholder="8080"
                    value={newService.port}
                    onChange={(e) => setNewService(prev => ({ ...prev, port: parseInt(e.target.value) }))}
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setShowCreateForm(false)}>
                  취소
                </Button>
                <Button onClick={createService} disabled={loading}>
                  {loading ? '생성 중...' : '생성'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 템플릿 서비스 생성 모달 */}
      {showTemplateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle>템플릿으로 서비스 생성</CardTitle>
              <CardDescription>
                미리 정의된 템플릿을 사용하여 서비스를 생성합니다.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="template-select">템플릿 선택</Label>
                <Select value={selectedTemplate} onValueChange={setSelectedTemplate}>
                  <SelectTrigger>
                    <SelectValue placeholder="템플릿을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    {templates.map((template) => (
                      <SelectItem key={template.id} value={template.id}>
                        {template.name} - {template.description}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="template-plugin-id">플러그인 ID</Label>
                  <Input
                    id="template-plugin-id"
                    placeholder="plugin_id"
                    value={newService.plugin_id}
                    onChange={(e) => setNewService(prev => ({ ...prev, plugin_id: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="template-service-name">서비스 이름 (선택사항)</Label>
                  <Input
                    id="template-service-name"
                    placeholder="기본 이름 사용"
                    value={newService.name}
                    onChange={(e) => setNewService(prev => ({ ...prev, name: e.target.value }))}
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setShowTemplateForm(false)}>
                  취소
                </Button>
                <Button onClick={createServiceFromTemplate} disabled={loading || !selectedTemplate}>
                  {loading ? '생성 중...' : '생성'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default PluginMicroserviceDashboard; 