'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Users, 
  TrendingUp, 
  Clock, 
  DollarSign, 
  ShoppingCart, 
  Building2,
  Activity,
  Calendar
} from 'lucide-react';

export default function DashboardPage() {
  const stats = [
    {
      title: "총 매장 수",
      value: "24",
      change: "+2",
      icon: Building2,
      color: "text-blue-600"
    },
    {
      title: "총 직원 수",
      value: "156",
      change: "+12",
      icon: Users,
      color: "text-green-600"
    },
    {
      title: "오늘 매출",
      value: "₩2,450,000",
      change: "+15%",
      icon: DollarSign,
      color: "text-purple-600"
    },
    {
      title: "주문 수",
      value: "342",
      change: "+8%",
      icon: ShoppingCart,
      color: "text-orange-600"
    }
  ];

  const recentActivities = [
    { id: 1, action: "새 주문 접수", location: "강남점", time: "2분 전" },
    { id: 2, action: "재고 부족 알림", location: "홍대점", time: "5분 전" },
    { id: 3, action: "직원 출근 체크", location: "신촌점", time: "10분 전" },
    { id: 4, action: "매출 보고서 생성", location: "전체", time: "15분 전" }
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* 헤더 */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                대시보드
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                레스토랑 관리 시스템 현황
              </p>
            </div>
            <div className="flex space-x-3">
              <Button variant="outline">
                <Calendar className="h-4 w-4 mr-2" />
                오늘
              </Button>
              <Button>
                <Activity className="h-4 w-4 mr-2" />
                실시간 모니터링
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                        {stat.title}
                      </p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        {stat.value}
                      </p>
                      <p className="text-sm text-green-600 dark:text-green-400">
                        {stat.change}
                      </p>
                    </div>
                    <div className={`p-3 rounded-lg bg-gray-100 dark:bg-gray-700`}>
                      <Icon className={`h-6 w-6 ${stat.color}`} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* 차트 및 활동 섹션 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 매출 차트 */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>매출 추이</CardTitle>
                <CardDescription>최근 7일간의 매출 현황</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="text-center">
                    <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500 dark:text-gray-400">차트가 여기에 표시됩니다</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 최근 활동 */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>최근 활동</CardTitle>
                <CardDescription>실시간 시스템 활동</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentActivities.map((activity) => (
                    <div key={activity.id} className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {activity.action}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {activity.location} • {activity.time}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
                <Button variant="outline" className="w-full mt-4">
                  모든 활동 보기
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* 빠른 액션 */}
        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle>빠른 액션</CardTitle>
              <CardDescription>자주 사용하는 기능에 빠르게 접근</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Button variant="outline" className="h-20 flex-col">
                  <Users className="h-6 w-6 mb-2" />
                  <span className="text-sm">직원 관리</span>
                </Button>
                <Button variant="outline" className="h-20 flex-col">
                  <ShoppingCart className="h-6 w-6 mb-2" />
                  <span className="text-sm">주문 관리</span>
                </Button>
                <Button variant="outline" className="h-20 flex-col">
                  <Building2 className="h-6 w-6 mb-2" />
                  <span className="text-sm">매장 관리</span>
                </Button>
                <Button variant="outline" className="h-20 flex-col">
                  <Clock className="h-6 w-6 mb-2" />
                  <span className="text-sm">스케줄</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 