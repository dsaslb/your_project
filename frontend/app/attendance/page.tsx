'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Clock, 
  Search, 
  Calendar,
  User,
  CheckCircle,
  XCircle,
  AlertTriangle,
  TrendingUp,
  Users
} from 'lucide-react';

interface Attendance {
  id: number;
  employee_name: string;
  employee_id: string;
  date: string;
  check_in: string;
  check_out: string;
  status: 'present' | 'absent' | 'late' | 'early_leave';
  work_hours: number;
  overtime_hours: number;
  notes: string;
}

export default function AttendancePage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  // 샘플 데이터
  const attendanceData: Attendance[] = [
    {
      id: 1,
      employee_name: '김철수',
      employee_id: 'EMP001',
      date: '2024-01-15',
      check_in: '09:00',
      check_out: '18:00',
      status: 'present',
      work_hours: 8,
      overtime_hours: 0,
      notes: ''
    },
    {
      id: 2,
      employee_name: '이영희',
      employee_id: 'EMP002',
      date: '2024-01-15',
      check_in: '09:15',
      check_out: '18:00',
      status: 'late',
      work_hours: 7.75,
      overtime_hours: 0,
      notes: '지하철 지연'
    },
    {
      id: 3,
      employee_name: '박민수',
      employee_id: 'EMP003',
      date: '2024-01-15',
      check_in: '09:00',
      check_out: '17:00',
      status: 'early_leave',
      work_hours: 7,
      overtime_hours: 0,
      notes: '개인 사정'
    },
    {
      id: 4,
      employee_name: '최지영',
      employee_id: 'EMP004',
      date: '2024-01-15',
      check_in: '',
      check_out: '',
      status: 'absent',
      work_hours: 0,
      overtime_hours: 0,
      notes: '병가'
    }
  ];

  const filteredAttendance = attendanceData.filter(attendance => {
    const matchesSearch = attendance.employee_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         attendance.employee_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || attendance.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'present':
        return <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50">정상출근</Badge>;
      case 'late':
        return <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/50">지각</Badge>;
      case 'early_leave':
        return <Badge className="bg-orange-500/20 text-orange-400 border-orange-500/50">조퇴</Badge>;
      case 'absent':
        return <Badge className="bg-red-500/20 text-red-400 border-red-500/50">결근</Badge>;
      default:
        return <Badge className="bg-slate-500/20 text-slate-400 border-slate-500/50">알 수 없음</Badge>;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'present':
        return <CheckCircle className="h-4 w-4 text-emerald-400" />;
      case 'late':
        return <AlertTriangle className="h-4 w-4 text-yellow-400" />;
      case 'early_leave':
        return <AlertTriangle className="h-4 w-4 text-orange-400" />;
      case 'absent':
        return <XCircle className="h-4 w-4 text-red-400" />;
      default:
        return <Clock className="h-4 w-4 text-slate-400" />;
    }
  };

  const stats = {
    total: attendanceData.length,
    present: attendanceData.filter(a => a.status === 'present').length,
    late: attendanceData.filter(a => a.status === 'late').length,
    absent: attendanceData.filter(a => a.status === 'absent').length,
    averageHours: Math.round(attendanceData.reduce((acc, a) => acc + a.work_hours, 0) / attendanceData.length * 10) / 10
  };

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent">
            출근 관리
          </h1>
          <p className="text-slate-400 mt-2">직원 출근 현황 및 관리</p>
        </div>
        <div className="flex items-center gap-4">
          <Button className="bg-cyan-500/20 text-cyan-400 border-cyan-500/50 hover:bg-cyan-500/30">
            <Calendar className="h-4 w-4 mr-2" />
            출근 기록
          </Button>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-black/50 border-emerald-500/20 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">전체 직원</CardTitle>
            <Users className="h-4 w-4 text-emerald-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-400">{stats.total}명</div>
            <p className="text-xs text-emerald-400">등록된 직원</p>
          </CardContent>
        </Card>

        <Card className="bg-black/50 border-emerald-500/20 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">정상출근</CardTitle>
            <CheckCircle className="h-4 w-4 text-emerald-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-400">{stats.present}명</div>
            <p className="text-xs text-emerald-400">정시 출근</p>
          </CardContent>
        </Card>

        <Card className="bg-black/50 border-yellow-500/20 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">지각</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-400">{stats.late}명</div>
            <p className="text-xs text-yellow-400">지각자</p>
          </CardContent>
        </Card>

        <Card className="bg-black/50 border-cyan-500/20 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">평균 근무시간</CardTitle>
            <TrendingUp className="h-4 w-4 text-cyan-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-cyan-400">{stats.averageHours}시간</div>
            <p className="text-xs text-cyan-400">일평균</p>
          </CardContent>
        </Card>
      </div>

      {/* 필터 및 검색 */}
      <Card className="bg-black/50 border-cyan-500/20 backdrop-blur-xl">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="직원명 또는 사번으로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-slate-800/50 border-slate-600 text-white"
              />
            </div>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-md text-white"
            />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-md text-white"
            >
              <option value="all">전체 상태</option>
              <option value="present">정상출근</option>
              <option value="late">지각</option>
              <option value="early_leave">조퇴</option>
              <option value="absent">결근</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* 출근 목록 */}
      <div className="space-y-4">
        {filteredAttendance.map((attendance) => (
          <Card key={attendance.id} className="bg-black/50 border-slate-500/20 backdrop-blur-xl hover:border-cyan-500/50 transition-all duration-300">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {getStatusIcon(attendance.status)}
                  <div>
                    <CardTitle className="text-white flex items-center gap-2">
                      <User className="h-4 w-4" />
                      {attendance.employee_name}
                    </CardTitle>
                    <p className="text-sm text-slate-400">{attendance.employee_id}</p>
                  </div>
                </div>
                {getStatusBadge(attendance.status)}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* 출근 정보 */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-slate-400 text-sm">출근 시간</p>
                  <p className="text-white font-semibold">
                    {attendance.check_in || '-'}
                  </p>
                </div>
                <div>
                  <p className="text-slate-400 text-sm">퇴근 시간</p>
                  <p className="text-white font-semibold">
                    {attendance.check_out || '-'}
                  </p>
                </div>
                <div>
                  <p className="text-slate-400 text-sm">근무 시간</p>
                  <p className="text-white font-semibold">
                    {attendance.work_hours}시간
                  </p>
                </div>
                <div>
                  <p className="text-slate-400 text-sm">초과 근무</p>
                  <p className="text-white font-semibold">
                    {attendance.overtime_hours}시간
                  </p>
                </div>
              </div>

              {/* 비고 */}
              {attendance.notes && (
                <div className="bg-slate-800/30 rounded-lg p-3">
                  <p className="text-sm text-slate-300">
                    <span className="font-medium">비고:</span> {attendance.notes}
                  </p>
                </div>
              )}

              {/* 액션 버튼 */}
              <div className="flex gap-2">
                <Button size="sm" className="flex-1 bg-blue-500/20 text-blue-400 border-blue-500/50 hover:bg-blue-500/30">
                  상세 보기
                </Button>
                <Button size="sm" variant="outline" className="border-slate-500/50 text-slate-400 hover:bg-slate-500/10">
                  수정
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredAttendance.length === 0 && (
        <Card className="bg-black/50 border-slate-500/20 backdrop-blur-xl">
          <CardContent className="p-12 text-center">
            <Clock className="h-12 w-12 text-slate-400 mx-auto mb-4" />
            <p className="text-slate-400">출근 기록이 없습니다.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 