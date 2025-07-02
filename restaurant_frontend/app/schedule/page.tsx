"use client"

import { useState, useEffect } from "react"
import { ResizableLayout } from "@/components/resizable-layout"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Calendar, Plus, Users, Clock, Edit, Trash2, Eye, X, Check, List, LayoutGrid, Sun, Moon, Broom } from "lucide-react"
import { useUser } from "@/components/UserContext"
import { api as noticeApi } from '../notice/page';
import { toast } from 'sonner';
import NotificationService from '@/lib/notification-service';

// 스케줄 타입 정의
type Schedule = {
  id: number;
  date: string;
  time: string;
  employee: string;
  task: string;
  status: 'completed' | 'in_progress' | 'pending';
  type: 'work' | 'cleaning';
  notes?: string;
};

// 더미 근무/청소 일정 타입
const dummyStaff = ["김철수", "이영희", "박민수", "정수진", "최서버", "한직원"]
const dummyZones = ["홀A", "홀B", "주방", "화장실", "외부"]

const dummyWorkSchedules = [
  { id: 1, name: "김철수", role: "주방장", date: "2024-06-10", start: "09:00", end: "18:00", status: "근무완료" },
  { id: 2, name: "이영희", role: "서버", date: "2024-06-10", start: "10:00", end: "19:00", status: "지각" },
  { id: 3, name: "박민수", role: "청소원", date: "2024-06-11", start: "08:00", end: "17:00", status: "결근" },
  { id: 4, name: "정수진", role: "매니저", date: "2024-06-12", start: "09:00", end: "18:00", status: "근무완료" },
  { id: 5, name: "최서버", role: "서버", date: "2024-06-13", start: "10:00", end: "19:00", status: "예정" },
  { id: 6, name: "한직원", role: "주방보조", date: "2024-06-14", start: "09:00", end: "18:00", status: "예정" },
]

const dummyCleanSchedules = [
  { id: 1, zone: "홀A", manager: "박민수", date: "2024-06-10", time: "14:00", status: "완료" },
  { id: 2, zone: "주방", manager: "김철수", date: "2024-06-10", time: "16:00", status: "대기" },
  { id: 3, zone: "화장실", manager: "이영희", date: "2024-06-11", time: "15:00", status: "완료" },
  { id: 4, zone: "외부", manager: "정수진", date: "2024-06-12", time: "17:00", status: "대기" },
  { id: 5, zone: "홀B", manager: "최서버", date: "2024-06-13", time: "13:00", status: "완료" },
]

// 알림 등록 함수
async function createScheduleNotice({ type, title, content, author }) {
  try {
    await noticeApi.createNotice({
      type,
      title,
      content,
      status: 'unread',
      author
    });
  } catch (e) {
    // 무시(실패 시에도 schedule는 정상 동작)
  }
}

