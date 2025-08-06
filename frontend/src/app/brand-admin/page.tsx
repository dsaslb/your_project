"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Store, Users, DollarSign, TrendingUp, Building, Activity } from 'lucide-react';
import { toast } from 'sonner';

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

interface BrandStats {
  totalStores: number;
  totalEmployees: number;
  activeStores: number;
  activeEmployees: number;
  totalRevenue: number;
  growthRate: number;
}

export default function BrandAdminPage() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [stats, setStats] = useState<BrandStats>({
    totalStores: 0,
    totalEmployees: 0,
    activeStores: 0,
    activeEmployees: 0,
    totalRevenue: 0,
    growthRate: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBrandData();
  }, []);

  const fetchBrandData = async () => {
    try {
      setLoading(true);
      
      // 모든 API 호출을 병렬로 실행
      const [brandsRes, branchesRes, employeesRes] = await Promise.all([
        fetch('/api/admin/brands'),
        fetch('/api/admin/branches'),
        fetch('/api/admin/employees')
      ]);

      let brandsList: Brand[] = [];
      let branchesList: Branch[] = [];
      let employeesList: Employee[] = [];

      // 브랜드 데이터
      if (brandsRes.ok) {
        const brandsData = await brandsRes.json();
        brandsList = brandsData.data || brandsData.brands || [];
        setBrands(brandsList);
      }

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

      // 통계 계산
      const activeStores = branchesList.filter(branch => branch.status === 'active').length;
      const activeEmployees = employeesList.filter(emp => emp.status === 'active').length;
      
      // 샘플 매출 데이터 (실제로는 API에서 가져와야 함)
      const totalRevenue = branchesList.length * 2500000; // 매장당 평균 250만원
      const growthRate = 12.5; // 샘플 성장률

      setStats({
        totalStores: branchesList.length,
        totalEmployees: employeesList.length,
        activeStores,
        activeEmployees,
        totalRevenue,
        growthRate
      });

    } catch (error) {
      console.error('브랜드 데이터 로딩 오류:', error);
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

  // 매장별 직원 수 계산
  const getEmployeeCount = (branchId: number) => {
    return employees.filter(emp => emp.branch_id === branchId).length;
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-lg mb-2">로딩 중...</div>
            <div className="text-sm text-gray-500">브랜드 데이터를 가져오는 중입니다</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">브랜드 관리자</h1>
        <p className="text-gray-600">브랜드별 매장 및 직원 관리</p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 매장</CardTitle>
            <Store className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalStores}개</div>
            <p className="text-xs text-muted-foreground">운영 중: {stats.activeStores}개</p>
          </CardContent>
        </Card>

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
            <CardTitle className="text-sm font-medium">총 브랜드</CardTitle>
            <Building className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{brands.length}개</div>
            <p className="text-xs text-muted-foreground">활성 브랜드</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">성장률</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">+{stats.growthRate}%</div>
            <p className="text-xs text-muted-foreground">전월 대비</p>
          </CardContent>
        </Card>
      </div>

      {/* 브랜드별 현황 */}
      <Card className="border border-gray-100 mb-8">
        <CardHeader>
          <CardTitle>브랜드별 현황</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {brands.slice(0, 6).map((brand) => {
              const brandBranches = branches.filter(branch => branch.brand_id === brand.id);
              const brandEmployees = employees.filter(emp => 
                brandBranches.some(branch => branch.id === emp.branch_id)
              );
              const activeBranches = brandBranches.filter(branch => branch.status === 'active');
              const activeEmployees = brandEmployees.filter(emp => emp.status === 'active');
              
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
                    <p>매장: {brandBranches.length}개 (활성: {activeBranches.length}개)</p>
                    <p>직원: {brandEmployees.length}명 (활성: {activeEmployees.length}명)</p>
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

      {/* 매장 목록 */}
      <Card className="border border-gray-100">
        <CardHeader>
          <CardTitle>매장 현황</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {branches.slice(0, 9).map((branch) => {
              const employeeCount = getEmployeeCount(branch.id);
              const activeEmployees = employees.filter(emp => 
                emp.branch_id === branch.id && emp.status === 'active'
              ).length;
              
              return (
                <div key={branch.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{branch.name}</h4>
                    <span className={`text-xs px-2 py-1 rounded ${
                      branch.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {branch.status === 'active' ? '활성' : '비활성'}
                    </span>
                  </div>
                  <div className="space-y-1 text-sm text-gray-600">
                    <p>브랜드: {getBrandName(branch.brand_id)}</p>
                    <p>직원: {employeeCount}명 (활성: {activeEmployees}명)</p>
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
    </div>
  );
} 