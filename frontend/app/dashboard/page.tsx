'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Badge } from '../../src/components/ui/badge';
import { Button } from '../../src/components/ui/button';
import { Input } from '../../src/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../src/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../src/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../src/components/ui/table';
import { 
  Building2, 
  BarChart3, 
  Store, 
  Users, 
  Plus, 
  Eye, 
  Edit, 
  Trash2, 
  Search, 
  RefreshCw, 
  Zap, 
  Sparkles,
  Globe,
  Shield,
  Activity,
  Target,
  Rocket,
  HardDrive,
  TrendingUp
} from 'lucide-react';
import { toast } from 'sonner';

interface Brand {
  id: number;
  name: string;
  code: string;
  description: string;
  status: 'active' | 'inactive' | 'pending';
  store_count: number;
  employee_count: number;
  total_revenue: number;
  improvement_requests: number;
  ai_diagnoses: number;
  pending_approvals: number;
  last_activity: string;
  industry_id?: number;
}

interface Industry {
  id: number;
  name: string;
  code: string;
  description: string;
  icon: string;
  color: string;
  brand_count: number;
  store_count: number;
  employee_count: number;
  total_revenue: number;
  status: 'active' | 'inactive';
  last_activity: string;
}

export default function Dashboard() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null);
  const [selectedIndustry, setSelectedIndustry] = useState<Industry | null>(null);
  const [viewMode, setViewMode] = useState<'overview' | 'brands' | 'industries' | 'analytics'>('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [pulseAnimation, setPulseAnimation] = useState(false);

  // 인증 토큰 가져오기
  const getAuthToken = () => {
    return localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
  };

  // API 호출 헤더 생성
  const getAuthHeaders = () => {
    const token = getAuthToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    };
  };

  // 연결 상태 확인
  const checkConnection = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiUrl}/api/status`, {
        headers: getAuthHeaders()
      });
      setIsConnected(response.ok);
    } catch (error) {
      setIsConnected(false);
    }
  };

  // 브랜드 데이터 로드
  const loadBrands = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiUrl}/api/admin/brands`, {
        headers: getAuthHeaders()
      });
      if (response.ok) {
        const data = await response.json();
        setBrands(data.brands || []);
      } else {
        console.error('브랜드 로드 실패:', response.status);
        toast.error('브랜드 데이터를 불러오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('브랜드 로드 오류:', error);
      toast.error('브랜드 데이터를 불러오는데 실패했습니다.');
    }
  };

  // 업종 데이터 로드
  const loadIndustries = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiUrl}/api/admin/industries`, {
        headers: getAuthHeaders()
      });
      if (response.ok) {
        const data = await response.json();
        setIndustries(data.industries || []);
      } else {
        console.error('업종 로드 실패:', response.status);
        toast.error('업종 데이터를 불러오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('업종 로드 오류:', error);
      toast.error('업종 데이터를 불러오는데 실패했습니다.');
    }
  };

  // 테스트 로그인
  const testLogin = async () => {
    setPulseAnimation(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiUrl}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: 'admin',
          password: 'admin123'
        })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('authToken', data.token);
        sessionStorage.setItem('authToken', data.token);
        toast.success('퀀텀 로그인 성공!');
        await refreshData();
      } else {
        toast.error('로그인 실패');
      }
    } catch (error) {
      console.error('로그인 오류:', error);
      toast.error('로그인 중 오류가 발생했습니다.');
    } finally {
      setTimeout(() => setPulseAnimation(false), 1000);
    }
  };

  // 데이터 새로고침
  const refreshData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadBrands(),
        loadIndustries(),
        checkConnection()
      ]);
      toast.success('데이터가 동기화되었습니다.');
    } catch (error) {
      console.error('데이터 새로고침 오류:', error);
      toast.error('데이터 동기화에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 상태 배지 생성
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50">활성</Badge>;
      case 'inactive':
        return <Badge className="bg-red-500/20 text-red-400 border-red-500/50">비활성</Badge>;
      case 'pending':
        return <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/50">대기</Badge>;
      default:
        return <Badge className="bg-slate-500/20 text-slate-400 border-slate-500/50">알 수 없음</Badge>;
    }
  };

  // 필터링된 데이터
  const filteredBrands = brands.filter(brand => {
    const matchesSearch = brand.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         brand.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || brand.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const filteredIndustries = industries.filter(industry => {
    const matchesSearch = industry.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         industry.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || industry.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // 통계 데이터
  const stats = {
    totalBrands: brands.length,
    activeBrands: brands.filter(b => b.status === 'active').length,
    totalIndustries: industries.length,
    activeIndustries: industries.filter(i => i.status === 'active').length,
    totalStores: brands.reduce((sum, brand) => sum + brand.store_count, 0),
    totalEmployees: brands.reduce((sum, brand) => sum + brand.employee_count, 0)
  };

  // 더미 데이터 (백엔드 없이도 동작)
  const dummyBrands: Brand[] = [
    {
      id: 1,
      name: '스타벅스',
      code: 'SBUX',
      description: '글로벌 커피 체인',
      status: 'active',
      store_count: 12,
      employee_count: 156,
      total_revenue: 1200000,
      improvement_requests: 3,
      ai_diagnoses: 8,
      pending_approvals: 2,
      last_activity: '2024-01-15 14:30:00'
    },
    {
      id: 2,
      name: '카페베네',
      code: 'CBENE',
      description: '국내 커피 전문점',
      status: 'active',
      store_count: 8,
      employee_count: 89,
      total_revenue: 850000,
      improvement_requests: 1,
      ai_diagnoses: 5,
      pending_approvals: 0,
      last_activity: '2024-01-15 13:45:00'
    },
    {
      id: 3,
      name: '빽다방',
      code: 'BKDAB',
      description: '저가 커피 체인',
      status: 'active',
      store_count: 15,
      employee_count: 203,
      total_revenue: 980000,
      improvement_requests: 2,
      ai_diagnoses: 6,
      pending_approvals: 1,
      last_activity: '2024-01-15 12:20:00'
    }
  ];

  const dummyIndustries: Industry[] = [
    {
      id: 1,
      name: '커피/음료',
      code: 'BEVERAGE',
      description: '음료 및 커피 전문점',
      icon: '☕',
      color: '#8B4513',
      brand_count: 3,
      store_count: 35,
      employee_count: 448,
      total_revenue: 3030000,
      status: 'active',
      last_activity: '2024-01-15 15:00:00'
    },
    {
      id: 2,
      name: '패스트푸드',
      code: 'FASTFOOD',
      description: '패스트푸드 및 간편식',
      icon: '🍔',
      color: '#FF6B35',
      brand_count: 2,
      store_count: 18,
      employee_count: 234,
      total_revenue: 1850000,
      status: 'active',
      last_activity: '2024-01-15 14:15:00'
    }
  ];

  // 초기 데이터 로드
  useEffect(() => {
    // 백엔드 연결 시도 후 실패하면 더미 데이터 사용
    const loadData = async () => {
      try {
        await refreshData();
      } catch (error) {
        console.log('백엔드 연결 실패, 더미 데이터 사용');
        setBrands(dummyBrands);
        setIndustries(dummyIndustries);
        setIsConnected(false);
      }
    };
    
    loadData();
  }, []);

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      {/* 배경 효과 */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(120,119,198,0.3),transparent_50%)]"></div>
      <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(68,68,68,0.2)_50%,transparent_75%)] bg-[length:20px_20px]"></div>
      
      {/* 상단 네온 라인 */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-60"></div>
      
      <div className="relative z-10">
        <div className="container mx-auto px-4 py-8">
          {/* 헤더 */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-cyan-400 rounded-full animate-pulse"></div>
                  <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent animate-pulse">
                    업종별 관리자 대시보드
                  </h1>
                  <Sparkles className="w-8 h-8 text-cyan-400 animate-bounce" />
                </div>
                <p className="text-slate-400 text-lg font-light">
                  업종별 브랜드 및 매장 통합 관리 시스템
                </p>
              </div>
              <div className="flex items-center gap-4">
                <div className={`flex items-center gap-3 px-4 py-2 rounded-full border ${
                  isConnected 
                    ? 'border-emerald-500/50 bg-emerald-500/10 text-emerald-400' 
                    : 'border-red-500/50 bg-red-500/10 text-red-400'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
                  <span className="text-sm font-medium">{isConnected ? '시스템 온라인' : '시스템 오프라인'}</span>
                </div>
                <Button 
                  onClick={testLogin}
                  className={`bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white border-0 shadow-lg shadow-cyan-500/25 transition-all duration-300 ${
                    pulseAnimation ? 'animate-pulse' : ''
                  }`}
                >
                  <Zap className="w-4 h-4 mr-2" />
                  퀀텀 로그인
                </Button>
                <Button 
                  variant="outline" 
                  onClick={refreshData}
                  disabled={loading}
                  className="border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/10 hover:border-cyan-400"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                  동기화
                </Button>
              </div>
            </div>

            {/* 탭 네비게이션 */}
            <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as any)} className="w-full">
              <TabsList className="grid w-full grid-cols-4 bg-slate-900/50 border border-slate-700/50 backdrop-blur-sm">
                <TabsTrigger value="overview" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-cyan-500/20 data-[state=active]:to-blue-500/20 data-[state=active]:text-cyan-400 data-[state=active]:border-cyan-500/50">
                  <Globe className="w-4 h-4 mr-2" />
                  개요
                </TabsTrigger>
                <TabsTrigger value="brands" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-500/20 data-[state=active]:to-pink-500/20 data-[state=active]:text-purple-400 data-[state=active]:border-purple-500/50">
                  <Building2 className="w-4 h-4 mr-2" />
                  브랜드 관리
                </TabsTrigger>
                <TabsTrigger value="industries" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-emerald-500/20 data-[state=active]:to-teal-500/20 data-[state=active]:text-emerald-400 data-[state=active]:border-emerald-500/50">
                  <BarChart3 className="w-4 h-4 mr-2" />
                  업종 관리
                </TabsTrigger>
                <TabsTrigger value="analytics" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500/20 data-[state=active]:to-red-500/20 data-[state=active]:text-orange-400 data-[state=active]:border-orange-500/50">
                  <Target className="w-4 h-4 mr-2" />
                  분석
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>

          {/* 검색 및 필터 */}
          <div className="flex items-center gap-4 mb-8">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-cyan-400 w-5 h-5" />
              <Input
                placeholder="퀀텀 데이터 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-12 bg-slate-900/50 border-slate-700/50 text-white placeholder:text-slate-500 focus:border-cyan-500/50 focus:ring-cyan-500/20"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48 bg-slate-900/50 border-slate-700/50 text-white focus:border-cyan-500/50">
                <SelectValue placeholder="Status Filter" />
              </SelectTrigger>
              <SelectContent className="bg-slate-900 border-slate-700">
                <SelectItem value="all" className="text-white hover:bg-slate-800">전체 시스템</SelectItem>
                <SelectItem value="active" className="text-white hover:bg-slate-800">활성</SelectItem>
                <SelectItem value="inactive" className="text-white hover:bg-slate-800">비활성</SelectItem>
                <SelectItem value="pending" className="text-white hover:bg-slate-800">대기</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as any)}>
            {/* 개요 탭 */}
            <TabsContent value="overview" className="space-y-8">
              {/* 통계 카드 */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm hover:border-cyan-500/50 transition-all duration-300 group">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                      <Building2 className="w-5 h-5 text-cyan-400" />
                      총 브랜드
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <span className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                          {stats.totalBrands}
                        </span>
                      </div>
                      <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50">
                        {stats.activeBrands} 활성
                      </Badge>
                    </div>
                    <div className="mt-2 h-1 bg-slate-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full transition-all duration-500"
                        style={{ width: `${stats.totalBrands > 0 ? (stats.activeBrands / stats.totalBrands) * 100 : 0}%` }}
                      ></div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm hover:border-purple-500/50 transition-all duration-300 group">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-purple-400" />
                      총 업종
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <span className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
                          {stats.totalIndustries}
                        </span>
                      </div>
                      <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50">
                        {stats.activeIndustries} 활성
                      </Badge>
                    </div>
                    <div className="mt-2 h-1 bg-slate-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-purple-400 to-pink-500 rounded-full transition-all duration-500"
                        style={{ width: `${stats.totalIndustries > 0 ? (stats.activeIndustries / stats.totalIndustries) * 100 : 0}%` }}
                      ></div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm hover:border-emerald-500/50 transition-all duration-300 group">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                      <Store className="w-5 h-5 text-emerald-400" />
                      총 매장
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center">
                      <span className="text-4xl font-bold bg-gradient-to-r from-emerald-400 to-teal-500 bg-clip-text text-transparent">
                        {stats.totalStores}
                      </span>
                    </div>
                    <div className="mt-2 h-1 bg-slate-700 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-emerald-400 to-teal-500 rounded-full animate-pulse"></div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm hover:border-orange-500/50 transition-all duration-300 group">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                      <Users className="w-5 h-5 text-orange-400" />
                      총 직원
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center">
                      <span className="text-4xl font-bold bg-gradient-to-r from-orange-400 to-red-500 bg-clip-text text-transparent">
                        {stats.totalEmployees}
                      </span>
                    </div>
                    <div className="mt-2 h-1 bg-slate-700 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-orange-400 to-red-500 rounded-full animate-pulse"></div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* 시스템 모니터링 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-cyan-400">
                      <Activity className="w-5 h-5" />
                      퀀텀 활동 피드
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {brands.slice(0, 5).map((brand, index) => (
                        <div key={brand.id} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-700/50 hover:border-cyan-500/50 transition-all duration-300">
                          <div>
                            <p className="font-medium text-white">{brand.name}</p>
                            <p className="text-sm text-slate-400 font-mono">{brand.code}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-cyan-400">{brand.store_count} 매장</p>
                            <p className="text-xs text-slate-500">{brand.employee_count} 직원</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-emerald-400">
                      <Shield className="w-5 h-5" />
                      시스템 상태
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 bg-emerald-500/10 rounded-lg border border-emerald-500/30">
                        <div className="flex items-center gap-3">
                          <div className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse"></div>
                          <span className="text-white">퀀텀 백엔드</span>
                        </div>
                        <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50">정상 운영</Badge>
                      </div>
                      <div className="flex items-center justify-between p-4 bg-blue-500/10 rounded-lg border border-blue-500/30">
                        <div className="flex items-center gap-3">
                          <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse"></div>
                          <span className="text-white">신경망 데이터베이스</span>
                        </div>
                        <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/50">온라인</Badge>
                      </div>
                      <div className="flex items-center justify-between p-4 bg-purple-500/10 rounded-lg border border-purple-500/30">
                        <div className="flex items-center gap-3">
                          <div className="w-3 h-3 bg-purple-400 rounded-full animate-pulse"></div>
                          <span className="text-white">AI 프로세서</span>
                        </div>
                        <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/50">활성</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* 브랜드 관리 탭 */}
            <TabsContent value="brands" className="space-y-6">
              <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between text-purple-400">
                    <span className="flex items-center gap-2">
                      <Building2 className="w-5 h-5" />
                      퀀텀 브랜드 매트릭스
                    </span>
                    <Button size="sm" className="bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 border-0">
                      <Plus className="w-4 h-4 mr-2" />
                      새 브랜드
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow className="border-slate-700/50 hover:bg-slate-800/50">
                        <TableHead className="text-slate-400">브랜드명</TableHead>
                        <TableHead className="text-slate-400">퀀텀 코드</TableHead>
                        <TableHead className="text-slate-400">매장</TableHead>
                        <TableHead className="text-slate-400">직원</TableHead>
                        <TableHead className="text-slate-400">상태</TableHead>
                        <TableHead className="text-slate-400">액션</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredBrands.map((brand) => (
                        <TableRow key={brand.id} className="border-slate-700/50 hover:bg-slate-800/50 transition-all duration-300">
                          <TableCell className="font-medium text-white">{brand.name}</TableCell>
                          <TableCell className="font-mono text-cyan-400">{brand.code}</TableCell>
                          <TableCell className="text-emerald-400">{brand.store_count}</TableCell>
                          <TableCell className="text-orange-400">{brand.employee_count}</TableCell>
                          <TableCell>{getStatusBadge(brand.status)}</TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Button size="sm" variant="ghost" className="text-cyan-400 hover:bg-cyan-500/10">
                                <Eye className="w-4 h-4" />
                              </Button>
                              <Button size="sm" variant="ghost" className="text-purple-400 hover:bg-purple-500/10">
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button size="sm" variant="ghost" className="text-red-400 hover:bg-red-500/10">
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </TabsContent>

            {/* 업종 관리 탭 */}
            <TabsContent value="industries" className="space-y-6">
              <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between text-emerald-400">
                    <span className="flex items-center gap-2">
                      <BarChart3 className="w-5 h-5" />
                      업종 퀀텀 매트릭스
                    </span>
                    <Button size="sm" className="bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 border-0">
                      <Plus className="w-4 h-4 mr-2" />
                      새 업종
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow className="border-slate-700/50 hover:bg-slate-800/50">
                        <TableHead className="text-slate-400">업종명</TableHead>
                        <TableHead className="text-slate-400">퀀텀 코드</TableHead>
                        <TableHead className="text-slate-400">브랜드</TableHead>
                        <TableHead className="text-slate-400">매장</TableHead>
                        <TableHead className="text-slate-400">상태</TableHead>
                        <TableHead className="text-slate-400">액션</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredIndustries.map((industry) => (
                        <TableRow key={industry.id} className="border-slate-700/50 hover:bg-slate-800/50 transition-all duration-300">
                          <TableCell className="font-medium text-white">{industry.name}</TableCell>
                          <TableCell className="font-mono text-cyan-400">{industry.code}</TableCell>
                          <TableCell className="text-purple-400">{industry.brand_count}</TableCell>
                          <TableCell className="text-emerald-400">{industry.store_count}</TableCell>
                          <TableCell>{getStatusBadge(industry.status)}</TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Button size="sm" variant="ghost" className="text-cyan-400 hover:bg-cyan-500/10">
                                <Eye className="w-4 h-4" />
                              </Button>
                              <Button size="sm" variant="ghost" className="text-purple-400 hover:bg-purple-500/10">
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button size="sm" variant="ghost" className="text-red-400 hover:bg-red-500/10">
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </TabsContent>

            {/* 분석 탭 */}
            <TabsContent value="analytics" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 업종별 성과 분석 */}
                <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-orange-400">
                      <Target className="w-5 h-5" />
                      업종별 성과 분석
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {industries.map((industry) => (
                        <div key={industry.id} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-white">{industry.name}</h4>
                            <span className="text-sm text-orange-400 font-mono">
                              {industry.total_revenue.toLocaleString()}원
                            </span>
                          </div>
                          <div className="grid grid-cols-3 gap-4 text-sm">
                            <div>
                              <span className="text-slate-400">브랜드:</span>
                              <span className="text-purple-400 ml-1">{industry.brand_count}</span>
                            </div>
                            <div>
                              <span className="text-slate-400">매장:</span>
                              <span className="text-emerald-400 ml-1">{industry.store_count}</span>
                            </div>
                            <div>
                              <span className="text-slate-400">직원:</span>
                              <span className="text-orange-400 ml-1">{industry.employee_count}</span>
                            </div>
                          </div>
                          <div className="mt-3 h-2 bg-slate-700 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-gradient-to-r from-orange-400 to-red-500 rounded-full transition-all duration-500"
                              style={{ width: `${Math.min((industry.total_revenue / 5000000) * 100, 100)}%` }}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* 브랜드별 매출 분석 */}
                <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-purple-400">
                      <TrendingUp className="w-5 h-5" />
                      브랜드별 매출 분석
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {brands.slice(0, 5).map((brand) => (
                        <div key={brand.id} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-white">{brand.name}</h4>
                            <span className="text-sm text-purple-400 font-mono">
                              {brand.total_revenue.toLocaleString()}원
                            </span>
                          </div>
                          <div className="grid grid-cols-3 gap-4 text-sm">
                            <div>
                              <span className="text-slate-400">매장:</span>
                              <span className="text-emerald-400 ml-1">{brand.store_count}</span>
                            </div>
                            <div>
                              <span className="text-slate-400">직원:</span>
                              <span className="text-orange-400 ml-1">{brand.employee_count}</span>
                            </div>
                            <div>
                              <span className="text-slate-400">요청:</span>
                              <span className="text-yellow-400 ml-1">{brand.improvement_requests}</span>
                            </div>
                          </div>
                          <div className="mt-3 h-2 bg-slate-700 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-gradient-to-r from-purple-400 to-pink-500 rounded-full transition-all duration-500"
                              style={{ width: `${Math.min((brand.total_revenue / 2000000) * 100, 100)}%` }}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* 실시간 모니터링 */}
              <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-cyan-400">
                    <Activity className="w-5 h-5" />
                    실시간 모니터링
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="p-4 bg-emerald-500/10 rounded-lg border border-emerald-500/30">
                      <div className="flex items-center gap-2 mb-2">
                        <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                        <span className="text-sm font-medium text-emerald-400">활성 브랜드</span>
                      </div>
                      <span className="text-2xl font-bold text-white">{brands.filter(b => b.status === 'active').length}</span>
                    </div>
                    <div className="p-4 bg-blue-500/10 rounded-lg border border-blue-500/30">
                      <div className="flex items-center gap-2 mb-2">
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                        <span className="text-sm font-medium text-blue-400">총 매장</span>
                      </div>
                      <span className="text-2xl font-bold text-white">{brands.reduce((sum, b) => sum + b.store_count, 0)}</span>
                    </div>
                    <div className="p-4 bg-purple-500/10 rounded-lg border border-purple-500/30">
                      <div className="flex items-center gap-2 mb-2">
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                        <span className="text-sm font-medium text-purple-400">총 직원</span>
                      </div>
                      <span className="text-2xl font-bold text-white">{brands.reduce((sum, b) => sum + b.employee_count, 0)}</span>
                    </div>
                    <div className="p-4 bg-orange-500/10 rounded-lg border border-orange-500/30">
                      <div className="flex items-center gap-2 mb-2">
                        <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse"></div>
                        <span className="text-sm font-medium text-orange-400">개선 요청</span>
                      </div>
                      <span className="text-2xl font-bold text-white">{brands.reduce((sum, b) => sum + b.improvement_requests, 0)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* 하단 네온 라인 */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-400 to-transparent opacity-60"></div>
    </div>
  );
} 