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
      console.error('스케줄 로드 오류:', error);
      toast.error('스케줄을 불러오는 중 오류가 발생했습니다.');
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
      console.error('템플릿 로드 오류:', error);
    }
  };

  const fetchEmployees = async () => {
    try {
      const response = await fetch('/api/employees');
      if (response.ok) {
        const data = await response.json();
        setEmployees(data.employees || []);
      }
    } catch (error) {
      console.error('직원 로드 오류:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/schedule/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data.stats || {
          todayWorking: 0,
          totalHours: 0,
          completedCheckins: 0,
          weeklySchedules: 0
        });
      }
    } catch (error) {
      console.error('통계 로드 오류:', error);
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
        toast.success('스케줄이 성공적으로 생성되었습니다.');
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
        toast.error('스케줄 생성에 실패했습니다.');
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
      case 'active': return 'text-green-600 bg-green-100';
      case 'completed': return 'text-blue-600 bg-blue-100';
      case 'cancelled': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '활성';
      case 'completed': return '완료';
      case 'cancelled': return '취소';
      default: return '대기';
    }
  };

  const getShiftTypeText = (shiftType: string) => {
    switch (shiftType) {
      case 'full_day': return '전일 근무';
      case 'half_day': return '반일 근무';
      case 'night_shift': return '야간 근무';
      default: return '기타';
    }
  };

  const getEmployeeInfo = (userId: number) => {
    return employees.find(emp => emp.id === userId);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">스케줄 관리</h1>
          <p className="text-gray-600 mt-2">직원들의 근무 스케줄을 관리하세요</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={viewMode === 'list' ? 'default' : 'outline'}
            onClick={() => setViewMode('list')}
          >
            <Calendar className="w-4 h-4 mr-2" />
            목록 보기
          </Button>
          <Button
            variant={viewMode === 'calendar' ? 'default' : 'outline'}
            onClick={() => setViewMode('calendar')}
          >
            <CalendarDays className="w-4 h-4 mr-2" />
            캘린더 보기
          </Button>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border border-gray-100">
          <CardContent className="p-4">
            <div className="flex items-center">
              <Users className="w-8 h-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm text-gray-600">오늘 근무자</p>
                <p className="text-2xl font-bold">{stats.todayWorking}명</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border border-gray-100">
          <CardContent className="p-4">
            <div className="flex items-center">
              <Clock className="w-8 h-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm text-gray-600">총 근무 시간</p>
                <p className="text-2xl font-bold">{stats.totalHours}시간</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border border-gray-100">
          <CardContent className="p-4">
            <div className="flex items-center">
              <CheckCircle className="w-8 h-8 text-purple-600" />
              <div className="ml-3">
                <p className="text-sm text-gray-600">체크인 완료</p>
                <p className="text-2xl font-bold">{stats.completedCheckins}명</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border border-gray-100">
          <CardContent className="p-4">
            <div className="flex items-center">
              <Calendar className="w-8 h-8 text-orange-600" />
              <div className="ml-3">
                <p className="text-sm text-gray-600">주간 스케줄</p>
                <p className="text-2xl font-bold">{stats.weeklySchedules}개</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 필터 및 새 스케줄 생성 */}
      <div className="flex justify-between items-center">
        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            <Label htmlFor="status-filter">상태:</Label>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체</SelectItem>
                <SelectItem value="active">활성</SelectItem>
                <SelectItem value="completed">완료</SelectItem>
                <SelectItem value="cancelled">취소</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center gap-2">
            <Label htmlFor="employee-filter">직원:</Label>
            <Select value={filterEmployee} onValueChange={setFilterEmployee}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 직원</SelectItem>
                {employees.map((employee) => (
                  <SelectItem key={employee.id} value={employee.id.toString()}>
                    {employee.name || employee.username}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        <Dialog>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              새 스케줄
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>새 스케줄 생성</DialogTitle>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="employee">직원</Label>
                <Select value={newSchedule.user_id} onValueChange={(value) => setNewSchedule({...newSchedule, user_id: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="직원을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    {employees.map((employee) => (
                      <SelectItem key={employee.id} value={employee.id.toString()}>
                        {employee.name || employee.username}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="date">날짜</Label>
                <Input
                  type="date"
                  value={newSchedule.schedule_date}
                  onChange={(e) => setNewSchedule({...newSchedule, schedule_date: e.target.value})}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="shift-type">근무 유형</Label>
                <Select value={newSchedule.shift_type} onValueChange={(value) => setNewSchedule({...newSchedule, shift_type: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="full_day">전일 근무</SelectItem>
                    <SelectItem value="half_day">반일 근무</SelectItem>
                    <SelectItem value="night_shift">야간 근무</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <Label htmlFor="start-time">시작 시간</Label>
                  <Input
                    type="time"
                    value={newSchedule.start_time}
                    onChange={(e) => setNewSchedule({...newSchedule, start_time: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="end-time">종료 시간</Label>
                  <Input
                    type="time"
                    value={newSchedule.end_time}
                    onChange={(e) => setNewSchedule({...newSchedule, end_time: e.target.value})}
                  />
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="notes">메모</Label>
                <Input
                  value={newSchedule.notes}
                  onChange={(e) => setNewSchedule({...newSchedule, notes: e.target.value})}
                  placeholder="스케줄에 대한 메모를 입력하세요"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline">취소</Button>
              <Button onClick={createSchedule}>생성</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* 스케줄 목록 */}
      {viewMode === 'list' ? (
        <Card className="border border-gray-100">
          <CardHeader>
            <CardTitle>스케줄 목록</CardTitle>
          </CardHeader>
          <CardContent>
            {schedules.length === 0 ? (
              <p className="text-gray-500 text-center py-8">스케줄이 없습니다.</p>
            ) : (
              <div className="space-y-4">
                {schedules.map((schedule) => (
                  <div key={schedule.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <div>
                        <p className="font-semibold">{schedule.user_name}</p>
                        <p className="text-sm text-gray-600">{schedule.schedule_date}</p>
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