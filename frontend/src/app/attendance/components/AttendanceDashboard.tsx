"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Calendar, Clock, Users, TrendingUp, Settings, Plus, Download } from "lucide-react";
import { toast } from "sonner";
import TestDataGenerator from "./TestDataGenerator";

interface AttendanceRecord {
  id: string;
  user_id: number;
  user_name: string;
  user_position: string;
  date: string;
  clock_in: string;
  clock_out: string;
  work_type: string;
  note: string;
  is_late: boolean;
  is_early_leave: boolean;
  overtime_hours: number;
  created_at: string;
  updated_at: string;
}

interface AttendanceStatistics {
  total_records: number;
  total_work_hours: number;
  avg_work_hours: number;
  late_count: number;
  early_leave_count: number;
  absent_count: number;
  overtime_hours: number;
}

interface AttendanceSettings {
  brand_id: number;
  branch_id: number | null;
  work_start_time: string;
  work_end_time: string;
  late_threshold_minutes: number;
  overtime_threshold_hours: number;
  auto_notification: boolean;
  notification_interval: number;
  work_types: string[];
  is_active: boolean;
}

const AttendanceDashboard: React.FC = () => {
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [statistics, setStatistics] = useState<AttendanceStatistics | null>(null);
  const [settings, setSettings] = useState<AttendanceSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedUser, setSelectedUser] = useState<number | null>(null);

  // 데이터 로드
  useEffect(() => {
    loadData();
  }, [selectedDate, selectedUser]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // 출퇴근 기록 조회
      const recordsParams = new URLSearchParams({
        start_date: selectedDate,
        end_date: selectedDate,
        page: '1',
        per_page: '50'
      });
      
      if (selectedUser) {
        recordsParams.append('user_id', selectedUser.toString());
      }
      
      const recordsResponse = await fetch(`/api/attendance/records?${recordsParams}`);
      const recordsData = await recordsResponse.json();
      
      if (recordsData.success) {
        setRecords(recordsData.records);
      }
      
      // 통계 조회
      const statsParams = new URLSearchParams({
        start_date: selectedDate,
        end_date: selectedDate
      });
      
      if (selectedUser) {
        statsParams.append('user_id', selectedUser.toString());
      }
      
      const statsResponse = await fetch(`/api/attendance/statistics?${statsParams}`);
      const statsData = await statsResponse.json();
      
      if (statsData.success) {
        setStatistics(statsData.statistics);
      }
      
      // 설정 조회
      const settingsResponse = await fetch('/api/attendance/settings');
      const settingsData = await settingsResponse.json();
      
      if (settingsData.success) {
        setSettings(settingsData.settings);
      }
      
    } catch (error) {
      console.error('데이터 로드 오류:', error);
      toast.error('데이터를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleClockIn = async (userId: number) => {
    try {
      const response = await fetch('/api/attendance/clock-in', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          work_type: '정규',
          note: ''
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        toast.success('출근이 기록되었습니다.');
        loadData();
      } else {
        toast.error(data.error || '출근 기록에 실패했습니다.');
      }
    } catch (error) {
      console.error('출근 기록 오류:', error);
      toast.error('출근 기록 중 오류가 발생했습니다.');
    }
  };

  const handleClockOut = async (userId: number) => {
    try {
      const response = await fetch('/api/attendance/clock-out', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          note: ''
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        toast.success('퇴근이 기록되었습니다.');
        loadData();
      } else {
        toast.error(data.error || '퇴근 기록에 실패했습니다.');
      }
    } catch (error) {
      console.error('퇴근 기록 오류:', error);
      toast.error('퇴근 기록 중 오류가 발생했습니다.');
    }
  };

  const getStatusBadge = (record: AttendanceRecord) => {
    if (!record.clock_in) {
      return <Badge variant="destructive">미출근</Badge>;
    }
    
    if (!record.clock_out) {
      return <Badge variant="default">근무중</Badge>;
    }
    
    if (record.is_late && record.is_early_leave) {
      return <Badge variant="destructive">지각+조퇴</Badge>;
    }
    
    if (record.is_late) {
      return <Badge variant="destructive">지각</Badge>;
    }
    
    if (record.is_early_leave) {
      return <Badge variant="secondary">조퇴</Badge>;
    }
    
    return <Badge variant="default">정상</Badge>;
  };

  const calculateWorkHours = (clockIn: string, clockOut: string) => {
    if (!clockIn || !clockOut) return 0;
    
    const start = new Date(`2000-01-01T${clockIn}:00`);
    const end = new Date(`2000-01-01T${clockOut}:00`);
    
    if (end < start) {
      end.setDate(end.getDate() + 1);
    }
    
    const diff = end.getTime() - start.getTime();
    return Math.round((diff / (1000 * 60 * 60)) * 10) / 10;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">데이터를 불러오는 중...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">출퇴근 관리</h1>
          <p className="text-gray-600 dark:text-gray-400">
            직원별 출근/퇴근/지각/초과근무 기록 및 통계 관리
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => loadData()}>
            <Clock className="w-4 h-4 mr-2" />
            새로고침
          </Button>
          <Button>
            <Download className="w-4 h-4 mr-2" />
            내보내기
          </Button>
        </div>
      </div>

      {/* 통계 카드 */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 기록</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_records}</div>
              <p className="text-xs text-muted-foreground">
                오늘 출퇴근 기록
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 근무시간</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_work_hours}h</div>
              <p className="text-xs text-muted-foreground">
                평균 {statistics.avg_work_hours}h/인
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">지각/조퇴</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.late_count + statistics.early_leave_count}</div>
              <p className="text-xs text-muted-foreground">
                지각 {statistics.late_count} / 조퇴 {statistics.early_leave_count}
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">초과근무</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.overtime_hours}h</div>
              <p className="text-xs text-muted-foreground">
                총 초과근무 시간
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 메인 콘텐츠 */}
      <Tabs defaultValue="dashboard" className="space-y-4">
        <TabsList>
          <TabsTrigger value="dashboard">대시보드</TabsTrigger>
          <TabsTrigger value="records">상세 내역</TabsTrigger>
          <TabsTrigger value="statistics">월별 통계</TabsTrigger>
          <TabsTrigger value="settings">설정</TabsTrigger>
        </TabsList>

        {/* 대시보드 탭 */}
        <TabsContent value="dashboard" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>오늘의 출퇴근 현황</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {records.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    오늘의 출퇴근 기록이 없습니다.
                  </div>
                ) : (
                  <div className="grid gap-4">
                    {records.map((record) => (
                      <div key={record.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center space-x-4">
                          <div>
                            <div className="font-medium">{record.user_name}</div>
                            <div className="text-sm text-gray-500">{record.user_position}</div>
                          </div>
                          <div className="text-sm">
                            <div>출근: {record.clock_in || '미출근'}</div>
                            <div>퇴근: {record.clock_out || '미퇴근'}</div>
                            {record.clock_in && record.clock_out && (
                              <div>근무시간: {calculateWorkHours(record.clock_in, record.clock_out)}h</div>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {getStatusBadge(record)}
                          <div className="flex space-x-1">
                            {!record.clock_in && (
                              <Button size="sm" onClick={() => handleClockIn(record.user_id)}>
                                출근
                              </Button>
                            )}
                            {record.clock_in && !record.clock_out && (
                              <Button size="sm" variant="outline" onClick={() => handleClockOut(record.user_id)}>
                                퇴근
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 상세 내역 탭 */}
        <TabsContent value="records" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>출퇴근 상세 내역</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">직원명</th>
                      <th className="text-left p-2">직책</th>
                      <th className="text-left p-2">날짜</th>
                      <th className="text-left p-2">출근시간</th>
                      <th className="text-left p-2">퇴근시간</th>
                      <th className="text-left p-2">근무시간</th>
                      <th className="text-left p-2">상태</th>
                      <th className="text-left p-2">초과근무</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map((record) => (
                      <tr key={record.id} className="border-b">
                        <td className="p-2">{record.user_name}</td>
                        <td className="p-2">{record.user_position}</td>
                        <td className="p-2">{record.date}</td>
                        <td className="p-2">{record.clock_in || '-'}</td>
                        <td className="p-2">{record.clock_out || '-'}</td>
                        <td className="p-2">
                          {record.clock_in && record.clock_out 
                            ? `${calculateWorkHours(record.clock_in, record.clock_out)}h`
                            : '-'
                          }
                        </td>
                        <td className="p-2">{getStatusBadge(record)}</td>
                        <td className="p-2">{record.overtime_hours}h</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 월별 통계 탭 */}
        <TabsContent value="statistics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>월별 통계</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                월별 통계 기능은 추후 구현 예정입니다.
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 설정 탭 */}
        <TabsContent value="settings" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>출퇴근 설정</CardTitle>
              </CardHeader>
              <CardContent>
                {settings ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium">기본 출근시간</label>
                        <div className="text-lg">{settings.work_start_time}</div>
                      </div>
                      <div>
                        <label className="text-sm font-medium">기본 퇴근시간</label>
                        <div className="text-lg">{settings.work_end_time}</div>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium">지각 기준 (분)</label>
                        <div className="text-lg">{settings.late_threshold_minutes}분</div>
                      </div>
                      <div>
                        <label className="text-sm font-medium">초과근무 기준 (시간)</label>
                        <div className="text-lg">{settings.overtime_threshold_hours}시간</div>
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-medium">근무 유형</label>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {settings.work_types.map((type) => (
                          <Badge key={type} variant="outline">{type}</Badge>
                        ))}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={settings.auto_notification}
                        readOnly
                      />
                      <label className="text-sm">자동 알림 활성화</label>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    설정을 불러올 수 없습니다.
                  </div>
                )}
              </CardContent>
            </Card>
            
            <TestDataGenerator />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AttendanceDashboard; 