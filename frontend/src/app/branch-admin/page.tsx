"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, DollarSign, Clock, TrendingUp, Store, Building, UserPlus, Mail, Phone, Shield, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, Input, Label, Textarea, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Alert, AlertDescription } from '@/components/ui';

interface Branch {
  id: number;
  name: string;
  brand_id: number;
  address: string;
  phone: string;
  status: string;
  created_at: string;
}

interface Employee {
  id: number;
  username: string;
  name?: string;
  email?: string;
  role: string;
  position?: string;
  department?: string;
  status: string;
  branch_id?: number;
  created_at: string;
}

interface Brand {
  id: number;
  name: string;
  industry_id: number;
  description?: string;
  status: string;
  created_at: string;
}

interface BranchStats {
  totalEmployees: number;
  activeEmployees: number;
  totalRevenue: number;
  averageWorkHours: number;
  customerSatisfaction: number;
  totalBranches: number;
  activeBranches: number;
}

interface EmployeeAccount {
  id: number;
  username: string;
  name: string;
  email: string;
  phone: string;
  position: string;
  department: string;
  branch_id: number;
  status: string;
  created_at: string;
}

interface EmployeeCreationData {
  name: string;
  email: string;
  phone: string;
  position: string;
  department: string;
  branch_id: number;
}

