import React, { Suspense, lazy } from 'react';
import { LoadingSpinner } from '../ui/LoadingSpinner';

// 지연 로딩할 컴포넌트들
const DataTable = lazy(() => import('../ui/DataTable').then(module => ({ default: module.DataTable })));
const StatsCard = lazy(() => import('../ui/StatsCard').then(module => ({ default: module.StatsCard })));
const MemoizedCard = lazy(() => import('../optimized/MemoizedCard').then(module => ({ default: module.MemoizedCard })));

// 로딩 컴포넌트
const TableLoading = () => (
  <div className="space-y-4">
    <div className="h-8 bg-gray-200 rounded animate-pulse"></div>
    <div className="space-y-2">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="h-12 bg-gray-100 rounded animate-pulse"></div>
      ))}
    </div>
  </div>
);

const CardLoading = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {[...Array(6)].map((_, i) => (
      <div key={i} className="h-48 bg-gray-100 rounded-lg animate-pulse"></div>
    ))}
  </div>
);

// 지연 로딩된 브랜드 페이지
export function LazyBrandsPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* 헤더 */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">브랜드 관리</h1>
            <p className="text-gray-600 mt-1">등록된 브랜드 목록을 확인하고 관리하세요.</p>
          </div>
        </div>

        {/* 통계 카드 - 지연 로딩 */}
        <Suspense fallback={<CardLoading />}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatsCard
              title="총 브랜드"
              value="2"
              description="활성 브랜드 수"
            />
            <StatsCard
              title="총 매장"
              value="3"
              description="전체 매장 수"
            />
            <StatsCard
              title="총 직원"
              value="3"
              description="전체 직원 수"
            />
            <StatsCard
              title="이번 달 매출"
              value="0원"
              description="전체 브랜드 합계"
            />
          </div>
        </Suspense>

        {/* 데이터 테이블 - 지연 로딩 */}
        <Suspense fallback={<TableLoading />}>
          <DataTable
            title="브랜드 목록"
            data={[]}
            columns={[]}
            loading={false}
            emptyMessage="데이터를 불러오는 중..."
          />
        </Suspense>

        {/* 브랜드 카드 - 지연 로딩 */}
        <Suspense fallback={<CardLoading />}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <MemoizedCard 
              title="로딩 중..." 
              value="..."
            />
          </div>
        </Suspense>
      </div>
    </div>
  );
}

// 기본 내보내기
export default LazyBrandsPage; 