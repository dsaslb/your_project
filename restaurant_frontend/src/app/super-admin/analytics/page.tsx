'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';
import { SuperAdminOnly } from '@/components/auth/PermissionGuard';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Building2, 
  Activity, 
  AlertTriangle,
  CheckCircle,
  Clock,
  PieChart,
  LineChart
} from 'lucide-react';

// 분석 데이터 타입
interface BrandOverviewData {
  overview: {
    total_branches: number;
    total_users: number;
    total_orders: number;
    total_schedules: number;
  };
  role_distribution: Array<{
    role: string;
    total: number;
    active: number;
    inactive: number;
  }>;
  branch_distribution: Array<{
    branch_id: number;
    total_users: number;
    active_users: number;
    managers: number;
    employees: number;
  }>;
  recent_activity: {
    orders_30_days: number;
    schedules_30_days: number;
    new_users_30_days: number;
  };
}

interface BranchPerformanceData {
  branch_info?: {
    id: number;
    name: string;
    address: string;
  };
  user_performance?: {
    total_users: number;
    active_users: number;
    managers: number;
    employees: number;
    recent_logins: number;
    activity_rate: number;
  };
  order_performance?: {
    total_orders: number;
    completed_orders: number;
    pending_orders: number;
    completion_rate: number;
    avg_order_amount: number;
  };
  schedule_performance?: {
    total_schedules: number;
    completed_schedules: number;
    pending_schedules: number;
    completion_rate: number;
  };
  branch_comparison?: Array<{
    branch_id: number;
    branch_name: string;
    total_users: number;
    active_users: number;
    total_orders: number;
    completed_orders: number;
    avg_order_amount: number;
    user_activity_rate: number;
    order_completion_rate: number;
  }>;
}

interface UserActivityData {
  daily_logins: Array<{
    date: string;
    count: number;
  }>;
  role_activity: Array<{
    role: string;
    total_users: number;
    active_7_days: number;
    active_30_days: number;
    activity_rate_7_days: number;
    activity_rate_30_days: number;
    avg_days_to_first_login: number;
  }>;
  inactive_users: Array<{
    id: number;
    username: string;
    name: string;
    role: string;
    branch_id?: number;
    last_login?: string;
  }>;
}

interface SystemHealthData {
  table_stats: Array<{
    table_name: string;
    record_count: number;
  }>;
  recent_errors: Array<{
    action: string;
    details: string;
    created_at: string;
  }>;
  monthly_signups: Array<{
    month: string;
    count: number;
  }>;
  system_status: {
    database_health: string;
    api_response_time: string;
    active_connections: number;
    last_backup: string;
  };
}

