// 동적 라우트: /brand-dashboard/[brand_id]/page.tsx
'use client';

import { useRouter, useParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

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

  // 각 하위 데이터 상태
  const [stores, setStores] = useState<Store[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [sales, setSales] = useState<Sale[]>([]);
  const [improvements, setImprovements] = useState<Improvement[]>([]);
  const [loading, setLoading] = useState(true);

  // 브랜드별 데이터 불러오기 (API 연동)
  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        // 실제 운영에서는 /api/admin/stores?brand_id=... 등으로 교체
        const [storesRes, employeesRes, salesRes, improvementsRes] = await Promise.all([
          fetch(`/api/admin/stores?brand_id=${brandId}`),
          fetch(`/api/admin/employees?brand_id=${brandId}`),
          fetch(`/api/admin/brand/${brandId}/sales`),
          fetch(`/api/admin/brand/${brandId}/improvements`),
        ]);
        setStores(storesRes.ok ? (await storesRes.json()).stores || [] : []);
        setEmployees(employeesRes.ok ? (await employeesRes.json()).employees || [] : []);
        setSales(salesRes.ok ? (await salesRes.json()).sales || [] : []);
        setImprovements(improvementsRes.ok ? (await improvementsRes.json()).improvements || [] : []);
      } catch (e) {
        setStores([]); setEmployees([]); setSales([]); setImprovements([]);
      } finally {
        setLoading(false);
      }
    }
    if (brandId) fetchData();
  }, [brandId]);

  return (
    <div className="min-h-screen p-8 bg-gradient-to-br from-white to-blue-50 dark:from-slate-900 dark:to-slate-800">
      <h1 className="text-3xl font-bold mb-6">브랜드 대시보드 (ID: {brandId})</h1>
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
              {stores.length === 0 ? (
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
              {employees.length === 0 ? (
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