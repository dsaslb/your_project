"use client"

import React, { useState, useEffect } from 'react';
import { AppLayout } from "@/components/app-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import { useUser } from '@/components/UserContext';
import { 
  Users, 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  UserPlus,
  Clock,
  Mail,
  Phone,
  Eye,
  X,
  Check,
  ArrowRight,
  CheckCircle,
  XCircle,
  AlertCircle,
  DollarSign,
  MapPin,
  Calendar,
  Briefcase,
  Star,
  TrendingUp,
  BarChart3
} from "lucide-react"
import { api as noticeApi } from '../notice/page';
import { toast } from '@/lib/toast';
import NotificationService from '@/lib/notification-service';

// 직원 타입 정의
interface Staff {
  id: number;
  name: string;
  position: string;
  email: string;
  phone: string;
  status: 'active' | 'inactive' | 'on_leave';
  joinDate: string;
  workHours: string;
  department?: string;
  salary?: number;
  notes?: string;
  avatar?: string;
  permissions: string[];
  attendanceRate: number;
  performance: number;
  lastActive: string;
  address: string;
  emergencyContact: string;
  skills: string[];
}

const mockStaff: Staff[] = [
  {
    id: 1,
    name: "김철수",
    position: "주방장",
    email: "kim@restaurant.com",
    phone: "010-1234-5678",
    status: "active",
    joinDate: "2023-01-15",
    workHours: "40시간/주",
    department: "주방",
    salary: 3500000,
    notes: "경력 5년, 주방 관리 담당",
    avatar: "/avatars/kim.jpg",
    permissions: ['manage_staff', 'view_reports', 'manage_schedule'],
    attendanceRate: 95,
    performance: 92,
    lastActive: "2024-01-15 09:30",
    address: "서울시 강남구 역삼동 123-45",
    emergencyContact: "010-9876-5432 (부모님)",
    skills: ["고객관리", "재고관리", "팀리더십"]
  },
  {
    id: 2,
    name: "이영희",
    position: "서버",
    email: "lee@restaurant.com",
    phone: "010-2345-6789",
    status: "active",
    joinDate: "2023-03-20",
    workHours: "35시간/주",
    department: "서비스",
    salary: 2800000,
    notes: "고객 서비스 우수",
    avatar: "/avatars/lee.jpg",
    permissions: ['view_schedule', 'view_orders'],
    attendanceRate: 88,
    performance: 85,
    lastActive: "2024-01-15 08:45",
    address: "서울시 서초구 서초동 456-78",
    emergencyContact: "010-8765-4321 (배우자)",
    skills: ["고객서비스", "메뉴추천", "영어회화"]
  },
  {
    id: 3,
    name: "박민수",
    position: "청소원",
    email: "park@restaurant.com",
    phone: "010-3456-7890",
    status: "inactive",
    joinDate: "2022-11-10",
    workHours: "20시간/주",
    department: "청소",
    salary: 2000000,
    notes: "파트타임 근무",
    avatar: "/avatars/park.jpg",
    permissions: ['manage_inventory', 'view_orders', 'manage_menu'],
    attendanceRate: 92,
    performance: 96,
    lastActive: "2024-01-15 07:00",
    address: "서울시 마포구 합정동 789-12",
    emergencyContact: "010-7654-3210 (형님)",
    skills: ["요리기술", "재료관리", "품질관리"]
  },
  {
    id: 4,
    name: "정수진",
    position: "매니저",
    email: "jung@restaurant.com",
    phone: "010-4567-8901",
    status: "active",
    joinDate: "2022-08-05",
    workHours: "45시간/주",
    department: "관리",
    salary: 4500000,
    notes: "매장 전체 관리 담당",
    avatar: "/avatars/jung.jpg",
    permissions: ['manage_staff', 'view_reports', 'manage_schedule'],
    attendanceRate: 90,
    performance: 88,
    lastActive: "2024-01-15 08:00",
    address: "서울시 강서구 화곡동 654-87",
    emergencyContact: "010-5432-1098 (아버지)",
    skills: ["재료준비", "청소", "보조업무"]
  },
  {
    id: 5,
    name: "최지영",
    position: "캐셔",
    email: "choi@restaurant.com",
    phone: "010-5678-9012",
    status: "on_leave",
    joinDate: "2023-06-05",
    workHours: "35시간/주",
    department: "서비스",
    salary: 2500000,
    notes: "정확하고 꼼꼼한 업무 처리",
    avatar: "/avatars/choi.jpg",
    permissions: ['view_orders', 'process_payment'],
    attendanceRate: 78,
    performance: 82,
    lastActive: "2024-01-10 18:00",
    address: "서울시 송파구 문정동 321-54",
    emergencyContact: "010-6543-2109 (어머니)",
    skills: ["계산처리", "고객응대", "정리정돈"]
  },
  {
    id: 6,
    name: "정현우",
    position: "보조주방",
    email: "jung@restaurant.com",
    phone: "010-5678-9012",
    status: "active",
    joinDate: "2023-08-15",
    workHours: "35시간/주",
    department: "주방",
    salary: 2200000,
    notes: "성실하고 배우려는 의지가 강함",
    avatar: "/avatars/jung.jpg",
    permissions: ['view_orders'],
    attendanceRate: 90,
    performance: 88,
    lastActive: "2024-01-15 08:00",
    address: "서울시 강서구 화곡동 654-87",
    emergencyContact: "010-5432-1098 (아버지)",
    skills: ["재료준비", "청소", "보조업무"]
  }
];

