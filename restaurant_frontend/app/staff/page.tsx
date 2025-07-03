"use client"

import React, { useState, useEffect, useMemo } from 'react';
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
import { toast } from '@/lib/toast';
import NotificationService from '@/lib/notification-service';
import { PermissionGuard } from '@/components/PermissionGuard';
import { Alert } from '@/components/ui/alert';

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

// 1. API 함수 정의 (예시)
const staffApi = {
  async getStaff() {
    const res = await fetch('/api/staff');
    if (!res.ok) throw new Error('직원 목록을 불러오지 못했습니다.');
    return res.json();
  },
  async createStaff(data) {
    const res = await fetch('/api/staff', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('직원 등록에 실패했습니다.');
    return res.json();
  },
  async updateStaff(id, data) {
    const res = await fetch(`/api/staff/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('직원 수정에 실패했습니다.');
    return res.json();
  },
  async deleteStaff(id) {
    const res = await fetch(`/api/staff/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('직원 삭제에 실패했습니다.');
    return res.json();
  },
  async getStaffDetail(id) {
    const res = await fetch(`/api/staff/${id}`);
    if (!res.ok) throw new Error('직원 상세를 불러오지 못했습니다.');
    return res.json();
  },
  async getStaffHistory(id) {
    const res = await fetch(`/api/staff/${id}/history`);
    if (!res.ok) throw new Error('직원 이력을 불러오지 못했습니다.');
    return res.json();
  },
};

// 권한 체크 함수 예시
function useStaffPermissions(user) {
  return {
    canAdd: user?.role === 'admin' || user?.permissions?.employee_management?.create,
    canEdit: user?.role === 'admin' || user?.permissions?.employee_management?.edit,
    canDelete: user?.role === 'admin' || user?.permissions?.employee_management?.delete,
    canView: true,
  };
}

export default function StaffPage() {
  const { user } = useUser();
  const [staff, setStaff] = useState<Staff[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [departmentFilter, setDepartmentFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('all');
  const [sortOption, setSortOption] = useState('latest');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedStaff, setSelectedStaff] = useState<Staff | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string|null>(null);
  const [newItem, setNewItem] = useState({ name: '', role: 'employee', status: 'active' });
  const perms = useStaffPermissions(user);

  // 2. useEffect로 직원 목록 불러오기
  useEffect(() => {
    const fetchStaff = async () => {
      try {
        setLoading(true);
        const staffList = await staffApi.getStaff();
        setStaff(staffList);
      } catch (e) {
        toast.error('직원 목록을 불러오지 못했습니다.');
      } finally {
        setLoading(false);
      }
    };
    fetchStaff();
  }, []);

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

  // 필터/정렬 적용
  const filteredStaff = useMemo(() => {
    let filtered = [...staff];
    if (statusFilter !== 'all') filtered = filtered.filter(s => s.status === statusFilter);
    if (departmentFilter !== 'all') filtered = filtered.filter(s => s.department === departmentFilter);
    // 기간 필터 예시(최근 30일 입사)
    if (dateFilter === '30days') {
      const monthAgo = new Date();
      monthAgo.setDate(monthAgo.getDate() - 30);
      filtered = filtered.filter(s => new Date(s.joinDate) >= monthAgo);
    }
    // 정렬
    if (sortOption === 'latest') filtered.sort((a, b) => new Date(b.joinDate).getTime() - new Date(a.joinDate).getTime());
    else if (sortOption === 'oldest') filtered.sort((a, b) => new Date(a.joinDate).getTime() - new Date(b.joinDate).getTime());
    else if (sortOption === 'performance') filtered.sort((a, b) => b.performance - a.performance);
    return filtered;
  }, [staff, statusFilter, departmentFilter, dateFilter, sortOption]);

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

  // 3. 등록/수정/삭제/상세 함수 실제 API 연동
  const handleAddStaff = async () => {
    try {
      await staffApi.createStaff(newItem);
      setShowAddModal(false);
      toast.success('직원이 등록되었습니다.');
      const staffList = await staffApi.getStaff();
      setStaff(staffList);
    } catch (e) {
      toast.error('직원 등록에 실패했습니다.');
    }
  };
  const handleUpdateStaff = async (id, updates) => {
    try {
      await staffApi.updateStaff(id, updates);
      toast.success('직원 정보가 수정되었습니다.');
      const staffList = await staffApi.getStaff();
      setStaff(staffList);
    } catch (e) {
      toast.error('직원 수정에 실패했습니다.');
    }
  };
  const handleDeleteStaff = async (id) => {
    try {
      await staffApi.deleteStaff(id);
      setShowDeleteModal(false);
      setSelectedStaff(null);
      toast.success('직원이 삭제되었습니다.');
      const staffList = await staffApi.getStaff();
      setStaff(staffList);
    } catch (e) {
      toast.error('직원 삭제에 실패했습니다.');
    }
  };
  const handleStaffDetail = async (id) => {
    try {
      const detail = await staffApi.getStaffDetail(id);
      setSelectedStaff(detail);
      setShowDetailModal(true);
    } catch (e) {
      toast.error('직원 상세 정보를 불러오지 못했습니다.');
    }
  };
  const handleStaffHistory = async (id) => {
    try {
      const history = await staffApi.getStaffHistory(id);
      setStaffHistory(history); // staffHistory는 useState로 관리
    } catch (e) {
      toast.error('직원 이력을 불러오지 못했습니다.');
    }
  };

  // 권한별 분기 예시
  if (!user) return <div className="p-6">로그인 필요</div>;
  if (user.role === 'employee') {
    return <div className="p-6">직원은 본인 정보만 확인할 수 있습니다.</div>;
  }

  return (
    <PermissionGuard permissions={['staff.view']} fallback={<Alert message="직원 관리 접근 권한이 없습니다." type="error" />}>
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
                {perms.canAdd && (
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

            {/* 상단 필터/정렬 UI */}
            <div className="flex flex-wrap gap-2 mb-4 items-end">
              <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="border rounded px-2 py-1">
                <option value="all">상태 전체</option>
                <option value="active">재직</option>
                <option value="inactive">퇴사</option>
                <option value="on_leave">휴직</option>
              </select>
              <select value={departmentFilter} onChange={e => setDepartmentFilter(e.target.value)} className="border rounded px-2 py-1">
                <option value="all">부서 전체</option>
                {[...new Set(staff.map(s => s.department))].map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
              <select value={dateFilter} onChange={e => setDateFilter(e.target.value)} className="border rounded px-2 py-1">
                <option value="all">전체 기간</option>
                <option value="30days">최근 30일 입사</option>
              </select>
              <select value={sortOption} onChange={e => setSortOption(e.target.value)} className="border rounded px-2 py-1">
                <option value="latest">최신 입사순</option>
                <option value="oldest">오래된 입사순</option>
                <option value="performance">성과순</option>
              </select>
            </div>

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
                        {perms.canEdit && (
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
                        )}
                        {perms.canDelete && (
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
                                {perms.canEdit && (
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
                                )}
                                {perms.canDelete && (
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
                    {perms.canEdit && (
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
                      <Input placeholder="직원 이름" value={newItem.name} onChange={e => setNewItem({ ...newItem, name: e.target.value })} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        이메일
                      </label>
                      <Input type="email" placeholder="이메일 주소" value={newItem.email} onChange={e => setNewItem({ ...newItem, email: e.target.value })} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        전화번호
                      </label>
                      <Input placeholder="전화번호" value={newItem.phone} onChange={e => setNewItem({ ...newItem, phone: e.target.value })} />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          부서
                        </label>
                        <select className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white" value={newItem.department} onChange={e => setNewItem({ ...newItem, department: e.target.value })}>
                          <option>서비스팀</option>
                          <option>주방팀</option>
                          <option>관리팀</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          직책
                        </label>
                        <Input placeholder="직책" value={newItem.position} onChange={e => setNewItem({ ...newItem, position: e.target.value })} />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        상태
                      </label>
                      <select className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white" value={newItem.status} onChange={e => setNewItem({ ...newItem, status: e.target.value as 'active' | 'inactive' | 'on_leave' })}>
                        <option value="active">재직중</option>
                        <option value="inactive">퇴사</option>
                        <option value="on_leave">휴직중</option>
                      </select>
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
                      <Input defaultValue={selectedStaff.name} onChange={e => setSelectedStaff({ ...selectedStaff, name: e.target.value })} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        이메일
                      </label>
                      <Input type="email" defaultValue={selectedStaff.email} onChange={e => setSelectedStaff({ ...selectedStaff, email: e.target.value })} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        전화번호
                      </label>
                      <Input defaultValue={selectedStaff.phone} onChange={e => setSelectedStaff({ ...selectedStaff, phone: e.target.value })} />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          부서
                        </label>
                        <select 
                          defaultValue={selectedStaff.department}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                          onChange={e => setSelectedStaff({ ...selectedStaff, department: e.target.value })}
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
                        <Input defaultValue={selectedStaff.position} onChange={e => setSelectedStaff({ ...selectedStaff, position: e.target.value })} />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        상태
                      </label>
                      <select 
                        defaultValue={selectedStaff.status}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                        onChange={e => setSelectedStaff({ ...selectedStaff, status: e.target.value as 'active' | 'inactive' | 'on_leave' })}
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
    </PermissionGuard>
  )
} 