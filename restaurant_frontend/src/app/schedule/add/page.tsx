"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Calendar, Clock, User, MapPin, FileText, Save, X, AlertTriangle, CheckCircle, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';

interface Staff {
  id: number;
  name: string;
  position: string;
  phone: string;
  contract?: {
    workDays: string[];
    workHours: {
      start: string;
      end: string;
    };
  };
}

interface ScheduleForm {
  staff_id: number;
  date: string;
  start_time: string;
  end_time: string;
  type: string;
  location: string;
  memo: string;
}

interface ContractViolation {
  type: 'work_days' | 'work_hours' | 'overtime';
  message: string;
  severity: 'warning' | 'error';
}

export default function ScheduleAddPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [staffList, setStaffList] = useState<Staff[]>([]);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [showScheduleDialog, setShowScheduleDialog] = useState(false);
  const [contractViolations, setContractViolations] = useState<ContractViolation[]>([]);
  const [formData, setFormData] = useState<ScheduleForm>({
    staff_id: 0,
    date: new Date().toISOString().split('T')[0],
    start_time: "09:00",
    end_time: "17:00",
    type: "근무",
    location: "홀",
    memo: ""
  });

  // 더미 직원 데이터 (계약 정보 포함)
  const dummyStaff = [
    { 
      id: 1, 
      name: "김철수", 
      position: "주방장", 
      phone: "010-1234-5678",
      contract: {
        workDays: ["월", "화", "수", "목", "금"],
        workHours: { start: "09:00", end: "18:00" }
      }
    },
    { 
      id: 2, 
      name: "이영희", 
      position: "서빙", 
      phone: "010-2345-6789",
      contract: {
        workDays: ["월", "화", "수", "목", "금", "토"],
        workHours: { start: "10:00", end: "19:00" }
      }
    },
    { 
      id: 3, 
      name: "박민수", 
      position: "카운터", 
      phone: "010-3456-7890",
      contract: {
        workDays: ["월", "화", "수", "목", "금"],
        workHours: { start: "11:00", end: "20:00" }
      }
    },
    { 
      id: 4, 
      name: "최지영", 
      position: "서빙", 
      phone: "010-4567-8901",
      contract: {
        workDays: ["월", "화", "수", "목", "금", "토", "일"],
        workHours: { start: "12:00", end: "21:00" }
      }
    },
    { 
      id: 5, 
      name: "정현우", 
      position: "부주방장", 
      phone: "010-5678-9012",
      contract: {
        workDays: ["월", "화", "수", "목", "금"],
        workHours: { start: "08:00", end: "17:00" }
      }
    }
  ];

  useEffect(() => {
    setStaffList(dummyStaff);
  }, []);

  // 달력 생성 함수
  const generateCalendarDays = () => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const days = [];
    const currentDate = new Date(startDate);
    
    while (currentDate <= lastDay || days.length < 42) {
      days.push(new Date(currentDate));
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    return days;
  };

  // 날짜 클릭 핸들러
  const handleDateClick = (date: Date) => {
    const dateString = date.toISOString().split('T')[0];
    setSelectedDate(dateString);
    setFormData(prev => ({ ...prev, date: dateString }));
    setShowScheduleDialog(true);
  };

  // 계약 위반 검사
  const checkContractViolations = (staff: Staff, schedule: ScheduleForm): ContractViolation[] => {
    const violations: ContractViolation[] = [];
    
    if (!staff.contract) return violations;

    const scheduleDate = new Date(schedule.date);
    const dayOfWeek = ['일', '월', '화', '수', '목', '금', '토'][scheduleDate.getDay()];
    
    // 근무일 검사
    if (!staff.contract.workDays.includes(dayOfWeek)) {
      violations.push({
        type: 'work_days',
        message: `${staff.name}의 계약서에는 ${dayOfWeek}요일 근무가 포함되지 않습니다.`,
        severity: 'warning'
      });
    }

    // 근무시간 검사
    const contractStart = staff.contract.workHours.start;
    const contractEnd = staff.contract.workHours.end;
    
    if (schedule.start_time < contractStart) {
      violations.push({
        type: 'work_hours',
        message: `${staff.name}의 계약 시작시간(${contractStart})보다 일찍 시작합니다.`,
        severity: 'warning'
      });
    }
    
    if (schedule.end_time > contractEnd) {
      violations.push({
        type: 'work_hours',
        message: `${schedule.end_time > contractEnd ? '초과근무' : '계약 종료시간'} ${staff.name}의 계약 종료시간(${contractEnd})을 초과합니다.`,
        severity: 'error'
      });
    }

    // 근무시간 계산
    const startTime = new Date(`2000-01-01T${schedule.start_time}`);
    const endTime = new Date(`2000-01-01T${schedule.end_time}`);
    const workHours = (endTime.getTime() - startTime.getTime()) / (1000 * 60 * 60);
    
    if (workHours > 8) {
      violations.push({
        type: 'overtime',
        message: `${staff.name}의 근무시간이 8시간을 초과합니다 (${workHours.toFixed(1)}시간).`,
        severity: 'error'
      });
    }

    return violations;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // 직원이 선택되면 계약 위반 검사
    if (name === 'staff_id' && value) {
      const selectedStaff = staffList.find(staff => staff.id === Number(value));
      if (selectedStaff) {
        const violations = checkContractViolations(selectedStaff, {
          ...formData,
          staff_id: Number(value)
        });
        setContractViolations(violations);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch('/api/schedule', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          user_id: formData.staff_id,
          date: formData.date,
          start_time: formData.start_time,
          end_time: formData.end_time,
          type: "work",
          category: formData.type,
          memo: formData.memo,
          team: formData.location,
          branch_id: 1,
          manager_id: 1
        })
      });

      const result = await response.json();

      if (result.success) {
        alert("스케줄이 성공적으로 추가되었습니다.");
        setShowScheduleDialog(false);
        router.push('/schedule');
      } else {
        alert(result.message || "스케줄 추가 중 오류가 발생했습니다.");
      }
    } catch (error) {
      console.error('Error adding schedule:', error);
      alert("스케줄 추가 중 오류가 발생했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  const selectedStaff = staffList.find(staff => staff.id === formData.staff_id);
  const calendarDays = generateCalendarDays();
  const weekDays = ['일', '월', '화', '수', '목', '금', '토'];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <button
              onClick={() => router.back()}
              className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <ArrowLeft className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            </button>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">스케줄 추가</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            캘린더에서 날짜를 클릭하여 근무 스케줄을 추가하세요.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 캘린더 */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="h-5 w-5" />
                    {currentMonth.getFullYear()}년 {currentMonth.getMonth() + 1}월
                  </CardTitle>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))}
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))}
                    >
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {/* 요일 헤더 */}
                <div className="grid grid-cols-7 gap-1 mb-2">
                  {weekDays.map(day => (
                    <div key={day} className="p-2 text-center text-sm font-medium text-gray-500 dark:text-gray-400">
                      {day}
                    </div>
                  ))}
                </div>

                {/* 달력 그리드 */}
                <div className="grid grid-cols-7 gap-1">
                  {calendarDays.map((date, index) => {
                    const isCurrentMonth = date.getMonth() === currentMonth.getMonth();
                    const isToday = date.toDateString() === new Date().toDateString();
                    const isSelected = selectedDate === date.toISOString().split('T')[0];
                    
                    return (
                      <button
                        key={index}
                        onClick={() => handleDateClick(date)}
                        className={`
                          p-3 h-16 text-sm rounded-lg transition-colors
                          ${isCurrentMonth 
                            ? 'hover:bg-blue-50 dark:hover:bg-blue-900/20 cursor-pointer' 
                            : 'text-gray-300 dark:text-gray-600 cursor-not-allowed'
                          }
                          ${isToday ? 'bg-blue-100 dark:bg-blue-900/30 border-2 border-blue-500' : ''}
                          ${isSelected ? 'bg-blue-500 text-white' : ''}
                          ${!isCurrentMonth ? 'bg-gray-50 dark:bg-gray-800' : 'bg-white dark:bg-gray-700'}
                        `}
                        disabled={!isCurrentMonth}
                      >
                        <div className="text-left">
                          <div className={`font-medium ${isToday ? 'text-blue-600 dark:text-blue-400' : ''}`}>
                            {date.getDate()}
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 직원 목록 및 계약 정보 */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  직원 목록
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {staffList.map(staff => (
                    <div
                      key={staff.id}
                      className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                        formData.staff_id === staff.id
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                      }`}
                      onClick={() => {
                        setFormData(prev => ({ ...prev, staff_id: staff.id }));
                        const violations = checkContractViolations(staff, { ...formData, staff_id: staff.id });
                        setContractViolations(violations);
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white">
                            {staff.name}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {staff.position}
                          </div>
                        </div>
                        {formData.staff_id === staff.id && (
                          <CheckCircle className="h-5 w-5 text-blue-500" />
                        )}
                      </div>
                      {staff.contract && (
                        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                          <div>근무일: {staff.contract.workDays.join(', ')}</div>
                          <div>근무시간: {staff.contract.workHours.start} ~ {staff.contract.workHours.end}</div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* 계약 위반 알림 */}
            {contractViolations.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-orange-600 dark:text-orange-400">
                    <AlertTriangle className="h-5 w-5" />
                    계약 위반 알림
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {contractViolations.map((violation, index) => (
                      <div
                        key={index}
                        className={`p-3 rounded-lg border-l-4 ${
                          violation.severity === 'error'
                            ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                            : 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20'
                        }`}
                      >
                        <div className="text-sm text-gray-700 dark:text-gray-300">
                          {violation.message}
                        </div>
                        <Badge
                          variant={violation.severity === 'error' ? 'destructive' : 'secondary'}
                          className="mt-1"
                        >
                          {violation.severity === 'error' ? '심각' : '주의'}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* 스케줄 추가 다이얼로그 */}
        <Dialog open={showScheduleDialog} onOpenChange={setShowScheduleDialog}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>스케줄 추가</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* 선택된 직원 정보 */}
              {selectedStaff && (
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <div className="font-medium text-blue-900 dark:text-blue-100">
                    {selectedStaff.name} ({selectedStaff.position})
                  </div>
                  <div className="text-sm text-blue-700 dark:text-blue-300">
                    {selectedDate} • {formData.start_time} ~ {formData.end_time}
                  </div>
                </div>
              )}

              {/* 시간 설정 */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    시작 시간
                  </label>
                  <Input
                    type="time"
                    name="start_time"
                    value={formData.start_time}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    종료 시간
                  </label>
                  <Input
                    type="time"
                    name="end_time"
                    value={formData.end_time}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>

              {/* 근무 유형 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  근무 유형
                </label>
                <select
                  name="type"
                  value={formData.type}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="근무">일반 근무</option>
                  <option value="야근">야근</option>
                  <option value="휴일근무">휴일 근무</option>
                  <option value="대체근무">대체 근무</option>
                </select>
              </div>

              {/* 근무 위치 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  근무 위치
                </label>
                <select
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="홀">홀</option>
                  <option value="주방">주방</option>
                  <option value="카운터">카운터</option>
                  <option value="창고">창고</option>
                </select>
              </div>

              {/* 메모 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  메모
                </label>
                <Textarea
                  name="memo"
                  value={formData.memo}
                  onChange={handleInputChange}
                  placeholder="특별한 지시사항이나 메모를 입력하세요"
                  rows={3}
                />
              </div>

              {/* 계약 위반 알림 (다이얼로그 내) */}
              {contractViolations.length > 0 && (
                <div className="p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="h-4 w-4 text-orange-600" />
                    <span className="text-sm font-medium text-orange-800 dark:text-orange-200">
                      계약 위반 알림
                    </span>
                  </div>
                  <div className="text-xs text-orange-700 dark:text-orange-300">
                    {contractViolations[0].message}
                  </div>
                </div>
              )}

              {/* 버튼 */}
              <div className="flex gap-3 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowScheduleDialog(false)}
                  className="flex-1"
                >
                  취소
                </Button>
                <Button
                  type="submit"
                  disabled={isLoading}
                  className="flex-1"
                >
                  {isLoading ? "추가중..." : "스케줄 추가"}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
} 