"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { 
  Store, 
  Users, 
  ShoppingCart, 
  Package, 
  Clock, 
  Star,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  DollarSign,
  Calendar,
  MapPin,
  Phone,
  Mail,
  Settings,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight
} from "lucide-react";

interface StoreMetrics {
  name: string;
  location: string;
  status: 'open' | 'closed' | 'maintenance';
  todayRevenue: number;
  todayOrders: number;
  totalStaff: number;
  activeStaff: number;
  averageRating: number;
  inventoryAlerts: number;
  pendingOrders: number;
  completedOrders: number;
  customerCount: number;
  growth: number;
}

interface StaffData {
  id: number;
  name: string;
  role: string;
  status: 'working' | 'break' | 'off' | 'late';
  startTime: string;
  endTime: string;
  avatar: string;
}

interface OrderData {
  id: number;
  customerName: string;
  items: string[];
  total: number;
  status: 'pending' | 'preparing' | 'ready' | 'completed';
  time: string;
}

export default function StoreDashboard() {
  const [storeMetrics, setStoreMetrics] = useState<StoreMetrics>({
    name: "강남점",
    location: "서울시 강남구 테헤란로 123",
    status: 'open',
    todayRevenue: 1250000,
    todayOrders: 47,
    totalStaff: 15,
    activeStaff: 12,
    averageRating: 4.8,
    inventoryAlerts: 3,
    pendingOrders: 8,
    completedOrders: 39,
    customerCount: 156,
    growth: 12.5
  });

  const [staff, setStaff] = useState<StaffData[]>([
    { id: 1, name: "김철수", role: "매니저", status: 'working', startTime: "09:00", endTime: "18:00", avatar: "KC" },
    { id: 2, name: "이영희", role: "주방장", status: 'working', startTime: "08:00", endTime: "17:00", avatar: "LY" },
    { id: 3, name: "박민수", role: "서버", status: 'break', startTime: "10:00", endTime: "19:00", avatar: "PM" },
    { id: 4, name: "정수진", role: "서버", status: 'working', startTime: "11:00", endTime: "20:00", avatar: "JS" },
    { id: 5, name: "최동현", role: "주방보조", status: 'working', startTime: "09:30", endTime: "18:30", avatar: "CD" }
  ]);

  const [recentOrders, setRecentOrders] = useState<OrderData[]>([
    { id: 1, customerName: "김고객", items: ["김치찌개", "밥"], total: 15000, status: 'completed', time: "14:30" },
    { id: 2, customerName: "이고객", items: ["된장찌개", "밥"], total: 12000, status: 'ready', time: "14:25" },
    { id: 3, customerName: "박고객", items: ["비빔밥"], total: 8000, status: 'preparing', time: "14:20" },
    { id: 4, customerName: "정고객", items: ["갈비찜", "밥", "국"], total: 25000, status: 'pending', time: "14:15" }
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'bg-green-500';
      case 'closed': return 'bg-red-500';
      case 'maintenance': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'open': return '영업중';
      case 'closed': return '휴무';
      case 'maintenance': return '점검중';
      default: return '알 수 없음';
    }
  };

  const getStaffStatusColor = (status: string) => {
    switch (status) {
      case 'working': return 'bg-green-500';
      case 'break': return 'bg-yellow-500';
      case 'off': return 'bg-gray-500';
      case 'late': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStaffStatusText = (status: string) => {
    switch (status) {
      case 'working': return '근무중';
      case 'break': return '휴식중';
      case 'off': return '퇴근';
      case 'late': return '지각';
      default: return '알 수 없음';
    }
  };

  const getOrderStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-500';
      case 'preparing': return 'bg-blue-500';
      case 'ready': return 'bg-green-500';
      case 'completed': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getOrderStatusText = (status: string) => {
    switch (status) {
      case 'pending': return '대기중';
      case 'preparing': return '조리중';
      case 'ready': return '준비완료';
      case 'completed': return '완료';
      default: return '알 수 없음';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">매장 관리자 대시보드</h1>
          <p className="text-gray-600 dark:text-gray-400">{storeMetrics.name} - 실시간 운영 현황</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${getStatusColor(storeMetrics.status)}`} />
            <span className="text-sm font-medium">{getStatusText(storeMetrics.status)}</span>
          </div>
          <Button variant="outline">
            <Settings className="h-4 w-4 mr-2" />
            매장 설정
          </Button>
        </div>
      </div>

      {/* 매장 정보 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Store className="h-5 w-5 mr-2" />
            매장 정보
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3">
              <MapPin className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="font-medium">{storeMetrics.location}</p>
                <p className="text-sm text-muted-foreground">매장 위치</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Phone className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="font-medium">02-1234-5678</p>
                <p className="text-sm text-muted-foreground">매장 전화</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Mail className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="font-medium">gangnam@restaurant.com</p>
                <p className="text-sm text-muted-foreground">매장 이메일</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 오늘의 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">오늘 매출</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(storeMetrics.todayRevenue)}</div>
            <div className="flex items-center space-x-1 text-xs text-muted-foreground">
              {storeMetrics.growth > 0 ? (
                <ArrowUpRight className="h-3 w-3 text-green-500" />
              ) : (
                <ArrowDownRight className="h-3 w-3 text-red-500" />
              )}
              <span className={storeMetrics.growth > 0 ? 'text-green-600' : 'text-red-600'}>
                {storeMetrics.growth > 0 ? '+' : ''}{storeMetrics.growth}%
              </span>
              <span>어제 대비</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">오늘 주문</CardTitle>
            <ShoppingCart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{storeMetrics.todayOrders}</div>
            <p className="text-xs text-muted-foreground">
              완료: {storeMetrics.completedOrders} | 대기: {storeMetrics.pendingOrders}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">고객 수</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{storeMetrics.customerCount}</div>
            <p className="text-xs text-muted-foreground">
              평점: {storeMetrics.averageRating} ⭐
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">재고 알림</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{storeMetrics.inventoryAlerts}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-red-600">재고 부족</span> 상품
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 직원 현황 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Users className="h-5 w-5 mr-2" />
            직원 현황
          </CardTitle>
          <CardDescription>현재 근무 중인 직원 및 스케줄</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {staff.map((member) => (
              <div key={member.id} className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                  {member.avatar}
                </div>
                <div className="flex-1">
                  <p className="font-medium">{member.name}</p>
                  <p className="text-sm text-muted-foreground">{member.role}</p>
                  <p className="text-xs text-muted-foreground">
                    {member.startTime} - {member.endTime}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${getStaffStatusColor(member.status)}`} />
                  <span className="text-xs">{getStaffStatusText(member.status)}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 주문 현황 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <ShoppingCart className="h-5 w-5 mr-2" />
              최근 주문
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentOrders.map((order) => (
                <div key={order.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="flex-1">
                    <p className="font-medium">{order.customerName}</p>
                    <p className="text-sm text-muted-foreground">
                      {order.items.join(', ')}
                    </p>
                    <p className="text-xs text-muted-foreground">{order.time}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{formatCurrency(order.total)}</p>
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${getOrderStatusColor(order.status)}`} />
                      <span className="text-xs">{getOrderStatusText(order.status)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="h-5 w-5 mr-2" />
              주문 상태 분포
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">대기중</span>
                <span className="font-medium">{storeMetrics.pendingOrders}</span>
              </div>
              <Progress value={(storeMetrics.pendingOrders / storeMetrics.todayOrders) * 100} className="h-2" />
              
              <div className="flex items-center justify-between">
                <span className="text-sm">조리중</span>
                <span className="font-medium">5</span>
              </div>
              <Progress value={(5 / storeMetrics.todayOrders) * 100} className="h-2" />
              
              <div className="flex items-center justify-between">
                <span className="text-sm">준비완료</span>
                <span className="font-medium">3</span>
              </div>
              <Progress value={(3 / storeMetrics.todayOrders) * 100} className="h-2" />
              
              <div className="flex items-center justify-between">
                <span className="text-sm">완료</span>
                <span className="font-medium">{storeMetrics.completedOrders}</span>
              </div>
              <Progress value={(storeMetrics.completedOrders / storeMetrics.todayOrders) * 100} className="h-2" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 알림 및 이슈 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <AlertTriangle className="h-5 w-5 mr-2" />
            매장 알림
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center space-x-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <AlertTriangle className="h-4 w-4 text-red-600" />
              <div>
                <p className="font-medium">재고 부족 알림</p>
                <p className="text-sm text-muted-foreground">김치, 된장, 고추가루 재고가 부족합니다.</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
              <Clock className="h-4 w-4 text-yellow-600" />
              <div>
                <p className="font-medium">직원 퇴근 예정</p>
                <p className="text-sm text-muted-foreground">박민수 직원이 19:00에 퇴근 예정입니다.</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <div>
                <p className="font-medium">목표 달성</p>
                <p className="text-sm text-muted-foreground">오늘 매출 목표를 110% 달성했습니다.</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 