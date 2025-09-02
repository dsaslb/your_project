'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Button } from '../../src/components/ui/button';
import { Input } from '../../src/components/ui/input';
import { Badge } from '../../src/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../../src/components/ui/dialog';
import { Label } from '../../src/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../src/components/ui/select';
import { Textarea } from '../../src/components/ui/textarea';
import { 
  Building2, 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  Users,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  AlertTriangle,
  Brain,
  Calendar,
  BarChart3
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../../src/lib/api-client';
import useLoadingState from '../../src/hooks/useLoadingState';
import useErrorHandler from '../../src/hooks/useErrorHandler';

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

  // AI 리포트 관리
  getAIReports(storeId: number): any[] {
    const key = `ai_reports_${storeId}`;
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : [];
  }

  saveAIReports(storeId: number, reports: any[]): void {
    const key = `ai_reports_${storeId}`;
    localStorage.setItem(key, JSON.stringify(reports));
  }
}

// AI 분석 클래스
class AIAnalyzer {
  static analyzeStoreEfficiency(schedules: any[], attendance: any[], sales: any[]): any {
    const analysis: {
      issues: string[];
      improvements: string[];
      efficiency_score: number;
      recommendations: string[];
    } = {
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
}

interface AttendanceRecord {
  id: string;
  employee_id: number;
  employee_name: string;
  date: string;
  check_in: string;
  check_out: string;
  status: 'present' | 'absent' | 'late' | 'early_leave';
}

interface SalesData {
  id: string;
  date: string;
  amount: number;
  customer_count: number;
  staff_count: number;
}

interface AIReport {
  id: string;
  date: string;
  issues: string[];
  improvements: string[];
  efficiency_score: number;
  recommendations: string[];
}

export default function StoreManagement() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [attendanceRecords, setAttendanceRecords] = useState<AttendanceRecord[]>([]);
  const [salesData, setSalesData] = useState<SalesData[]>([]);
  const [aiReports, setAiReports] = useState<AIReport[]>([]);
  
  const [selectedEmployee, setSelectedEmployee] = useState<number | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('all');
  
  const [isScheduleDialogOpen, setIsScheduleDialogOpen] = useState(false);
  const [isAttendanceDialogOpen, setIsAttendanceDialogOpen] = useState(false);
  const [isSalesDialogOpen, setIsSalesDialogOpen] = useState(false);
  const [isAIReportDialogOpen, setIsAIReportDialogOpen] = useState(false);
  
  const [scheduleForm, setScheduleForm] = useState({
    employee_id: 0,
    date: '',
    start_time: '',
    end_time: '',
    type: 'work' as const,
    role: '',
    notes: ''
  });

  const [attendanceForm, setAttendanceForm] = useState({
    employee_id: 0,
    date: '',
    check_in: '',
    check_out: '',
    status: 'present' as const
  });

  const [salesForm, setSalesForm] = useState({
    date: '',
    amount: 0,
    customer_count: 0,
    staff_count: 0
  });

  const { isLoading, setLoading, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();
  const storageManager = LocalStorageManager.getInstance();

  // 현재 매장 ID (실제로는 사용자 정보에서 가져와야 함)
  const currentStoreId = 1;

  // 직원 마스터 데이터 조회
  const fetchEmployees = async () => {
    try {
      const response = await apiClient.get('/api/employees/master') as any;
      if (response.data.success) {
        setEmployees(response.data.employees);
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

  // 로컬 스토리지에서 데이터 로드
  const loadLocalData = () => {
    setSchedules(storageManager.getSchedules(currentStoreId));
    setAttendanceRecords(storageManager.getAttendanceRecords(currentStoreId));
    setSalesData(storageManager.getSalesData(currentStoreId));
    setAiReports(storageManager.getAIReports(currentStoreId));
  };

  // 스케줄 관리
  const addSchedule = () => {
    const newSchedule: Schedule = {
      id: Date.now().toString(),
      employee_id: scheduleForm.employee_id,
      employee_name: employees.find(emp => emp.id === scheduleForm.employee_id)?.name || '',
      date: scheduleForm.date,
      start_time: scheduleForm.start_time,
      end_time: scheduleForm.end_time,
      type: scheduleForm.type,
      role: scheduleForm.role,
      notes: scheduleForm.notes,
      color: scheduleForm.type === 'work' ? '#3b82f6' : 
             scheduleForm.type === 'cleaning' ? '#f59e0b' : 
             scheduleForm.type === 'task' ? '#8b5cf6' : '#10b981'
    };

    const updatedSchedules = [...schedules, newSchedule];
    setSchedules(updatedSchedules);
    storageManager.saveSchedules(currentStoreId, updatedSchedules);
    
    setIsScheduleDialogOpen(false);
    setScheduleForm({ employee_id: 0, date: '', start_time: '', end_time: '', type: 'work', role: '', notes: '' });
    toast.success('스케줄이 추가되었습니다.');
  };

  // 출퇴근 기록 관리
  const addAttendanceRecord = () => {
    const newRecord: AttendanceRecord = {
      id: Date.now().toString(),
      employee_id: attendanceForm.employee_id,
      employee_name: employees.find(emp => emp.id === attendanceForm.employee_id)?.name || '',
      date: attendanceForm.date,
      check_in: attendanceForm.check_in,
      check_out: attendanceForm.check_out,
      status: attendanceForm.status
    };

    const updatedRecords = [...attendanceRecords, newRecord];
    setAttendanceRecords(updatedRecords);
    storageManager.saveAttendanceRecords(currentStoreId, updatedRecords);
    
    setIsAttendanceDialogOpen(false);
    setAttendanceForm({ employee_id: 0, date: '', check_in: '', check_out: '', status: 'present' });
    toast.success('출퇴근 기록이 추가되었습니다.');
  };

  // 매출 데이터 관리
  const addSalesData = () => {
    const newSales: SalesData = {
      id: Date.now().toString(),
      date: salesForm.date,
      amount: salesForm.amount,
      customer_count: salesForm.customer_count,
      staff_count: salesForm.staff_count
    };

    const updatedSales = [...salesData, newSales];
    setSalesData(updatedSales);
    storageManager.saveSalesData(currentStoreId, updatedSales);
    
    setIsSalesDialogOpen(false);
    setSalesForm({ date: '', amount: 0, customer_count: 0, staff_count: 0 });
    toast.success('매출 데이터가 추가되었습니다.');
  };

  // AI 분석 실행
  const runAIAnalysis = () => {
    const analysis = AIAnalyzer.analyzeStoreEfficiency(schedules, attendanceRecords, salesData);
    
    const newReport: AIReport = {
      id: Date.now().toString(),
      date: new Date().toISOString().split('T')[0],
      issues: analysis.issues,
      improvements: analysis.improvements,
      efficiency_score: analysis.efficiency_score,
      recommendations: analysis.recommendations
    };

    const updatedReports = [...aiReports, newReport];
    setAiReports(updatedReports);
    storageManager.saveAIReports(currentStoreId, updatedReports);
    
    setIsAIReportDialogOpen(false);
    toast.success('AI 분석이 완료되었습니다.');
  };

  // AI 리포트 상위 관리자에게 제출
  const submitAIReport = async (report: AIReport) => {
    try {
      await apiClient.post('/api/ai-reports/summary', {
        store_id: currentStoreId,
        report_date: report.date,
        summary_data: {
          issues: report.issues,
          improvements: report.improvements,
          efficiency_score: report.efficiency_score
        }
      });
      toast.success('AI 리포트가 상위 관리자에게 제출되었습니다.');
    } catch (error) {
      toast.error('AI 리포트 제출 실패');
    }
  };

  useEffect(() => {
    fetchEmployees();
    loadLocalData();
  }, []);

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">매장 관리자 대시보드</h1>
        <div className="flex gap-2">
          <Button onClick={() => setIsScheduleDialogOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            스케줄 추가
          </Button>
          <Button onClick={() => setIsAttendanceDialogOpen(true)}>
            <Clock className="w-4 h-4 mr-2" />
            출퇴근 기록
          </Button>
          <Button onClick={() => setIsSalesDialogOpen(true)}>
            <TrendingUp className="w-4 h-4 mr-2" />
            매출 입력
          </Button>
          <Button onClick={() => setIsAIReportDialogOpen(true)}>
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
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{employees.length}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">오늘 스케줄</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {schedules.filter(s => s.date === new Date().toISOString().split('T')[0]).length}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">오늘 출근</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {attendanceRecords.filter(r => r.date === new Date().toISOString().split('T')[0] && r.status === 'present').length}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평균 효율도</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {aiReports.length > 0 ? Math.round(aiReports[aiReports.length - 1].efficiency_score) : 0}%
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI 리포트 섹션 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5" />
            AI 분석 리포트
          </CardTitle>
        </CardHeader>
        <CardContent>
          {aiReports.length > 0 ? (
            <div className="space-y-4">
              {aiReports.slice(-3).reverse().map((report) => (
                <div key={report.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold">분석 리포트 - {report.date}</h3>
                    <div className="flex gap-2">
                      <Badge variant={report.efficiency_score >= 80 ? 'default' : 'destructive'}>
                        효율도: {Math.round(report.efficiency_score)}%
                      </Badge>
                      <Button size="sm" onClick={() => submitAIReport(report)}>
                        상위 제출
                      </Button>
                    </div>
                  </div>
                  
                  {report.issues.length > 0 && (
                    <div className="mb-2">
                      <h4 className="font-medium text-red-600 flex items-center gap-1">
                        <AlertTriangle className="w-4 h-4" />
                        문제점
                      </h4>
                      <ul className="list-disc list-inside text-sm">
                        {report.issues.map((issue, index) => (
                          <li key={index}>{issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {report.improvements.length > 0 && (
                    <div>
                      <h4 className="font-medium text-green-600">개선사항</h4>
                      <ul className="list-disc list-inside text-sm">
                        {report.improvements.map((improvement, index) => (
                          <li key={index}>{improvement}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground">AI 분석 리포트가 없습니다. AI 분석을 실행해보세요.</p>
          )}
        </CardContent>
      </Card>

      {/* 스케줄 관리 다이얼로그 */}
      <Dialog open={isScheduleDialogOpen} onOpenChange={setIsScheduleDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>스케줄 추가</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>직원</Label>
              <Select value={scheduleForm.employee_id.toString()} onValueChange={(value) => setScheduleForm({...scheduleForm, employee_id: parseInt(value)})}>
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
              <Label>날짜</Label>
              <Input type="date" value={scheduleForm.date} onChange={(e) => setScheduleForm({...scheduleForm, date: e.target.value})} />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>시작 시간</Label>
                <Input type="time" value={scheduleForm.start_time} onChange={(e) => setScheduleForm({...scheduleForm, start_time: e.target.value})} />
              </div>
              <div>
                <Label>종료 시간</Label>
                <Input type="time" value={scheduleForm.end_time} onChange={(e) => setScheduleForm({...scheduleForm, end_time: e.target.value})} />
              </div>
            </div>
            
            <div>
              <Label>유형</Label>
              <Select value={scheduleForm.type} onValueChange={(value) => setScheduleForm({...scheduleForm, type: value as any})}>
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
              <Label>역할</Label>
              <Input value={scheduleForm.role} onChange={(e) => setScheduleForm({...scheduleForm, role: e.target.value})} />
            </div>
            
            <div>
              <Label>메모</Label>
              <Textarea value={scheduleForm.notes} onChange={(e) => setScheduleForm({...scheduleForm, notes: e.target.value})} />
            </div>
            
            <Button onClick={addSchedule} className="w-full">스케줄 추가</Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* 출퇴근 기록 다이얼로그 */}
      <Dialog open={isAttendanceDialogOpen} onOpenChange={setIsAttendanceDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>출퇴근 기록</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>직원</Label>
              <Select value={attendanceForm.employee_id.toString()} onValueChange={(value) => setAttendanceForm({...attendanceForm, employee_id: parseInt(value)})}>
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
              <Label>날짜</Label>
              <Input type="date" value={attendanceForm.date} onChange={(e) => setAttendanceForm({...attendanceForm, date: e.target.value})} />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>출근 시간</Label>
                <Input type="time" value={attendanceForm.check_in} onChange={(e) => setAttendanceForm({...attendanceForm, check_in: e.target.value})} />
              </div>
              <div>
                <Label>퇴근 시간</Label>
                <Input type="time" value={attendanceForm.check_out} onChange={(e) => setAttendanceForm({...attendanceForm, check_out: e.target.value})} />
              </div>
            </div>
            
            <div>
              <Label>상태</Label>
              <Select value={attendanceForm.status} onValueChange={(value) => setAttendanceForm({...attendanceForm, status: value as any})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="present">정상 출근</SelectItem>
                  <SelectItem value="late">지각</SelectItem>
                  <SelectItem value="absent">결근</SelectItem>
                  <SelectItem value="early_leave">조퇴</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <Button onClick={addAttendanceRecord} className="w-full">출퇴근 기록 추가</Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* 매출 데이터 다이얼로그 */}
      <Dialog open={isSalesDialogOpen} onOpenChange={setIsSalesDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>매출 데이터 입력</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>날짜</Label>
              <Input type="date" value={salesForm.date} onChange={(e) => setSalesForm({...salesForm, date: e.target.value})} />
            </div>
            
            <div>
              <Label>매출액</Label>
              <Input type="number" value={salesForm.amount} onChange={(e) => setSalesForm({...salesForm, amount: parseInt(e.target.value)})} />
            </div>
            
            <div>
              <Label>고객 수</Label>
              <Input type="number" value={salesForm.customer_count} onChange={(e) => setSalesForm({...salesForm, customer_count: parseInt(e.target.value)})} />
            </div>
            
            <div>
              <Label>근무 인원</Label>
              <Input type="number" value={salesForm.staff_count} onChange={(e) => setSalesForm({...salesForm, staff_count: parseInt(e.target.value)})} />
            </div>
            
            <Button onClick={addSalesData} className="w-full">매출 데이터 추가</Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* AI 분석 다이얼로그 */}
      <Dialog open={isAIReportDialogOpen} onOpenChange={setIsAIReportDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>AI 분석 실행</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-muted-foreground">
              현재 저장된 스케줄, 출퇴근 기록, 매출 데이터를 기반으로 AI 분석을 실행합니다.
            </p>
            
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="p-4 border rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{schedules.length}</div>
                <div className="text-sm">스케줄</div>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="text-2xl font-bold text-green-600">{attendanceRecords.length}</div>
                <div className="text-sm">출퇴근 기록</div>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{salesData.length}</div>
                <div className="text-sm">매출 데이터</div>
              </div>
            </div>
            
            <Button onClick={runAIAnalysis} className="w-full">
              <Brain className="w-4 h-4 mr-2" />
              AI 분석 실행
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
} 