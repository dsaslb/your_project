"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Users, 
  TrendingUp, 
  DollarSign, 
  ShoppingCart,
  ArrowLeft,
  Home,
  Clock,
  Target,
  Calendar,
  Award,
  BarChart3,
  Activity,
  UserCheck
} from 'lucide-react';
import Link from 'next/link';

interface Staff {
  id: number;
  name: string;
  position: string;
  branch_name: string;
  brand_name: string;
  today_orders: number;
  today_revenue: number;
  avg_order_value: number;
}

interface Schedule {
  date: string;
  start_time: string;
  end_time: string;
  type: '근무' | '휴가' | '병가';
}

interface Goal {
  name: string;
  target: number;
  current: number;
  unit: string;
}

export default function StaffPage() {
  const [staff, setStaff] = useState<Staff[]>([]);
  const [selectedStaff, setSelectedStaff] = useState<Staff | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // 직원 데이터 로드
      const staffResponse = await fetch('/api/admin/restaurant/industry/staff');
      const staffData = await staffResponse.json();
      setStaff(staffData);

    } catch (error) {
      console.error('데이터 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  const getSchedule = (): Schedule[] => {
    return [
      { date: '2024-01-15', start_time: '09:00', end_time: '17:00', type: '근무' },
      { date: '2024-01-16', start_time: '09:00', end_time: '17:00', type: '근무' },
      { date: '2024-01-17', start_time: '13:00', end_time: '21:00', type: '근무' },
      { date: '2024-01-18', start_time: '', end_time: '', type: '휴가' },
      { date: '2024-01-19', start_time: '09:00', end_time: '17:00', type: '근무' },
    ];
  };

  const getGoals = (): Goal[] => {
    return [
      { name: '일일 주문 처리', target: 50, current: 35, unit: '건' },
      { name: '일일 매출 목표', target: 500000, current: 420000, unit: '원' },
      { name: '고객 만족도', target: 95, current: 92, unit: '%' },
      { name: '평균 주문 금액', target: 15000, current: 12000, unit: '원' },
    ];
  };

  const getPerformanceData = () => {
    return [
      { date: '1/10', orders: 45, revenue: 450000 },
      { date: '1/11', orders: 52, revenue: 520000 },
      { date: '1/12', orders: 38, revenue: 380000 },
      { date: '1/13', orders: 61, revenue: 610000 },
      { date: '1/14', orders: 48, revenue: 480000 },
      { date: '1/15', orders: 35, revenue: 420000 },
    ];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">👤</div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">직원 대시보드</h1>
                <p className="text-sm text-gray-500">개인 성과 및 스케줄 관리</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/restaurant/hierarchy">
                <Button variant="outline" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  계층 관리
                </Button>
              </Link>
              <Link href="/">
                <Button variant="outline" size="sm">
                  <Home className="h-4 w-4 mr-2" />
                  홈으로
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* 브레드크럼 */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center space-x-2 py-3">
            <Link href="/" className="text-gray-500 hover:text-gray-700">
              홈
            </Link>
            <ArrowLeft className="h-4 w-4 text-gray-400" />
            <Link href="/restaurant/hierarchy" className="text-gray-500 hover:text-gray-700">
              레스토랑 계층 관리
            </Link>
            <ArrowLeft className="h-4 w-4 text-gray-400" />
            <span className="text-gray-900 font-medium">직원 관리</span>
          </div>
        </div>
      </nav>

      {/* 메인 콘텐츠 */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* 직원별 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 직원 수</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{staff.length}명</div>
              <p className="text-xs text-muted-foreground">
                근무 중인 직원
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">오늘 총 주문</CardTitle>
              <ShoppingCart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {staff.reduce((sum, s) => sum + s.today_orders, 0)}건
              </div>
              <p className="text-xs text-muted-foreground">
                전체 직원 합계
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">오늘 총 매출</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(staff.reduce((sum, s) => sum + s.today_revenue, 0))}
              </div>
              <p className="text-xs text-muted-foreground">
                전체 직원 합계
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">평균 주문 금액</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(
                  staff.reduce((sum, s) => sum + s.avg_order_value, 0) / staff.length
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                직원 평균
              </p>
            </CardContent>
          </Card>
        </div>

        {/* 직원 목록 */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold">직원별 현황</h2>
            <p className="text-sm text-gray-600">각 직원의 성과 및 소속 정보</p>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {staff.map((staffMember) => (
                <Card key={staffMember.id} className="hover:shadow-lg transition-shadow cursor-pointer"
                      onClick={() => setSelectedStaff(staffMember)}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="text-lg font-semibold">{staffMember.name}</span>
                      <Badge variant="secondary">{staffMember.position}</Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="text-sm text-gray-600">
                      {staffMember.branch_name} - {staffMember.brand_name}
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="flex items-center gap-1">
                        <ShoppingCart className="h-4 w-4 text-blue-600" />
                        <span className="text-gray-600">오늘 주문:</span>
                      </div>
                      <div className="font-semibold">{staffMember.today_orders}건</div>
                      
                      <div className="flex items-center gap-1">
                        <DollarSign className="h-4 w-4 text-green-600" />
                        <span className="text-gray-600">매출 기여:</span>
                      </div>
                      <div className="font-semibold">{formatCurrency(staffMember.today_revenue)}</div>
                      
                      <div className="flex items-center gap-1">
                        <TrendingUp className="h-4 w-4 text-purple-600" />
                        <span className="text-gray-600">평균 주문:</span>
                      </div>
                      <div className="font-semibold">{formatCurrency(staffMember.avg_order_value)}</div>
                    </div>
                    
                    <Button className="w-full" variant="outline">
                      상세 보기
                      <ArrowLeft className="h-4 w-4 ml-2" />
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>

        {/* 선택된 직원의 상세 정보 */}
        {selectedStaff && (
          <div className="space-y-6">
            {/* 직원 상세 현황 */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">
                    {selectedStaff.name} - 개인 대시보드
                  </h3>
                  <Button variant="ghost" onClick={() => setSelectedStaff(null)}>
                    닫기
                  </Button>
                </div>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* 개인 성과 통계 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <BarChart3 className="h-5 w-5" />
                        개인 성과 통계
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                          <div className="flex items-center gap-3">
                            <ShoppingCart className="h-5 w-5 text-blue-600" />
                            <div>
                              <div className="font-medium">오늘 처리 주문</div>
                              <div className="text-sm text-gray-600">{selectedStaff.today_orders}건</div>
                            </div>
                          </div>
                          <div className="text-2xl font-bold text-blue-600">
                            {selectedStaff.today_orders}
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                          <div className="flex items-center gap-3">
                            <DollarSign className="h-5 w-5 text-green-600" />
                            <div>
                              <div className="font-medium">오늘 매출 기여</div>
                              <div className="text-sm text-gray-600">매출 기여도</div>
                            </div>
                          </div>
                          <div className="text-2xl font-bold text-green-600">
                            {formatCurrency(selectedStaff.today_revenue)}
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                          <div className="flex items-center gap-3">
                            <TrendingUp className="h-5 w-5 text-purple-600" />
                            <div>
                              <div className="font-medium">평균 주문 금액</div>
                              <div className="text-sm text-gray-600">고객당 평균</div>
                            </div>
                          </div>
                          <div className="text-2xl font-bold text-purple-600">
                            {formatCurrency(selectedStaff.avg_order_value)}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* 스케줄 관리 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Calendar className="h-5 w-5" />
                        이번 주 스케줄
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {getSchedule().map((schedule, index) => (
                          <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                            <div className="flex items-center gap-3">
                              <div className="text-sm font-medium">
                                {new Date(schedule.date).toLocaleDateString('ko-KR', { 
                                  month: 'short', 
                                  day: 'numeric' 
                                })}
                              </div>
                              <div className="text-sm text-gray-600">
                                {schedule.start_time && schedule.end_time 
                                  ? `${schedule.start_time} - ${schedule.end_time}`
                                  : schedule.type
                                }
                              </div>
                            </div>
                            <Badge variant={
                              schedule.type === '근무' ? 'default' : 
                              schedule.type === '휴가' ? 'secondary' : 'destructive'
                            }>
                              {schedule.type}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>

            {/* 목표 및 성취 */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  목표 및 성취
                </h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {getGoals().map((goal, index) => (
                    <Card key={index}>
                      <CardContent className="pt-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium">{goal.name}</span>
                          <span className="text-sm text-gray-600">
                            {goal.current}/{goal.target} {goal.unit}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${Math.min((goal.current / goal.target) * 100, 100)}%` }}
                          ></div>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          달성률: {Math.round((goal.current / goal.target) * 100)}%
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </div>

            {/* 성과 분석 */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  최근 6일 성과 분석
                </h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-6 gap-4">
                  {getPerformanceData().map((data, index) => (
                    <Card key={index}>
                      <CardContent className="pt-4">
                        <div className="text-center">
                          <div className="text-sm font-medium mb-2">{data.date}</div>
                          <div className="text-lg font-bold text-blue-600 mb-1">
                            {data.orders}건
                          </div>
                          <div className="text-sm text-gray-600">
                            {formatCurrency(data.revenue)}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </div>

            {/* 빠른 액션 */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b">
                <h3 className="text-lg font-semibold">빠른 액션</h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
                    <Clock className="h-6 w-6 mb-2" />
                    <span className="text-sm">스케줄 확인</span>
                  </Button>
                  <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
                    <Target className="h-6 w-6 mb-2" />
                    <span className="text-sm">목표 설정</span>
                  </Button>
                  <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
                    <Award className="h-6 w-6 mb-2" />
                    <span className="text-sm">성과 리포트</span>
                  </Button>
                  <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
                    <UserCheck className="h-6 w-6 mb-2" />
                    <span className="text-sm">프로필 관리</span>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 직원 성과 분석 */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="px-6 py-4 border-b">
            <h3 className="text-lg font-semibold">직원 성과 분석</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ShoppingCart className="h-5 w-5" />
                    주문 처리 순위
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {staff
                      .sort((a, b) => b.today_orders - a.today_orders)
                      .slice(0, 5)
                      .map((staffMember, index) => (
                        <div key={staffMember.id} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant={index === 0 ? "default" : "secondary"}>
                              {index + 1}
                            </Badge>
                            <span className="font-medium">{staffMember.name}</span>
                          </div>
                          <span className="text-sm font-semibold">
                            {staffMember.today_orders}건
                          </span>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <DollarSign className="h-5 w-5" />
                    매출 기여 순위
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {staff
                      .sort((a, b) => b.today_revenue - a.today_revenue)
                      .slice(0, 5)
                      .map((staffMember, index) => (
                        <div key={staffMember.id} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant={index === 0 ? "default" : "secondary"}>
                              {index + 1}
                            </Badge>
                            <span className="font-medium">{staffMember.name}</span>
                          </div>
                          <span className="text-sm font-semibold">
                            {formatCurrency(staffMember.today_revenue)}
                          </span>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    효율성 순위
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {staff
                      .sort((a, b) => b.avg_order_value - a.avg_order_value)
                      .slice(0, 5)
                      .map((staffMember, index) => (
                        <div key={staffMember.id} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant={index === 0 ? "default" : "secondary"}>
                              {index + 1}
                            </Badge>
                            <span className="font-medium">{staffMember.name}</span>
                          </div>
                          <span className="text-sm font-semibold">
                            {formatCurrency(staffMember.avg_order_value)}
                          </span>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 