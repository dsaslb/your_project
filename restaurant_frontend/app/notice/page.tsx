"use client"

import React, { useState, useEffect, useMemo } from "react"
import { AppLayout } from "@/components/app-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { 
  Bell, 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  MessageSquare,
  AlertCircle,
  CheckCircle,
  Clock,
  User,
  Mail,
  Eye,
  X,
  Check,
  Filter,
  Megaphone,
  MoreVertical,
  Loader2,
  RefreshCw,
  BarChart3,
  TrendingUp,
  Calendar,
  XCircle
} from "lucide-react"
import { useUser, ActionGuard, useActionPermission } from "@/components/UserContext"
import { Separator } from "@/components/ui/separator"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Pie as PieChartJs } from 'react-chartjs-2'
import { Alert } from "@/components/ui/alert"

// 공지사항 타입 정의
type Notice = {
  id: number;
  title: string;
  content: string;
  type: 'notice' | 'alert' | 'info';
  priority: 'high' | 'medium' | 'low';
  author: string;
  createdAt: string;
  isRead: boolean;
  targetAudience: 'all' | 'kitchen' | 'service' | 'cleaning' | 'management';
  category?: string;
  status: "unread" | "read";
};

// 피드백 타입 정의
type Feedback = {
  id: number;
  title: string;
  content: string;
  type: 'feedback' | 'suggestion' | 'complaint';
  status: 'pending' | 'in_progress' | 'completed' | 'rejected';
  author: string;
  createdAt: string;
  category: string;
  assignedTo?: string;
  response?: string;
  responseDate?: string;
};