// 분석 데이터 훅들
const useBrandOverview = () => {
  return useQuery({
    queryKey: ['analytics', 'brand-overview'],
    queryFn: async () => {
      const response = await apiClient.get<BrandOverviewData>('/api/analytics/brand-overview');
      if (!response.success) {
        throw new Error(response.error || '브랜드 현황을 불러올 수 없습니다.');
      }
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5분
  });
};

const useBranchPerformance = (branchId?: number) => {
  return useQuery({
    queryKey: ['analytics', 'branch-performance', branchId],
    queryFn: async () => {
      const params = branchId ? { branch_id: branchId } : {};
      const response = await apiClient.get<BranchPerformanceData>('/api/analytics/branch-performance', params);
      if (!response.success) {
        throw new Error(response.error || '매장 성과를 불러올 수 없습니다.');
      }
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
};

const useUserActivity = () => {
  return useQuery({
    queryKey: ['analytics', 'user-activity'],
    queryFn: async () => {
      const response = await apiClient.get<UserActivityData>('/api/analytics/user-activity');
      if (!response.success) {
        throw new Error(response.error || '사용자 활동을 불러올 수 없습니다.');
      }
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
};

const useSystemHealth = () => {
  return useQuery({
    queryKey: ['analytics', 'system-health'],
    queryFn: async () => {
      const response = await apiClient.get<SystemHealthData>('/api/analytics/system-health');
      if (!response.success) {
        throw new Error(response.error || '시스템 상태를 불러올 수 없습니다.');
      }
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2분
  });
};

// 통계 카드 컴포넌트
const StatCard = ({ 
  title, 
  value, 
  description, 
  icon: Icon, 
  trend,
  color = "default"
}: {
  title: string;
  value: string | number;
  description?: string;
  icon: React.ComponentType<{ className?: string }>;
  trend?: 'up' | 'down' | 'neutral';
  color?: 'default' | 'success' | 'warning' | 'danger';
}) => {
  const colorClasses = {
    default: 'text-muted-foreground',
    success: 'text-green-500',
    warning: 'text-yellow-500',
    danger: 'text-red-500',
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className={`h-4 w-4 ${colorClasses[color]}`} />
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
};

// 분석 대시보드 메인 컴포넌트
const AnalyticsDashboard = () => {
  const [selectedBranch, setSelectedBranch] = useState<number | undefined>();
  
  const brandOverview = useBrandOverview();
  const branchPerformance = useBranchPerformance(selectedBranch);
  const userActivity = useUserActivity();
  const systemHealth = useSystemHealth();

  const isLoading = brandOverview.isLoading || branchPerformance.isLoading || 
                   userActivity.isLoading || systemHealth.isLoading;

  const hasError = brandOverview.error || branchPerformance.error || 
                  userActivity.error || systemHealth.error;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">분석 데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 text-red-500 mx-auto mb-4" />
          <p className="text-red-500 mb-4">분석 데이터를 불러올 수 없습니다.</p>
          <Button onClick={() => window.location.reload()}>다시 시도</Button>
        </div>
      </div>
    );
  }

  return (
    <SuperAdminOnly>
      <div className="space-y-6">
        {/* 헤더 */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">데이터 분석</h1>
            <p className="text-muted-foreground">
              브랜드 및 매장별 종합 분석 및 인사이트
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="flex items-center gap-1">
              <BarChart3 className="h-3 w-3" />
              실시간 분석
            </Badge>
            <Button variant="outline" size="sm">
              <LineChart className="h-4 w-4 mr-2" />
              리포트 다운로드
            </Button>
          </div>
        </div>

        {/* 브랜드 개요 통계 */}
        {brandOverview.data && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="전체 매장"
              value={brandOverview.data.overview.total_branches}
              description="운영 중인 매장 수"
              icon={Building2}
              trend="neutral"
            />
            <StatCard
              title="전체 사용자"
              value={brandOverview.data.overview.total_users}
              description="등록된 모든 사용자"
              icon={Users}
              trend="up"
            />
            <StatCard
              title="총 주문 수"
              value={brandOverview.data.overview.total_orders}
              description="전체 주문 건수"
              icon={Activity}
              trend="up"
            />
            <StatCard
              title="총 스케줄"
              value={brandOverview.data.overview.total_schedules}
              description="전체 스케줄 수"
              icon={Clock}
              trend="neutral"
            />
          </div>
        )}

        {/* 탭 컨텐츠 */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">브랜드 개요</TabsTrigger>
            <TabsTrigger value="performance">매장 성과</TabsTrigger>
            <TabsTrigger value="activity">사용자 활동</TabsTrigger>
            <TabsTrigger value="system">시스템 상태</TabsTrigger>
          </TabsList>

          {/* 브랜드 개요 탭 */}
          <TabsContent value="overview" className="space-y-4">
            {brandOverview.data && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* 역할별 분포 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <PieChart className="h-5 w-5" />
                      역할별 사용자 분포
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {brandOverview.data.role_distribution.map((role) => (
                        <div key={role.role} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">
                              {role.role === 'super_admin' && '슈퍼 관리자'}
                              {role.role === 'brand_manager' && '브랜드 관리자'}
                              {role.role === 'store_manager' && '매장 관리자'}
                              {role.role === 'employee' && '직원'}
                            </Badge>
                          </div>
                          <div className="text-right">
                            <div className="font-medium">{role.total}명</div>
                            <div className="text-xs text-muted-foreground">
                              활성: {role.active}명
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* 최근 활동 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="h-5 w-5" />
                      최근 30일 활동
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span>신규 주문</span>
                        <Badge variant="outline">{brandOverview.data.recent_activity.orders_30_days}건</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>신규 스케줄</span>
                        <Badge variant="outline">{brandOverview.data.recent_activity.schedules_30_days}건</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>신규 사용자</span>
                        <Badge variant="outline">{brandOverview.data.recent_activity.new_users_30_days}명</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          {/* 매장 성과 탭 */}
          <TabsContent value="performance" className="space-y-4">
            <div className="flex items-center gap-4 mb-4">
              <Select value={selectedBranch?.toString()} onValueChange={(value) => setSelectedBranch(value ? parseInt(value) : undefined)}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="매장 선택" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">전체 매장 비교</SelectItem>
                  {/* 매장 목록은 실제 데이터에서 동적으로 생성 */}
                </SelectContent>
              </Select>
            </div>

            {branchPerformance.data && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {selectedBranch && branchPerformance.data.user_performance && (
                  <Card>
                    <CardHeader>
                      <CardTitle>사용자 성과</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span>총 사용자</span>
                          <span className="font-medium">{branchPerformance.data.user_performance.total_users}명</span>
                        </div>
                        <div className="flex justify-between">
                          <span>활성 사용자</span>
                          <span className="font-medium">{branchPerformance.data.user_performance.active_users}명</span>
                        </div>
                        <div className="flex justify-between">
                          <span>활동률</span>
                          <span className="font-medium">{branchPerformance.data.user_performance.activity_rate.toFixed(1)}%</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {selectedBranch && branchPerformance.data.order_performance && (
                  <Card>
                    <CardHeader>
                      <CardTitle>주문 성과</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span>총 주문</span>
                          <span className="font-medium">{branchPerformance.data.order_performance.total_orders}건</span>
                        </div>
                        <div className="flex justify-between">
                          <span>완료율</span>
                          <span className="font-medium">{branchPerformance.data.order_performance.completion_rate.toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span>평균 주문 금액</span>
                          <span className="font-medium">₩{branchPerformance.data.order_performance.avg_order_amount.toLocaleString()}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {!selectedBranch && branchPerformance.data.branch_comparison && (
                  <Card className="col-span-2">
                    <CardHeader>
                      <CardTitle>매장별 성과 비교</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {branchPerformance.data.branch_comparison.map((branch) => (
                          <div key={branch.branch_id} className="flex items-center justify-between p-3 border rounded-lg">
                            <div>
                              <div className="font-medium">{branch.branch_name}</div>
                              <div className="text-sm text-muted-foreground">
                                사용자: {branch.total_users}명 | 주문: {branch.total_orders}건
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-sm">
                                활동률: {branch.user_activity_rate.toFixed(1)}%
                              </div>
                              <div className="text-sm">
                                완료율: {branch.order_completion_rate.toFixed(1)}%
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </TabsContent>

          {/* 사용자 활동 탭 */}
          <TabsContent value="activity" className="space-y-4">
            {userActivity.data && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* 역할별 활동률 */}
                <Card>
                  <CardHeader>
                    <CardTitle>역할별 활동률</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {userActivity.data.role_activity.map((activity) => (
                        <div key={activity.role} className="flex items-center justify-between">
                          <div>
                            <div className="font-medium">
                              {activity.role === 'super_admin' && '슈퍼 관리자'}
                              {activity.role === 'brand_manager' && '브랜드 관리자'}
                              {activity.role === 'store_manager' && '매장 관리자'}
                              {activity.role === 'employee' && '직원'}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              총 {activity.total_users}명
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-medium">{activity.activity_rate_7_days.toFixed(1)}%</div>
                            <div className="text-xs text-muted-foreground">7일 활동률</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* 비활성 사용자 */}
                <Card>
                  <CardHeader>
                    <CardTitle>비활성 사용자 (30일 이상)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {userActivity.data.inactive_users.slice(0, 5).map((user) => (
                        <div key={user.id} className="flex items-center justify-between p-2 border rounded">
                          <div>
                            <div className="font-medium">{user.name}</div>
                            <div className="text-sm text-muted-foreground">@{user.username}</div>
                          </div>
                          <Badge variant="outline">
                            {user.role === 'super_admin' && '슈퍼 관리자'}
                            {user.role === 'brand_manager' && '브랜드 관리자'}
                            {user.role === 'store_manager' && '매장 관리자'}
                            {user.role === 'employee' && '직원'}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          {/* 시스템 상태 탭 */}
          <TabsContent value="system" className="space-y-4">
            {systemHealth.data && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* 시스템 상태 */}
                <Card>
                  <CardHeader>
                    <CardTitle>시스템 상태</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span>데이터베이스</span>
                        <Badge variant={systemHealth.data.system_status.database_health === 'healthy' ? 'default' : 'destructive'}>
                          {systemHealth.data.system_status.database_health === 'healthy' ? '정상' : '오류'}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>API 응답 시간</span>
                        <Badge variant="outline">{systemHealth.data.system_status.api_response_time}</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>활성 연결</span>
                        <Badge variant="outline">{systemHealth.data.system_status.active_connections}개</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>마지막 백업</span>
                        <span className="text-sm text-muted-foreground">{systemHealth.data.system_status.last_backup}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* 테이블 통계 */}
                <Card>
                  <CardHeader>
                    <CardTitle>데이터베이스 테이블</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {systemHealth.data.table_stats.map((table) => (
                        <div key={table.table_name} className="flex items-center justify-between">
                          <span className="capitalize">{table.table_name}</span>
                          <Badge variant="outline">{table.record_count.toLocaleString()}개</Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </SuperAdminOnly>
  );
};

export default AnalyticsDashboard; 