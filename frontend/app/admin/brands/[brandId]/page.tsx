import { notFound } from 'next/navigation';
import React from 'react';

export default async function BrandDashboard({ params }: { params: Promise<{ brandId: string }> }) {
  const { brandId } = await params;
  
  // 브랜드 상세 데이터 불러오기
  const res = await fetch(`http://localhost:5000/api/brands/${brandId}`, { cache: 'no-store' });
  if (!res.ok) return notFound();
  const brand = await res.json();

  // 매장, 매출, 개선 등 추가 데이터 불러오기
  const [storesRes, salesRes, improvementsRes] = await Promise.all([
    fetch(`http://localhost:5000/api/brands/${brandId}/stores`, { cache: 'no-store' }),
    fetch(`http://localhost:5000/api/brands/${brandId}/sales`, { cache: 'no-store' }),
    fetch(`http://localhost:5000/api/brands/${brandId}/improvements`, { cache: 'no-store' })
  ]);
  const stores = storesRes.ok ? await storesRes.json() : [];
  const sales = salesRes.ok ? await salesRes.json() : [];
  const improvements = improvementsRes.ok ? await improvementsRes.json() : [];

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-6">{brand.name} 대시보드</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div className="bg-white rounded shadow p-6">
          <h2 className="text-lg font-semibold mb-2">매장 현황</h2>
          <div>매장 수: {brand.store_count}</div>
          <ul className="mt-2 list-disc ml-6">
            {stores.map((store: any) => (
              <li key={store.id}>{store.name}</li>
            ))}
          </ul>
        </div>
        <div className="bg-white rounded shadow p-6">
          <h2 className="text-lg font-semibold mb-2">매출 현황</h2>
          <div>총 매출: {brand.total_sales?.toLocaleString()} 원</div>
          <ul className="mt-2 list-disc ml-6">
            {sales.map((sale: any) => (
              <li key={sale.id}>{sale.date}: {sale.amount.toLocaleString()}원</li>
            ))}
          </ul>
        </div>
        <div className="bg-white rounded shadow p-6">
          <h2 className="text-lg font-semibold mb-2">개선 요청</h2>
          <ul className="mt-2 list-disc ml-6">
            {improvements.map((impr: any) => (
              <li key={impr.id}>{impr.title} ({impr.status})</li>
            ))}
          </ul>
        </div>
      </div>
      <div className="bg-white rounded shadow p-6">
        <h2 className="text-lg font-semibold mb-2">브랜드 정보</h2>
        <div>업종: {brand.industry}</div>
        <div>설명: {brand.description || '설명 없음'}</div>
        <div>등록일: {new Date(brand.created_at).toLocaleDateString('ko-KR')}</div>
        <div>상태: {brand.status === 'active' ? '활성' : '비활성'}</div>
      </div>
    </div>
  );
} 