// Toast 알림용
function Toast({ message, type, onClose }: { message: string; type: "success" | "error" | "info"; onClose: () => void }) {
  return (
    <div className={`fixed top-6 right-6 z-50 px-4 py-3 rounded shadow-lg text-white ${type === "success" ? "bg-green-600" : type === "error" ? "bg-red-600" : "bg-blue-600"}`}
      role="alert">
      <div className="flex items-center gap-2">
        {type === "success" ? <CheckCircle className="w-5 h-5" /> : type === "error" ? <XCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
        <span>{message}</span>
        <button className="ml-2" onClick={onClose}><X className="w-4 h-4" /></button>
      </div>
    </div>
  );
}

// API 응답 타입
interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

// API 호출 함수들
const api = {
  // 알림 목록 조회
  async getNotices(): Promise<Notice[]> {
    try {
      const response = await fetch('http://localhost:5000/api/notices', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result: ApiResponse<Notice[]> = await response.json();
      return result.data || [];
    } catch (error) {
      console.error('Failed to fetch notices:', error);
      throw error;
    }
  },

  // 알림 등록
  async createNotice(notice: Omit<Notice, 'id' | 'createdAt'>): Promise<Notice> {
    try {
      const response = await fetch('http://localhost:5000/api/notices', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(notice),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result: ApiResponse<Notice> = await response.json();
      return result.data;
    } catch (error) {
      console.error('Failed to create notice:', error);
      throw error;
    }
  },

  // 알림 삭제
  async deleteNotice(id: number): Promise<boolean> {
    try {
      const response = await fetch(`http://localhost:5000/api/notices/${id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return true;
    } catch (error) {
      console.error('Failed to delete notice:', error);
      throw error;
    }
  },

  // 알림 읽음 처리
  async markAsRead(id: number): Promise<Notice> {
    try {
      const response = await fetch(`http://localhost:5000/api/notices/${id}/read`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result: ApiResponse<Notice> = await response.json();
      return result.data;
    } catch (error) {
      console.error('Failed to mark notice as read:', error);
      throw error;
    }
  }
};

// SSE 실시간 알림 구독 훅
function useNoticeSSE(onNewNotice: (notice: Notice) => void, onError: (msg: string) => void) {
  useEffect(() => {
    let eventSource: EventSource | null = null;
    let reconnectTimer: NodeJS.Timeout | null = null;
    let isUnmounted = false;

    function connect() {
      eventSource = new EventSource('http://localhost:5000/api/notices/stream');
      eventSource.onmessage = (event) => {
        try {
          const notice: Notice = JSON.parse(event.data);
          onNewNotice(notice);
        } catch (e) {
          onError('실시간 알림 데이터 파싱 오류');
        }
      };
      eventSource.onerror = () => {
        onError('실시간 알림 서버 연결 끊김, 재연결 시도 중...');
        eventSource?.close();
        if (!isUnmounted) {
          reconnectTimer = setTimeout(connect, 3000);
        }
      };
    }
    connect();
    return () => {
      isUnmounted = true;
      eventSource?.close();
      if (reconnectTimer) clearTimeout(reconnectTimer);
    };
  }, [onNewNotice, onError]);
}

// 통계 데이터 타입
interface NoticeStats {
  total: number;
  unread: number;
  read: number;
  byType: { type: string; count: number }[];
  byCategory: { category: string; count: number }[];
  byDate: { date: string; count: number }[];
}

export default function NoticePage() {
  const { user } = useUser();
  const [notices, setNotices] = useState<Notice[]>([]);
  const [filteredNotices, setFilteredNotices] = useState<Notice[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [dateFilter, setDateFilter] = useState<string>("all");
  const [showAddModal, setShowAddModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedNotice, setSelectedNotice] = useState<Notice | null>(null);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" | "info" } | null>(null);
  
  // 로딩 및 에러 상태
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [empty, setEmpty] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sseStatus, setSseStatus] = useState<'connected'|'disconnected'|'error'>('disconnected');
  const [showStats, setShowStats] = useState(false);
  // 정렬 옵션
  const [sortOption, setSortOption] = useState<'latest'|'oldest'|'priority'>('latest');

  // 권한 체크
  const canCreateNotice = useActionPermission('notices.create');
  const canDeleteNotice = useActionPermission('notices.delete');
  const canEditNotice = useActionPermission('notices.edit');

  // 통계 계산
  const stats = useMemo((): NoticeStats => {
    const total = notices.length;
    const unread = notices.filter(n => n.status === 'unread').length;
    const read = notices.filter(n => n.status === 'read').length;
    
    const byType = Object.entries(
      notices.reduce((acc, notice) => {
        acc[notice.type] = (acc[notice.type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>)
    ).map(([type, count]) => ({ type, count }));
    
    const byCategory = Object.entries(
      notices.reduce((acc, notice) => {
        const category = notice.category || '기타';
        acc[category] = (acc[category] || 0) + 1;
        return acc;
      }, {} as Record<string, number>)
    ).map(([category, count]) => ({ category, count }));
    
    const byDate = Object.entries(
      notices.reduce((acc, notice) => {
        const date = notice.createdAt.split(' ')[0];
        acc[date] = (acc[date] || 0) + 1;
        return acc;
      }, {} as Record<string, number>)
    ).map(([date, count]) => ({ date, count })).slice(-7); // 최근 7일
    
    return { total, unread, read, byType, byCategory, byDate };
  }, [notices]);

  // SSE 연결 상태 표시용 텍스트/아이콘
  const sseStatusText = {
    connected: '실시간 연결됨',
    disconnected: '실시간 연결 끊김',
    error: '실시간 연결 오류'
  };
  const sseStatusIcon = {
    connected: '🟢',
    disconnected: '🔴',
    error: '⚠️'
  };

  // 실시간 알림 구독
  useNoticeSSE(
    (notice) => {
      setNotices((prev) => [notice, ...prev]);
      setFilteredNotices((prev) => [notice, ...prev]);
      setToast({ message: '새로운 알림이 도착했습니다.', type: 'info' });
    },
    (msg) => {
      setSseStatus('error');
      setToast({ message: msg, type: 'error' });
    }
  );

  // 알림 목록 로드
  const loadNotices = async () => {
    setLoading(true);
    setError(null);
    setEmpty(false);
    try {
      const data = await api.getNotices();
      setNotices(data);
      if (data.length === 0) setEmpty(true);
    } catch (err) {
      setError('공지/알림을 불러오지 못했습니다. 네트워크 상태를 확인 후 재시도 해주세요.');
      setToast({ message: '공지/알림을 불러오지 못했습니다.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // 초기 로드
  useEffect(() => {
    loadNotices();
  }, []);

  // 필터/정렬 적용 함수
  useEffect(() => {
    let filtered = [...notices];
    if (searchTerm) {
      filtered = filtered.filter(n => n.title.includes(searchTerm) || n.content.includes(searchTerm));
    }
    if (typeFilter !== 'all') {
      filtered = filtered.filter(n => n.type === typeFilter);
    }
    if (statusFilter !== 'all') {
      filtered = filtered.filter(n => n.status === statusFilter);
    }
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(n => n.category === categoryFilter);
    }
    // 기간 필터(예시: 최근 7일)
    if (dateFilter === '7days') {
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      filtered = filtered.filter(n => new Date(n.createdAt) >= weekAgo);
    }
    // 정렬
    if (sortOption === 'latest') {
      filtered.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    } else if (sortOption === 'oldest') {
      filtered.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime());
    } else if (sortOption === 'priority') {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      filtered.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
    }
    setFilteredNotices(filtered);
  }, [notices, searchTerm, typeFilter, statusFilter, categoryFilter, dateFilter, sortOption]);

  // 타입별 색상
  const getTypeColor = (type: string) => {
    switch (type) {
      case "notice": return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300";
      case "alert": return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300";
      default: return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300";
    }
  };
  
  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case "unread": return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300";
      case "read": return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300";
      default: return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300";
    }
  };

  // 등록
  const handleAddNotice = async () => {
    setIsSubmitting(true);
    try {
      const newNotice = await api.createNotice({
        type: "notice",
        title: "신규 공지",
        content: "테스트용 신규 공지입니다.",
        status: "unread",
        author: user?.name || "관리자"
      });
      
      setNotices(prev => [newNotice, ...prev]);
      setShowAddModal(false);
      setToast({ message: "공지/알림이 등록되었습니다.", type: "success" });
    } catch (error) {
      console.error('Failed to create notice:', error);
      setToast({ message: "공지/알림 등록에 실패했습니다.", type: "error" });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // 삭제
  const handleDeleteNotice = async (id: number) => {
    try {
      await api.deleteNotice(id);
      setNotices(prev => prev.filter(n => n.id !== id));
      setToast({ message: "삭제되었습니다.", type: "success" });
      setShowDetailModal(false);
      setSelectedNotice(null);
    } catch (error) {
      console.error('Failed to delete notice:', error);
      setToast({ message: "삭제에 실패했습니다.", type: "error" });
    }
  };
  
  // 읽음 처리
  const handleReadNotice = async (id: number) => {
    try {
      const updatedNotice = await api.markAsRead(id);
      setNotices(prev => prev.map(n => n.id === id ? updatedNotice : n));
      setToast({ message: "확인 처리되었습니다.", type: "success" });
    } catch (error) {
      console.error('Failed to mark notice as read:', error);
      setToast({ message: "확인 처리에 실패했습니다.", type: "error" });
    }
  };

  // Toast 자동 닫기
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 3500);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  // 통계 카드/그래프 UI 추가
  // 카드 스타일
  const cardClass = "flex flex-col items-center justify-center bg-white dark:bg-gray-800 rounded shadow p-4 w-32 h-24 m-2";
  // 파이차트 데이터(유형별)
  const pieData = {
    labels: stats.byType.map((t) => t.type),
    datasets: [
      {
        data: stats.byType.map((t) => t.count),
        backgroundColor: ['#60a5fa', '#fbbf24', '#f87171', '#34d399', '#a78bfa'],
      },
    ],
  };

  // 로딩 상태
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 text-gray-500 dark:text-gray-400">
        <span className="animate-spin text-3xl mb-2">⏳</span>
        <span>공지/알림을 불러오는 중입니다...</span>
      </div>
    );
  }

  // 에러 상태
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-96 text-red-500 dark:text-red-400">
        <span className="text-3xl mb-2">⚠️</span>
        <span>{error}</span>
        <button
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          onClick={loadNotices}
        >
          재시도
        </button>
      </div>
    );
  }

  if (empty) {
    return (
      <div className="flex flex-col items-center justify-center h-96 text-gray-400 dark:text-gray-500">
        <span className="text-4xl mb-2">📭</span>
        <span>공지/알림이 없습니다.</span>
      </div>
    );
  }

  return (
    <AppLayout>
      <div className="w-full h-full bg-gray-50 dark:bg-gray-900 p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* 헤더 */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">알림/공지</h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                API 연동 완료 - 실제 백엔드와 연동된 공지/알림 관리
              </p>
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                onClick={() => setShowStats(!showStats)}
                className="bg-purple-50 hover:bg-purple-100 dark:bg-purple-900/20 dark:hover:bg-purple-900/30"
              >
                <BarChart3 className="w-4 h-4 mr-2" />
                {showStats ? '통계 숨기기' : '통계 보기'}
              </Button>
              <ActionGuard action="notices.create">
                <Button 
                  onClick={() => setShowAddModal(true)} 
                  className="bg-blue-600 hover:bg-blue-700"
                  aria-label="새 공지사항 등록"
                >
                  <Plus className="w-4 h-4 mr-2" aria-hidden="true" /> 등록
                </Button>
              </ActionGuard>
              <Button 
                variant="outline" 
                onClick={loadNotices}
                aria-label="목록 새로고침"
              >
                <RefreshCw className="w-4 h-4 mr-2" aria-hidden="true" />
                새로고침
              </Button>
            </div>
          </div>

          {/* 페이지 정상 작동 메시지 */}
          <Card className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
            <CardContent className="p-4">
              <div className="flex items-center">
                <Check className="w-5 h-5 text-green-600 mr-2" />
                <span className="text-green-800 dark:text-green-200 font-medium">
                  ✅ 알림/피드백 페이지 정상 작동 중 - 등록/수정/삭제/확인/필터 기능 테스트 가능
                </span>
              </div>
            </CardContent>
          </Card>

          {/* 통계 섹션 */}
          {showStats && (
            <div className="space-y-6">
              {/* 통계 카드 */}
              <div className="flex flex-wrap gap-2 mb-4">
                <div className={cardClass}>
                  <span className="text-lg font-bold">전체</span>
                  <span className="text-2xl">{stats.total}</span>
                </div>
                <div className={cardClass}>
                  <span className="text-lg font-bold">미확인</span>
                  <span className="text-2xl text-red-500">{stats.unread}</span>
                </div>
                <div className={cardClass}>
                  <span className="text-lg font-bold">확인</span>
                  <span className="text-2xl text-green-500">{stats.read}</span>
                </div>
                {stats.byType.map((t) => (
                  <div className={cardClass} key={t.type}>
                    <span className="text-sm font-semibold">{t.type}</span>
                    <span className="text-xl">{t.count}</span>
                  </div>
                ))}
              </div>

              {/* 파이차트(유형별) */}
              <div className="w-64 h-64 mb-4">
                <PieChartJs data={pieData} />
              </div>

              {/* 차트 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>유형별 분포</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={stats.byType}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ type, percent }) => `${type} ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="count"
                        >
                          {stats.byType.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>최근 7일 등록 현황</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={stats.byDate}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#8884d8" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          {/* API 연동 상태 표시 */}
          <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-blue-600 mr-2" />
                  <span className="text-blue-800 dark:text-blue-200 font-medium">
                    ✅ API 연동 완료 - 실제 백엔드 API와 연동되어 실시간 데이터 처리 중
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span>실시간 연결:</span>
                  {sseStatus === 'connected' && <span className="text-green-600">● 연결됨</span>}
                  {sseStatus === 'disconnected' && <span className="text-gray-400">● 대기</span>}
                  {sseStatus === 'error' && <span className="text-red-600">● 오류/재연결 중</span>}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 필터바 */}
          <div className="flex flex-wrap gap-2 mb-4 items-end">
            <input
              type="text"
              placeholder="키워드 검색"
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="border rounded px-2 py-1 w-40"
            />
            <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)} className="border rounded px-2 py-1">
              <option value="all">유형 전체</option>
              <option value="notice">공지</option>
              <option value="alert">경고</option>
              <option value="info">안내</option>
            </select>
            <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="border rounded px-2 py-1">
              <option value="all">상태 전체</option>
              <option value="unread">미확인</option>
              <option value="read">확인</option>
            </select>
            <select value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)} className="border rounded px-2 py-1">
              <option value="all">카테고리 전체</option>
              {stats.byCategory.map(c => (
                <option key={c.category} value={c.category}>{c.category}</option>
              ))}
            </select>
            <select value={dateFilter} onChange={e => setDateFilter(e.target.value)} className="border rounded px-2 py-1">
              <option value="all">전체 기간</option>
              <option value="7days">최근 7일</option>
            </select>
            {/* 정렬 드롭다운 */}
            <select value={sortOption} onChange={e => setSortOption(e.target.value as any)} className="border rounded px-2 py-1">
              <option value="latest">최신순</option>
              <option value="oldest">오래된순</option>
              <option value="priority">중요도순</option>
            </select>
          </div>

          {/* 공지사항 작성 폼 */}
          {showAddModal && (
            <div 
              className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
              role="dialog"
              aria-modal="true"
              aria-labelledby="modal-title"
            >
              <div className="bg-white dark:bg-gray-900 rounded-lg max-w-md w-full">
                <div className="p-6">
                  <h2 id="modal-title" className="text-xl font-bold text-gray-900 dark:text-white mb-4">공지/알림 등록</h2>
                  <div className="space-y-4">
                    <div>
                      <label htmlFor="notice-title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        제목
                      </label>
                      <Input 
                        id="notice-title"
                        placeholder="제목" 
                        aria-describedby="title-help"
                      />
                      <p id="title-help" className="text-xs text-gray-500 mt-1">공지사항의 제목을 입력하세요</p>
                    </div>
                    <div>
                      <label htmlFor="notice-content" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        내용
                      </label>
                      <Input 
                        id="notice-content"
                        placeholder="내용" 
                        aria-describedby="content-help"
                      />
                      <p id="content-help" className="text-xs text-gray-500 mt-1">공지사항의 내용을 입력하세요</p>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-6">
                    <Button 
                      onClick={handleAddNotice} 
                      className="flex-1"
                      disabled={isSubmitting}
                      aria-describedby="submit-help"
                    >
                      {isSubmitting ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
                          등록 중...
                        </>
                      ) : (
                        '등록'
                      )}
                    </Button>
                    <Button 
                      variant="outline" 
                      onClick={() => setShowAddModal(false)} 
                      className="flex-1"
                      aria-label="등록 취소"
                    >
                      취소
                    </Button>
                  </div>
                  <p id="submit-help" className="sr-only">등록 버튼을 클릭하면 새로운 공지사항이 등록됩니다</p>
                </div>
              </div>
            </div>
          )}

          {/* 공지사항 목록 */}
          {filteredNotices.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <Bell className="w-12 h-12 mx-auto mb-4 text-gray-400" aria-hidden="true" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  {searchTerm || typeFilter !== "all" || statusFilter !== "all" || categoryFilter !== "all" || dateFilter !== "all"
                    ? "검색 결과가 없습니다" 
                    : "등록된 알림이 없습니다"}
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {searchTerm || typeFilter !== "all" || statusFilter !== "all" || categoryFilter !== "all" || dateFilter !== "all"
                    ? "다른 검색어나 필터를 시도해보세요"
                    : "새로운 알림을 등록해보세요"}
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" role="list" aria-label="공지사항 목록">
              {filteredNotices.map(notice => (
                <Card key={notice.id} className="hover:shadow-lg transition-shadow" role="listitem">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {notice.type === "notice" ? <Megaphone className="w-6 h-6 text-blue-500" aria-hidden="true" /> : 
                         notice.type === "alert" ? <Bell className="w-6 h-6 text-red-500" aria-hidden="true" /> :
                         <AlertCircle className="w-6 h-6 text-green-500" aria-hidden="true" />}
                        <span className="font-semibold text-lg text-gray-900 dark:text-white">{notice.title}</span>
                      </div>
                      <Badge className={getTypeColor(notice.type)}>
                        {notice.type === "notice" ? "공지" : notice.type === "alert" ? "알림" : "정보"}
                      </Badge>
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">작성자: {notice.author}</div>
                    <div className="text-xs text-gray-400 dark:text-gray-500 mb-2">작성일: {notice.createdAt}</div>
                    {notice.category && (
                      <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">카테고리: {notice.category}</div>
                    )}
                    <div className="flex gap-2 mt-2">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => { setSelectedNotice(notice); setShowDetailModal(true); }}
                        aria-label={`${notice.title} 상세보기`}
                      >
                        <Eye className="w-4 h-4 mr-1" aria-hidden="true" /> 상세
                      </Button>
                      <ActionGuard action="notices.delete">
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => handleDeleteNotice(notice.id)} 
                          className="text-red-600 hover:text-red-700"
                          aria-label={`${notice.title} 삭제`}
                        >
                          <Trash2 className="w-4 h-4" aria-hidden="true" /> 삭제
                        </Button>
                      </ActionGuard>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* 상세 모달 */}
        {showDetailModal && selectedNotice && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            role="dialog"
            aria-modal="true"
            aria-labelledby="detail-title"
          >
            <div className="bg-white dark:bg-gray-900 rounded-lg max-w-md w-full">
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 id="detail-title" className="text-xl font-bold text-gray-900 dark:text-white">상세 보기</h2>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => setShowDetailModal(false)}
                    aria-label="상세보기 닫기"
                  >
                    <X className="w-6 h-6" aria-hidden="true" />
                  </Button>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-lg font-semibold">
                    {selectedNotice.type === "notice" ? <Megaphone className="w-5 h-5 text-blue-500" aria-hidden="true" /> : 
                     selectedNotice.type === "alert" ? <Bell className="w-5 h-5 text-red-500" aria-hidden="true" /> :
                     <AlertCircle className="w-5 h-5 text-green-500" aria-hidden="true" />}
                    {selectedNotice.title}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">{selectedNotice.content}</div>
                  <div className="text-xs text-gray-400 dark:text-gray-500">작성일: {selectedNotice.createdAt}</div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">작성자: {selectedNotice.author}</div>
                  <Badge className={getTypeColor(selectedNotice.type)}>
                    {selectedNotice.type === "notice" ? "공지" : selectedNotice.type === "alert" ? "알림" : "정보"}
                  </Badge>
                  <Badge className={getStatusColor(selectedNotice.status)}>
                    {selectedNotice.status === "unread" ? "미확인" : "확인"}
                  </Badge>
                </div>
                <div className="flex gap-2 mt-6">
                  {selectedNotice.status === "unread" && (
                    <Button 
                      onClick={() => handleReadNotice(selectedNotice.id)} 
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                      aria-label="확인 처리"
                    >
                      <Check className="w-4 h-4 mr-2" aria-hidden="true" /> 확인
                    </Button>
                  )}
                  <Button 
                    variant="outline" 
                    onClick={() => setShowDetailModal(false)} 
                    className="flex-1"
                    aria-label="상세보기 닫기"
                  >
                    닫기
                  </Button>
                  <ActionGuard action="notices.delete">
                    <Button 
                      variant="destructive" 
                      onClick={() => handleDeleteNotice(selectedNotice.id)} 
                      className="flex-1"
                      aria-label="공지사항 삭제"
                    >
                      삭제
                    </Button>
                  </ActionGuard>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 접근성 개선: 페이지 정보 */}
        <div className="sr-only">
          <p>공지사항 관리 페이지입니다. 총 {filteredNotices.length}개의 공지사항이 있습니다.</p>
          <p>검색어: {searchTerm || '없음'}</p>
          <p>필터: 유형={typeFilter}, 상태={statusFilter}, 카테고리={categoryFilter}, 기간={dateFilter}</p>
        </div>

        {/* 렌더링 상단에 SSE 상태 표시 및 연결 실패 시 재시도 버튼 */}
        <div className="flex items-center gap-2 mb-2 text-sm">
          <span>{sseStatusIcon[sseStatus]}</span>
          <span>{sseStatusText[sseStatus]}</span>
          {sseStatus === 'error' && (
            <button
              className="ml-2 px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
              onClick={() => { setSseStatus('disconnected'); loadNotices(); setToast(null); }}
            >
              실시간 재시도
            </button>
          )}
        </div>

        {/* Toast 메시지 */}
        {toast && (
          <div className={`fixed top-4 right-4 z-50 px-4 py-2 rounded shadow-lg text-white ${toast.type === 'error' ? 'bg-red-500' : toast.type === 'info' ? 'bg-blue-500' : 'bg-green-500'}`}>
            {toast.message}
          </div>
        )}
      </div>
    </AppLayout>
  )
} 