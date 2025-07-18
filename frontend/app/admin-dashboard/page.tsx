'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
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
import FeedbackSystem from '../../../core/frontend/FeedbackSystem';
import { Tooltip } from '@/components/ui/tooltip';
import { toast } from 'react-hot-toast';
import { Bar } from 'react-chartjs-2'; // 차트 예시
import Link from 'next/link';
import AutomationHistory from './automation-history';

// 브랜드 타입 정의 (예시)
type Brand = {
  id: string;
  name: string;
};

function AutomationStatusBanner() {
  // 실제 자동화 점검/최신화/보안 상태를 API/스크립트 결과와 연동하는 샘플
  const [status, setStatus] = useState({
    upToDate: true,
    outdatedFiles: 0,
    securityPatch: false,
    lastCheck: '2024-06-01 09:00',
    details: [],
  });

  useEffect(() => {
    // 실제로는 백엔드 API(예: /api/automation-status)에서 점검 결과를 받아옴
    fetch('/api/automation-status')
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data) setStatus(data);
        // 경고/오류 상태일 때 Toast 알림 자동 표시
        if (data && (!data.upToDate || data.securityPatch)) {
          toast.error('자동화 점검 경고: 미점검/미최신화 파일 또는 보안 패치 필요!');
        }
      })
      .catch(() => {});
  }, []);

  return (
    <div
      className={`mb-4 p-4 rounded flex items-center gap-4 ${status.upToDate ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}
      role="status"
      aria-live="polite"
      aria-label="자동화 상태 및 최신화 점검 결과"
    >
      <span className="text-2xl">
        {status.upToDate ? '✅' : '⚠️'}
      </span>
      <div>
        <div className="font-bold">
          {status.upToDate ? '모든 시스템 최신화 및 자동화 정상' : `미점검/미최신화 파일 ${status.outdatedFiles}개, 보안 패치 필요`}
        </div>
        <div className="text-xs text-gray-500">최종 점검: {status.lastCheck}</div>
        {status.details.length > 0 && (
          <ul className="list-disc ml-4 text-xs mt-1">
            {status.details.map((d, i) => <li key={i}>{d}</li>)}
          </ul>
        )}
      </div>
    </div>
  );
}

export default function AdminDashboard() {
  const { user } = useUserStore();
  const router = useRouter();
  const [checking, setChecking] = useState(false);

  useEffect(() => {
    // [샘플] WebSocket으로 실시간 알림 수신
    // [안내] WebSocket 주소/이벤트는 실제 운영 환경에 맞게 수정하세요.
    const ws = new WebSocket('wss://yourserver/ws/alerts');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'alert') {
        toast(data.message, { icon: '🔔' });
      }
    };
    return () => ws.close();
  }, []);

  async function checkSystemHealth() {
    setChecking(true);
    try {
      const res = await fetch('/api/admin/system-health');
      const data = await res.json();
      if (res.ok) {
        toast.success(`시스템 정상: ${data.status}`);
      } else {
        toast.error(`점검 실패: ${data.message || '오류'}`);
      }
    } catch {
      toast.error('네트워크 오류');
    } finally {
      setChecking(false);
    }
  }

  return (
    <ProtectedRoute requiredRoles={['admin']}>
      <AdminDashboardContent />
      <button
        onClick={checkSystemHealth}
        className="px-4 py-2 bg-green-600 text-white rounded"
        disabled={checking}
        aria-label="운영 상태 점검"
      >
        {checking ? '점검 중...' : '운영 상태 점검'}
      </button>
    </ProtectedRoute>
  );
}

function AdminDashboardContent() {
  const { user } = useUserStore();
  const router = useRouter();

  // 브랜드 목록 상태
  const [brands, setBrands] = useState<Brand[]>([]);
  const [loadingBrands, setLoadingBrands] = useState(true);

  // 통계/알림/피드백 상태
  const [stats, setStats] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [feedbacks, setFeedbacks] = useState<any[]>([]);
  const [loadingStats, setLoadingStats] = useState(true);
  const [loadingAlerts, setLoadingAlerts] = useState(true);
  const [loadingFeedbacks, setLoadingFeedbacks] = useState(true);

  // 상세 모달 상태
  const [selectedAlert, setSelectedAlert] = useState<any | null>(null);
  const [selectedFeedback, setSelectedFeedback] = useState<any | null>(null);

  // 모달 닫기 핸들러
  const closeModal = () => {
    setSelectedAlert(null);
    setSelectedFeedback(null);
  };

  // 브랜드 목록 불러오기 (API 연동)
  useEffect(() => {
    async function fetchBrands() {
      setLoadingBrands(true);
      try {
        // 실제 운영에서는 /api/brands 등으로 교체
        const res = await fetch('/api/brands');
        if (res.ok) {
          const data = await res.json();
          setBrands(data.brands || []);
        } else {
          setBrands([]);
        }
      } catch (e) {
        setBrands([]);
      } finally {
        setLoadingBrands(false);
      }
    }
    fetchBrands();
  }, []);

  // 통계 데이터 불러오기
  useEffect(() => {
    async function fetchStats() {
      setLoadingStats(true);
      try {
        const res = await fetch('/api/admin/brand_stats');
        if (res.ok) {
          const data = await res.json();
          setStats(data.stats || {});
        } else {
          setStats(null);
        }
      } catch (e) {
        setStats(null);
      } finally {
        setLoadingStats(false);
      }
    }
    fetchStats();
  }, []);

  // 시스템 알림 불러오기
  useEffect(() => {
    async function fetchAlerts() {
      setLoadingAlerts(true);
      try {
        const res = await fetch('/api/admin/system-alerts');
        if (res.ok) {
          const data = await res.json();
          setAlerts(data.alerts || []);
        } else {
          setAlerts([]);
        }
      } catch (e) {
        setAlerts([]);
      } finally {
        setLoadingAlerts(false);
      }
    }
    fetchAlerts();
  }, []);

  // 피드백 데이터 불러오기
  useEffect(() => {
    async function fetchFeedbacks() {
      setLoadingFeedbacks(true);
      try {
        const res = await fetch('/api/feedback');
        if (res.ok) {
          const data = await res.json();
          setFeedbacks(data.feedbacks || []);
        } else {
          setFeedbacks([]);
        }
      } catch (e) {
        setFeedbacks([]);
      } finally {
        setLoadingFeedbacks(false);
      }
    }
    fetchFeedbacks();
  }, []);

  // 더미 데이터 (실제로는 API에서 가져올 데이터)
  // const stats = {
  //   totalUsers: 156,
  //   totalBranches: 8,
  //   activeSessions: 23,
  //   systemHealth: "정상",
  //   revenue: "₩12,450,000",
  //   recentActivities: [
  //     { id: 1, action: "새 사용자 등록", user: "김철수", time: "2분 전", type: "success" },
  //     { id: 2, action: "매장 정보 업데이트", user: "홍대점", time: "5분 전", type: "info" },
  //     { id: 3, action: "시스템 백업 완료", user: "시스템", time: "10분 전", type: "success" },
  //     { id: 4, action: "권한 변경", user: "이영희", time: "15분 전", type: "warning" },
  //   ],
  //   systemAlerts: [
  //     { id: 1, type: "warning", message: "매장 3개에서 백업 필요", time: "1시간 전", priority: "high" },
  //     { id: 2, type: "info", message: "새로운 업데이트 사용 가능", time: "2시간 전", priority: "low" },
  //   ]
  // };

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

  // 신규 피드백/알림/시스템 상태 요약 계산
  const newFeedbackCount = feedbacks.filter((f: any) => f.status === 'pending').length;
  const highPriorityAlerts = alerts.filter((a: any) => a.priority === 'high');
  const systemHealth = stats?.systemHealth || 'N/A';

  // [샘플] 피드백 차트 데이터/옵션 예시
  const feedbackChartData = {
    labels: ['1주차', '2주차', '3주차', '4주차'],
    datasets: [{
      label: '피드백 건수',
      data: [3, 7, 5, 9],
      backgroundColor: 'rgba(37, 99, 235, 0.5)',
    }],
  };
  const feedbackChartOptions = { responsive: true, plugins: { legend: { display: false } } };

  const [tab, setTab] = useState<'dashboard' | 'history'>('dashboard');

  return (
    <>
      <div className="flex items-center gap-4 mb-4">
        <button
          className={`px-4 py-2 rounded ${tab === 'dashboard' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
          onClick={() => setTab('dashboard')}
          aria-label="대시보드 탭"
        >
          대시보드
        </button>
        <button
          className={`px-4 py-2 rounded ${tab === 'history' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
          onClick={() => setTab('history')}
          aria-label="자동화 이력 탭"
        >
          자동화 이력
        </button>
        <span className="text-xs text-gray-500">대시보드와 자동화 이력을 탭으로 빠르게 전환할 수 있습니다.</span>
      </div>
      {tab === 'dashboard' && (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
          {/* 대시보드 요약 배너 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <Card className="flex items-center gap-4 p-4 bg-blue-50 border-blue-200">
              <div>
                <span className="text-lg font-bold text-blue-700">신규 피드백</span>
                <span className="ml-2 inline-block bg-blue-600 text-white rounded-full px-3 py-1 text-sm font-semibold">{newFeedbackCount}</span>
              </div>
              <Tooltip>오늘 접수된 신규 피드백 건수입니다.</Tooltip>
            </Card>
            <Card className="flex items-center gap-4 p-4 bg-orange-50 border-orange-200">
              <div>
                <span className="text-lg font-bold text-orange-700">미처리 알림</span>
                <span className="ml-2 inline-block bg-orange-600 text-white rounded-full px-3 py-1 text-sm font-semibold">{alerts.length}</span>
              </div>
              <Tooltip>아직 확인되지 않은 시스템 알림 개수입니다.</Tooltip>
            </Card>
            <Card className={`flex items-center gap-4 p-4 ${systemHealth === '정상' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
              <div>
                <span className="text-lg font-bold text-green-700">시스템 상태</span>
                <span className={`ml-2 inline-block rounded-full px-3 py-1 text-sm font-semibold ${systemHealth === '정상' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'}`}>{systemHealth}</span>
              </div>
              <Tooltip>현재 시스템의 전체 상태입니다.</Tooltip>
            </Card>
          </div>
          <div className="p-6 space-y-8">
            {/* 브랜드별 대시보드/메뉴 동적 생성 */}
            {/*
              [자동화 안내]
              - 이 영역은 /api/brands API에서 브랜드 목록을 받아
              - 신규 브랜드 생성 시 자동으로 대시보드/메뉴에 반영됩니다.
              - 별도의 수동 추가 없이, 브랜드 생성만 하면 자동으로 카드/메뉴가 생성됩니다.
            */}
            <div className="mb-8">
              <h2 className="text-2xl font-bold mb-2">내 브랜드 대시보드</h2>
              {loadingBrands ? (
                <div>브랜드 목록 불러오는 중...</div>
              ) : brands.length === 0 ? (
                <div>관리하는 브랜드가 없습니다.<br/>[신규 브랜드 생성 시 이곳에 자동으로 추가됩니다]</div>
              ) : (
                <div className="flex flex-wrap gap-4">
                  {brands.map((brand) => (
                    <Card key={brand.id} className="w-64 cursor-pointer hover:shadow-xl transition" onClick={() => router.push(`/brand-dashboard/${brand.id}`)}>
                      <CardHeader>
                        <CardTitle>{brand.name}</CardTitle>
                        <CardDescription>브랜드 전용 대시보드</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <Button variant="outline" onClick={() => router.push(`/brand-dashboard/${brand.id}`)}>
                          바로가기
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
            {/* 헤더 */}
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <h1 className="text-4xl font-bold bg-gradient-to-r from-slate-900 to-slate-600 dark:from-white dark:to-slate-300 bg-clip-text text-transparent">
                  업종별 관리자 대시보드
                </h1>
                <p className="text-slate-600 dark:text-slate-400 text-lg">
                  전체 시스템 관리 및 운영 현황
                </p>
              </div>
              <div className="flex items-center space-x-3">
                <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white border-0 shadow-lg">
                  <Crown className="h-4 w-4 mr-1" />
                  업종별 관리자
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
                  <div className="text-3xl font-bold text-slate-900 dark:text-white">{loadingStats ? '...' : stats?.totalUsers || 'N/A'}</div>
                  <p className="text-xs text-slate-600 dark:text-slate-400 flex items-center mt-1">
                    <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
                    {loadingStats ? '...' : stats?.userGrowth || '0%'} from last month
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
                  <div className="text-3xl font-bold text-slate-900 dark:text-white">{loadingStats ? '...' : stats?.totalBranches || 'N/A'}</div>
                  <p className="text-xs text-slate-600 dark:text-slate-400 flex items-center mt-1">
                    <Target className="h-3 w-3 mr-1 text-blue-500" />
                    {loadingStats ? '...' : stats?.branchGrowth || '0'} new this month
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
                  <div className="text-3xl font-bold text-slate-900 dark:text-white">{loadingStats ? '...' : stats?.activeSessions || 'N/A'}</div>
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
                  <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">{loadingStats ? '...' : stats?.systemHealth || 'N/A'}</div>
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
                    {loadingStats ? (
                      <div>활동 데이터를 불러오는 중입니다...</div>
                    ) : stats?.recentActivities?.length === 0 ? (
                      <div>최근 활동이 없습니다.</div>
                    ) : (
                      stats.recentActivities.map((activity: any) => (
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
                      ))
                    )}
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
                    {loadingAlerts ? (
                      <div>알림 데이터를 불러오는 중입니다...</div>
                    ) : alerts.length === 0 ? (
                      <div>주의가 필요한 알림이 없습니다.</div>
                    ) : (
                      alerts.map((alert: any) => (
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
                      ))
                    )}
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
                      <p className="text-2xl font-bold text-slate-900 dark:text-white">{loadingStats ? '...' : stats?.totalRevenue || 'N/A'}</p>
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
                      <p className="text-2xl font-bold text-slate-900 dark:text-white">{loadingStats ? '...' : stats?.onlineStatus || 'N/A'}</p>
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
                      <p className="text-2xl font-bold text-slate-900 dark:text-white">{loadingStats ? '...' : stats?.databaseStatus || 'N/A'}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
          {/* 중요 알림 강조 */}
          {highPriorityAlerts.length > 0 && (
            <div className="mb-6">
              <Card className="p-4 bg-red-100 border-red-300">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="text-red-600" />
                  <span className="font-bold text-red-700">중요 알림:</span>
                  {highPriorityAlerts.map((alert: any) => (
                    <button
                      key={alert.id}
                      className="ml-2 text-red-800 font-semibold underline hover:text-red-600"
                      aria-label="알림 상세 보기"
                      onClick={() => setSelectedAlert(alert)}
                    >
                      {alert.message}
                    </button>
                  ))}
                  <Tooltip>즉시 조치가 필요한 중요 알림입니다.</Tooltip>
                </div>
              </Card>
            </div>
          )}
          <div className="mt-12">
            <h2 className="text-xl font-bold mb-4">실시간 피드백 관리</h2>
            <FeedbackSystem
              userId={String(user?.id || '')}
              isAdmin={true}
              onFeedbackSubmit={() => {}}
              onFeedbackUpdate={() => {}}
              // 피드백 클릭 시 상세 모달 오픈 (예시)
              onFeedbackClick={(feedback: any) => setSelectedFeedback(feedback)}
            />
          </div>
          {/* 알림 상세 모달 */}
          {selectedAlert && (
            <div
              className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
              role="dialog"
              aria-modal="true"
              aria-label="알림 상세 모달"
            >
              <div className="bg-white rounded-lg p-6 w-full max-w-lg shadow-xl">
                <h3 className="text-lg font-bold mb-2 text-red-700">알림 상세</h3>
                <p className="mb-2">{selectedAlert.message}</p>
                <p className="text-sm text-gray-600 mb-4">우선순위: {selectedAlert.priority}</p>
                <button
                  className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  onClick={closeModal}
                  aria-label="모달 닫기"
                >
                  닫기
                </button>
              </div>
            </div>
          )}
          {/* 피드백 상세 모달 */}
          {selectedFeedback && (
            <div
              className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
              role="dialog"
              aria-modal="true"
              aria-label="피드백 상세 모달"
            >
              <div className="bg-white rounded-lg p-6 w-full max-w-lg shadow-xl">
                <h3 className="text-lg font-bold mb-2 text-blue-700">피드백 상세</h3>
                <p className="mb-2 font-semibold">{selectedFeedback.title}</p>
                <p className="mb-2">{selectedFeedback.description}</p>
                <p className="text-sm text-gray-600 mb-2">상태: {selectedFeedback.status}</p>
                <p className="text-sm text-gray-600 mb-4">작성일: {selectedFeedback.created_at}</p>
                {/* 상태 변경/댓글 추가 등 처리 버튼 예시 */}
                <button
                  className="mr-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                  onClick={() => {/* 상태 변경 로직 예시 */}}
                  aria-label="피드백 상태 변경"
                >
                  상태 변경
                </button>
                <button
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  onClick={closeModal}
                  aria-label="모달 닫기"
                >
                  닫기
                </button>
              </div>
            </div>
          )}
        </div>
      )}
      {tab === 'history' && <AutomationHistory />}
    </>
  );
} 

function RecentSystemAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [search, setSearch] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('all');
  useEffect(() => {
    fetch('/api/admin/system-alerts')
      .then(res => res.json())
      .then(data => setAlerts(data.alerts || []));
  }, []);
  const now = Date.now();
  const filteredAlerts = alerts.filter(alert => {
    const matchesSearch =
      !search ||
      alert.message.toLowerCase().includes(search.toLowerCase()) ||
      (alert.time && alert.time.includes(search));
    const matchesPriority =
      priorityFilter === 'all' || alert.priority === priorityFilter;
    return matchesSearch && matchesPriority;
  });
  return (
    <section className="mt-8" aria-label="최근 시스템 알림">
      <h2 className="text-lg font-bold mb-2">최근 시스템 알림/이상 감지</h2>
      <div className="mb-2 flex gap-2">
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="메시지/날짜 검색"
          className="px-2 py-1 border rounded"
          aria-label="알림 검색"
        />
        <select
          value={priorityFilter}
          onChange={e => setPriorityFilter(e.target.value)}
          className="px-2 py-1 border rounded"
          aria-label="우선순위 필터"
        >
          <option value="all">전체</option>
          <option value="high">중요</option>
          <option value="normal">일반</option>
        </select>
      </div>
      <ul className="list-disc pl-6 space-y-1" role="list">
        {filteredAlerts.length === 0 ? (
          <li className="text-gray-400" aria-live="polite">
            최근 알림이 없습니다.
          </li>
        ) : (
          filteredAlerts.map((alert, idx) => {
            const isNew = alert.timestamp && now - new Date(alert.timestamp).getTime() < 60000;
            return (
              <li
                key={idx}
                role="listitem"
                className={
                  (alert.priority === 'high' ? 'text-red-600 font-bold flex items-center ' : '') +
                  (isNew ? ' bg-yellow-100 animate-pulse' : '')
                }
                aria-live={isNew ? 'assertive' : undefined}
              >
                {alert.priority === 'high' && (
                  <span className="mr-1" aria-label="중요 알림" role="img">🚨</span>
                )}
                [{alert.time}] {alert.message}
                {isNew && <span className="ml-2 text-xs text-yellow-700">(새 알림)</span>}
                <button
                  className="ml-2 px-2 py-1 text-xs bg-gray-200 rounded hover:bg-gray-300"
                  aria-label="알림 상세 보기"
                  onClick={() => setSelectedAlert(alert)}
                >
                  상세 보기
                </button>
              </li>
            );
          })
        )}
      </ul>
      {/* 알림 상세 모달 */}
      {selectedAlert && (
        <div
          className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
          role="dialog"
          aria-modal="true"
          aria-labelledby="alert-modal-title"
        >
          <div className="bg-white rounded p-6 w-full max-w-md">
            <h3 id="alert-modal-title" className="text-lg font-bold mb-2">알림 상세 정보</h3>
            <div className="mb-2"><b>메시지:</b> {selectedAlert.message}</div>
            <div className="mb-2"><b>발생 시각:</b> {selectedAlert.time}</div>
            <div className="mb-2"><b>우선순위:</b> {selectedAlert.priority}</div>
            {selectedAlert.link && (
              <div className="mb-2">
                <b>관련 링크:</b>{' '}
                <a href={selectedAlert.link} target="_blank" rel="noopener noreferrer" className="underline text-blue-600">
                  자세히 보기
                </a>
              </div>
            )}
            <button
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
              onClick={() => setSelectedAlert(null)}
              aria-label="닫기"
            >
              닫기
            </button>
          </div>
        </div>
      )}
    </section>
  );
} 