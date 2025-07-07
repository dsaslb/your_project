"use client";
import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Building2, 
  Store, 
  Users, 
  BarChart3, 
  Settings, 
  Bell,
  TrendingUp,
  CheckCircle,
  Clock,
  MapPin,
  DollarSign,
  AlertTriangle
} from 'lucide-react';
import useUserStore from '@/store/useUserStore';
import { useRouter } from 'next/navigation';

export default function BrandAdminDashboard() {
  const { user, permissions } = useUserStore();
  const router = useRouter();

  // 권한 확인
  if (!user || !permissions.canAccessBrandAdmin) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="text-red-600">접근 권한 없음</CardTitle>
            <CardDescription>
              브랜드 관리자 권한이 필요합니다.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => router.push('/dashboard')}>
              대시보드로 돌아가기
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // 더미 데이터
  const stats = {
    totalStores: 5,
    totalEmployees: 127,
    totalRevenue: "₩125,000,000",
    monthlyGrowth: "+8.5%",
    storePerformance: [
      { id: 1, name: "강남점", revenue: "₩35,000,000", employees: 28, status: "정상" },
      { id: 2, name: "홍대점", revenue: "₩28,000,000", employees: 25, status: "정상" },
      { id: 3, name: "부산점", revenue: "₩22,000,000", employees: 22, status: "정상" },
      { id: 4, name: "대구점", revenue: "₩20,000,000", employees: 20, status: "점검 필요" },
      { id: 5, name: "인천점", revenue: "₩20,000,000", employees: 20, status: "정상" },
    ],
    recentActivities: [
      { id: 1, action: "강남점 매출 보고서 제출", store: "강남점", time: "10분 전" },
      { id: 2, action: "홍대점 직원 등록", store: "홍대점", time: "30분 전" },
      { id: 3, action: "부산점 재고 업데이트", store: "부산점", time: "1시간 전" },
      { id: 4, action: "대구점 스케줄 변경", store: "대구점", time: "2시간 전" },
    ]
  };

  const stores = [
    {
      name: '강남점',
      location: '서울 강남구',
      status: '운영중',
      employees: 25,
      todaySales: '₩450,000',
      icon: MapPin
    },
    {
      name: '홍대점',
      location: '서울 마포구',
      status: '운영중',
      employees: 22,
      todaySales: '₩380,000',
      icon: MapPin
    },
    {
      name: '부산점',
      location: '부산 해운대구',
      status: '운영중',
      employees: 28,
      todaySales: '₩520,000',
      icon: MapPin
    },
    {
      name: '대구점',
      location: '대구 중구',
      status: '운영중',
      employees: 20,
      todaySales: '₩320,000',
      icon: MapPin
    },
    {
      name: '인천점',
      location: '인천 연수구',
      status: '운영중',
      employees: 18,
      todaySales: '₩280,000',
      icon: MapPin
    }
  ];

  const quickActions = [
    {
      title: '매장 관리',
      description: '매장별 설정 및 관리',
      icon: Store,
      href: '/store-dashboard',
      color: 'bg-blue-500'
    },
    {
      title: '직원 관리',
      description: '직원 등록 및 승인',
      icon: Users,
      href: '/staff',
      color: 'bg-green-500'
    },
    {
      title: '매출 분석',
      description: '매장별 매출 통계',
      icon: BarChart3,
      href: '/analytics',
      color: 'bg-purple-500'
    },
    {
      title: '알림 관리',
      description: '브랜드 알림 설정',
      icon: Bell,
      href: '/notifications',
      color: 'bg-orange-500'
    }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center space-x-3">
            <Building2 className="w-8 h-8 text-blue-600" />
            <span>브랜드 관리자 대시보드</span>
          </h1>
          <p className="text-gray-600 mt-2">
            브랜드별 통합 관리 및 모니터링
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="default" className="bg-blue-600">
            <Building2 className="w-3 h-3 mr-1" />
            브랜드 관리자
          </Badge>
          <Badge variant="outline">
            {user.name}
          </Badge>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 매장</CardTitle>
            <Store className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalStores}</div>
            <p className="text-xs text-muted-foreground">
              운영 중인 매장
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 직원</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalEmployees}</div>
            <p className="text-xs text-muted-foreground">
              +5 this month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 매출</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalRevenue}</div>
            <p className="text-xs text-muted-foreground">
              {stats.monthlyGrowth} from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평균 매출</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₩25,000,000</div>
            <p className="text-xs text-muted-foreground">
              매장당 평균
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 매장별 성과 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Store className="h-5 w-5" />
            <span>매장별 성과</span>
          </CardTitle>
          <CardDescription>
            각 매장의 매출 및 직원 현황
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {stats.storePerformance.map((store) => (
              <div key={store.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div>
                    <h3 className="font-medium">{store.name}</h3>
                    <p className="text-sm text-muted-foreground">{store.employees}명 직원</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="font-medium">{store.revenue}</p>
                    <p className="text-sm text-muted-foreground">월 매출</p>
                  </div>
                  <Badge variant={store.status === "정상" ? "default" : "destructive"}>
                    {store.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 최근 활동 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="h-5 w-5" />
              <span>최근 활동</span>
            </CardTitle>
            <CardDescription>
              매장에서 발생한 최근 활동들
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <p className="font-medium text-sm">{activity.action}</p>
                    <p className="text-xs text-muted-foreground">{activity.store}</p>
                  </div>
                  <span className="text-xs text-muted-foreground">{activity.time}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 빠른 액션 */}
        <Card>
          <CardHeader>
            <CardTitle>빠른 액션</CardTitle>
            <CardDescription>
              자주 사용하는 브랜드 관리 기능들
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <Button variant="outline" className="h-16 flex flex-col space-y-2">
                <Store className="h-5 w-5" />
                <span className="text-sm">매장 관리</span>
              </Button>
              <Button variant="outline" className="h-16 flex flex-col space-y-2">
                <Users className="h-5 w-5" />
                <span className="text-sm">직원 관리</span>
              </Button>
              <Button variant="outline" className="h-16 flex flex-col space-y-2">
                <BarChart3 className="h-5 w-5" />
                <span className="text-sm">브랜드 통계</span>
              </Button>
              <Button variant="outline" className="h-16 flex flex-col space-y-2">
                <AlertTriangle className="h-5 w-5" />
                <span className="text-sm">알림 관리</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 