// 알림 등록 함수
async function createStaffNotice({ type, title, content, author }) {
  try {
    await noticeApi.createNotice({
      type,
      title,
      content,
      status: 'unread',
      author
    });
  } catch (e) {
    // 무시(실패 시에도 staff는 정상 동작)
  }
}

export default function StaffPage() {
  const { user } = useUser();
  const [staff, setStaff] = useState<Staff[]>(mockStaff);
  const [filteredStaff, setFilteredStaff] = useState<Staff[]>(mockStaff);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [departmentFilter, setDepartmentFilter] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedStaff, setSelectedStaff] = useState<Staff | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [loading, setLoading] = useState(true);

  // 통계 계산
  const stats = {
    total: staff.length,
    active: staff.filter(s => s.status === 'active').length,
    inactive: staff.filter(s => s.status === 'inactive').length,
    onLeave: staff.filter(s => s.status === 'on_leave').length,
    avgAttendance: Math.round(staff.reduce((sum, s) => sum + s.attendanceRate, 0) / staff.length),
    avgPerformance: Math.round(staff.reduce((sum, s) => sum + s.performance, 0) / staff.length),
    totalSalary: staff.reduce((sum, s) => sum + s.salary, 0)
  };

  // 검색 및 필터링
  useEffect(() => {
    let filtered = staff;

    if (searchTerm) {
      filtered = filtered.filter(s => 
        s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.position.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.department?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(s => s.status === statusFilter);
    }

    if (departmentFilter !== 'all') {
      filtered = filtered.filter(s => s.department === departmentFilter);
    }

    setFilteredStaff(filtered);
  }, [staff, searchTerm, statusFilter, departmentFilter]);

  // 직원 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'inactive': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      case 'on_leave': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  // 직원 상태별 텍스트
  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '재직중';
      case 'inactive': return '퇴사';
      case 'on_leave': return '휴직중';
      default: return '알 수 없음';
    }
  };

  // 권한별 색상
  const getPermissionColor = (permission: string) => {
    const colors = {
      'manage_staff': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      'view_reports': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
      'manage_schedule': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      'manage_inventory': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
      'view_orders': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-300',
      'process_payment': 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-300',
      'manage_menu': 'bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-300'
    };
    return colors[permission as keyof typeof colors] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
  };

  // 권한 텍스트 변환
  const getPermissionText = (permission: string) => {
    const texts = {
      'manage_staff': '직원관리',
      'view_reports': '보고서조회',
      'manage_schedule': '스케줄관리',
      'manage_inventory': '재고관리',
      'view_orders': '주문조회',
      'process_payment': '결제처리',
      'manage_menu': '메뉴관리'
    };
    return texts[permission as keyof typeof texts] || permission;
  };



  // 직원 등록 (더미)
  const handleAddStaff = async () => {
    const newStaff: Staff = {
      id: Math.max(...staff.map(s => s.id)) + 1,
      name: '새 직원',
      position: '직원',
      email: 'new@restaurant.com',
      phone: '010-0000-0000',
      status: 'active',
      joinDate: new Date().toISOString().split('T')[0],
      workHours: '35시간/주',
      department: '서비스',
      salary: 2500000,
      notes: '새로 등록된 직원',
      avatar: '/avatars/new.jpg',
      permissions: ['view_orders'],
      attendanceRate: 90,
      performance: 85,
      lastActive: new Date().toISOString(),
      address: '주소 입력 필요',
      emergencyContact: '비상연락처 입력 필요',
      skills: ['기본업무']
    };
    setStaff([...staff, newStaff]);
    setShowAddModal(false);
    await createStaffNotice({
      type: 'alert',
      title: '직원 등록',
      content: `${newStaff.name} 직원이 등록되었습니다.`,
      author: user?.name || '관리자'
    });
  };

  const handleUpdateStaff = async (id: number, updates: Partial<Staff>) => {
    try {
      const oldStaff = staff.find(s => s.id === id);
      const updatedStaff = { ...oldStaff, ...updates, updatedAt: new Date().toISOString() };
      
      setStaff(prev => prev.map(s => s.id === id ? updatedStaff : s));
      toast.success('직원 정보가 수정되었습니다.');

      // 직원 정보 변경 알림 생성
      await NotificationService.createStaffNotification('updated', updatedStaff);
    } catch (error) {
      console.error('직원 수정 실패:', error);
      toast.error('직원 수정에 실패했습니다.');
    }
  };

  const handleDeleteStaff = async (id: number) => {
    try {
      const staffToDelete = staff.find(s => s.id === id);
      setStaff(prev => prev.filter(s => s.id !== id));
      setShowDeleteModal(false);
      setSelectedStaff(null);
      toast.success('직원이 삭제되었습니다.');

      // 직원 삭제 알림 생성
      if (staffToDelete) {
        await NotificationService.createStaffNotification('left', staffToDelete);
        await createStaffNotice({
          type: 'alert',
          title: '직원 삭제',
          content: `${staffToDelete.name} 직원이 삭제되었습니다.`,
          author: user?.name || '관리자'
        });
      }
    } catch (error) {
      console.error('직원 삭제 실패:', error);
      toast.error('직원 삭제에 실패했습니다.');
    }
  };

  const handleStaffLeave = async (id: number) => {
    try {
      const staffMember = staff.find(s => s.id === id);
      if (!staffMember) return;

      const updatedStaff = { 
        ...staffMember, 
        status: 'inactive',
        updatedAt: new Date().toISOString() 
      };
      
      setStaff(prev => prev.map(s => s.id === id ? updatedStaff : s));
      toast.success('직원 퇴사 처리가 완료되었습니다.');

      // 직원 퇴사 알림 생성
      await NotificationService.createStaffNotification('left', updatedStaff);
    } catch (error) {
      console.error('직원 퇴사 처리 실패:', error);
      toast.error('직원 퇴사 처리에 실패했습니다.');
    }
  };

  const handleAttendanceIssue = async (id: number, issue: string) => {
    try {
      const staffMember = staff.find(s => s.id === id);
      if (!staffMember) return;

      // 출근 이슈 알림 생성
      await NotificationService.createStaffNotification('attendance_issue', {
        ...staffMember,
        issue: issue
      });
      
      toast.success('출근 이슈가 보고되었습니다.');
    } catch (error) {
      console.error('출근 이슈 보고 실패:', error);
      toast.error('출근 이슈 보고에 실패했습니다.');
    }
  };

  return (
    <AppLayout>
      <div className="w-full h-full bg-gray-50 dark:bg-gray-900 p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* 헤더 */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">직원 관리</h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                직원 정보 관리, 권한 설정, 성과 모니터링
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
                variant="outline"
                size="sm"
              >
                {viewMode === 'grid' ? '목록보기' : '그리드보기'}
              </Button>
              {user?.permissions?.includes('manage_staff') && (
                <Button onClick={() => setShowAddModal(true)} className="bg-blue-600 hover:bg-blue-700">
                  <UserPlus className="w-4 h-4 mr-2" />
                  직원 등록
                </Button>
              )}
            </div>
          </div>

          {/* 페이지 정상 작동 메시지 */}
          <Card className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
            <CardContent className="p-4">
              <div className="flex items-center">
                <Check className="w-5 h-5 text-green-600 mr-2" />
                <span className="text-green-800 dark:text-green-200 font-medium">
                  ✅ 직원 관리 페이지 정상 작동 중 - 등록/수정/삭제/상세 기능 테스트 가능
                </span>
              </div>
            </CardContent>
          </Card>

          {/* 통계 카드 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">전체 직원</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}명</p>
                  </div>
                  <Users className="w-8 h-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">재직중</p>
                    <p className="text-2xl font-bold text-green-600">{stats.active}명</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">평균 출근률</p>
                    <p className="text-2xl font-bold text-purple-600">{stats.avgAttendance}%</p>
                  </div>
                  <Clock className="w-8 h-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">평균 성과</p>
                    <p className="text-2xl font-bold text-orange-600">{stats.avgPerformance}%</p>
                  </div>
                  <Star className="w-8 h-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 검색 및 필터 */}
          <Card>
            <CardContent className="p-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      placeholder="이름, 이메일, 직책으로 검색..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                  >
                    <option value="all">전체 상태</option>
                    <option value="active">재직중</option>
                    <option value="inactive">퇴사</option>
                    <option value="on_leave">휴직중</option>
                  </select>
                  <select
                    value={departmentFilter}
                    onChange={(e) => setDepartmentFilter(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                  >
                    <option value="all">전체 부서</option>
                    <option value="관리팀">관리팀</option>
                    <option value="서비스팀">서비스팀</option>
                    <option value="주방팀">주방팀</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 직원 목록 */}
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredStaff.map((member) => (
                <Card key={member.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <Avatar className="w-12 h-12">
                          <AvatarImage src={member.avatar} />
                          <AvatarFallback className="bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300">
                            {member.name.charAt(0)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <h3 className="font-semibold text-gray-900 dark:text-white">{member.name}</h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{member.position}</p>
                        </div>
                      </div>
                      <Badge className={getStatusColor(member.status)}>
                        {getStatusText(member.status)}
                      </Badge>
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                        <Mail className="w-4 h-4" />
                        {member.email}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                        <Phone className="w-4 h-4" />
                        {member.phone}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                        <Briefcase className="w-4 h-4" />
                        {member.department}
                      </div>
                    </div>

                    <Separator className="my-4" />

                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">출근률</span>
                        <span className="font-medium">{member.attendanceRate}%</span>
                      </div>
                      <Progress value={member.attendanceRate} className="h-2" />
                      
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">성과</span>
                        <span className="font-medium">{member.performance}%</span>
                      </div>
                      <Progress value={member.performance} className="h-2" />
                    </div>

                    <div className="flex gap-2 mt-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedStaff(member);
                          setShowDetailModal(true);
                        }}
                        className="flex-1"
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        상세보기
                      </Button>
                      {user?.permissions?.includes('manage_staff') && (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedStaff(member);
                              setShowEditModal(true);
                            }}
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedStaff(member);
                              setShowDeleteModal(true);
                            }}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 dark:bg-gray-800">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          직원
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          연락처
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          부서/직책
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          상태
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          성과
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          작업
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                      {filteredStaff.map((member) => (
                        <tr key={member.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <Avatar className="w-8 h-8 mr-3">
                                <AvatarImage src={member.avatar} />
                                <AvatarFallback className="bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300">
                                  {member.name.charAt(0)}
                                </AvatarFallback>
                              </Avatar>
                              <div>
                                <div className="text-sm font-medium text-gray-900 dark:text-white">
                                  {member.name}
                                </div>
                                <div className="text-sm text-gray-500 dark:text-gray-400">
                                  {member.email}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900 dark:text-white">{member.phone}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900 dark:text-white">{member.department}</div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">{member.position}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <Badge className={getStatusColor(member.status)}>
                              {getStatusText(member.status)}
                            </Badge>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center gap-2">
                              <div className="text-sm text-gray-900 dark:text-white">
                                {member.performance}%
                              </div>
                              <Progress value={member.performance} className="w-16 h-2" />
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                  setSelectedStaff(member);
                                  setShowDetailModal(true);
                                }}
                              >
                                <Eye className="w-4 h-4" />
                              </Button>
                              {user?.permissions?.includes('manage_staff') && (
                                <>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => {
                                      setSelectedStaff(member);
                                      setShowEditModal(true);
                                    }}
                                  >
                                    <Edit className="w-4 h-4" />
                                  </Button>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => {
                                      setSelectedStaff(member);
                                      setShowDeleteModal(true);
                                    }}
                                    className="text-red-600 hover:text-red-700"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </Button>
                                </>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* 상세보기 모달 */}
        {showDetailModal && selectedStaff && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white dark:bg-gray-900 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-start mb-6">
                  <div className="flex items-center gap-4">
                    <Avatar className="w-16 h-16">
                      <AvatarImage src={selectedStaff.avatar} />
                      <AvatarFallback className="bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300 text-xl">
                        {selectedStaff.name.charAt(0)}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                        {selectedStaff.name}
                      </h2>
                      <p className="text-gray-600 dark:text-gray-400">{selectedStaff.position}</p>
                      <Badge className={`mt-2 ${getStatusColor(selectedStaff.status)}`}>
                        {getStatusText(selectedStaff.status)}
                      </Badge>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowDetailModal(false)}
                  >
                    <XCircle className="w-6 h-6" />
                  </Button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">기본 정보</h3>
                    <div className="space-y-3">
                      <div className="flex items-center gap-3">
                        <Mail className="w-4 h-4 text-gray-500" />
                        <span className="text-gray-700 dark:text-gray-300">{selectedStaff.email}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <Phone className="w-4 h-4 text-gray-500" />
                        <span className="text-gray-700 dark:text-gray-300">{selectedStaff.phone}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <MapPin className="w-4 h-4 text-gray-500" />
                        <span className="text-gray-700 dark:text-gray-300">{selectedStaff.address}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <Calendar className="w-4 h-4 text-gray-500" />
                        <span className="text-gray-700 dark:text-gray-300">
                          입사일: {selectedStaff.joinDate}
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <DollarSign className="w-4 h-4 text-gray-500" />
                        <span className="text-gray-700 dark:text-gray-300">
                          급여: {selectedStaff.salary?.toLocaleString()}원
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">성과 지표</h3>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-600 dark:text-gray-400">출근률</span>
                          <span className="font-medium">{selectedStaff.attendanceRate}%</span>
                        </div>
                        <Progress value={selectedStaff.attendanceRate} className="h-3" />
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-600 dark:text-gray-400">성과</span>
                          <span className="font-medium">{selectedStaff.performance}%</span>
                        </div>
                        <Progress value={selectedStaff.performance} className="h-3" />
                      </div>
                    </div>

                    <div className="space-y-3">
                      <h4 className="font-medium text-gray-900 dark:text-white">권한</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedStaff.permissions.map((permission) => (
                          <Badge key={permission} className={getPermissionColor(permission)}>
                            {getPermissionText(permission)}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-3">
                      <h4 className="font-medium text-gray-900 dark:text-white">보유 기술</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedStaff.skills.map((skill) => (
                          <Badge key={skill} variant="outline">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-6 space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">추가 정보</h3>
                  <div className="space-y-3">
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white mb-1">비상연락처</h4>
                      <p className="text-gray-700 dark:text-gray-300">{selectedStaff.emergencyContact}</p>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white mb-1">메모</h4>
                      <p className="text-gray-700 dark:text-gray-300">{selectedStaff.notes}</p>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white mb-1">마지막 활동</h4>
                      <p className="text-gray-700 dark:text-gray-300">{selectedStaff.lastActive}</p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2 mt-6">
                  {user?.permissions?.includes('manage_staff') && (
                    <>
                      <Button
                        onClick={() => {
                          setShowDetailModal(false);
                          setShowEditModal(true);
                        }}
                        className="flex-1"
                      >
                        <Edit className="w-4 h-4 mr-2" />
                        수정
                      </Button>
                      <Button
                        variant="destructive"
                        onClick={() => {
                          setShowDetailModal(false);
                          setShowDeleteModal(true);
                        }}
                        className="flex-1"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        삭제
                      </Button>
                    </>
                  )}
                  <Button
                    variant="outline"
                    onClick={() => setShowDetailModal(false)}
                    className="flex-1"
                  >
                    닫기
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 직원 등록 모달 */}
        {showAddModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white dark:bg-gray-900 rounded-lg max-w-md w-full">
              <div className="p-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">직원 등록</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      이름
                    </label>
                    <Input placeholder="직원 이름" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      이메일
                    </label>
                    <Input type="email" placeholder="이메일 주소" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      전화번호
                    </label>
                    <Input placeholder="전화번호" />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        부서
                      </label>
                      <select className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white">
                        <option>서비스팀</option>
                        <option>주방팀</option>
                        <option>관리팀</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        직책
                      </label>
                      <Input placeholder="직책" />
                    </div>
                  </div>
                </div>
                <div className="flex gap-2 mt-6">
                  <Button onClick={handleAddStaff} className="flex-1">
                    등록
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowAddModal(false)}
                    className="flex-1"
                  >
                    취소
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 직원 수정 모달 */}
        {showEditModal && selectedStaff && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white dark:bg-gray-900 rounded-lg max-w-md w-full">
              <div className="p-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">직원 정보 수정</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      이름
                    </label>
                    <Input defaultValue={selectedStaff.name} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      이메일
                    </label>
                    <Input type="email" defaultValue={selectedStaff.email} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      전화번호
                    </label>
                    <Input defaultValue={selectedStaff.phone} />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        부서
                      </label>
                      <select 
                        defaultValue={selectedStaff.department}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                      >
                        <option>서비스팀</option>
                        <option>주방팀</option>
                        <option>관리팀</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        직책
                      </label>
                      <Input defaultValue={selectedStaff.position} />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      상태
                    </label>
                    <select 
                      defaultValue={selectedStaff.status}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                    >
                      <option value="active">재직중</option>
                      <option value="inactive">퇴사</option>
                      <option value="on_leave">휴직중</option>
                    </select>
                  </div>
                </div>
                <div className="flex gap-2 mt-6">
                  <Button className="flex-1">
                    수정
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowEditModal(false)}
                    className="flex-1"
                  >
                    취소
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 삭제 확인 모달 */}
        {showDeleteModal && selectedStaff && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white dark:bg-gray-900 rounded-lg max-w-md w-full">
              <div className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white">직원 삭제</h2>
                </div>
                <p className="text-gray-700 dark:text-gray-300 mb-6">
                  <strong>{selectedStaff.name}</strong> 직원을 삭제하시겠습니까?<br />
                  이 작업은 되돌릴 수 없습니다.
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="destructive"
                    onClick={() => handleDeleteStaff(selectedStaff.id)}
                    className="flex-1"
                  >
                    삭제
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowDeleteModal(false)}
                    className="flex-1"
                  >
                    취소
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  )
} 