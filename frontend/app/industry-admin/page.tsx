'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';
import { 
  Building2, 
  Plus, 
  Edit, 
  Trash2, 
  Search, 
  Filter,
  Users,
  Store,
  TrendingUp,
  Activity,
  UserPlus,
  Mail,
  Phone,
  Shield,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';

interface Industry {
  id: number;
  name: string;
  description: string;
  status: 'active' | 'inactive';
  total_brands: number;
  total_stores: number;
  total_employees: number;
  created_at: string;
}

interface Brand {
  id: number;
  name: string;
  description: string;
  industry_id: number;
  status: 'active' | 'inactive';
  created_at: string;
}

interface BrandManager {
  id: number;
  name: string;
  email: string;
  phone: string;
  brand_id: number;
  role: 'brand_manager';
  status: 'active' | 'inactive';
  temp_password: string;
  created_at: string;
}

interface BrandCreationData {
  brand: {
    name: string;
    description: string;
    industry_id: number;
  };
  manager: {
    name: string;
    email: string;
    phone: string;
  };
}

export default function IndustryAdminPage() {
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [brandManagers, setBrandManagers] = useState<BrandManager[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddIndustryDialog, setShowAddIndustryDialog] = useState(false);
  const [showAddBrandDialog, setShowAddBrandDialog] = useState(false);
  const [selectedIndustry, setSelectedIndustry] = useState<Industry | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  
  const [newIndustry, setNewIndustry] = useState({
    name: '',
    description: ''
  });

  const [newBrandData, setNewBrandData] = useState<BrandCreationData>({
    brand: {
      name: '',
      description: '',
      industry_id: 0
    },
    manager: {
      name: '',
      email: '',
      phone: ''
    }
  });

  // 검증 상태
  const [validationErrors, setValidationErrors] = useState<{[key: string]: string}>({});
  const [emailChecking, setEmailChecking] = useState(false);
  const [emailAvailable, setEmailAvailable] = useState<boolean | null>(null);

  // 샘플 데이터
  const sampleIndustries: Industry[] = [
    {
      id: 1,
      name: '음식점',
      description: '음식점 및 카페 관련 업종',
      status: 'active',
      total_brands: 15,
      total_stores: 120,
      total_employees: 450,
      created_at: '2024-01-15'
    },
    {
      id: 2,
      name: '소매업',
      description: '소매 및 도매 관련 업종',
      status: 'active',
      total_brands: 8,
      total_stores: 85,
      total_employees: 320,
      created_at: '2024-01-20'
    },
    {
      id: 3,
      name: '서비스업',
      description: '다양한 서비스 제공 업종',
      status: 'active',
      total_brands: 12,
      total_stores: 95,
      total_employees: 280,
      created_at: '2024-02-01'
    }
  ];

  useEffect(() => {
    // 실제 API 호출 대신 샘플 데이터 사용
    setTimeout(() => {
      setIndustries(sampleIndustries);
      setLoading(false);
    }, 1000);
  }, []);

  // 이메일 중복 체크 (실시간)
  useEffect(() => {
    const email = newBrandData.manager.email;
    if (email && isValidEmail(email)) {
      setEmailChecking(true);
      // 실제로는 API 호출
      setTimeout(() => {
        const isDuplicate = brandManagers.some(manager => manager.email === email);
        setEmailAvailable(!isDuplicate);
        setEmailChecking(false);
      }, 500);
    } else {
      setEmailAvailable(null);
    }
  }, [newBrandData.manager.email, brandManagers]);

  // 입력 검증
  const validateInputs = () => {
    const errors: {[key: string]: string} = {};

    // 브랜드 정보 검증
    if (!newBrandData.brand.name.trim()) {
      errors.brandName = '브랜드명은 필수입니다.';
    } else if (newBrandData.brand.name.length < 2) {
      errors.brandName = '브랜드명은 2자 이상이어야 합니다.';
    }

    if (!newBrandData.brand.description.trim()) {
      errors.brandDescription = '브랜드 설명은 필수입니다.';
    }

    if (!newBrandData.brand.industry_id) {
      errors.industry = '업종을 선택해주세요.';
    }

    // 관리자 정보 검증
    if (!newBrandData.manager.name.trim()) {
      errors.managerName = '관리자명은 필수입니다.';
    }

    if (!newBrandData.manager.email.trim()) {
      errors.managerEmail = '이메일은 필수입니다.';
    } else if (!isValidEmail(newBrandData.manager.email)) {
      errors.managerEmail = '올바른 이메일 형식이 아닙니다.';
    } else if (emailAvailable === false) {
      errors.managerEmail = '이미 사용 중인 이메일입니다.';
    }

    if (!newBrandData.manager.phone.trim()) {
      errors.managerPhone = '전화번호는 필수입니다.';
    } else if (!isValidPhone(newBrandData.manager.phone)) {
      errors.managerPhone = '올바른 전화번호 형식이 아닙니다.';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // 이메일 형식 검증
  const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  // 전화번호 형식 검증
  const isValidPhone = (phone: string) => {
    const phoneRegex = /^[0-9-+\s()]+$/;
    return phoneRegex.test(phone) && phone.length >= 10;
  };

  // 임시 비밀번호 생성
  const generateTempPassword = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < 12; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return password;
  };

  // 브랜드 + 관리자 생성
  const handleCreateBrandAndManager = async () => {
    if (!validateInputs()) {
      toast.error('입력 정보를 확인해주세요.');
      return;
    }

    setIsCreating(true);

    try {
      // 실제로는 API 호출하여 트랜잭션 처리
      await new Promise(resolve => setTimeout(resolve, 2000)); // 시뮬레이션

      const tempPassword = generateTempPassword();
      const newBrandId = brands.length + 1;
      const newManagerId = brandManagers.length + 1;

      // 브랜드 생성
      const newBrand: Brand = {
        id: newBrandId,
        name: newBrandData.brand.name,
        description: newBrandData.brand.description,
        industry_id: newBrandData.brand.industry_id,
        status: 'active',
        created_at: new Date().toISOString().split('T')[0]
      };

      // 브랜드 관리자 생성
      const newManager: BrandManager = {
        id: newManagerId,
        name: newBrandData.manager.name,
        email: newBrandData.manager.email,
        phone: newBrandData.manager.phone,
        brand_id: newBrandId,
        role: 'brand_manager',
        status: 'active',
        temp_password: tempPassword,
        created_at: new Date().toISOString().split('T')[0]
      };

      // 상태 업데이트
      setBrands([...brands, newBrand]);
      setBrandManagers([...brandManagers, newManager]);

      // 업종의 브랜드 수 증가
      setIndustries(industries.map(industry => 
        industry.id === newBrandData.brand.industry_id 
          ? { ...industry, total_brands: industry.total_brands + 1 }
          : industry
      ));

      // 성공 알림
      toast.success('브랜드와 관리자 계정이 성공적으로 생성되었습니다!', {
        description: `브랜드: ${newBrand.name}, 관리자: ${newManager.name}`,
        duration: 5000
      });

      // 생성 결과 모달 표시
      showCreationResult(newBrand, newManager, tempPassword);

      // 폼 초기화
      setNewBrandData({
        brand: { name: '', description: '', industry_id: 0 },
        manager: { name: '', email: '', phone: '' }
      });
      setShowAddBrandDialog(false);
      setValidationErrors({});

    } catch (error) {
      toast.error('브랜드 생성 중 오류가 발생했습니다.', {
        description: '잠시 후 다시 시도해주세요.'
      });
    } finally {
      setIsCreating(false);
    }
  };

  // 생성 결과 표시
  const showCreationResult = (brand: Brand, manager: BrandManager, tempPassword: string) => {
    // 실제로는 별도 모달 컴포넌트를 사용
    alert(`
브랜드 및 관리자 계정 생성 완료!

브랜드 정보:
- 브랜드명: ${brand.name}
- 설명: ${brand.description}
- 상태: 활성

관리자 정보:
- 이름: ${manager.name}
- 이메일: ${manager.email}
- 전화번호: ${manager.phone}
- 임시 비밀번호: ${tempPassword}

⚠️ 임시 비밀번호를 안전하게 보관하시고, 첫 로그인 시 변경해주세요.
    `);
  };

  const filteredIndustries = industries.filter(industry =>
    industry.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    industry.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleAddIndustry = () => {
    if (newIndustry.name.trim()) {
      const newIndustryData: Industry = {
        id: industries.length + 1,
        name: newIndustry.name,
        description: newIndustry.description,
        status: 'active',
        total_brands: 0,
        total_stores: 0,
        total_employees: 0,
        created_at: new Date().toISOString().split('T')[0]
      };
      setIndustries([...industries, newIndustryData]);
      setNewIndustry({ name: '', description: '' });
      setShowAddIndustryDialog(false);
      toast.success('업종이 추가되었습니다.');
    }
  };

  const handleDeleteIndustry = (id: number) => {
    setIndustries(industries.filter(industry => industry.id !== id));
    toast.success('업종이 삭제되었습니다.');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto"></div>
          <p className="mt-4 text-slate-400">업종 데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* 헤더 */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Building2 className="w-8 h-8 text-cyan-400" />
            업종 관리자
          </h1>
          <p className="text-slate-400 mt-2">업종별 브랜드 및 매장 관리</p>
        </div>
        
        <div className="flex gap-3">
          <Dialog open={showAddBrandDialog} onOpenChange={setShowAddBrandDialog}>
            <DialogTrigger asChild>
              <Button className="flex items-center gap-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700">
                <UserPlus className="w-4 h-4" />
                브랜드 + 관리자 생성
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-slate-800 border-slate-600 max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-white flex items-center gap-2">
                  <UserPlus className="w-5 h-5" />
                  브랜드 및 브랜드 관리자 생성
                </DialogTitle>
              </DialogHeader>
              
              <div className="space-y-6">
                {/* 브랜드 정보 섹션 */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Store className="w-5 h-5 text-purple-400" />
                    브랜드 정보
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="brandName" className="text-slate-300">브랜드명 *</Label>
                      <Input
                        id="brandName"
                        value={newBrandData.brand.name}
                        onChange={(e) => setNewBrandData({
                          ...newBrandData,
                          brand: { ...newBrandData.brand, name: e.target.value }
                        })}
                        className={`bg-slate-700 border-slate-600 text-white ${
                          validationErrors.brandName ? 'border-red-500' : ''
                        }`}
                        placeholder="브랜드명을 입력하세요"
                      />
                      {validationErrors.brandName && (
                        <p className="text-red-400 text-sm mt-1">{validationErrors.brandName}</p>
                      )}
                    </div>
                    
                    <div>
                      <Label htmlFor="industry" className="text-slate-300">업종 선택 *</Label>
                      <Select
                        value={newBrandData.brand.industry_id.toString()}
                        onValueChange={(value) => setNewBrandData({
                          ...newBrandData,
                          brand: { ...newBrandData.brand, industry_id: parseInt(value) }
                        })}
                      >
                        <SelectTrigger className={`bg-slate-700 border-slate-600 text-white ${
                          validationErrors.industry ? 'border-red-500' : ''
                        }`}>
                          <SelectValue placeholder="업종을 선택하세요" />
                        </SelectTrigger>
                        <SelectContent className="bg-slate-700 border-slate-600">
                          {industries.map((industry) => (
                            <SelectItem key={industry.id} value={industry.id.toString()}>
                              {industry.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {validationErrors.industry && (
                        <p className="text-red-400 text-sm mt-1">{validationErrors.industry}</p>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="brandDescription" className="text-slate-300">브랜드 설명 *</Label>
                    <Textarea
                      id="brandDescription"
                      value={newBrandData.brand.description}
                      onChange={(e) => setNewBrandData({
                        ...newBrandData,
                        brand: { ...newBrandData.brand, description: e.target.value }
                      })}
                      className={`bg-slate-700 border-slate-600 text-white ${
                        validationErrors.brandDescription ? 'border-red-500' : ''
                      }`}
                      placeholder="브랜드에 대한 설명을 입력하세요"
                      rows={3}
                    />
                    {validationErrors.brandDescription && (
                      <p className="text-red-400 text-sm mt-1">{validationErrors.brandDescription}</p>
                    )}
                  </div>
                </div>

                {/* 관리자 정보 섹션 */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Shield className="w-5 h-5 text-blue-400" />
                    브랜드 관리자 정보
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="managerName" className="text-slate-300">관리자명 *</Label>
                      <Input
                        id="managerName"
                        value={newBrandData.manager.name}
                        onChange={(e) => setNewBrandData({
                          ...newBrandData,
                          manager: { ...newBrandData.manager, name: e.target.value }
                        })}
                        className={`bg-slate-700 border-slate-600 text-white ${
                          validationErrors.managerName ? 'border-red-500' : ''
                        }`}
                        placeholder="관리자 이름을 입력하세요"
                      />
                      {validationErrors.managerName && (
                        <p className="text-red-400 text-sm mt-1">{validationErrors.managerName}</p>
                      )}
                    </div>
                    
                    <div>
                      <Label htmlFor="managerEmail" className="text-slate-300">이메일 *</Label>
                      <div className="relative">
                        <Input
                          id="managerEmail"
                          type="email"
                          value={newBrandData.manager.email}
                          onChange={(e) => setNewBrandData({
                            ...newBrandData,
                            manager: { ...newBrandData.manager, email: e.target.value }
                          })}
                          className={`bg-slate-700 border-slate-600 text-white pr-10 ${
                            validationErrors.managerEmail ? 'border-red-500' : ''
                          }`}
                          placeholder="이메일을 입력하세요"
                        />
                        <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                          {emailChecking ? (
                            <Loader2 className="w-4 h-4 animate-spin text-slate-400" />
                          ) : emailAvailable === true ? (
                            <CheckCircle className="w-4 h-4 text-green-400" />
                          ) : emailAvailable === false ? (
                            <AlertCircle className="w-4 h-4 text-red-400" />
                          ) : null}
                        </div>
                      </div>
                      {validationErrors.managerEmail && (
                        <p className="text-red-400 text-sm mt-1">{validationErrors.managerEmail}</p>
                      )}
                      {emailAvailable === true && (
                        <p className="text-green-400 text-sm mt-1">사용 가능한 이메일입니다.</p>
                      )}
                      {emailAvailable === false && (
                        <p className="text-red-400 text-sm mt-1">이미 사용 중인 이메일입니다.</p>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="managerPhone" className="text-slate-300">전화번호 *</Label>
                    <Input
                      id="managerPhone"
                      value={newBrandData.manager.phone}
                      onChange={(e) => setNewBrandData({
                        ...newBrandData,
                        manager: { ...newBrandData.manager, phone: e.target.value }
                      })}
                      className={`bg-slate-700 border-slate-600 text-white ${
                        validationErrors.managerPhone ? 'border-red-500' : ''
                      }`}
                      placeholder="전화번호를 입력하세요 (예: 010-1234-5678)"
                    />
                    {validationErrors.managerPhone && (
                      <p className="text-red-400 text-sm mt-1">{validationErrors.managerPhone}</p>
                    )}
                  </div>
                </div>

                {/* 안내 메시지 */}
                <Alert className="bg-blue-900/20 border-blue-600">
                  <AlertCircle className="h-4 w-4 text-blue-400" />
                  <AlertDescription className="text-blue-200">
                    브랜드와 관리자 계정이 동시에 생성됩니다. 생성 후 임시 비밀번호가 발급되며, 
                    관리자는 브랜드 관리자 대시보드에 바로 접근할 수 있습니다.
                  </AlertDescription>
                </Alert>

                {/* 버튼 */}
                <div className="flex justify-end gap-2">
                  <Button 
                    variant="outline" 
                    onClick={() => setShowAddBrandDialog(false)}
                    disabled={isCreating}
                  >
                    취소
                  </Button>
                  <Button 
                    onClick={handleCreateBrandAndManager}
                    disabled={isCreating}
                    className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                  >
                    {isCreating ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        생성 중...
                      </>
                    ) : (
                      <>
                        <UserPlus className="w-4 h-4 mr-2" />
                        브랜드 + 관리자 생성
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>

          <Dialog open={showAddIndustryDialog} onOpenChange={setShowAddIndustryDialog}>
            <DialogTrigger asChild>
              <Button variant="outline" className="flex items-center gap-2">
                <Plus className="w-4 h-4" />
                새 업종 추가
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-slate-800 border-slate-600">
              <DialogHeader>
                <DialogTitle className="text-white">새 업종 추가</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name" className="text-slate-300">업종명</Label>
                  <Input
                    id="name"
                    value={newIndustry.name}
                    onChange={(e) => setNewIndustry({...newIndustry, name: e.target.value})}
                    className="bg-slate-700 border-slate-600 text-white"
                    placeholder="업종명을 입력하세요"
                  />
                </div>
                <div>
                  <Label htmlFor="description" className="text-slate-300">설명</Label>
                  <Input
                    id="description"
                    value={newIndustry.description}
                    onChange={(e) => setNewIndustry({...newIndustry, description: e.target.value})}
                    className="bg-slate-700 border-slate-600 text-white"
                    placeholder="업종에 대한 설명을 입력하세요"
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setShowAddIndustryDialog(false)}>
                    취소
                  </Button>
                  <Button onClick={handleAddIndustry}>
                    추가
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* 검색 및 필터 */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
          <Input
            placeholder="업종명 또는 설명으로 검색..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-slate-800 border-slate-600 text-white"
          />
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">총 업종</p>
                <p className="text-2xl font-bold text-white">{industries.length}</p>
              </div>
              <Building2 className="w-8 h-8 text-cyan-400" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">총 브랜드</p>
                <p className="text-2xl font-bold text-white">
                  {industries.reduce((sum, industry) => sum + industry.total_brands, 0)}
                </p>
              </div>
              <Store className="w-8 h-8 text-emerald-400" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">총 매장</p>
                <p className="text-2xl font-bold text-white">
                  {industries.reduce((sum, industry) => sum + industry.total_stores, 0)}
                </p>
              </div>
              <Store className="w-8 h-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">총 직원</p>
                <p className="text-2xl font-bold text-white">
                  {industries.reduce((sum, industry) => sum + industry.total_employees, 0)}
                </p>
              </div>
              <Users className="w-8 h-8 text-yellow-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 업종 목록 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredIndustries.map((industry) => (
          <Card key={industry.id} className="bg-slate-800/50 border-slate-600 backdrop-blur-xl hover:bg-slate-700/50 transition-colors">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-white">{industry.name}</CardTitle>
                  <p className="text-slate-400 text-sm mt-1">{industry.description}</p>
                </div>
                <Badge className={industry.status === 'active' ? 'bg-green-600' : 'bg-red-600'}>
                  {industry.status === 'active' ? '활성' : '비활성'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">브랜드:</span>
                  <span className="text-white font-medium">{industry.total_brands}개</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">매장:</span>
                  <span className="text-white font-medium">{industry.total_stores}개</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">직원:</span>
                  <span className="text-white font-medium">{industry.total_employees}명</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">생성일:</span>
                  <span className="text-white font-medium">{industry.created_at}</span>
                </div>
                
                <div className="flex gap-2 pt-3">
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="flex-1"
                    onClick={() => {
                      setSelectedIndustry(industry);
                      setNewBrandData({
                        ...newBrandData,
                        brand: { ...newBrandData.brand, industry_id: industry.id }
                      });
                      setShowAddBrandDialog(true);
                    }}
                  >
                    <UserPlus className="w-4 h-4 mr-1" />
                    브랜드 추가
                  </Button>
                  <Button size="sm" variant="outline" className="flex-1">
                    <Edit className="w-4 h-4 mr-1" />
                    수정
                  </Button>
                  <Button 
                    size="sm" 
                    variant="destructive" 
                    className="flex-1"
                    onClick={() => handleDeleteIndustry(industry.id)}
                  >
                    <Trash2 className="w-4 h-4 mr-1" />
                    삭제
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredIndustries.length === 0 && (
        <div className="text-center py-12">
          <Building2 className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400 text-lg">업종이 없습니다.</p>
          <p className="text-slate-500 text-sm mt-2">새 업종을 추가해보세요.</p>
        </div>
      )}
    </div>
  );
}