'use client';

import { memo, useMemo, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar, Clock, User, Building, MapPin, Phone, Mail } from 'lucide-react';

// 직원 정보 타입 정의
interface EmployeeInfo {
  id: number;
  name: string;
  employee_id: string;
  position: string;
  department: string;
  branch: {
    id: number;
    name: string;
    address: string;
  };
  contact: {
    phone: string;
    email: string;
  };
  schedule: {
    today: string;
    start_time: string;
    end_time: string;
    status: 'scheduled' | 'working' | 'completed' | 'absent';
  };
  stats: {
    total_work_hours: number;
    this_month_hours: number;
    attendance_rate: number;
    overtime_hours: number;
  };
}

// 근무 일정 타입 정의
interface WorkSchedule {
  id: number;
  date: string;
  start_time: string;
  end_time: string;
  status: 'scheduled' | 'working' | 'completed' | 'absent';
  notes?: string;
}

interface LazyEmployeeDashboardProps {
  employeeInfo: EmployeeInfo;
  workSchedule: WorkSchedule[];
  currentTime: Date;
  onClockIn: () => void;
  onClockOut: () => void;
  isLoading?: boolean;
}

// 상태 배지 컴포넌트 (메모이제이션)
const StatusBadge = memo(({ status }: { status: string }) => {
  const badgeConfig = useMemo(() => {
    switch (status) {
      case 'working':
        return { className: "bg-green-500", text: "근무중" };
      case 'completed':
        return { className: "bg-blue-500", text: "완료" };
      case 'scheduled':
        return { className: "bg-gray-500", text: "예정" };
      case 'absent':
        return { className: "bg-red-500", text: "결근" };
      default:
        return { className: "outline", text: "알 수 없음" };
    }
  }, [status]);

  return (
    <Badge className={badgeConfig.className} variant={badgeConfig.className === "outline" ? "outline" : "default"}>
      {badgeConfig.text}
    </Badge>
  );
});

StatusBadge.displayName = 'StatusBadge';

// 직원 정보 카드 (메모이제이션)
const EmployeeInfoCard = memo(({ employeeInfo }: { employeeInfo: EmployeeInfo }) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <User className="h-5 w-5" />
        직원 정보
      </CardTitle>
    </CardHeader>
    <CardContent>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-500">이름</p>
          <p className="text-lg font-semibold">{employeeInfo.name}</p>
        </div>
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-500">사원번호</p>
          <p className="text-lg font-semibold">{employeeInfo.employee_id}</p>
        </div>
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-500">직급</p>
          <p className="text-lg font-semibold">{employeeInfo.position}</p>
        </div>
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-500">부서</p>
          <p className="text-lg font-semibold">{employeeInfo.department}</p>
        </div>
      </div>
    </CardContent>
  </Card>
));

EmployeeInfoCard.displayName = 'EmployeeInfoCard';

// 근무 정보 카드 (메모이제이션)
const WorkInfoCard = memo(({ 
  employeeInfo, 
  onClockIn, 
  onClockOut 
}: { 
  employeeInfo: EmployeeInfo;
  onClockIn: () => void;
  onClockOut: () => void;
}) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Clock className="h-5 w-5" />
        오늘 근무
      </CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-500">근무 시간</span>
        <span className="font-semibold">
          {employeeInfo.schedule.start_time} - {employeeInfo.schedule.end_time}
        </span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-500">상태</span>
        <StatusBadge status={employeeInfo.schedule.status} />
      </div>
      <div className="flex gap-2">
        <Button 
          onClick={onClockIn}
          disabled={employeeInfo.schedule.status === 'working' || employeeInfo.schedule.status === 'completed'}
          className="flex-1"
        >
          출근
        </Button>
        <Button 
          onClick={onClockOut}
          disabled={employeeInfo.schedule.status === 'scheduled' || employeeInfo.schedule.status === 'completed'}
          variant="outline"
          className="flex-1"
        >
          퇴근
        </Button>
      </div>
    </CardContent>
  </Card>
));

WorkInfoCard.displayName = 'WorkInfoCard';

