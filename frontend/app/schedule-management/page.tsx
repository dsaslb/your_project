'use client';

import React, { useState, useEffect, useCallback } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import listPlugin from '@fullcalendar/list';
import { Card, CardContent, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Button } from '../../src/components/ui/button';
import { Input } from '../../src/components/ui/input';
import { Badge } from '../../src/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../../src/components/ui/dialog';
import { Label } from '../../src/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../src/components/ui/select';
import { Textarea } from '../../src/components/ui/textarea';
import { 
  Calendar, 
  Plus, 
  Filter, 
  Download, 
  Upload, 
  Settings, 
  User, 
  Building, 
  MapPin,
  Brain,
  TrendingUp
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../../src/lib/api-client';

// 로컬 스토리지 관리 클래스
class LocalStorageManager {
  private static instance: LocalStorageManager;
  
  static getInstance(): LocalStorageManager {
    if (!LocalStorageManager.instance) {
      LocalStorageManager.instance = new LocalStorageManager();
    }
    return LocalStorageManager.instance;
  }

  // 스케줄 데이터 관리
  getSchedules(storeId: number): any[] {
    const key = `schedules_${storeId}`;
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : [];
  }

  saveSchedules(storeId: number, schedules: any[]): void {
    const key = `schedules_${storeId}`;
    localStorage.setItem(key, JSON.stringify(schedules));
  }

  // 출퇴근 기록 관리
  getAttendanceRecords(storeId: number): any[] {
    const key = `attendance_${storeId}`;
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : [];
  }

  saveAttendanceRecords(storeId: number, records: any[]): void {
    const key = `attendance_${storeId}`;
    localStorage.setItem(key, JSON.stringify(records));
  }

  // 매출 데이터 관리
  getSalesData(storeId: number): any[] {
    const key = `sales_${storeId}`;
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : [];
  }

  saveSalesData(storeId: number, sales: any[]): void {
    const key = `sales_${storeId}`;
    localStorage.setItem(key, JSON.stringify(sales));
  }
}

// AI 분석 클래스
class AIAnalyzer {
  static analyzeScheduleEfficiency(schedules: any[], attendance: any[], sales: any[]): any {
    const analysis = {
      issues: [],
      improvements: [],
      efficiency_score: 0,
      recommendations: []
    };

    // 간단한 AI 분석 로직
    const totalStaff = schedules.length;
    const totalSales = sales.reduce((sum, sale) => sum + sale.amount, 0);
    const avgSalesPerStaff = totalSales / totalStaff;

    if (avgSalesPerStaff < 100000) {
      analysis.issues.push('직원당 매출이 낮음');
      analysis.improvements.push('직원 교육 및 동기 부여 강화');
    }

    if (totalStaff > 10) {
      analysis.issues.push('인원 과다');
      analysis.improvements.push('인원 최적화 필요');
    }

    analysis.efficiency_score = Math.min(100, Math.max(0, avgSalesPerStaff / 1000));
    
    return analysis;
  }
}

interface Employee {
  id: number;
  name: string;
  email: string;
  phone: string;
  role: string;
  department: string;
  position: string;
  store_id: number;
}

interface Store {
  id: number;
  name: string;
  code: string;
  address: string;
  phone: string;
  status: string;
  brand_name: string;
  brand_id: number;
}

interface Schedule {
  id: string;
  employee_id: number;
  employee_name: string;
  date: string;
  start_time: string;
  end_time: string;
  type: 'work' | 'cleaning' | 'task' | 'break';
  role: string;
  notes: string;
  color: string;
  store_id: number;
  store_name: string;
}

interface ScheduleFormData {
  employee_id: number;
  date: string;
  start_time: string;
  end_time: string;
  type: 'work' | 'cleaning' | 'task' | 'break';
  role: string;
  notes: string;
}

export default function ScheduleManagement() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [stores, setStores] = useState<Store[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [selectedEmployee, setSelectedEmployee] = useState<number | 'all'>('all');
  const [selectedStore, setSelectedStore] = useState<number | 'all'>('all');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [calendarView, setCalendarView] = useState<string>('dayGridMonth');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<Schedule | null>(null);
  const [formData, setFormData] = useState<ScheduleFormData>({
    employee_id: 0,
    date: '',
    start_time: '',
    end_time: '',
    type: 'work',
    role: '',
    notes: ''
  });

  const storageManager = LocalStorageManager.getInstance();
  
  // 현재 매장 ID (실제로는 사용자 정보에서 가져와야 함)
  const currentStoreId = 1;

  // 직원 마스터 데이터 조회
  const fetchEmployees = async () => {
    try {
      const response = await apiClient.get('/api/employees/master') as any;
      if (response.data.success) {
        setEmployees(response.data.employees);
      } else {
        // 샘플 데이터로 대체
        setEmployees([
          { id: 1, name: '김직원', email: 'kim@store.com', phone: '010-1234-5678', role: 'employee', department: '서빙', position: '직원', store_id: 1 },
          { id: 2, name: '이매니저', email: 'lee@store.com', phone: '010-2345-6789', role: 'manager', department: '관리', position: '매니저', store_id: 1 }
        ]);
      }
    } catch (error) {
      console.error('직원 데이터 조회 실패:', error);
      // 샘플 데이터로 대체
      setEmployees([
        { id: 1, name: '김직원', email: 'kim@store.com', phone: '010-1234-5678', role: 'employee', department: '서빙', position: '직원', store_id: 1 },
        { id: 2, name: '이매니저', email: 'lee@store.com', phone: '010-2345-6789', role: 'manager', department: '관리', position: '매니저', store_id: 1 }
      ]);
    }
  };

  // 매장 마스터 데이터 조회
  const fetchStores = async () => {
    try {
      const response = await apiClient.get('/api/stores/master') as any;
      if (response.data.success) {
        setStores(response.data.stores);
      } else {
        // 샘플 데이터로 대체
        setStores([
          { id: 1, name: '강남점', code: 'GN001', address: '서울시 강남구', phone: '02-1234-5678', status: 'active', brand_name: '스타벅스', brand_id: 1 }
        ]);
      }
    } catch (error) {
      console.error('매장 데이터 조회 실패:', error);
      // 샘플 데이터로 대체
      setStores([
        { id: 1, name: '강남점', code: 'GN001', address: '서울시 강남구', phone: '02-1234-5678', status: 'active', brand_name: '스타벅스', brand_id: 1 }
      ]);
    }
  };

  // 로컬 스토리지에서 스케줄 데이터 로드
  const loadSchedules = () => {
    const localSchedules = storageManager.getSchedules(currentStoreId);
    setSchedules(localSchedules);
  };

  // 스케줄 타입별 색상 반환
  const getTypeColor = (type: string): string => {
    switch (type) {
      case 'work': return '#3b82f6';
      case 'cleaning': return '#f59e0b';
      case 'task': return '#8b5cf6';
      case 'break': return '#10b981';
      default: return '#6b7280';
    }
  };

  // 스케줄 타입별 텍스트 반환
  const getTypeText = (type: string): string => {
    switch (type) {
      case 'work': return '근무';
      case 'cleaning': return '청소';
      case 'task': return '업무';
      case 'break': return '휴식';
      default: return '기타';
    }
  };

  // 근무 시간 계산
  const calculateWorkHours = (startTime: string, endTime: string): number => {
    const start = new Date(`2000-01-01T${startTime}:00`);
    const end = new Date(`2000-01-01T${endTime}:00`);
    return (end.getTime() - start.getTime()) / (1000 * 60 * 60);
  };

  // FullCalendar 이벤트 데이터 변환
  const calendarEvents = schedules
    .filter(schedule => {
      if (selectedEmployee !== 'all' && schedule.employee_id !== selectedEmployee) return false;
      if (selectedStore !== 'all' && schedule.store_id !== selectedStore) return false;
      if (selectedType !== 'all' && schedule.type !== selectedType) return false;
      return true;
    })
    .map(schedule => ({
      id: schedule.id,
      title: `${schedule.employee_name} - ${getTypeText(schedule.type)}`,
      start: `${schedule.date}T${schedule.start_time}:00`,
      end: `${schedule.date}T${schedule.end_time}:00`,
      backgroundColor: schedule.color || getTypeColor(schedule.type),
      borderColor: schedule.color || getTypeColor(schedule.type),
      extendedProps: {
        employee_name: schedule.employee_name,
        role: schedule.role,
        notes: schedule.notes,
        type: schedule.type,
        store_name: schedule.store_name
      }
    }));

  // 날짜 선택 핸들러
  const handleDateSelect = useCallback((selectInfo: any) => {
    setFormData({
      employee_id: 0,
      date: selectInfo.startStr.split('T')[0],
      start_time: selectInfo.startStr.split('T')[1]?.substring(0, 5) || '09:00',
      end_time: selectInfo.endStr.split('T')[1]?.substring(0, 5) || '18:00',
      type: 'work',
      role: '',
      notes: ''
    });
    setEditingSchedule(null);
    setIsDialogOpen(true);
  }, []);

  // 이벤트 클릭 핸들러
  const handleEventClick = useCallback((clickInfo: any) => {
    const schedule = schedules.find(s => s.id === clickInfo.event.id);
    if (schedule) {
      setEditingSchedule(schedule);
      setFormData({
        employee_id: schedule.employee_id,
        date: schedule.date,
        start_time: schedule.start_time,
        end_time: schedule.end_time,
        type: schedule.type,
        role: schedule.role,
        notes: schedule.notes
      });
      setIsDialogOpen(true);
    }
  }, [schedules]);

  // 폼 제출 핸들러
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.employee_id || !formData.date || !formData.start_time || !formData.end_time) {
      toast.error('필수 필드를 모두 입력해주세요.');
      return;
    }

    const employee = employees.find(emp => emp.id === formData.employee_id);
    const store = stores.find(s => s.id === currentStoreId);

    if (editingSchedule) {
      // 스케줄 수정
      const updatedSchedules = schedules.map(schedule => 
        schedule.id === editingSchedule.id 
          ? {
              ...schedule,
              employee_id: formData.employee_id,
              employee_name: employee?.name || '',
              date: formData.date,
              start_time: formData.start_time,
              end_time: formData.end_time,
              type: formData.type,
              role: formData.role,
              notes: formData.notes,
              color: getTypeColor(formData.type)
            }
          : schedule
      );
      setSchedules(updatedSchedules);
      storageManager.saveSchedules(currentStoreId, updatedSchedules);
      toast.success('스케줄이 수정되었습니다.');
    } else {
      // 새 스케줄 추가
      const newSchedule: Schedule = {
        id: Date.now().toString(),
        employee_id: formData.employee_id,
        employee_name: employee?.name || '',
        date: formData.date,
        start_time: formData.start_time,
        end_time: formData.end_time,
        type: formData.type,
        role: formData.role,
        notes: formData.notes,
        color: getTypeColor(formData.type),
        store_id: currentStoreId,
        store_name: store?.name || ''
      };

      const updatedSchedules = [...schedules, newSchedule];
      setSchedules(updatedSchedules);
      storageManager.saveSchedules(currentStoreId, updatedSchedules);
      toast.success('스케줄이 추가되었습니다.');
    }

    setIsDialogOpen(false);
    setEditingSchedule(null);
    setFormData({
      employee_id: 0,
      date: '',
      start_time: '',
      end_time: '',
      type: 'work',
      role: '',
      notes: ''
    });
  };

  // 스케줄 삭제
  const handleDelete = () => {
    if (!editingSchedule) return;

    const updatedSchedules = schedules.filter(schedule => schedule.id !== editingSchedule.id);
    setSchedules(updatedSchedules);
    storageManager.saveSchedules(currentStoreId, updatedSchedules);
    
    setIsDialogOpen(false);
    setEditingSchedule(null);
    setFormData({
      employee_id: 0,
      date: '',
      start_time: '',
      end_time: '',
      type: 'work',
      role: '',
      notes: ''
    });
    toast.success('스케줄이 삭제되었습니다.');
  };

  // AI 분석 실행
  const runAIAnalysis = () => {
    const attendanceRecords = storageManager.getAttendanceRecords(currentStoreId);
    const salesData = storageManager.getSalesData(currentStoreId);
    
    const analysis = AIAnalyzer.analyzeScheduleEfficiency(schedules, attendanceRecords, salesData);
    
    toast.success(`AI 분석 완료: 효율도 ${Math.round(analysis.efficiency_score)}%`);
    console.log('AI 분석 결과:', analysis);
  };

  useEffect(() => {
    fetchEmployees();
    fetchStores();
    loadSchedules();
  }, []);

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">스케줄 관리</h1>
        <div className="flex gap-2">
          <Button onClick={() => setIsDialogOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            스케줄 추가
          </Button>
          <Button onClick={runAIAnalysis} variant="outline">
            <Brain className="w-4 h-4 mr-2" />
            AI 분석
          </Button>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 직원</CardTitle>
            <User className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{employees.length}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 스케줄</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{schedules.length}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">청소/업무</CardTitle>
            <Building className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {schedules.filter(s => s.type === 'cleaning' || s.type === 'task').length}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 근무시간</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round(schedules.reduce((total, s) => total + calculateWorkHours(s.start_time, s.end_time), 0))}h
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 필터 섹션 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="w-5 h-5" />
            필터
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <Label>직원</Label>
              <Select value={selectedEmployee.toString()} onValueChange={(value) => setSelectedEmployee(value === 'all' ? 'all' : parseInt(value))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">전체 직원</SelectItem>
                  {employees.map((emp) => (
                    <SelectItem key={emp.id} value={emp.id.toString()}>{emp.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>매장</Label>
              <Select value={selectedStore.toString()} onValueChange={(value) => setSelectedStore(value === 'all' ? 'all' : parseInt(value))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">전체 매장</SelectItem>
                  {stores.map((store) => (
                    <SelectItem key={store.id} value={store.id.toString()}>{store.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>유형</Label>
              <Select value={selectedType} onValueChange={setSelectedType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">전체</SelectItem>
                  <SelectItem value="work">근무</SelectItem>
                  <SelectItem value="cleaning">청소</SelectItem>
                  <SelectItem value="task">업무</SelectItem>
                  <SelectItem value="break">휴식</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>뷰</Label>
              <Select value={calendarView} onValueChange={setCalendarView}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="dayGridMonth">월</SelectItem>
                  <SelectItem value="timeGridWeek">주</SelectItem>
                  <SelectItem value="timeGridDay">일</SelectItem>
                  <SelectItem value="listWeek">목록</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 캘린더 */}
      <Card>
        <CardContent className="p-6">
          <FullCalendar
            plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin]}
            headerToolbar={{
              left: 'prev,next today',
              center: 'title',
              right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
            }}
            initialView={calendarView}
            editable={true}
            selectable={true}
            selectMirror={true}
            dayMaxEvents={true}
            weekends={true}
            events={calendarEvents}
            select={handleDateSelect}
            eventClick={handleEventClick}
            locale="ko"
            height="100%"
            eventDisplay="block"
            eventTimeFormat={{
              hour: '2-digit',
              minute: '2-digit',
              meridiem: false,
              hour12: false
            }}
          />
        </CardContent>
      </Card>

      {/* 스케줄 추가/수정 다이얼로그 */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {editingSchedule ? '스케줄 수정' : '스케줄 추가'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label>직원</Label>
              <Select value={formData.employee_id.toString()} onValueChange={(value) => setFormData({...formData, employee_id: parseInt(value)})}>
                <SelectTrigger>
                  <SelectValue placeholder="직원 선택" />
                </SelectTrigger>
                <SelectContent>
                  {employees.map((emp) => (
                    <SelectItem key={emp.id} value={emp.id.toString()}>{emp.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>유형</Label>
              <Select value={formData.type} onValueChange={(value) => setFormData({...formData, type: value as any})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="work">근무</SelectItem>
                  <SelectItem value="cleaning">청소</SelectItem>
                  <SelectItem value="task">업무</SelectItem>
                  <SelectItem value="break">휴식</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>날짜</Label>
              <Input type="date" value={formData.date} onChange={(e) => setFormData({...formData, date: e.target.value})} />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>시작 시간</Label>
                <Input type="time" value={formData.start_time} onChange={(e) => setFormData({...formData, start_time: e.target.value})} />
              </div>
              <div>
                <Label>종료 시간</Label>
                <Input type="time" value={formData.end_time} onChange={(e) => setFormData({...formData, end_time: e.target.value})} />
              </div>
            </div>
            
            <div>
              <Label>역할</Label>
              <Input value={formData.role} onChange={(e) => setFormData({...formData, role: e.target.value})} />
            </div>
            
            <div>
              <Label>메모</Label>
              <Textarea value={formData.notes} onChange={(e) => setFormData({...formData, notes: e.target.value})} />
            </div>
            
            <div className="flex gap-2">
              <Button type="submit" className="flex-1">
                {editingSchedule ? '수정' : '추가'}
              </Button>
              {editingSchedule && (
                <Button type="button" variant="destructive" onClick={handleDelete}>
                  삭제
                </Button>
              )}
              <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                취소
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
} 