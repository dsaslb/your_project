"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search, Filter, Calendar, Clock, Users, TrendingUp, Download, Plus, Edit, Trash2 } from "lucide-react";
import { toast } from "sonner";

interface User {
  id: number;
  name: string;
  username: string;
  position: string;
  department: string;
  role: string;
  status: string;
  email: string;
  phone: string;
}

interface Attendance {
  id: number;
  user_id: number;
  user_name: string;
  date: string;
  clock_in: string;
  clock_out: string;
  work_hours: number;
  is_late: boolean;
  is_early_leave: boolean;
  is_absent: boolean;
  overtime_hours: number;
  status: 'present' | 'late' | 'absent' | 'early_leave';
}

interface AttendanceSummary {
  total_days: number;
  total_hours: number;
  late_count: number;
  early_leave_count: number;
  absent_count: number;
  overtime_hours: number;
  estimated_wage: number;
  avg_hours_per_day: number;
}

// 직원 승인 예시 데이터
const sampleUsers: User[] = [
  {
    id: 1,
    name: "김주방",
    username: "kitchen_kim",
    position: "주방장",
    department: "주방",
    role: "employee",
    status: "approved",
    email: "kitchen_kim@restaurant.com",
    phone: "010-1111-1111"
  },
  {
    id: 2,
    name: "이보조",
    username: "kitchen_lee",
    position: "주방보조",
    department: "주방",
    role: "employee",
    status: "approved",
    email: "kitchen_lee@restaurant.com",
    phone: "010-1111-1112"
  },
  {
    id: 3,
    name: "박서버",
    username: "service_park",
    position: "서버",
    department: "홀서비스",
    role: "employee",
    status: "approved",
    email: "service_park@restaurant.com",
    phone: "010-1111-1113"
  },
  {
    id: 4,
    name: "최홀보조",
    username: "service_choi",
    position: "홀보조",
    department: "홀서비스",
    role: "employee",
    status: "approved",
    email: "service_choi@restaurant.com",
    phone: "010-1111-1114"
  },
  {
    id: 5,
    name: "정매니저",
    username: "manager_jung",
    position: "매니저",
    department: "매니지먼트",
    role: "manager",
    status: "approved",
    email: "manager_jung@restaurant.com",
    phone: "010-1111-1115"
  },
  {
    id: 6,
    name: "한캐셔",
    username: "cashier_han",
    position: "캐셔",
    department: "매니지먼트",
    role: "employee",
    status: "approved",
    email: "cashier_han@restaurant.com",
    phone: "010-1111-1116"
  },
  {
    id: 7,
    name: "윤배달",
    username: "delivery_yoon",
    position: "배달원",
    department: "배달",
    role: "employee",
    status: "approved",
    email: "delivery_yoon@restaurant.com",
    phone: "010-1111-1117"
  },
  {
    id: 8,
    name: "임청소",
    username: "cleaning_lim",
    position: "청소원",
    department: "청소",
    role: "employee",
    status: "approved",
    email: "cleaning_lim@restaurant.com",
    phone: "010-1111-1118"
  }
];

// 근태 예시 데이터
const sampleAttendances: Attendance[] = [
  {
    id: 1,
    user_id: 1,
    user_name: "김주방",
    date: "2025-01-06",
    clock_in: "09:00",
    clock_out: "18:00",
    work_hours: 9.0,
    is_late: false,
    is_early_leave: false,
    is_absent: false,
    overtime_hours: 1.0,
    status: "present"
  },
  {
    id: 2,
    user_id: 2,
    user_name: "이보조",
    date: "2025-01-06",
    clock_in: "09:15",
    clock_out: "18:00",
    work_hours: 8.75,
    is_late: true,
    is_early_leave: false,
    is_absent: false,
    overtime_hours: 0.75,
    status: "late"
  },
  {
    id: 3,
    user_id: 3,
    user_name: "박서버",
    date: "2025-01-06",
    clock_in: "08:45",
    clock_out: "17:30",
    work_hours: 8.75,
    is_late: false,
    is_early_leave: true,
    is_absent: false,
    overtime_hours: 0.75,
    status: "early_leave"
  },
  {
    id: 4,
    user_id: 4,
    user_name: "최홀보조",
    date: "2025-01-06",
    clock_in: "09:00",
    clock_out: "18:00",
    work_hours: 9.0,
    is_late: false,
    is_early_leave: false,
    is_absent: false,
    overtime_hours: 1.0,
    status: "present"
  },
  {
    id: 5,
    user_id: 5,
    user_name: "정매니저",
    date: "2025-01-06",
    clock_in: "08:30",
    clock_out: "19:00",
    work_hours: 10.5,
    is_late: false,
    is_early_leave: false,
    is_absent: false,
    overtime_hours: 2.5,
    status: "present"
  }
];

