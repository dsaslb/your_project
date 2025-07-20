"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Store, 
  Building2, 
  Users, 
  TrendingUp, 
  DollarSign, 
  ShoppingCart,
  ArrowLeft,
  Home,
  BarChart3,
  Calendar,
  Target
} from 'lucide-react';
import Link from 'next/link';

interface Brand {
  id: number;
  name: string;
  today_revenue: number;
  branch_count: number;
  staff_count: number;
  avg_revenue_per_branch: number;
}

interface Branch {
  id: number;
  name: string;
  brand_name: string;
  location: string;
  today_revenue: number;
  staff_count: number;
  today_orders: number;
  avg_order_value: number;
}

export default function BrandManagerPage() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // 브랜드 데이터 로드
      const brandsResponse = await fetch('/api/admin/restaurant/industry/brands');
      const brandsData = await brandsResponse.json();
      setBrands(brandsData);

      // 매장 데이터 로드
      const branchesResponse = await fetch('/api/admin/restaurant/industry/branches');
      const branchesData = await branchesResponse.json();
      setBranches(branchesData);

    } catch (error) {
      console.error('데이터 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  const getBranchesByBrand = (brandId: number) => {
    return branches.filter(branch => 
      branch.brand_name === brands.find(b => b.id === brandId)?.name
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">🏪</div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">브랜드 관리자 대시보드</h1>
                <p className="text-sm text-gray-500">브랜드별 현황 및 매장 관리</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/restaurant/hierarchy">
                <Button variant="outline" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  계층 관리
                </Button>
              </Link>
              <Link href="/">
                <Button variant="outline" size="sm">
                  <Home className="h-4 w-4 mr-2" />
                  홈으로
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* 브레드크럼 */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center space-x-2 py-3">
            <Link href="/" className="text-gray-500 hover:text-gray-700">
              홈
            </Link>
            <ArrowLeft className="h-4 w-4 text-gray-400" />
            <Link href="/restaurant/hierarchy" className="text-gray-500 hover:text-gray-700">
              레스토랑 계층 관리
            </Link>
            <ArrowLeft className="h-4 w-4 text-gray-400" />
            <span className="text-gray-900 font-medium">브랜드 관리</span>
          </div>
        </div>
      </nav>

      {/* 메인 콘텐츠 */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* 브랜드별 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 브랜드 수</CardTitle>
              <Store className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{brands.length}개</div>
              <p className="text-xs text-muted-foreground">
                활성 브랜드
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 매장 수</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{branches.length}개</div>
              <p className="text-xs text-muted-foreground">
                운영 중인 매장
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">오늘 총 매출</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(brands.reduce((sum, brand) => sum + brand.today_revenue, 0))}
              </div>
              <p className="text-xs text-muted-foreground">
                전체 브랜드 합계
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">평균 매장당 매출</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(
                  brands.reduce((sum, brand) => sum + brand.avg_revenue_per_branch, 0) / brands.length
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                브랜드 평균
              </p>
            </CardContent>
          </Card>
        </div>

        {/* 브랜드 목록 */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold">브랜드별 현황</h2>
            <p className="text-sm text-gray-600">각 브랜드의 성과 및 소속 매장 현황</p>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {brands.map((brand) => (
                <Card key={brand.id} className="hover:shadow-lg transition-shadow cursor-pointer"
                      onClick={() => setSelectedBrand(brand)}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="text-lg font-semibold">{brand.name}</span>
                      <Badge variant="secondary">{brand.branch_count}개 매장</Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="flex items-center gap-1">
                        <DollarSign className="h-4 w-4 text-green-600" />
                        <span className="text-gray-600">오늘 매출:</span>
                      </div>
                      <div className="font-semibold">{formatCurrency(brand.today_revenue)}</div>
                      
                      <div className="flex items-center gap-1">
                        <Users className="h-4 w-4 text-blue-600" />
                        <span className="text-gray-600">직원 수:</span>
                      </div>
                      <div className="font-semibold">{brand.staff_count}명</div>
                      
                      <div className="flex items-center gap-1">
                        <TrendingUp className="h-4 w-4 text-purple-600" />
                        <span className="text-gray-600">매장당 평균:</span>
                      </div>
                      <div className="font-semibold">{formatCurrency(brand.avg_revenue_per_branch)}</div>
                    </div>
                    
                    <Button className="w-full" variant="outline">
                      매장 보기
                      <ArrowLeft className="h-4 w-4 ml-2" />
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>

        {/* 선택된 브랜드의 매장들 */}
        {selectedBrand && (
          <div className="bg-white rounded-lg shadow mb-8">
            <div className="px-6 py-4 border-b">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">
                  {selectedBrand.name} - 소속 매장 현황
                </h3>
                <Button variant="ghost" onClick={() => setSelectedBrand(null)}>
                  닫기
                </Button>
              </div>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {getBranchesByBrand(selectedBrand.id).map((branch) => (
                  <Card key={branch.id} className="border-l-4 border-l-blue-500">
                    <CardContent className="pt-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold">{branch.name}</h4>
                        <Badge variant="outline">{branch.brand_name}</Badge>
                      </div>
                      <div className="text-sm text-gray-600 mb-3">{branch.location}</div>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div className="flex items-center gap-1">
                          <DollarSign className="h-4 w-4 text-green-600" />
                          <span>매출: {formatCurrency(branch.today_revenue)}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <ShoppingCart className="h-4 w-4 text-blue-600" />
                          <span>주문: {branch.today_orders}건</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Users className="h-4 w-4 text-purple-600" />
                          <span>직원: {branch.staff_count}명</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <TrendingUp className="h-4 w-4 text-orange-600" />
                          <span>평균: {formatCurrency(branch.avg_order_value)}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 브랜드 성과 분석 */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="px-6 py-4 border-b">
            <h3 className="text-lg font-semibold">브랜드 성과 분석</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    매출 순위
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {brands
                      .sort((a, b) => b.today_revenue - a.today_revenue)
                      .slice(0, 5)
                      .map((brand, index) => (
                        <div key={brand.id} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant={index === 0 ? "default" : "secondary"}>
                              {index + 1}
                            </Badge>
                            <span className="font-medium">{brand.name}</span>
                          </div>
                          <span className="text-sm font-semibold">
                            {formatCurrency(brand.today_revenue)}
                          </span>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Building2 className="h-5 w-5" />
                    매장 수 순위
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {brands
                      .sort((a, b) => b.branch_count - a.branch_count)
                      .slice(0, 5)
                      .map((brand, index) => (
                        <div key={brand.id} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant={index === 0 ? "default" : "secondary"}>
                              {index + 1}
                            </Badge>
                            <span className="font-medium">{brand.name}</span>
                          </div>
                          <span className="text-sm font-semibold">
                            {brand.branch_count}개
                          </span>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    효율성 순위
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {brands
                      .sort((a, b) => b.avg_revenue_per_branch - a.avg_revenue_per_branch)
                      .slice(0, 5)
                      .map((brand, index) => (
                        <div key={brand.id} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant={index === 0 ? "default" : "secondary"}>
                              {index + 1}
                            </Badge>
                            <span className="font-medium">{brand.name}</span>
                          </div>
                          <span className="text-sm font-semibold">
                            {formatCurrency(brand.avg_revenue_per_branch)}
                          </span>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>

        {/* 빠른 액션 */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h3 className="text-lg font-semibold">빠른 액션</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
                <Store className="h-6 w-6 mb-2" />
                <span className="text-sm">새 브랜드 추가</span>
              </Button>
              <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
                <Building2 className="h-6 w-6 mb-2" />
                <span className="text-sm">매장 등록</span>
              </Button>
              <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
                <BarChart3 className="h-6 w-6 mb-2" />
                <span className="text-sm">성과 리포트</span>
              </Button>
              <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
                <Calendar className="h-6 w-6 mb-2" />
                <span className="text-sm">일정 관리</span>
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 