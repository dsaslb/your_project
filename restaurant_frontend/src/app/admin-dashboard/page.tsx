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
  DollarSign,
  Zap,
  Target,
  Globe,
  Database,
  Cpu
} from 'lucide-react';
import useUserStore from '@/store/useUserStore';
import { useRouter } from 'next/navigation';

export default function SuperAdminDashboard() {
  const { user, isSuperAdmin } = useUserStore();
  const router = useRouter();

  // 권한 확인
  if (!user || !isSuperAdmin()) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 flex items-center justify-center p-4">
        <Card className="w-96 shadow-2xl border-0 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm">
          <CardHeader className="text-center">
            <div className="mx-auto w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mb-4">
              <Shield className="h-6 w-6 text-red-600 dark:text-red-400" />
            </div>
            <CardTitle className="text-red-600 dark:text-red-400">접근 권한 없음</CardTitle>
            <CardDescription className="text-slate-600 dark:text-slate-400">
              슈퍼 관리자 권한이 필요합니다.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => router.push('/dashboard')}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg"
            >
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
    revenue: "₩12,450,000",
    recentActivities: [
      { id: 1, action: "새 사용자 등록", user: "김철수", time: "2분 전", type: "success" },
      { id: 2, action: "매장 정보 업데이트", user: "홍대점", time: "5분 전", type: "info" },
      { id: 3, action: "시스템 백업 완료", user: "시스템", time: "10분 전", type: "success" },
      { id: 4, action: "권한 변경", user: "이영희", time: "15분 전", type: "warning" },
    ],
    systemAlerts: [
      { id: 1, type: "warning", message: "매장 3개에서 백업 필요", time: "1시간 전", priority: "high" },
      { id: 2, type: "info", message: "새로운 업데이트 사용 가능", time: "2시간 전", priority: "low" },
    ]
  };

  const quickActions = [
    {
      title: '매장 관리',
      description: '매장별 설정 및 관리',
      icon: Building2,
      href: '/brand-dashboard',
      gradient: 'from-blue-500 to-cyan-500',
      bgGradient: 'bg-gradient-to-br from-blue-500/10 to-cyan-500/10'
    },
    {
      title: '직원 승인',
      description: '신규 직원 승인 처리',
      icon: Users,
      href: '/staff/approval',
      gradient: 'from-green-500 to-emerald-500',
      bgGradient: 'bg-gradient-to-br from-green-500/10 to-emerald-500/10'
    },
    {
      title: '시스템 설정',
      description: '전체 시스템 설정',
      icon: Settings,
      href: '/settings',
      gradient: 'from-purple-500 to-pink-500',
      bgGradient: 'bg-gradient-to-br from-purple-500/10 to-pink-500/10'
    },
    {
      title: '통계 분석',
      description: '전체 매장 통계',
      icon: BarChart3,
      href: '/analytics',
      gradient: 'from-orange-500 to-red-500',
      bgGradient: 'bg-gradient-to-br from-orange-500/10 to-red-500/10'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      <div className="p-6 space-y-8">
        {/* 헤더 */}
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-slate-900 to-slate-600 dark:from-white dark:to-slate-300 bg-clip-text text-transparent">
              슈퍼 관리자 대시보드
            </h1>
            <p className="text-slate-600 dark:text-slate-400 text-lg">
              전체 시스템 현황 및 관리
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white border-0 shadow-lg">
              <Crown className="h-4 w-4 mr-1" />
              슈퍼 관리자
            </Badge>
            <Button size="sm" variant="outline" className="border-slate-300 dark:border-slate-600">
              <Bell className="h-4 w-4 mr-2" />
              알림
            </Button>
          </div>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="group hover:shadow-2xl transition-all duration-300 border-0 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-700 dark:text-slate-300">전체 사용자</CardTitle>
              <div className="p-2 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-lg group-hover:scale-110 transition-transform">
                <Users className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900 dark:text-white">{stats.totalUsers}</div>
              <p className="text-xs text-slate-600 dark:text-slate-400 flex items-center mt-1">
                <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
                +12% from last month
              </p>
            </CardContent>
          </Card>

          <Card className="group hover:shadow-2xl transition-all duration-300 border-0 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-700 dark:text-slate-300">전체 매장</CardTitle>
              <div className="p-2 bg-gradient-to-br from-green-500/10 to-emerald-500/10 rounded-lg group-hover:scale-110 transition-transform">
                <Building2 className="h-4 w-4 text-green-600 dark:text-green-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900 dark:text-white">{stats.totalBranches}</div>
              <p className="text-xs text-slate-600 dark:text-slate-400 flex items-center mt-1">
                <Target className="h-3 w-3 mr-1 text-blue-500" />
                +2 new this month
              </p>
            </CardContent>
          </Card>

          <Card className="group hover:shadow-2xl transition-all duration-300 border-0 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-700 dark:text-slate-300">활성 세션</CardTitle>
              <div className="p-2 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-lg group-hover:scale-110 transition-transform">
                <Activity className="h-4 w-4 text-purple-600 dark:text-purple-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900 dark:text-white">{stats.activeSessions}</div>
              <p className="text-xs text-slate-600 dark:text-slate-400 flex items-center mt-1">
                <Zap className="h-3 w-3 mr-1 text-yellow-500" />
                현재 접속 중
              </p>
            </CardContent>
          </Card>

          <Card className="group hover:shadow-2xl transition-all duration-300 border-0 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-700 dark:text-slate-300">시스템 상태</CardTitle>
              <div className="p-2 bg-gradient-to-br from-emerald-500/10 to-teal-500/10 rounded-lg group-hover:scale-110 transition-transform">
                <Shield className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">{stats.systemHealth}</div>
              <p className="text-xs text-slate-600 dark:text-slate-400 flex items-center mt-1">
                <CheckCircle className="h-3 w-3 mr-1 text-emerald-500" />
                모든 시스템 정상
              </p>
            </CardContent>
          </Card>
        </div>

        {/* 메인 콘텐츠 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 최근 활동 */}
          <Card className="border-0 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm shadow-xl">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-slate-900 dark:text-white">
                <div className="p-2 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-lg">
                  <Clock className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
                <span>최근 활동</span>
              </CardTitle>
              <CardDescription className="text-slate-600 dark:text-slate-400">
                시스템에서 발생한 최근 활동들
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stats.recentActivities.map((activity) => (
                  <div key={activity.id} className="group flex items-center justify-between p-4 bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-700/50 dark:to-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700 hover:shadow-md transition-all duration-200">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-full ${
                        activity.type === 'success' ? 'bg-green-100 dark:bg-green-900/30' :
                        activity.type === 'warning' ? 'bg-yellow-100 dark:bg-yellow-900/30' :
                        'bg-blue-100 dark:bg-blue-900/30'
                      }`}>
                        {activity.type === 'success' ? (
                          <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                        ) : activity.type === 'warning' ? (
                          <AlertTriangle className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
                        ) : (
                          <Activity className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-sm text-slate-900 dark:text-white">{activity.action}</p>
                        <p className="text-xs text-slate-600 dark:text-slate-400">{activity.user}</p>
                      </div>
                    </div>
                    <span className="text-xs text-slate-500 dark:text-slate-400 group-hover:text-slate-700 dark:group-hover:text-slate-300 transition-colors">
                      {activity.time}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 시스템 알림 */}
          <Card className="border-0 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm shadow-xl">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-slate-900 dark:text-white">
                <div className="p-2 bg-gradient-to-br from-orange-500/10 to-red-500/10 rounded-lg">
                  <AlertTriangle className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                </div>
                <span>시스템 알림</span>
              </CardTitle>
              <CardDescription className="text-slate-600 dark:text-slate-400">
                주의가 필요한 시스템 알림들
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stats.systemAlerts.map((alert) => (
                  <div key={alert.id} className="group flex items-center justify-between p-4 bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 rounded-xl border border-orange-200 dark:border-orange-800 hover:shadow-md transition-all duration-200">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-full">
                        <AlertTriangle className="h-4 w-4 text-orange-600 dark:text-orange-400" />
                      </div>
                      <div>
                        <p className="font-medium text-sm text-slate-900 dark:text-white">{alert.message}</p>
                        <p className="text-xs text-slate-600 dark:text-slate-400">{alert.time}</p>
                      </div>
                    </div>
                    <Badge className={`${
                      alert.priority === 'high' 
                        ? 'bg-gradient-to-r from-red-500 to-pink-500 text-white' 
                        : 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white'
                    } border-0 shadow-sm`}>
                      {alert.priority === 'high' ? '높음' : '낮음'}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 빠른 액션 */}
        <Card className="border-0 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm shadow-xl">
          <CardHeader>
            <CardTitle className="text-slate-900 dark:text-white">빠른 액션</CardTitle>
            <CardDescription className="text-slate-600 dark:text-slate-400">
              자주 사용하는 관리 기능들
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {quickActions.map((action, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className={`h-24 flex flex-col space-y-3 border-0 bg-white/60 dark:bg-slate-700/60 backdrop-blur-sm hover:shadow-xl transition-all duration-300 group ${action.bgGradient}`}
                  onClick={() => router.push(action.href)}
                >
                  <div className={`p-3 bg-gradient-to-br ${action.gradient} rounded-full group-hover:scale-110 transition-transform`}>
                    <action.icon className="h-6 w-6 text-white" />
                  </div>
                  <span className="text-sm font-medium text-slate-900 dark:text-white">{action.title}</span>
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 추가 통계 섹션 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-0 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full">
                  <DollarSign className="h-6 w-6 text-white" />
                </div>
                <div>
                  <p className="text-sm text-slate-600 dark:text-slate-400">총 매출</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">{stats.revenue}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 bg-gradient-to-br from-green-500/10 to-emerald-500/10 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full">
                  <Globe className="h-6 w-6 text-white" />
                </div>
                <div>
                  <p className="text-sm text-slate-600 dark:text-slate-400">온라인 상태</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">8/8</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 bg-gradient-to-br from-purple-500/10 to-pink-500/10 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full">
                  <Database className="h-6 w-6 text-white" />
                </div>
                <div>
                  <p className="text-sm text-slate-600 dark:text-slate-400">데이터베이스</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">정상</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 