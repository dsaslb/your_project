'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Building2, 
  Store, 
  Users, 
  TrendingUp, 
  Activity, 
  AlertTriangle,
  Crown,
  BarChart3,
  Settings,
  Bell
} from 'lucide-react';

interface IndustryStats {
  totalIndustries: number;
  totalBrands: number;
  totalStores: number;
  totalEmployees: number;
  activeStores: number;
  totalRevenue: number;
  growthRate: number;
}

interface Industry {
  id: number;
  name: string;
  type: 'hospital' | 'fashion' | 'beauty' | 'restaurant' | 'retail';
  brandsCount: number;
  storesCount: number;
  employeesCount: number;
  revenue: number;
  status: 'active' | 'inactive' | 'maintenance';
  lastUpdated: string;
}

export default function IndustryDashboard() {
  const [stats, setStats] = useState<IndustryStats>({
    totalIndustries: 0,
    totalBrands: 0,
    totalStores: 0,
    totalEmployees: 0,
    activeStores: 0,
    totalRevenue: 0,
    growthRate: 0
  });

  const [industries, setIndustries] = useState<Industry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 로그인 시에만 데이터 fetch (실시간 아님)
    loadIndustryData();
  }, []);

  const loadIndustryData = async () => {
    try {
      // 실제로는 백엔드 API에서 데이터 가져오기
      // 현재는 더미 데이터 사용
      const mockStats: IndustryStats = {
        totalIndustries: 4,
        totalBrands: 12,
        totalStores: 48,
        totalEmployees: 240,
        activeStores: 45,
        totalRevenue: 1250000000,
        growthRate: 15.5
      };

      const mockIndustries: Industry[] = [
        {
          id: 1,
          name: '의료 서비스',
          type: 'hospital',
          brandsCount: 3,
          storesCount: 15,
          employeesCount: 75,
          revenue: 450000000,
          status: 'active',
          lastUpdated: '2024-01-15T14:30:00'
        },
        {
          id: 2,
          name: '패션 리테일',
          type: 'fashion',
          brandsCount: 4,
          storesCount: 18,
          employeesCount: 90,
          revenue: 380000000,
          status: 'active',
          lastUpdated: '2024-01-15T14:25:00'
        },
        {
          id: 3,
          name: '뷰티 서비스',
          type: 'beauty',
          brandsCount: 3,
          storesCount: 12,
          employeesCount: 60,
          revenue: 280000000,
          status: 'active',
          lastUpdated: '2024-01-15T14:20:00'
        },
        {
          id: 4,
          name: '레스토랑',
          type: 'restaurant',
          brandsCount: 2,
          storesCount: 3,
          employeesCount: 15,
          revenue: 140000000,
          status: 'active',
          lastUpdated: '2024-01-15T14:15:00'
        }
      ];

      setStats(mockStats);
      setIndustries(mockIndustries);
    } catch (error) {
      console.error('업종 데이터 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const getIndustryIcon = (type: string) => {
    switch (type) {
      case 'hospital': return '🏥';
      case 'fashion': return '👗';
      case 'beauty': return '💄';
      case 'restaurant': return '🍽️';
      case 'retail': return '🛍️';
      default: return '🏢';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-600';
      case 'inactive': return 'bg-gray-500/20 text-gray-600';
      case 'maintenance': return 'bg-yellow-500/20 text-yellow-600';
      default: return 'bg-gray-500/20 text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* 헤더 */}
      <header className="bg-white/10 backdrop-blur-xl border-b border-white/20">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Crown className="h-8 w-8 text-yellow-400" />
              <div>
                <h1 className="text-2xl font-bold text-white">업종별 최상위 관리자</h1>
                <p className="text-slate-300">전체 업종 통합 관리 및 모니터링</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="text-green-400 border-green-400">
                <Activity className="h-4 w-4 mr-1" />
                실시간 모니터링
              </Badge>
              <div className="text-slate-300 text-sm">
                {new Date().toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">총 업종</CardTitle>
              <Building2 className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.totalIndustries}</div>
              <p className="text-xs text-slate-400">활성 업종 수</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">총 브랜드</CardTitle>
              <Store className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.totalBrands}</div>
              <p className="text-xs text-slate-400">등록된 브랜드</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">총 매장</CardTitle>
              <Users className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.totalStores}</div>
              <p className="text-xs text-slate-400">운영 중인 매장</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">총 매출</CardTitle>
              <TrendingUp className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {(stats.totalRevenue / 1000000).toFixed(0)}M
              </div>
              <p className="text-xs text-slate-400">월 총 매출</p>
            </CardContent>
          </Card>
        </div>

        {/* 업종별 상세 정보 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 업종 목록 */}
          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                업종별 현황
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {industries.map((industry) => (
                  <div
                    key={industry.id}
                    className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">{getIndustryIcon(industry.type)}</div>
                      <div>
                        <h3 className="font-semibold text-white">{industry.name}</h3>
                        <p className="text-sm text-slate-400">
                          {industry.brandsCount}개 브랜드 • {industry.storesCount}개 매장
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-white">
                        {(industry.revenue / 1000000).toFixed(0)}M
                      </div>
                      <Badge className={getStatusColor(industry.status)}>
                        {industry.status === 'active' ? '활성' : 
                         industry.status === 'inactive' ? '비활성' : '점검중'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 성과 지표 */}
          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                성과 지표
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-300">매장 운영률</span>
                    <span className="text-white font-semibold">
                      {((stats.activeStores / stats.totalStores) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <Progress 
                    value={(stats.activeStores / stats.totalStores) * 100} 
                    className="h-2"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-300">성장률</span>
                    <span className="text-green-400 font-semibold">+{stats.growthRate}%</span>
                  </div>
                  <Progress 
                    value={stats.growthRate} 
                    className="h-2 bg-slate-700"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-300">직원당 매출</span>
                    <span className="text-white font-semibold">
                      {Math.round(stats.totalRevenue / stats.totalEmployees).toLocaleString()}원
                    </span>
                  </div>
                  <Progress 
                    value={75} 
                    className="h-2 bg-slate-700"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 빠른 액션 */}
        <div className="mt-8">
          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Settings className="h-5 w-5" />
                빠른 액션
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button className="p-4 rounded-lg bg-blue-500/20 hover:bg-blue-500/30 transition-colors text-white">
                  <Building2 className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">새 업종 추가</span>
                </button>
                <button className="p-4 rounded-lg bg-green-500/20 hover:bg-green-500/30 transition-colors text-white">
                  <Store className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">브랜드 관리</span>
                </button>
                <button className="p-4 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 transition-colors text-white">
                  <Users className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">직원 통계</span>
                </button>
                <button className="p-4 rounded-lg bg-yellow-500/20 hover:bg-yellow-500/30 transition-colors text-white">
                  <Bell className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">알림 설정</span>
                </button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 