"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import {
  ChevronLeft,
  ChevronRight,
  Plus,
  Search,
  Settings,
  Menu,
  Clock,
  MapPin,
  Users,
  Calendar,
  Pause,
  Sparkles,
  X,
  User,
  Phone,
  Mail,
  Edit,
  Trash2,
  CheckCircle,
  AlertTriangle
} from "lucide-react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { useStaffStore, useScheduleStore } from '@/store';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function SchedulePage() {
  const router = useRouter();
  const [isLoaded, setIsLoaded] = useState(false);
  const [showAIPopup, setShowAIPopup] = useState(false);
  const [typedText, setTypedText] = useState("");
  const [isPlaying, setIsPlaying] = useState(false);
  const [showScheduleDialog, setShowScheduleDialog] = useState(false);
  const [selectedCellDate, setSelectedCellDate] = useState<string>("");
  const [scheduleForm, setScheduleForm] = useState({
    staff_id: "",
    staff_name: "",
    startTime: "09:00",
    endTime: "17:00",
    location: "홀",
    memo: "",
  });
  const [events, setEvents] = useState<any[]>([]);

  // Store에서 데이터 가져오기
  const { 
    staffMembers, 
    loading: staffLoading, 
    fetchStaffData 
  } = useStaffStore();

  const { 
    schedules, 
    loading: scheduleLoading, 
    fetchSchedules,
    createSchedule 
  } = useScheduleStore();

  useEffect(() => {
    setIsLoaded(true);
    fetchStaffData('schedule');
    fetchSchedules();
    const popupTimer = setTimeout(() => {
      setShowAIPopup(true);
    }, 3000);
    return () => clearTimeout(popupTimer);
  }, []);

  // 직원 데이터 변경 이벤트 리스너
  useEffect(() => {
    const handleStaffDataUpdate = () => {
      console.log('스케줄: 직원 데이터 업데이트 감지');
      fetchStaffData('schedule');
    };

    window.addEventListener('staffDataUpdated', handleStaffDataUpdate);
    return () => window.removeEventListener('staffDataUpdated', handleStaffDataUpdate);
  }, []);

  useEffect(() => {
    if (showAIPopup) {
      const text = "이번 주 직원 스케줄이 완료되었습니다. 추가 근무 신청이 3건 있습니다.";
      let i = 0;
      const typingInterval = setInterval(() => {
        if (i < text.length) {
          setTypedText((prev) => prev + text.charAt(i));
          i++;
        } else {
          clearInterval(typingInterval);
        }
      }, 50);
      return () => clearInterval(typingInterval);
    }
  }, [showAIPopup]);

  const [currentView, setCurrentView] = useState<"daily" | "weekly" | "monthly">("weekly");
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedEvent, setSelectedEvent] = useState<any>(null);

  const handleEventClick = (event: any) => {
    setSelectedEvent(event);
  };

  const calculateEventStyle = (startTime: string, endTime: string) => {
    const start = parseInt(startTime.split(":")[0]);
    const end = parseInt(endTime.split(":")[0]);
    const duration = end - start;
    const top = (start - 8) * 60;
    const height = duration * 60;
    return {
      top: `${top}px`,
      height: `${height}px`,
    };
  };

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  const days = ["월", "화", "수", "목", "금", "토", "일"];

  const getCurrentViewTitle = () => {
    const options = { year: 'numeric', month: 'long' } as const;
    const monthYear = currentDate.toLocaleDateString('ko-KR', options);
    
    switch (currentView) {
      case "daily":
        return `${currentDate.getDate()}일 ${monthYear}`;
      case "weekly":
        const weekStart = new Date(currentDate);
        weekStart.setDate(currentDate.getDate() - currentDate.getDay() + 1);
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekStart.getDate() + 6);
        return `${weekStart.getDate()}일 - ${weekEnd.getDate()}일 ${monthYear}`;
      case "monthly":
        return monthYear;
      default:
        return monthYear;
    }
  };

  const renderDailyView = () => (
    <div className="space-y-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold mb-4">일간 스케줄</h3>
        <div className="flex justify-between items-center mb-4">
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {currentDate.toLocaleDateString('ko-KR', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric',
              weekday: 'long'
            })}
          </span>
          <button
            onClick={() => openScheduleDialog(currentDate.toISOString().split('T')[0])}
            className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors flex items-center gap-1"
          >
            <Plus className="h-3 w-3" />
            스케줄 추가
          </button>
        </div>
        <div className="space-y-4">
          {events
            .filter(event => {
              const eventDate = new Date(event.date);
              return eventDate.toDateString() === currentDate.toDateString();
            })
            .map(event => (
              <div key={event.id} className="flex items-center space-x-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className={`w-4 h-4 rounded-full ${event.color}`}></div>
                <div className="flex-1">
                  <h4 className="font-medium">{event.title}</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {event.startTime} - {event.endTime} • {event.location}
                  </p>
                </div>
                <button
                  onClick={() => handleEventClick(event)}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  상세보기
                </button>
              </div>
            ))}
          {events.filter(event => {
            const eventDate = new Date(event.date);
            return eventDate.toDateString() === currentDate.toDateString();
          }).length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Calendar className="h-12 w-12 mx-auto mb-2 text-gray-300" />
              <p>등록된 스케줄이 없습니다.</p>
              <button
                onClick={() => openScheduleDialog(currentDate.toISOString().split('T')[0])}
                className="mt-2 text-blue-600 hover:text-blue-800 text-sm"
              >
                첫 번째 스케줄을 등록해보세요
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const openScheduleDialog = (date: string) => {
    setSelectedCellDate(date);
    setShowScheduleDialog(true);
  };

  const handleScheduleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setScheduleForm({ ...scheduleForm, [e.target.name]: e.target.value });
  };

  const handleStaffSelect = (staffId: string) => {
    const selectedStaff = staffMembers.find(staff => staff.id.toString() === staffId);
    setScheduleForm({
      ...scheduleForm,
      staff_id: staffId,
      staff_name: selectedStaff ? (selectedStaff.name || selectedStaff.username) : "",
    });
  };

  const handleLocationSelect = (location: string) => {
    setScheduleForm({ ...scheduleForm, location });
  };

  const handleScheduleSubmit = async () => {
    if (!scheduleForm.staff_id || !scheduleForm.startTime || !scheduleForm.endTime) {
      toast.error("필수 정보를 모두 입력해주세요.");
      return;
    }
    const staff = staffMembers.find(s => s.id.toString() === scheduleForm.staff_id);
    if (!staff) {
      toast.error("직원 목록이 없습니다. 직원 등록 후 이용해주세요.");
      return;
    }
    try {
      const newSchedule = {
        id: Date.now(),
        title: `${staff.name || staff.username} (${scheduleForm.location})`,
        startTime: scheduleForm.startTime,
        endTime: scheduleForm.endTime,
        color: getRandomColor(),
        day: new Date(selectedCellDate).getDay() || 7,
        date: selectedCellDate,
        description: scheduleForm.memo || `${scheduleForm.location} 근무`,
        location: scheduleForm.location,
        attendees: [staff.name || staff.username],
        organizer: "매니저",
        position: staff.position || "",
        phone: staff.phone || "",
      };
      setEvents(prev => [...prev, newSchedule]);
      toast.success("스케줄이 등록되었습니다.");
      setShowScheduleDialog(false);
      setScheduleForm({
        staff_id: "",
        staff_name: "",
        startTime: "09:00",
        endTime: "17:00",
        location: "홀",
        memo: "",
      });
    } catch (error) {
      toast.error("스케줄 등록 중 오류가 발생했습니다.");
    }
  };

  const getRandomColor = () => {
    const colors = [
      "bg-blue-500", "bg-green-500", "bg-purple-500", "bg-yellow-500", 
      "bg-indigo-500", "bg-pink-500", "bg-teal-500", "bg-cyan-500",
      "bg-blue-400", "bg-green-400", "bg-purple-400", "bg-yellow-400"
    ];
    return colors[Math.floor(Math.random() * colors.length)];
  };

  const renderWeeklyView = () => (
    <div className="space-y-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold mb-4">주간 스케줄</h3>
        <div className="grid grid-cols-7 gap-4">
          {days.map((day, dayIndex) => (
            <div key={day} className="space-y-2">
              <div className="text-center font-medium text-sm text-gray-600 dark:text-gray-400">
                {day}
              </div>
              <div className="space-y-1">
                <div
                  className="min-h-[40px] bg-gray-100 dark:bg-gray-700 rounded cursor-pointer flex items-center justify-center text-xs text-gray-500"
                  onClick={() => openScheduleDialog(/* 날짜 계산 로직 필요 */ new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate() + dayIndex).toISOString().split('T')[0])}
                >
                  + 스케줄 등록
                </div>
                {events
                  .filter(event => event.day === dayIndex + 1)
                  .map(event => (
                    <div
                      key={event.id}
                      onClick={() => handleEventClick(event)}
                      className={`p-2 rounded text-xs text-white cursor-pointer ${event.color}`}
                    >
                      <div className="font-medium truncate">{event.title}</div>
                      <div className="text-xs opacity-90">
                        {event.startTime} - {event.endTime}
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderMonthlyView = () => (
    <div className="space-y-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold mb-4">월간 스케줄</h3>
        <div className="grid grid-cols-7 gap-1">
          {days.map(day => (
            <div key={day} className="text-center font-medium text-sm text-gray-600 dark:text-gray-400 p-2">
              {day}
            </div>
          ))}
          {Array.from({ length: 35 }, (_, i) => {
            const dayEvents = events.filter(event => {
              const eventDate = new Date(event.date);
              return eventDate.getDate() === i + 1;
            });
            
            // 현재 월의 날짜 계산
            const year = currentDate.getFullYear();
            const month = currentDate.getMonth();
            const firstDay = new Date(year, month, 1);
            const lastDay = new Date(year, month + 1, 0);
            const startDate = new Date(firstDay);
            startDate.setDate(startDate.getDate() - firstDay.getDay());
            
            const currentDayDate = new Date(startDate);
            currentDayDate.setDate(startDate.getDate() + i);
            const isCurrentMonth = currentDayDate.getMonth() === month;
            const dateString = currentDayDate.toISOString().split('T')[0];
            
            return (
              <div 
                key={i} 
                className={`min-h-[80px] p-1 border border-gray-200 dark:border-gray-600 ${
                  isCurrentMonth ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-900'
                }`}
                onClick={() => isCurrentMonth && openScheduleDialog(dateString)}
              >
                <div className={`text-xs mb-1 ${isCurrentMonth ? 'text-gray-900 dark:text-white' : 'text-gray-400'}`}>
                  {currentDayDate.getDate()}
                </div>
                <div className="space-y-1">
                  {dayEvents.slice(0, 2).map(event => (
                    <div
                      key={event.id}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEventClick(event);
                      }}
                      className={`p-1 rounded text-xs text-white cursor-pointer ${event.color}`}
                    >
                      <div className="truncate">{event.title}</div>
                    </div>
                  ))}
                  {dayEvents.length > 2 && (
                    <div className="text-xs text-gray-500 text-center">
                      +{dayEvents.length - 2}개 더
                    </div>
                  )}
                  {isCurrentMonth && dayEvents.length === 0 && (
                    <div className="text-xs text-gray-400 text-center cursor-pointer hover:text-blue-500">
                      + 등록
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );

  // 등록 다이얼로그 개선
  const renderScheduleDialog = () => (
    <Dialog open={showScheduleDialog} onOpenChange={setShowScheduleDialog}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>스케줄 등록</DialogTitle>
          <DialogDescription>
            새로운 근무 스케줄을 추가합니다. 직원, 날짜, 시간을 선택해주세요.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          {staffMembers.length === 0 ? (
            <div className="text-red-500 text-center py-8">
              등록 가능한 직원이 없습니다.<br />
              먼저 직원 관리 페이지에서 직원을 등록/승인해 주세요.
            </div>
          ) : (
            <>
              <div>
                <Label>직원 선택</Label>
                <Select value={scheduleForm.staff_id} onValueChange={handleStaffSelect}>
                  <SelectTrigger>
                    <SelectValue placeholder="직원을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    {staffMembers.map((staff) => (
                      <SelectItem key={staff.id} value={staff.id.toString()}>
                        {staff.name || staff.username} ({staff.position})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="startTime">시작 시간</Label>
                  <Input
                    name="startTime"
                    type="time"
                    value={scheduleForm.startTime}
                    onChange={handleScheduleFormChange}
                  />
                </div>
                <div>
                  <Label htmlFor="endTime">종료 시간</Label>
                  <Input
                    name="endTime"
                    type="time"
                    value={scheduleForm.endTime}
                    onChange={handleScheduleFormChange}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="location">근무 위치</Label>
                <Select value={scheduleForm.location} onValueChange={handleLocationSelect}>
                  <SelectTrigger>
                    <SelectValue placeholder="위치를 선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="홀">홀</SelectItem>
                    <SelectItem value="주방">주방</SelectItem>
                    <SelectItem value="카운터">카운터</SelectItem>
                    <SelectItem value="배달">배달</SelectItem>
                    <SelectItem value="청소">청소</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="memo">메모</Label>
                <Textarea
                  name="memo"
                  placeholder="추가 사항을 입력하세요"
                  value={scheduleForm.memo}
                  onChange={handleScheduleFormChange}
                  rows={3}
                />
              </div>
            </>
          )}
          <div className="flex justify-end space-x-2 pt-4">
            <Button variant="outline" onClick={() => setShowScheduleDialog(false)}>
              취소
            </Button>
            <Button onClick={handleScheduleSubmit} disabled={staffMembers.length === 0}>
              등록
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );

  // 더미 데이터
  const scheduleData = {
    today: "2024-01-15",
    totalShifts: 28,
    completedShifts: 25,
    pendingShifts: 3,
    schedules: [
      {
        id: 1,
        employeeName: "김철수",
        position: "매니저",
        date: "2024-01-15",
        startTime: "09:00",
        endTime: "18:00",
        status: "completed",
        hours: 9
      },
      {
        id: 2,
        employeeName: "이영희",
        position: "직원",
        date: "2024-01-15",
        startTime: "10:00",
        endTime: "19:00",
        status: "completed",
        hours: 9
      },
      {
        id: 3,
        employeeName: "박민수",
        position: "직원",
        date: "2024-01-15",
        startTime: "11:00",
        endTime: "20:00",
        status: "in-progress",
        hours: 9
      },
      {
        id: 4,
        employeeName: "정수진",
        position: "직원",
        date: "2024-01-15",
        startTime: "12:00",
        endTime: "21:00",
        status: "pending",
        hours: 9
      },
      {
        id: 5,
        employeeName: "최동현",
        position: "직원",
        date: "2024-01-16",
        startTime: "09:00",
        endTime: "18:00",
        status: "pending",
        hours: 9
      }
    ],
    weeklyStats: [
      { day: "월", shifts: 25, completed: 24 },
      { day: "화", shifts: 26, completed: 25 },
      { day: "수", shifts: 24, completed: 23 },
      { day: "목", shifts: 27, completed: 26 },
      { day: "금", shifts: 28, completed: 25 },
      { day: "토", shifts: 30, completed: 28 },
      { day: "일", shifts: 22, completed: 20 }
    ]
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge variant="default" className="bg-green-600"><CheckCircle className="w-3 h-3 mr-1" />완료</Badge>;
      case "in-progress":
        return <Badge variant="secondary">진행 중</Badge>;
      case "pending":
        return <Badge variant="outline">대기</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getTimeStatus = (startTime: string, endTime: string) => {
    const now = new Date();
    const currentTime = now.getHours() * 60 + now.getMinutes();
    const startMinutes = parseInt(startTime.split(':')[0]) * 60 + parseInt(startTime.split(':')[1]);
    const endMinutes = parseInt(endTime.split(':')[0]) * 60 + parseInt(endTime.split(':')[1]);
    
    if (currentTime < startMinutes) return "upcoming";
    if (currentTime >= startMinutes && currentTime <= endMinutes) return "current";
    return "completed";
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">스케줄 관리</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            직원 스케줄을 일간, 주간, 월간으로 확인하고 관리하세요.
          </p>
        </div>

        {/* Controls */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="flex flex-col sm:flex-row gap-4 flex-1">
              {/* View Toggle */}
              <div className="flex bg-gray-200 dark:bg-gray-700 rounded-lg p-1">
                <button
                  onClick={() => setCurrentView("daily")}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === "daily"
                      ? "bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm"
                      : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                  }`}
                >
                  일간
                </button>
                <button
                  onClick={() => setCurrentView("weekly")}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === "weekly"
                      ? "bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm"
                      : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                  }`}
                >
                  주간
                </button>
                <button
                  onClick={() => setCurrentView("monthly")}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === "monthly"
                      ? "bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm"
                      : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                  }`}
                >
                  월간
                </button>
              </div>

              {/* Date Navigation */}
              <div className="flex items-center gap-4">
                <button
                  onClick={() => {
                    const newDate = new Date(currentDate);
                    if (currentView === "daily") {
                      newDate.setDate(currentDate.getDate() - 1);
                    } else if (currentView === "weekly") {
                      newDate.setDate(currentDate.getDate() - 7);
                    } else if (currentView === "monthly") {
                      newDate.setMonth(currentDate.getMonth() - 1);
                    }
                    setCurrentDate(newDate);
                  }}
                  className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  <ChevronLeft className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                </button>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {getCurrentViewTitle()}
                </span>
                <button
                  onClick={() => {
                    const newDate = new Date(currentDate);
                    if (currentView === "daily") {
                      newDate.setDate(currentDate.getDate() + 1);
                    } else if (currentView === "weekly") {
                      newDate.setDate(currentDate.getDate() + 7);
                    } else if (currentView === "monthly") {
                      newDate.setMonth(currentDate.getMonth() + 1);
                    }
                    setCurrentDate(newDate);
                  }}
                  className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  <ChevronRight className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Schedule Content */}
        {currentView === "daily" && renderDailyView()}
        {currentView === "weekly" && renderWeeklyView()}
        {currentView === "monthly" && renderMonthlyView()}

        {/* Stats */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">오늘 스케줄</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{scheduleData.totalShifts}</div>
              <p className="text-xs text-muted-foreground">
                {scheduleData.today}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">완료된 근무</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{scheduleData.completedShifts}</div>
              <p className="text-xs text-muted-foreground">
                정상 출근 완료
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">대기 중</CardTitle>
              <Clock className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{scheduleData.pendingShifts}</div>
              <p className="text-xs text-muted-foreground">
                아직 출근하지 않음
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">평균 근무시간</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">8.5시간</div>
              <p className="text-xs text-muted-foreground">
                일일 평균
              </p>
            </CardContent>
          </Card>
        </div>

        {/* 오늘의 스케줄 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Calendar className="h-5 w-5" />
              <span>오늘의 스케줄</span>
            </CardTitle>
            <CardDescription>
              {scheduleData.today} 근무 스케줄
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {scheduleData.schedules.filter(s => s.date === scheduleData.today).map((schedule) => (
                <div key={schedule.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                        {schedule.employeeName.charAt(0)}
                      </span>
                    </div>
                    <div>
                      <h3 className="font-medium">{schedule.employeeName}</h3>
                      <p className="text-sm text-muted-foreground">{schedule.position}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-6">
                    <div className="text-center">
                      <p className="font-medium">{schedule.startTime} - {schedule.endTime}</p>
                      <p className="text-sm text-muted-foreground">{schedule.hours}시간</p>
                    </div>
                    {getStatusBadge(schedule.status)}
                    <div className="flex items-center space-x-2">
                      <Button variant="outline" size="sm">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 주간 통계 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>주간 출근 현황</CardTitle>
              <CardDescription>
                이번 주 일별 출근 완료율
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {scheduleData.weeklyStats.map((day) => (
                  <div key={day.day} className="flex items-center justify-between">
                    <span className="text-sm font-medium">{day.day}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{width: `${(day.completed / day.shifts) * 100}%`}}
                        ></div>
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {day.completed}/{day.shifts}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>시간대별 근무 현황</CardTitle>
              <CardDescription>
                오늘 시간대별 출근 직원 수
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">오전 (09:00-12:00)</span>
                  <Badge variant="default" className="bg-blue-600">8명</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">오후 (12:00-18:00)</span>
                  <Badge variant="default" className="bg-green-600">12명</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">저녁 (18:00-21:00)</span>
                  <Badge variant="secondary">8명</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">야간 (21:00-24:00)</span>
                  <Badge variant="outline">0명</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 알림 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5" />
              <span>스케줄 알림</span>
            </CardTitle>
            <CardDescription>
              주의가 필요한 스케줄 관련 알림
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                <AlertTriangle className="h-4 w-4 text-yellow-600" />
                <div className="flex-1">
                  <p className="font-medium text-sm">정수진 직원 출근 지연</p>
                  <p className="text-xs text-muted-foreground">예정: 12:00, 현재: 12:30</p>
                </div>
                <Badge variant="destructive">지연</Badge>
              </div>
              <div className="flex items-center space-x-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <CheckCircle className="h-4 w-4 text-blue-600" />
                <div className="flex-1">
                  <p className="font-medium text-sm">내일 스케줄 등록 완료</p>
                  <p className="text-xs text-muted-foreground">2024-01-16 스케줄이 등록되었습니다</p>
                </div>
                <Badge variant="secondary">완료</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Popup */}
      {showAIPopup && (
        <div className="fixed bottom-6 right-6 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <Sparkles className="h-4 w-4 text-white" />
            </div>
            <div className="flex-1">
              <p className="text-sm text-gray-900 dark:text-white mb-2">{typedText}</p>
              <div className="flex gap-2">
                <button className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors">
                  확인
                </button>
                <button
                  onClick={() => setShowAIPopup(false)}
                  className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-3 py-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                >
                  닫기
                </button>
              </div>
            </div>
            <button
              onClick={() => setShowAIPopup(false)}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Event Detail Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-96 max-w-[90vw]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {selectedEvent.title}
              </h3>
              <button
                onClick={() => setSelectedEvent(null)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <Clock className="h-4 w-4" />
                <span>
                  {selectedEvent.startTime} - {selectedEvent.endTime}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <MapPin className="h-4 w-4" />
                <span>{selectedEvent.location}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <User className="h-4 w-4" />
                <span>{selectedEvent.position}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <Phone className="h-4 w-4" />
                <span>{selectedEvent.phone}</span>
              </div>
              <p className="text-sm text-gray-700 dark:text-gray-300 mt-3">
                {selectedEvent.description}
              </p>
            </div>
            <div className="flex gap-2 mt-6">
              <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                수정
              </button>
              <button className="flex-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 py-2 px-4 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
                삭제
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 개선된 등록 다이얼로그 */}
      {renderScheduleDialog()}
    </div>
  );
} 