const AttendancePage = () => {
  const [users, setUsers] = useState<User[]>(sampleUsers);
  const [attendances, setAttendances] = useState<Attendance[]>(sampleAttendances);
  const [summary, setSummary] = useState<AttendanceSummary | null>(null);
  const [selectedUser, setSelectedUser] = useState<string>("all");
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [selectedDepartment, setSelectedDepartment] = useState<string>("all");
  const [selectedStatus, setSelectedStatus] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("date");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [isLoading, setIsLoading] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingAttendance, setEditingAttendance] = useState<Attendance | null>(null);
  const [activeTab, setActiveTab] = useState("overview");

  // 필터링된 데이터
  const filteredAttendances = attendances.filter(attendance => {
    const user = users.find(u => u.id === attendance.user_id);
    const matchesUser = selectedUser === "all" || attendance.user_id.toString() === selectedUser;
    const matchesDepartment = selectedDepartment === "all" || user?.department === selectedDepartment;
    const matchesStatus = selectedStatus === "all" || attendance.status === selectedStatus;
    const matchesSearch = searchTerm === "" || 
      attendance.user_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user?.position.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user?.department.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesUser && matchesDepartment && matchesStatus && matchesSearch;
  });

  // 정렬된 데이터
  const sortedAttendances = [...filteredAttendances].sort((a, b) => {
    let comparison = 0;
    switch (sortBy) {
      case "name":
        comparison = a.user_name.localeCompare(b.user_name);
        break;
      case "date":
        comparison = a.date.localeCompare(b.date);
        break;
      case "work_hours":
        comparison = a.work_hours - b.work_hours;
        break;
      case "status":
        comparison = a.status.localeCompare(b.status);
        break;
      default:
        comparison = 0;
    }
    return sortOrder === "asc" ? comparison : -comparison;
  });

  // 근태 요약 계산
  useEffect(() => {
    const totalDays = filteredAttendances.length;
    const totalHours = filteredAttendances.reduce((sum, att) => sum + att.work_hours, 0);
    const lateCount = filteredAttendances.filter(att => att.is_late).length;
    const earlyLeaveCount = filteredAttendances.filter(att => att.is_early_leave).length;
    const absentCount = filteredAttendances.filter(att => att.is_absent).length;
    const overtimeHours = filteredAttendances.reduce((sum, att) => sum + att.overtime_hours, 0);
    const estimatedWage = totalHours * 12000; // 시급 12,000원

    setSummary({
      total_days: totalDays,
      total_hours: totalHours,
      late_count: lateCount,
      early_leave_count: earlyLeaveCount,
      absent_count: absentCount,
      overtime_hours: overtimeHours,
      estimated_wage: estimatedWage,
      avg_hours_per_day: totalDays > 0 ? totalHours / totalDays : 0
    });
  }, [filteredAttendances]);

  // 근태 수정/추가
  const saveAttendance = async (attendanceData: Partial<Attendance>) => {
    try {
      // 실제로는 API 호출
      toast.success('근태 정보가 저장되었습니다.');
      setIsEditModalOpen(false);
      setEditingAttendance(null);
    } catch (error) {
      toast.error('근태 정보 저장 중 오류가 발생했습니다.');
    }
  };

  // 급여 계산
  const calculateWage = (user: User, attendance: Attendance) => {
    const hourlyWage = 12000;
    
    // 현재는 시급 기준으로 계산
    return attendance.work_hours * hourlyWage;
  };

  // 상태별 배지 색상
  const getStatusBadge = (attendance: Attendance) => {
    switch (attendance.status) {
      case 'present':
        return <Badge variant="default" className="bg-green-100 text-green-800">정상</Badge>;
      case 'late':
        return <Badge variant="destructive">지각</Badge>;
      case 'early_leave':
        return <Badge variant="secondary">조퇴</Badge>;
      case 'absent':
        return <Badge variant="outline">결근</Badge>;
      default:
        return <Badge variant="default">정상</Badge>;
    }
  };

  // 부서별 색상
  const getDepartmentColor = (department: string) => {
    const colors = {
      '주방': 'bg-orange-100 text-orange-800',
      '홀서비스': 'bg-blue-100 text-blue-800',
      '매니지먼트': 'bg-purple-100 text-purple-800',
      '배달': 'bg-green-100 text-green-800',
      '청소': 'bg-gray-100 text-gray-800'
    };
    return colors[department as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="p-4 md:p-6 space-y-6 max-w-7xl mx-auto">
      {/* 헤더 */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">근태 관리</h1>
          <p className="text-gray-600 mt-1">직원 출퇴근 현황 및 급여 계산, 근태 수정/추가/삭제 기능을 제공합니다.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            내보내기
          </Button>
          <Button onClick={() => setIsEditModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            근태 추가
          </Button>
        </div>
      </div>

      {/* 탭 네비게이션 */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            개요
          </TabsTrigger>
          <TabsTrigger value="attendance" className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            근태 현황
          </TabsTrigger>
          <TabsTrigger value="employees" className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            직원 관리
          </TabsTrigger>
        </TabsList>

        {/* 개요 탭 */}
        <TabsContent value="overview" className="space-y-6">
          {/* 통계 카드 */}
          {summary && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">총 근무일</p>
                      <p className="text-2xl font-bold text-blue-600">{summary.total_days}</p>
                    </div>
                    <Calendar className="w-8 h-8 text-blue-500" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">총 근무시간</p>
                      <p className="text-2xl font-bold text-green-600">{summary.total_hours.toFixed(1)}h</p>
                    </div>
                    <Clock className="w-8 h-8 text-green-500" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">지각</p>
                      <p className="text-2xl font-bold text-red-600">{summary.late_count}</p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-red-500" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">예상 급여</p>
                      <p className="text-2xl font-bold text-purple-600">
                        {summary.estimated_wage.toLocaleString()}원
                      </p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-purple-500" />
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* 차트 영역 (향후 구현) */}
          <Card>
            <CardHeader>
              <CardTitle>근태 통계</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center text-gray-500">
                차트 영역 (향후 구현 예정)
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 근태 현황 탭 */}
        <TabsContent value="attendance" className="space-y-6">
          {/* 필터 및 검색 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter className="w-5 h-5" />
                검색 및 필터
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="직원명, 직책, 부서 검색..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={selectedUser} onValueChange={setSelectedUser}>
                  <SelectTrigger>
                    <SelectValue placeholder="직원 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">전체 직원</SelectItem>
                    {users.map((user) => (
                      <SelectItem key={user.id} value={user.id.toString()}>
                        {user.name} ({user.position})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select value={selectedDepartment} onValueChange={setSelectedDepartment}>
                  <SelectTrigger>
                    <SelectValue placeholder="부서 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">전체 부서</SelectItem>
                    <SelectItem value="주방">주방</SelectItem>
                    <SelectItem value="홀서비스">홀서비스</SelectItem>
                    <SelectItem value="매니지먼트">매니지먼트</SelectItem>
                    <SelectItem value="배달">배달</SelectItem>
                    <SelectItem value="청소">청소</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                  <SelectTrigger>
                    <SelectValue placeholder="상태 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">전체 상태</SelectItem>
                    <SelectItem value="present">정상</SelectItem>
                    <SelectItem value="late">지각</SelectItem>
                    <SelectItem value="early_leave">조퇴</SelectItem>
                    <SelectItem value="absent">결근</SelectItem>
                  </SelectContent>
                </Select>
                <Input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                />
                <div className="flex gap-2">
                  <Select value={sortBy} onValueChange={setSortBy}>
                    <SelectTrigger>
                      <SelectValue placeholder="정렬 기준" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="date">날짜</SelectItem>
                      <SelectItem value="name">이름</SelectItem>
                      <SelectItem value="work_hours">근무시간</SelectItem>
                      <SelectItem value="status">상태</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
                  >
                    {sortOrder === "asc" ? "↑" : "↓"}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 근태 테이블 */}
          <Card>
            <CardHeader>
              <CardTitle>근태 현황 ({sortedAttendances.length}건)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-gray-50">
                      <th className="text-left p-3 font-medium">직원</th>
                      <th className="text-left p-3 font-medium">부서</th>
                      <th className="text-left p-3 font-medium">날짜</th>
                      <th className="text-left p-3 font-medium">출근</th>
                      <th className="text-left p-3 font-medium">퇴근</th>
                      <th className="text-left p-3 font-medium">근무시간</th>
                      <th className="text-left p-3 font-medium">상태</th>
                      <th className="text-left p-3 font-medium">급여</th>
                      <th className="text-left p-3 font-medium">관리</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedAttendances.map((attendance) => {
                      const user = users.find(u => u.id === attendance.user_id);
                      const wage = calculateWage(user!, attendance);
                      
                      return (
                        <tr key={attendance.id} className="border-b hover:bg-gray-50 transition-colors">
                          <td className="p-3">
                            <div>
                              <div className="font-medium">{attendance.user_name}</div>
                              <div className="text-sm text-gray-500">{user?.position}</div>
                            </div>
                          </td>
                          <td className="p-3">
                            <Badge className={getDepartmentColor(user?.department || "")}>
                              {user?.department}
                            </Badge>
                          </td>
                          <td className="p-3">{attendance.date}</td>
                          <td className="p-3">{attendance.clock_in || '-'}</td>
                          <td className="p-3">{attendance.clock_out || '-'}</td>
                          <td className="p-3">
                            <div>
                              <div className="font-medium">{attendance.work_hours.toFixed(1)}시간</div>
                              {attendance.overtime_hours > 0 && (
                                <div className="text-xs text-orange-600">
                                  +{attendance.overtime_hours.toFixed(1)}h (야근)
                                </div>
                              )}
                            </div>
                          </td>
                          <td className="p-3">{getStatusBadge(attendance)}</td>
                          <td className="p-3 font-medium">{wage.toLocaleString()}원</td>
                          <td className="p-3">
                            <div className="flex gap-1">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                  setEditingAttendance(attendance);
                                  setIsEditModalOpen(true);
                                }}
                              >
                                <Edit className="w-3 h-3" />
                              </Button>
                              <Button variant="outline" size="sm">
                                <Trash2 className="w-3 h-3" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                {sortedAttendances.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    <Clock className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p>근태 데이터가 없습니다.</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 직원 관리 탭 */}
        <TabsContent value="employees" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>직원 목록 ({users.length}명)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {users.map((user) => (
                  <Card key={user.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-lg">{user.name}</h3>
                          <p className="text-sm text-gray-600">{user.position}</p>
                          <Badge className={`mt-2 ${getDepartmentColor(user.department)}`}>
                            {user.department}
                          </Badge>
                          <div className="mt-2 space-y-1 text-sm text-gray-500">
                            <p>{user.email}</p>
                            <p>{user.phone}</p>
                          </div>
                        </div>
                        <Badge variant={user.status === "approved" ? "default" : "secondary"}>
                          {user.status === "approved" ? "승인됨" : "미승인"}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 근태 수정/추가 모달 */}
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>
              {editingAttendance ? '근태 수정' : '근태 추가'}
            </DialogTitle>
          </DialogHeader>
          <AttendanceEditForm
            attendance={editingAttendance}
            users={users}
            onSave={saveAttendance}
            onCancel={() => {
              setIsEditModalOpen(false);
              setEditingAttendance(null);
            }}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
};

// 근태 수정/추가 폼 컴포넌트
interface AttendanceEditFormProps {
  attendance: Attendance | null;
  users: User[];
  onSave: (data: Partial<Attendance>) => void;
  onCancel: () => void;
}

const AttendanceEditForm: React.FC<AttendanceEditFormProps> = ({
  attendance,
  users,
  onSave,
  onCancel
}) => {
  const [formData, setFormData] = useState({
    user_id: attendance?.user_id || 0,
    date: attendance?.date || new Date().toISOString().split('T')[0],
    clock_in: attendance?.clock_in || '',
    clock_out: attendance?.clock_out || '',
  });

  const displayUserId = formData.user_id === 0 ? '' : formData.user_id.toString();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="user_id">직원</Label>
        <Select value={displayUserId} onValueChange={(value) => setFormData({...formData, user_id: parseInt(value) || 0})}>
          <SelectTrigger>
            <SelectValue placeholder="직원을 선택하세요" />
          </SelectTrigger>
          <SelectContent>
            {users.map((user) => (
              <SelectItem key={user.id} value={user.id.toString()}>
                {user.name} ({user.position})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      
      <div>
        <Label htmlFor="date">날짜</Label>
        <Input
          id="date"
          type="date"
          value={formData.date}
          onChange={(e) => setFormData({...formData, date: e.target.value})}
        />
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="clock_in">출근 시간</Label>
          <Input
            id="clock_in"
            type="time"
            value={formData.clock_in}
            onChange={(e) => setFormData({...formData, clock_in: e.target.value})}
          />
        </div>
        
        <div>
          <Label htmlFor="clock_out">퇴근 시간</Label>
          <Input
            id="clock_out"
            type="time"
            value={formData.clock_out}
            onChange={(e) => setFormData({...formData, clock_out: e.target.value})}
          />
        </div>
      </div>
      
      <div className="flex justify-end space-x-2 pt-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          취소
        </Button>
        <Button type="submit">
          저장
        </Button>
      </div>
    </form>
  );
};

export default AttendancePage; 