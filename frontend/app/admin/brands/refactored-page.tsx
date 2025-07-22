'use client';

import React, { useState, useMemo, useCallback } from 'react';
import { useBrands, useCreateBrand } from '../../../src/hooks/useApi';
import { useAuthStore } from '../../../src/store/authStore';
import { useUIStore } from '../../../src/store/uiStore';
import { DataTable, Column } from '../../../src/components/ui/DataTable';
import { StatsCard } from '../../../src/components/ui/StatsCard';
import { MemoizedCard } from '../../../src/components/optimized/MemoizedCard';
import { LoadingSpinner } from '../../../src/components/ui/LoadingSpinner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Building, Users, Calendar, TrendingUp, Plus } from 'lucide-react';
import { toast } from 'sonner';

export default function RefactoredBrandsPage() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newBrand, setNewBrand] = useState({
    name: '',
    industry: '',
    description: ''
  });

  // Zustand 스토어 사용
  const { user } = useAuthStore();
  const { addToast } = useUIStore();

  // API 훅 사용
  const { data: brandsData, isLoading, error, refetch } = useBrands();
  const createBrandMutation = useCreateBrand();

  const brands = brandsData?.data || [];

  // 메모이제이션된 통계 데이터
  const statsData = useMemo(() => [
    {
      title: '총 브랜드',
      value: brands.length,
      description: '활성 브랜드 수',
      icon: Building
    },
    {
      title: '총 매장',
      value: brands.reduce((total: number, brand: any) => total + (brand.branch_count || 0), 0),
      description: '전체 매장 수',
      icon: Building
    },
    {
      title: '총 직원',
      value: brands.reduce((total: number, brand: any) => total + (brand.employee_count || 0), 0),
      description: '전체 직원 수',
      icon: Users
    },
    {
      title: '이번 달 매출',
      value: `${brands.reduce((total: number, brand: any) => total + (brand.monthly_sales || 0), 0).toLocaleString()}원`,
      description: '전체 브랜드 합계',
      icon: TrendingUp
    }
  ], [brands]);

  // 메모이제이션된 테이블 컬럼
  const columns: Column<any>[] = useMemo(() => [
    {
      key: 'name',
      title: '브랜드명',
      render: (value, record) => (
        <div>
          <div className="font-medium">{value}</div>
          <div className="text-sm text-gray-500">{record.industry}</div>
        </div>
      )
    },
    {
      key: 'description',
      title: '설명',
      render: (value) => (
        <div className="max-w-xs truncate" title={value}>
          {value || '설명이 없습니다.'}
        </div>
      )
    },
    {
      key: 'branch_count',
      title: '매장 수',
      align: 'center',
      render: (value) => <span className="font-medium">{value || 0}개</span>
    },
    {
      key: 'employee_count',
      title: '직원 수',
      align: 'center',
      render: (value) => <span className="font-medium">{value || 0}명</span>
    },
    {
      key: 'created_at',
      title: '등록일',
      align: 'center',
      render: (value) => (
        <span className="text-sm text-gray-600">
          {new Date(value).toLocaleDateString('ko-KR')}
        </span>
      )
    },
    {
      key: 'status',
      title: '상태',
      align: 'center',
      render: (value) => (
        <span className={`px-2 py-1 text-xs rounded-full ${
          value === 'active' 
            ? 'bg-green-100 text-green-800' 
            : 'bg-gray-100 text-gray-800'
        }`}>
          {value === 'active' ? '활성' : '비활성'}
        </span>
      )
    }
  ], []);

  // 메모이제이션된 액션 핸들러
  const handleCreateBrand = useCallback(async () => {
    if (!newBrand.name || !newBrand.industry) {
      addToast({
        type: 'error',
        title: '입력 오류',
        message: '브랜드명과 업종을 입력해주세요.'
      });
      return;
    }

    try {
      await createBrandMutation.mutateAsync(newBrand);
      setNewBrand({ name: '', industry: '', description: '' });
      setIsCreateDialogOpen(false);
      addToast({
        type: 'success',
        title: '성공',
        message: '브랜드가 생성되었습니다.'
      });
    } catch (error) {
      console.error('브랜드 생성 실패:', error);
    }
  }, [newBrand, createBrandMutation, addToast]);

  const handleBrandClick = useCallback((brand: any) => {
    // 브랜드 상세 페이지로 이동
    console.log('브랜드 클릭:', brand);
  }, []);

  const handleExport = useCallback(() => {
    // CSV 내보내기 로직
    console.log('브랜드 데이터 내보내기');
    addToast({
      type: 'info',
      title: '내보내기',
      message: '브랜드 데이터를 내보내는 중입니다.'
    });
  }, [addToast]);

  const handleSearch = useCallback((query: string) => {
    // 검색 로직
    console.log('검색:', query);
  }, []);

  if (isLoading) {
    return <LoadingSpinner size="lg" text="브랜드 정보를 불러오는 중..." fullScreen />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-500 mb-4">브랜드 정보를 불러오는데 실패했습니다.</p>
          <Button onClick={() => refetch()} variant="outline">
            다시 시도
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* 헤더 */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">브랜드 관리</h1>
            <p className="text-gray-600 mt-1">
              등록된 브랜드 목록을 확인하고 관리하세요.
              {user && <span className="ml-2 text-sm text-blue-600">({user.name}님)</span>}
            </p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                새 브랜드 추가
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>새 브랜드 추가</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">브랜드명 *</Label>
                  <Input
                    id="name"
                    value={newBrand.name}
                    onChange={(e) => setNewBrand({ ...newBrand, name: e.target.value })}
                    placeholder="브랜드명을 입력하세요"
                  />
                </div>
                <div>
                  <Label htmlFor="industry">업종 *</Label>
                  <Input
                    id="industry"
                    value={newBrand.industry}
                    onChange={(e) => setNewBrand({ ...newBrand, industry: e.target.value })}
                    placeholder="업종을 입력하세요 (예: 카페, 레스토랑)"
                  />
                </div>
                <div>
                  <Label htmlFor="description">설명</Label>
                  <Input
                    id="description"
                    value={newBrand.description}
                    onChange={(e) => setNewBrand({ ...newBrand, description: e.target.value })}
                    placeholder="브랜드에 대한 설명을 입력하세요"
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                    취소
                  </Button>
                  <Button 
                    onClick={handleCreateBrand}
                    disabled={createBrandMutation.isPending}
                  >
                    {createBrandMutation.isPending ? '생성 중...' : '생성'}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statsData.map((stat, index) => (
            <StatsCard
              key={index}
              title={stat.title}
              value={stat.value}
              description={stat.description}
              icon={stat.icon}
              onClick={() => console.log(`${stat.title} 클릭`)}
            />
          ))}
        </div>

        {/* 브랜드 목록 - DataTable 사용 */}
        <DataTable
          title="브랜드 목록"
          data={brands}
          columns={columns}
          loading={isLoading}
          error={error}
          onRefresh={refetch}
          onAdd={() => setIsCreateDialogOpen(true)}
          onExport={handleExport}
          searchable
          onSearch={handleSearch}
          actions={[
            {
              label: '상세보기',
              onClick: handleBrandClick,
              variant: 'outline',
              size: 'sm'
            },
            {
              label: '매장 관리',
              onClick: (brand) => console.log('매장 관리:', brand),
              variant: 'outline',
              size: 'sm'
            }
          ]}
          emptyMessage="등록된 브랜드가 없습니다"
          emptyAction={{
            label: '첫 번째 브랜드 추가',
            onClick: () => setIsCreateDialogOpen(true)
          }}
        />

        {/* 브랜드 카드 뷰 (대안) */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {brands.map((brand: any) => (
            <MemoizedCard
              key={brand.id}
              title={brand.name}
              subtitle={brand.industry}
              content={
                <div className="space-y-2">
                  <p className="text-sm text-gray-700">
                    {brand.description || '설명이 없습니다.'}
                  </p>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">매장 수:</span>
                    <span className="font-medium">{brand.branch_count || 0}개</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">직원 수:</span>
                    <span className="font-medium">{brand.employee_count || 0}명</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">등록일:</span>
                    <span className="font-medium">
                      {new Date(brand.created_at).toLocaleDateString('ko-KR')}
                    </span>
                  </div>
                </div>
              }
              badge={{
                text: brand.status === 'active' ? '활성' : '비활성',
                variant: brand.status === 'active' ? 'default' : 'secondary'
              }}
              icon={Building}
              actions={[
                {
                  label: '상세보기',
                  onClick: () => handleBrandClick(brand),
                  variant: 'outline',
                  size: 'sm'
                },
                {
                  label: '매장 관리',
                  onClick: () => console.log('매장 관리:', brand),
                  variant: 'outline',
                  size: 'sm'
                }
              ]}
              onClick={() => handleBrandClick(brand)}
            />
          ))}
        </div>
      </div>
    </div>
  );
} 