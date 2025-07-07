"use client";

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Store, 
  Users, 
  BarChart3, 
  Settings, 
  Bell,
  TrendingUp,
  CheckCircle,
  Clock,
  ShoppingCart,
  Package,
  Calendar,
  MapPin,
  DollarSign,
  AlertTriangle
} from 'lucide-react';
import useUserStore from '@/store/useUserStore';
import { useRouter, useSearchParams } from 'next/navigation';

export default function StoreAdminDashboard() {
  const { user, permissions } = useUserStore();
  const router = useRouter();
  const searchParams = useSearchParams();
  const storeName = searchParams.get('store') || '강남점';

  // 권한 확인
  if (!user || !permissions.canAccessStoreAdmin) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="text-red-600">접근 권한 없음</CardTitle>
            <CardDescription>
              매장 관리자 권한이 필요합니다.
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
  const storeData = {
    storeInfo: {
      name: "강남점",
      address: "서울시 강남구 테헤란로 123",
      manager: "김철수",
      phone: "02-1234-5678"
    },
    stats: {
      totalEmployees: 28,
      activeEmployees: 25,
      todayRevenue: "₩2,450,000",
      monthlyRevenue: "₩35,000,000",
      pendingOrders: 8,
      completedOrders: 156
    },
    todaySchedule: [
      { id: 1, name: "김철수", position: "매니저", startTime: "09:00", endTime: "18:00", status: "present" },
      { id: 2, name: "이영희", position: "직원", startTime: "10:00", endTime: "19:00", status: "present" },
      { id: 3, name: "박민수", position: "직원", startTime: "11:00", endTime: "20:00", status: "late" },
      { id: 4, name: "정수진", position: "직원", startTime: "12:00", endTime: "21:00", status: "absent" },
    ],
    recentOrders: [
      { id: 1, customerName: "김고객", items: ["아메리카노", "카페라떼"], total: 8500, status: "preparing", time: "14:30" },
      { id: 2, customerName: "이고객", items: ["카푸치노", "티라떼"], total: 12000, status: "ready", time: "14:25" },
      { id: 3, customerName: "박고객", items: ["에스프레소"], total: 4500, status: "completed", time: "14:20" },
      { id: 4, customerName: "정고객", items: ["아메리카노", "카페모카"], total: 12000, status: "preparing", time: "14:15" },
    ],
    alerts: [
      { id: 1, type: "warning", message: "재고 부족: 원두 2kg 남음", time: "10분 전" },
      { id: 2, type: "info", message: "새 직원 등록: 홍길동", time: "30분 전" },
      { id: 3, type: "success", message: "일일 매출 목표 달성", time: "1시간 전" },
    ]
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "present":
        return <Badge variant="default" className="bg-green-600"><CheckCircle className="w-3 h-3 mr-1" />출근</Badge>;
      case "late":
        return <Badge variant="secondary">지각</Badge>;
      case "absent":
        return <Badge variant="destructive">결근</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getOrderStatusBadge = (status: string) => {
    switch (status) {
      case "preparing":
        return <Badge variant="secondary">제조 중</Badge>;
      case "ready":
        return <Badge variant="default" className="bg-blue-600">준비 완료</Badge>;
      case "completed":
        return <Badge variant="default" className="bg-green-600">완료</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case "info":
        return <CheckCircle className="h-4 w-4 text-blue-600" />;
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-600" />;
    }
  };

  const stats = [
    {
      title: '오늘 매출',
      value: '₩450,000',
      change: '+12%',
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      title: '총 주문',
      value: '156',
      change: '+8',
      icon: ShoppingCart,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      title: '직원 수',
      value: '25',
      change: '+2',
      icon: Users,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      title: '재고 부족',
      value: '3',
      change: '-1',
      icon: Package,
      color: 'text-red-600',
      bgColor: 'bg-red-100'
    }
  ];

  const storeInfo = {
    name: storeName,
    location: '서울 강남구',
    status: '운영중',
    manager: '김매니저',
    phone: '02-1234-5678',
    address: '서울 강남구 테헤란로 123',
    openTime: '09:00 - 22:00'
  };

  const quickActions = [
    {
      title: '직원 관리',
      description: '직원 등록 및 스케줄 관리',
      icon: Users,
      href: '/staff',
      color: 'bg-blue-500'
    },
    {
      title: '주문 관리',
      description: '발주 및 재고 관리',
      icon: ShoppingCart,
      href: '/orders',
      color: 'bg-green-500'
    },
    {
      title: '스케줄 관리',
      description: '근무표 및 일정 관리',
      icon: Calendar,
      href: '/schedule',
      color: 'bg-purple-500'
    },
    {
      title: '재고 관리',
      description: '재고 현황 및 발주',
      icon: Package,
      href: '/inventory',
      color: 'bg-orange-500'
    }
  ];

  const todaySchedule = [
    { name: '김직원1', position: '주방', time: '09:00-17:00', status: '출근' },
    { name: '이직원2', position: '서빙', time: '10:00-18:00', status: '출근' },
    { name: '박직원3', position: '주방', time: '12:00-20:00', status: '대기' },
    { name: '최직원4', position: '서빙', time: '14:00-22:00', status: '대기' }
  ];

  const recentOrders = [
    { id: '001', item: '토마토', quantity: '10kg', status: '승인됨', time: '10:30' },
    { id: '002', item: '양파', quantity: '5kg', status: '대기중', time: '11:15' },
    { id: '003', item: '고기', quantity: '3kg', status: '승인됨', time: '12:00' },
    { id: '004', item: '쌀', quantity: '20kg', status: '대기중', time: '13:45' }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center space-x-3">
            <Store className="w-8 h-8 text-green-600" />
            <span>{storeInfo.name} 관리자 대시보드</span>
          </h1>
          <p className="text-gray-600 mt-2">
            매장별 운영 관리 및 모니터링
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="default" className="bg-green-600">
            <Store className="w-3 h-3 mr-1" />
            매장 관리자
          </Badge>
          <Badge variant="outline">
            {user.name}
          </Badge>
        </div>
      </div>

      {/* 매장 정보 */}
      <Card className="bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center">
                <MapPin className="w-6 h-6 text-white" />
              </div>
              <div>
                <CardTitle className="text-xl">{storeInfo.name}</CardTitle>
                <CardDescription className="flex items-center space-x-2">
                  <MapPin className="w-3 h-3" />
                  <span>{storeInfo.address}</span>
                </CardDescription>
              </div>
            </div>
            <div className="text-right">
              <Badge variant="default" className="bg-green-600">
                <CheckCircle className="w-3 h-3 mr-1" />
                {storeInfo.status}
              </Badge>
              <p className="text-sm text-gray-600 mt-1">{storeInfo.openTime}</p>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`w-4 h-4 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">
                  <span className={stat.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}>
                    {stat.change}
                  </span> 어제 대비
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* 빠른 액션 */}
      <div>
        <h2 className="text-xl font-semibold mb-4">빠른 액션</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <Card 
                key={index}
                className="cursor-pointer hover:shadow-lg transition-all duration-200 hover:scale-105"
                onClick={() => router.push(action.href)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center space-x-3">
                    <div className={`w-10 h-10 ${action.color} rounded-lg flex items-center justify-center`}>
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{action.title}</CardTitle>
                      <CardDescription className="text-sm">
                        {action.description}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <Button size="sm" variant="outline" className="w-full">
                    접속하기
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* 오늘 스케줄과 최근 주문 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Calendar className="w-5 h-5 text-blue-600" />
              <span>오늘 스케줄</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {storeData.todaySchedule.map((employee) => (
                <div key={employee.id} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">{employee.name}</p>
                    <p className="text-sm text-gray-600">{employee.position} • {employee.startTime} - {employee.endTime}</p>
                  </div>
                  {getStatusBadge(employee.status)}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <ShoppingCart className="w-5 h-5 text-green-600" />
              <span>최근 발주</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {storeData.recentOrders.map((order) => (
                <div key={order.id} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">{order.customerName}</p>
                    <p className="text-sm text-gray-600">주문번호: {order.id} • {order.items.join(", ")}</p>
                  </div>
                  <div className="text-right">
                    <Badge variant={getOrderStatusBadge(order.status)}>
                      {getOrderStatusBadge(order.status)}
                    </Badge>
                    <p className="text-xs text-gray-500 mt-1">{order.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 매장 통계 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5 text-purple-600" />
              <span>주간 매출 추이</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span>월요일</span>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div className="bg-purple-600 h-2 rounded-full" style={{width: '65%'}}></div>
                  </div>
                  <span className="text-sm font-medium">₩65만원</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span>화요일</span>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div className="bg-purple-600 h-2 rounded-full" style={{width: '78%'}}></div>
                  </div>
                  <span className="text-sm font-medium">₩78만원</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span>수요일</span>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div className="bg-purple-600 h-2 rounded-full" style={{width: '85%'}}></div>
                  </div>
                  <span className="text-sm font-medium">₩85만원</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="w-5 h-5 text-blue-600" />
              <span>직원 현황</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span>총 직원 수</span>
                <Badge variant="default">25명</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span>출근 중</span>
                <Badge variant="default" className="bg-green-600">18명</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span>휴가/병가</span>
                <Badge variant="secondary">3명</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span>미출근</span>
                <Badge variant="destructive">4명</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 알림 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5" />
            <span>매장 알림</span>
          </CardTitle>
          <CardDescription>
            주의가 필요한 알림들
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {storeData.alerts.map((alert) => (
              <div key={alert.id} className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                {getAlertIcon(alert.type)}
                <div className="flex-1">
                  <p className="font-medium text-sm">{alert.message}</p>
                  <p className="text-xs text-muted-foreground">{alert.time}</p>
                </div>
                <Badge variant={alert.type === "warning" ? "destructive" : "secondary"}>
                  {alert.type === "warning" ? "경고" : alert.type === "info" ? "정보" : "성공"}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 