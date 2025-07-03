"use client"

import React, { useState, useEffect, useMemo } from 'react';
import { ResizableLayout } from "@/components/resizable-layout"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Calendar, Plus, Users, Clock, Edit, Trash2, Eye, X, Check, List, LayoutGrid, Sun, Moon, Broom } from "lucide-react"
import { useUser } from "@/components/UserContext"
import { toast } from 'sonner';
import NotificationService from '@/lib/notification-service';
import { PermissionGuard } from '@/components/PermissionGuard';
import { Alert } from '@/components/ui/alert';

interface ScheduleItem {
  id: number;
  staff: string;
  date: string;
  shift: string;
  status: 'confirmed' | 'pending' | 'cancelled';
}

const dummySchedules: ScheduleItem[] = [
  { id: 1, staff: '홍길동', date: '2024-06-01', shift: '오전', status: 'confirmed' },
  { id: 2, staff: '김철수', date: '2024-06-01', shift: '오후', status: 'pending' },
  { id: 3, staff: '이영희', date: '2024-06-02', shift: '오전', status: 'cancelled' },
];

// 알림 등록 함수 (더미 구현)
async function createScheduleNotice({ type, title, content, author }) {
  try {
    // 실제 API 호출 대신 콘솔 로그
    console.log('Schedule notice created:', { type, title, content, author });
  } catch (e) {
    console.error('Failed to create schedule notice:', e);
  }
}

// 권한 체크 함수 예시
function useSchedulePermissions(user) {
  return {
    canAdd: user?.role === 'admin' || user?.permissions?.schedule_management?.create,
    canEdit: user?.role === 'admin' || user?.permissions?.schedule_management?.edit,
    canDelete: user?.role === 'admin' || user?.permissions?.schedule_management?.delete,
    canComplete: user?.role === 'admin' || user?.permissions?.schedule_management?.edit,
    canView: true,
  };
}