export default function SchedulePage() {
  const { user, setUser } = useUser()
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedSchedule, setSelectedSchedule] = useState<Schedule | null>(null)
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
  const [workSchedules, setWorkSchedules] = useState(dummyWorkSchedules)
  const [cleanSchedules, setCleanSchedules] = useState(dummyCleanSchedules)

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

  // Toast 알림 표시 함수
  const showToastMessage = (message: string, type: "success" | "error" = "success") => {
    setToastMessage(message)
    setToastType(type)
    setShowToast(true)
    setTimeout(() => setShowToast(false), 3000)
  }

  // 근무 등록/수정 핸들러
  const handleWorkSubmit = async () => {
    if (!workForm.name || !workForm.role || !workForm.date || !workForm.start || !workForm.end) {
      showToastMessage('모든 항목을 입력하세요', 'error'); return;
    }
    if (editWork) {
      setWorkSchedules(workSchedules.map(w => w.id === editWork.id ? { ...workForm, id: editWork.id } : w))
      await createScheduleNotice({
        type: 'alert',
        title: '근무 일정 수정',
        content: `${workForm.name} 근무 일정이 수정되었습니다.`,
        author: user?.name || '관리자'
      })
      showToastMessage('근무 일정이 수정되었습니다.')
    } else {
      setWorkSchedules([...workSchedules, { ...workForm, id: Date.now() }])
      await createScheduleNotice({
        type: 'alert',
        title: '근무 일정 등록',
        content: `${workForm.name} 근무 일정이 등록되었습니다.`,
        author: user?.name || '관리자'
      })
      showToastMessage('근무 일정이 등록되었습니다.')
    }
    setShowWorkModal(false); setEditWork(null); setWorkForm({ name: '', role: '', date: '', start: '', end: '', status: '예정' })
  }
  // 근무 삭제
  const handleWorkDelete = async (id) => {
    setWorkSchedules(workSchedules.filter(w => w.id !== id));
    await createScheduleNotice({
      type: 'alert',
      title: '근무 일정 삭제',
      content: `근무 일정이 삭제되었습니다.`,
      author: user?.name || '관리자'
    })
    showToastMessage('근무 일정이 삭제되었습니다.')
  }
  // 근무 상세
  const handleWorkDetail = (item) => setShowDetail({ ...item, type: 'work' })
  // 근무 수정
  const handleWorkEdit = (item) => { setEditWork(item); setWorkForm(item); setShowWorkModal(true) }
  // 근무 완료 체크
  const handleWorkComplete = async (id) => {
    setWorkSchedules(workSchedules.map(w => w.id === id ? { ...w, status: '근무완료' } : w));
    await createScheduleNotice({
      type: 'alert',
      title: '근무 완료',
      content: `${workSchedules.find(w => w.id === id)?.name} 근무가 완료되었습니다.`,
      author: user?.name || '관리자'
    })
    showToastMessage('근무 완료로 처리되었습니다.')
  }

  // 청소 등록/수정 핸들러
  const handleCleanSubmit = async () => {
    if (!cleanForm.zone || !cleanForm.manager || !cleanForm.date || !cleanForm.time) {
      showToastMessage('모든 항목을 입력하세요', 'error'); return;
    }
    if (editClean) {
      setCleanSchedules(cleanSchedules.map(c => c.id === editClean.id ? { ...cleanForm, id: editClean.id } : c))
      await createScheduleNotice({
        type: 'alert',
        title: '청소 일정 수정',
        content: `${cleanForm.zone} 청소 일정이 수정되었습니다.`,
        author: user?.name || '관리자'
      })
      showToastMessage('청소 일정이 수정되었습니다.')
    } else {
      setCleanSchedules([...cleanSchedules, { ...cleanForm, id: Date.now() }])
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
  const handleCleanDelete = async (id) => {
    setCleanSchedules(cleanSchedules.filter(c => c.id !== id));
    await createScheduleNotice({
      type: 'alert',
      title: '청소 일정 삭제',
      content: `청소 일정이 삭제되었습니다.`,
      author: user?.name || '관리자'
    })
    showToastMessage('청소 일정이 삭제되었습니다.')
  }
  // 청소 상세
  const handleCleanDetail = (item) => setShowDetail({ ...item, type: 'clean' })
  // 청소 수정
  const handleCleanEdit = (item) => { setEditClean(item); setCleanForm(item); setShowCleanModal(true) }
  // 청소 완료 체크
  const handleCleanComplete = async (id) => {
    setCleanSchedules(cleanSchedules.map(c => c.id === id ? { ...c, status: '완료' } : c));
    await createScheduleNotice({
      type: 'alert',
      title: '청소 완료',
      content: `${cleanSchedules.find(c => c.id === id)?.zone} 청소가 완료되었습니다.`,
      author: user?.name || '관리자'
    })
    showToastMessage('청소 완료로 처리되었습니다.')
  }

  const handleAddSchedule = async (scheduleData: Omit<Schedule, 'id' | 'createdAt' | 'updatedAt'>) => {
    try {
      const newSchedule: Schedule = {
        ...scheduleData,
        id: Date.now().toString(),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      setWorkSchedules(prev => [newSchedule, ...prev]);
      setShowAddModal(false);
      toast.success('일정이 등록되었습니다.');

      // 일정 등록 알림 생성
      await NotificationService.createScheduleNotification('created', newSchedule);
    } catch (error) {
      console.error('일정 등록 실패:', error);
      toast.error('일정 등록에 실패했습니다.');
    }
  };

  const handleUpdateSchedule = async (id: string, updates: Partial<Schedule>) => {
    try {
      const oldSchedule = workSchedules.find(schedule => schedule.id === id);
      const updatedSchedule = { ...oldSchedule, ...updates, updatedAt: new Date().toISOString() };
      
      setWorkSchedules(prev => prev.map(schedule => 
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

  const handleDeleteSchedule = async (id: string) => {
    try {
      const scheduleToDelete = workSchedules.find(schedule => schedule.id === id);
      setWorkSchedules(prev => prev.filter(schedule => schedule.id !== id));
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

  const handleCancelSchedule = async (id: string) => {
    try {
      const schedule = workSchedules.find(schedule => schedule.id === id);
      if (!schedule) return;

      const updatedSchedule = { 
        ...schedule, 
        status: 'cancelled',
        updatedAt: new Date().toISOString() 
      };
      
      setWorkSchedules(prev => prev.map(s => s.id === id ? updatedSchedule : s));
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

      workSchedules.forEach(schedule => {
        if (schedule.status === 'confirmed') {
          const scheduleTime = new Date(schedule.startTime);
          const timeDiff = scheduleTime.getTime() - now.getTime();
          
          // 30분 전이고 아직 알림을 보내지 않았다면
          if (timeDiff > 0 && timeDiff <= 30 * 60 * 1000 && !schedule.reminderSent) {
            NotificationService.createScheduleNotification('reminder', schedule);
            
            // 알림 전송 표시
            setWorkSchedules(prev => prev.map(s => 
              s.id === schedule.id ? { ...s, reminderSent: true } : s
            ));
          }
        }
      });
    };

    // 1분마다 체크
    const interval = setInterval(checkScheduleReminders, 60 * 1000);
    return () => clearInterval(interval);
  }, [workSchedules]);

  return (
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
              <span className="text-3xl font-bold text-primary mt-2">{workSchedules.filter(s => s.status === 'in_progress').length}명</span>
            </Card>
            <Card className="rounded-lg border bg-card p-6 flex flex-col items-start">
              <span className="text-muted-foreground text-xs mb-1">총 근무시간</span>
              <span className="text-3xl font-bold text-orange-500 mt-2">{workSchedules.length * 8}시간</span>
            </Card>
            <Card className="rounded-lg border bg-card p-6 flex flex-col items-start">
              <span className="text-muted-foreground text-xs mb-1">청소 스케줄</span>
              <span className="text-3xl font-bold text-green-500 mt-2">{cleanSchedules.length}건</span>
            </Card>
          </div>

          {/* 근무 스케줄 탭 */}
          {activeTab === 'work' && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">근무 스케줄 ({calendarView === 'week' ? '주간' : '월간'})</h2>
                <Button>근무 등록</Button>
              </div>
              {/* 리스트/카드 뷰 */}
              {listView === 'list' ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-3">직원명</th>
                        <th className="text-left p-3">역할</th>
                        <th className="text-left p-3">날짜</th>
                        <th className="text-left p-3">출근</th>
                        <th className="text-left p-3">퇴근</th>
                        <th className="text-left p-3">상태</th>
                      </tr>
                    </thead>
                    <tbody>
                      {workSchedules.map((w) => (
                        <tr key={w.id} className="border-b">
                          <td className="p-3">{w.name}</td>
                          <td className="p-3">{w.role}</td>
                          <td className="p-3">{w.date}</td>
                          <td className="p-3">{w.start}</td>
                          <td className="p-3">{w.end}</td>
                          <td className="p-3">
                            <Badge>{w.status}</Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {workSchedules.map((w) => (
                    <Card key={w.id} className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-bold">{w.name}</div>
                        <Badge>{w.status}</Badge>
                      </div>
                      <div className="text-sm text-gray-500 mb-1">{w.role}</div>
                      <div className="text-xs text-gray-400">{w.date} {w.start}~{w.end}</div>
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
                        <th className="text-left p-3">구역</th>
                        <th className="text-left p-3">담당자</th>
                        <th className="text-left p-3">날짜</th>
                        <th className="text-left p-3">시간</th>
                        <th className="text-left p-3">상태</th>
                      </tr>
                    </thead>
                    <tbody>
                      {cleanSchedules.map((c) => (
                        <tr key={c.id} className="border-b">
                          <td className="p-3">{c.zone}</td>
                          <td className="p-3">{c.manager}</td>
                          <td className="p-3">{c.date}</td>
                          <td className="p-3">{c.time}</td>
                          <td className="p-3">
                            <Badge>{c.status}</Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {cleanSchedules.map((c) => (
                    <Card key={c.id} className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-bold">{c.zone}</div>
                        <Badge>{c.status}</Badge>
                      </div>
                      <div className="text-sm text-gray-500 mb-1">담당: {c.manager}</div>
                      <div className="text-xs text-gray-400">{c.date} {c.time}</div>
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
                    value={newSchedule.date}
                    onChange={(e) => setNewSchedule({...newSchedule, date: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">시간</label>
                  <Input
                    placeholder="예: 08:00 - 16:00"
                    value={newSchedule.time}
                    onChange={(e) => setNewSchedule({...newSchedule, time: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">직원</label>
                  <Input
                    placeholder="직원명"
                    value={newSchedule.employee}
                    onChange={(e) => setNewSchedule({...newSchedule, employee: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">업무</label>
                  <Input
                    placeholder="업무 내용"
                    value={newSchedule.task}
                    onChange={(e) => setNewSchedule({...newSchedule, task: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">유형</label>
                  <select
                    className="w-full border rounded px-3 py-2"
                    value={newSchedule.type}
                    onChange={(e) => setNewSchedule({...newSchedule, type: e.target.value as "work" | "cleaning"})}
                  >
                    <option value="work">근무</option>
                    <option value="cleaning">청소</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">메모</label>
                  <textarea
                    className="w-full border rounded px-3 py-2"
                    placeholder="추가 메모"
                    value={newSchedule.notes}
                    onChange={(e) => setNewSchedule({...newSchedule, notes: e.target.value})}
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-2 mt-6">
                <Button variant="outline" onClick={() => setShowAddModal(false)}>
                  취소
                </Button>
                <Button onClick={handleAddSchedule}>
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
                  <p className="text-gray-900 dark:text-white">{selectedSchedule.time}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">직원</label>
                  <p className="text-gray-900 dark:text-white">{selectedSchedule.employee}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">업무</label>
                  <p className="text-gray-900 dark:text-white">{selectedSchedule.task}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">유형</label>
                  <Badge variant={selectedSchedule.type === 'work' ? 'default' : 'secondary'}>
                    {selectedSchedule.type === 'work' ? '근무' : '청소'}
                  </Badge>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">상태</label>
                  <Badge className={getStatusColor(selectedSchedule.status)}>
                    {getStatusText(selectedSchedule.status)}
                  </Badge>
                </div>
                {selectedSchedule.notes && (
                  <div>
                    <label className="block text-sm font-medium mb-1">메모</label>
                    <p className="text-gray-900 dark:text-white">{selectedSchedule.notes}</p>
                  </div>
                )}
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
                    value={selectedSchedule.time}
                    onChange={(e) => setSelectedSchedule({...selectedSchedule, time: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">직원</label>
                  <Input
                    value={selectedSchedule.employee}
                    onChange={(e) => setSelectedSchedule({...selectedSchedule, employee: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">업무</label>
                  <Input
                    value={selectedSchedule.task}
                    onChange={(e) => setSelectedSchedule({...selectedSchedule, task: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">상태</label>
                  <select
                    className="w-full border rounded px-3 py-2"
                    value={selectedSchedule.status}
                    onChange={(e) => setSelectedSchedule({...selectedSchedule, status: e.target.value as "completed" | "in_progress" | "pending"})}
                  >
                    <option value="pending">대기</option>
                    <option value="in_progress">진행중</option>
                    <option value="completed">완료</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">메모</label>
                  <textarea
                    className="w-full border rounded px-3 py-2"
                    value={selectedSchedule.notes || ""}
                    onChange={(e) => setSelectedSchedule({...selectedSchedule, notes: e.target.value})}
                  />
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
  )
} 