'use client';
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, RefreshCw, Plus, Building2, Store, Users, DollarSign, TrendingUp, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { toast } from 'sonner';
import BrandCard from './components/BrandCard';
import BrandDetailModal from './components/BrandDetailModal';
import IndustryModal from './components/IndustryModal';

interface Brand {
  id: number;
  name: string;
  code: string;
  description: string;
  status: 'active' | 'inactive' | 'pending';
  store_count: number;
  employee_count: number;
  total_revenue: number;
  improvement_requests: number;
  ai_diagnoses: number;
  pending_approvals: number;
  last_activity: string;
  industry_id?: number;
}

interface Industry {
  id: number;
  name: string;
  code: string;
  description: string;
  icon: string;
  color: string;
  brand_count: number;
  store_count: number;
  employee_count: number;
  total_revenue: number;
  status: 'active' | 'inactive';
  last_activity: string;
}

export default function Dashboard() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null);
  const [selectedIndustry, setSelectedIndustry] = useState<Industry | null>(null);
  const [industryModal, setIndustryModal] = useState<{
    isOpen: boolean;
    mode: 'create' | 'edit';
    industry?: Industry | null;
  }>({
    isOpen: false,
    mode: 'create',
    industry: null
  });
  const [viewMode, setViewMode] = useState<'brands' | 'industries'>('brands');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(false);

  // 브랜드 데이터 로드
  const loadBrands = async () => {
    try {
      const response = await fetch('http://192.168.45.44:5000/api/admin/brands');
      if (response.ok) {
        const data = await response.json();
        setBrands(data.brands || []);
      } else {
        console.error('브랜드 로드 실패');
      }
    } catch (error) {
      console.error('브랜드 로드 오류:', error);
    }
  };

  // 업종 데이터 로드
  const loadIndustries = async () => {
    try {
      const response = await fetch('http://192.168.45.44:5000/api/admin/industries');
      if (response.ok) {
        const data = await response.json();
        setIndustries(data.industries || []);
      } else {
        console.error('업종 로드 실패:', response.status, response.statusText);
        // 오류가 발생해도 빈 배열로 설정하여 기본 업종 초기화가 작동하도록 함
        setIndustries([]);
      }
    } catch (error) {
      console.error('업종 로드 오류:', error);
      // 네트워크 오류 등이 발생해도 빈 배열로 설정
      setIndustries([]);
    }
  };

  // 업종 저장 (생성/수정)
  const handleIndustrySave = async (industry: any) => {
    try {
      const url = industry.id 
        ? `http://192.168.45.44:5000/api/admin/industries/${industry.id}`
        : 'http://192.168.45.44:5000/api/admin/industries';
      
      const method = industry.id ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(industry),
      });

      if (response.ok) {
        await loadIndustries();
        return true;
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || '저장 실패');
      }
    } catch (error) {
      console.error('업종 저장 오류:', error);
      throw error;
    }
  };

  // 업종 삭제
  const handleIndustryDelete = async (id: number) => {
    try {
      const response = await fetch(`http://192.168.45.44:5000/api/admin/industries/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        await loadIndustries();
        return true;
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || '삭제 실패');
      }
    } catch (error) {
      console.error('업종 삭제 오류:', error);
      throw error;
    }
  };

  // 기본 업종들 초기화
  const initializeDefaultIndustries = async () => {
    try {
      // 이미 업종이 있으면 초기화하지 않음
      if (industries.length > 0) {
        return;
      }
      
      const defaultIndustries = [
        {
          name: '꽃집',
          code: 'FLOWER_SHOP',
          description: '꽃집 및 화원 관련 업종',
          icon: '💐',
          color: '#FF6B9D',
          status: 'active' as const
        },
        {
          name: '병원',
          code: 'HOSPITAL',
          description: '병원 및 의료기관 관련 업종',
          icon: '🏥',
          color: '#4F46E5',
          status: 'active' as const
        },
        {
          name: '미용실',
          code: 'BEAUTY_SALON',
          description: '미용실 및 헤어샵 관련 업종',
          icon: '✂️',
          color: '#EC4899',
          status: 'active' as const
        },
        {
          name: '음식점',
          code: 'RESTAURANT',
          description: '음식점 및 식당 관련 업종',
          icon: '🍽️',
          color: '#F59E0B',
          status: 'active' as const
        },
        {
          name: '카페',
          code: 'CAFE',
          description: '카페 및 커피숍 관련 업종',
          icon: '☕',
          color: '#8B5CF6',
          status: 'active' as const
        },
        {
          name: '약국',
          code: 'PHARMACY',
          description: '약국 및 의약품 관련 업종',
          icon: '💊',
          color: '#10B981',
          status: 'active' as const
        },
        {
          name: '의류',
          code: 'CLOTHING',
          description: '의류 및 패션 관련 업종',
          icon: '👕',
          color: '#EF4444',
          status: 'active' as const
        },
        {
          name: '편의점',
          code: 'CONVENIENCE_STORE',
          description: '편의점 및 소매점 관련 업종',
          icon: '🛒',
          color: '#F59E0B',
          status: 'active' as const
        },
        {
          name: '은행',
          code: 'BANK',
          description: '은행 및 금융기관 관련 업종',
          icon: '🏦',
          color: '#10B981',
          status: 'active' as const
        },
        {
          name: '학교',
          code: 'SCHOOL',
          description: '학교 및 교육기관 관련 업종',
          icon: '🎓',
          color: '#3B82F6',
          status: 'active' as const
        },
        {
          name: '자동차',
          code: 'AUTOMOTIVE',
          description: '자동차 및 정비 관련 업종',
          icon: '🚗',
          color: '#6B7280',
          status: 'active' as const
        },
        {
          name: '부동산',
          code: 'REAL_ESTATE',
          description: '부동산 및 중개 관련 업종',
          icon: '🏠',
          color: '#F59E0B',
          status: 'active' as const
        },
        {
          name: 'IT',
          code: 'IT',
          description: 'IT 및 소프트웨어 관련 업종',
          icon: '💻',
          color: '#3B82F6',
          status: 'active' as const
        },
        {
          name: '예술',
          code: 'ART',
          description: '예술 및 문화 관련 업종',
          icon: '🎨',
          color: '#EC4899',
          status: 'active' as const
        },
        {
          name: '스포츠',
          code: 'SPORTS',
          description: '스포츠 및 레저 관련 업종',
          icon: '⚽',
          color: '#10B981',
          status: 'active' as const
        }
      ];

      for (const industry of defaultIndustries) {
        try {
          await handleIndustrySave(industry);
        } catch (error) {
          console.log('기본 업종 추가 중 오류:', error);
        }
      }
      toast.success('기본 업종들이 추가되었습니다!');
    } catch (error) {
      console.error('기본 업종 초기화 오류:', error);
    }
  };

  // 브랜드 상세 정보 로드
  const loadBrandDetail = async (brandId: number) => {
    try {
      const response = await fetch(`http://192.168.45.44:5000/api/admin/brand/${brandId}/details`);
      if (response.ok) {
        const data = await response.json();
        setSelectedBrand(data.brand);
      }
    } catch (error) {
      console.error('브랜드 상세 정보 로드 오류:', error);
    }
  };

  // 업종 상세 정보 로드
  const loadIndustryDetail = async (industryId: number) => {
    try {
      const response = await fetch(`http://192.168.45.44:5000/api/admin/industries/${industryId}/detail`);
      if (response.ok) {
        const data = await response.json();
        setSelectedIndustry(data.industry);
      }
    } catch (error) {
      console.error('업종 상세 정보 로드 오류:', error);
    }
  };

  // 필터링된 데이터
  const filteredBrands = brands.filter(brand => {
    const matchesSearch = brand.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         brand.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || brand.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const filteredIndustries = industries.filter(industry => {
    const matchesSearch = industry.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         industry.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || industry.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // 전체 통계
  const totalStats = {
    brands: brands.length,
    industries: industries.length,
    totalStores: brands.reduce((sum, brand) => sum + brand.store_count, 0),
    totalEmployees: brands.reduce((sum, brand) => sum + brand.employee_count, 0),
    totalRevenue: brands.reduce((sum, brand) => sum + brand.total_revenue, 0),
    pendingApprovals: brands.reduce((sum, brand) => sum + brand.pending_approvals, 0)
  };

  useEffect(() => {
    loadBrands();
    loadIndustries();
  }, []);

  // 업종 로드 후 기본 업종 초기화
  useEffect(() => {
    if (industries.length === 0) {
      // 약간의 지연 후 초기화 (업종 로드 완료 후)
      const timer = setTimeout(() => {
        initializeDefaultIndustries();
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [industries.length]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">활성</Badge>;
      case 'inactive':
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100">비활성</Badge>;
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">대기</Badge>;
      default:
        return <Badge variant="secondary">알 수 없음</Badge>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* 헤더 */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">통합 대시보드</h1>
            <p className="text-gray-600 dark:text-gray-400">브랜드 및 업종 현황을 한눈에 확인하세요</p>
          </div>
          <div className="flex items-center gap-3">
            <Button 
              variant={viewMode === 'brands' ? 'default' : 'outline'} 
              onClick={() => setViewMode('brands')}
            >
              브랜드 관리
            </Button>
            <Button 
              variant={viewMode === 'industries' ? 'default' : 'outline'} 
              onClick={() => setViewMode('industries')}
            >
              업종 관리
            </Button>
            <Button 
              variant="outline" 
              onClick={() => viewMode === 'brands' ? loadBrands() : loadIndustries()}
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              새로고침
            </Button>
          </div>
        </div>

        {/* 전체 통계 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">
                {viewMode === 'brands' ? '총 브랜드' : '총 업종'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center">
                <Building2 className="w-5 h-5 text-blue-500 mr-2" />
                <span className="text-2xl font-bold">
                  {viewMode === 'brands' ? totalStats.brands : totalStats.industries}
                </span>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">총 매장</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center">
                <Store className="w-5 h-5 text-green-500 mr-2" />
                <span className="text-2xl font-bold">{totalStats.totalStores}개</span>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">총 직원</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center">
                <Users className="w-5 h-5 text-purple-500 mr-2" />
                <span className="text-2xl font-bold">{totalStats.totalEmployees}명</span>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">총 매출</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center">
                <DollarSign className="w-5 h-5 text-yellow-500 mr-2" />
                <span className="text-2xl font-bold">{totalStats.totalRevenue.toLocaleString()}원</span>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">승인 대기</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center">
                <Clock className="w-5 h-5 text-orange-500 mr-2" />
                <span className="text-2xl font-bold">{totalStats.pendingApprovals}건</span>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">성장률</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center">
                <TrendingUp className="w-5 h-5 text-green-500 mr-2" />
                <span className="text-2xl font-bold text-green-600">+12%</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 검색 및 필터 */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder={viewMode === 'brands' ? '브랜드명 또는 코드로 검색...' : '업종명 또는 코드로 검색...'}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="상태 필터" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체</SelectItem>
                <SelectItem value="active">활성</SelectItem>
                <SelectItem value="inactive">비활성</SelectItem>
                {viewMode === 'brands' && <SelectItem value="pending">대기</SelectItem>}
              </SelectContent>
            </Select>
            {viewMode === 'industries' && (
              <Button onClick={() => setIndustryModal({ isOpen: true, mode: 'create', industry: null })}>
                <Plus className="w-4 h-4 mr-2" />
                업종 추가
              </Button>
            )}
          </div>
        </div>

        {/* 목록 */}
        {viewMode === 'brands' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredBrands.map((brand) => (
              <BrandCard
                key={brand.id}
                brand={brand}
                onClick={() => loadBrandDetail(brand.id)}
              />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredIndustries.map((industry) => (
              <Card 
                key={industry.id} 
                className="cursor-pointer hover:shadow-lg transition-shadow duration-200 relative"
                onClick={() => loadIndustryDetail(industry.id)}
              >
                <div className="absolute top-2 right-2 z-10">
                  <Button 
                    size="sm" 
                    variant="outline" 
                    onClick={(e) => { 
                      e.stopPropagation(); 
                      setIndustryModal({ isOpen: true, mode: 'edit', industry: industry }); 
                    }}
                  >
                    편집
                  </Button>
                </div>
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div 
                      className="w-12 h-12 rounded-lg flex items-center justify-center text-2xl"
                      style={{ backgroundColor: industry.color + '20' }}
                    >
                      {industry.icon}
                    </div>
                    <div>
                      <CardTitle>{industry.name}</CardTitle>
                      <CardDescription>{industry.code}</CardDescription>
                    </div>
                  </div>
                  {getStatusBadge(industry.status)}
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="flex items-center">
                      <Building2 className="w-4 h-4 text-blue-500 mr-2" />
                      <span>{industry.brand_count}개</span>
                    </div>
                    <div className="flex items-center">
                      <Store className="w-4 h-4 text-green-500 mr-2" />
                      <span>{industry.store_count}개</span>
                    </div>
                    <div className="flex items-center">
                      <Users className="w-4 h-4 text-purple-500 mr-2" />
                      <span>{industry.employee_count}명</span>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 pt-2 border-t">
                    마지막 활동: {new Date(industry.last_activity).toLocaleDateString()}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* 결과 없음 */}
        {((viewMode === 'brands' && filteredBrands.length === 0) || 
          (viewMode === 'industries' && filteredIndustries.length === 0)) && (
          <div className="text-center py-12">
            <div className="text-gray-500 dark:text-gray-400">
              {searchTerm || statusFilter !== 'all' ? '검색 결과가 없습니다.' : `${viewMode === 'brands' ? '브랜드' : '업종'}가 없습니다.`}
            </div>
          </div>
        )}
      </div>

      {/* 브랜드 상세 모달 */}
      <BrandDetailModal
        brand={selectedBrand}
        isOpen={!!selectedBrand}
        onClose={() => setSelectedBrand(null)}
      />

      {/* 업종 상세 모달 */}
      {selectedIndustry && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-slate-800 rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div 
                    className="w-12 h-12 rounded-lg flex items-center justify-center text-2xl"
                    style={{ backgroundColor: selectedIndustry.color + '20' }}
                  >
                    {selectedIndustry.icon}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold">{selectedIndustry.name}</h2>
                    <p className="text-gray-500">{selectedIndustry.code}</p>
                  </div>
                </div>
                <Button variant="outline" size="sm" onClick={() => setSelectedIndustry(null)}>
                  닫기
                </Button>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-blue-600">{selectedIndustry.brand_count}</div>
                    <div className="text-sm text-gray-500">브랜드</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-green-600">{selectedIndustry.store_count}</div>
                    <div className="text-sm text-gray-500">매장</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-purple-600">{selectedIndustry.employee_count}</div>
                    <div className="text-sm text-gray-500">직원</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-yellow-600">{selectedIndustry.total_revenue.toLocaleString()}</div>
                    <div className="text-sm text-gray-500">매출</div>
                  </CardContent>
                </Card>
              </div>

              {selectedIndustry.description && (
                <Card className="mb-6">
                  <CardHeader>
                    <CardTitle>설명</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p>{selectedIndustry.description}</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 업종 관리 모달 */}
      <IndustryModal
        industry={industryModal.industry}
        isOpen={industryModal.isOpen}
        onClose={() => setIndustryModal({ isOpen: false, mode: 'create', industry: null })}
        onSave={handleIndustrySave}
        onDelete={handleIndustryDelete}
        mode={industryModal.mode}
      />
    </div>
  );
} 