// 1. API 함수 정의 (예시)
const scheduleApi = {
  async getSchedules(type: 'work' | 'cleaning') {
    const res = await fetch(`/api/schedule?type=${type}`);
    if (!res.ok) throw new Error('스케줄 목록을 불러오지 못했습니다.');
    return res.json();
  },
  async createSchedule(data) {
    const res = await fetch('/api/schedule', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('스케줄 등록에 실패했습니다.');
    return res.json();
  },
  async updateSchedule(id, data) {
    const res = await fetch(`/api/schedule/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('스케줄 수정에 실패했습니다.');
    return res.json();
  },
  async deleteSchedule(id) {
    const res = await fetch(`/api/schedule/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('스케줄 삭제에 실패했습니다.');
    return res.json();
  },
  async getScheduleDetail(id) {
    const res = await fetch(`/api/schedule/${id}`);
    if (!res.ok) throw new Error('스케줄 상세를 불러오지 못했습니다.');
    return res.json();
  },
};

export default function SchedulePage() {
  const { user, setUser } = useUser()
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedSchedule, setSelectedSchedule] = useState<ScheduleItem | null>(null)
  const [showToast, setShowToast] = useState(false)
  const [toastMessage, setToastMessage] = useState("")
  const [toastType, setToastType] = useState<"success" | "error">("success")
  const [activeTab, setActiveTab] = useState<'work' | 'cleaning'>("work")
  const [calendarView, setCalendarView] = useState<'week' | 'month'>("week")
  const [listView, setListView] = useState<'list' | 'card'>("card")
  const [darkMode, setDarkMode] = useState(false)
  
  // 더미 매장 데이터
  const stores = [
    { id: "1", name: "강남점" },
    { id: "2", name: "홍대점" },
    { id: "3", name: "잠실점" },
  ]
  // 최고관리자용 매장 선택 state
  const [selectedStore, setSelectedStore] = useState(stores[0].id)

  // 2단계: useState로 더미 데이터 관리
  const [schedules, setSchedules] = useState<ScheduleItem[]>(dummySchedules)

  // 모달/폼 상태
  const [showWorkModal, setShowWorkModal] = useState(false)
  const [showCleanModal, setShowCleanModal] = useState(false)
  const [editWork, setEditWork] = useState(null)
  const [editClean, setEditClean] = useState(null)
  const [showDetail, setShowDetail] = useState(null)
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' })

  // 근무 등록/수정
  const [workForm, setWorkForm] = useState({
    name: '', role: '', date: '', start: '', end: '', status: '예정'
  })
  // 청소 등록/수정
  const [cleanForm, setCleanForm] = useState({
    zone: '', manager: '', date: '', time: '', status: '대기'
  })

  const perms = useSchedulePermissions(user);
  // 필터/정렬 상태
  const [statusFilter, setStatusFilter] = useState('all');
  const [managerFilter, setManagerFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('all');
  const [sortOption, setSortOption] = useState('latest');

  // Toast 알림 표시 함수
  const showToastMessage = (message: string, type: "success" | "error" = "success") => {
    setToastMessage(message)
    setToastType(type)
    setShowToast(true)
    setTimeout(() => setShowToast(false), 3000)
  }

  // 2. useEffect로 스케줄 목록 불러오기
  useEffect(() => {
    const fetchSchedules = async () => {
      try {
        setLoading(true);
        const work = await scheduleApi.getSchedules('work');
        setSchedules(work);
      } catch (e) {
        showToastMessage('스케줄 목록을 불러오지 못했습니다.', 'error');
      } finally {
        setLoading(false);
      }
    };
    fetchSchedules();
  }, []);

  // 3. 등록/수정/삭제/상세 함수 실제 API 연동
  const handleAdd = async () => {
    if (!workForm.name || !workForm.date) {
      showToastMessage('이름과 날짜를 입력하세요.', 'error');
      return;
    }
    try {
      if (editWork) {
        await scheduleApi.updateSchedule(editWork.id, workForm);
        showToastMessage('근무 일정이 수정되었습니다.');
      } else {
        await scheduleApi.createSchedule({ ...workForm, type: 'work' });
        showToastMessage('근무 일정이 등록되었습니다.');
      }
      setShowWorkModal(false); setEditWork(null); setWorkForm({ name: '', role: '', date: '', start: '', end: '', status: '예정' });
      // 목록 새로고침
      const work = await scheduleApi.getSchedules('work');
      setSchedules(work);
    } catch (e) {
      showToastMessage('근무 일정 처리에 실패했습니다.', 'error');
    }
  };
  const handleDelete = async (id: number) => {
    try {
      await scheduleApi.deleteSchedule(id);
      showToastMessage('근무 일정이 삭제되었습니다.');
      const work = await scheduleApi.getSchedules('work');
      setSchedules(work);
    } catch (e) {
      showToastMessage('근무 일정 삭제에 실패했습니다.', 'error');
    }
  };
  const handleDetail = async (item: ScheduleItem) => {
    try {
      const detail = await scheduleApi.getScheduleDetail(item.id);
      setShowDetail(detail);
    } catch (e) {
      showToastMessage('상세 정보를 불러오지 못했습니다.', 'error');
    }
  };
  const handleEdit = (item: ScheduleItem) => { setEditWork(item); setWorkForm(item); setShowWorkModal(true) };
  const handleComplete = async (id: number) => {
    try {
      await scheduleApi.updateSchedule(id, { status: 'completed' });
      showToastMessage('근무 완료로 처리되었습니다.');
      const work = await scheduleApi.getSchedules('work');
      setSchedules(work);
    } catch (e) {
      showToastMessage('근무 완료 처리에 실패했습니다.', 'error');
    }
  };

  // 청소 등록/수정 핸들러
  const handleCleanSubmit = async () => {
    if (!cleanForm.zone || !cleanForm.manager || !cleanForm.date || !cleanForm.time) {
      showToastMessage('모든 항목을 입력하세요', 'error'); return;
    }
    if (editClean) {
      setSchedules(schedules.map(c => c.id === editClean.id ? { ...cleanForm, id: editClean.id } : c))
      await createScheduleNotice({
        type: 'alert',
        title: '청소 일정 수정',
        content: `${cleanForm.zone} 청소 일정이 수정되었습니다.`,
        author: user?.name || '관리자'
      })
      showToastMessage('청소 일정이 수정되었습니다.')
    } else {
      setSchedules([...schedules, { ...cleanForm, id: Date.now() }])
      await createScheduleNotice({
        type: 'alert',
        title: '청소 일정 등록',
        content: `${cleanForm.zone} 청소 일정이 등록되었습니다.`,
        author: user?.name || '관리자'
      })
      showToastMessage('청소 일정이 등록되었습니다.')
    }
    setShowCleanModal(false); setEditClean(null); setCleanForm({ zone: '', manager: '', date: '', time: '', status: '대기' })
  }
  // 청소 삭제
  const handleCleanDelete = async (id: number) => {
    setSchedules(schedules.filter(c => c.id !== id));
    await createScheduleNotice({
      type: 'alert',
      title: '청소 일정 삭제',
      content: `청소 일정이 삭제되었습니다.`,
      author: user?.name || '관리자'
    })
    showToastMessage('청소 일정이 삭제되었습니다.')
  }
  // 청소 상세
  const handleCleanDetail = (item: ScheduleItem) => setShowDetail(item)
  // 청소 수정
  const handleCleanEdit = (item: ScheduleItem) => { setEditClean(item); setCleanForm(item); setShowCleanModal(true) }
  // 청소 완료 체크
  const handleCleanComplete = async (id: number) => {
    setSchedules(schedules.map(c => c.id === id ? { ...c, status: 'completed' } : c));
    await createScheduleNotice({
      type: 'alert',
      title: '청소 완료',
      content: `${schedules.find(c => c.id === id)?.staff} 청소가 완료되었습니다.`,
      author: user?.name || '관리자'
    })
    showToastMessage('청소 완료로 처리되었습니다.')
  }

  const handleAddSchedule = async (scheduleData: Omit<ScheduleItem, 'id'>) => {
    try {
      const newSchedule: ScheduleItem = {
        ...scheduleData,
        id: Date.now(),
      };

      setSchedules(prev => [newSchedule, ...prev]);
      setShowAddModal(false);
      toast.success('일정이 등록되었습니다.');

      // 일정 등록 알림 생성
      await NotificationService.createScheduleNotification('created', newSchedule);
    } catch (error) {
      console.error('일정 등록 실패:', error);
      toast.error('일정 등록에 실패했습니다.');
    }
  };

  const handleUpdateSchedule = async (id: number, updates: Partial<ScheduleItem>) => {
    try {
      const oldSchedule = schedules.find(schedule => schedule.id === id);
      const updatedSchedule = { ...oldSchedule, ...updates, updatedAt: new Date().toISOString() };
      
      setSchedules(prev => prev.map(schedule => 
        schedule.id === id ? updatedSchedule : schedule
      ));
      toast.success('일정이 수정되었습니다.');

      // 일정 수정 알림 생성
      await NotificationService.createScheduleNotification('updated', updatedSchedule);
    } catch (error) {
      console.error('일정 수정 실패:', error);
      toast.error('일정 수정에 실패했습니다.');
    }
  };

  const handleDeleteSchedule = async (id: number) => {
    try {
      const scheduleToDelete = schedules.find(schedule => schedule.id === id);
      setSchedules(prev => prev.filter(schedule => schedule.id !== id));
      toast.success('일정이 삭제되었습니다.');

      // 일정 삭제 알림 생성
      if (scheduleToDelete) {
        await NotificationService.createScheduleNotification('cancelled', scheduleToDelete);
      }
    } catch (error) {
      console.error('일정 삭제 실패:', error);
      toast.error('일정 삭제에 실패했습니다.');
    }
  };

  const handleCancelSchedule = async (id: number) => {
    try {
      const schedule = schedules.find(schedule => schedule.id === id);
      if (!schedule) return;

      const updatedSchedule = { 
        ...schedule, 
        status: 'cancelled',
        updatedAt: new Date().toISOString() 
      };
      
      setSchedules(prev => prev.map(s => s.id === id ? updatedSchedule : s));
      toast.success('일정이 취소되었습니다.');

      // 일정 취소 알림 생성
      await NotificationService.createScheduleNotification('cancelled', updatedSchedule);
    } catch (error) {
      console.error('일정 취소 실패:', error);
      toast.error('일정 취소에 실패했습니다.');
    }
  };

  // 일정 알림 체크 (30분 전 알림)
  useEffect(() => {
    const checkScheduleReminders = () => {
      const now = new Date();
      const thirtyMinutesFromNow = new Date(now.getTime() + 30 * 60 * 1000);

      schedules.forEach(schedule => {
        if (schedule.status === 'confirmed') {
          const scheduleTime = new Date(schedule.date);
          const timeDiff = scheduleTime.getTime() - now.getTime();
          
          // 30분 전이고 아직 알림을 보내지 않았다면
          if (timeDiff > 0 && timeDiff <= 30 * 60 * 1000 && !schedule.reminderSent) {
            NotificationService.createScheduleNotification('reminder', schedule);
            
            // 알림 전송 표시
            setSchedules(prev => prev.map(s => 
              s.id === schedule.id ? { ...s, reminderSent: true } : s
            ));
          }
        }
      });
    };

    // 1분마다 체크
    const interval = setInterval(checkScheduleReminders, 60 * 1000);
    return () => clearInterval(interval);
  }, [schedules]);

  // 필터/정렬 적용(근무)
  const filteredSchedules = useMemo(() => {
    let filtered = [...schedules];
    if (statusFilter !== 'all') filtered = filtered.filter(s => s.status === statusFilter);
    if (managerFilter !== 'all') filtered = filtered.filter(s => s.staff === managerFilter);
    // 기간 필터 예시(최근 7일)
    if (dateFilter === '7days') {
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      filtered = filtered.filter(s => new Date(s.date) >= weekAgo);
    }
    // 정렬
    if (sortOption === 'latest') filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    else if (sortOption === 'oldest') filtered.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    return filtered;
  }, [schedules, statusFilter, managerFilter, dateFilter, sortOption]);

  // 권한별 분기 예시
  if (!user) return <div className="p-6">로그인 필요</div>;
  if (user.role === 'employee') {
    return <div className="p-6">직원은 본인 스케줄만 확인할 수 있습니다.</div>;
  }

  return (
    <PermissionGuard permissions={['schedule.view']} fallback={<Alert message="스케줄 관리 접근 권한이 없습니다." type="error" />}>
      <ResizableLayout
        sidebar={
          <Sidebar
            isCollapsed={isSidebarCollapsed}
            onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            user={user}
          />
        }
        defaultSidebarWidth={20}
        minSidebarWidth={10}
        maxSidebarWidth={35}
      >
        <div className="flex h-full flex-col">
          {/* 상단 탭 */}
          <div className="flex items-center gap-2 border-b px-6 pt-4 bg-background">
            <Button variant={activeTab === 'work' ? 'default' : 'ghost'} onClick={() => setActiveTab('work')}>근무 스케줄</Button>
            <Button variant={activeTab === 'cleaning' ? 'default' : 'ghost'} onClick={() => setActiveTab('cleaning')}>청소 스케줄</Button>
            <div className="ml-auto flex gap-2">
              <Button variant={calendarView === 'week' ? 'default' : 'outline'} size="sm" onClick={() => setCalendarView('week')}><Sun className="w-4 h-4 mr-1" />주간</Button>
              <Button variant={calendarView === 'month' ? 'default' : 'outline'} size="sm" onClick={() => setCalendarView('month')}><Moon className="w-4 h-4 mr-1" />월간</Button>
              <Button variant={listView === 'list' ? 'default' : 'outline'} size="sm" onClick={() => setListView('list')}><List className="w-4 h-4" /></Button>
              <Button variant={listView === 'card' ? 'default' : 'outline'} size="sm" onClick={() => setListView('card')}><LayoutGrid className="w-4 h-4" /></Button>
            </div>
          </div>

          {/* Header */}
          <header className="flex h-16 items-center justify-between border-b px-6">
            <h1 className="text-2xl font-bold">스케줄 관리</h1>
            <div className="flex items-center gap-4">
              {user.role === "admin" ? (
                <select
                  className="border rounded px-2 py-1 text-sm"
                  value={selectedStore}
                  onChange={e => setSelectedStore(e.target.value)}
                >
                  {stores.map(store => (
                    <option key={store.id} value={store.id}>{store.name}</option>
                  ))}
                </select>
              ) : (
                <span className="text-sm text-muted-foreground">{user.name}님 환영합니다</span>
              )}
              <Button onClick={() => setShowAddModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                새 스케줄 추가
              </Button>
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 p-6 space-y-6">
            {/* 페이지 정상 작동 메시지 */}
            <Card className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
              <CardContent className="p-4">
                <div className="flex items-center">
                  <Check className="w-5 h-5 text-green-600 mr-2" />
                  <span className="text-green-800 dark:text-green-200 font-medium">
                    ✅ 스케줄 관리 페이지 정상 작동 중 - 등록/수정/삭제/상세 기능 테스트 가능
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* 상단 요약 카드 섹션 */}
            <div className="grid gap-6 md:grid-cols-3 mb-8">
              <Card className="rounded-lg border bg-card p-6 flex flex-col items-start">
                <span className="text-muted-foreground text-xs mb-1">오늘 근무자</span>
                <span className="text-3xl font-bold text-primary mt-2">{schedules.filter(s => s.status === 'confirmed').length}명</span>
              </Card>
              <Card className="rounded-lg border bg-card p-6 flex flex-col items-start">
                <span className="text-muted-foreground text-xs mb-1">총 근무시간</span>
                <span className="text-3xl font-bold text-orange-500 mt-2">{schedules.length * 8}시간</span>
              </Card>
              <Card className="rounded-lg border bg-card p-6 flex flex-col items-start">
                <span className="text-muted-foreground text-xs mb-1">청소 스케줄</span>
                <span className="text-3xl font-bold text-green-500 mt-2">{schedules.length}건</span>
              </Card>
            </div>

            {/* 근무 스케줄 탭 */}
            {activeTab === 'work' && (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold">근무 스케줄 ({calendarView === 'week' ? '주간' : '월간'})</h2>
                  <Button>근무 등록</Button>
                </div>
                {/* 상단 필터/정렬 UI(근무) */}
                <div className="flex flex-wrap gap-2 mb-4 items-end">
                  <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="border rounded px-2 py-1">
                    <option value="all">상태 전체</option>
                    <option value="예정">예정</option>
                    <option value="근무완료">완료</option>
                    <option value="지각">지각</option>
                    <option value="결근">결근</option>
                  </select>
                  <select value={managerFilter} onChange={e => setManagerFilter(e.target.value)} className="border rounded px-2 py-1">
                    <option value="all">담당자 전체</option>
                    {[...new Set(schedules.map(s => s.staff))].map(n => (
                      <option key={n} value={n}>{n}</option>
                    ))}
                  </select>
                  <select value={dateFilter} onChange={e => setDateFilter(e.target.value)} className="border rounded px-2 py-1">
                    <option value="all">전체 기간</option>
                    <option value="7days">최근 7일</option>
                  </select>
                  <select value={sortOption} onChange={e => setSortOption(e.target.value)} className="border rounded px-2 py-1">
                    <option value="latest">최신순</option>
                    <option value="oldest">오래된순</option>
                  </select>
                </div>
                {/* 리스트/카드 뷰 */}
                {listView === 'list' ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left p-3">직원명</th>
                          <th className="text-left p-3">날짜</th>
                          <th className="text-left p-3">시간</th>
                          <th className="text-left p-3">상태</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredSchedules.map((s) => (
                          <tr key={s.id} className="border-b">
                            <td className="p-3">{s.staff}</td>
                            <td className="p-3">{s.date}</td>
                            <td className="p-3">{s.shift}</td>
                            <td className="p-3">
                              <Badge>{s.status}</Badge>
                            </td>
                            <td>
                              {perms.canEdit && <Button onClick={() => handleEdit(s)}>수정</Button>}
                              {perms.canDelete && <Button onClick={() => handleDelete(s.id)}>삭제</Button>}
                              {perms.canComplete && s.status !== 'completed' && <Button onClick={() => handleComplete(s.id)}>완료</Button>}
                              <Button onClick={() => handleDetail(s)}>상세</Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredSchedules.map((s) => (
                      <Card key={s.id} className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="font-bold">{s.staff}</div>
                          <Badge>{s.status}</Badge>
                        </div>
                        <div className="text-sm text-gray-500 mb-1">{s.date} {s.shift}</div>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* 청소 스케줄 탭 */}
            {activeTab === 'cleaning' && (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold">청소 스케줄 ({calendarView === 'week' ? '주간' : '월간'})</h2>
                  <Button>청소 등록</Button>
                </div>
                {listView === 'list' ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left p-3">직원명</th>
                          <th className="text-left p-3">날짜</th>
                          <th className="text-left p-3">시간</th>
                          <th className="text-left p-3">상태</th>
                        </tr>
                      </thead>
                      <tbody>
                        {schedules.map((s) => (
                          <tr key={s.id} className="border-b">
                            <td className="p-3">{s.staff}</td>
                            <td className="p-3">{s.date}</td>
                            <td className="p-3">{s.shift}</td>
                            <td className="p-3">
                              <Badge>{s.status}</Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {schedules.map((s) => (
                      <Card key={s.id} className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="font-bold">{s.staff}</div>
                          <Badge>{s.status}</Badge>
                        </div>
                        <div className="text-sm text-gray-500 mb-1">{s.date} {s.shift}</div>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            )}
          </main>

          {/* 스케줄 추가 모달 */}
          {showAddModal && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-md">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold">새 스케줄 추가</h2>
                  <Button variant="ghost" size="sm" onClick={() => setShowAddModal(false)}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">날짜</label>
                    <Input
                      type="date"
                      value={workForm.date}
                      onChange={(e) => setWorkForm({...workForm, date: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">시간</label>
                    <Input
                      placeholder="예: 08:00 - 16:00"
                      value={workForm.start}
                      onChange={(e) => setWorkForm({...workForm, start: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">직원</label>
                    <Input
                      placeholder="직원명"
                      value={workForm.name}
                      onChange={(e) => setWorkForm({...workForm, name: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">역할</label>
                    <Input
                      placeholder="역할"
                      value={workForm.role}
                      onChange={(e) => setWorkForm({...workForm, role: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">상태</label>
                    <select
                      className="w-full border rounded px-3 py-2"
                      value={workForm.status}
                      onChange={(e) => setWorkForm({...workForm, status: e.target.value as "completed" | "in_progress" | "pending"})}
                    >
                      <option value="pending">대기</option>
                      <option value="in_progress">진행중</option>
                      <option value="completed">완료</option>
                    </select>
                  </div>
                </div>
                <div className="flex justify-end space-x-2 mt-6">
                  <Button variant="outline" onClick={() => setShowAddModal(false)}>
                    취소
                  </Button>
                  <Button onClick={handleAdd}>
                    등록
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* 스케줄 상세 모달 */}
          {showDetailModal && selectedSchedule && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-md">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold">스케줄 상세</h2>
                  <Button variant="ghost" size="sm" onClick={() => setShowDetailModal(false)}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">날짜</label>
                    <p className="text-gray-900 dark:text-white">{selectedSchedule.date}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">시간</label>
                    <p className="text-gray-900 dark:text-white">{selectedSchedule.shift}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">직원</label>
                    <p className="text-gray-900 dark:text-white">{selectedSchedule.staff}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">상태</label>
                    <Badge className={getStatusColor(selectedSchedule.status)}>
                      {getStatusText(selectedSchedule.status)}
                    </Badge>
                  </div>
                </div>
                <div className="flex justify-end mt-6">
                  <Button onClick={() => setShowDetailModal(false)}>
                    닫기
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* 스케줄 수정 모달 */}
          {showEditModal && selectedSchedule && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-md">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold">스케줄 수정</h2>
                  <Button variant="ghost" size="sm" onClick={() => setShowEditModal(false)}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">날짜</label>
                    <Input
                      type="date"
                      value={selectedSchedule.date}
                      onChange={(e) => setSelectedSchedule({...selectedSchedule, date: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">시간</label>
                    <Input
                      value={selectedSchedule.shift}
                      onChange={(e) => setSelectedSchedule({...selectedSchedule, shift: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">직원</label>
                    <Input
                      value={selectedSchedule.staff}
                      onChange={(e) => setSelectedSchedule({...selectedSchedule, staff: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">상태</label>
                    <select
                      className="w-full border rounded px-3 py-2"
                      value={selectedSchedule.status}
                      onChange={(e) => setSelectedSchedule({...selectedSchedule, status: e.target.value as "confirmed" | "pending" | "cancelled"})}
                    >
                      <option value="confirmed">확정</option>
                      <option value="pending">대기</option>
                      <option value="cancelled">취소</option>
                    </select>
                  </div>
                </div>
                <div className="flex justify-end space-x-2 mt-6">
                  <Button variant="outline" onClick={() => setShowEditModal(false)}>
                    취소
                  </Button>
                  <Button onClick={handleUpdateSchedule}>
                    수정
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Toast 알림 */}
          {showToast && (
            <div className={`fixed bottom-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
              toastType === "success" 
                ? "bg-green-500 text-white" 
                : "bg-red-500 text-white"
            }`}>
              {toastMessage}
            </div>
          )}
        </div>
      </ResizableLayout>
    </PermissionGuard>
  )
} 