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
  Search, 
  Edit, 
  Trash2, 
  Clock,
  Users,
  CheckCircle,
  XCircle,
  AlertTriangle,
  BarChart3,
  TrendingUp,
  Filter,
  Download,
  Upload,
  Settings,
  User,
  Building,
  MapPin
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient, Employee as EmployeeType } from '../../src/lib/api-client';
import useLoadingState from '../../src/hooks/useLoadingState';
import useErrorHandler from '../../src/hooks/useErrorHandler';

interface Schedule {
  id: number;
  employee_id: number;
  employee_name: string;
  date: string;
  start_time: string;
  end_time: string;
  role: string;
  status: 'scheduled' | 'working' | 'completed' | 'absent' | 'late';
  notes?: string;
  store_id: number;
  store_name?: string;
  created_at: string;
  updated_at: string;
  type?: 'work' | 'cleaning' | 'task' | 'break';
  color?: string;
}

interface ScheduleFormData {
  employee_id: number;
  date: string;
  start_time: string;
  end_time: string;
  role: string;
  notes: string;
  store_id: number;
  type: 'work' | 'cleaning' | 'task' | 'break';
}

interface Employee {
  id: number;
  name: string;
  email: string;
  phone: string;
  position: string;
  store_id: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export default function ScheduleManagement() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [stores, setStores] = useState<any[]>([]);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<Schedule | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedEmployee, setSelectedEmployee] = useState<string>('all');
  const [selectedStore, setSelectedStore] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [calendarView, setCalendarView] = useState<'dayGridMonth' | 'timeGridWeek' | 'timeGridDay' | 'listWeek'>('dayGridMonth');
  
  const [formData, setFormData] = useState<ScheduleFormData>({
    employee_id: 0,
    date: '',
    start_time: '',
    end_time: '',
    role: '',
    notes: '',
    store_id: 0,
    type: 'work',
  });

  const { isLoading, setLoading, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 직원 목록 조회
  const fetchEmployees = async () => {
    try {
      // 실제 API 호출
      const response = await apiClient.get('/api/employees') as any;
      if (response.data.success) {
        setEmployees(response.data.employees);
      } else {
        // 임시 샘플 데이터
        const sampleEmployees: Employee[] = [
          { id: 1, name: '김철수', email: 'kim@example.com', phone: '010-1234-5678', position: '매니저', store_id: 1, status: 'active', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
          { id: 2, name: '이영희', email: 'lee@example.com', phone: '010-2345-6789', position: '바리스타', store_id: 1, status: 'active', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
          { id: 3, name: '박민수', email: 'park@example.com', phone: '010-3456-7890', position: '캐셔', store_id: 2, status: 'active', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
          { id: 4, name: '최지영', email: 'choi@example.com', phone: '010-4567-8901', position: '청소담당', store_id: 1, status: 'active', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
          { id: 5, name: '정현우', email: 'jung@example.com', phone: '010-5678-9012', position: '재고관리', store_id: 2, status: 'active', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' }
        ];
        setEmployees(sampleEmployees);
      }
    } catch (error) {
      // 임시 샘플 데이터
      const sampleEmployees: Employee[] = [
        { id: 1, name: '김철수', email: 'kim@example.com', phone: '010-1234-5678', position: '매니저', store_id: 1, status: 'active', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
        { id: 2, name: '이영희', email: 'lee@example.com', phone: '010-2345-6789', position: '바리스타', store_id: 1, status: 'active', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
        { id: 3, name: '박민수', email: 'park@example.com', phone: '010-3456-7890', position: '캐셔', store_id: 2, status: 'active', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
        { id: 4, name: '최지영', email: 'choi@example.com', phone: '010-4567-8901', position: '청소담당', store_id: 1, status: 'active', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
        { id: 5, name: '정현우', email: 'jung@example.com', phone: '010-5678-9012', position: '재고관리', store_id: 2, status: 'active', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' }
      ];
      setEmployees(sampleEmployees);
    }
  };

  // 매장 목록 조회
  const fetchStores = async () => {
    try {
      const response = await apiClient.get('/api/stores') as any;
      if (response.data.success) {
        setStores(response.data.stores);
      } else {
        // 임시 샘플 데이터
        const sampleStores = [
          { id: 1, name: '스타벅스 강남점', address: '서울시 강남구' },
          { id: 2, name: '스타벅스 홍대점', address: '서울시 마포구' }
        ];
        setStores(sampleStores);
      }
    } catch (error) {
      // 임시 샘플 데이터
      const sampleStores = [
        { id: 1, name: '스타벅스 강남점', address: '서울시 강남구' },
        { id: 2, name: '스타벅스 홍대점', address: '서울시 마포구' }
      ];
      setStores(sampleStores);
    }
  };

  // 스케줄 목록 조회
  const fetchSchedules = async () => {
    try {
      const response = await apiClient.get('/api/schedules') as any;
      if (response.data.success) {
        setSchedules(response.data.schedules);
      } else {
        // 임시 샘플 데이터
        const sampleSchedules: Schedule[] = [
          {
            id: 1,
            employee_id: 1,
            employee_name: '김철수',
            date: '2024-01-15',
            start_time: '09:00',
            end_time: '18:00',
            role: '매니저',
            status: 'completed',
            notes: '오픈 담당',
            store_id: 1,
            store_name: '스타벅스 강남점',
            created_at: '2024-01-10T00:00:00Z',
            updated_at: '2024-01-15T18:00:00Z',
            type: 'work',
            color: '#3b82f6'
          },
          {
            id: 2,
            employee_id: 2,
            employee_name: '이영희',
            date: '2024-01-15',
            start_time: '10:00',
            end_time: '19:00',
            role: '바리스타',
            status: 'working',
            notes: '중간 근무',
            store_id: 1,
            store_name: '스타벅스 강남점',
            created_at: '2024-01-10T00:00:00Z',
            updated_at: '2024-01-15T10:00:00Z',
            type: 'work',
            color: '#10b981'
          },
          {
            id: 3,
            employee_id: 4,
            employee_name: '최지영',
            date: '2024-01-15',
            start_time: '20:00',
            end_time: '22:00',
            role: '청소담당',
            status: 'scheduled',
            notes: '매장 청소',
            store_id: 1,
            store_name: '스타벅스 강남점',
            created_at: '2024-01-10T00:00:00Z',
            updated_at: '2024-01-10T00:00:00Z',
            type: 'cleaning',
            color: '#f59e0b'
          },
          {
            id: 4,
            employee_id: 5,
            employee_name: '정현우',
            date: '2024-01-16',
            start_time: '08:00',
            end_time: '10:00',
            role: '재고관리',
            status: 'scheduled',
            notes: '재고 점검',
            store_id: 2,
            store_name: '스타벅스 홍대점',
            created_at: '2024-01-10T00:00:00Z',
            updated_at: '2024-01-10T00:00:00Z',
            type: 'task',
            color: '#8b5cf6'
          }
        ];
        setSchedules(sampleSchedules);
      }
    } catch (error) {
      // 임시 샘플 데이터
      const sampleSchedules: Schedule[] = [
        {
          id: 1,
          employee_id: 1,
          employee_name: '김철수',
          date: '2024-01-15',
          start_time: '09:00',
          end_time: '18:00',
          role: '매니저',
          status: 'completed',
          notes: '오픈 담당',
          store_id: 1,
            store_name: '스타벅스 강남점',
            created_at: '2024-01-10T00:00:00Z',
            updated_at: '2024-01-15T18:00:00Z',
            type: 'work',
            color: '#3b82f6'
          },
          {
            id: 2,
            employee_id: 2,
            employee_name: '이영희',
            date: '2024-01-15',
            start_time: '10:00',
            end_time: '19:00',
            role: '바리스타',
            status: 'working',
            notes: '중간 근무',
            store_id: 1,
            store_name: '스타벅스 강남점',
            created_at: '2024-01-10T00:00:00Z',
            updated_at: '2024-01-15T10:00:00Z',
            type: 'work',
            color: '#10b981'
          },
          {
            id: 3,
            employee_id: 4,
            employee_name: '최지영',
            date: '2024-01-15',
            start_time: '20:00',
            end_time: '22:00',
            role: '청소담당',
            status: 'scheduled',
            notes: '매장 청소',
            store_id: 1,
            store_name: '스타벅스 강남점',
            created_at: '2024-01-10T00:00:00Z',
            updated_at: '2024-01-10T00:00:00Z',
            type: 'cleaning',
            color: '#f59e0b'
          },
          {
            id: 4,
            employee_id: 5,
            employee_name: '정현우',
            date: '2024-01-16',
            start_time: '08:00',
            end_time: '10:00',
            role: '재고관리',
            status: 'scheduled',
            notes: '재고 점검',
            store_id: 2,
            store_name: '스타벅스 홍대점',
            created_at: '2024-01-10T00:00:00Z',
            updated_at: '2024-01-10T00:00:00Z',
            type: 'task',
            color: '#8b5cf6'
          }
        ];
        setSchedules(sampleSchedules);
      }
    };

  const resetForm = () => {
    setFormData({
      employee_id: 0,
      date: '',
      start_time: '',
      end_time: '',
      role: '',
      notes: '',
      store_id: 0,
      type: 'work',
    });
    setEditingSchedule(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.employee_id || !formData.date || !formData.start_time || !formData.end_time) {
      toast.error('필수 항목을 입력해주세요.');
      return;
    }

    try {
      setLoading(true);
      
      // 실제 API 호출 대신 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (editingSchedule) {
        // 수정
        setSchedules(prev => prev.map(schedule => 
          schedule.id === editingSchedule.id 
            ? { 
                ...schedule, 
                ...formData, 
                updated_at: new Date().toISOString(),
                color: getTypeColor(formData.type)
              }
            : schedule
        ));
        toast.success('스케줄이 수정되었습니다.');
      } else {
        // 생성
        const employee = employees.find(emp => emp.id === formData.employee_id);
        const store = stores.find(store => store.id === formData.store_id);
        const newSchedule: Schedule = {
          id: Date.now(),
          employee_id: formData.employee_id,
          employee_name: employee?.name || '',
          date: formData.date,
          start_time: formData.start_time,
          end_time: formData.end_time,
          role: formData.role,
          status: 'scheduled',
          notes: formData.notes,
          store_id: formData.store_id,
          store_name: store?.name || '',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          type: formData.type,
          color: getTypeColor(formData.type)
        };
        
        setSchedules(prev => [...prev, newSchedule]);
        toast.success('스케줄이 생성되었습니다.');
      }
      
      setIsCreateDialogOpen(false);
      resetForm();
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (schedule: Schedule) => {
    if (!confirm(`${schedule.employee_name}의 스케줄을 삭제하시겠습니까?`)) return;
    
    try {
      setLoading(true);
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSchedules(prev => prev.filter(s => s.id !== schedule.id));
      toast.success('스케줄이 삭제되었습니다.');
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (schedule: Schedule) => {
    setEditingSchedule(schedule);
    setFormData({
      employee_id: schedule.employee_id,
      date: schedule.date,
      start_time: schedule.start_time,
      end_time: schedule.end_time,
      role: schedule.role,
      notes: schedule.notes || '',
      store_id: schedule.store_id,
      type: schedule.type || 'work',
    });
    setIsCreateDialogOpen(true);
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'work': return '#3b82f6';
      case 'cleaning': return '#f59e0b';
      case 'task': return '#8b5cf6';
      case 'break': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getTypeText = (type: string) => {
    switch (type) {
      case 'work': return '근무';
      case 'cleaning': return '청소';
      case 'task': return '업무';
      case 'break': return '휴식';
      default: return '기타';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'scheduled': return '예정';
      case 'working': return '근무중';
      case 'completed': return '완료';
      case 'absent': return '결근';
      case 'late': return '지각';
      default: return '알 수 없음';
    }
  };

  // FullCalendar 이벤트 데이터 변환
  const calendarEvents = schedules
    .filter(schedule => {
      const matchesEmployee = selectedEmployee === 'all' || schedule.employee_id.toString() === selectedEmployee;
      const matchesStore = selectedStore === 'all' || schedule.store_id.toString() === selectedStore;
      const matchesType = selectedType === 'all' || schedule.type === selectedType;
      return matchesEmployee && matchesStore && matchesType;
    })
    .map(schedule => ({
      id: schedule.id.toString(),
      title: `${schedule.employee_name} - ${getTypeText(schedule.type || 'work')}`,
      start: `${schedule.date}T${schedule.start_time}:00`,
      end: `${schedule.date}T${schedule.end_time}:00`,
      backgroundColor: schedule.color || getTypeColor(schedule.type || 'work'),
      borderColor: schedule.color || getTypeColor(schedule.type || 'work'),
      extendedProps: {
        employee_name: schedule.employee_name,
        role: schedule.role,
        status: schedule.status,
        notes: schedule.notes,
        type: schedule.type,
        store_name: schedule.store_name
      }
    }));

  const handleDateSelect = (selectInfo: any) => {
    setFormData(prev => ({
      ...prev,
      date: selectInfo.startStr.split('T')[0],
      start_time: selectInfo.startStr.split('T')[1].substring(0, 5),
      end_time: selectInfo.endStr.split('T')[1].substring(0, 5)
    }));
    setIsCreateDialogOpen(true);
  };

  const handleEventClick = (clickInfo: any) => {
    const schedule = schedules.find(s => s.id.toString() === clickInfo.event.id);
    if (schedule) {
      handleEdit(schedule);
    }
  };

  useEffect(() => {
    fetchSchedules();
    fetchEmployees();
    fetchStores();
  }, []);

  const filteredSchedules = schedules.filter(schedule => {
    const matchesEmployee = selectedEmployee === 'all' || schedule.employee_id.toString() === selectedEmployee;
    const matchesStore = selectedStore === 'all' || schedule.store_id.toString() === selectedStore;
    const matchesType = selectedType === 'all' || schedule.type === selectedType;
    return matchesEmployee && matchesStore && matchesType;
  });

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      zIndex: 9999,
      backgroundColor: '#f3f4f6',
      fontFamily: 'Arial, sans-serif',
      overflow: 'auto'
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '2rem auto',
        padding: '0 2rem'
      }}>
        {/* 헤더 */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2rem'
        }}>
          <div>
            <h1 style={{
              fontSize: '2rem',
              fontWeight: 'bold',
              color: '#1f2937',
              marginBottom: '0.5rem'
            }}>
              스케줄 관리
            </h1>
            <p style={{
              fontSize: '1.125rem',
              color: '#6b7280'
            }}>
              캘린더 형식 직원 스케줄 관리
            </p>
          </div>
          
          <div style={{
            display: 'flex',
            gap: '1rem'
          }}>
            <button
              onClick={() => setIsCreateDialogOpen(true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1rem',
                backgroundColor: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              <Plus style={{ width: '16px', height: '16px' }} />
              스케줄 추가
            </button>
          </div>
        </div>

        {/* 통계 카드 */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem'
        }}>
          <div style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1rem'
            }}>
              <h3 style={{ fontSize: '0.875rem', margin: '0' }}>총 스케줄</h3>
              <Calendar style={{ width: '20px', height: '20px' }} />
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
              {schedules.length}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0' }}>
              오늘: {schedules.filter(schedule => schedule.date === new Date().toISOString().split('T')[0]).length}건
            </p>
          </div>

          <div style={{
            backgroundColor: '#10b981',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1rem'
            }}>
              <h3 style={{ fontSize: '0.875rem', margin: '0' }}>근무중</h3>
              <Clock style={{ width: '20px', height: '20px' }} />
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
              {schedules.filter(schedule => schedule.status === 'working').length}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0' }}>
              현재 근무자
            </p>
          </div>

          <div style={{
            backgroundColor: '#f59e0b',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1rem'
            }}>
              <h3 style={{ fontSize: '0.875rem', margin: '0' }}>청소/업무</h3>
              <Users style={{ width: '20px', height: '20px' }} />
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
              {schedules.filter(schedule => schedule.type === 'cleaning' || schedule.type === 'task').length}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0' }}>
              청소 및 업무 스케줄
            </p>
          </div>

          <div style={{
            backgroundColor: '#8b5cf6',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1rem'
            }}>
              <h3 style={{ fontSize: '0.875rem', margin: '0' }}>총 직원</h3>
              <User style={{ width: '20px', height: '20px' }} />
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
              {employees.length}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0' }}>
              활성 직원 수
            </p>
          </div>
        </div>

        {/* 필터 및 뷰 컨트롤 */}
        <div style={{
          backgroundColor: 'white',
          padding: '1.5rem',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          marginBottom: '2rem'
        }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: '1rem',
            alignItems: 'end'
          }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                직원
              </label>
              <select
                value={selectedEmployee}
                onChange={(e) => setSelectedEmployee(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '0.875rem',
                  backgroundColor: 'white'
                }}
              >
                <option value="all">전체 직원</option>
                {employees.map(employee => (
                  <option key={employee.id} value={employee.id.toString()}>
                    {employee.name} ({employee.position})
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                매장
              </label>
              <select
                value={selectedStore}
                onChange={(e) => setSelectedStore(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '0.875rem',
                  backgroundColor: 'white'
                }}
              >
                <option value="all">전체 매장</option>
                {stores.map(store => (
                  <option key={store.id} value={store.id.toString()}>
                    {store.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                유형
              </label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '0.875rem',
                  backgroundColor: 'white'
                }}
              >
                <option value="all">전체 유형</option>
                <option value="work">근무</option>
                <option value="cleaning">청소</option>
                <option value="task">업무</option>
                <option value="break">휴식</option>
              </select>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                뷰
              </label>
              <select
                value={calendarView}
                onChange={(e) => setCalendarView(e.target.value as any)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '0.875rem',
                  backgroundColor: 'white'
                }}
              >
                <option value="dayGridMonth">월간</option>
                <option value="timeGridWeek">주간</option>
                <option value="timeGridDay">일간</option>
                <option value="listWeek">목록</option>
              </select>
            </div>
          </div>
        </div>

        {/* 캘린더 */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          padding: '1.5rem',
          marginBottom: '2rem'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '1.5rem'
          }}>
            <h2 style={{
              fontSize: '1.25rem',
              fontWeight: 'bold',
              color: '#1f2937',
              margin: '0'
            }}>
              스케줄 캘린더
            </h2>
            
            <div style={{
              display: 'flex',
              gap: '0.5rem'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem',
                fontSize: '0.75rem'
              }}>
                <div style={{
                  width: '12px',
                  height: '12px',
                  backgroundColor: '#3b82f6',
                  borderRadius: '2px'
                }}></div>
                <span>근무</span>
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem',
                fontSize: '0.75rem'
              }}>
                <div style={{
                  width: '12px',
                  height: '12px',
                  backgroundColor: '#f59e0b',
                  borderRadius: '2px'
                }}></div>
                <span>청소</span>
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem',
                fontSize: '0.75rem'
              }}>
                <div style={{
                  width: '12px',
                  height: '12px',
                  backgroundColor: '#8b5cf6',
                  borderRadius: '2px'
                }}></div>
                <span>업무</span>
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem',
                fontSize: '0.75rem'
              }}>
                <div style={{
                  width: '12px',
                  height: '12px',
                  backgroundColor: '#10b981',
                  borderRadius: '2px'
                }}></div>
                <span>휴식</span>
              </div>
            </div>
          </div>
          
          <div style={{ height: '600px' }}>
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
          </div>
        </div>

        {/* 스케줄 생성/수정 다이얼로그 */}
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogContent style={{
            maxWidth: '500px',
            width: '90vw'
          }}>
            <DialogHeader>
              <DialogTitle>
                {editingSchedule ? '스케줄 수정' : '새 스케줄 생성'}
              </DialogTitle>
            </DialogHeader>
            
            <form onSubmit={handleSubmit} style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem'
            }}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '1rem'
              }}>
                <div>
                  <Label htmlFor="employee">직원</Label>
                  <select
                    id="employee"
                    value={formData.employee_id}
                    onChange={(e) => {
                      const employee = employees.find(emp => emp.id.toString() === e.target.value);
                      setFormData(prev => ({
                        ...prev,
                        employee_id: parseInt(e.target.value),
                        role: employee?.position || '',
                        store_id: employee?.store_id || 0
                      }));
                    }}
                    required
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                  >
                    <option value="">직원 선택</option>
                    {employees.map(employee => (
                      <option key={employee.id} value={employee.id}>
                        {employee.name} ({employee.position})
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <Label htmlFor="type">유형</Label>
                  <select
                    id="type"
                    value={formData.type}
                    onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as any }))}
                    required
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                  >
                    <option value="work">근무</option>
                    <option value="cleaning">청소</option>
                    <option value="task">업무</option>
                    <option value="break">휴식</option>
                  </select>
                </div>
              </div>
              
              <div>
                <Label htmlFor="date">날짜</Label>
                <Input
                  id="date"
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData(prev => ({ ...prev, date: e.target.value }))}
                  required
                />
              </div>
              
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '1rem'
              }}>
                <div>
                  <Label htmlFor="start_time">시작 시간</Label>
                  <Input
                    id="start_time"
                    type="time"
                    value={formData.start_time}
                    onChange={(e) => setFormData(prev => ({ ...prev, start_time: e.target.value }))}
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="end_time">종료 시간</Label>
                  <Input
                    id="end_time"
                    type="time"
                    value={formData.end_time}
                    onChange={(e) => setFormData(prev => ({ ...prev, end_time: e.target.value }))}
                    required
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="role">직책</Label>
                <Input
                  id="role"
                  value={formData.role}
                  onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                  placeholder="직책 입력"
                />
              </div>
              
              <div>
                <Label htmlFor="notes">메모</Label>
                <textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                  placeholder="스케줄 메모"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem',
                    minHeight: '80px',
                    resize: 'vertical'
                  }}
                />
              </div>
              
              <div style={{
                display: 'flex',
                gap: '1rem',
                justifyContent: 'flex-end'
              }}>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setIsCreateDialogOpen(false);
                    resetForm();
                  }}
                >
                  취소
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? '처리중...' : (editingSchedule ? '수정' : '생성')}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
} 