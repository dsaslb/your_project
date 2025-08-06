"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Building2, Store, Users, DollarSign, TrendingUp, Calendar } from 'lucide-react';
import { toast } from 'sonner';

interface Industry {
  id: number;
  name: string;
  description?: string;
  status: string;
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

interface IndustryStats {
  totalIndustries: number;
  totalBrands: number;
  totalBranches: number;
  totalEmployees: number;
  activeIndustries: number;
  activeBrands: number;
  activeBranches: number;
  activeEmployees: number;
  totalRevenue: number;
  growthRate: number;
}

export default function IndustryAdminPage() {
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [stats, setStats] = useState<IndustryStats>({
    totalIndustries: 0,
    totalBrands: 0,
    totalBranches: 0,
    totalEmployees: 0,
    activeIndustries: 0,
    activeBrands: 0,
    activeBranches: 0,
    activeEmployees: 0,
    totalRevenue: 0,
    growthRate: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchIndustryData();
  }, []);

  const fetchIndustryData = async () => {
    try {
      setLoading(true);
      
      // 모든 API 호출을 병렬로 실행
      const [industriesRes, brandsRes, branchesRes, employeesRes] = await Promise.all([
        fetch('/api/admin/industries'),
        fetch('/api/admin/brands'),
        fetch('/api/admin/branches'),
        fetch('/api/admin/employees')
      ]);

      let industriesList: Industry[] = [];
      let brandsList: Brand[] = [];
      let branchesList: Branch[] = [];
      let employeesList: Employee[] = [];

      // 업종 데이터
      if (industriesRes.ok) {
        const industriesData = await industriesRes.json();
        industriesList = industriesData.data || industriesData.industries || [];
        setIndustries(industriesList);
      } else {
        console.error('업종 데이터 로딩 실패:', industriesRes.status);
      }

      // 브랜드 데이터
      if (brandsRes.ok) {
        const brandsData = await brandsRes.json();
        brandsList = brandsData.data || brandsData.brands || [];
        setBrands(brandsList);
      } else {
        console.error('브랜드 데이터 로딩 실패:', brandsRes.status);
      }

      // 매장 데이터
      if (branchesRes.ok) {
        const branchesData = await branchesRes.json();
        branchesList = branchesData.data || branchesData.branches || [];
        setBranches(branchesList);
      } else {
        console.error('매장 데이터 로딩 실패:', branchesRes.status);
      }

      // 직원 데이터
      if (employeesRes.ok) {
        const employeesData = await employeesRes.json();
        employeesList = employeesData.data || employeesData.employees || [];
        setEmployees(employeesList);
      } else {
        console.error('직원 데이터 로딩 실패:', employeesRes.status);
      }

      // 통계 계산
      const activeIndustries = industriesList.filter(ind => ind.status === 'active').length;
      const activeBrands = brandsList.filter(brand => brand.status === 'active').length;
      const activeBranches = branchesList.filter(branch => branch.status === 'active').length;
      const activeEmployees = employeesList.filter(emp => emp.status === 'active').length;
      
      // 샘플 매출 데이터 (실제로는 API에서 가져와야 함)
      const totalRevenue = branchesList.length * 2500000; // 매장당 평균 250만원
      const growthRate = 12.5; // 샘플 성장률

      setStats({
        totalIndustries: industriesList.length,
        totalBrands: brandsList.length,
        totalBranches: branchesList.length,
        totalEmployees: employeesList.length,
        activeIndustries,
        activeBrands,
        activeBranches,
        activeEmployees,
        totalRevenue,
        growthRate
      });

    } catch (error) {
      console.error('업종 데이터 로딩 오류:', error);
      toast.error('데이터를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 브랜드 ID로 브랜드 정보 찾기
  const getBrandName = (brandId: number) => {
    const brand = brands.find(b => b.id === brandId);
    return brand?.name || '알 수 없음';
  };

  // 업종 ID로 업종 정보 찾기
  const getIndustryName = (industryId: number) => {
    const industry = industries.find(i => i.id === industryId);
    return industry?.name || '알 수 없음';
  };

  // 브랜드별 매장 수 계산
  const getBranchCount = (brandId: number) => {
    return branches.filter(branch => branch.brand_id === brandId).length;
  };

  // 브랜드별 직원 수 계산
  const getEmployeeCount = (brandId: number) => {
    const brandBranches = branches.filter(branch => branch.brand_id === brandId);
    const branchIds = brandBranches.map(branch => branch.id);
    return employees.filter(emp => emp.branch_id && branchIds.includes(emp.branch_id)).length;
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-lg mb-2">로딩 중...</div>
            <div className="text-sm text-gray-500">업종 데이터를 가져오는 중입니다</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">업종 관리자</h1>
        <p className="text-gray-600">레스토랑 업종 전체 관리</p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 업종</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalIndustries}개</div>
            <p className="text-xs text-muted-foreground">활성: {stats.activeIndustries}개</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 브랜드</CardTitle>
            <Store className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalBrands}개</div>
            <p className="text-xs text-muted-foreground">활성: {stats.activeBrands}개</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 매장</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalBranches}개</div>
            <p className="text-xs text-muted-foreground">활성: {stats.activeBranches}개</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 직원</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalEmployees}명</div>
            <p className="text-xs text-muted-foreground">활성: {stats.activeEmployees}명</p>
          </CardContent>
        </Card>
      </div>

      {/* 추가 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 매출</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₩{stats.totalRevenue.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">업종 전체 매출</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">성장률</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">+{stats.growthRate}%</div>
            <p className="text-xs text-muted-foreground">전월 대비</p>
          </CardContent>
        </Card>
      </div>

      {/* 업종별 현황 */}
      <Card className="border border-gray-100 mb-8">
        <CardHeader>
          <CardTitle>업종별 현황</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {industries.map((industry) => {
              const industryBrands = brands.filter(brand => brand.industry_id === industry.id);
              const industryBranches = branches.filter(branch => 
                industryBrands.some(brand => brand.id === branch.brand_id)
              );
              const industryEmployees = employees.filter(emp => 
                emp.branch_id && industryBranches.some(branch => branch.id === emp.branch_id)
              );
              
              return (
                <div key={industry.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-lg">{industry.name}</h4>
                    <span className={`text-xs px-2 py-1 rounded ${
                      industry.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {industry.status === 'active' ? '활성' : '비활성'}
                    </span>
                  </div>
                  <div className="space-y-2 text-sm text-gray-600">
                    <p>브랜드: {industryBrands.length}개</p>
                    <p>매장: {industryBranches.length}개</p>
                    <p>직원: {industryEmployees.length}명</p>
                    {industry.description && (
                      <p className="text-xs text-gray-500">{industry.description}</p>
                    )}
                  </div>
                </div>
              );
            })}
            {industries.length === 0 && (
              <div className="col-span-full text-center py-8 text-gray-500">
                등록된 업종이 없습니다.
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 브랜드 목록 */}
      <Card className="border border-gray-100">
        <CardHeader>
          <CardTitle>브랜드 현황</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {brands.slice(0, 9).map((brand) => {
              const branchCount = getBranchCount(brand.id);
              const employeeCount = getEmployeeCount(brand.id);
              
              return (
                <div key={brand.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-lg">{brand.name}</h4>
                    <span className={`text-xs px-2 py-1 rounded ${
                      brand.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {brand.status === 'active' ? '활성' : '비활성'}
                    </span>
                  </div>
                  <div className="space-y-2 text-sm text-gray-600">
                    <p>업종: {getIndustryName(brand.industry_id)}</p>
                    <p>매장: {branchCount}개</p>
                    <p>직원: {employeeCount}명</p>
                    {brand.description && (
                      <p className="text-xs text-gray-500">{brand.description}</p>
                    )}
                  </div>
                </div>
              );
            })}
            {brands.length === 0 && (
              <div className="col-span-full text-center py-8 text-gray-500">
                등록된 브랜드가 없습니다.
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 