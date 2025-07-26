'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { 
  Building2, 
  Store, 
  Users, 
  TrendingUp, 
  Activity, 
  AlertTriangle,
  Crown,
  BarChart3,
  Settings,
  Bell,
  Plus,
  UserPlus,
  CheckCircle,
  XCircle
} from 'lucide-react';

interface IndustryStats {
  totalIndustries: number;
  totalBrands: number;
  totalStores: number;
  totalEmployees: number;
  activeStores: number;
  totalRevenue: number;
  growthRate: number;
}

interface Industry {
  id: number;
  name: string;
  type: 'hospital' | 'fashion' | 'beauty' | 'your_program' | 'retail';
  brandsCount: number;
  storesCount: number;
  employeesCount: number;
  revenue: number;
  status: 'active' | 'inactive' | 'maintenance';
  lastUpdated: string;
}

interface BrandFormData {
  brand_name: string;
  brand_description: string;
  brand_contact_email: string;
  brand_contact_phone: string;
  brand_address: string;
  admin_name: string;
  admin_email: string;
  admin_phone: string;
}

export default function IndustryDashboard() {
  const [stats, setStats] = useState<IndustryStats>({
    totalIndustries: 0,
    totalBrands: 0,
    totalStores: 0,
    totalEmployees: 0,
    activeStores: 0,
    totalRevenue: 0,
    growthRate: 0
  });

  const [industries, setIndustries] = useState<Industry[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<BrandFormData>({
    brand_name: '',
    brand_description: '',
    brand_contact_email: '',
    brand_contact_phone: '',
    brand_address: '',
    admin_name: '',
    admin_email: '',
    admin_phone: ''
  });

  useEffect(() => {
    // 로그인 시에만 데이터 fetch (실시간 아님)
    loadIndustryData();
  }, []);

  const loadIndustryData = async () => {
    try {
      // 새로운 API 유틸리티 사용
      const { brandApi } = await import('@/utils/api');
      
      const [statsResult, brandsResult] = await Promise.all([
        brandApi.getStats(),
        brandApi.getAll()
      ]);

      if (statsResult.success && statsResult.data) {
        setStats(statsResult.data as IndustryStats);
      } else {
        // API 호출 실패 시 기본 데이터 사용
        console.warn('업종 통계 API 호출 실패:', statsResult.error);
        setStats({
          totalIndustries: 0,
          totalBrands: 0,
          totalStores: 0,
          totalEmployees: 0,
          activeStores: 0,
          totalRevenue: 0,
          growthRate: 0
        });
      }

      if (brandsResult.success && brandsResult.data) {
        const brandsData = brandsResult.data as any;
        // 브랜드 데이터를 업종별로 그룹화하여 업종 데이터 생성
        const groupedIndustries = brandsData.brands?.reduce((acc: any, brand: any) => {
          const industryType = brand.industry_type || 'restaurant';
          if (!acc[industryType]) {
            acc[industryType] = {
              id: industryType,
              name: brand.industry_name || '레스토랑',
              type: industryType,
              brandsCount: 0,
              storesCount: 0,
              employeesCount: 0,
              revenue: 0,
              status: 'active',
              lastUpdated: new Date().toISOString()
            };
          }
          acc[industryType].brandsCount++;
          acc[industryType].storesCount += brand.store_count || 0;
          acc[industryType].employeesCount += brand.employee_count || 0;
          acc[industryType].revenue += brand.revenue || 0;
          return acc;
        }, {});

        setIndustries(Object.values(groupedIndustries || {}));
      }
    } catch (error) {
      console.error('업종 데이터 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof BrandFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateForm = (): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];
    
    if (!formData.brand_name.trim()) errors.push('브랜드명을 입력해주세요.');
    if (!formData.brand_description.trim()) errors.push('브랜드 설명을 입력해주세요.');
    if (!formData.admin_name.trim()) errors.push('관리자 이름을 입력해주세요.');
    if (!formData.admin_email.trim()) errors.push('관리자 이메일을 입력해주세요.');
    if (!formData.admin_phone.trim()) errors.push('관리자 연락처를 입력해주세요.');
    
    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (formData.admin_email && !emailRegex.test(formData.admin_email)) {
      errors.push('올바른 이메일 형식을 입력해주세요.');
    }
    
    // 전화번호 형식 검증
    const phoneRegex = /^[0-9-+\s()]{10,15}$/;
    if (formData.admin_phone && !phoneRegex.test(formData.admin_phone)) {
      errors.push('올바른 전화번호 형식을 입력해주세요.');
    }

    return { isValid: errors.length === 0, errors };
  };

  const handleSubmit = async () => {
    const validation = validateForm();
    if (!validation.isValid) {
      validation.errors.forEach(error => toast.error(error));
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch('/api/industry/create_brand_with_admin', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const result = await response.json();

      if (result.success) {
        toast.success('브랜드와 브랜드관리자 계정이 성공적으로 생성되었습니다!', {
          description: `임시 비밀번호: ${result.data.temp_password}`,
          duration: 10000,
        });
        
        // 폼 초기화
        setFormData({
          brand_name: '',
          brand_description: '',
          brand_contact_email: '',
          brand_contact_phone: '',
          brand_address: '',
          admin_name: '',
          admin_email: '',
          admin_phone: ''
        });
        
        // 다이얼로그 닫기
        setIsCreateDialogOpen(false);
        
        // 데이터 새로고침
        await loadIndustryData();
      } else {
        toast.error(result.error || '브랜드 생성 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('브랜드 생성 오류:', error);
      toast.error('네트워크 오류가 발생했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      brand_name: '',
      brand_description: '',
      brand_contact_email: '',
      brand_contact_phone: '',
      brand_address: '',
      admin_name: '',
      admin_email: '',
      admin_phone: ''
    });
  };

  const getIndustryIcon = (type: string) => {
    switch (type) {
      case 'hospital': return '🏥';
      case 'fashion': return '👗';
      case 'beauty': return '💄';
      case 'your_program': return '🛠️';
      case 'retail': return '🛍️';
      default: return '🏢';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-600';
      case 'inactive': return 'bg-gray-500/20 text-gray-600';
      case 'maintenance': return 'bg-yellow-500/20 text-yellow-600';
      default: return 'bg-gray-500/20 text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* 헤더 */}
      <header className="bg-white/10 backdrop-blur-xl border-b border-white/20">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Crown className="h-8 w-8 text-yellow-400" />
              <div>
                <h1 className="text-2xl font-bold text-white">업종별 최상위 관리자</h1>
                <p className="text-slate-300">전체 업종 통합 관리 및 모니터링</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                    <Plus className="h-4 w-4 mr-2" />
                    브랜드 + 관리자 생성
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                      <UserPlus className="h-5 w-5" />
                      브랜드 및 브랜드관리자 계정 생성
                    </DialogTitle>
                  </DialogHeader>
                  
                  <div className="space-y-6">
                    {/* 브랜드 정보 섹션 */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
                        브랜드 정보
                      </h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="brand_name">브랜드명 *</Label>
                          <Input
                            id="brand_name"
                            value={formData.brand_name}
                            onChange={(e) => handleInputChange('brand_name', e.target.value)}
                            placeholder="브랜드명을 입력하세요"
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="brand_contact_email">브랜드 이메일</Label>
                          <Input
                            id="brand_contact_email"
                            type="email"
                            value={formData.brand_contact_email}
                            onChange={(e) => handleInputChange('brand_contact_email', e.target.value)}
                            placeholder="브랜드 연락처 이메일"
                          />
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="brand_description">브랜드 설명 *</Label>
                        <Textarea
                          id="brand_description"
                          value={formData.brand_description}
                          onChange={(e) => handleInputChange('brand_description', e.target.value)}
                          placeholder="브랜드에 대한 설명을 입력하세요"
                          rows={3}
                        />
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="brand_contact_phone">브랜드 연락처</Label>
                          <Input
                            id="brand_contact_phone"
                            value={formData.brand_contact_phone}
                            onChange={(e) => handleInputChange('brand_contact_phone', e.target.value)}
                            placeholder="브랜드 연락처 전화번호"
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="brand_address">브랜드 주소</Label>
                          <Input
                            id="brand_address"
                            value={formData.brand_address}
                            onChange={(e) => handleInputChange('brand_address', e.target.value)}
                            placeholder="브랜드 주소"
                          />
                        </div>
                      </div>
                    </div>
                    
                    {/* 브랜드관리자 정보 섹션 */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
                        브랜드관리자 정보
                      </h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="admin_name">관리자 이름 *</Label>
                          <Input
                            id="admin_name"
                            value={formData.admin_name}
                            onChange={(e) => handleInputChange('admin_name', e.target.value)}
                            placeholder="관리자 이름을 입력하세요"
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="admin_email">관리자 이메일 *</Label>
                          <Input
                            id="admin_email"
                            type="email"
                            value={formData.admin_email}
                            onChange={(e) => handleInputChange('admin_email', e.target.value)}
                            placeholder="관리자 이메일을 입력하세요"
                          />
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="admin_phone">관리자 연락처 *</Label>
                        <Input
                          id="admin_phone"
                          value={formData.admin_phone}
                          onChange={(e) => handleInputChange('admin_phone', e.target.value)}
                          placeholder="관리자 전화번호를 입력하세요"
                        />
                      </div>
                    </div>
                    
                    {/* 안내 메시지 */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <div className="flex items-start gap-2">
                        <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                        <div className="text-sm text-blue-800">
                          <p className="font-medium mb-1">생성 완료 후 안내사항:</p>
                          <ul className="list-disc list-inside space-y-1">
                            <li>브랜드관리자 계정이 자동으로 생성됩니다</li>
                            <li>임시 비밀번호가 발급되어 화면에 표시됩니다</li>
                            <li>브랜드관리자는 브랜드 전용 대시보드에 접근할 수 있습니다</li>
                            <li>추후 로그인 기능이 구현되면 정식 로그인이 가능합니다</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex justify-end gap-3 pt-4 border-t">
                    <Button
                      variant="outline"
                      onClick={() => {
                        resetForm();
                        setIsCreateDialogOpen(false);
                      }}
                      disabled={isSubmitting}
                    >
                      <XCircle className="h-4 w-4 mr-2" />
                      취소
                    </Button>
                    <Button
                      onClick={handleSubmit}
                      disabled={isSubmitting}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      {isSubmitting ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          생성 중...
                        </>
                      ) : (
                        <>
                          <CheckCircle className="h-4 w-4 mr-2" />
                          브랜드 + 관리자 생성
                        </>
                      )}
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
              
              <Badge variant="outline" className="text-green-400 border-green-400">
                <Activity className="h-4 w-4 mr-1" />
                실시간 모니터링
              </Badge>
              <div className="text-slate-300 text-sm">
                {new Date().toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">총 업종</CardTitle>
              <Building2 className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.totalIndustries}</div>
              <p className="text-xs text-slate-400">활성 업종 수</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">총 브랜드</CardTitle>
              <Store className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.totalBrands}</div>
              <p className="text-xs text-slate-400">등록된 브랜드</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">총 매장</CardTitle>
              <Users className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.totalStores}</div>
              <p className="text-xs text-slate-400">운영 중인 매장</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">총 매출</CardTitle>
              <TrendingUp className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {(stats.totalRevenue / 1000000).toFixed(0)}M
              </div>
              <p className="text-xs text-slate-400">월 총 매출</p>
            </CardContent>
          </Card>
        </div>

        {/* 업종별 상세 정보 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 업종 목록 */}
          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                업종별 현황
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {industries.map((industry) => (
                  <div
                    key={industry.id}
                    className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">{getIndustryIcon(industry.type)}</div>
                      <div>
                        <h3 className="font-semibold text-white">{industry.name}</h3>
                        <p className="text-sm text-slate-400">
                          {industry.brandsCount}개 브랜드 • {industry.storesCount}개 매장
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-white">
                        {(industry.revenue / 1000000).toFixed(0)}M
                      </div>
                      <Badge className={getStatusColor(industry.status)}>
                        {industry.status === 'active' ? '활성' : 
                         industry.status === 'inactive' ? '비활성' : '점검중'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 성과 지표 */}
          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                성과 지표
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-300">매장 운영률</span>
                    <span className="text-white font-semibold">
                      {((stats.activeStores / stats.totalStores) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <Progress 
                    value={(stats.activeStores / stats.totalStores) * 100} 
                    className="h-2"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-300">성장률</span>
                    <span className="text-green-400 font-semibold">+{stats.growthRate}%</span>
                  </div>
                  <Progress 
                    value={stats.growthRate} 
                    className="h-2 bg-slate-700"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-300">직원당 매출</span>
                    <span className="text-white font-semibold">
                      {Math.round(stats.totalRevenue / stats.totalEmployees).toLocaleString()}원
                    </span>
                  </div>
                  <Progress 
                    value={75} 
                    className="h-2 bg-slate-700"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 빠른 액션 */}
        <div className="mt-8">
          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Settings className="h-5 w-5" />
                빠른 액션
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button className="p-4 rounded-lg bg-blue-500/20 hover:bg-blue-500/30 transition-colors text-white">
                  <Building2 className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">새 업종 추가</span>
                </button>
                <button className="p-4 rounded-lg bg-green-500/20 hover:bg-green-500/30 transition-colors text-white">
                  <Store className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">브랜드 관리</span>
                </button>
                <button className="p-4 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 transition-colors text-white">
                  <Users className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">직원 통계</span>
                </button>
                <button className="p-4 rounded-lg bg-yellow-500/20 hover:bg-yellow-500/30 transition-colors text-white">
                  <Bell className="h-6 w-6 mx-auto mb-2" />
                  <span className="text-sm">알림 설정</span>
                </button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 