"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Calendar, Users, Clock, CheckCircle, Plus, Edit, Trash2, Filter, CalendarDays } from 'lucide-react';
import { toast } from 'sonner';
import { Calendar as CalendarComponent } from '@/components/ui/calendar';

interface Schedule {
  id: number;
  user_id?: string;
  user_name: string;
  schedule_date: string;
  shift_type: string;
  start_time: string;
  end_time: string;
  break_start?: string;
  break_end?: string;
  total_hours: number;
  status: string;
  notes?: string;
  created_by: string;
}

interface ScheduleTemplate {
  id: number;
  name: string;
  description?: string;
  shift_type: string;
  start_time: string;
  end_time: string;
}

interface Employee {
  id: number;
  username: string;
  role: string;
  name?: string;
  email?: string;
  phone?: string;
  position?: string;
  department?: string;
  status?: string;
  branch_id?: number;
}

export default function ScheduleManagementPage() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [templates, setTemplates] = useState<ScheduleTemplate[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterEmployee, setFilterEmployee] = useState('all');
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('list');
  
  // 통계 데이터
  const [stats, setStats] = useState({
    todayWorking: 0,
    totalHours: 0,
    completedCheckins: 0,
    weeklySchedules: 0
  });

  // 새 스케줄 생성 상태
  const [newSchedule, setNewSchedule] = useState({
    user_id: '',
    schedule_date: new Date().toISOString().split('T')[0],
    shift_type: 'full_day',
    start_time: '09:00',
    end_time: '18:00',
    break_start: '12:00',
    break_end: '13:00',
    notes: ''
  });

  useEffect(() => {
    fetchSchedules();
    fetchTemplates();
    fetchEmployees();
    fetchStats();
  }, [selectedDate, filterStatus, filterEmployee]);

  const fetchSchedules = async () => {
    try {
      const params = new URLSearchParams({
        start_date: selectedDate,
        end_date: selectedDate
      });
      
      if (filterStatus !== 'all') params.append('status', filterStatus);
      if (filterEmployee !== 'all') params.append('user_id', filterEmployee);
      
      const response = await fetch(`/api/schedule/schedules?${params}`);
      if (response.ok) {
        const data = await response.json();
        setSchedules(data.schedules || []);
      }
    } catch (error) {
      console.error('스케줄 조회 오류:', error);
      toast.error('스케줄 조회 중 오류가 발생했습니다.');
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch('/api/schedule/templates');
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || []);
      }
    } catch (error) {
      console.error('템플릿 조회 오류:', error);
    }
  };

  const fetchEmployees = async () => {
    try {
      // 먼저 /api/admin/employees에서 직원 데이터를 가져옴
      const response = await fetch('/api/admin/employees');
      if (response.ok) {
        const data = await response.json();
        if (data.data && Array.isArray(data.data)) {
          setEmployees(data.data);
        } else if (data.employees && Array.isArray(data.employees)) {
          // 백업 형식 지원
          setEmployees(data.employees);
        } else {
          console.warn('직원 데이터가 올바른 형식이 아닙니다:', data);
          setEmployees([]);
        }
      } else {
        console.warn('직원 API 호출 실패, 스케줄 API 사용');
        // 백업으로 스케줄 API 사용
        const backupResponse = await fetch('/api/schedule/employees');
        if (backupResponse.ok) {
          const backupData = await backupResponse.json();
          setEmployees(backupData.employees || []);
        } else {
          setEmployees([]);
        }
      }
    } catch (error) {
      console.error('직원 조회 오류:', error);
      // 오류 발생 시 빈 배열로 설정
      setEmployees([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/schedule/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('통계 조회 오류:', error);
    }
  };

  const createSchedule = async () => {
    try {
      const response = await fetch('/api/schedule/schedules', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newSchedule),
      });

      if (response.ok) {
        toast.success('스케줄이 생성되었습니다.');
        fetchSchedules();
        setNewSchedule({
          user_id: '',
          schedule_date: new Date().toISOString().split('T')[0],
          shift_type: 'full_day',
          start_time: '09:00',
          end_time: '18:00',
          break_start: '12:00',
          break_end: '13:00',
          notes: ''
        });
      } else {
        const error = await response.json();
        toast.error(error.error || '스케줄 생성에 실패했습니다.');
      }
    } catch (error) {
      console.error('스케줄 생성 오류:', error);
      toast.error('스케줄 생성 중 오류가 발생했습니다.');
    }
  };

  const deleteSchedule = async (scheduleId: number) => {
    if (!confirm('정말로 이 스케줄을 삭제하시겠습니까?')) return;

    try {
      const response = await fetch(`/api/schedule/schedules/${scheduleId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        toast.success('스케줄이 삭제되었습니다.');
        fetchSchedules();
      } else {
        toast.error('스케줄 삭제에 실패했습니다.');
      }
    } catch (error) {
      console.error('스케줄 삭제 오류:', error);
      toast.error('스케줄 삭제 중 오류가 발생했습니다.');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'text-green-600';
      case 'published': return 'text-blue-600';
      case 'draft': return 'text-gray-600';
      case 'cancelled': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'confirmed': return '확정됨';
      case 'published': return '발표됨';
      case 'draft': return '임시저장';
      case 'cancelled': return '취소됨';
      default: return status;
    }
  };

  const getShiftTypeText = (shiftType: string) => {
    switch (shiftType) {
      case 'morning': return '오전';
      case 'afternoon': return '오후';
      case 'night': return '야간';
      case 'full_day': return '종일';
      case 'part_time': return '파트타임';
      default: return shiftType;
    }
  };

  // 직원 ID로 직원 정보를 찾는 헬퍼 함수
  const getEmployeeInfo = (userId: number) => {
    return employees.find(emp => emp.id === userId);
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-lg mb-2">로딩 중...</div>
            <div className="text-sm text-gray-500">직원 데이터를 가져오는 중입니다</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">스케줄 관리</h1>
            <p className="text-gray-600">직원 스케줄 및 근무 관리</p>
          </div>
          <div className="flex gap-2">
            <Button
              variant={viewMode === 'list' ? 'default' : 'outline'}
              onClick={() => setViewMode('list')}
              size="sm"
            >
              목록
            </Button>
            <Button
              variant={viewMode === 'calendar' ? 'default' : 'outline'}
              onClick={() => setViewMode('calendar')}
              size="sm"
            >
              <CalendarDays className="w-4 h-4 mr-2" />
              캘린더
            </Button>
          </div>
        </div>

        {/* 필터 및 검색 */}
        <div className="flex gap-4 mb-6">
          <div className="flex items-center gap-2">
            <Label htmlFor="date">날짜:</Label>
            <Input
              id="date"
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="w-40"
            />
          </div>
          <div className="flex items-center gap-2">
            <Label htmlFor="status">상태:</Label>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체</SelectItem>
                <SelectItem value="draft">임시저장</SelectItem>
                <SelectItem value="published">발표됨</SelectItem>
                <SelectItem value="confirmed">확정됨</SelectItem>
                <SelectItem value="cancelled">취소됨</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center gap-2">
            <Label htmlFor="employee">직원:</Label>
            <Select value={filterEmployee} onValueChange={setFilterEmployee}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 직원</SelectItem>
                {employees.length === 0 ? (
                  <SelectItem value="" disabled>
                    직원 데이터를 불러오는 중...
                  </SelectItem>
                ) : (
                  employees.map((employee) => (
                    <SelectItem key={employee.id} value={employee.id.toString()}>
                      {employee.name || employee.username}
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">오늘 근무</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.todayWorking}명</div>
            <p className="text-xs text-muted-foreground">근무 중인 직원</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 근무 시간</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalHours}시간</div>
            <p className="text-xs text-muted-foreground">오늘 총 근무</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">출근 완료</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.completedCheckins}명</div>
            <p className="text-xs text-muted-foreground">정시 출근</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">이번 주 스케줄</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.weeklySchedules}개</div>
            <p className="text-xs text-muted-foreground">스케줄 항목</p>
          </CardContent>
        </Card>
      </div>

      {/* 스케줄 뷰 */}
      {viewMode === 'list' ? (
        <Card className="border border-gray-100">
          <CardHeader className="flex justify-between items-center">
            <CardTitle>스케줄 목록</CardTitle>
            <Dialog>
              <DialogTrigger asChild>
                <Button size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  새 스케줄
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>새 스케줄 생성</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="employee">직원</Label>
                    <Select value={newSchedule.user_id} onValueChange={(value) => setNewSchedule({...newSchedule, user_id: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="직원을 선택하세요" />
                      </SelectTrigger>
                      <SelectContent>
                        {employees.length === 0 ? (
                          <SelectItem value="" disabled>
                            직원 데이터를 불러오는 중...
                          </SelectItem>
                        ) : (
                          employees.map((employee) => (
                            <SelectItem key={employee.id} value={employee.id.toString()}>
                              <div className="flex flex-col">
                                <span className="font-medium">
                                  {employee.name || employee.username}
                                </span>
                                <span className="text-xs text-gray-500">
                                  {employee.position && `${employee.position}`}
                                  {employee.department && ` • ${employee.department}`}
                                  {employee.role && ` • ${employee.role}`}
                                </span>
                              </div>
                            </SelectItem>
                          ))
                        )}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="schedule_date">날짜</Label>
                    <Input
                      id="schedule_date"
                      type="date"
                      value={newSchedule.schedule_date}
                      onChange={(e) => setNewSchedule({...newSchedule, schedule_date: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label htmlFor="shift_type">근무 유형</Label>
                    <Select value={newSchedule.shift_type} onValueChange={(value) => setNewSchedule({...newSchedule, shift_type: value})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="morning">오전</SelectItem>
                        <SelectItem value="afternoon">오후</SelectItem>
                        <SelectItem value="night">야간</SelectItem>
                        <SelectItem value="full_day">종일</SelectItem>
                        <SelectItem value="part_time">파트타임</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <Label htmlFor="start_time">시작 시간</Label>
                      <Input
                        id="start_time"
                        type="time"
                        value={newSchedule.start_time}
                        onChange={(e) => setNewSchedule({...newSchedule, start_time: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="end_time">종료 시간</Label>
                      <Input
                        id="end_time"
                        type="time"
                        value={newSchedule.end_time}
                        onChange={(e) => setNewSchedule({...newSchedule, end_time: e.target.value})}
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="notes">메모</Label>
                    <Input
                      id="notes"
                      value={newSchedule.notes}
                      onChange={(e) => setNewSchedule({...newSchedule, notes: e.target.value})}
                      placeholder="스케줄 메모"
                    />
                  </div>
                  <Button onClick={createSchedule} className="w-full">
                    스케줄 생성
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </CardHeader>
          <CardContent>
            {schedules.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                해당 날짜에 스케줄이 없습니다.
              </div>
            ) : (
              <div className="space-y-4">
                {schedules.map((schedule) => {
                  const employee = getEmployeeInfo(parseInt(schedule.user_id || '0'));
                  return (
                    <div key={schedule.id} className="grid grid-cols-1 md:grid-cols-6 gap-4 p-4 border rounded-lg">
                      <div>
                        <h4 className="font-semibold">{employee?.name || employee?.username || schedule.user_name}</h4>
                        <p className="text-sm text-gray-600">{getShiftTypeText(schedule.shift_type)}</p>
                        {employee && (
                          <p className="text-xs text-gray-500">
                            {employee.position && `${employee.position}`}
                            {employee.department && ` • ${employee.department}`}
                          </p>
                        )}
                      </div>
                    <div>
                      <p className="text-sm text-gray-600">근무 시간</p>
                      <p className="font-semibold">{schedule.start_time} - {schedule.end_time}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-600">총 시간</p>
                      <p className="font-semibold">{schedule.total_hours}시간</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-600">상태</p>
                      <p className={`font-semibold ${getStatusColor(schedule.status)}`}>
                        {getStatusText(schedule.status)}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-600">생성자</p>
                      <p className="font-semibold">{schedule.created_by}</p>
                    </div>
                    <div className="flex justify-center gap-2">
                      <Button size="sm" variant="outline">
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        onClick={() => deleteSchedule(schedule.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="border border-gray-100 lg:col-span-2">
            <CardHeader>
              <CardTitle>스케줄 캘린더</CardTitle>
            </CardHeader>
            <CardContent>
              <CalendarComponent
                mode="single"
                selected={new Date(selectedDate)}
                onSelect={(date) => {
                  if (date) {
                    setSelectedDate(date.toISOString().split('T')[0]);
                  }
                }}
                className="rounded-md border"
              />
            </CardContent>
          </Card>
          <Card className="border border-gray-100">
            <CardHeader>
              <CardTitle>선택된 날짜 스케줄</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {schedules.length === 0 ? (
                  <p className="text-gray-500 text-sm">선택된 날짜에 스케줄이 없습니다.</p>
                ) : (
                  schedules.map((schedule) => {
                    const employee = getEmployeeInfo(parseInt(schedule.user_id || '0'));
                    return (
                      <div key={schedule.id} className="p-3 border rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h4 className="font-semibold text-sm">
                              {employee?.name || employee?.username || schedule.user_name}
                            </h4>
                            {employee && (
                              <p className="text-xs text-gray-500">
                                {employee.position && `${employee.position}`}
                                {employee.department && ` • ${employee.department}`}
                              </p>
                            )}
                          </div>
                          <span className={`text-xs px-2 py-1 rounded ${getStatusColor(schedule.status)}`}>
                            {getStatusText(schedule.status)}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600 mb-1">
                          {schedule.start_time} - {schedule.end_time} ({schedule.total_hours}시간)
                        </p>
                        <p className="text-xs text-gray-500">{getShiftTypeText(schedule.shift_type)}</p>
                      </div>
                    );
                  })
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
} 