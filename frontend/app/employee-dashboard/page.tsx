'use client';

import React, { useState } from 'react';
import { useEmployees, useSchedules, useAttendance } from '@/hooks/useDashboard';
import DashboardLayout, { StatCard } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  User, 
  Clock, 
  Calendar,
  TrendingUp,
  Activity,
  CheckCircle,
  AlertCircle,
  RefreshCw
} from 'lucide-react';

export default function EmployeeDashboard() {
  const [currentEmployeeId, setCurrentEmployeeId] = useState<number | undefined>(1); // 기본값 설정

  // API 훅 사용
  const { employees, loading: employeesLoading, error: employeesError, refetch: refetchEmployees } = useEmployees(1, 10);
  const { schedules, loading: schedulesLoading, error: schedulesError, refetch: refetchSchedules } = useSchedules(1, 10, new Date().toISOString().split('T')[0], undefined, currentEmployeeId);
  const { attendance, loading: attendanceLoading, error: attendanceError, refetch: refetchAttendance } = useAttendance(1, 10, new Date().toISOString().split('T')[0], undefined, currentEmployeeId);

  const loading = employeesLoading || schedulesLoading || attendanceLoading;
  const error = employeesError || schedulesError || attendanceError;

  // 현재 직원 정보
  const currentEmployee = employees.find(emp => emp.id === currentEmployeeId);

  // 통계 데이터
  const stats = [
    {
      label: '이번 주 근무시간',
      value: `${schedules.reduce((total, schedule) => {
        const start = new Date(schedule.start_time || '');
        const end = new Date(schedule.end_time || '');
        return total + (end.getTime() - start.getTime()) / (1000 * 60 * 60);
      }, 0).toFixed(1)}시간`,
      icon: <Clock className="w-4 h-4" />,
      color: 'text-cyan-400',
      trend: '목표 40시간',
      trendValue: ''
    },
    {
      label: '완료된 업무',
      value: `${schedules.filter(s => s.status === 'completed').length}건`,
      icon: <CheckCircle className="w-4 h-4" />,
      color: 'text-emerald-400',
      trend: '이번 주',
      trendValue: ''
    },
    {
      label: '대기 업무',
      value: `${schedules.filter(s => s.status === 'pending').length}건`,
      icon: <AlertCircle className="w-4 h-4" />,
      color: 'text-orange-400',
      trend: '우선순위 높음',
      trendValue: ''
    },
    {
      label: '성과 점수',
      value: `${Math.floor(Math.random() * 20 + 80)}점`,
      icon: <TrendingUp className="w-4 h-4" />,
      color: 'text-purple-400',
      trend: '+5점 지난주 대비',
      trendValue: ''
    }
  ];

  const actions = [
    {
      label: '새로고침',
      icon: <RefreshCw className="w-4 h-4" />,
      onClick: () => {
        refetchEmployees();
        refetchSchedules();
        refetchAttendance();
      }
    }
  ];

  const handleRefresh = () => {
    refetchEmployees();
    refetchSchedules();
    refetchAttendance();
  };

  return (
    <DashboardLayout
      title="직원 대시보드"
      subtitle="내 근무 현황 및 업무 관리"
      icon={<User className="w-6 h-6" />}
      stats={stats}
      actions={actions}
      onRefresh={handleRefresh}
      loading={loading}
    >
      {/* 메인 콘텐츠 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 오늘 근무표 */}
        <Card className="bg-black/50 border-cyan-500/20 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-cyan-400 flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              오늘 근무표
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {schedules.slice(0, 3).map((schedule, index) => (
              <div key={schedule.id || index} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                <div>
                  <p className="text-lg font-semibold text-white">
                    {new Date(schedule.start_time || '').toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })} - 
                    {new Date(schedule.end_time || '').toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}
                  </p>
                  <p className="text-sm text-slate-400">{schedule.role || '정규 근무'}</p>
                </div>
                <Badge 
                  className={
                    schedule.status === 'completed' 
                      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50'
                      : schedule.status === 'in_progress'
                      ? 'bg-blue-500/20 text-blue-400 border-blue-500/50'
                      : 'bg-orange-500/20 text-orange-400 border-orange-500/50'
                  }
                >
                  {schedule.status === 'completed' ? '완료' : schedule.status === 'in_progress' ? '진행중' : '대기'}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* 출근 기록 */}
        <Card className="bg-black/50 border-emerald-500/20 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-emerald-400 flex items-center gap-2">
              <Activity className="h-5 w-5" />
              출근 기록
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {attendance.slice(0, 5).map((record, index) => (
              <div key={record.id || index} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center">
                    <CheckCircle className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-300">
                      {new Date(record.date || '').toLocaleDateString('ko-KR')}
                    </p>
                    <p className="text-xs text-slate-400">
                      {new Date(record.check_in_time || '').toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })} - 
                      {record.check_out_time ? new Date(record.check_out_time).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }) : '미퇴근'}
                    </p>
                  </div>
                </div>
                <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50">
                  {record.status === 'present' ? '출근' : record.status === 'absent' ? '결근' : '지각'}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* 업무 현황 */}
      <Card className="bg-black/50 border-purple-500/20 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-purple-400 flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            업무 현황
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-slate-800/50 rounded-lg text-center">
              <div className="text-2xl font-bold text-emerald-400 mb-2">
                {schedules.filter(s => s.status === 'completed').length}
              </div>
              <p className="text-sm text-slate-300">완료된 업무</p>
            </div>
            <div className="p-4 bg-slate-800/50 rounded-lg text-center">
              <div className="text-2xl font-bold text-blue-400 mb-2">
                {schedules.filter(s => s.status === 'in_progress').length}
              </div>
              <p className="text-sm text-slate-300">진행중인 업무</p>
            </div>
            <div className="p-4 bg-slate-800/50 rounded-lg text-center">
              <div className="text-2xl font-bold text-orange-400 mb-2">
                {schedules.filter(s => s.status === 'pending').length}
              </div>
              <p className="text-sm text-slate-300">대기중인 업무</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </DashboardLayout>
  );
} 