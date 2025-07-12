'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Store, 
  Users, 
  TrendingUp, 
  Activity, 
  MapPin,
  BarChart3,
  Settings,
  Bell,
  Calendar,
  Package,
  Clock,
  Star
} from 'lucide-react';

interface StoreStats {
  totalEmployees: number;
  activeEmployees: number;
  todayRevenue: number;
  monthlyRevenue: number;
  growthRate: number;
  averageOrderValue: number;
  customerSatisfaction: number;
  pendingOrders: number;
  lowStockItems: number;
}

interface Employee {
  id: number;
  name: string;
  role: 'manager' | 'staff' | 'kitchen' | 'cashier';
  status: 'active' | 'break' | 'off';
  startTime: string;
  endTime: string;
  avatar: string;
}

export default function StoreDashboard() {
  const [stats, setStats] = useState<StoreStats>({
    totalEmployees: 0,
    activeEmployees: 0,
    todayRevenue: 0,
    monthlyRevenue: 0,
    growthRate: 0,
    averageOrderValue: 0,
    customerSatisfaction: 0,
    pendingOrders: 0,
    lowStockItems: 0
  });

  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 로그인 시에만 데이터 fetch (실시간 아님)
    loadStoreData();
  }, []);

  const loadStoreData = async () => {
    try {
      // 실제로는 백엔드 API에서 데이터 가져오기
      // 현재는 더미 데이터 사용
      const mockStats: StoreStats = {
        totalEmployees: 12,
        activeEmployees: 8,
        todayRevenue: 850000,
        monthlyRevenue: 45000000,
        growthRate: 8.5,
        averageOrderValue: 28000,
        customerSatisfaction: 4.7,
        pendingOrders: 5,
        lowStockItems: 3
      };

      const mockEmployees: Employee[] = [
        {
          id: 1,
          name: '김매니저',
          role: 'manager',
          status: 'active',
          startTime: '09:00',
          endTime: '18:00',
          avatar: '👨‍💼'
        },
        {
          id: 2,
          name: '이주방장',
          role: 'kitchen',
          status: 'active',
          startTime: '08:00',
          endTime: '17:00',
          avatar: '👨‍🍳'
        },
        {
          id: 3,
          name: '박카운터',
          role: 'cashier',
          status: 'active',
          startTime: '10:00',
          endTime: '19:00',
          avatar: '👩‍💼'
        },
        {
          id: 4,
          name: '최서빙',
          role: 'staff',
          status: 'break',
          startTime: '11:00',
          endTime: '20:00',
          avatar: '👩‍🍳'
        },
        {
          id: 5,
          name: '정청소',
          role: 'staff',
          status: 'active',
          startTime: '12:00',
          endTime: '21:00',
          avatar: '🧹'
        },
        {
          id: 6,
          name: '강배달',
          role: 'staff',
          status: 'active',
          startTime: '13:00',
          endTime: '22:00',
          avatar: '🚚'
        }
      ];

      setStats(mockStats);
      setEmployees(mockEmployees);
    } catch (error) {
      console.error('매장 데이터 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'manager': return 'bg-blue-500/20 text-blue-600';
      case 'kitchen': return 'bg-orange-500/20 text-orange-600';
      case 'cashier': return 'bg-green-500/20 text-green-600';
      case 'staff': return 'bg-purple-500/20 text-purple-600';
      default: return 'bg-gray-500/20 text-gray-600';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-600';
      case 'break': return 'bg-yellow-500/20 text-yellow-600';
      case 'off': return 'bg-gray-500/20 text-gray-600';
      default: return 'bg-gray-500/20 text-gray-600';
    }
  };

  const getRoleText = (role: string) => {
    switch (role) {
      case 'manager': return '매니저';
      case 'kitchen': return '주방';
      case 'cashier': return '카운터';
      case 'staff': return '직원';
      default: return '직원';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '근무중';
      case 'break': return '휴식중';
      case 'off': return '퇴근';
      default: return '알 수 없음';
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
              <Store className="h-8 w-8 text-green-400" />
              <div>
                <h1 className="text-2xl font-bold text-white">강남점 관리자</h1>
                <p className="text-slate-300">매장 실시간 운영 및 직원 관리</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="text-green-400 border-green-400">
                <Activity className="h-4 w-4 mr-1" />
                실시간 운영
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
              <CardTitle className="text-sm font-medium text-slate-300">오늘 매출</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {(stats.todayRevenue / 1000).toFixed(0)}K
              </div>
              <p className="text-xs text-slate-400">오늘 총 매출</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">근무 직원</CardTitle>
              <Users className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.activeEmployees}</div>
              <p className="text-xs text-slate-400">현재 근무 중</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">대기 주문</CardTitle>
              <Clock className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.pendingOrders}</div>
              <p className="text-xs text-slate-400">처리 대기 중</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">고객 만족도</CardTitle>
              <Star className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.customerSatisfaction}</div>
              <p className="text-xs text-slate-400">평균 평점</p>
            </CardContent>
          </Card>
        </div>

        {/* 직원 현황 및 성과 지표 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 직원 현황 */}
          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Users className="h-5 w-5" />
                직원 현황
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {employees.map((employee) => (
                  <div
                    key={employee.id}
                    className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">{employee.avatar}</div>
                      <div>
                        <h3 className="font-semibold text-white">{employee.name}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge className={getRoleColor(employee.role)}>
                            {getRoleText(employee.role)}
                          </Badge>
                          <Badge className={getStatusColor(employee.status)}>
                            {getStatusText(employee.status)}
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <div className="text-right text-sm text-slate-300">
                      <div>{employee.startTime} - {employee.endTime}</div>
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
                    <span className="text-slate-300">직원 출근률</span>
                    <span className="text-white font-semibold">
                      {((stats.activeEmployees / stats.totalEmployees) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <Progress 
                    value={(stats.activeEmployees / stats.totalEmployees) * 100} 
                    className="h-2"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-300">월 매출 달성률</span>
                    <span className="text-white font-semibold">85%</span>
                  </div>
                  <Progress 
                    value={85} 
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
                    <span className="text-slate-300">재고 부족 알림</span>
                    <span className="text-white font-semibold">{stats.lowStockItems}개</span>
                  </div>
                  <Progress 
                    value={30} 
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
                  <Users className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">직원 스케줄</span>
                </button>
                <button className="p-4 rounded-lg bg-green-500/20 hover:bg-green-500/30 transition-colors text-white">
                  <Package className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">재고 관리</span>
                </button>
                <button className="p-4 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 transition-colors text-white">
                  <Calendar className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">주문 관리</span>
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