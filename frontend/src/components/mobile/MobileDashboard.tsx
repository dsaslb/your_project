"use client";
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  Users, 
  ShoppingCart, 
  Calendar,
  Clock,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { useMobile, useMobileOptimization } from '@/hooks/useMobile';
import { cn } from '@/lib/utils';

interface DashboardStats {
  totalOrders: number;
  activeStaff: number;
  pendingTasks: number;
  todayRevenue: number;
  recentAlerts: Array<{
    id: string;
    type: 'success' | 'warning' | 'error';
    message: string;
    time: string;
  }>;
}

const MobileDashboard: React.FC = () => {
  const { isMobile, isStandalone } = useMobile();
  const { mobileSpacing, mobileGridCols, pwaPadding } = useMobileOptimization();
  const [stats, setStats] = useState<DashboardStats>({
    totalOrders: 0,
    activeStaff: 0,
    pendingTasks: 0,
    todayRevenue: 0,
    recentAlerts: [],
  });

  // 더미 데이터 로드
  useEffect(() => {
    const loadStats = async () => {
      // 실제 API 호출로 대체 가능
      setStats({
        totalOrders: 156,
        activeStaff: 8,
        pendingTasks: 12,
        todayRevenue: 1250000,
        recentAlerts: [
          {
            id: '1',
            type: 'success',
            message: '새 주문이 접수되었습니다',
            time: '2분 전',
          },
          {
            id: '2',
            type: 'warning',
            message: '재고 부족 알림',
            time: '5분 전',
          },
          {
            id: '3',
            type: 'error',
            message: '시스템 오류 발생',
            time: '10분 전',
          },
        ],
      });
    };

    loadStats();
  }, []);

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getAlertColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className={cn("min-h-screen bg-gray-50", pwaPadding)}>
      {/* 헤더 */}
      <div className="bg-white shadow-sm border-b border-gray-200 px-4 py-3">
        <h1 className="text-xl font-bold text-gray-900">대시보드</h1>
        <p className="text-sm text-gray-500 mt-1">
          {new Date().toLocaleDateString('ko-KR', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            weekday: 'long'
          })}
        </p>
      </div>

      <div className={cn("p-4", mobileSpacing)}>
        {/* 통계 카드 */}
        <div className={cn("grid gap-4", mobileGridCols)}>
          <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center space-x-2">
                <ShoppingCart className="w-4 h-4" />
                <span>총 주문</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalOrders.toLocaleString()}</div>
              <div className="text-xs opacity-90 mt-1">오늘 처리된 주문</div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center space-x-2">
                <Users className="w-4 h-4" />
                <span>활성 직원</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.activeStaff}</div>
              <div className="text-xs opacity-90 mt-1">현재 근무 중</div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center space-x-2">
                <Clock className="w-4 h-4" />
                <span>대기 작업</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.pendingTasks}</div>
              <div className="text-xs opacity-90 mt-1">처리 대기 중</div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center space-x-2">
                <TrendingUp className="w-4 h-4" />
                <span>오늘 매출</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ₩{(stats.todayRevenue / 10000).toFixed(0)}만
              </div>
              <div className="text-xs opacity-90 mt-1">오늘 총 매출</div>
            </CardContent>
          </Card>
        </div>

        {/* 빠른 액션 버튼 */}
        <div className="mt-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">빠른 액션</h2>
          <div className="grid grid-cols-2 gap-3">
            <Button 
              variant="outline" 
              className="h-16 flex flex-col items-center justify-center space-y-1"
            >
              <ShoppingCart className="w-6 h-6" />
              <span className="text-sm">새 주문</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-16 flex flex-col items-center justify-center space-y-1"
            >
              <Users className="w-6 h-6" />
              <span className="text-sm">직원 관리</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-16 flex flex-col items-center justify-center space-y-1"
            >
              <Calendar className="w-6 h-6" />
              <span className="text-sm">출근 관리</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-16 flex flex-col items-center justify-center space-y-1"
            >
              <AlertCircle className="w-6 h-6" />
              <span className="text-sm">알림 확인</span>
            </Button>
          </div>
        </div>

        {/* 최근 알림 */}
        <div className="mt-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">최근 알림</h2>
          <div className="space-y-3">
            {stats.recentAlerts.map((alert) => (
              <div
                key={alert.id}
                className={cn(
                  "p-3 rounded-lg border",
                  getAlertColor(alert.type)
                )}
              >
                <div className="flex items-start space-x-3">
                  {getAlertIcon(alert.type)}
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {alert.message}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {alert.time}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* PWA 설치 안내 */}
        {!isStandalone && (
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm">📱</span>
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-medium text-blue-900">
                  앱으로 설치하기
                </h3>
                <p className="text-xs text-blue-700 mt-1">
                  홈 화면에 추가하여 더 빠르게 접근하세요
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MobileDashboard; 