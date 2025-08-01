'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  User, 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Wifi,
  TrendingUp,
  Users,
  Calendar,
  Activity,
  Building2,
  Mail,
  Phone,
  MapPin,
  Clock,
  Star,
  ArrowLeft,
  Bell,
  Filter,
  SortAsc,
  SortDesc
} from 'lucide-react';
import { toast } from 'sonner';
import ProtectedRoute from '@/components/ProtectedRoute';
import { OfflineStorage } from '@/utils/offlineStorage';

interface Staff {
  id: string;
  name: string;
  email: string;
  phone: string;
  role: string;
  department: string;
  hireDate: string;
  status: 'active' | 'inactive';
  location: string;
  avatar?: string;
  lastActive?: string;
  workHours?: number;
  performance?: number;
}

interface StaffFormData {
  name: string;
  email: string;
  phone: string;
  role: string;
  department: string;
  hireDate: string;
  location: string;
}

interface ApiResponse {
  success: boolean;
  data?: any;
  error?: string;
  message?: string;
}

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  message: string;
  timestamp: string;
}

// API 호출 함수
const apiCall = async (endpoint: string, options: RequestInit = {}): Promise<ApiResponse> => {
  try {
    const response = await fetch(`http://192.168.45.44:5000${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API 호출 오류:', error);
    return {
      success: false,
      error: '네트워크 오류가 발생했습니다.',
    };
  }
};

// 직원 상세 정보 컴포넌트
function StaffDetail({ staffId, onBack }: { staffId: string | null; onBack?: () => void }) {
  const [staff, setStaff] = useState<Staff | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!staffId) return;

    const fetchStaffDetail = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // 온라인 모드 시도
        try {
          const response = await apiCall(`/api/admin/employees/${staffId}`);
          if (response.success && response.data) {
            setStaff(response.data);
            return;
          }
        } catch (apiError) {
          console.log('🌐 백엔드 연결 실패, 오프라인 모드로 전환:', apiError);
        }

        // 오프라인 모드: 로컬 데이터에서 찾기
        const offlineData = OfflineStorage.loadEmployees();
        const foundStaff = offlineData.find(s => s.id === staffId);
        
        if (foundStaff) {
          setStaff(foundStaff);
        } else {
          setError('직원 정보를 찾을 수 없습니다.');
        }
      } catch (error) {
        console.error('직원 상세 정보 조회 오류:', error);
        setError('직원 정보를 불러오는 중 오류가 발생했습니다.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStaffDetail();
  }, [staffId]);

  if (isLoading) {
    return (
      <div className="text-center py-16">
        <div className="quantum-glass rounded-full p-8 w-32 h-32 mx-auto mb-6 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400"></div>
        </div>
        <p className="text-gray-300 text-lg">직원 정보를 불러오는 중...</p>
        <p className="text-gray-400 text-sm mt-2">잠시만 기다려주세요</p>
      </div>
    );
  }

  if (error || !staff) {
    return (
      <div className="text-center py-16">
        <div className="quantum-glass rounded-full p-8 w-32 h-32 mx-auto mb-6 flex items-center justify-center">
          <AlertTriangle className="w-16 h-16 text-red-400" />
        </div>
        <h3 className="text-xl font-semibold text-red-400 mb-2">오류가 발생했습니다</h3>
        <p className="text-gray-300 mb-6 max-w-md mx-auto">{error || '직원 정보를 찾을 수 없습니다.'}</p>
        <Button
          onClick={onBack}
          className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 quantum-hover"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          목록으로 돌아가기
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            onClick={onBack}
            variant="outline"
            className="border-green-600/50 text-green-400 hover:border-green-500 hover:text-green-300 quantum-hover"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            목록으로
          </Button>
          <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-400">
            직원 상세 정보
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <Badge 
            variant="secondary" 
            className={`${
              staff.status === 'active' 
                ? 'bg-green-900/50 text-green-300 border-green-500/30' 
                : 'bg-red-900/50 text-red-300 border-red-500/30'
            }`}
          >
            {staff.status === 'active' ? '활성' : '비활성'}
          </Badge>
        </div>
      </div>

      {/* 직원 정보 카드 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 기본 정보 */}
        <Card className="quantum-glass quantum-hover border-green-500/30">
          <CardHeader>
            <CardTitle className="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-400">
              기본 정보
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500/20 to-emerald-500/20 rounded-full flex items-center justify-center">
                <User className="w-8 h-8 text-green-400" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white">{staff.name || '이름 없음'}</h3>
                <p className="text-gray-400">{staff.role || '역할 없음'}</p>
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm">
                <Mail className="w-4 h-4 text-green-400" />
                <span className="text-gray-300">{staff.email || '이메일 없음'}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Phone className="w-4 h-4 text-green-400" />
                <span className="text-gray-300">{staff.phone || '전화번호 없음'}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Building2 className="w-4 h-4 text-green-400" />
                <span className="text-gray-300">{staff.department || '부서 없음'}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <MapPin className="w-4 h-4 text-green-400" />
                <span className="text-gray-300">{staff.location || '위치 없음'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 근무 정보 */}
        <Card className="quantum-glass quantum-hover border-blue-500/30">
          <CardHeader>
            <CardTitle className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
              근무 정보
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm">
                <Calendar className="w-4 h-4 text-blue-400" />
                <span className="text-gray-300">입사일: {staff.hireDate || '입사일 없음'}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Clock className="w-4 h-4 text-blue-400" />
                <span className="text-gray-300">근무시간: {staff.workHours || 0}시간</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Activity className="w-4 h-4 text-blue-400" />
                <span className="text-gray-300">마지막 활동: {staff.lastActive || '활동 기록 없음'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 성과 정보 */}
        <Card className="quantum-glass quantum-hover border-purple-500/30">
          <CardHeader>
            <CardTitle className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
              성과 정보
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm">
                <Star className="w-4 h-4 text-purple-400" />
                <span className="text-gray-300">성과 점수: {staff.performance || 0}점</span>
              </div>
              
              {/* 성과 게이지 */}
              {staff.performance && (
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>성과</span>
                    <span>{staff.performance}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        staff.performance >= 80 ? 'bg-green-500' :
                        staff.performance >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.min(staff.performance, 100)}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// 직원 목록 컴포넌트
function StaffList({ onSelectStaff }: { onSelectStaff: (staffId: string) => void }) {
  const [staff, setStaff] = useState<Staff[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'role' | 'department' | 'performance'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive'>('all');
  const [isOffline, setIsOffline] = useState(false);
  
  // 생성/수정 다이얼로그 상태
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingStaff, setEditingStaff] = useState<Staff | null>(null);
  const [formData, setFormData] = useState<StaffFormData>({
    name: '',
    email: '',
    phone: '',
    role: '',
    department: '',
    hireDate: '',
    location: ''
  });

  // 폼 초기화
  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      phone: '',
      role: '',
      department: '',
      hireDate: '',
      location: ''
    });
    setEditingStaff(null);
  };

  // 입력 처리
  const handleInputChange = (field: keyof StaffFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // 폼 제출 처리
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.email.trim() || !formData.role.trim()) {
      toast.error('이름, 이메일, 역할은 필수 입력 항목입니다.');
      return;
    }

    try {
      if (editingStaff) {
        // 수정
        try {
          const response = await fetch(`http://192.168.45.44:5000/api/admin/employees/${editingStaff.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData),
            signal: AbortSignal.timeout(5000)
          });
          
          if (response.ok) {
            toast.success('직원이 성공적으로 수정되었습니다.');
            setIsCreateDialogOpen(false);
            resetForm();
            fetchStaff();
            return;
          }
        } catch (apiError) {
          console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
        }
        
        // 오프라인 모드: 로컬 데이터 수정
        const updatedStaff = staff.map(item => 
          item.id === editingStaff.id 
            ? { ...item, ...formData, updated_at: new Date().toISOString() }
            : item
        );
        
        setStaff(updatedStaff);
        OfflineStorage.saveEmployees(updatedStaff);
        OfflineStorage.setOfflineMode(true);
        toast.success('직원이 오프라인 모드에서 수정되었습니다.');
        setIsCreateDialogOpen(false);
        resetForm();
        
      } else {
        // 생성
        try {
          const response = await fetch('http://192.168.45.44:5000/api/admin/employees', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData),
            signal: AbortSignal.timeout(5000)
          });
          
          if (response.ok) {
            toast.success('직원이 성공적으로 생성되었습니다.');
            setIsCreateDialogOpen(false);
            resetForm();
            fetchStaff();
            return;
          }
        } catch (apiError) {
          console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
        }
        
        // 오프라인 모드: 로컬 데이터 생성
        const newStaff = {
          id: Date.now().toString(),
          ...formData,
          status: 'active' as const,
          workHours: 0,
          performance: 0,
          lastActive: new Date().toISOString(),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        const updatedStaff = [...staff, newStaff];
        setStaff(updatedStaff);
        OfflineStorage.saveEmployees(updatedStaff);
        OfflineStorage.setOfflineMode(true);
        toast.success('직원이 오프라인 모드에서 생성되었습니다.');
        setIsCreateDialogOpen(false);
        resetForm();
      }
    } catch (error) {
      console.error('직원 처리 오류:', error);
      toast.error('직원 처리 중 오류가 발생했습니다.');
    }
  };

  // 수정 모드 시작
  const handleEdit = (staffMember: Staff) => {
    setEditingStaff(staffMember);
    setFormData({
      name: staffMember.name,
      email: staffMember.email,
      phone: staffMember.phone,
      role: staffMember.role,
      department: staffMember.department,
      hireDate: staffMember.hireDate,
      location: staffMember.location
    });
    setIsCreateDialogOpen(true);
  };

  // 직원 목록 조회
  const fetchStaff = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // 온라인 모드 시도
      try {
        const response = await apiCall('/api/admin/employees');
        if (response.success && response.data) {
          setStaff(response.data);
          OfflineStorage.saveEmployees(response.data);
          OfflineStorage.saveLastSync();
          OfflineStorage.setOfflineMode(false);
          setIsOffline(false);
          return;
        }
      } catch (apiError) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 전환:', apiError);
      }

      // 오프라인 모드: 로컬 데이터 사용
      let offlineData = OfflineStorage.loadEmployees();
      
      if (offlineData.length === 0) {
        const defaultData = OfflineStorage.createDefaultData();
        offlineData = defaultData.employees;
      }
      
      setStaff(offlineData);
      OfflineStorage.setOfflineMode(true);
      setIsOffline(true);
    } catch (error) {
      console.error('직원 목록 조회 오류:', error);
      setError('직원 목록을 불러오는 중 오류가 발생했습니다.');
      setStaff([]);
    } finally {
      setIsLoading(false);
    }
  };

  // 직원 삭제 처리
  const handleDelete = async (staffMember: Staff) => {
    if (!confirm(`"${staffMember.name}" 직원을 비활성화하시겠습니까?\n\n⚠️ 이 작업은 되돌릴 수 없습니다.`)) {
      return;
    }

    try {
      // 온라인 모드: 백엔드 API 호출
      try {
        const response = await fetch(`http://192.168.45.44:5000/api/admin/employees/${staffMember.id}`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          signal: AbortSignal.timeout(5000)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
          toast.success(result.message || '직원이 성공적으로 비활성화되었습니다.');
          fetchStaff(); // 목록 새로고침
          return;
        } else {
          // 백엔드에서 오류 응답
          const errorMessage = result.error || '직원 비활성화에 실패했습니다.';
          toast.error(errorMessage);
        }
      } catch (apiError) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
      }
      
      // 오프라인 모드: 로컬 데이터 비활성화
      const updatedStaff = staff.map(item => 
        item.id === staffMember.id 
          ? { ...item, status: 'inactive' as const }
          : item
      );
      setStaff(updatedStaff);
      OfflineStorage.saveEmployees(updatedStaff);
      OfflineStorage.setOfflineMode(true);
      toast.success('직원이 오프라인 모드에서 비활성화되었습니다.');
      
    } catch (error) {
      console.error('직원 비활성화 오류:', error);
      toast.error('직원 비활성화 중 오류가 발생했습니다.');
    }
  };

  // 직원 활성화 처리
  const handleActivate = async (staffMember: Staff) => {
    if (!confirm(`"${staffMember.name}" 직원을 활성화하시겠습니까?`)) {
      return;
    }

    try {
      // 온라인 모드: 백엔드 API 호출
      try {
        const response = await fetch(`http://192.168.45.44:5000/api/admin/employees/${staffMember.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'active' }),
          signal: AbortSignal.timeout(5000)
        });
        
        if (response.ok) {
          toast.success('직원이 성공적으로 활성화되었습니다.');
          fetchStaff();
          return;
        }
      } catch (apiError) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
      }
      
      // 오프라인 모드: 로컬 데이터 활성화
      const updatedStaff = staff.map(item => 
        item.id === staffMember.id 
          ? { ...item, status: 'active' as const }
          : item
      );
      setStaff(updatedStaff);
      OfflineStorage.saveEmployees(updatedStaff);
      OfflineStorage.setOfflineMode(true);
      toast.success('직원이 오프라인 모드에서 활성화되었습니다.');
      
    } catch (error) {
      console.error('직원 활성화 오류:', error);
      toast.error('직원 활성화 중 오류가 발생했습니다.');
    }
  };

  useEffect(() => {
    fetchStaff();
  }, []);

  // 통계 계산
  const totalStaff = staff.length;
  const activeStaff = staff.filter(s => s.status === 'active').length;
  const avgPerformance = staff.length > 0 
    ? Math.round(staff.reduce((sum, s) => sum + (s.performance || 0), 0) / staff.length)
    : 0;
  const departments = [...new Set(staff.map(s => s.department).filter(Boolean))].length;

  // 필터링 및 정렬
  const filteredAndSortedStaff = staff
    .filter(s => {
      const matchesSearch = 
        (s.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
        (s.email || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
        (s.role || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
        (s.department || '').toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesStatus = filterStatus === 'all' || s.status === filterStatus;
      
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      const aValue = a[sortBy] || '';
      const bValue = b[sortBy] || '';
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  if (isLoading) {
    return (
      <div className="text-center py-16">
        <div className="quantum-glass rounded-full p-8 w-32 h-32 mx-auto mb-6 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400"></div>
        </div>
        <p className="text-gray-300 text-lg">직원 정보를 불러오는 중...</p>
        <p className="text-gray-400 text-sm mt-2">잠시만 기다려주세요</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-16">
        <div className="quantum-glass rounded-full p-8 w-32 h-32 mx-auto mb-6 flex items-center justify-center">
          <AlertTriangle className="w-16 h-16 text-red-400" />
        </div>
        <h3 className="text-xl font-semibold text-red-400 mb-2">오류가 발생했습니다</h3>
        <p className="text-gray-300 mb-6 max-w-md mx-auto">{error}</p>
        <Button
          onClick={fetchStaff}
          className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 quantum-hover"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          다시 시도
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 통계 카드 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="quantum-glass quantum-hover border-green-500/30">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">총 직원</p>
                <p className="text-2xl font-bold text-green-400">{totalStaff}</p>
              </div>
              <Users className="w-8 h-8 text-green-400/60" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="quantum-glass quantum-hover border-blue-500/30">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">활성 직원</p>
                <p className="text-2xl font-bold text-blue-400">{activeStaff}</p>
              </div>
              <Activity className="w-8 h-8 text-blue-400/60" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="quantum-glass quantum-hover border-purple-500/30">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">평균 성과</p>
                <p className="text-2xl font-bold text-purple-400">{avgPerformance}%</p>
              </div>
              <Star className="w-8 h-8 text-purple-400/60" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="quantum-glass quantum-hover border-orange-500/30">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">부서 수</p>
                <p className="text-2xl font-bold text-orange-400">{departments}</p>
              </div>
              <Building2 className="w-8 h-8 text-orange-400/60" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 검색 및 필터 */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              type="text"
              placeholder="이름, 이메일, 역할, 부서로 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 quantum-glass border-green-500/30 text-white placeholder:text-slate-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20"
            />
          </div>
          
          {/* 생성 버튼 */}
          <Button
            onClick={() => {
              resetForm();
              setIsCreateDialogOpen(true);
            }}
            className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold px-6 py-2 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300"
          >
            <Plus className="w-5 h-5 mr-2" />
            새 직원 추가
          </Button>
          
          <div className="flex gap-2">
            <Select value={filterStatus} onValueChange={(value: any) => setFilterStatus(value)}>
              <SelectTrigger className="quantum-glass border-green-500/30 text-white focus:border-green-500 focus:ring-2 focus:ring-green-500/20">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="quantum-glass border-green-500/30">
                <SelectItem value="all">전체</SelectItem>
                <SelectItem value="active">활성</SelectItem>
                <SelectItem value="inactive">비활성</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
              <SelectTrigger className="quantum-glass border-green-500/30 text-white focus:border-green-500 focus:ring-2 focus:ring-green-500/20">
                <SortAsc className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="quantum-glass border-green-500/30">
                <SelectItem value="name">이름</SelectItem>
                <SelectItem value="role">역할</SelectItem>
                <SelectItem value="department">부서</SelectItem>
                <SelectItem value="performance">성과</SelectItem>
              </SelectContent>
            </Select>
            
            <Button
              variant="outline"
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              className="quantum-glass border-green-500/30 text-green-400 hover:border-green-500 hover:text-green-300 quantum-hover"
            >
              {sortOrder === 'asc' ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />}
            </Button>
          </div>
        </div>
        
        {isOffline && (
          <div className="flex items-center gap-2 p-3 bg-yellow-900/20 border border-yellow-600/30 rounded-lg">
            <Wifi className="w-4 h-4 text-yellow-400" />
            <span className="text-yellow-400 text-sm">오프라인 모드 - 로컬 데이터 사용 중</span>
            <Button
              onClick={fetchStaff}
              size="sm"
              variant="outline"
              className="ml-auto border-yellow-600/50 text-yellow-400 hover:border-yellow-500 hover:text-yellow-300 quantum-hover"
            >
              <RefreshCw className="w-3 h-3 mr-1" />
              동기화
            </Button>
          </div>
        )}
      </div>

      {/* 직원 목록 */}
      <div className="space-y-2">
        {filteredAndSortedStaff.length > 0 ? (
          filteredAndSortedStaff.map((staff) => (
            <Card 
              key={staff.id}
              className="quantum-glass quantum-hover border-green-500/30 transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-green-500/20"
            >
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div 
                    className="flex items-center space-x-4 min-w-0 flex-1 cursor-pointer"
                    onClick={() => onSelectStaff(staff.id)}
                  >
                    <div className="w-12 h-12 bg-gradient-to-br from-green-500/20 to-emerald-500/20 rounded-full flex items-center justify-center text-white font-bold text-lg flex-shrink-0">
                      {(staff.name || '?').charAt(0)}
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="font-semibold text-lg truncate text-white">
                        {staff.name || '이름 없음'}
                      </h3>
                      <p className="text-sm text-gray-400 truncate">
                        {staff.email || '이메일 없음'}
                      </p>
                      <p className="text-sm text-gray-500 truncate">
                        {staff.role || '역할 없음'} • {staff.department || '부서 없음'}
                      </p>
                      {staff.performance && (
                        <p className="text-sm text-green-400">성과: {staff.performance}점</p>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3 flex-shrink-0">
                    <Badge 
                      variant="secondary" 
                      className={`${
                        staff.status === 'active' 
                          ? 'bg-green-900/50 text-green-300 border-green-500/30' 
                          : 'bg-red-900/50 text-red-300 border-red-500/30'
                      }`}
                    >
                      {staff.status === 'active' ? '활성' : '비활성'}
                    </Badge>
                    
                    {/* 삭제 버튼 */}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(staff);
                      }}
                      className="border-red-600/50 text-red-400 hover:border-red-500 hover:text-red-300 quantum-hover"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                    
                    {/* 수정 버튼 */}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEdit(staff);
                      }}
                      className="border-blue-600/50 text-blue-400 hover:border-blue-500 hover:text-blue-300 quantum-hover"
                    >
                      <Edit className="w-4 h-4" />
                    </Button>

                    {/* 활성화 버튼 */}
                    {staff.status === 'inactive' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleActivate(staff);
                        }}
                        className="border-green-600/50 text-green-400 hover:border-green-500 hover:text-green-300 quantum-hover"
                      >
                        <CheckCircle className="w-4 h-4" />
                      </Button>
                    )}

                    <div className="text-gray-400">
                      <ArrowLeft className="w-4 h-4 rotate-180" />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <div className="text-center py-16">
            <div className="quantum-glass rounded-full p-8 w-32 h-32 mx-auto mb-6 flex items-center justify-center">
              <User className="w-16 h-16 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-300 mb-2">직원이 없습니다</h3>
            <p className="text-gray-400 mb-6 max-w-md mx-auto">검색 조건에 맞는 직원을 찾을 수 없습니다</p>
            <Button
              onClick={() => {
                setSearchTerm('');
                setFilterStatus('all');
              }}
              className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 quantum-hover"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              필터 초기화
            </Button>
          </div>
        )}
      </div>
      
      {/* 생성/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="bg-slate-800/95 border-green-500/50 text-white max-w-md mx-auto backdrop-blur-xl">
          <DialogHeader>
            <DialogTitle className="text-xl text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-400">
              {editingStaff ? '직원 수정' : '직원 추가'}
            </DialogTitle>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name" className="text-gray-300 block mb-2">이름 *</Label>
              <Input
                id="name"
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                className="bg-slate-700/50 border-green-500/50 text-white placeholder:text-slate-400 focus:border-green-400 focus:ring-2 focus:ring-green-400/20"
                placeholder="직원 이름"
                required
              />
            </div>
            
            <div>
              <Label htmlFor="email" className="text-gray-300 block mb-2">이메일 *</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                className="bg-slate-700/50 border-green-500/50 text-white placeholder:text-slate-400 focus:border-green-400 focus:ring-2 focus:ring-green-400/20"
                placeholder="이메일 주소"
                required
              />
            </div>
            
            <div>
              <Label htmlFor="phone" className="text-gray-300 block mb-2">전화번호</Label>
              <Input
                id="phone"
                type="tel"
                value={formData.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                className="bg-slate-700/50 border-green-500/50 text-white placeholder:text-slate-400 focus:border-green-400 focus:ring-2 focus:ring-green-400/20"
                placeholder="전화번호"
              />
            </div>
            
            <div>
              <Label htmlFor="role" className="text-gray-300 block mb-2">역할 *</Label>
              <Input
                id="role"
                type="text"
                value={formData.role}
                onChange={(e) => handleInputChange('role', e.target.value)}
                className="bg-slate-700/50 border-green-500/50 text-white placeholder:text-slate-400 focus:border-green-400 focus:ring-2 focus:ring-green-400/20"
                placeholder="직원 역할"
                required
              />
            </div>
            
            <div>
              <Label htmlFor="department" className="text-gray-300 block mb-2">부서</Label>
              <Input
                id="department"
                type="text"
                value={formData.department}
                onChange={(e) => handleInputChange('department', e.target.value)}
                className="bg-slate-700/50 border-green-500/50 text-white placeholder:text-slate-400 focus:border-green-400 focus:ring-2 focus:ring-green-400/20"
                placeholder="소속 부서"
              />
            </div>
            
            <div>
              <Label htmlFor="hireDate" className="text-gray-300 block mb-2">입사일</Label>
              <Input
                id="hireDate"
                type="date"
                value={formData.hireDate}
                onChange={(e) => handleInputChange('hireDate', e.target.value)}
                className="bg-slate-700/50 border-green-500/50 text-white placeholder:text-slate-400 focus:border-green-400 focus:ring-2 focus:ring-green-400/20"
              />
            </div>
            
            <div>
              <Label htmlFor="location" className="text-gray-300 block mb-2">위치</Label>
              <Input
                id="location"
                type="text"
                value={formData.location}
                onChange={(e) => handleInputChange('location', e.target.value)}
                className="bg-slate-700/50 border-green-500/50 text-white placeholder:text-slate-400 focus:border-green-400 focus:ring-2 focus:ring-green-400/20"
                placeholder="근무 위치"
              />
            </div>
            
            <div className="flex justify-end space-x-2 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsCreateDialogOpen(false)}
                className="border-gray-600/50 text-gray-300 hover:border-gray-500 hover:text-gray-200"
              >
                취소
              </Button>
              <Button 
                type="submit" 
                className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
              >
                {editingStaff ? '수정' : '추가'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// useSearchParams를 사용하는 컴포넌트
function StaffPageContent() {
  const searchParams = useSearchParams();
  const [selectedStaffId, setSelectedStaffId] = useState<string | null>(
    searchParams.get('staffId')
  );

  const handleBackToList = () => {
    setSelectedStaffId(null);
  };

  return (
    <ProtectedRoute requiredRole="admin" requiredPermission={{ module: 'staff_management', action: 'view' }}>
      <div className="min-h-screen bg-gradient-to-br from-green-900 via-emerald-900 to-teal-900 text-white p-4 sm:p-6 lg:p-8">
        <div className="max-w-7xl mx-auto">
          {/* 헤더 */}
          <div className="mb-8">
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-2xl sm:text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-400 quantum-pulse">
                    직원 관리
                  </h1>
                </div>
                <p className="text-gray-300 text-sm sm:text-base">직원 정보를 관리하고 성과를 추적하세요</p>
              </div>
            </div>
          </div>

          {/* 메인 콘텐츠 */}
          {selectedStaffId ? (
            <StaffDetail staffId={selectedStaffId} onBack={handleBackToList} />
          ) : (
            <StaffList onSelectStaff={setSelectedStaffId} />
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}

// Suspense로 감싸진 메인 컴포넌트
export default function StaffPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-green-900 via-emerald-900 to-teal-900 text-white flex items-center justify-center">
        <div className="quantum-glass rounded-full p-8 w-32 h-32 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400"></div>
        </div>
      </div>
    }>
      <StaffPageContent />
    </Suspense>
  );
} 