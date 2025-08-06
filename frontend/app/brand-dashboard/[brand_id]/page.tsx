// 동적 라우트: /brand-dashboard/[brand_id]/page.tsx
'use client';

import { useRouter, useParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useBrands, useStores, useEmployees } from '@/hooks/useDashboard';
import { toast } from 'sonner';
import { Building2, Users, TrendingUp, ArrowLeft, RefreshCw } from 'lucide-react';

// 브랜드별 하위 데이터 타입 예시
type Store = { id: string; name: string };
type Employee = { id: string; name: string };
type Sale = { id: string; amount: number };
type Improvement = { id: string; title: string };

export default function BrandDashboardPage() {
  // URL에서 brand_id 추출
  const params = useParams();
  const brandId = params?.brand_id as string;
  const router = useRouter();
  
  // 새로운 통합 Hook 사용
  const { brands, loading: brandLoading, error: brandError, refetch: refreshBrand } = useBrands();
  const { stores, loading: storesLoading, refetch: refreshStores } = useStores(1, 50, '', '', brandId ? parseInt(brandId) : undefined);
  const { employees, loading: employeesLoading, refetch: refreshEmployees } = useEmployees(1, 50, '', '', undefined, brandId ? parseInt(brandId) : undefined);
  
  // 현재 브랜드 정보 찾기
  const brandDetail = brands.find(brand => brand.id === parseInt(brandId));
  
  // 기존 sales, improvements는 임시로 빈 배열 (추후 API 추가 필요)
  const [sales, setSales] = useState<Sale[]>([]);
  const [improvements, setImprovements] = useState<Improvement[]>([]);
  
  // 전체 로딩 상태
  const loading = brandLoading || storesLoading || employeesLoading;
  
  // 데이터 새로고침 함수
  const handleRefresh = async () => {
    try {
      await Promise.all([
        refreshBrand(),
        refreshStores(),
        refreshEmployees()
      ]);
      toast.success('브랜드 데이터가 성공적으로 새로고침되었습니다');
    } catch (error) {
      toast.error('데이터 새로고침에 실패했습니다');
      console.error('브랜드 대시보드 새로고침 오류:', error);
    }
  };

  return (
    <div className="min-h-screen p-8 bg-gradient-to-br from-white to-blue-50 dark:from-slate-900 dark:to-slate-800">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">
            {brandDetail?.name || `브랜드 대시보드 (ID: ${brandId})`}
          </h1>
          {brandDetail?.description && (
            <p className="text-gray-600 dark:text-gray-400 mt-2">{brandDetail.description}</p>
          )}
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => router.back()}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            뒤로가기
          </Button>
          <Button
            onClick={handleRefresh}
            disabled={loading}
            className="flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            새로고침
          </Button>
        </div>
      </div>
      
      {/* 브랜드 통계 카드 */}
      {brandDetail && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">총 매장</p>
                  <p className="text-2xl font-bold">{brandDetail.stats?.total_stores || 0}</p>
                </div>
                <Building2 className="w-8 h-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">총 직원</p>
                  <p className="text-2xl font-bold">{brandDetail.stats?.total_employees || 0}</p>
                </div>
                <Users className="w-8 h-8 text-green-500" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">총 주문</p>
                  <p className="text-2xl font-bold">{brandDetail.stats?.total_orders || 0}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">오늘 주문</p>
                  <p className="text-2xl font-bold">{brandDetail.stats?.today_orders || 0}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-orange-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}
      
      {brandError && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          브랜드 정보를 불러오는데 실패했습니다: {brandError}
        </div>
      )}
      {loading ? (
        <div>데이터 불러오는 중...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* 매장 */}
          <Card>
            <CardHeader>
              <CardTitle>매장 목록</CardTitle>
              <CardDescription>이 브랜드에 속한 매장</CardDescription>
            </CardHeader>
            <CardContent>
              {!stores || stores.length === 0 ? (
                <div>매장이 없습니다.</div>
              ) : (
                <ul>
                  {stores.map(store => (
                    <li key={store.id}>{store.name}</li>
                  ))}
                </ul>
              )}
              <Button className="mt-2" onClick={() => router.push(`/brand-dashboard/${brandId}/stores`)}>매장 관리</Button>
            </CardContent>
          </Card>
          {/* 직원 */}
          <Card>
            <CardHeader>
              <CardTitle>직원 목록</CardTitle>
              <CardDescription>이 브랜드에 속한 직원</CardDescription>
            </CardHeader>
            <CardContent>
              {!employees || employees.length === 0 ? (
                <div>직원이 없습니다.</div>
              ) : (
                <ul>
                  {employees.map(emp => (
                    <li key={emp.id}>{emp.name}</li>
                  ))}
                </ul>
              )}
              <Button className="mt-2" onClick={() => router.push(`/brand-dashboard/${brandId}/employees`)}>직원 관리</Button>
            </CardContent>
          </Card>
          {/* 매출 */}
          <Card>
            <CardHeader>
              <CardTitle>매출 현황</CardTitle>
              <CardDescription>이 브랜드의 매출 데이터</CardDescription>
            </CardHeader>
            <CardContent>
              {sales.length === 0 ? (
                <div>매출 데이터가 없습니다.</div>
              ) : (
                <ul>
                  {sales.map(sale => (
                    <li key={sale.id}>매출: {sale.amount.toLocaleString()}원</li>
                  ))}
                </ul>
              )}
              <Button className="mt-2" onClick={() => router.push(`/brand-dashboard/${brandId}/sales`)}>매출 관리</Button>
            </CardContent>
          </Card>
          {/* 개선요청 */}
          <Card>
            <CardHeader>
              <CardTitle>개선요청</CardTitle>
              <CardDescription>이 브랜드의 개선요청 목록</CardDescription>
            </CardHeader>
            <CardContent>
              {improvements.length === 0 ? (
                <div>개선요청이 없습니다.</div>
              ) : (
                <ul>
                  {improvements.map(impr => (
                    <li key={impr.id}>{impr.title}</li>
                  ))}
                </ul>
              )}
              <Button className="mt-2" onClick={() => router.push(`/brand-dashboard/${brandId}/improvements`)}>개선요청 관리</Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
} 