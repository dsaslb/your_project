'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Crown, 
  Building2, 
  Users, 
  BarChart3, 
  Settings, 
  Bell,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  Activity,
  Shield,
  DollarSign
} from 'lucide-react';
import useUserStore from '@/store/useUserStore';
import { useRouter } from 'next/navigation';

export default function SuperAdminDashboard() {
  const { user, permissions } = useUserStore();
  const router = useRouter();

  // 권한 확인
  if (!user || !permissions.canAccessSuperAdmin) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="text-red-600">접근 권한 없음</CardTitle>
            <CardDescription>
              슈퍼 관리자 권한이 필요합니다.
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

  // 더미 데이터 (실제로는 API에서 가져올 데이터)
  const stats = {
    totalUsers: 156,
    totalBranches: 8,
    activeSessions: 23,
    systemHealth: "정상",
    recentActivities: [
      { id: 1, action: "새 사용자 등록", user: "김철수", time: "2분 전" },
      { id: 2, action: "매장 정보 업데이트", user: "홍대점", time: "5분 전" },
      { id: 3, action: "시스템 백업 완료", user: "시스템", time: "10분 전" },
      { id: 4, action: "권한 변경", user: "이영희", time: "15분 전" },
    ],
    systemAlerts: [
      { id: 1, type: "warning", message: "매장 3개에서 백업 필요", time: "1시간 전" },
      { id: 2, type: "info", message: "새로운 업데이트 사용 가능", time: "2시간 전" },
    ]
  };

  const quickActions = [
    {
      title: '매장 관리',
      description: '매장별 설정 및 관리',
      icon: Building2,
      href: '/brand-dashboard',
      color: 'bg-blue-500'
    },
    {
      title: '직원 승인',
      description: '신규 직원 승인 처리',
      icon: Users,
      href: '/staff/approval',
      color: 'bg-green-500'
    },
    {
      title: '시스템 설정',
      description: '전체 시스템 설정',
      icon: Settings,
      href: '/settings',
      color: 'bg-purple-500'
    },
    {
      title: '통계 분석',
      description: '전체 매장 통계',
      icon: BarChart3,
      href: '/analytics',
      color: 'bg-orange-500'
    }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            슈퍼 관리자 대시보드
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            전체 시스템 현황 및 관리
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="flex items-center space-x-1">
            <Crown className="h-4 w-4" />
            <span>슈퍼 관리자</span>
          </Badge>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 사용자</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalUsers}</div>
            <p className="text-xs text-muted-foreground">
              +12% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 매장</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalBranches}</div>
            <p className="text-xs text-muted-foreground">
              +2 new this month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">활성 세션</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeSessions}</div>
            <p className="text-xs text-muted-foreground">
              현재 접속 중
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">시스템 상태</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.systemHealth}</div>
            <p className="text-xs text-muted-foreground">
              모든 시스템 정상
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 최근 활동 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="h-5 w-5" />
              <span>최근 활동</span>
            </CardTitle>
            <CardDescription>
              시스템에서 발생한 최근 활동들
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <p className="font-medium text-sm">{activity.action}</p>
                    <p className="text-xs text-muted-foreground">{activity.user}</p>
                  </div>
                  <span className="text-xs text-muted-foreground">{activity.time}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 시스템 알림 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5" />
              <span>시스템 알림</span>
            </CardTitle>
            <CardDescription>
              주의가 필요한 시스템 알림들
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.systemAlerts.map((alert) => (
                <div key={alert.id} className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                  <div>
                    <p className="font-medium text-sm">{alert.message}</p>
                    <p className="text-xs text-muted-foreground">{alert.time}</p>
                  </div>
                  <Badge variant={alert.type === "warning" ? "destructive" : "secondary"}>
                    {alert.type === "warning" ? "경고" : "정보"}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 빠른 액션 */}
      <Card>
        <CardHeader>
          <CardTitle>빠른 액션</CardTitle>
          <CardDescription>
            자주 사용하는 관리 기능들
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-20 flex flex-col space-y-2">
              <Users className="h-6 w-6" />
              <span className="text-sm">사용자 관리</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col space-y-2">
              <Building2 className="h-6 w-6" />
              <span className="text-sm">매장 관리</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col space-y-2">
              <BarChart3 className="h-6 w-6" />
              <span className="text-sm">통계 보기</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col space-y-2">
              <Shield className="h-6 w-6" />
              <span className="text-sm">시스템 모니터링</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 