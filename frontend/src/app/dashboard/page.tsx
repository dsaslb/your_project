"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, ShoppingCart, DollarSign, Activity, TrendingUp, Zap, Target, Award, Building, Store, UserCheck, Briefcase } from 'lucide-react';
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

interface DashboardStats {
  totalIndustries: number;
  totalBrands: number;
  totalBranches: number;
  totalEmployees: number;
  activeIndustries: number;
  activeBrands: number;
  activeBranches: number;
  activeEmployees: number;
}

export default function DashboardPage() {
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    totalIndustries: 0,
    totalBrands: 0,
    totalBranches: 0,
    totalEmployees: 0,
    activeIndustries: 0,
    activeBrands: 0,
    activeBranches: 0,
    activeEmployees: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
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
      }

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

      // 통계 계산 (로컬 변수 사용)
      const activeIndustries = industriesList.filter(ind => ind.status === 'active').length;
      const activeBrands = brandsList.filter(brand => brand.status === 'active').length;
      const activeBranches = branchesList.filter(branch => branch.status === 'active').length;
      const activeEmployees = employeesList.filter(emp => emp.status === 'active').length;

      setStats({
        totalIndustries: industriesList.length,
        totalBrands: brandsList.length,
        totalBranches: branchesList.length,
        totalEmployees: employeesList.length,
        activeIndustries,
        activeBrands,
        activeBranches,
        activeEmployees
      });

    } catch (error) {
      console.error('대시보드 데이터 로딩 오류:', error);
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-2xl text-cyan-400 mb-2">로딩 중...</div>
            <div className="text-slate-300">대시보드 데이터를 불러오는 중입니다</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-cyan-400 to-purple-600 rounded-xl flex items-center justify-center">
            <Zap className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
              퀀텀 대시보드
            </h1>
            <p className="text-slate-300">실시간 시스템 현황 및 통계</p>
          </div>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-gradient-to-br from-cyan-500/10 to-cyan-600/10 border-cyan-500/20 backdrop-blur-xl hover:from-cyan-500/20 hover:to-cyan-600/20 transition-all duration-300 group">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-cyan-300">총 직원</CardTitle>
            <div className="p-2 bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-lg group-hover:scale-110 transition-transform duration-300">
              <Users className="h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-cyan-400">{stats.totalEmployees}</div>
            <div className="flex items-center gap-2 mt-2">
              <TrendingUp className="h-4 w-4 text-green-400" />
              <p className="text-xs text-cyan-300">활성: {stats.activeEmployees}명</p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-emerald-500/10 to-emerald-600/10 border-emerald-500/20 backdrop-blur-xl hover:from-emerald-500/20 hover:to-emerald-600/20 transition-all duration-300 group">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-emerald-300">총 매장</CardTitle>
            <div className="p-2 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg group-hover:scale-110 transition-transform duration-300">
              <Store className="h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-emerald-400">{stats.totalBranches}</div>
            <div className="flex items-center gap-2 mt-2">
              <TrendingUp className="h-4 w-4 text-green-400" />
              <p className="text-xs text-emerald-300">활성: {stats.activeBranches}개</p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-amber-500/10 to-amber-600/10 border-amber-500/20 backdrop-blur-xl hover:from-amber-500/20 hover:to-amber-600/20 transition-all duration-300 group">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-amber-300">총 브랜드</CardTitle>
            <div className="p-2 bg-gradient-to-br from-amber-500 to-amber-600 rounded-lg group-hover:scale-110 transition-transform duration-300">
              <Building className="h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-amber-400">{stats.totalBrands}</div>
            <div className="flex items-center gap-2 mt-2">
              <TrendingUp className="h-4 w-4 text-green-400" />
              <p className="text-xs text-amber-300">활성: {stats.activeBrands}개</p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-rose-500/10 to-rose-600/10 border-rose-500/20 backdrop-blur-xl hover:from-rose-500/20 hover:to-rose-600/20 transition-all duration-300 group">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-rose-300">총 업종</CardTitle>
            <div className="p-2 bg-gradient-to-br from-rose-500 to-rose-600 rounded-lg group-hover:scale-110 transition-transform duration-300">
              <Briefcase className="h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-rose-400">{stats.totalIndustries}</div>
            <div className="flex items-center gap-2 mt-2">
              <TrendingUp className="h-4 w-4 text-green-400" />
              <p className="text-xs text-rose-300">활성: {stats.activeIndustries}개</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 상세 정보 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-gradient-to-br from-purple-500/10 to-purple-600/10 border-purple-500/20 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-purple-300 flex items-center gap-2">
              <Target className="h-5 w-5" />
              최근 등록된 직원
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {employees.slice(0, 5).map((employee) => (
                <div key={employee.id} className="flex items-center space-x-4 p-3 bg-gradient-to-r from-green-500/10 to-green-600/10 rounded-lg border border-green-500/20">
                  <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-green-300">
                      {employee.name || employee.username}
                    </p>
                    <p className="text-xs text-green-400">
                      {employee.position && `${employee.position}`}
                      {employee.department && ` • ${employee.department}`}
                      {employee.role && ` • ${employee.role}`}
                    </p>
                  </div>
                  <div className="text-xs text-green-400">
                    {new Date(employee.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
              {employees.length === 0 && (
                <div className="text-center py-4 text-slate-400">
                  등록된 직원이 없습니다.
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-indigo-500/10 to-indigo-600/10 border-indigo-500/20 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-indigo-300 flex items-center gap-2">
              <Award className="h-5 w-5" />
              브랜드별 매장 현황
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {brands.slice(0, 5).map((brand) => {
                const brandBranches = branches.filter(branch => branch.brand_id === brand.id);
                const activeBranches = brandBranches.filter(branch => branch.status === 'active');
                return (
                  <div key={brand.id} className="flex justify-between items-center p-3 bg-gradient-to-r from-blue-500/10 to-blue-600/10 rounded-lg border border-blue-500/20">
                    <div>
                      <span className="text-sm text-blue-300 font-medium">{brand.name}</span>
                      <p className="text-xs text-blue-400">
                        {getIndustryName(brand.industry_id)}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="text-sm text-blue-400 font-medium">
                        {brandBranches.length}개
                      </span>
                      <p className="text-xs text-blue-400">
                        활성: {activeBranches.length}개
                      </p>
                    </div>
                  </div>
                );
              })}
              {brands.length === 0 && (
                <div className="text-center py-4 text-slate-400">
                  등록된 브랜드가 없습니다.
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 추가 상세 정보 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <Card className="bg-gradient-to-br from-teal-500/10 to-teal-600/10 border-teal-500/20 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-teal-300 flex items-center gap-2">
              <Building className="h-5 w-5" />
              업종별 브랜드 현황
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {industries.slice(0, 5).map((industry) => {
                const industryBrands = brands.filter(brand => brand.industry_id === industry.id);
                const activeBrands = industryBrands.filter(brand => brand.status === 'active');
                return (
                  <div key={industry.id} className="flex justify-between items-center p-3 bg-gradient-to-r from-teal-500/10 to-teal-600/10 rounded-lg border border-teal-500/20">
                    <div>
                      <span className="text-sm text-teal-300 font-medium">{industry.name}</span>
                      <p className="text-xs text-teal-400">
                        {industry.description || '설명 없음'}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="text-sm text-teal-400 font-medium">
                        {industryBrands.length}개
                      </span>
                      <p className="text-xs text-teal-400">
                        활성: {activeBrands.length}개
                      </p>
                    </div>
                  </div>
                );
              })}
              {industries.length === 0 && (
                <div className="text-center py-4 text-slate-400">
                  등록된 업종이 없습니다.
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-500/10 to-orange-600/10 border-orange-500/20 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-orange-300 flex items-center gap-2">
              <Store className="h-5 w-5" />
              최근 등록된 매장
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {branches.slice(0, 5).map((branch) => (
                <div key={branch.id} className="flex items-center space-x-4 p-3 bg-gradient-to-r from-orange-500/10 to-orange-600/10 rounded-lg border border-orange-500/20">
                  <div className="w-3 h-3 bg-orange-400 rounded-full animate-pulse"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-orange-300">{branch.name}</p>
                    <p className="text-xs text-orange-400">
                      {getBrandName(branch.brand_id)} • {branch.address}
                    </p>
                  </div>
                  <div className="text-xs text-orange-400">
                    {new Date(branch.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
              {branches.length === 0 && (
                <div className="text-center py-4 text-slate-400">
                  등록된 매장이 없습니다.
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 