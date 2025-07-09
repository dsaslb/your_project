'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  User, 
  Clock, 
  Calendar,
  TrendingUp, 
  Activity, 
  Star,
  BarChart3,
  Settings,
  Bell,
  CheckCircle,
  AlertTriangle,
  Target
} from 'lucide-react';

interface EmployeeStats {
  todayWorkHours: number;
  weeklyWorkHours: number;
  monthlyWorkHours: number;
  totalOrders: number;
  customerRating: number;
  performanceScore: number;
  attendanceRate: number;
  overtimeHours: number;
}

interface Task {
  id: number;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  dueDate: string;
  category: 'cleaning' | 'service' | 'kitchen' | 'admin';
}

interface Schedule {
  id: number;
  date: string;
  startTime: string;
  endTime: string;
  type: 'work' | 'break' | 'training' | 'meeting';
  status: 'scheduled' | 'completed' | 'absent';
}

export default function EmployeeDashboard() {
  const [stats, setStats] = useState<EmployeeStats>({
    todayWorkHours: 0,
    weeklyWorkHours: 0,
    monthlyWorkHours: 0,
    totalOrders: 0,
    customerRating: 0,
    performanceScore: 0,
    attendanceRate: 0,
    overtimeHours: 0
  });

  const [tasks, setTasks] = useState<Task[]>([]);
  const [schedule, setSchedule] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 로그인 시에만 데이터 fetch (실시간 아님)
    loadEmployeeData();
  }, []);

  const loadEmployeeData = async () => {
    try {
      // 실제로는 백엔드 API에서 데이터 가져오기
      // 현재는 더미 데이터 사용
      const mockStats: EmployeeStats = {
        todayWorkHours: 6.5,
        weeklyWorkHours: 32.5,
        monthlyWorkHours: 140,
        totalOrders: 45,
        customerRating: 4.8,
        performanceScore: 92,
        attendanceRate: 95,
        overtimeHours: 2.5
      };

      const mockTasks: Task[] = [
        {
          id: 1,
          title: '테이블 정리',
          description: '1-5번 테이블 청소 및 정리',
          status: 'completed',
          priority: 'high',
          dueDate: '2024-01-15',
          category: 'cleaning'
        },
        {
          id: 2,
          title: '고객 서비스',
          description: '새 고객 응대 및 주문 처리',
          status: 'in_progress',
          priority: 'high',
          dueDate: '2024-01-15',
          category: 'service'
        },
        {
          id: 3,
          title: '재고 확인',
          description: '주방 재고 현황 점검',
          status: 'pending',
          priority: 'medium',
          dueDate: '2024-01-16',
          category: 'kitchen'
        },
        {
          id: 4,
          title: '매출 정리',
          description: '오늘 매출 정리 및 보고서 작성',
          status: 'pending',
          priority: 'low',
          dueDate: '2024-01-15',
          category: 'admin'
        }
      ];

      const mockSchedule: Schedule[] = [
        {
          id: 1,
          date: '2024-01-15',
          startTime: '09:00',
          endTime: '18:00',
          type: 'work',
          status: 'completed'
        },
        {
          id: 2,
          date: '2024-01-15',
          startTime: '12:00',
          endTime: '13:00',
          type: 'break',
          status: 'completed'
        },
        {
          id: 3,
          date: '2024-01-16',
          startTime: '09:00',
          endTime: '18:00',
          type: 'work',
          status: 'scheduled'
        },
        {
          id: 4,
          date: '2024-01-17',
          startTime: '10:00',
          endTime: '11:00',
          type: 'training',
          status: 'scheduled'
        }
      ];

      setStats(mockStats);
      setTasks(mockTasks);
      setSchedule(mockSchedule);
    } catch (error) {
      console.error('직원 데이터 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTaskStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500/20 text-green-600';
      case 'in_progress': return 'bg-blue-500/20 text-blue-600';
      case 'pending': return 'bg-yellow-500/20 text-yellow-600';
      default: return 'bg-gray-500/20 text-gray-600';
    }
  };

  const getTaskPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-500/20 text-red-600';
      case 'medium': return 'bg-yellow-500/20 text-yellow-600';
      case 'low': return 'bg-green-500/20 text-green-600';
      default: return 'bg-gray-500/20 text-gray-600';
    }
  };

  const getScheduleTypeColor = (type: string) => {
    switch (type) {
      case 'work': return 'bg-blue-500/20 text-blue-600';
      case 'break': return 'bg-green-500/20 text-green-600';
      case 'training': return 'bg-purple-500/20 text-purple-600';
      case 'meeting': return 'bg-orange-500/20 text-orange-600';
      default: return 'bg-gray-500/20 text-gray-600';
    }
  };

  const getTaskStatusText = (status: string) => {
    switch (status) {
      case 'completed': return '완료';
      case 'in_progress': return '진행중';
      case 'pending': return '대기중';
      default: return '알 수 없음';
    }
  };

  const getTaskPriorityText = (priority: string) => {
    switch (priority) {
      case 'high': return '높음';
      case 'medium': return '보통';
      case 'low': return '낮음';
      default: return '알 수 없음';
    }
  };

  const getScheduleTypeText = (type: string) => {
    switch (type) {
      case 'work': return '근무';
      case 'break': return '휴식';
      case 'training': return '교육';
      case 'meeting': return '회의';
      default: return '기타';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* 헤더 */}
      <header className="bg-white/10 backdrop-blur-xl border-b border-white/20">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <User className="h-8 w-8 text-blue-400" />
              <div>
                <h1 className="text-2xl font-bold text-white">김직원님</h1>
                <p className="text-slate-300">개인 업무 현황 및 스케줄 관리</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="text-green-400 border-green-400">
                <Activity className="h-4 w-4 mr-1" />
                근무중
              </Badge>
              <div className="text-slate-300 text-sm">
                {new Date().toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">오늘 근무시간</CardTitle>
              <Clock className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.todayWorkHours}h</div>
              <p className="text-xs text-slate-400">오늘 총 근무시간</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">처리 주문</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.totalOrders}</div>
              <p className="text-xs text-slate-400">오늘 처리한 주문</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">고객 평점</CardTitle>
              <Star className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.customerRating}</div>
              <p className="text-xs text-slate-400">평균 고객 만족도</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">성과 점수</CardTitle>
              <Target className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.performanceScore}</div>
              <p className="text-xs text-slate-400">월간 성과 점수</p>
            </CardContent>
          </Card>
        </div>

        {/* 업무 현황 및 스케줄 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 업무 목록 */}
          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <CheckCircle className="h-5 w-5" />
                오늘의 업무
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">
                        {task.category === 'cleaning' ? '🧹' :
                         task.category === 'service' ? '👥' :
                         task.category === 'kitchen' ? '👨‍🍳' : '📋'}
                      </div>
                      <div>
                        <h3 className="font-semibold text-white">{task.title}</h3>
                        <p className="text-sm text-slate-400">{task.description}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge className={getTaskStatusColor(task.status)}>
                            {getTaskStatusText(task.status)}
                          </Badge>
                          <Badge className={getTaskPriorityColor(task.priority)}>
                            {getTaskPriorityText(task.priority)}
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <div className="text-right text-sm text-slate-300">
                      <div>{task.dueDate}</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 스케줄 및 성과 지표 */}
          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                스케줄 및 성과
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* 스케줄 */}
                <div>
                  <h3 className="text-white font-semibold mb-3">이번 주 스케줄</h3>
                  <div className="space-y-2">
                    {schedule.slice(0, 3).map((item) => (
                      <div
                        key={item.id}
                        className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/10"
                      >
                        <div className="flex items-center gap-2">
                          <Badge className={getScheduleTypeColor(item.type)}>
                            {getScheduleTypeText(item.type)}
                          </Badge>
                          <span className="text-white text-sm">
                            {item.startTime} - {item.endTime}
                          </span>
                        </div>
                        <span className="text-slate-300 text-sm">{item.date}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 성과 지표 */}
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-slate-300">출근률</span>
                      <span className="text-white font-semibold">{stats.attendanceRate}%</span>
                    </div>
                    <Progress 
                      value={stats.attendanceRate} 
                      className="h-2"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-slate-300">주간 근무시간</span>
                      <span className="text-white font-semibold">{stats.weeklyWorkHours}h</span>
                    </div>
                    <Progress 
                      value={(stats.weeklyWorkHours / 40) * 100} 
                      className="h-2 bg-slate-700"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-slate-300">초과근무</span>
                      <span className="text-white font-semibold">{stats.overtimeHours}h</span>
                    </div>
                    <Progress 
                      value={25} 
                      className="h-2 bg-slate-700"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 빠른 액션 */}
        <div className="mt-8">
          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Settings className="h-5 w-5" />
                빠른 액션
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button className="p-4 rounded-lg bg-blue-500/20 hover:bg-blue-500/30 transition-colors text-white">
                  <Clock className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">출근 체크</span>
                </button>
                <button className="p-4 rounded-lg bg-green-500/20 hover:bg-green-500/30 transition-colors text-white">
                  <CheckCircle className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">업무 완료</span>
                </button>
                <button className="p-4 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 transition-colors text-white">
                  <Calendar className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">스케줄 확인</span>
                </button>
                <button className="p-4 rounded-lg bg-yellow-500/20 hover:bg-yellow-500/30 transition-colors text-white">
                  <Bell className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">알림 설정</span>
                </button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 