// 통계 카드 (메모이제이션)
const StatsCard = memo(({ employeeInfo }: { employeeInfo: EmployeeInfo }) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Calendar className="h-5 w-5" />
        근무 통계
      </CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-500">이번 달 근무시간</span>
        <span className="font-semibold">{employeeInfo.stats.this_month_hours}시간</span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-500">출근률</span>
        <span className="font-semibold">{employeeInfo.stats.attendance_rate}%</span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-500">초과근무</span>
        <span className="font-semibold">{employeeInfo.stats.overtime_hours}시간</span>
      </div>
    </CardContent>
  </Card>
));

StatsCard.displayName = 'StatsCard';

// 지점 정보 카드 (메모이제이션)
const BranchInfoCard = memo(({ employeeInfo }: { employeeInfo: EmployeeInfo }) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Building className="h-5 w-5" />
        근무 지점
      </CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="space-y-2">
        <p className="font-semibold">{employeeInfo.branch.name}</p>
        <p className="text-sm text-gray-600 flex items-center gap-1">
          <MapPin className="h-4 w-4" />
          {employeeInfo.branch.address}
        </p>
      </div>
      <div className="space-y-2">
        <p className="text-sm text-gray-500 flex items-center gap-1">
          <Phone className="h-4 w-4" />
          {employeeInfo.contact.phone}
        </p>
        <p className="text-sm text-gray-500 flex items-center gap-1">
          <Mail className="h-4 w-4" />
          {employeeInfo.contact.email}
        </p>
      </div>
    </CardContent>
  </Card>
));

BranchInfoCard.displayName = 'BranchInfoCard';

// 근무 일정 카드 (메모이제이션)
const ScheduleCard = memo(({ workSchedule }: { workSchedule: WorkSchedule[] }) => (
  <Card>
    <CardHeader>
      <CardTitle>근무 일정</CardTitle>
    </CardHeader>
    <CardContent>
      <div className="space-y-4">
        {workSchedule.map((schedule) => (
          <div key={schedule.id} className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-4">
              <div className="text-center">
                <p className="text-sm text-gray-500">날짜</p>
                <p className="font-semibold">
                  {new Date(schedule.date).toLocaleDateString('ko-KR', { 
                    month: 'short', 
                    day: 'numeric',
                    weekday: 'short'
                  })}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-500">시간</p>
                <p className="font-semibold">{schedule.start_time} - {schedule.end_time}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <StatusBadge status={schedule.status} />
              {schedule.notes && (
                <p className="text-sm text-gray-600">{schedule.notes}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </CardContent>
  </Card>
));

ScheduleCard.displayName = 'ScheduleCard';

// 메인 컴포넌트 (메모이제이션)
const LazyEmployeeDashboard = memo(({
  employeeInfo,
  workSchedule,
  currentTime,
  onClockIn,
  onClockOut,
  isLoading = false
}: LazyEmployeeDashboardProps) => {
  // 현재 시간 포맷팅 (메모이제이션)
  const formattedTime = useMemo(() => ({
    date: currentTime.toLocaleDateString('ko-KR', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      weekday: 'long'
    }),
    time: currentTime.toLocaleTimeString('ko-KR')
  }), [currentTime]);

  // 출근/퇴근 핸들러 (메모이제이션)
  const handleClockIn = useCallback(() => {
    onClockIn();
  }, [onClockIn]);

  const handleClockOut = useCallback(() => {
    onClockOut();
  }, [onClockOut]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">직원 정보를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (!employeeInfo) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-500">직원 정보를 찾을 수 없습니다.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* 헤더 */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">직원 대시보드</h1>
            <p className="text-gray-600 mt-1">
              {formattedTime.date} {formattedTime.time}
            </p>
          </div>
        </div>

        {/* 직원 정보 카드 */}
        <EmployeeInfoCard employeeInfo={employeeInfo} />

        {/* 근무 정보 및 출퇴근 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <WorkInfoCard 
            employeeInfo={employeeInfo} 
            onClockIn={handleClockIn}
            onClockOut={handleClockOut}
          />
          <StatsCard employeeInfo={employeeInfo} />
          <BranchInfoCard employeeInfo={employeeInfo} />
        </div>

        {/* 근무 일정 */}
        <ScheduleCard workSchedule={workSchedule} />
      </div>
    </div>
  );
});

LazyEmployeeDashboard.displayName = 'LazyEmployeeDashboard';

export default LazyEmployeeDashboard; 