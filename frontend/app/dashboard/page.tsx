'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { OfflineStorage } from '@/utils/offlineStorage';
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
  Search,
  Wifi
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

interface IndustryFormData {
  name: string;
  code: string;
  description: string;
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
  const [isOffline, setIsOffline] = useState(false);
  
  // 업종 생성 관련 상태
  const [isCreateIndustryDialogOpen, setIsCreateIndustryDialogOpen] = useState(false);
  const [industryFormData, setIndustryFormData] = useState<IndustryFormData>({
    name: '',
    code: '',
    description: '',
  });

  const { isLoading, error, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 대시보드 데이터 로드
  const loadDashboardData = async () => {
    try {
      console.log('🔍 백엔드 API 호출 시작...');
      
      // 백엔드 API 직접 호출 시도
      try {
        const baseURL = 'http://192.168.45.44:5000';
        
        // 각 API 엔드포인트 호출 (존재하는 엔드포인트만)
        const [industriesRes, brandsRes] = await Promise.allSettled([
          fetch(`${baseURL}/api/admin/industries`, { signal: AbortSignal.timeout(5000) }),
          fetch(`${baseURL}/api/admin/brands`, { signal: AbortSignal.timeout(5000) })
        ]);

        console.log('📊 API 응답 결과:', {
          industries: industriesRes,
          brands: brandsRes
        });

        // 데이터 파싱 및 처리
        let industries: any[] = [];
        let brands: any[] = [];
        let stores: any[] = []; // 기본값
        let employees: any[] = []; // 기본값

        if (industriesRes.status === 'fulfilled' && industriesRes.value.ok) {
          const industriesData = await industriesRes.value.json();
          console.log('📋 업종 데이터:', industriesData);
          industries = industriesData.data || industriesData.items || industriesData || [];
        }

        if (brandsRes.status === 'fulfilled' && brandsRes.value.ok) {
          const brandsData = await brandsRes.value.json();
          console.log('📋 브랜드 데이터:', brandsData);
          brands = brandsData.data || brandsData.items || brandsData || [];
        }

        // 매장과 직원은 현재 API가 없으므로 기본값 사용
        console.log('📋 매장 데이터: API 없음, 기본값 사용');
        console.log('📋 직원 데이터: API 없음, 기본값 사용');

        // 활성 상태 필터링
        const activeIndustries = industries.filter((item: any) => 
          item.status === 'active' || item.status === 'ACTIVE' || item.is_active === true
        );
        const activeBrands = brands.filter((item: any) => 
          item.status === 'active' || item.status === 'ACTIVE' || item.is_active === true
        );
        const activeStores = stores.filter((item: any) => 
          item.status === 'active' || item.status === 'ACTIVE' || item.is_active === true
        );
        const activeEmployees = employees.filter((item: any) => 
          item.status === 'active' || item.status === 'ACTIVE' || item.is_active === true
        );

        const realStats = {
          industries: { total: industries.length, active: activeIndustries.length },
          brands: { total: brands.length, active: activeBrands.length },
          stores: { total: stores.length, active: activeStores.length },
          employees: { total: employees.length, active: activeEmployees.length }
        };

        console.log('✅ 온라인 모드: 백엔드에서 가져온 실제 통계:', realStats);
        setStats(realStats);
        setIsOffline(false);

        // 시스템 상태 업데이트
        setSystemStatus(prev => ({
          ...prev,
          backend: 'online',
          database: 'online',
          lastSync: typeof window !== 'undefined' ? new Date().toLocaleString('ko-KR') : '로딩 중...'
        }));

      } catch (apiError) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 전환:', apiError);
        
        // 오프라인 모드: 로컬 데이터 사용
        const offlineIndustries = OfflineStorage.loadIndustries();
        const offlineBrands = OfflineStorage.loadBrands();
        
        // 로컬 데이터가 없으면 기본 데이터 생성
        if (offlineIndustries.length === 0 && offlineBrands.length === 0) {
          console.log('📦 기본 오프라인 데이터 생성');
          const defaultData = OfflineStorage.createDefaultData();
          OfflineStorage.saveIndustries(defaultData.industries);
          OfflineStorage.saveBrands(defaultData.brands);
        }
        
        const industries = OfflineStorage.loadIndustries();
        const brands = OfflineStorage.loadBrands();
        
        // 활성 상태 필터링
        const activeIndustries = industries.filter((item: any) => 
          item.status === 'active' || item.status === 'ACTIVE' || item.is_active === true
        );
        const activeBrands = brands.filter((item: any) => 
          item.status === 'active' || item.status === 'ACTIVE' || item.is_active === true
        );

        const offlineStats = {
          industries: { total: industries.length, active: activeIndustries.length },
          brands: { total: brands.length, active: activeBrands.length },
          stores: { total: 0, active: 0 },
          employees: { total: 0, active: 0 }
        };

        console.log('✅ 오프라인 모드: 로컬 데이터 통계:', offlineStats);
        setStats(offlineStats);
        setIsOffline(true);

        // 시스템 상태 업데이트
        setSystemStatus(prev => ({
          ...prev,
          backend: 'offline',
          database: 'offline',
          lastSync: OfflineStorage.getLastSync() ? 
            new Date(OfflineStorage.getLastSync()!).toLocaleString('ko-KR') : '동기화 없음'
        }));
      }

    } catch (error) {
      console.error('❌ 대시보드 데이터 로드 실패:', error);
      
      // 최종 폴백: 기본값 사용
      const fallbackData = {
        industries: { total: 0, active: 0 },
        brands: { total: 0, active: 0 },
        stores: { total: 0, active: 0 },
        employees: { total: 0, active: 0 }
      };

      console.log('🔄 최종 폴백: 기본값 사용:', fallbackData);
      setStats(fallbackData);
      setIsOffline(true);
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
      console.log('🔍 시스템 상태 체크 시작...');
      
      // 간단한 업종 API 테스트로 백엔드 상태 확인
      const testResponse = await fetch('http://192.168.45.44:5000/api/admin/industries');
      if (testResponse.ok) {
        console.log('✅ 백엔드 연결 성공');
        setSystemStatus(prev => ({
          ...prev,
          backend: 'online',
          database: 'online',
          lastSync: typeof window !== 'undefined' ? new Date().toLocaleString('ko-KR') : '로딩 중...'
        }));
      } else {
        throw new Error(`HTTP ${testResponse.status}`);
      }
    } catch (error) {
      console.log('❌ 백엔드 연결 실패:', error);
      setSystemStatus(prev => ({
        ...prev,
        backend: 'offline',
        database: 'offline',
        lastSync: typeof window !== 'undefined' ? new Date().toLocaleString('ko-KR') : '로딩 중...'
      }));
    }
  };