export default function BranchAdminPage() {
  const [branches, setBranches] = useState<Branch[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [employeeAccounts, setEmployeeAccounts] = useState<EmployeeAccount[]>([]);
  const [stats, setStats] = useState<BranchStats>({
    totalEmployees: 0,
    activeEmployees: 0,
    totalRevenue: 0,
    averageWorkHours: 0,
    customerSatisfaction: 0,
    totalBranches: 0,
    activeBranches: 0
  });
  const [loading, setLoading] = useState(true);
  
  // 직원 생성 관련 상태
  const [showAddEmployeeDialog, setShowAddEmployeeDialog] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [newEmployeeData, setNewEmployeeData] = useState<EmployeeCreationData>({
    name: '',
    email: '',
    phone: '',
    position: '',
    department: '',
    branch_id: 0
  });
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [emailChecking, setEmailChecking] = useState(false);
  const [emailAvailable, setEmailAvailable] = useState(true);

  useEffect(() => {
    fetchBranchData();
  }, []);

  // 실시간 이메일 중복 확인
  useEffect(() => {
    if (newEmployeeData.email && newEmployeeData.email.length > 3) {
      setEmailChecking(true);
      const isDuplicate = employeeAccounts.some(emp => emp.email === newEmployeeData.email);
      setEmailAvailable(!isDuplicate);
      setEmailChecking(false);
    }
  }, [newEmployeeData.email, employeeAccounts]);

  const fetchBranchData = async () => {
    try {
      setLoading(true);
      
      // 모든 API 호출을 병렬로 실행
      const [branchesRes, employeesRes, brandsRes] = await Promise.all([
        fetch('/api/admin/branches'),
        fetch('/api/admin/employees'),
        fetch('/api/admin/brands')
      ]);

      let branchesList: Branch[] = [];
      let employeesList: Employee[] = [];
      let brandsList: Brand[] = [];

      // 매장 데이터
      if (branchesRes.ok) {
        const branchesData = await branchesRes.json();
        branchesList = branchesData.data || branchesData.branches || [];
        setBranches(branchesList);
      }

      // 직원 데이터
      if (employeesRes.ok) {
        const employeesData = await employeesRes.json();
        employeesList = employeesData.data || employeesData.employees || [];
        setEmployees(employeesList);
      }

      // 브랜드 데이터
      if (brandsRes.ok) {
        const brandsData = await brandsRes.json();
        brandsList = brandsData.data || brandsData.brands || [];
        setBrands(brandsList);
      }

      // 통계 계산
      const activeEmployees = employeesList.filter(emp => emp.status === 'active').length;
      const activeBranches = branchesList.filter(branch => branch.status === 'active').length;
      
      // 샘플 데이터 (실제로는 API에서 가져와야 함)
      const totalRevenue = branchesList.length * 2500000; // 매장당 평균 250만원
      const averageWorkHours = 8.5; // 평균 근무시간
      const customerSatisfaction = 4.8; // 고객 만족도

      setStats({
        totalEmployees: employeesList.length,
        activeEmployees,
        totalRevenue,
        averageWorkHours,
        customerSatisfaction,
        totalBranches: branchesList.length,
        activeBranches
      });

    } catch (error) {
      console.error('매장 데이터 로딩 오류:', error);
      toast.error('데이터를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 입력 유효성 검사
  const validateInputs = (data: EmployeeCreationData) => {
    const errors: Record<string, string> = {};

    if (!data.name.trim()) {
      errors.name = '직원 이름을 입력해주세요';
    }

    if (!data.email.trim()) {
      errors.email = '이메일을 입력해주세요';
    } else if (!isValidEmail(data.email)) {
      errors.email = '올바른 이메일 형식을 입력해주세요';
    } else if (!emailAvailable) {
      errors.email = '이미 사용 중인 이메일입니다';
    }

    if (!data.phone.trim()) {
      errors.phone = '전화번호를 입력해주세요';
    } else if (!isValidPhone(data.phone)) {
      errors.phone = '올바른 전화번호 형식을 입력해주세요';
    }

    if (!data.position.trim()) {
      errors.position = '직책을 입력해주세요';
    }

    if (!data.department.trim()) {
      errors.department = '부서를 입력해주세요';
    }

    if (!data.branch_id) {
      errors.branch_id = '매장을 선택해주세요';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // 이메일 유효성 검사
  const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  // 전화번호 유효성 검사
  const isValidPhone = (phone: string) => {
    const phoneRegex = /^[0-9-+\s()]+$/;
    return phoneRegex.test(phone) && phone.length >= 10;
  };

  // 임시 비밀번호 생성
  const generateTempPassword = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let password = '';
    for (let i = 0; i < 8; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return password;
  };

  // 직원 및 계정 생성
  const handleCreateEmployeeAndAccount = async () => {
    if (!validateInputs(newEmployeeData)) {
      return;
    }

    setIsCreating(true);
    try {
      // 실제로는 API 호출을 해야 하지만, 여기서는 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000));

      const tempPassword = generateTempPassword();
      const newEmployee: EmployeeAccount = {
        id: Date.now(),
        username: newEmployeeData.email.split('@')[0],
        name: newEmployeeData.name,
        email: newEmployeeData.email,
        phone: newEmployeeData.phone,
        position: newEmployeeData.position,
        department: newEmployeeData.department,
        branch_id: newEmployeeData.branch_id,
        status: 'active',
        created_at: new Date().toISOString()
      };

      setEmployeeAccounts(prev => [...prev, newEmployee]);
      setEmployees(prev => [...prev, newEmployee]);

      toast.success('직원 및 계정이 성공적으로 생성되었습니다!');
      showCreationResult(newEmployee, tempPassword);
      
      // 폼 초기화
      setNewEmployeeData({
        name: '',
        email: '',
        phone: '',
        position: '',
        department: '',
        branch_id: 0
      });
      setShowAddEmployeeDialog(false);
      setValidationErrors({});

    } catch (error) {
      console.error('직원 생성 오류:', error);
      toast.error('직원 생성 중 오류가 발생했습니다.');
    } finally {
      setIsCreating(false);
    }
  };

  // 생성 결과 표시
  const showCreationResult = (employee: EmployeeAccount, tempPassword: string) => {
    const branch = branches.find(b => b.id === employee.branch_id);
    alert(`✅ 직원 및 계정 생성 완료!

📋 생성된 정보:
• 직원명: ${employee.name}
• 이메일: ${employee.email}
• 임시 비밀번호: ${tempPassword}
• 매장: ${branch?.name || '미지정'}
• 직책: ${employee.position}
• 부서: ${employee.department}

⚠️ 임시 비밀번호를 안전하게 전달해주세요.
직원이 첫 로그인 시 비밀번호를 변경하도록 안내해주세요.`);
  };

  // 브랜드 ID로 브랜드 정보 찾기
  const getBrandName = (brandId: number) => {
    const brand = brands.find(b => b.id === brandId);
    return brand?.name || '알 수 없음';
  };

  // 매장별 직원 수 계산
  const getEmployeeCount = (branchId: number) => {
    return employees.filter(emp => emp.branch_id === branchId).length;
  };

  // 매장별 활성 직원 수 계산
  const getActiveEmployeeCount = (branchId: number) => {
    return employees.filter(emp => emp.branch_id === branchId && emp.status === 'active').length;
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-lg mb-2">로딩 중...</div>
            <div className="text-sm text-gray-500">매장 데이터를 가져오는 중입니다</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">매장 관리자</h1>
        <p className="text-gray-600">매장별 직원 및 운영 관리</p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 직원</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalEmployees}명</div>
            <p className="text-xs text-muted-foreground">활성: {stats.activeEmployees}명</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 매장</CardTitle>
            <Store className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalBranches}개</div>
            <p className="text-xs text-muted-foreground">활성: {stats.activeBranches}개</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평균 근무시간</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.averageWorkHours}시간</div>
            <p className="text-xs text-muted-foreground">직원당 평균</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">고객 만족도</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.customerSatisfaction}/5.0</div>
            <p className="text-xs text-muted-foreground">평균 평점</p>
          </CardContent>
        </Card>
      </div>

      {/* 직원 생성 버튼 */}
      <div className="mb-6">
        <Dialog open={showAddEmployeeDialog} onOpenChange={setShowAddEmployeeDialog}>
          <DialogTrigger asChild>
            <button className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              <UserPlus className="h-4 w-4" />
              직원 + 계정 생성
            </button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                직원 및 계정 생성
              </DialogTitle>
            </DialogHeader>
            
            <div className="space-y-4">
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  직원 정보와 함께 시스템 계정을 동시에 생성합니다. 임시 비밀번호가 자동으로 생성됩니다.
                </AlertDescription>
              </Alert>

              <div className="space-y-3">
                <div>
                  <Label htmlFor="name">직원 이름 *</Label>
                  <Input
                    id="name"
                    value={newEmployeeData.name}
                    onChange={(e) => setNewEmployeeData(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="홍길동"
                    className={validationErrors.name ? 'border-red-500' : ''}
                  />
                  {validationErrors.name && (
                    <p className="text-sm text-red-500 mt-1">{validationErrors.name}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="email">이메일 *</Label>
                  <div className="relative">
                    <Input
                      id="email"
                      type="email"
                      value={newEmployeeData.email}
                      onChange={(e) => setNewEmployeeData(prev => ({ ...prev, email: e.target.value }))}
                      placeholder="employee@company.com"
                      className={validationErrors.email ? 'border-red-500' : ''}
                    />
                    {emailChecking && (
                      <Loader2 className="h-4 w-4 animate-spin absolute right-3 top-3 text-gray-400" />
                    )}
                    {!emailChecking && newEmployeeData.email && (
                      emailAvailable ? (
                        <CheckCircle className="h-4 w-4 text-green-500 absolute right-3 top-3" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-red-500 absolute right-3 top-3" />
                      )
                    )}
                  </div>
                  {validationErrors.email && (
                    <p className="text-sm text-red-500 mt-1">{validationErrors.email}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="phone">전화번호 *</Label>
                  <Input
                    id="phone"
                    value={newEmployeeData.phone}
                    onChange={(e) => setNewEmployeeData(prev => ({ ...prev, phone: e.target.value }))}
                    placeholder="010-1234-5678"
                    className={validationErrors.phone ? 'border-red-500' : ''}
                  />
                  {validationErrors.phone && (
                    <p className="text-sm text-red-500 mt-1">{validationErrors.phone}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="position">직책 *</Label>
                  <Input
                    id="position"
                    value={newEmployeeData.position}
                    onChange={(e) => setNewEmployeeData(prev => ({ ...prev, position: e.target.value }))}
                    placeholder="매니저"
                    className={validationErrors.position ? 'border-red-500' : ''}
                  />
                  {validationErrors.position && (
                    <p className="text-sm text-red-500 mt-1">{validationErrors.position}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="department">부서 *</Label>
                  <Input
                    id="department"
                    value={newEmployeeData.department}
                    onChange={(e) => setNewEmployeeData(prev => ({ ...prev, department: e.target.value }))}
                    placeholder="영업팀"
                    className={validationErrors.department ? 'border-red-500' : ''}
                  />
                  {validationErrors.department && (
                    <p className="text-sm text-red-500 mt-1">{validationErrors.department}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="branch">매장 선택 *</Label>
                  <Select
                    value={newEmployeeData.branch_id.toString()}
                    onValueChange={(value) => setNewEmployeeData(prev => ({ ...prev, branch_id: parseInt(value) }))}
                  >
                    <SelectTrigger className={validationErrors.branch_id ? 'border-red-500' : ''}>
                      <SelectValue placeholder="매장을 선택하세요" />
                    </SelectTrigger>
                    <SelectContent>
                      {branches.map((branch) => (
                        <SelectItem key={branch.id} value={branch.id.toString()}>
                          {branch.name} ({getBrandName(branch.brand_id)})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {validationErrors.branch_id && (
                    <p className="text-sm text-red-500 mt-1">{validationErrors.branch_id}</p>
                  )}
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => setShowAddEmployeeDialog(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  disabled={isCreating}
                >
                  취소
                </button>
                <button
                  onClick={handleCreateEmployeeAndAccount}
                  disabled={isCreating}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isCreating ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      생성 중...
                    </>
                  ) : (
                    <>
                      <UserPlus className="h-4 w-4 mr-2" />
                      직원 + 계정 생성
                    </>
                  )}
                </button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* 매장별 현황 */}
      <Card className="border border-gray-100 mb-8">
        <CardHeader>
          <CardTitle>매장별 현황</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {branches.slice(0, 9).map((branch) => {
              const employeeCount = getEmployeeCount(branch.id);
              const activeEmployeeCount = getActiveEmployeeCount(branch.id);
              
              return (
                <div key={branch.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-lg">{branch.name}</h4>
                    <span className={`text-xs px-2 py-1 rounded ${
                      branch.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {branch.status === 'active' ? '활성' : '비활성'}
                    </span>
                  </div>
                  <div className="space-y-2 text-sm text-gray-600">
                    <p>브랜드: {getBrandName(branch.brand_id)}</p>
                    <p>직원: {employeeCount}명 (활성: {activeEmployeeCount}명)</p>
                    <p className="text-xs text-gray-500">{branch.address}</p>
                    <p className="text-xs text-gray-500">{branch.phone}</p>
                  </div>
                </div>
              );
            })}
            {branches.length === 0 && (
              <div className="col-span-full text-center py-8 text-gray-500">
                등록된 매장이 없습니다.
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 직원 현황 */}
      <Card className="border border-gray-100">
        <CardHeader>
          <CardTitle>직원 현황</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {employees.slice(0, 9).map((employee) => {
              const branch = branches.find(b => b.id === employee.branch_id);
              
              return (
                <div key={employee.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{employee.name || employee.username}</h4>
                    <span className={`text-xs px-2 py-1 rounded ${
                      employee.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {employee.status === 'active' ? '근무 중' : '비활성'}
                    </span>
                  </div>
                  <div className="space-y-1 text-sm text-gray-600">
                    <p>직책: {employee.position || employee.role}</p>
                    <p>부서: {employee.department || '미지정'}</p>
                    <p>매장: {branch?.name || '미지정'}</p>
                    {employee.email && (
                      <p className="text-xs text-gray-500">{employee.email}</p>
                    )}
                  </div>
                </div>
              );
            })}
            {employees.length === 0 && (
              <div className="col-span-full text-center py-8 text-gray-500">
                등록된 직원이 없습니다.
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 