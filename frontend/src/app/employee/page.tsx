'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  User, 
  Clock, 
  Calendar, 
  TrendingUp, 
  Award,
  Settings,
  Bell,
  CheckCircle,
  AlertTriangle,
  BarChart3,
  Target,
  Star,
  MapPin,
  Phone,
  Mail,
  CalendarDays,
  Clock4,
  Users,
  Activity
} from 'lucide-react';

interface EmployeeStats {
  totalWorkDays: number;
  averageHours: number;
  performanceRating: number;
  completedTasks: number;
  pendingTasks: number;
  monthlySalary: number;
}

interface WorkSchedule {
  id: number;
  date: string;
  startTime: string;
  endTime: string;
  status: 'scheduled' | 'completed' | 'absent';
  type: 'regular' | 'overtime' | 'holiday';
}

interface Task {
  id: number;
  title: string;
  description: string;
  dueDate: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
}

export default function EmployeeDashboard() {
  const [stats, setStats] = useState<EmployeeStats>({
    totalWorkDays: 0,
    averageHours: 0,
    performanceRating: 0,
    completedTasks: 0,
    pendingTasks: 0,
    monthlySalary: 0
  });
  const [schedule, setSchedule] = useState<WorkSchedule[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEmployeeData();
  }, []);

  const loadEmployeeData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/employee/dashboard');
      const result = await response.json();

      if (result.success) {
        setStats(result.data.stats);
        setSchedule(result.data.schedule);
        setTasks(result.data.tasks);
      } else {
        // 임시 데이터 (API 연결 전)
        setStats({
          totalWorkDays: 22,
          averageHours: 8.5,
          performanceRating: 4.2,
          completedTasks: 15,
          pendingTasks: 3,
          monthlySalary: 2500000
        });
        
        setSchedule([
          {
            id: 1,
            date: '2024-01-15',
            startTime: '09:00',
            endTime: '18:00',
            status: 'completed',
            type: 'regular'
          },
          {
            id: 2,
            date: '2024-01-16',
            startTime: '09:00',
            endTime: '18:00',
            status: 'scheduled',
            type: 'regular'
          }
        ]);
        
        setTasks([
          {
            id: 1,
            title: '고객 응대 업무',
            description: '전화 및 이메일 고객 문의 처리',
            dueDate: '2024-01-16',
            status: 'in_progress',
            priority: 'high'
          },
          {
            id: 2,
            title: '재고 정리',
            description: '매장 재고 현황 점검 및 정리',
            dueDate: '2024-01-17',
            status: 'pending',
            priority: 'medium'
          }
        ]);
      }
    } catch (error) {
      console.error('데이터 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400 border-green-400';
      case 'scheduled': return 'text-blue-400 border-blue-400';
      case 'absent': return 'text-red-400 border-red-400';
      default: return 'text-gray-400 border-gray-400';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return '완료';
      case 'scheduled': return '예정';
      case 'absent': return '결근';
      default: return '알 수 없음';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTaskStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'in_progress': return 'text-blue-600';
      case 'pending': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* 헤더 */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              직원 대시보드
            </h1>
            <p className="text-slate-300">
              개인 업무 및 근무 관리
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="outline" className="text-white border-white hover:bg-white hover:text-slate-900">
              <Bell className="h-4 w-4 mr-2" />
              알림
            </Button>
            <Button variant="outline" className="text-white border-white hover:bg-white hover:text-slate-900">
              <Settings className="h-4 w-4 mr-2" />
              설정
            </Button>
          </div>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <Card className="bg-white/10 border-white/20 text-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 근무일</CardTitle>
              <Calendar className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalWorkDays}일</div>
              <p className="text-xs text-slate-300">이번 달</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 border-white/20 text-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">평균 근무시간</CardTitle>
              <Clock className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.averageHours}시간</div>
              <p className="text-xs text-slate-300">일평균</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 border-white/20 text-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">성과 평가</CardTitle>
              <Star className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.performanceRating}/5.0</div>
              <p className="text-xs text-slate-300">최근 평가</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 border-white/20 text-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">완료된 업무</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.completedTasks}개</div>
              <p className="text-xs text-slate-300">이번 주</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 border-white/20 text-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">대기 중인 업무</CardTitle>
              <AlertTriangle className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.pendingTasks}개</div>
              <p className="text-xs text-slate-300">처리 필요</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 border-white/20 text-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">월 급여</CardTitle>
              <TrendingUp className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.monthlySalary.toLocaleString()}원</div>
              <p className="text-xs text-slate-300">이번 달</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 근무 일정 */}
          <Card className="bg-white/10 border-white/20 text-white">
            <CardHeader>
              <CardTitle className="flex items-center">
                <CalendarDays className="h-5 w-5 mr-2" />
                근무 일정
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {schedule.slice(0, 5).map((item) => (
                  <div key={item.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="text-sm">
                        <div className="font-medium">{item.date}</div>
                        <div className="text-slate-300">
                          {item.startTime} - {item.endTime}
                        </div>
                      </div>
                    </div>
                    <Badge className={`${getStatusColor(item.status)} bg-transparent`}>
                      {getStatusText(item.status)}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 업무 목록 */}
          <Card className="bg-white/10 border-white/20 text-white">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="h-5 w-5 mr-2" />
                업무 목록
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {tasks.map((task) => (
                  <div key={task.id} className="p-3 bg-white/5 rounded-lg">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-medium">{task.title}</h4>
                      <Badge className={`${getPriorityColor(task.priority)} text-xs`}>
                        {task.priority === 'high' ? '높음' : task.priority === 'medium' ? '보통' : '낮음'}
                      </Badge>
                    </div>
                    <p className="text-sm text-slate-300 mb-2">{task.description}</p>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-400">마감일: {task.dueDate}</span>
                      <span className={`${getTaskStatusColor(task.status)}`}>
                        {task.status === 'completed' ? '완료' : 
                         task.status === 'in_progress' ? '진행중' : '대기중'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 