"use client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Users, 
  TrendingUp, 
  DollarSign,
  Clock,
  ShoppingCart,
  Package,
  AlertTriangle,
  CheckCircle,
  Calendar,
  Menu,
  Bell
} from "lucide-react";
import { useState } from "react";

interface MobileDashboardProps {
  userRole: string;
  stats: {
    totalUsers?: number;
    totalOrders?: number;
    totalRevenue?: string;
    pendingOrders?: number;
    activeUsers?: number;
    completedOrders?: number;
  };
}

export default function MobileDashboard({ userRole, stats }: MobileDashboardProps) {
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: '개요', icon: TrendingUp },
    { id: 'orders', label: '주문', icon: ShoppingCart },
    { id: 'staff', label: '직원', icon: Users },
    { id: 'alerts', label: '알림', icon: Bell },
  ];

  const renderOverview = () => (
    <div className="space-y-4">
      {/* 주요 통계 카드들 */}
      <div className="grid grid-cols-2 gap-3">
        <Card className="p-3">
          <div className="flex items-center space-x-2">
            <DollarSign className="h-4 w-4 text-green-600" />
            <div>
              <p className="text-xs text-muted-foreground">오늘 매출</p>
              <p className="text-lg font-bold">{stats.totalRevenue || '₩0'}</p>
            </div>
          </div>
        </Card>
        
        <Card className="p-3">
          <div className="flex items-center space-x-2">
            <ShoppingCart className="h-4 w-4 text-blue-600" />
            <div>
              <p className="text-xs text-muted-foreground">대기 주문</p>
              <p className="text-lg font-bold">{stats.pendingOrders || 0}</p>
            </div>
          </div>
        </Card>
        
        <Card className="p-3">
          <div className="flex items-center space-x-2">
            <Users className="h-4 w-4 text-purple-600" />
            <div>
              <p className="text-xs text-muted-foreground">활성 직원</p>
              <p className="text-lg font-bold">{stats.activeUsers || 0}</p>
            </div>
          </div>
        </Card>
        
        <Card className="p-3">
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <div>
              <p className="text-xs text-muted-foreground">완료 주문</p>
              <p className="text-lg font-bold">{stats.completedOrders || 0}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* 빠른 액션 버튼들 */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">빠른 액션</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3">
            <Button variant="outline" size="sm" className="h-12 flex flex-col space-y-1">
              <ShoppingCart className="h-4 w-4" />
              <span className="text-xs">주문 관리</span>
            </Button>
            <Button variant="outline" size="sm" className="h-12 flex flex-col space-y-1">
              <Users className="h-4 w-4" />
              <span className="text-xs">직원 관리</span>
            </Button>
            <Button variant="outline" size="sm" className="h-12 flex flex-col space-y-1">
              <Calendar className="h-4 w-4" />
              <span className="text-xs">스케줄</span>
            </Button>
            <Button variant="outline" size="sm" className="h-12 flex flex-col space-y-1">
              <Package className="h-4 w-4" />
              <span className="text-xs">재고</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderOrders = () => (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">최근 주문</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div>
                  <p className="font-medium text-sm">주문 #{1000 + i}</p>
                  <p className="text-xs text-muted-foreground">아메리카노, 카페라떼</p>
                </div>
                <div className="text-right">
                  <p className="font-medium text-sm">₩{8500 + i * 1000}</p>
                  <Badge variant="secondary" className="text-xs">제조 중</Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderStaff = () => (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">오늘 출근</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { name: '김철수', role: '매니저', status: 'present' },
              { name: '이영희', role: '직원', status: 'present' },
              { name: '박민수', role: '직원', status: 'late' },
            ].map((staff, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                      {staff.name.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <p className="font-medium text-sm">{staff.name}</p>
                    <p className="text-xs text-muted-foreground">{staff.role}</p>
                  </div>
                </div>
                <Badge 
                  variant={staff.status === 'present' ? 'default' : 'secondary'}
                  className={staff.status === 'present' ? 'bg-green-600' : ''}
                >
                  {staff.status === 'present' ? '출근' : '지각'}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderAlerts = () => (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">알림</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center space-x-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
              <div className="flex-1">
                <p className="font-medium text-sm">재고 부족</p>
                <p className="text-xs text-muted-foreground">원두 2kg 남음</p>
              </div>
              <Badge variant="destructive" className="text-xs">긴급</Badge>
            </div>
            
            <div className="flex items-center space-x-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <CheckCircle className="h-4 w-4 text-blue-600" />
              <div className="flex-1">
                <p className="font-medium text-sm">새 직원 등록</p>
                <p className="text-xs text-muted-foreground">홍길동 직원이 등록되었습니다</p>
              </div>
              <Badge variant="secondary" className="text-xs">정보</Badge>
            </div>
            
            <div className="flex items-center space-x-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <div className="flex-1">
                <p className="font-medium text-sm">목표 달성</p>
                <p className="text-xs text-muted-foreground">일일 매출 목표 달성</p>
              </div>
              <Badge variant="default" className="bg-green-600 text-xs">성공</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* 헤더 */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-gray-900 dark:text-white">
              {userRole === 'super_admin' ? '슈퍼 관리자' :
               userRole === 'brand_manager' ? '브랜드 관리자' :
               userRole === 'store_manager' ? '매장 관리자' : '직원'} 대시보드
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              모바일 최적화
            </p>
          </div>
          <Button variant="outline" size="sm">
            <Menu className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* 탭 네비게이션 */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="flex space-x-1 p-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex flex-col items-center space-y-1 p-2 rounded-lg text-xs transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 컨텐츠 */}
      <div className="p-4">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'orders' && renderOrders()}
        {activeTab === 'staff' && renderStaff()}
        {activeTab === 'alerts' && renderAlerts()}
      </div>
    </div>
  );
} 