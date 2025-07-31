'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { MapPin, Users, Phone, CheckCircle, XCircle, TrendingUp } from 'lucide-react';
import { apiClient, Store, Brand } from '@/lib/api-client';
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

export default function StoresPage() {
  const [stores, setStores] = useState<Store[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [selectedStore, setSelectedStore] = useState<Store | null>(null);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit' | 'delete' | 'view'>('create');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortColumn, setSortColumn] = useState<string>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [filterBrandId, setFilterBrandId] = useState<number | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const { isLoading, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 브랜드 목록 조회
  const fetchBrands = useCallback(async () => {
    try {
      const response = await apiClient.getBrands({ per_page: 100 });
      if (response.success) {
        setBrands(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  }, [handleError]);

  // 매장 목록 조회
  const fetchStores = useCallback(async () => {
    await withLoading(async () => {
      try {
        const response = await apiClient.getStores({
          page: currentPage,
          per_page: 10,
          search: searchTerm,
          sort_by: sortColumn,
          sort_order: sortOrder,
          brand_id: filterBrandId || undefined,
          status: filterStatus === 'all' ? undefined : filterStatus,
        });

        if (response.success) {
          setStores(response.data);
          setTotalItems(response.pagination?.total || response.data.length);
        }
      } catch (error) {
        handleError(error as Error);
      }
    });
  }, [currentPage, searchTerm, sortColumn, sortOrder, filterBrandId, filterStatus, withLoading, handleError]);

  // 매장 통계 카드
  const renderStatsCards = () => {
    const activeStores = stores.filter(store => store.status === 'active').length;
    const totalEmployees = stores.reduce((sum, store) => sum + (store.employee_count || 0), 0);
    const avgEmployeesPerStore = stores.length > 0 ? (totalEmployees / stores.length).toFixed(1) : '0';

    return (
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 매장</CardTitle>
            <MapPin className="h-4 w-4 text-cyan-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{totalItems}</div>
            <p className="text-xs text-slate-400">등록된 매장 수</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">활성 매장</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{activeStores}</div>
            <p className="text-xs text-slate-400">운영 중인 매장</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">비활성 매장</CardTitle>
            <XCircle className="h-4 w-4 text-red-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{totalItems - activeStores}</div>
            <p className="text-xs text-slate-400">운영 중지 매장</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 직원</CardTitle>
            <Users className="h-4 w-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{totalEmployees}</div>
            <p className="text-xs text-slate-400">매장별 직원 합계</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평균 직원</CardTitle>
            <TrendingUp className="h-4 w-4 text-orange-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{avgEmployeesPerStore}</div>
            <p className="text-xs text-slate-400">매장당 평균 직원 수</p>
          </CardContent>
        </Card>
      </div>
    );
  };

  // 컬럼 정의
  const columns: Column<Store>[] = [
    {
      key: 'id',
      header: 'ID',
      width: 'w-16',
      align: 'center',
    },
    {
      key: 'name',
      header: '매장명',
      sortable: true,
      searchable: true,
    },
    {
      key: 'code',
      header: '매장 코드',
      sortable: true,
      searchable: true,
    },
    {
      key: 'brand_name',
      header: '브랜드',
      sortable: true,
      render: (value: string) => (
        <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs">
          {value || '-'}
        </span>
      ),
    },
    {
      key: 'address',
      header: '주소',
      render: (value: string) => (
        <span className="text-sm text-slate-400 truncate block max-w-xs">
          {value || '-'}
        </span>
      ),
    },
    {
      key: 'phone',
      header: '전화번호',
      render: (value: string) => (
        <span className="flex items-center gap-1 text-sm">
          <Phone className="h-3 w-3 text-slate-400" />
          {value || '-'}
        </span>
      ),
    },
    {
      key: 'manager_name',
      header: '점장',
      render: (value: string) => value || '-',
    },
    {
      key: 'employee_count',
      header: '직원 수',
      align: 'center',
      sortable: true,
      render: (value: number) => (
        <span className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded text-xs">
          {value || 0}명
        </span>
      ),
    },
    {
      key: 'status',
      header: '상태',
      align: 'center',
      sortable: true,
      render: (value: string) => (
        <span
          className={`px-2 py-1 rounded-full text-xs ${
            value === 'active'
              ? 'bg-green-500/20 text-green-300'
              : 'bg-red-500/20 text-red-300'
          }`}
        >
          {value === 'active' ? '운영중' : '중지'}
        </span>
      ),
    },
    {
      key: 'created_at',
      header: '개점일',
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
      name: 'brand_id',
      label: '브랜드',
      type: 'select',
      required: true,
      options: brands.map(brand => ({
        value: brand.id,
        label: brand.name,
      })),
    },
    {
      name: 'name',
      label: '매장명',
      type: 'text',
      placeholder: '예: 강남점',
      required: true,
      validation: (value: string) => {
        if (value.length < 2) return '매장명은 2자 이상이어야 합니다.';
        if (value.length > 50) return '매장명은 50자 이하여야 합니다.';
        return undefined;
      },
    },
    {
      name: 'code',
      label: '매장 코드',
      type: 'text',
      placeholder: '예: GANGNAM001',
      required: true,
      validation: (value: string) => {
        if (!/^[A-Z0-9_]+$/.test(value)) {
          return '매장 코드는 대문자, 숫자, 언더스코어만 사용 가능합니다.';
        }
        if (value.length < 3 || value.length > 30) {
          return '매장 코드는 3-30자여야 합니다.';
        }
        return undefined;
      },
    },
    {
      name: 'address',
      label: '주소',
      type: 'text',
      placeholder: '매장 주소를 입력하세요',
      required: false,
    },
    {
      name: 'phone',
      label: '전화번호',
      type: 'tel',
      placeholder: '예: 02-1234-5678',
      required: false,
      validation: (value: string) => {
        if (value && !/^[0-9-]+$/.test(value)) {
          return '전화번호는 숫자와 하이픈만 사용 가능합니다.';
        }
        return undefined;
      },
    },
    {
      name: 'manager_name',
      label: '점장명',
      type: 'text',
      placeholder: '점장 이름을 입력하세요',
      required: false,
    },
    {
      name: 'status',
      label: '상태',
      type: 'select',
      required: true,
      options: [
        { value: 'active', label: '운영중' },
        { value: 'inactive', label: '운영중지' },
      ],
    },
  ];

  // CRUD 핸들러
  const handleAdd = () => {
    setSelectedStore(null);
    setDialogMode('create');
    setDialogOpen(true);
  };

  const handleEdit = (store: Store) => {
    setSelectedStore(store);
    setDialogMode('edit');
    setDialogOpen(true);
  };

  const handleDelete = (store: Store) => {
    setSelectedStore(store);
    setDialogMode('delete');
    setDialogOpen(true);
  };

  const handleView = (store: Store) => {
    setSelectedStore(store);
    setDialogMode('view');
    setDialogOpen(true);
  };

  const handleSubmit = async (data: Store) => {
    try {
      if (dialogMode === 'create') {
        const response = await apiClient.createStore(data);
        if (response.success) {
          toast.success('매장이 생성되었습니다.');
          await fetchStores();
        }
      } else if (dialogMode === 'edit' && selectedStore) {
        const response = await apiClient.updateStore(selectedStore.id, data);
        if (response.success) {
          toast.success('매장이 수정되었습니다.');
          await fetchStores();
        }
      } else if (dialogMode === 'delete' && selectedStore) {
        const response = await apiClient.deleteStore(selectedStore.id);
        if (response.success) {
          toast.success('매장이 삭제되었습니다.');
          await fetchStores();
        }
      }
    } catch (error) {
      handleError(error as Error);
      throw error;
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    fetchBrands();
  }, [fetchBrands]);

  useEffect(() => {
    fetchStores();
  }, [fetchStores]);

  return (
    <div className="p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">매장 관리</h1>
        <p className="text-slate-400">브랜드별 매장을 관리합니다.</p>
      </div>

      {/* 통계 카드 */}
      {renderStatsCards()}

      {/* 필터 */}
      <div className="flex gap-4 mb-6">
        <Select
          value={filterBrandId?.toString() || 'all'}
          onValueChange={(value) => {
            setFilterBrandId(value === 'all' ? null : parseInt(value));
            setCurrentPage(1);
          }}
        >
          <SelectTrigger className="w-64 bg-slate-800/50 border-slate-700">
            <SelectValue placeholder="브랜드 선택" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">전체 브랜드</SelectItem>
            {brands.map(brand => (
              <SelectItem key={brand.id} value={brand.id.toString()}>
                {brand.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={filterStatus}
          onValueChange={(value) => {
            setFilterStatus(value);
            setCurrentPage(1);
          }}
        >
          <SelectTrigger className="w-48 bg-slate-800/50 border-slate-700">
            <SelectValue placeholder="상태 선택" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">전체 상태</SelectItem>
            <SelectItem value="active">운영중</SelectItem>
            <SelectItem value="inactive">운영중지</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* 데이터 테이블 */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardContent className="p-0">
          <DataTable
            data={stores}
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
            onRefresh={fetchStores}
            isLoading={isLoading}
            emptyMessage="등록된 매장이 없습니다."
          />
        </CardContent>
      </Card>

      {/* CRUD 다이얼로그 */}
      <CrudDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        mode={dialogMode}
        title={
          dialogMode === 'create' ? '새 매장 추가' :
          dialogMode === 'edit' ? '매장 수정' :
          dialogMode === 'delete' ? '매장 삭제' :
          '매장 상세'
        }
        data={selectedStore}
        fields={formFields}
        onSubmit={handleSubmit}
      />
    </div>
  );
}