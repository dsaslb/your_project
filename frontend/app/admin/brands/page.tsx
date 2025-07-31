'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { Store, Users, MapPin, TrendingUp, Building2 } from 'lucide-react';
import { apiClient, Brand, Industry } from '@/lib/api-client';
import DataTable, { Column } from '@/components/common/DataTable';
import CrudDialog, { FormField } from '@/components/common/CrudDialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import useLoadingState from '@/hooks/useLoadingState';
import useErrorHandler from '@/hooks/useErrorHandler';

export default function BrandsPage() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit' | 'delete' | 'view'>('create');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortColumn, setSortColumn] = useState<string>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [filterIndustryId, setFilterIndustryId] = useState<number | null>(null);

  const { isLoading, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 업종 목록 조회
  const fetchIndustries = useCallback(async () => {
    try {
      const response = await apiClient.getIndustries({ per_page: 100 });
      if (response.success) {
        setIndustries(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  }, [handleError]);

  // 브랜드 목록 조회
  const fetchBrands = useCallback(async () => {
    await withLoading(async () => {
      try {
        const response = await apiClient.getBrands({
          page: currentPage,
          per_page: 10,
          search: searchTerm,
          sort_by: sortColumn,
          sort_order: sortOrder,
          industry_id: filterIndustryId || undefined,
        });

        if (response.success) {
          setBrands(response.data);
          setTotalItems(response.pagination?.total || response.data.length);
        }
      } catch (error) {
        handleError(error as Error);
      }
    });
  }, [currentPage, searchTerm, sortColumn, sortOrder, filterIndustryId, withLoading, handleError]);

  // 브랜드 통계 카드
  const renderStatsCards = () => {
    const totalStores = brands.reduce((sum, brand) => sum + (brand.store_count || 0), 0);
    const totalEmployees = brands.reduce((sum, brand) => sum + (brand.employee_count || 0), 0);
    const avgStoresPerBrand = brands.length > 0 ? (totalStores / brands.length).toFixed(1) : '0';

    return (
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 브랜드</CardTitle>
            <Store className="h-4 w-4 text-cyan-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{totalItems}</div>
            <p className="text-xs text-slate-400">등록된 브랜드 수</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 매장</CardTitle>
            <MapPin className="h-4 w-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{totalStores}</div>
            <p className="text-xs text-slate-400">브랜드별 매장 합계</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 직원</CardTitle>
            <Users className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{totalEmployees}</div>
            <p className="text-xs text-slate-400">브랜드별 직원 합계</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평균 매장</CardTitle>
            <TrendingUp className="h-4 w-4 text-orange-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{avgStoresPerBrand}</div>
            <p className="text-xs text-slate-400">브랜드당 평균 매장 수</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">활성 브랜드</CardTitle>
            <Building2 className="h-4 w-4 text-pink-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {brands.filter(brand => brand.store_count > 0).length}
            </div>
            <p className="text-xs text-slate-400">매장이 있는 브랜드</p>
          </CardContent>
        </Card>
      </div>
    );
  };

  // 컬럼 정의
  const columns: Column<Brand>[] = [
    {
      key: 'id',
      header: 'ID',
      width: 'w-16',
      align: 'center',
    },
    {
      key: 'name',
      header: '브랜드명',
      sortable: true,
      searchable: true,
    },
    {
      key: 'code',
      header: '브랜드 코드',
      sortable: true,
      searchable: true,
    },
    {
      key: 'industry_name',
      header: '업종',
      sortable: true,
      render: (value: string, row: Brand) => (
        <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs">
          {value || row.industry_name || '-'}
        </span>
      ),
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
      key: 'store_count',
      header: '매장 수',
      align: 'center',
      sortable: true,
      render: (value: number) => (
        <span className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded text-xs">
          {value || 0}개
        </span>
      ),
    },
    {
      key: 'employee_count',
      header: '직원 수',
      align: 'center',
      sortable: true,
      render: (value: number) => (
        <span className="px-2 py-1 bg-green-500/20 text-green-300 rounded text-xs">
          {value || 0}명
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
      name: 'industry_id',
      label: '업종',
      type: 'select',
      required: true,
      options: industries.map(ind => ({
        value: ind.id,
        label: ind.name,
      })),
    },
    {
      name: 'name',
      label: '브랜드명',
      type: 'text',
      placeholder: '예: 스타벅스',
      required: true,
      validation: (value: string) => {
        if (value.length < 2) return '브랜드명은 2자 이상이어야 합니다.';
        if (value.length > 50) return '브랜드명은 50자 이하여야 합니다.';
        return undefined;
      },
    },
    {
      name: 'code',
      label: '브랜드 코드',
      type: 'text',
      placeholder: '예: STARBUCKS',
      required: true,
      validation: (value: string) => {
        if (!/^[A-Z0-9_]+$/.test(value)) {
          return '브랜드 코드는 대문자, 숫자, 언더스코어만 사용 가능합니다.';
        }
        if (value.length < 2 || value.length > 30) {
          return '브랜드 코드는 2-30자여야 합니다.';
        }
        return undefined;
      },
    },
    {
      name: 'description',
      label: '설명',
      type: 'textarea',
      placeholder: '브랜드에 대한 설명을 입력하세요.',
      required: false,
    },
  ];

  // CRUD 핸들러
  const handleAdd = () => {
    setSelectedBrand(null);
    setDialogMode('create');
    setDialogOpen(true);
  };

  const handleEdit = (brand: Brand) => {
    setSelectedBrand(brand);
    setDialogMode('edit');
    setDialogOpen(true);
  };

  const handleDelete = (brand: Brand) => {
    setSelectedBrand(brand);
    setDialogMode('delete');
    setDialogOpen(true);
  };

  const handleView = (brand: Brand) => {
    setSelectedBrand(brand);
    setDialogMode('view');
    setDialogOpen(true);
  };

  const handleSubmit = async (data: Brand) => {
    try {
      if (dialogMode === 'create') {
        const response = await apiClient.createBrand(data);
        if (response.success) {
          toast.success('브랜드가 생성되었습니다.');
          await fetchBrands();
        }
      } else if (dialogMode === 'edit' && selectedBrand) {
        const response = await apiClient.updateBrand(selectedBrand.id, data);
        if (response.success) {
          toast.success('브랜드가 수정되었습니다.');
          await fetchBrands();
        }
      } else if (dialogMode === 'delete' && selectedBrand) {
        const response = await apiClient.deleteBrand(selectedBrand.id);
        if (response.success) {
          toast.success('브랜드가 삭제되었습니다.');
          await fetchBrands();
        }
      }
    } catch (error) {
      handleError(error as Error);
      throw error;
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    fetchIndustries();
  }, [fetchIndustries]);

  useEffect(() => {
    fetchBrands();
  }, [fetchBrands]);

  return (
    <div className="p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">브랜드 관리</h1>
        <p className="text-slate-400">업종별 브랜드를 관리합니다.</p>
      </div>

      {/* 통계 카드 */}
      {renderStatsCards()}

      {/* 필터 */}
      <div className="mb-6">
        <Select
          value={filterIndustryId?.toString() || 'all'}
          onValueChange={(value) => {
            setFilterIndustryId(value === 'all' ? null : parseInt(value));
            setCurrentPage(1);
          }}
        >
          <SelectTrigger className="w-64 bg-slate-800/50 border-slate-700">
            <SelectValue placeholder="업종 선택" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">전체 업종</SelectItem>
            {industries.map(industry => (
              <SelectItem key={industry.id} value={industry.id.toString()}>
                {industry.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* 데이터 테이블 */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardContent className="p-0">
          <DataTable
            data={brands}
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
            onRefresh={fetchBrands}
            isLoading={isLoading}
            emptyMessage="등록된 브랜드가 없습니다."
          />
        </CardContent>
      </Card>

      {/* CRUD 다이얼로그 */}
      <CrudDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        mode={dialogMode}
        title={
          dialogMode === 'create' ? '새 브랜드 추가' :
          dialogMode === 'edit' ? '브랜드 수정' :
          dialogMode === 'delete' ? '브랜드 삭제' :
          '브랜드 상세'
        }
        data={selectedBrand}
        fields={formFields}
        onSubmit={handleSubmit}
      />
    </div>
  );
} 