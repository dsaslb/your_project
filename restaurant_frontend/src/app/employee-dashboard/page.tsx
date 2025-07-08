"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { 
  User, 
  Clock, 
  Calendar, 
  CheckCircle, 
  AlertTriangle,
  TrendingUp,
  Star,
  Target,
  Award,
  Bell,
  Settings,
  LogOut,
  LogIn,
  Coffee,
  Briefcase,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight
} from "lucide-react";

interface EmployeeData {
  id: number;
  name: string;
  role: string;
  department: string;
  employeeId: string;
  joinDate: string;
  avatar: string;
}

interface WorkSchedule {
  date: string;
  dayOfWeek: string;
  startTime: string;
  endTime: string;
  status: 'scheduled' | 'working' | 'completed' | 'off' | 'late';
  totalHours: number;
}

interface WorkStats {
  totalWorkDays: number;
  totalWorkHours: number;
  averageWorkHours: number;
  overtimeHours: number;
  attendanceRate: number;
  lateCount: number;
  earlyLeaveCount: number;
  performanceScore: number;
}

interface TaskData {
  id: number;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'in-progress' | 'completed';
  dueDate: string;
  assignedBy: string;
}

export default function EmployeeDashboard() {
  const [employee, setEmployee] = useState<EmployeeData>({
    id: 1,
    name: "김철수",
    role: "서버",
    department: "서빙팀",
    employeeId: "EMP001",
    joinDate: "2023-03-15",
    avatar: "KC"
  });

  const [workStats, setWorkStats] = useState<WorkStats>({
    totalWorkDays: 22,
    totalWorkHours: 176,
    averageWorkHours: 8.0,
    overtimeHours: 12,
    attendanceRate: 95.5,
    lateCount: 1,
    earlyLeaveCount: 0,
    performanceScore: 4.2
  });

  const [currentSchedule, setCurrentSchedule] = useState<WorkSchedule>({
    date: "2024-01-15",
    dayOfWeek: "월요일",
    startTime: "09:00",
    endTime: "18:00",
    status: 'working',
    totalHours: 8
  });

  const [weeklySchedule, setWeeklySchedule] = useState<WorkSchedule[]>([
    { date: "2024-01-15", dayOfWeek: "월", startTime: "09:00", endTime: "18:00", status: 'working', totalHours: 8 },
    { date: "2024-01-16", dayOfWeek: "화", startTime: "10:00", endTime: "19:00", status: 'scheduled', totalHours: 8 },
    { date: "2024-01-17", dayOfWeek: "수", startTime: "09:00", endTime: "18:00", status: 'scheduled', totalHours: 8 },
    { date: "2024-01-18", dayOfWeek: "목", startTime: "11:00", endTime: "20:00", status: 'scheduled', totalHours: 8 },
    { date: "2024-01-19", dayOfWeek: "금", startTime: "09:00", endTime: "18:00", status: 'scheduled', totalHours: 8 },
    { date: "2024-01-20", dayOfWeek: "토", startTime: "10:00", endTime: "19:00", status: 'scheduled', totalHours: 8 },
    { date: "2024-01-21", dayOfWeek: "일", startTime: "", endTime: "", status: 'off', totalHours: 0 }
  ]);

  const [tasks, setTasks] = useState<TaskData[]>([
    { id: 1, title: "테이블 정리", description: "1-5번 테이블 청소 및 정리", priority: 'high', status: 'completed', dueDate: "2024-01-15", assignedBy: "매니저" },
    { id: 2, title: "주문 확인", description: "새로운 주문 확인 및 처리", priority: 'high', status: 'in-progress', dueDate: "2024-01-15", assignedBy: "매니저" },
    { id: 3, title: "재고 확인", description: "서빙용품 재고 상태 확인", priority: 'medium', status: 'pending', dueDate: "2024-01-16", assignedBy: "매니저" },
    { id: 4, title: "고객 응대", description: "VIP 고객 특별 서비스", priority: 'high', status: 'pending', dueDate: "2024-01-15", assignedBy: "매니저" }
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'working': return 'bg-green-500';
      case 'scheduled': return 'bg-blue-500';
      case 'completed': return 'bg-gray-500';
      case 'off': return 'bg-red-500';
      case 'late': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'working': return '근무중';
      case 'scheduled': return '예정';
      case 'completed': return '완료';
      case 'off': return '휴무';
      case 'late': return '지각';
      default: return '알 수 없음';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'high': return '높음';
      case 'medium': return '보통';
      case 'low': return '낮음';
      default: return '알 수 없음';
    }
  };

  const getTaskStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-500';
      case 'in-progress': return 'bg-blue-500';
      case 'completed': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getTaskStatusText = (status: string) => {
    switch (status) {
      case 'pending': return '대기중';
      case 'in-progress': return '진행중';
      case 'completed': return '완료';
      default: return '알 수 없음';
    }
  };

  const formatTime = (time: string) => {
    if (!time) return "휴무";
    return time;
  };

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">직원 대시보드</h1>
          <p className="text-gray-600 dark:text-gray-400">개인 업무 현황 및 스케줄 관리</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${getStatusColor(currentSchedule.status)}`} />
            <span className="text-sm font-medium">{getStatusText(currentSchedule.status)}</span>
          </div>
          <Button variant="outline">
            <Settings className="h-4 w-4 mr-2" />
            설정
          </Button>
        </div>
      </div>

      {/* 직원 정보 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <User className="h-5 w-5 mr-2" />
            직원 정보
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold text-xl">
              {employee.avatar}
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-semibold">{employee.name}</h3>
              <p className="text-gray-600">{employee.role} • {employee.department}</p>
              <p className="text-sm text-gray-500">사번: {employee.employeeId} | 입사일: {employee.joinDate}</p>
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-1">
                <Star className="h-4 w-4 text-yellow-500" />
                <span className="font-semibold">{workStats.performanceScore}</span>
              </div>
              <p className="text-sm text-gray-500">성과 점수</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 오늘의 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">출근률</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{workStats.attendanceRate}%</div>
            <p className="text-xs text-muted-foreground">
              지각: {workStats.lateCount}회 | 조퇴: {workStats.earlyLeaveCount}회
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 근무시간</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{workStats.totalWorkHours}h</div>
            <p className="text-xs text-muted-foreground">
              평균: {workStats.averageWorkHours}h/일 | 초과: {workStats.overtimeHours}h
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">완료된 업무</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tasks.filter(t => t.status === 'completed').length}</div>
            <p className="text-xs text-muted-foreground">
              총 {tasks.length}개 중 완료
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">오늘 스케줄</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatTime(currentSchedule.startTime)}</div>
            <p className="text-xs text-muted-foreground">
              {currentSchedule.dayOfWeek} • {formatTime(currentSchedule.endTime)}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 주간 스케줄 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Calendar className="h-5 w-5 mr-2" />
            이번 주 스케줄
          </CardTitle>
          <CardDescription>주간 근무 일정 및 시간</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-7 gap-2">
            {weeklySchedule.map((schedule, index) => (
              <div key={index} className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <p className="text-sm font-medium">{schedule.dayOfWeek}</p>
                <p className="text-xs text-muted-foreground">{schedule.date.split('-')[2]}</p>
                <div className="mt-2">
                  <div className={`w-3 h-3 rounded-full mx-auto ${getStatusColor(schedule.status)}`} />
                  <p className="text-xs mt-1">{getStatusText(schedule.status)}</p>
                </div>
                {schedule.status !== 'off' && (
                  <div className="mt-1 text-xs">
                    <p>{formatTime(schedule.startTime)}</p>
                    <p>{formatTime(schedule.endTime)}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 업무 현황 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Briefcase className="h-5 w-5 mr-2" />
              할당된 업무
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {tasks.map((task) => (
                <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${getPriorityColor(task.priority)}`} />
                      <span className="font-medium">{task.title}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">{task.description}</p>
                    <p className="text-xs text-muted-foreground">
                      담당: {task.assignedBy} • 마감: {task.dueDate}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${getTaskStatusColor(task.status)}`} />
                      <span className="text-xs">{getTaskStatusText(task.status)}</span>
                    </div>
                    <Badge variant="outline" className="text-xs mt-1">
                      {getPriorityText(task.priority)}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="h-5 w-5 mr-2" />
              근무 통계
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">출근률</span>
                <span className="font-medium">{workStats.attendanceRate}%</span>
              </div>
              <Progress value={workStats.attendanceRate} className="h-2" />
              
              <div className="flex items-center justify-between">
                <span className="text-sm">업무 완료율</span>
                <span className="font-medium">
                  {Math.round((tasks.filter(t => t.status === 'completed').length / tasks.length) * 100)}%
                </span>
              </div>
              <Progress value={(tasks.filter(t => t.status === 'completed').length / tasks.length) * 100} className="h-2" />
              
              <div className="flex items-center justify-between">
                <span className="text-sm">평균 근무시간</span>
                <span className="font-medium">{workStats.averageWorkHours}h</span>
              </div>
              <Progress value={(workStats.averageWorkHours / 10) * 100} className="h-2" />
              
              <div className="flex items-center justify-between">
                <span className="text-sm">성과 점수</span>
                <span className="font-medium">{workStats.performanceScore}/5.0</span>
              </div>
              <Progress value={(workStats.performanceScore / 5) * 100} className="h-2" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 알림 및 공지 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Bell className="h-5 w-5 mr-2" />
            개인 알림
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center space-x-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <Award className="h-4 w-4 text-blue-600" />
              <div>
                <p className="font-medium">우수 직원 선정</p>
                <p className="text-sm text-muted-foreground">이번 달 우수 직원으로 선정되었습니다. 축하합니다!</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
              <div>
                <p className="font-medium">업무 마감 알림</p>
                <p className="text-sm text-muted-foreground">오늘 할당된 업무 중 2개가 아직 완료되지 않았습니다.</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <div>
                <p className="font-medium">근무 시간 달성</p>
                <p className="text-sm text-muted-foreground">이번 주 목표 근무 시간을 달성했습니다.</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 빠른 액션 */}
      <Card>
        <CardHeader>
          <CardTitle>빠른 액션</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-16 flex flex-col space-y-2">
              <LogIn className="h-5 w-5" />
              <span className="text-sm">출근 체크</span>
            </Button>
            <Button variant="outline" className="h-16 flex flex-col space-y-2">
              <Coffee className="h-5 w-5" />
              <span className="text-sm">휴식 시작</span>
            </Button>
            <Button variant="outline" className="h-16 flex flex-col space-y-2">
              <LogOut className="h-5 w-5" />
              <span className="text-sm">퇴근 체크</span>
            </Button>
            <Button variant="outline" className="h-16 flex flex-col space-y-2">
              <Settings className="h-5 w-5" />
              <span className="text-sm">설정</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 