'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Users, 
  User, 
  Search, 
  Edit, 
  Trash2, 
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
  Calendar,
  FileText,
  BarChart3,
  Settings,
  Bell,
  TrendingUp,
  Activity,
  Target,
  Award,
  Wifi
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient, Employee as EmployeeType } from '../../lib/api-client';
import useLoadingState from '@/hooks/useLoadingState';
import useErrorHandler from '@/hooks/useErrorHandler';
import { OfflineStorage } from '@/utils/offlineStorage';

interface EmployeeStats {
  total: number;
  active: number;
  onDuty: number;
  offDuty: number;
  newThisMonth: number;
}

interface WorkSchedule {
  id: string;
  employeeId: string;
  employeeName: string;
  date: string;
  startTime: string;
  endTime: string;
  role: string;
  status: 'scheduled' | 'working' | 'completed' | 'absent' | 'late';
  hours: number;
}

interface PerformanceData {
  id: string;
  employeeId: string;
  employeeName: string;
  period: string;
  salesTarget: number;
  actualSales: number;
  customerSatisfaction: number;
  efficiency: number;
  attendance: number;
  rating: number;
}

interface TrainingData {
  id: string;
  employeeId: string;
  employeeName: string;
  courseName: string;
  completionDate: string;
  score: number;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  certificate: string;
}

interface PayrollData {
  id: string;
  employeeId: string;
  employeeName: string;
  period: string;
  baseSalary: number;
  overtime: number;
  bonuses: number;
  deductions: number;
  netSalary: number;
  status: 'pending' | 'processed' | 'paid';
}

export default function StaffManagement() {
  const [employees, setEmployees] = useState<EmployeeType[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [isOffline, setIsOffline] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  
  const [stats, setStats] = useState<EmployeeStats>({
    total: 0,
    active: 0,
    onDuty: 0,
    offDuty: 0,
    newThisMonth: 0
  });

  const { isLoading, setLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  const fetchData = async () => {
    try {
      setLoading(true);
      // 실제 API 호출 대신 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 샘플 데이터
      const sampleEmployees: EmployeeType[] = [
        {
          id: 1,
          name: '김철수',
          email: 'kim@example.com',
          phone: '010-1234-5678',
          position: '바리스타',
          department: '커피팀',
          status: 'active',
          hire_date: '2023-01-15',
          store_id: 1
        },
        {
          id: 2,
          name: '이영희',
          email: 'lee@example.com',
          phone: '010-2345-6789',
          position: '매니저',
          department: '관리팀',
          status: 'active',
          hire_date: '2022-06-20',
          store_id: 1
        },
        {
          id: 3,
          name: '박민수',
          email: 'park@example.com',
          phone: '010-3456-7890',
          position: '바리스타',
          department: '커피팀',
          status: 'inactive',
          hire_date: '2023-03-10',
          store_id: 1
        }
      ];
      
      setEmployees(sampleEmployees);
      
      // 통계 계산
      const total = sampleEmployees.length;
      const active = sampleEmployees.filter(emp => emp.status === 'active').length;
      const onDuty = Math.floor(active * 0.7); // 70% 근무중으로 가정
      const offDuty = active - onDuty;
      const newThisMonth = Math.floor(total * 0.2); // 20% 신규로 가정
      
      setStats({
        total,
        active,
        onDuty,
        offDuty,
        newThisMonth
      });
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (employee: EmployeeType) => {
    try {
      setLoading(true);
      // 실제 API 호출 대신 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setEmployees(prev => prev.filter(emp => emp.id !== employee.id));
      toast.success('직원이 삭제되었습니다.');
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  const handleActivate = async (employee: EmployeeType) => {
    try {
      setLoading(true);
      // 실제 API 호출 대신 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setEmployees(prev => prev.map(emp => 
        emp.id === employee.id 
          ? { ...emp, status: 'active' }
          : emp
      ));
      
      toast.success('직원이 활성화되었습니다.');
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (employee: EmployeeType) => {
    // 편집 기능 구현
    toast.info('편집 기능은 추후 구현 예정입니다.');
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredEmployees = employees.filter(employee => {
    const matchesSearch = employee.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (employee.email?.toLowerCase() || '').includes(searchTerm.toLowerCase());
    const matchesRole = selectedRole === 'all' || employee.position === selectedRole;
    const matchesStatus = selectedStatus === 'all' || employee.status === selectedStatus;
    
    return matchesSearch && matchesRole && matchesStatus;
  });

  return (
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Users className="w-6 h-6" />
          직원 대시보드
        </h1>
        <p className="text-gray-300 mt-2">직원 관리 및 모니터링</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-4 mb-8 items-center">
        {isOffline && (
          <div className="flex items-center gap-2 px-4 py-2 bg-yellow-500/20 text-yellow-400 rounded-lg text-sm">
            <Wifi className="w-4 h-4" />
            오프라인 모드
          </div>
        )}
        
        <Button
          onClick={fetchData}
          disabled={isLoading}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          새로고침
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">총 직원</p>
                <p className="text-2xl font-bold text-white">{stats.total}</p>
                <p className="text-gray-400 text-sm">{stats.active}명 활성</p>
              </div>
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">근무중</p>
                <p className="text-2xl font-bold text-white">{stats.onDuty}</p>
                <p className="text-gray-400 text-sm">{stats.offDuty}명 휴무</p>
              </div>
              <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">신규</p>
                <p className="text-2xl font-bold text-white">{stats.newThisMonth}</p>
                <p className="text-gray-400 text-sm">이번 달 신규</p>
              </div>
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <User className="w-6 h-6 text-purple-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">평균 성과</p>
                <p className="text-2xl font-bold text-white">87%</p>
                <p className="text-gray-400 text-sm">이번 달 기준</p>
              </div>
              <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-yellow-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 직원 목록 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="text-white">직원 목록</CardTitle>
            <div className="flex gap-4">
              <Input
                placeholder="직원 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64 bg-white/10 border-white/20 text-white placeholder-gray-400"
              />
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="px-3 py-2 bg-white/10 border border-white/20 text-white rounded-md"
              >
                <option value="all">모든 직책</option>
                <option value="바리스타">바리스타</option>
                <option value="매니저">매니저</option>
                <option value="캐셔">캐셔</option>
              </select>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="px-3 py-2 bg-white/10 border border-white/20 text-white rounded-md"
              >
                <option value="all">모든 상태</option>
                <option value="active">활성</option>
                <option value="inactive">비활성</option>
              </select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredEmployees.map((employee) => (
              <div
                key={employee.id}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-all duration-300"
              >
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <User className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white">{employee.name}</h3>
                      <p className="text-gray-400">{employee.email}</p>
                      <p className="text-gray-400">{employee.phone}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-white font-medium">{employee.position}</p>
                      <p className="text-gray-400 text-sm">{employee.department}</p>
                      <Badge 
                        className={
                          employee.status === 'active' 
                            ? 'bg-green-500/20 text-green-400' 
                            : 'bg-red-500/20 text-red-400'
                        }
                      >
                        {employee.status === 'active' ? '활성' : '비활성'}
                      </Badge>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(employee)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      {employee.status === 'inactive' ? (
                        <Button
                          size="sm"
                          onClick={() => handleActivate(employee)}
                          className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </Button>
                      ) : (
                        <Button
                          size="sm"
                          onClick={() => handleDelete(employee)}
                          className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 