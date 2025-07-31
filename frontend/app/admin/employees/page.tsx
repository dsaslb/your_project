'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { User, Mail, Phone, Calendar, CheckCircle, XCircle, Briefcase, MapPin } from 'lucide-react';
import { apiClient, Employee, Store } from '@/lib/api-client';
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

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [stores, setStores] = useState<Store[]>([]);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit' | 'delete' | 'view'>('create');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortColumn, setSortColumn] = useState<string>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [filterStoreId, setFilterStoreId] = useState<number | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const { isLoading, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 매장 목록 조회
  const fetchStores = useCallback(async () => {
    try {
      const response = await apiClient.getStores({ per_page: 100 });
      if (response.success) {
        setStores(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  }, [handleError]);

  // 직원 목록 조회
  const fetchEmployees = useCallback(async () => {
    await withLoading(async () => {
      try {
        const response = await apiClient.getEmployees({
          page: currentPage,
          per_page: 10,
          search: searchTerm,
          sort_by: sortColumn,
          sort_order: sortOrder,
          store_id: filterStoreId || undefined,
          status: filterStatus === 'all' ? undefined : filterStatus,
        });

        if (response.success) {
          setEmployees(response.data);
          setTotalItems(response.pagination?.total || response.data.length);
        }
      } catch (error) {
        handleError(error as Error);
      }
    });
  }, [currentPage, searchTerm, sortColumn, sortOrder, filterStoreId, filterStatus, withLoading, handleError]);

  // 직원 통계 카드
  const renderStatsCards = () => {
    const activeEmployees = employees.filter(emp => emp.status === 'active').length;
    const positionCounts = employees.reduce((acc, emp) => {
      const position = emp.position || '기타';
      acc[position] = (acc[position] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    const mostCommonPosition = Object.entries(positionCounts)
      .sort(([, a], [, b]) => b - a)[0]?.[0] || '-';

    return (
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 직원</CardTitle>
            <User className="h-4 w-4 text-cyan-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{totalItems}</div>
            <p className="text-xs text-slate-400">등록된 직원 수</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">재직 중</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{activeEmployees}</div>
            <p className="text-xs text-slate-400">활성 직원 수</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">퇴직</CardTitle>
            <XCircle className="h-4 w-4 text-red-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{totalItems - activeEmployees}</div>
            <p className="text-xs text-slate-400">비활성 직원 수</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">주요 직급</CardTitle>
            <Briefcase className="h-4 w-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold text-white truncate">{mostCommonPosition}</div>
            <p className="text-xs text-slate-400">가장 많은 직급</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">매장 수</CardTitle>
            <MapPin className="h-4 w-4 text-orange-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {new Set(employees.map(emp => emp.store_id)).size}
            </div>
            <p className="text-xs text-slate-400">직원이 있는 매장</p>
          </CardContent>
        </Card>
      </div>
    );
  };

  // 컬럼 정의
  const columns: Column<Employee>[] = [
    {
      key: 'id',
      header: 'ID',
      width: 'w-16',
      align: 'center',
    },
    {
      key: 'name',
      header: '이름',
      sortable: true,
      searchable: true,
      render: (value: string, row: Employee) => (
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-purple-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
            {value.charAt(0)}
          </div>
          <span className="font-medium">{value}</span>
        </div>
      ),
    },
    {
      key: 'email',
      header: '이메일',
      searchable: true,
      render: (value: string) => (
        <span className="flex items-center gap-1 text-sm text-slate-400">
          <Mail className="h-3 w-3" />
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
      key: 'position',
      header: '직급',
      sortable: true,
      render: (value: string) => (
        <span className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded-full text-xs">
          {value || '미지정'}
        </span>
      ),
    },
    {
      key: 'store_name',
      header: '매장',
      sortable: true,
      render: (value: string) => (
        <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs">
          {value || '-'}
        </span>
      ),
    },
    {
      key: 'brand_name',
      header: '브랜드',
      render: (value: string) => (
        <span className="text-sm text-slate-400">
          {value || '-'}
        </span>
      ),
    },
    {
      key: 'hire_date',
      header: '입사일',
      sortable: true,
      render: (value: string) => {
        if (!value) return '-';
        return (
          <span className="flex items-center gap-1 text-sm">
            <Calendar className="h-3 w-3 text-slate-400" />
            {new Date(value).toLocaleDateString('ko-KR')}
          </span>
        );
      },
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
          {value === 'active' ? '재직중' : '퇴직'}
        </span>
      ),
    },
  ];

  // 폼 필드 정의
  const formFields: FormField[] = [
    {
      name: 'store_id',
      label: '매장',
      type: 'select',
      required: true,
      options: stores.map(store => ({
        value: store.id,
        label: `${store.name} (${store.brand_name})`,
      })),
    },
    {
      name: 'name',
      label: '이름',
      type: 'text',
      placeholder: '직원 이름을 입력하세요',
      required: true,
      validation: (value: string) => {
        if (value.length < 2) return '이름은 2자 이상이어야 합니다.';
        if (value.length > 30) return '이름은 30자 이하여야 합니다.';
        return undefined;
      },
    },
    {
      name: 'email',
      label: '이메일',
      type: 'email',
      placeholder: 'example@email.com',
      required: false,
      validation: (value: string) => {
        if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          return '올바른 이메일 형식이 아닙니다.';
        }
        return undefined;
      },
    },
    {
      name: 'phone',
      label: '전화번호',
      type: 'tel',
      placeholder: '010-1234-5678',
      required: false,
      validation: (value: string) => {
        if (value && !/^[0-9-]+$/.test(value)) {
          return '전화번호는 숫자와 하이픈만 사용 가능합니다.';
        }
        return undefined;
      },
    },
    {
      name: 'position',
      label: '직급',
      type: 'select',
      required: false,
      options: [
        { value: '점장', label: '점장' },
        { value: '부점장', label: '부점장' },
        { value: '매니저', label: '매니저' },
        { value: '직원', label: '직원' },
        { value: '파트타임', label: '파트타임' },
        { value: '인턴', label: '인턴' },
      ],
    },
    {
      name: 'hire_date',
      label: '입사일',
      type: 'date',
      required: false,
    },
    {
      name: 'status',
      label: '상태',
      type: 'select',
      required: true,
      options: [
        { value: 'active', label: '재직중' },
        { value: 'inactive', label: '퇴직' },
      ],
    },
  ];

  // CRUD 핸들러
  const handleAdd = () => {
    setSelectedEmployee(null);
    setDialogMode('create');
    setDialogOpen(true);
  };

  const handleEdit = (employee: Employee) => {
    setSelectedEmployee(employee);
    setDialogMode('edit');
    setDialogOpen(true);
  };

  const handleDelete = (employee: Employee) => {
    setSelectedEmployee(employee);
    setDialogMode('delete');
    setDialogOpen(true);
  };

  const handleView = (employee: Employee) => {
    setSelectedEmployee(employee);
    setDialogMode('view');
    setDialogOpen(true);
  };

  const handleSubmit = async (data: Employee) => {
    try {
      if (dialogMode === 'create') {
        const response = await apiClient.createEmployee(data);
        if (response.success) {
          toast.success('직원이 등록되었습니다.');
          await fetchEmployees();
        }
      } else if (dialogMode === 'edit' && selectedEmployee) {
        const response = await apiClient.updateEmployee(selectedEmployee.id, data);
        if (response.success) {
          toast.success('직원 정보가 수정되었습니다.');
          await fetchEmployees();
        }
      } else if (dialogMode === 'delete' && selectedEmployee) {
        const response = await apiClient.deleteEmployee(selectedEmployee.id);
        if (response.success) {
          toast.success('직원이 삭제되었습니다.');
          await fetchEmployees();
        }
      }
    } catch (error) {
      handleError(error as Error);
      throw error;
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    fetchStores();
  }, [fetchStores]);

  useEffect(() => {
    fetchEmployees();
  }, [fetchEmployees]);

  return (
    <div className="p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">직원 관리</h1>
        <p className="text-slate-400">매장별 직원을 관리합니다.</p>
      </div>

      {/* 통계 카드 */}
      {renderStatsCards()}

      {/* 필터 */}
      <div className="flex gap-4 mb-6">
        <Select
          value={filterStoreId?.toString() || 'all'}
          onValueChange={(value) => {
            setFilterStoreId(value === 'all' ? null : parseInt(value));
            setCurrentPage(1);
          }}
        >
          <SelectTrigger className="w-64 bg-slate-800/50 border-slate-700">
            <SelectValue placeholder="매장 선택" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">전체 매장</SelectItem>
            {stores.map(store => (
              <SelectItem key={store.id} value={store.id.toString()}>
                {store.name} ({store.brand_name})
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
            <SelectItem value="active">재직중</SelectItem>
            <SelectItem value="inactive">퇴직</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* 데이터 테이블 */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardContent className="p-0">
          <DataTable
            data={employees}
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
            onRefresh={fetchEmployees}
            isLoading={isLoading}
            emptyMessage="등록된 직원이 없습니다."
          />
        </CardContent>
      </Card>

      {/* CRUD 다이얼로그 */}
      <CrudDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        mode={dialogMode}
        title={
          dialogMode === 'create' ? '새 직원 등록' :
          dialogMode === 'edit' ? '직원 정보 수정' :
          dialogMode === 'delete' ? '직원 삭제' :
          '직원 상세'
        }
        data={selectedEmployee}
        fields={formFields}
        onSubmit={handleSubmit}
      />
    </div>
  );
}