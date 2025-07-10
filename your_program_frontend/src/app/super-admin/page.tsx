'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';
import { SuperAdminOnly } from '@/components/auth/PermissionGuard';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Users, 
  Building2, 
  Activity, 
  Shield, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3,
  Settings
} from 'lucide-react';

// 슈퍼 관리자 대시보드 데이터 타입
interface SuperAdminDashboardData {
  stats: {
    total_users: number;
    total_branches: number;
    active_sessions: number;
  };
  recent_users: Array<{
    id: number;
    username: string;
    name: string;
    role: string;
    created_at: string;
  }>;
  system_logs: Array<{
    id: number;
    action: string;
    user_id: number;
    details: string;
    created_at: string;
  }>;
}

// 슈퍼 관리자 대시보드 훅
const useSuperAdminDashboard = () => {
  return useQuery({
    queryKey: ['super-admin', 'dashboard'],
    queryFn: async () => {
      const response = await apiClient.get<SuperAdminDashboardData>('/api/super-admin/dashboard');
      if (!response.success) {
        throw new Error(response.error || '대시보드 데이터를 불러올 수 없습니다.');
      }
      return response.data;
    },
    staleTime: 30 * 1000, // 30초
  });
};

// 통계 카드 컴포넌트
const StatCard = ({ 
  title, 
  value, 
  description, 
  icon: Icon, 
  trend 
}: {
  title: string;
  value: string | number;
  description?: string;
  icon: React.ComponentType<{ className?: string }>;
  trend?: 'up' | 'down' | 'neutral';
}) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
      <Icon className="h-4 w-4 text-muted-foreground" />
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">{value}</div>
      {description && (
        <p className="text-xs text-muted-foreground">{description}</p>
      )}
      {trend && (
        <div className="flex items-center text-xs">
          {trend === 'up' && <TrendingUp className="h-3 w-3 text-green-500 mr-1" />}
          {trend === 'down' && <TrendingUp className="h-3 w-3 text-red-500 mr-1 rotate-180" />}
          <span className={trend === 'up' ? 'text-green-500' : trend === 'down' ? 'text-red-500' : 'text-muted-foreground'}>
            {trend === 'up' ? '증가' : trend === 'down' ? '감소' : '유지'}
          </span>
        </div>
      )}
    </CardContent>
  </Card>
);

// 최근 사용자 목록 컴포넌트
const RecentUsersList = ({ users }: { users: SuperAdminDashboardData['recent_users'] }) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Users className="h-5 w-5" />
        최근 가입자
      </CardTitle>
      <CardDescription>최근 5명의 신규 사용자</CardDescription>
    </CardHeader>
    <CardContent>
      <div className="space-y-3">
        {users.map((user) => (
          <div key={user.id} className="flex items-center justify-between p-3 border rounded-lg">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                <Users className="h-4 w-4 text-primary" />
              </div>
              <div>
                <p className="font-medium">{user.name}</p>
                <p className="text-sm text-muted-foreground">@{user.username}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">{user.role}</Badge>
              <span className="text-xs text-muted-foreground">
                {new Date(user.created_at).toLocaleDateString('ko-KR')}
              </span>
            </div>
          </div>
        ))}
      </div>
    </CardContent>
  </Card>
);

// 시스템 로그 컴포넌트
const SystemLogsList = ({ logs }: { logs: SuperAdminDashboardData['system_logs'] }) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Activity className="h-5 w-5" />
        시스템 로그
      </CardTitle>
      <CardDescription>최근 시스템 활동 기록</CardDescription>
    </CardHeader>
    <CardContent>
      <div className="space-y-3">
        {logs.map((log) => (
          <div key={log.id} className="flex items-start gap-3 p-3 border rounded-lg">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
            <div className="flex-1">
              <p className="font-medium text-sm">{log.action}</p>
              <p className="text-xs text-muted-foreground">{log.details}</p>
              <p className="text-xs text-muted-foreground mt-1">
                {new Date(log.created_at).toLocaleString('ko-KR')}
              </p>
            </div>
          </div>
        ))}
      </div>
    </CardContent>
  </Card>
);

// 슈퍼 관리자 대시보드 메인 컴포넌트
const SuperAdminDashboard = () => {
  const { data, isLoading, error, refetch } = useSuperAdminDashboard();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 text-red-500 mx-auto mb-4" />
          <p className="text-red-500 mb-4">데이터를 불러올 수 없습니다.</p>
          <Button onClick={() => refetch()}>다시 시도</Button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <SuperAdminOnly>
      <div className="space-y-6">
        {/* 헤더 */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">슈퍼 관리자 대시보드</h1>
            <p className="text-muted-foreground">
              전체 시스템 현황 및 최근 활동을 한눈에 확인하세요.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="flex items-center gap-1">
              <Shield className="h-3 w-3" />
              슈퍼 관리자
            </Badge>
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              시스템 설정
            </Button>
          </div>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard
            title="전체 사용자"
            value={data?.stats?.total_users ?? 0}
            description="등록된 모든 사용자"
            icon={Users}
            trend="up"
          />
          <StatCard
            title="전체 매장"
            value={data?.stats?.total_branches ?? 0}
            description="등록된 매장 수"
            icon={Building2}
            trend="neutral"
          />
          <StatCard
            title="활성 세션"
            value={data?.stats?.active_sessions ?? 0}
            description="현재 로그인 중인 세션"
            icon={Activity}
            trend="up"
          />
        </div>

        {/* 최근 사용자 */}
        <RecentUsersList users={data?.recent_users ?? []} />
        {/* 시스템 로그 */}
        <SystemLogsList logs={data?.system_logs ?? []} />
      </div>
    </SuperAdminOnly>
  );
};

export default SuperAdminDashboard; 