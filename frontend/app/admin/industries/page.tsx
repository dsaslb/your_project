'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { Building2, Store, Users, TrendingUp } from 'lucide-react';
import { apiClient, Industry } from '@/lib/api-client';
import DataTable, { Column } from '@/components/common/DataTable';
import CrudDialog, { FormField } from '@/components/common/CrudDialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import useLoadingState from '@/hooks/useLoadingState';
import useErrorHandler from '@/hooks/useErrorHandler';

export default function IndustriesPage() {
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [selectedIndustry, setSelectedIndustry] = useState<Industry | null>(null);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit' | 'delete' | 'view'>('create');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortColumn, setSortColumn] = useState<string>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const { isLoading, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 업종 목록 조회
  const fetchIndustries = useCallback(async () => {
    await withLoading(async () => {
      try {
        const response = await apiClient.getIndustries({
          page: currentPage,
          per_page: 10,
          search: searchTerm,
          sort_by: sortColumn,
          sort_order: sortOrder,
        });

        if (response.success) {
          setIndustries(response.data);
          setTotalItems(response.pagination?.total || response.data.length);
        }
      } catch (error) {
        handleError(error as Error);
      }
    });
  }, [currentPage, searchTerm, sortColumn, sortOrder, withLoading, handleError]);

  // 업종 통계 카드
  const renderStatsCards = () => {
    const totalBrands = industries.reduce((sum, ind) => sum + (ind.brand_count || 0), 0);
    const avgBrandsPerIndustry = industries.length > 0 ? (totalBrands / industries.length).toFixed(1) : '0';

    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 업종</CardTitle>
            <Building2 className="h-4 w-4 text-cyan-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{industries.length}</div>
            <p className="text-xs text-slate-400">등록된 업종 수</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 브랜드</CardTitle>
            <Store className="h-4 w-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{totalBrands}</div>
            <p className="text-xs text-slate-400">업종별 브랜드 합계</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평균 브랜드</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{avgBrandsPerIndustry}</div>
            <p className="text-xs text-slate-400">업종당 평균 브랜드 수</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">활성 업종</CardTitle>
            <Users className="h-4 w-4 text-orange-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {industries.filter(ind => ind.brand_count > 0).length}
            </div>
            <p className="text-xs text-slate-400">브랜드가 있는 업종</p>
          </CardContent>
        </Card>
      </div>
    );
  };

  // 컬럼 정의
  const columns: Column<Industry>[] = [
    {
      key: 'id',
      header: 'ID',
      width: 'w-16',
      align: 'center',
    },
    {
      key: 'name',
      header: '업종명',
      sortable: true,
      searchable: true,
    },
    {
      key: 'code',
      header: '업종 코드',
      sortable: true,
      searchable: true,
    },
    {
      key: 'description',
      header: '설명',
      render: (value: string) => (
        <span className="text-sm text-slate-400 truncate block max-w-xs">
          {value || '-'}
        </span>
      ),
    },
    {
      key: 'brand_count',
      header: '브랜드 수',
      align: 'center',
      sortable: true,
      render: (value: number) => (
        <span className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded-full text-xs">
          {value || 0}개
        </span>
      ),
    },
    {
      key: 'created_at',
      header: '생성일',
      sortable: true,
      render: (value: string) => {
        if (!value) return '-';
        return new Date(value).toLocaleDateString('ko-KR');
      },
    },
  ];

  // 폼 필드 정의
  const formFields: FormField[] = [
    {
      name: 'name',
      label: '업종명',
      type: 'text',
      placeholder: '예: 외식업',
      required: true,
      validation: (value: string) => {
        if (value.length < 2) return '업종명은 2자 이상이어야 합니다.';
        if (value.length > 50) return '업종명은 50자 이하여야 합니다.';
        return undefined;
      },
    },
    {
      name: 'code',
      label: '업종 코드',
      type: 'text',
      placeholder: '예: FOOD',
      required: true,
      validation: (value: string) => {
        if (!/^[A-Z0-9_]+$/.test(value)) {
          return '업종 코드는 대문자, 숫자, 언더스코어만 사용 가능합니다.';
        }
        if (value.length < 2 || value.length > 20) {
          return '업종 코드는 2-20자여야 합니다.';
        }
        return undefined;
      },
    },
    {
      name: 'description',
      label: '설명',
      type: 'textarea',
      placeholder: '업종에 대한 설명을 입력하세요.',
      required: false,
    },
  ];

  // CRUD 핸들러
  const handleAdd = () => {
    setSelectedIndustry(null);
    setDialogMode('create');
    setDialogOpen(true);
  };

  const handleEdit = (industry: Industry) => {
    setSelectedIndustry(industry);
    setDialogMode('edit');
    setDialogOpen(true);
  };

  const handleDelete = (industry: Industry) => {
    setSelectedIndustry(industry);
    setDialogMode('delete');
    setDialogOpen(true);
  };

  const handleView = (industry: Industry) => {
    setSelectedIndustry(industry);
    setDialogMode('view');
    setDialogOpen(true);
  };

  const handleSubmit = async (data: Industry) => {
    try {
      if (dialogMode === 'create') {
        const response = await apiClient.createIndustry(data);
        if (response.success) {
          toast.success('업종이 생성되었습니다.');
          await fetchIndustries();
        }
      } else if (dialogMode === 'edit' && selectedIndustry) {
        const response = await apiClient.updateIndustry(selectedIndustry.id, data);
        if (response.success) {
          toast.success('업종이 수정되었습니다.');
          await fetchIndustries();
        }
      } else if (dialogMode === 'delete' && selectedIndustry) {
        const response = await apiClient.deleteIndustry(selectedIndustry.id);
        if (response.success) {
          toast.success('업종이 삭제되었습니다.');
          await fetchIndustries();
        }
      }
    } catch (error) {
      handleError(error as Error);
      throw error; // CrudDialog에서 처리하도록 다시 던짐
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    fetchIndustries();
  }, [fetchIndustries]);

  return (
    <div className="p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">업종 관리</h1>
        <p className="text-slate-400">시스템에 등록된 업종을 관리합니다.</p>
      </div>

      {/* 통계 카드 */}
      {renderStatsCards()}

      {/* 데이터 테이블 */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardContent className="p-0">
          <DataTable
            data={industries}
            columns={columns}
            pageSize={10}
            totalItems={totalItems}
            currentPage={currentPage}
            onPageChange={setCurrentPage}
            onSort={(column, order) => {
              setSortColumn(column);
              setSortOrder(order);
            }}
            onSearch={setSearchTerm}
            onAdd={handleAdd}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onView={handleView}
            onRefresh={fetchIndustries}
            isLoading={isLoading}
            emptyMessage="등록된 업종이 없습니다."
          />
        </CardContent>
      </Card>

      {/* CRUD 다이얼로그 */}
      <CrudDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        mode={dialogMode}
        title={
          dialogMode === 'create' ? '새 업종 추가' :
          dialogMode === 'edit' ? '업종 수정' :
          dialogMode === 'delete' ? '업종 삭제' :
          '업종 상세'
        }
        data={selectedIndustry}
        fields={formFields}
        onSubmit={handleSubmit}
      />
    </div>
  );
}