  useEffect(() => {
    loadDashboardData();
    checkSystemStatus();
    
    // 2분마다 상태 체크 (백엔드 부하 감소)
    const interval = setInterval(checkSystemStatus, 120000);
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

  // 업종 생성 관련 함수들
  const resetIndustryForm = () => {
    setIndustryFormData({
      name: '',
      code: '',
      description: '',
    });
  };

  const handleIndustryInputChange = (field: keyof IndustryFormData, value: string) => {
    setIndustryFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleCreateIndustry = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!industryFormData.name.trim() || !industryFormData.code.trim()) {
      toast.error('업종명과 코드는 필수 입력 항목입니다.');
      return;
    }

    try {
      // 온라인 모드: 백엔드 API 호출
      try {
        const response = await fetch('http://192.168.45.44:5000/api/admin/industries', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(industryFormData),
          signal: AbortSignal.timeout(5000)
        });
        
        if (response.ok) {
          toast.success('업종이 성공적으로 생성되었습니다.');
          setIsCreateIndustryDialogOpen(false);
          resetIndustryForm();
          loadDashboardData(); // 대시보드 데이터 새로고침
          return;
        }
      } catch (apiError) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
      }
      
      // 오프라인 모드: 로컬 데이터 생성
      const newIndustry = {
        id: Date.now(),
        ...industryFormData,
        brand_count: 0,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      const existingIndustries = OfflineStorage.loadIndustries();
      const updatedIndustries = [...existingIndustries, newIndustry];
      OfflineStorage.saveIndustries(updatedIndustries);
      OfflineStorage.setOfflineMode(true);
      
      toast.success('업종이 오프라인 모드에서 생성되었습니다.');
      setIsCreateIndustryDialogOpen(false);
      resetIndustryForm();
      loadDashboardData(); // 대시보드 데이터 새로고침
      
    } catch (error) {
      console.error('업종 생성 오류:', error);
      toast.error('업종 생성 중 오류가 발생했습니다.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* 헤더 */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-white quantum-pulse">퀀텀 멀티테넌시 관리 시스템</h1>
              {isOffline && (
                <Badge variant="secondary" className="bg-yellow-900/50 text-yellow-300 border-yellow-600/30">
                  <Wifi className="w-3 h-3 mr-1" />
                  오프라인 모드
                </Badge>
              )}
            </div>
            <p className="text-slate-300">미래적 계층별 현황 및 시스템 상태 모니터링</p>
          </div>
          <div className="flex items-center gap-4">
            {isOffline && (
              <Button
                onClick={handleRefresh}
                variant="outline"
                className="border-yellow-600/50 text-yellow-400 hover:bg-yellow-600/20 hover:border-yellow-500"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                동기화 시도
              </Button>
            )}
            <Button
              onClick={() => {
                resetIndustryForm();
                setIsCreateIndustryDialogOpen(true);
              }}
              className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold px-6 py-2 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300"
            >
              <Plus className="w-5 h-5 mr-2" />
              새 업종 생성
            </Button>
            <Button
              onClick={handleRefresh}
              disabled={isLoading}
              className="bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-400 border-cyan-500/30 hover:from-cyan-500/30 hover:to-purple-500/30 hover:border-cyan-400"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              새로고침
            </Button>
          </div>
        </div>

        {/* 시스템 상태 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="quantum-glass quantum-hover">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Database className="w-5 h-5 text-cyan-400 quantum-neon" />
                  <span className="text-sm text-slate-300">백엔드</span>
                </div>
                <div className={`flex items-center gap-1 ${getStatusColor(systemStatus.backend)}`}>
                  {getStatusIcon(systemStatus.backend)}
                  <span className="text-xs font-medium">{systemStatus.backend}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="quantum-glass quantum-hover">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Activity className="w-5 h-5 text-green-400 quantum-neon" />
                  <span className="text-sm text-slate-300">데이터베이스</span>
                </div>
                <div className={`flex items-center gap-1 ${getStatusColor(systemStatus.database)}`}>
                  {getStatusIcon(systemStatus.database)}
                  <span className="text-xs font-medium">{systemStatus.database}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="quantum-glass quantum-hover">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <BarChart3 className="w-5 h-5 text-purple-400 quantum-neon" />
                  <span className="text-sm text-slate-300">오류 수</span>
                </div>
                <Badge variant="destructive" className="text-xs">
                  {systemStatus.errors.count}
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card className="quantum-glass quantum-hover">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Settings className="w-5 h-5 text-orange-400 quantum-neon" />
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
          <Card className="quantum-glass quantum-hover">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-300 mb-1">총 업종</p>
                  <p className="text-2xl font-bold text-white">{stats.industries.total}</p>
                  <p className="text-xs text-blue-200 mt-1">
                    활성: {stats.industries.active}
                  </p>
                </div>
                <Building2 className="w-8 h-8 text-blue-400 quantum-neon" />
              </div>
            </CardContent>
          </Card>

          <Card className="quantum-glass quantum-hover">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-purple-300 mb-1">총 브랜드</p>
                  <p className="text-2xl font-bold text-white">{stats.brands.total}</p>
                  <p className="text-xs text-purple-200 mt-1">
                    활성: {stats.brands.active}
                  </p>
                </div>
                <Store className="w-8 h-8 text-purple-400 quantum-neon" />
              </div>
            </CardContent>
          </Card>

          <Card className="quantum-glass quantum-hover">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-300 mb-1">총 매장</p>
                  <p className="text-2xl font-bold text-white">{stats.stores.total}</p>
                  <p className="text-xs text-green-200 mt-1">
                    활성: {stats.stores.active}
                  </p>
                </div>
                <Store className="w-8 h-8 text-green-400 quantum-neon" />
              </div>
            </CardContent>
          </Card>

          <Card className="quantum-glass quantum-hover">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-orange-300 mb-1">총 직원</p>
                  <p className="text-2xl font-bold text-white">{stats.employees.total}</p>
                  <p className="text-xs text-orange-200 mt-1">
                    활성: {stats.employees.active}
                  </p>
                </div>
                <Users className="w-8 h-8 text-orange-400 quantum-neon" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 뷰 선택 */}
        <div className="flex items-center gap-4">
          <Button
            variant={selectedView === 'overview' ? 'default' : 'outline'}
            onClick={() => setSelectedView('overview')}
            className={selectedView === 'overview' 
              ? "bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-400 border-cyan-500/30 hover:from-cyan-500/30 hover:to-purple-500/30"
              : "border-slate-600/50 text-slate-300 hover:bg-slate-700/50 hover:border-slate-500"
            }
          >
            <Eye className="w-4 h-4 mr-2" />
            개요
          </Button>
          <Button
            variant={selectedView === 'errors' ? 'default' : 'outline'}
            onClick={() => setSelectedView('errors')}
            className={selectedView === 'errors' 
              ? "bg-gradient-to-r from-red-500/20 to-orange-500/20 text-red-400 border-red-500/30 hover:from-red-500/30 hover:to-orange-500/30"
              : "border-slate-600/50 text-slate-300 hover:bg-slate-700/50 hover:border-slate-500"
            }
          >
            <AlertTriangle className="w-4 h-4 mr-2" />
            오류 현황
          </Button>
          <Button
            variant={selectedView === 'analytics' ? 'default' : 'outline'}
            onClick={() => setSelectedView('analytics')}
            className={selectedView === 'analytics' 
              ? "bg-gradient-to-r from-purple-500/20 to-pink-500/20 text-purple-400 border-purple-500/30 hover:from-purple-500/30 hover:to-pink-500/30"
              : "border-slate-600/50 text-slate-300 hover:bg-slate-700/50 hover:border-slate-500"
            }
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            분석
          </Button>
        </div>

        {/* 선택된 뷰에 따른 콘텐츠 */}
        {selectedView === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 시스템 현황 */}
            <Card className="quantum-glass quantum-hover">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-green-400" />
                  시스템 현황
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      <span className="text-sm font-medium text-green-300">백엔드 연결</span>
                    </div>
                    <p className="text-xs text-green-200">정상 작동 중</p>
                  </div>
                  <div className="p-4 bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/30 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Database className="w-4 h-4 text-blue-400" />
                      <span className="text-sm font-medium text-blue-300">데이터베이스</span>
                    </div>
                    <p className="text-xs text-blue-200">연결됨</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 시스템 정보 */}
            <Card className="quantum-glass quantum-hover">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Settings className="w-5 h-5 text-orange-400" />
                  시스템 정보
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-300">API 버전</span>
                    <Badge variant="outline" className="text-xs border-slate-600/50 text-slate-300">v1.0.0</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-300">환경</span>
                    <Badge variant="outline" className="text-xs border-slate-600/50 text-slate-300">개발</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-300">마지막 업데이트</span>
                    <span className="text-xs text-slate-400">
                      {systemStatus.lastSync || '로딩 중...'}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {selectedView === 'errors' && (
          <Card className="quantum-glass quantum-hover">
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
                    <div key={error.id} className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg border border-slate-600/30">
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
          <Card className="quantum-glass quantum-hover">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-purple-400" />
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
                        <div className="w-20 bg-slate-700/50 rounded-full h-2">
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
                        <div className="w-20 bg-slate-700/50 rounded-full h-2">
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
                        <div className="w-20 bg-slate-700/50 rounded-full h-2">
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
                        <div className="w-20 bg-slate-700/50 rounded-full h-2">
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

      {/* 업종 생성 다이얼로그 */}
      <Dialog open={isCreateIndustryDialogOpen} onOpenChange={setIsCreateIndustryDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle className="text-white">새 업종 생성</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreateIndustry}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="name" className="text-right text-slate-300">
                  업종명
                </Label>
                <Input
                  id="name"
                  value={industryFormData.name}
                  onChange={(e) => handleIndustryInputChange('name', e.target.value)}
                  className="col-span-3 text-white bg-slate-800/50 border-slate-700/50 focus:ring-cyan-500 focus:border-cyan-500"
                  placeholder="예: 음식점, 카페, 쇼핑몰"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="code" className="text-right text-slate-300">
                  코드
                </Label>
                <Input
                  id="code"
                  value={industryFormData.code}
                  onChange={(e) => handleIndustryInputChange('code', e.target.value)}
                  className="col-span-3 text-white bg-slate-800/50 border-slate-700/50 focus:ring-cyan-500 focus:border-cyan-500"
                  placeholder="예: FOOD, SHOPPING, SERVICE"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="description" className="text-right text-slate-300">
                  설명
                </Label>
                <Textarea
                  id="description"
                  value={industryFormData.description}
                  onChange={(e) => handleIndustryInputChange('description', e.target.value)}
                  className="col-span-3 text-white bg-slate-800/50 border-slate-700/50 focus:ring-cyan-500 focus:border-cyan-500"
                  placeholder="업종에 대한 간단한 설명"
                />
              </div>
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? '생성 중...' : '업종 생성'}
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
} 