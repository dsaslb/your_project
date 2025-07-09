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
  MapPin,
  BarChart3,
  Settings,
  Bell,
  Calendar,
  Package
} from 'lucide-react';

interface BrandStats {
  totalStores: number;
  totalEmployees: number;
  activeStores: number;
  totalRevenue: number;
  growthRate: number;
  averageOrderValue: number;
  customerSatisfaction: number;
}

interface Store {
  id: number;
  name: string;
  address: string;
  employeesCount: number;
  revenue: number;
  status: 'active' | 'inactive' | 'maintenance';
  lastUpdated: string;
  location: string;
}

export default function BrandDashboard() {
  const [stats, setStats] = useState<BrandStats>({
    totalStores: 0,
    totalEmployees: 0,
    activeStores: 0,
    totalRevenue: 0,
    growthRate: 0,
    averageOrderValue: 0,
    customerSatisfaction: 0
  });

  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 로그인 시에만 데이터 fetch (실시간 아님)
    loadBrandData();
  }, []);

  const loadBrandData = async () => {
    try {
      // 실제로는 백엔드 API에서 데이터 가져오기
      // 현재는 더미 데이터 사용
      const mockStats: BrandStats = {
        totalStores: 8,
        totalEmployees: 45,
        activeStores: 7,
        totalRevenue: 280000000,
        growthRate: 12.5,
        averageOrderValue: 45000,
        customerSatisfaction: 4.8
      };

      const mockStores: Store[] = [
        {
          id: 1,
          name: '강남점',
          address: '서울 강남구 테헤란로 123',
          employeesCount: 8,
          revenue: 45000000,
          status: 'active',
          lastUpdated: '2024-01-15T14:30:00',
          location: '강남구'
        },
        {
          id: 2,
          name: '홍대점',
          address: '서울 마포구 홍대로 456',
          employeesCount: 6,
          revenue: 38000000,
          status: 'active',
          lastUpdated: '2024-01-15T14:25:00',
          location: '마포구'
        },
        {
          id: 3,
          name: '잠실점',
          address: '서울 송파구 올림픽로 789',
          employeesCount: 7,
          revenue: 42000000,
          status: 'active',
          lastUpdated: '2024-01-15T14:20:00',
          location: '송파구'
        },
        {
          id: 4,
          name: '부산점',
          address: '부산 해운대구 해운대로 321',
          employeesCount: 5,
          revenue: 35000000,
          status: 'active',
          lastUpdated: '2024-01-15T14:15:00',
          location: '해운대구'
        },
        {
          id: 5,
          name: '대구점',
          address: '대구 중구 동성로 654',
          employeesCount: 6,
          revenue: 32000000,
          status: 'active',
          lastUpdated: '2024-01-15T14:10:00',
          location: '중구'
        },
        {
          id: 6,
          name: '광주점',
          address: '광주 서구 상무대로 987',
          employeesCount: 4,
          revenue: 28000000,
          status: 'active',
          lastUpdated: '2024-01-15T14:05:00',
          location: '서구'
        },
        {
          id: 7,
          name: '대전점',
          address: '대전 유성구 대학로 147',
          employeesCount: 5,
          revenue: 30000000,
          status: 'active',
          lastUpdated: '2024-01-15T14:00:00',
          location: '유성구'
        },
        {
          id: 8,
          name: '인천점',
          address: '인천 연수구 송도대로 258',
          employeesCount: 4,
          revenue: 20000000,
          status: 'maintenance',
          lastUpdated: '2024-01-15T13:55:00',
          location: '연수구'
        }
      ];

      setStats(mockStats);
      setStores(mockStores);
    } catch (error) {
      console.error('브랜드 데이터 로드 오류:', error);
    } finally {
      setLoading(false);
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
              <Building2 className="h-8 w-8 text-blue-400" />
              <div>
                <h1 className="text-2xl font-bold text-white">브랜드 관리자</h1>
                <p className="text-slate-300">○○브랜드 전체 매장 관리 및 통계</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="text-green-400 border-green-400">
                <Activity className="h-4 w-4 mr-1" />
                브랜드 모니터링
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
              <CardTitle className="text-sm font-medium text-slate-300">총 매장</CardTitle>
              <Store className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.totalStores}</div>
              <p className="text-xs text-slate-400">운영 중인 매장</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">총 직원</CardTitle>
              <Users className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.totalEmployees}</div>
              <p className="text-xs text-slate-400">전체 직원 수</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">월 매출</CardTitle>
              <TrendingUp className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {(stats.totalRevenue / 1000000).toFixed(0)}M
              </div>
              <p className="text-xs text-slate-400">월 총 매출</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">성장률</CardTitle>
              <BarChart3 className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-400">+{stats.growthRate}%</div>
              <p className="text-xs text-slate-400">전월 대비</p>
            </CardContent>
          </Card>
        </div>

        {/* 매장별 상세 정보 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 매장 목록 */}
          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Store className="h-5 w-5" />
                매장별 현황
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stores.map((store) => (
                  <div
                    key={store.id}
                    className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">🏪</div>
                      <div>
                        <h3 className="font-semibold text-white">{store.name}</h3>
                        <p className="text-sm text-slate-400 flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {store.location}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-white">
                        {(store.revenue / 10000).toFixed(0)}만원
                      </div>
                      <Badge className={getStatusColor(store.status)}>
                        {store.status === 'active' ? '운영중' : 
                         store.status === 'inactive' ? '휴점' : '점검중'}
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
                    <span className="text-slate-300">고객 만족도</span>
                    <span className="text-white font-semibold">{stats.customerSatisfaction}/5.0</span>
                  </div>
                  <Progress 
                    value={(stats.customerSatisfaction / 5) * 100} 
                    className="h-2 bg-slate-700"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-300">평균 주문 금액</span>
                    <span className="text-white font-semibold">
                      {stats.averageOrderValue.toLocaleString()}원
                    </span>
                  </div>
                  <Progress 
                    value={75} 
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
                    value={80} 
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
                  <Store className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">새 매장 추가</span>
                </button>
                <button className="p-4 rounded-lg bg-green-500/20 hover:bg-green-500/30 transition-colors text-white">
                  <Users className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">직원 관리</span>
                </button>
                <button className="p-4 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 transition-colors text-white">
                  <Calendar className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">스케줄 관리</span>
                </button>
                <button className="p-4 rounded-lg bg-yellow-500/20 hover:bg-yellow-500/30 transition-colors text-white">
                  <Package className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">재고 관리</span>
                </button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 