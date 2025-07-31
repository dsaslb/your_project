'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Building2, 
  Store, 
  Users, 
  User, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  RefreshCw,
  Database,
  Activity,
  BarChart3,
  Settings,
  Eye,
  Plus,
  Search
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api-client';
import { useLoadingState } from '@/hooks/useLoadingState';
import { useErrorHandler } from '@/hooks/useErrorHandler';

interface DashboardStats {
  industries: {
    total: number;
    active: number;
  };
  brands: {
    total: number;
    active: number;
  };
  stores: {
    total: number;
    active: number;
  };
  employees: {
    total: number;
    active: number;
  };
}

interface SystemStatus {
  backend: 'online' | 'offline' | 'error';
  database: 'online' | 'offline' | 'error';
  lastSync: string;
  errors: {
    count: number;
    recent: Array<{
      id: string;
      type: string;
      message: string;
      timestamp: string;
    }>;
  };
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    industries: { total: 0, active: 0 },
    brands: { total: 0, active: 0 },
    stores: { total: 0, active: 0 },
    employees: { total: 0, active: 0 }
  });
  
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    backend: 'offline',
    database: 'offline',
    lastSync: '',
    errors: { count: 0, recent: [] }
  });

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedView, setSelectedView] = useState<'overview' | 'errors' | 'analytics'>('overview');

  const { isLoading, error, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 대시보드 데이터 로드
  const loadDashboardData = async () => {
    try {
      // 업종 통계
      const industriesResponse = await (apiClient as any).getIndustries();
      const industries = industriesResponse.data || [];
      const activeIndustries = industries.filter((ind: any) => ind.status === 'active');

      // 브랜드 통계
      const brandsResponse = await (apiClient as any).getBrands();
      const brands = brandsResponse.data || [];
      const activeBrands = brands.filter((brand: any) => brand.status === 'active');

      // 매장 통계
      const storesResponse = await (apiClient as any).getStores();
      const stores = storesResponse.data || [];
      const activeStores = stores.filter((store: any) => store.status === 'active');

      // 직원 통계
      const employeesResponse = await (apiClient as any).getEmployees();
      const employees = employeesResponse.data || [];
      const activeEmployees = employees.filter((emp: any) => emp.status === 'active');

      setStats({
        industries: { total: industries.length, active: activeIndustries.length },
        brands: { total: brands.length, active: activeBrands.length },
        stores: { total: stores.length, active: activeStores.length },
        employees: { total: employees.length, active: activeEmployees.length }
      });

      // 시스템 상태 업데이트
      setSystemStatus(prev => ({
        ...prev,
        backend: 'online',
        database: 'online',
        lastSync: new Date().toLocaleString('ko-KR')
      }));

    } catch (error) {
      handleError(error as Error);
      setSystemStatus(prev => ({
        ...prev,
        backend: 'error',
        database: 'error'
      }));
    }
  };

  // 시스템 상태 체크
  const checkSystemStatus = async () => {
    try {
      await (apiClient as any).getIndustries(); // 간단한 API 호출로 상태 체크
      setSystemStatus(prev => ({
        ...prev,
        backend: 'online',
        database: 'online',
        lastSync: new Date().toLocaleString('ko-KR')
      }));
    } catch (error) {
      setSystemStatus(prev => ({
        ...prev,
        backend: 'offline',
        database: 'offline'
      }));
    }
  };

  useEffect(() => {
    loadDashboardData();
    checkSystemStatus();
    
    // 30초마다 상태 체크
    const interval = setInterval(checkSystemStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    withLoading(loadDashboardData);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-400';
      case 'offline': return 'text-red-400';
      case 'error': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return <CheckCircle className="w-4 h-4" />;
      case 'offline': return <XCircle className="w-4 h-4" />;
      case 'error': return <AlertTriangle className="w-4 h-4" />;
      default: return <XCircle className="w-4 h-4" />;
    }
  };

  const quickActions = [
    {
      title: '업종 관리',
      description: '업종별 관리 페이지로 이동',
      icon: <Building2 className="w-6 h-6" />,
      href: '/industry-management',
      color: 'from-blue-500/20 to-cyan-500/20'
    },
    {
      title: '브랜드 관리',
      description: '브랜드별 관리 페이지로 이동',
      icon: <Store className="w-6 h-6" />,
      href: '/brand-management',
      color: 'from-purple-500/20 to-pink-500/20'
    },
    {
      title: '매장 관리',
      description: '매장별 관리 페이지로 이동',
      icon: <Store className="w-6 h-6" />,
      href: '/store-management',
      color: 'from-green-500/20 to-emerald-500/20'
    },
    {
      title: '직원 관리',
      description: '직원별 관리 페이지로 이동',
      icon: <Users className="w-6 h-6" />,
      href: '/employee-management',
      color: 'from-orange-500/20 to-red-500/20'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* 헤더 */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">멀티테넌시 관리 시스템</h1>
            <p className="text-slate-300">계층별 현황 및 시스템 상태 모니터링</p>
          </div>
          <div className="flex items-center gap-4">
            <Button
              onClick={handleRefresh}
              disabled={isLoading}
              className="bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-400 border-cyan-500/30 hover:from-cyan-500/30 hover:to-purple-500/30"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              새로고침
            </Button>
          </div>
        </div>

        {/* 시스템 상태 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-slate-800/50 border-slate-600/30 backdrop-blur-xl">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Database className="w-5 h-5 text-blue-400" />
                  <span className="text-sm text-slate-300">백엔드</span>
                </div>
                <div className={`flex items-center gap-1 ${getStatusColor(systemStatus.backend)}`}>
                  {getStatusIcon(systemStatus.backend)}
                  <span className="text-xs font-medium">{systemStatus.backend}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-600/30 backdrop-blur-xl">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Activity className="w-5 h-5 text-green-400" />
                  <span className="text-sm text-slate-300">데이터베이스</span>
                </div>
                <div className={`flex items-center gap-1 ${getStatusColor(systemStatus.database)}`}>
                  {getStatusIcon(systemStatus.database)}
                  <span className="text-xs font-medium">{systemStatus.database}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-600/30 backdrop-blur-xl">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <BarChart3 className="w-5 h-5 text-purple-400" />
                  <span className="text-sm text-slate-300">오류 수</span>
                </div>
                <Badge variant="destructive" className="text-xs">
                  {systemStatus.errors.count}
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-600/30 backdrop-blur-xl">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Settings className="w-5 h-5 text-orange-400" />
                  <span className="text-sm text-slate-300">마지막 동기화</span>
                </div>
                <span className="text-xs text-slate-400">
                  {systemStatus.lastSync || '없음'}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border-blue-500/30 backdrop-blur-xl">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-300 mb-1">총 업종</p>
                  <p className="text-2xl font-bold text-white">{stats.industries.total}</p>
                  <p className="text-xs text-blue-200 mt-1">
                    활성: {stats.industries.active}
                  </p>
                </div>
                <Building2 className="w-8 h-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-500/30 backdrop-blur-xl">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-purple-300 mb-1">총 브랜드</p>
                  <p className="text-2xl font-bold text-white">{stats.brands.total}</p>
                  <p className="text-xs text-purple-200 mt-1">
                    활성: {stats.brands.active}
                  </p>
                </div>
                <Store className="w-8 h-8 text-purple-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/30 backdrop-blur-xl">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-300 mb-1">총 매장</p>
                  <p className="text-2xl font-bold text-white">{stats.stores.total}</p>
                  <p className="text-xs text-green-200 mt-1">
                    활성: {stats.stores.active}
                  </p>
                </div>
                <Store className="w-8 h-8 text-green-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-500/10 to-red-500/10 border-orange-500/30 backdrop-blur-xl">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-orange-300 mb-1">총 직원</p>
                  <p className="text-2xl font-bold text-white">{stats.employees.total}</p>
                  <p className="text-xs text-orange-200 mt-1">
                    활성: {stats.employees.active}
                  </p>
                </div>
                <Users className="w-8 h-8 text-orange-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 뷰 선택 */}
        <div className="flex items-center gap-4">
          <Button
            variant={selectedView === 'overview' ? 'default' : 'outline'}
            onClick={() => setSelectedView('overview')}
            className="bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-400 border-cyan-500/30 hover:from-cyan-500/30 hover:to-purple-500/30"
          >
            <Eye className="w-4 h-4 mr-2" />
            개요
          </Button>
          <Button
            variant={selectedView === 'errors' ? 'default' : 'outline'}
            onClick={() => setSelectedView('errors')}
            className="border-slate-600 text-slate-300 hover:bg-slate-700"
          >
            <AlertTriangle className="w-4 h-4 mr-2" />
            오류 현황
          </Button>
          <Button
            variant={selectedView === 'analytics' ? 'default' : 'outline'}
            onClick={() => setSelectedView('analytics')}
            className="border-slate-600 text-slate-300 hover:bg-slate-700"
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            분석
          </Button>
        </div>

        {/* 선택된 뷰에 따른 콘텐츠 */}
        {selectedView === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 빠른 액션 */}
            <Card className="bg-slate-800/50 border-slate-600/30 backdrop-blur-xl">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Plus className="w-5 h-5" />
                  빠른 액션
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  {quickActions.map((action, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      className={`h-auto p-4 flex flex-col items-center gap-2 bg-gradient-to-r ${action.color} border-slate-600/30 text-white hover:bg-slate-700/50`}
                      onClick={() => window.location.href = action.href}
                    >
                      {action.icon}
                      <div className="text-center">
                        <p className="font-medium text-sm">{action.title}</p>
                        <p className="text-xs text-slate-300 mt-1">{action.description}</p>
                      </div>
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* 시스템 정보 */}
            <Card className="bg-slate-800/50 border-slate-600/30 backdrop-blur-xl">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  시스템 정보
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-300">API 버전</span>
                    <Badge variant="outline" className="text-xs">v1.0.0</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-300">환경</span>
                    <Badge variant="outline" className="text-xs">개발</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-300">마지막 업데이트</span>
                    <span className="text-xs text-slate-400">
                      {new Date().toLocaleString('ko-KR')}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {selectedView === 'errors' && (
          <Card className="bg-slate-800/50 border-slate-600/30 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-yellow-400" />
                오류 현황
              </CardTitle>
            </CardHeader>
            <CardContent>
              {systemStatus.errors.count === 0 ? (
                <div className="text-center py-8">
                  <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-4" />
                  <p className="text-slate-300">현재 오류가 없습니다.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {systemStatus.errors.recent.map((error) => (
                    <div key={error.id} className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                      <div>
                        <p className="text-sm font-medium text-white">{error.type}</p>
                        <p className="text-xs text-slate-400">{error.message}</p>
                      </div>
                      <span className="text-xs text-slate-500">{error.timestamp}</span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {selectedView === 'analytics' && (
          <Card className="bg-slate-800/50 border-slate-600/30 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                데이터 분석
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-lg font-medium text-white mb-4">계층별 분포</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">업종</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-slate-700 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full" 
                            style={{ width: `${(stats.industries.active / Math.max(stats.industries.total, 1)) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-slate-400">
                          {stats.industries.active}/{stats.industries.total}
                        </span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">브랜드</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-slate-700 rounded-full h-2">
                          <div 
                            className="bg-purple-500 h-2 rounded-full" 
                            style={{ width: `${(stats.brands.active / Math.max(stats.brands.total, 1)) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-slate-400">
                          {stats.brands.active}/{stats.brands.total}
                        </span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">매장</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-slate-700 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full" 
                            style={{ width: `${(stats.stores.active / Math.max(stats.stores.total, 1)) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-slate-400">
                          {stats.stores.active}/{stats.stores.total}
                        </span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">직원</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-slate-700 rounded-full h-2">
                          <div 
                            className="bg-orange-500 h-2 rounded-full" 
                            style={{ width: `${(stats.employees.active / Math.max(stats.employees.total, 1)) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-slate-400">
                          {stats.employees.active}/{stats.employees.total}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="text-lg font-medium text-white mb-4">시스템 상태</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">백엔드 연결</span>
                      <Badge 
                        variant={systemStatus.backend === 'online' ? 'default' : 'destructive'}
                        className="text-xs"
                      >
                        {systemStatus.backend}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">데이터베이스</span>
                      <Badge 
                        variant={systemStatus.database === 'online' ? 'default' : 'destructive'}
                        className="text-xs"
                      >
                        {systemStatus.database}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">API 응답 시간</span>
                      <span className="text-sm text-slate-400">~200ms</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
} 