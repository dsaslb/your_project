'use client';

import React, { useEffect, useState } from 'react';
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
// import FeedbackSystem from '../../../core/frontend/FeedbackSystem'; // 실제로 존재하지 않거나 프론트엔드에서 접근 불가하므로 임시 주석 처리
import { Tooltip as TooltipUI } from '@/components/ui/tooltip';
import { toast } from 'sonner';
import { Bar } from 'react-chartjs-2'; // 차트 예시
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  PointElement,
  LineElement,
  Filler
} from 'chart.js';
import Link from 'next/link';
import { useMediaQuery } from 'react-responsive';
import LanguageSwitcher from '../../components/LanguageSwitcher';
import { Line, Pie } from 'react-chartjs-2'; // Chart.js 차트 컴포넌트만 사용
import { useBrands } from '../../src/hooks/useApi';

// Chart.js 스케일/플러그인 등록 (category 오류 방지)
ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, ChartTooltip, Legend, PointElement, LineElement, Filler);

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
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [realtimeNotifications, setRealtimeNotifications] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [brandFilter, setBrandFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const isMobile = useMediaQuery({ maxWidth: 768 });
  const [announcements, setAnnouncements] = useState<any[]>([]);
  // 실시간 KPI 변화 데이터 (예시: 최근 7일)
  const [kpiHistory, setKpiHistory] = useState<any>({
    dates: [], brands: [], stores: [], users: [], orders: []
  });
  // 실시간 알림/이상탐지 통계 (예시)
  const [alertStats, setAlertStats] = useState<any>({ success: 0, warning: 0, error: 0 });
  // WebSocket으로 실시간 KPI/알림 통계 수신 (개발 환경에서는 비활성화)
  useEffect(() => {
    if (process.env.NODE_ENV === 'production') {
      const ws = new WebSocket('wss://yourserver/ws/dashboard-kpi');
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'kpi_history') setKpiHistory(data.payload);
        if (data.type === 'alert_stats') setAlertStats(data.payload);
      };
      return () => ws.close();
    }
  }, []);

  // 실시간 알림 WebSocket 연결 (개발 환경에서는 비활성화)
  useEffect(() => {
    if (process.env.NODE_ENV === 'production') {
      const ws = new WebSocket('wss://yourserver/ws/alerts');
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'alert') {
          setRealtimeNotifications((prev) => [{...data, created_at: new Date().toISOString()}, ...prev].slice(0, 10));
          toast(data.message, { icon: '🔔' });
        }
      };
      return () => ws.close();
    }
  }, []);

  // 실시간 공지사항/피드백 WebSocket 연동 (개발 환경에서는 비활성화)
  useEffect(() => {
    if (process.env.NODE_ENV === 'production') {
      const ws = new WebSocket('wss://yourserver/ws/announcements');
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'announcement') {
          setAnnouncements((prev) => [data, ...prev].slice(0, 10));
          toast(`새 공지: ${data.title || data.message || ''}`, { icon: '📢' });
        }
        if (data.type === 'feedback') {
          toast(`새 피드백: ${data.user || '익명'} - ${data.message || ''}`, { icon: '💬' });
        }
      };
      return () => ws.close();
    }
  }, []);

  useEffect(() => {
    fetch('/api/admin/dashboard')
      .then(res => res.json())
      .then(data => {
        if (data.success) setDashboard(data);
        else setError(data.error || '데이터 로드 실패');
      })
      .catch(() => setError('네트워크 오류'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="dark:bg-slate-900 min-h-screen flex items-center justify-center text-lg">대시보드 로딩 중...</div>;
  if (error) return <div className="text-red-500 dark:text-red-400">{error}</div>;
  if (!dashboard) return <div>데이터 없음</div>;

  const { cards, charts, tables, notifications } = dashboard;
  // 필터/검색 적용
  const filteredOrders = tables.recent_orders.filter((o: any) =>
    (brandFilter === 'all' || o.brand_id === brandFilter) &&
    (statusFilter === 'all' || o.status === statusFilter) &&
    (search === '' || o.item?.toLowerCase().includes(search.toLowerCase()))
  );
  const filteredLogs = tables.system_logs.filter((log: any) =>
    search === '' || log.action?.toLowerCase().includes(search.toLowerCase())
  );
  const allNotifications = [...realtimeNotifications, ...notifications].slice(0, 10);

  return (
    <div className="p-2 md:p-6 space-y-8 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 min-h-screen">
      {/* 브랜드 관리 섹션을 최상단에 배치 */}
      <BrandManagerSection />
      <div className="flex justify-end items-center p-2 bg-white shadow mb-2">
        <LanguageSwitcher />
      </div>
      {/* KPI 카드 */}
      <div className="flex flex-wrap gap-4 mb-4">
        <Card className="flex-1 min-w-[180px] bg-gradient-to-br from-blue-500/10 to-cyan-500/10 dark:from-blue-900/30 dark:to-cyan-900/30 shadow-lg animate-fade-in">
          <CardContent className="py-4 flex items-center gap-3">
            <Crown className="h-6 w-6 text-blue-600 dark:text-blue-300" />
            <div>
              <div className="text-xs text-blue-700 dark:text-blue-200">브랜드 수</div>
              <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">{cards.total_brands}</div>
            </div>
          </CardContent>
        </Card>
        <Card className="flex-1 min-w-[180px] bg-gradient-to-br from-green-500/10 to-emerald-500/10 dark:from-green-900/30 dark:to-emerald-900/30 shadow-lg animate-fade-in">
          <CardContent className="py-4 flex items-center gap-3">
            <Building2 className="h-6 w-6 text-green-600 dark:text-green-300" />
            <div>
              <div className="text-xs text-green-700 dark:text-green-200">매장 수</div>
              <div className="text-2xl font-bold text-green-900 dark:text-green-100">{cards.total_stores}</div>
            </div>
          </CardContent>
        </Card>
        <Card className="flex-1 min-w-[180px] bg-gradient-to-br from-purple-500/10 to-pink-500/10 dark:from-purple-900/30 dark:to-pink-900/30 shadow-lg animate-fade-in">
          <CardContent className="py-4 flex items-center gap-3">
            <Users className="h-6 w-6 text-purple-600 dark:text-purple-300" />
            <div>
              <div className="text-xs text-purple-700 dark:text-purple-200">직원 수</div>
              <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">{cards.total_users}</div>
            </div>
          </CardContent>
        </Card>
        <Card className="flex-1 min-w-[180px] bg-gradient-to-br from-yellow-500/10 to-orange-500/10 dark:from-yellow-900/30 dark:to-orange-900/30 shadow-lg animate-fade-in">
          <CardContent className="py-4 flex items-center gap-3">
            <BarChart3 className="h-6 w-6 text-yellow-600 dark:text-yellow-300" />
            <div>
              <div className="text-xs text-yellow-700 dark:text-yellow-200">주문 수</div>
              <div className="text-2xl font-bold text-yellow-900 dark:text-yellow-100">{cards.total_orders}</div>
            </div>
          </CardContent>
        </Card>
      </div>
      {/* 필터/검색 */}
      <div className="flex flex-wrap gap-2 items-center mb-2">
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="상품/액션 검색"
          className="px-2 py-1 border rounded dark:bg-slate-800 dark:text-white"
        />
        <select value={brandFilter} onChange={e => setBrandFilter(e.target.value)} className="px-2 py-1 border rounded dark:bg-slate-800 dark:text-white">
          <option value="all">전체 브랜드</option>
          {charts.brand_stats.map((b: any) => <option key={b.brand_name} value={b.brand_name}>{b.brand_name}</option>)}
        </select>
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="px-2 py-1 border rounded dark:bg-slate-800 dark:text-white">
          <option value="all">전체 상태</option>
          <option value="pending">대기</option>
          <option value="completed">완료</option>
        </select>
      </div>
      {/* 브랜드별 통계 그래프 */}
      <div className="bg-white dark:bg-slate-800 rounded shadow p-4 overflow-x-auto animate-fade-in">
        <h2 className="font-bold mb-2 text-slate-900 dark:text-white">브랜드별 매장/직원/주문 통계</h2>
        <Bar
          data={{
            labels: charts.brand_stats.map((b: any) => b.brand_name),
            datasets: [
              { label: '매장 수', data: charts.brand_stats.map((b: any) => b.store_count), backgroundColor: 'rgba(59,130,246,0.5)' },
              { label: '직원 수', data: charts.brand_stats.map((b: any) => b.employee_count), backgroundColor: 'rgba(16,185,129,0.5)' },
              { label: '주문 수', data: charts.brand_stats.map((b: any) => b.order_count), backgroundColor: 'rgba(251,191,36,0.5)' },
            ]
          }}
          options={{ responsive: true, plugins: { legend: { position: isMobile ? 'bottom' : 'top' } } }}
        />
      </div>
      {/* 최근 주문 테이블 */}
      <div className="bg-white dark:bg-slate-800 rounded shadow p-4 overflow-x-auto animate-fade-in">
        <h2 className="font-bold mb-2 text-slate-900 dark:text-white">최근 주문</h2>
        <table className="w-full text-sm">
          <thead><tr><th>ID</th><th>상품</th><th>매장ID</th><th>상태</th><th>일시</th></tr></thead>
          <tbody>
            {filteredOrders.map((o: any) => (
              <tr key={o.id}><td>{o.id}</td><td>{o.item}</td><td>{o.store_id}</td><td>{o.status}</td><td>{o.created_at}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* 시스템 로그 테이블 */}
      <div className="bg-white dark:bg-slate-800 rounded shadow p-4 overflow-x-auto animate-fade-in">
        <h2 className="font-bold mb-2 text-slate-900 dark:text-white">시스템 로그</h2>
        <table className="w-full text-sm">
          <thead><tr><th>ID</th><th>액션</th><th>사용자</th><th>일시</th><th>상세</th></tr></thead>
          <tbody>
            {filteredLogs.map((log: any) => (
              <tr key={log.id}><td>{log.id}</td><td>{log.action}</td><td>{log.user_id}</td><td>{log.created_at}</td><td>{log.detail}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* 실시간 알림/최근 알림 리스트 */}
      <div className="bg-white dark:bg-slate-800 rounded shadow p-4 animate-fade-in">
        <h2 className="font-bold mb-2 text-slate-900 dark:text-white">실시간 알림/최근 알림</h2>
        <ul className="space-y-2">
          {allNotifications.map((n: any, idx: number) => (
            <li key={n.id || idx} className={`p-2 rounded flex items-center gap-2 ${n.level === 'info' ? 'bg-blue-50 dark:bg-blue-900/20' : n.level === 'warning' ? 'bg-yellow-50 dark:bg-yellow-900/20' : 'bg-red-50 dark:bg-red-900/20'} animate-fade-in`}>
              <Bell className="h-4 w-4 text-blue-400 dark:text-blue-200" />
              <b>[{n.level}]</b> {n.message} <span className="text-xs text-gray-400">{n.created_at}</span>
            </li>
          ))}
        </ul>
      </div>
      {/* 실시간 공지사항 리스트 */}
      <div className="bg-white dark:bg-slate-800 rounded shadow p-4 animate-fade-in mt-4">
        <h2 className="font-bold mb-2 text-slate-900 dark:text-white">공지사항</h2>
        <ul className="list-disc pl-6 space-y-1">
          {announcements.length === 0 ? (
            <li className="text-gray-400">최근 공지사항이 없습니다.</li>
          ) : (
            announcements.map((a, idx) => (
              <li key={idx} className="text-slate-800 dark:text-white">
                <b>{a.title || '공지'}</b> <span className="text-xs text-gray-500">{a.created_at || ''}</span>
                <div className="text-sm">{a.message}</div>
              </li>
            ))
          )}
        </ul>
      </div>
      {/* 실시간 KPI 변화 추이 차트 */}
      <div className="bg-white dark:bg-slate-800 rounded shadow p-4 animate-fade-in">
        <h2 className="font-bold mb-2 text-slate-900 dark:text-white">실시간 KPI 변화 추이</h2>
        <Line
          data={{
            labels: kpiHistory.dates,
            datasets: [
              { label: '브랜드 수', data: kpiHistory.brands, borderColor: 'rgba(59,130,246,1)', backgroundColor: 'rgba(59,130,246,0.2)', fill: true },
              { label: '매장 수', data: kpiHistory.stores, borderColor: 'rgba(16,185,129,1)', backgroundColor: 'rgba(16,185,129,0.2)', fill: true },
              { label: '직원 수', data: kpiHistory.users, borderColor: 'rgba(168,85,247,1)', backgroundColor: 'rgba(168,85,247,0.2)', fill: true },
              { label: '주문 수', data: kpiHistory.orders, borderColor: 'rgba(251,191,36,1)', backgroundColor: 'rgba(251,191,36,0.2)', fill: true },
            ]
          }}
          options={{ responsive: true, plugins: { legend: { position: 'top' } } }}
        />
      </div>
      {/* 실시간 알림/이상탐지 시각화 */}
      <div className="bg-white dark:bg-slate-800 rounded shadow p-4 animate-fade-in">
        <h2 className="font-bold mb-2 text-slate-900 dark:text-white">최근 알림/이상탐지 통계</h2>
        <Pie
          data={{
            labels: ['성공', '경고', '오류'],
            datasets: [
              { data: [alertStats.success, alertStats.warning, alertStats.error], backgroundColor: ['#22c55e', '#facc15', '#ef4444'] }
            ]
          }}
          options={{ responsive: true, plugins: { legend: { position: 'bottom' } } }}
        />
      </div>
    </div>
  );
}

function AdminDashboardContent() {
  const { user } = useUserStore();
  const router = useRouter();

  // useBrands만 실제 훅 사용
  const { data: brandsData, isLoading: loadingBrands }: any = useBrands();

  // 더미 데이터로 대체
  const loadingStats = false;
  const userGrowth = '12%';
  const branchGrowth = 8;
  const dashboardData = { data: { systemHealth: '정상', totalUsers: 156, totalBranches: 8, activeSessions: 23, revenue: '₩12,450,000' } };
  const statsData = { data: { ...dashboardData.data } };
  const alertsData = { data: { alerts: [
    { id: 1, type: 'warning', message: '매장 3개에서 백업 필요', time: '1시간 전', priority: 'high' },
    { id: 2, type: 'info', message: '새로운 업데이트 사용 가능', time: '2시간 전', priority: 'low' },
  ] } };
  const feedbacksData = { data: { feedbacks: [
    { id: 1, status: 'pending', message: '직원 승인 요청', time: '10분 전' },
    { id: 2, status: 'done', message: '매장 정보 수정', time: '1시간 전' },
  ] } };

  // 데이터 추출
  const stats = statsData?.data || dashboardData?.data;
  const brands: any[] = brandsData?.data?.brands || [];
  const alerts: any[] = alertsData?.data?.alerts || [];
  const feedbacks: any[] = feedbacksData?.data?.feedbacks || [];

  // 상세 모달 상태
  const recentActivities: any[] = [
    { id: 1, action: '새 사용자 등록', user: '김철수', time: '2분 전', type: 'success' },
    { id: 2, action: '매장 정보 업데이트', user: '홍대점', time: '5분 전', type: 'info' },
    { id: 3, action: '시스템 백업 완료', user: '시스템', time: '10분 전', type: 'success' },
    { id: 4, action: '권한 변경', user: '이영희', time: '15분 전', type: 'warning' },
  ];
  const [selectedAlert, setSelectedAlert] = useState<any | null>(null);
  const [selectedFeedback, setSelectedFeedback] = useState<any | null>(null);

    // 모달 닫기 핸들러
  const closeModal = () => {
    setSelectedAlert(null);
    setSelectedFeedback(null);
  };

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

  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
          {/* 대시보드 요약 배너 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <Card className="flex items-center gap-4 p-4 bg-blue-50 border-blue-200">
              <div>
                <span className="text-lg font-bold text-blue-700">신규 피드백</span>
                <span className="ml-2 inline-block bg-blue-600 text-white rounded-full px-3 py-1 text-sm font-semibold">{newFeedbackCount}</span>
              </div>
              <TooltipUI>오늘 접수된 신규 피드백 건수입니다.</TooltipUI>
            </Card>
            <Card className="flex items-center gap-4 p-4 bg-orange-50 border-orange-200">
              <div>
                <span className="text-lg font-bold text-orange-700">미처리 알림</span>
                <span className="ml-2 inline-block bg-orange-600 text-white rounded-full px-3 py-1 text-sm font-semibold">{alerts.length}</span>
              </div>
              <TooltipUI>아직 확인되지 않은 시스템 알림 개수입니다.</TooltipUI>
            </Card>
            <Card className={`flex items-center gap-4 p-4 ${systemHealth === '정상' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
              <div>
                <span className="text-lg font-bold text-green-700">시스템 상태</span>
                <span className={`ml-2 inline-block rounded-full px-3 py-1 text-sm font-semibold ${systemHealth === '정상' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'}`}>{systemHealth}</span>
              </div>
              <TooltipUI>현재 시스템의 전체 상태입니다.</TooltipUI>
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
                    {loadingStats ? '...' : userGrowth || '0%'} from last month
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
                    {loadingStats ? '...' : branchGrowth || '0'} new this month
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
                    ) : recentActivities.length === 0 ? (
                      <div>최근 활동이 없습니다.</div>
                    ) : (
                      recentActivities.map((activity: any) => (
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
                    {loadingStats ? (
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
                      <p className="text-2xl font-bold text-slate-900 dark:text-white">{loadingStats ? '...' : stats?.revenue || 'N/A'}</p>
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
                      <p className="text-2xl font-bold text-slate-900 dark:text-white">{loadingStats ? '...' : '정상'}</p>
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
                      <p className="text-2xl font-bold text-slate-900 dark:text-white">{loadingStats ? '...' : '정상'}</p>
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
                  <TooltipUI>즉시 조치가 필요한 중요 알림입니다.</TooltipUI>
                </div>
              </Card>
            </div>
          )}
          <div className="mt-12">
            <h2 className="text-xl font-bold mb-4">실시간 피드백 관리</h2>
            {/*
              <FeedbackSystem
                userId={String(user?.id || '')}
                isAdmin={true}
                // 피드백 클릭 시 상세 모달 오픈 (예시)
                onFeedbackClick={(feedback: any) => setSelectedFeedback(feedback)}
              />
              */}
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
    </>
  );
} 

function RecentSystemAlerts() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<any | null>(null);
  const [search, setSearch] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('all');
  useEffect(() => {
    fetch('/api/admin/system-alerts')
      .then(res => res.json())
      .then(data => setAlerts(data.alerts || []));
  }, []);
  const now = Date.now();
  const filteredAlerts: any[] = alerts.filter(alert => {
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

// 브랜드 관리 섹션 추가 (브랜드 목록, 추가/수정/삭제, 관리자 등록/수정/삭제)


function BrandManagerSection() {
  const [brands, setBrands] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [editBrand, setEditBrand] = useState(null);
  const [form, setForm] = useState({
    name: '',
    description: '',
    manager: { name: '', email: '', password: '' },
  });
  const [saving, setSaving] = useState(false);

  // 브랜드 목록 불러오기
  useEffect(() => {
    fetch('/api/admin/restaurant/industry/brands')
      .then(res => res.json())
      .then(data => setBrands(data.brands || []))
      .catch(() => setError('브랜드 목록을 불러오지 못했습니다.'))
      .finally(() => setLoading(false));
  }, []);

  // 브랜드 추가/수정
  const handleSave = async () => {
    // 이메일, 연락처 정규식
    const emailRegex = /^[\w.-]+@[\w.-]+\.[A-Za-z]{2,}$/;
    const phoneRegex = /^01[016789]-\d{3,4}-\d{4}$/;
    if (!form.name || !form.manager.name || !form.manager.email) {
      alert('브랜드명, 관리자 이름, 관리자 이메일을 모두 입력해 주세요.');
      return;
    }
    if (!emailRegex.test(form.manager.email)) {
      alert('이메일 형식이 올바르지 않습니다. 예: user@example.com');
      return;
    }
    if (!form.manager.phone || !phoneRegex.test(form.manager.phone)) {
      alert('연락처 형식이 올바르지 않습니다. 예: 010-1234-5678');
      return;
    }
    // 실제 전송 데이터 콘솔 출력
    console.log('브랜드 저장 요청 데이터:', form);
    setSaving(true);
    const method = editBrand ? 'PUT' : 'POST';
    const url = editBrand ? `/api/admin/restaurant/industry/brands/${editBrand.id}` : '/api/admin/restaurant/industry/brands';
    const body = JSON.stringify({
      name: form.name,
      description: form.description,
      manager: form.manager,
    });
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body,
    });
    if (res.ok) {
      setShowModal(false);
      setEditBrand(null);
      setForm({ name: '', description: '', manager: { name: '', email: '', phone: '', password: '' } });
      // 목록 새로고침
      setLoading(true);
      fetch('/api/admin/restaurant/industry/brands')
        .then(res => res.json())
        .then(data => setBrands(data.brands || []))
        .finally(() => setLoading(false));
    } else {
      alert('저장 실패');
    }
    setSaving(false);
  };

  // 브랜드 삭제
  const handleDelete = async (brandId: any) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return;
    await fetch(`/api/admin/restaurant/industry/brands/${brandId}`, { method: 'DELETE' });
    setBrands(brands.filter((b: any) => b.id !== brandId));
  };

  // 브랜드 수정 모달 열기
  const openEdit = (brand: any) => {
    setEditBrand(brand);
    setForm({
      name: brand.name,
      description: brand.description,
      manager: brand.manager || { name: '', email: '', password: '' },
    });
    setShowModal(true);
  };

  // 브랜드 추가 모달 열기
  const openAdd = () => {
    setEditBrand(null);
    setForm({ name: '', description: '', manager: { name: '', email: '', password: '' } });
    setShowModal(true);
  };

  return (
    <section className="mt-8" aria-label="브랜드 관리">
      <h2 className="text-lg font-bold mb-2">브랜드 관리</h2>
      <button className="mb-4 px-4 py-2 bg-blue-600 text-white rounded" onClick={openAdd}>브랜드 추가</button>
      {loading ? <div>로딩 중...</div> : error ? <div className="text-red-500">{error}</div> : (
        <table className="w-full text-sm mb-4">
          <thead><tr><th>이름</th><th>설명</th><th>관리자</th><th>액션</th></tr></thead>
          <tbody>
            {brands.map((brand: any) => (
              <tr key={brand.id}>
                <td>{brand.name}</td>
                <td>{brand.description}</td>
                <td>{brand.manager ? `${brand.manager.name} (${brand.manager.email})` : '-'}</td>
                <td>
                  <button className="px-2 py-1 bg-green-500 text-white rounded mr-2" onClick={() => openEdit(brand)}>수정</button>
                  <button className="px-2 py-1 bg-red-500 text-white rounded" onClick={() => handleDelete(brand.id)}>삭제</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {/* 브랜드 추가/수정 모달 */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white rounded p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-2">{editBrand ? '브랜드 수정' : '브랜드 추가'}</h3>
            <div className="mb-2">
              <label className="block mb-1">브랜드명</label>
              <input className="border rounded px-2 py-1 w-full" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
            </div>
            <div className="mb-2">
              <label className="block mb-1">설명</label>
              <input className="border rounded px-2 py-1 w-full" value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
            </div>
            <div className="mb-2">
              <label className="block mb-1">브랜드 관리자 이름</label>
              <input className="border rounded px-2 py-1 w-full" value={form.manager.name} onChange={e => setForm(f => ({ ...f, manager: { ...f.manager, name: e.target.value } }))} placeholder="예: 홍길동" />
            </div>
            <div className="mb-2">
              <label className="block mb-1">브랜드 관리자 이메일</label>
              <input className="border rounded px-2 py-1 w-full" value={form.manager.email} onChange={e => setForm(f => ({ ...f, manager: { ...f.manager, email: e.target.value } }))} placeholder="예: user@example.com" />
            </div>
            <div className="mb-2">
              <label className="block mb-1">브랜드 관리자 연락처</label>
              <input className="border rounded px-2 py-1 w-full" value={form.manager.phone || ''} onChange={e => setForm(f => ({ ...f, manager: { ...f.manager, phone: e.target.value } }))} placeholder="예: 010-1234-5678" />
            </div>
            <div className="mb-2">
              <label className="block mb-1">브랜드 관리자 비밀번호</label>
              <input type="password" className="border rounded px-2 py-1 w-full" value={form.manager.password} onChange={e => setForm(f => ({ ...f, manager: { ...f.manager, password: e.target.value } }))} />
            </div>
            <div className="flex gap-2 mt-4">
              <button className="px-4 py-2 bg-blue-600 text-white rounded" onClick={handleSave} disabled={saving}>{saving ? '저장 중...' : '저장'}</button>
              <button className="px-4 py-2 bg-gray-300 rounded" onClick={() => setShowModal(false)}>취소</button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
} 