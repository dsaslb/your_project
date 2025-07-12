'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Building2, 
  Store, 
  Users, 
  Settings, 
  BarChart3, 
  Calendar,
  ShoppingCart,
  Package,
  Bell,
  Shield,
  Crown
} from 'lucide-react';
import useUserStore from '@/store/useUserStore';

const PermissionNav = () => {
  const { user } = useUserStore();
  const router = useRouter();

  if (!user) {
    return null;
  }

  const navigationItems = [
    {
      title: '슈퍼 관리자 대시보드',
      description: '전체 시스템 관리 및 모니터링',
      href: '/admin-dashboard',
      icon: Crown,
      color: 'bg-purple-500',
      requiredPermission: 'canAccessSuperAdmin',
      role: 'super_admin'
    },
    {
      title: '브랜드 관리자 대시보드',
      description: '브랜드별 통합 관리',
      href: '/brand-dashboard',
      icon: Building2,
      color: 'bg-blue-500',
      requiredPermission: 'canAccessBrandAdmin',
      role: 'brand_admin'
    },
    {
      title: '매장 관리자 대시보드',
      description: '매장별 운영 관리',
      href: '/store-dashboard',
      icon: Store,
      color: 'bg-green-500',
      requiredPermission: 'canAccessStoreAdmin',
      role: 'store_admin'
    },
    {
      title: '일반 대시보드',
      description: '기본 업무 대시보드',
      href: '/dashboard',
      icon: BarChart3,
      color: 'bg-gray-500',
      requiredPermission: 'canAccessStaff',
      role: 'staff'
    }
  ];

  const featureItems = [
    {
      title: '직원 관리',
      description: '직원 등록, 승인, 관리',
      href: '/staff',
      icon: Users,
      color: 'bg-indigo-500'
    },
    {
      title: '스케줄 관리',
      description: '근무표 및 일정 관리',
      href: '/schedule',
      icon: Calendar,
      color: 'bg-orange-500'
    },
    {
      title: '주문 관리',
      description: '주문 처리 및 관리',
      href: '/orders',
      icon: ShoppingCart,
      color: 'bg-red-500'
    },
    {
      title: '재고 관리',
      description: '재고 현황 및 발주',
      href: '/inventory',
      icon: Package,
      color: 'bg-teal-500'
    },
    {
      title: '알림 센터',
      description: '시스템 알림 관리',
      href: '/notifications',
      icon: Bell,
      color: 'bg-yellow-500'
    },
    {
      title: '설정',
      description: '시스템 설정',
      href: '/settings',
      icon: Settings,
      color: 'bg-gray-600'
    }
  ];

  return (
    <div className="p-6 space-y-8">
      {/* 사용자 정보 */}
      <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <CardTitle className="text-xl">{user.name}</CardTitle>
                <CardDescription>
                  {user.username} • {user.role}
                </CardDescription>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant={user.role === 'super_admin' ? 'default' : 'secondary'}>
                {user.role === 'super_admin' ? '슈퍼 관리자' : 
                 user.role === 'brand_manager' ? '브랜드 관리자' :
                 user.role === 'store_manager' ? '매장 관리자' :
                 user.role === 'employee' ? '직원' : '직원'}
              </Badge>
              {user.role === 'super_admin' && (
                <Badge variant="destructive" className="bg-purple-600">
                  <Crown className="w-3 h-3 mr-1" />
                  최고권한
                </Badge>
              )}
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* 대시보드 선택 */}
      <div>
        <h2 className="text-2xl font-bold mb-4">대시보드 선택</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {navigationItems.map((item) => {
            // const hasPermission = permissions[item.requiredPermission as keyof typeof permissions];
            const hasPermission = true; // 임시로 모든 권한 허용
            const Icon = item.icon;
            
            return (
              <Card 
                key={item.href}
                className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
                  hasPermission ? 'hover:scale-105' : 'opacity-50 cursor-not-allowed'
                }`}
                onClick={() => hasPermission && router.push(item.href)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center space-x-3">
                    <div className={`w-10 h-10 ${item.color} rounded-lg flex items-center justify-center`}>
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{item.title}</CardTitle>
                      <CardDescription className="text-sm">
                        {item.description}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <Badge variant={hasPermission ? 'default' : 'secondary'}>
                      {hasPermission ? '접근 가능' : '접근 불가'}
                    </Badge>
                    {hasPermission && (
                      <Button size="sm" variant="outline">
                        접속하기
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* 기능 메뉴 */}
      <div>
        <h2 className="text-2xl font-bold mb-4">기능 메뉴</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {featureItems.map((item) => {
            const Icon = item.icon;
            
            return (
              <Card 
                key={item.href}
                className="cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-105"
                onClick={() => router.push(item.href)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center space-x-3">
                    <div className={`w-10 h-10 ${item.color} rounded-lg flex items-center justify-center`}>
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{item.title}</CardTitle>
                      <CardDescription className="text-sm">
                        {item.description}
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

      {/* 권한 정보 */}
      <Card className="bg-gray-50">
        <CardHeader>
          <CardTitle className="text-lg">현재 권한 정보</CardTitle>
        </CardHeader>
        <CardContent>
          {/* 권한 정보 임시 비활성화 */}
          <div className="text-sm text-gray-500">권한 정보를 불러올 수 없습니다.</div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PermissionNav; 