"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Button } from '../../src/components/ui/button';
import { Input } from '../../src/components/ui/input';
import { Badge } from '../../src/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../../src/components/ui/dialog';
import { Label } from '../../src/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../src/components/ui/select';
import { 
  Store, 
  Users, 
  TrendingUp, 
  Plus, 
  Edit, 
  Trash2, 
  Eye,
  Building2,
  MapPin,
  Phone,
  Mail,
  Calendar,
  DollarSign,
  Star,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { toast } from 'sonner';

interface Store {
  id: number;
  name: string;
  location: string;
  manager: string;
  status: 'operating' | 'maintenance' | 'closed';
  dailySales: number;
  employeeCount: number;
  rating: number;
}

interface EmployeeCreationData {
  employeeName: string;
  employeeEmail: string;
  employeePhone: string;
  position: string;
  department: string;
  hireDate: string;
  salary: string;
}

export default function BranchAdminPage() {
  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState<EmployeeCreationData>({
    employeeName: '',
    employeeEmail: '',
    employeePhone: '',
    position: '',
    department: '',
    hireDate: '',
    salary: ''
  });
  const [errors, setErrors] = useState<Partial<EmployeeCreationData>>({});

  useEffect(() => {
    // 샘플 데이터 로드
    const sampleStores: Store[] = [
      {
        id: 1,
        name: '강남점',
        location: '서울시 강남구 역삼동',
        manager: '김철수',
        status: 'operating',
        dailySales: 3500000,
        employeeCount: 15,
        rating: 4.8
      },
      {
        id: 2,
        name: '홍대점',
        location: '서울시 마포구 홍대입구',
        manager: '이영희',
        status: 'operating',
        dailySales: 2800000,
        employeeCount: 12,
        rating: 4.6
      },
      {
        id: 3,
        name: '신촌점',
        location: '서울시 서대문구 신촌동',
        manager: '박민수',
        status: 'maintenance',
        dailySales: 0,
        employeeCount: 8,
        rating: 4.7
      },
      {
        id: 4,
        name: '잠실점',
        location: '서울시 송파구 잠실동',
        manager: '최지영',
        status: 'operating',
        dailySales: 4200000,
        employeeCount: 18,
        rating: 4.9
      }
    ];

    setStores(sampleStores);
    setLoading(false);
  }, []);

  const handleInputChange = (field: keyof EmployeeCreationData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // 에러 메시지 초기화
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const validateForm = () => {
    const newErrors: Partial<EmployeeCreationData> = {};

    if (!formData.employeeName.trim()) {
      newErrors.employeeName = '직원 이름을 입력해주세요';
    }
    if (!formData.employeeEmail.trim()) {
      newErrors.employeeEmail = '이메일을 입력해주세요';
    } else if (!/\S+@\S+\.\S+/.test(formData.employeeEmail)) {
      newErrors.employeeEmail = '올바른 이메일 형식을 입력해주세요';
    }
    if (!formData.employeePhone.trim()) {
      newErrors.employeePhone = '전화번호를 입력해주세요';
    }
    if (!formData.position.trim()) {
      newErrors.position = '직책을 입력해주세요';
    }
    if (!formData.department.trim()) {
      newErrors.department = '부서를 입력해주세요';
    }
    if (!formData.hireDate) {
      newErrors.hireDate = '입사일을 선택해주세요';
    }
    if (!formData.salary.trim()) {
      newErrors.salary = '급여를 입력해주세요';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const generateTempPassword = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let password = '';
    for (let i = 0; i < 8; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return password;
  };

  const handleCreateEmployeeAndAccount = async () => {
    if (!validateForm()) {
      toast.error('입력 정보를 확인해주세요');
      return;
    }

    try {
      const tempPassword = generateTempPassword();
      
      // 실제로는 API 호출
      console.log('직원 생성 데이터:', formData);
      console.log('임시 비밀번호:', tempPassword);
      
      toast.success('직원 계정이 성공적으로 생성되었습니다');
      setShowCreateForm(false);
      setFormData({
        employeeName: '',
        employeeEmail: '',
        employeePhone: '',
        position: '',
        department: '',
        hireDate: '',
        salary: ''
      });
    } catch (error) {
      toast.error('직원 계정 생성에 실패했습니다');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operating': return 'bg-green-500/20 text-green-400';
      case 'maintenance': return 'bg-yellow-500/20 text-yellow-400';
      case 'closed': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'operating': return '운영중';
      case 'maintenance': return '점검중';
      case 'closed': return '폐점';
      default: return '알 수 없음';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR').format(amount);
  };

  if (loading) {
    return (
      <div className="min-h-screen p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-white">로딩 중...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Store className="w-6 h-6" />
          매장 관리자 대시보드
        </h1>
        <p className="text-gray-300 mt-2">매장 현황 및 직원 관리</p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">총 매장</p>
                <p className="text-2xl font-bold text-white">{stores.length}</p>
              </div>
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <Store className="w-6 h-6 text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">운영중</p>
                <p className="text-2xl font-bold text-white">
                  {stores.filter(s => s.status === 'operating').length}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">총 직원</p>
                <p className="text-2xl font-bold text-white">
                  {stores.reduce((sum, store) => sum + store.employeeCount, 0)}
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-purple-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">일일 매출</p>
                <p className="text-2xl font-bold text-white">
                  ₩{formatCurrency(stores.reduce((sum, store) => sum + store.dailySales, 0))}
                </p>
              </div>
              <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-yellow-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 매장 목록 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="text-white">매장 목록</CardTitle>
            <Button
              onClick={() => setShowCreateForm(true)}
              className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              직원 추가
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {stores.map((store) => (
              <div
                key={store.id}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-all duration-300"
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-semibold text-white">{store.name}</h3>
                  <Badge className={getStatusColor(store.status)}>
                    {getStatusText(store.status)}
                  </Badge>
                </div>
                
                <div className="space-y-3">
                  <div className="flex items-center text-gray-300">
                    <MapPin className="w-4 h-4 mr-2" />
                    <span className="text-sm">{store.location}</span>
                  </div>
                  
                  <div className="flex items-center text-gray-300">
                    <Users className="w-4 h-4 mr-2" />
                    <span className="text-sm">매니저: {store.manager}</span>
                  </div>
                  
                  <div className="flex items-center text-gray-300">
                    <DollarSign className="w-4 h-4 mr-2" />
                    <span className="text-sm">일일 매출: ₩{formatCurrency(store.dailySales)}</span>
                  </div>
                  
                  <div className="flex items-center text-gray-300">
                    <Users className="w-4 h-4 mr-2" />
                    <span className="text-sm">직원 수: {store.employeeCount}명</span>
                  </div>
                  
                  <div className="flex items-center text-gray-300">
                    <Star className="w-4 h-4 mr-2" />
                    <span className="text-sm">평점: {store.rating}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 직원 추가 다이얼로그 */}
      <Dialog open={showCreateForm} onOpenChange={setShowCreateForm}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20">
          <DialogHeader>
            <DialogTitle className="text-white">새 직원 추가</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="employeeName" className="text-gray-300">직원 이름</Label>
              <Input
                id="employeeName"
                value={formData.employeeName}
                onChange={(e) => handleInputChange('employeeName', e.target.value)}
                className="bg-white/10 border-white/20 text-white"
                placeholder="직원 이름을 입력하세요"
              />
              {errors.employeeName && (
                <p className="text-red-400 text-sm mt-1">{errors.employeeName}</p>
              )}
            </div>

            <div>
              <Label htmlFor="employeeEmail" className="text-gray-300">이메일</Label>
              <Input
                id="employeeEmail"
                type="email"
                value={formData.employeeEmail}
                onChange={(e) => handleInputChange('employeeEmail', e.target.value)}
                className="bg-white/10 border-white/20 text-white"
                placeholder="이메일을 입력하세요"
              />
              {errors.employeeEmail && (
                <p className="text-red-400 text-sm mt-1">{errors.employeeEmail}</p>
              )}
            </div>

            <div>
              <Label htmlFor="employeePhone" className="text-gray-300">전화번호</Label>
              <Input
                id="employeePhone"
                value={formData.employeePhone}
                onChange={(e) => handleInputChange('employeePhone', e.target.value)}
                className="bg-white/10 border-white/20 text-white"
                placeholder="전화번호를 입력하세요"
              />
              {errors.employeePhone && (
                <p className="text-red-400 text-sm mt-1">{errors.employeePhone}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="position" className="text-gray-300">직책</Label>
                <Input
                  id="position"
                  value={formData.position}
                  onChange={(e) => handleInputChange('position', e.target.value)}
                  className="bg-white/10 border-white/20 text-white"
                  placeholder="직책을 입력하세요"
                />
                {errors.position && (
                  <p className="text-red-400 text-sm mt-1">{errors.position}</p>
                )}
              </div>

              <div>
                <Label htmlFor="department" className="text-gray-300">부서</Label>
                <Input
                  id="department"
                  value={formData.department}
                  onChange={(e) => handleInputChange('department', e.target.value)}
                  className="bg-white/10 border-white/20 text-white"
                  placeholder="부서를 입력하세요"
                />
                {errors.department && (
                  <p className="text-red-400 text-sm mt-1">{errors.department}</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="hireDate" className="text-gray-300">입사일</Label>
                <Input
                  id="hireDate"
                  type="date"
                  value={formData.hireDate}
                  onChange={(e) => handleInputChange('hireDate', e.target.value)}
                  className="bg-white/10 border-white/20 text-white"
                />
                {errors.hireDate && (
                  <p className="text-red-400 text-sm mt-1">{errors.hireDate}</p>
                )}
              </div>

              <div>
                <Label htmlFor="salary" className="text-gray-300">급여</Label>
                <Input
                  id="salary"
                  value={formData.salary}
                  onChange={(e) => handleInputChange('salary', e.target.value)}
                  className="bg-white/10 border-white/20 text-white"
                  placeholder="급여를 입력하세요"
                />
                {errors.salary && (
                  <p className="text-red-400 text-sm mt-1">{errors.salary}</p>
                )}
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-2 mt-6">
            <Button
              variant="outline"
              onClick={() => setShowCreateForm(false)}
              className="border-white/20 text-white hover:bg-white/10"
            >
              취소
            </Button>
            <Button
              onClick={handleCreateEmployeeAndAccount}
              className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
            >
              직원 추가
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
} 