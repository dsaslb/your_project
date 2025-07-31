'use client';

import React, { useState, useCallback, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Search,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Edit,
  Trash2,
  Eye,
  Plus,
  RefreshCw,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Column<T> {
  key: keyof T | string;
  header: string;
  sortable?: boolean;
  searchable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, row: T) => React.ReactNode;
}

export interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  pageSize?: number;
  totalItems?: number;
  currentPage?: number;
  onPageChange?: (page: number) => void;
  onSort?: (column: string, order: 'asc' | 'desc') => void;
  onSearch?: (search: string) => void;
  onEdit?: (row: T) => void;
  onDelete?: (row: T) => void;
  onView?: (row: T) => void;
  onAdd?: () => void;
  onRefresh?: () => void;
  isLoading?: boolean;
  emptyMessage?: string;
  className?: string;
}

export function DataTable<T extends { id: number | string }>({
  data,
  columns,
  pageSize = 10,
  totalItems,
  currentPage = 1,
  onPageChange,
  onSort,
  onSearch,
  onEdit,
  onDelete,
  onView,
  onAdd,
  onRefresh,
  isLoading = false,
  emptyMessage = '데이터가 없습니다.',
  className,
}: DataTableProps<T>) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  // 페이지 정보 계산
  const totalPages = totalItems ? Math.ceil(totalItems / pageSize) : Math.ceil(data.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const currentData = totalItems ? data : data.slice(startIndex, endIndex);

  // 정렬 처리
  const handleSort = useCallback((columnKey: string) => {
    if (!onSort) return;

    const newOrder = sortColumn === columnKey && sortOrder === 'asc' ? 'desc' : 'asc';
    setSortColumn(columnKey);
    setSortOrder(newOrder);
    onSort(columnKey, newOrder);
  }, [sortColumn, sortOrder, onSort]);

  // 검색 처리
  const handleSearch = useCallback((value: string) => {
    setSearchTerm(value);
    if (onSearch) {
      onSearch(value);
    }
  }, [onSearch]);

  // 페이지 변경 처리
  const handlePageChange = useCallback((page: number) => {
    if (onPageChange && page >= 1 && page <= totalPages) {
      onPageChange(page);
    }
  }, [onPageChange, totalPages]);

  // 액션 버튼 렌더링
  const renderActions = useCallback((row: T) => {
    return (
      <div className="flex gap-1 justify-end">
        {onView && (
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-cyan-400 hover:bg-cyan-500/20"
            onClick={() => onView(row)}
          >
            <Eye className="h-4 w-4" />
          </Button>
        )}
        {onEdit && (
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-purple-400 hover:bg-purple-500/20"
            onClick={() => onEdit(row)}
          >
            <Edit className="h-4 w-4" />
          </Button>
        )}
        {onDelete && (
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-red-400 hover:bg-red-500/20"
            onClick={() => onDelete(row)}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        )}
      </div>
    );
  }, [onView, onEdit, onDelete]);

  // 검색 가능한 컬럼 필터링
  const searchableColumns = useMemo(() => 
    columns.filter(col => col.searchable !== false),
    [columns]
  );

  return (
    <div className={cn("space-y-4", className)}>
      {/* 상단 툴바 */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2 flex-1">
          {onSearch && searchableColumns.length > 0 && (
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="검색..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-10 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-400"
              />
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          {onRefresh && (
            <Button
              variant="outline"
              size="icon"
              onClick={onRefresh}
              disabled={isLoading}
              className="border-slate-700 hover:bg-slate-800"
            >
              <RefreshCw className={cn("h-4 w-4", isLoading && "animate-spin")} />
            </Button>
          )}
          {onAdd && (
            <Button
              onClick={onAdd}
              className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600"
            >
              <Plus className="h-4 w-4 mr-2" />
              추가
            </Button>
          )}
        </div>
      </div>

      {/* 테이블 */}
      <div className="rounded-lg border border-slate-700 overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-slate-800/50 border-b border-slate-700">
              {columns.map((column) => (
                <TableHead
                  key={column.key as string}
                  className={cn(
                    "text-slate-300",
                    column.align === 'center' && 'text-center',
                    column.align === 'right' && 'text-right',
                    column.width
                  )}
                >
                  {column.sortable !== false && onSort ? (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-auto p-0 font-medium hover:bg-transparent hover:text-white"
                      onClick={() => handleSort(column.key as string)}
                    >
                      {column.header}
                      {sortColumn === column.key ? (
                        sortOrder === 'asc' ? (
                          <ArrowUp className="ml-2 h-4 w-4" />
                        ) : (
                          <ArrowDown className="ml-2 h-4 w-4" />
                        )
                      ) : (
                        <ArrowUpDown className="ml-2 h-4 w-4 opacity-50" />
                      )}
                    </Button>
                  ) : (
                    column.header
                  )}
                </TableHead>
              ))}
              {(onView || onEdit || onDelete) && (
                <TableHead className="text-right w-32">작업</TableHead>
              )}
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell
                  colSpan={columns.length + (onView || onEdit || onDelete ? 1 : 0)}
                  className="text-center py-8 text-slate-400"
                >
                  <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2" />
                  로딩 중...
                </TableCell>
              </TableRow>
            ) : currentData.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={columns.length + (onView || onEdit || onDelete ? 1 : 0)}
                  className="text-center py-8 text-slate-400"
                >
                  {emptyMessage}
                </TableCell>
              </TableRow>
            ) : (
              currentData.map((row) => (
                <TableRow
                  key={row.id}
                  className="border-b border-slate-700 hover:bg-slate-800/30"
                >
                  {columns.map((column) => {
                    const value = column.key.includes('.')
                      ? column.key.split('.').reduce((obj: any, key) => obj?.[key], row)
                      : (row as any)[column.key];
                    
                    return (
                      <TableCell
                        key={column.key as string}
                        className={cn(
                          "text-slate-300",
                          column.align === 'center' && 'text-center',
                          column.align === 'right' && 'text-right'
                        )}
                      >
                        {column.render ? column.render(value, row) : value}
                      </TableCell>
                    );
                  })}
                  {(onView || onEdit || onDelete) && (
                    <TableCell>{renderActions(row)}</TableCell>
                  )}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* 페이지네이션 */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-slate-400">
            전체 {totalItems || data.length}개 중 {startIndex + 1}-{Math.min(endIndex, totalItems || data.length)}개
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={() => handlePageChange(1)}
              disabled={currentPage === 1}
              className="h-8 w-8 border-slate-700 hover:bg-slate-800"
            >
              <ChevronsLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="h-8 w-8 border-slate-700 hover:bg-slate-800"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            
            <div className="flex items-center gap-1">
              <Input
                type="number"
                min={1}
                max={totalPages}
                value={currentPage}
                onChange={(e) => handlePageChange(parseInt(e.target.value) || 1)}
                className="w-16 h-8 text-center bg-slate-800/50 border-slate-700"
              />
              <span className="text-sm text-slate-400">/ {totalPages}</span>
            </div>
            
            <Button
              variant="outline"
              size="icon"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="h-8 w-8 border-slate-700 hover:bg-slate-800"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={() => handlePageChange(totalPages)}
              disabled={currentPage === totalPages}
              className="h-8 w-8 border-slate-700 hover:bg-slate-800"
            >
              <ChevronsRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default DataTable;