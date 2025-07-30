'use client';

import { useState, useMemo } from 'react';
import { cn } from '@/lib/utils';
import { ChevronDown, ChevronUp, Search, Filter, MoreHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface Column {
  key: string;
  title: string;
  sortable?: boolean;
  filterable?: boolean;
  width?: string;
  render?: (value: any, row: any) => React.ReactNode;
}

interface DataTableProps {
  data: any[];
  columns: Column[];
  title?: string;
  searchable?: boolean;
  sortable?: boolean;
  filterable?: boolean;
  pagination?: boolean;
  pageSize?: number;
  onRowClick?: (row: any) => void;
  onSelectionChange?: (selectedRows: any[]) => void;
}

export const DataTable = ({
  data,
  columns,
  title,
  searchable = true,
  sortable = true,
  filterable = true,
  pagination = true,
  pageSize = 10,
  onRowClick,
  onSelectionChange,
}: DataTableProps) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedRows, setSelectedRows] = useState<any[]>([]);
  const [filters, setFilters] = useState<Record<string, string>>({});

  // 검색 및 필터링
  const filteredData = useMemo(() => {
    let result = [...data];

    // 검색
    if (searchTerm) {
      result = result.filter(row =>
        Object.values(row).some(value =>
          String(value).toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // 필터
    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        result = result.filter(row =>
          String(row[key]).toLowerCase().includes(value.toLowerCase())
        );
      }
    });

    return result;
  }, [data, searchTerm, filters]);

  // 정렬
  const sortedData = useMemo(() => {
    if (!sortColumn) return filteredData;

    return [...filteredData].sort((a, b) => {
      const aValue = a[sortColumn];
      const bValue = b[sortColumn];

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [filteredData, sortColumn, sortDirection]);

  // 페이지네이션
  const totalPages = Math.ceil(sortedData.length / pageSize);
  const paginatedData = pagination
    ? sortedData.slice((currentPage - 1) * pageSize, currentPage * pageSize)
    : sortedData;

  // 정렬 처리
  const handleSort = (columnKey: string) => {
    if (!sortable) return;

    if (sortColumn === columnKey) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
  };

  // 행 선택 처리
  const handleRowSelection = (row: any) => {
    const newSelection = selectedRows.includes(row)
      ? selectedRows.filter(r => r !== row)
      : [...selectedRows, row];
    
    setSelectedRows(newSelection);
    onSelectionChange?.(newSelection);
  };

  // 전체 선택 처리
  const handleSelectAll = () => {
    const newSelection = selectedRows.length === paginatedData.length
      ? []
      : [...paginatedData];
    
    setSelectedRows(newSelection);
    onSelectionChange?.(newSelection);
  };

  return (
    <div className="bg-black/30 backdrop-blur-sm border border-cyan-500/20 rounded-lg overflow-hidden">
      {/* 헤더 */}
      {title && (
        <div className="p-4 border-b border-cyan-500/20">
          <h3 className="text-lg font-semibold text-white">{title}</h3>
        </div>
      )}

      {/* 검색 및 필터 */}
      {(searchable || filterable) && (
        <div className="p-4 border-b border-cyan-500/20 space-y-3">
          {searchable && (
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                type="text"
                placeholder="검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-black/50 border-cyan-500/30 text-white placeholder:text-slate-400"
              />
            </div>
          )}

          {filterable && (
            <div className="flex flex-wrap gap-2">
              {columns
                .filter(col => col.filterable)
                .map(col => (
                  <div key={col.key} className="flex items-center space-x-2">
                    <span className="text-xs text-slate-400">{col.title}:</span>
                    <Input
                      type="text"
                      placeholder={`${col.title} 필터`}
                      value={filters[col.key] || ''}
                      onChange={(e) =>
                        setFilters(prev => ({
                          ...prev,
                          [col.key]: e.target.value
                        }))
                      }
                      className="w-32 h-8 text-xs bg-black/50 border-cyan-500/30 text-white"
                    />
                  </div>
                ))}
            </div>
          )}
        </div>
      )}

      {/* 테이블 */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-black/50 border-b border-cyan-500/20">
              {onSelectionChange && (
                <th className="p-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedRows.length === paginatedData.length && paginatedData.length > 0}
                    onChange={handleSelectAll}
                    className="rounded border-cyan-500/30 bg-black/50 text-cyan-400"
                  />
                </th>
              )}
              {columns.map(col => (
                <th
                  key={col.key}
                  className={cn(
                    "p-3 text-left text-sm font-medium text-slate-300",
                    col.sortable && sortable && "cursor-pointer hover:text-white",
                    col.width && `w-${col.width}`
                  )}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <div className="flex items-center space-x-1">
                    <span>{col.title}</span>
                    {col.sortable && sortable && sortColumn === col.key && (
                      sortDirection === 'asc' ? (
                        <ChevronUp className="w-3 h-3" />
                      ) : (
                        <ChevronDown className="w-3 h-3" />
                      )
                    )}
                  </div>
                </th>
              ))}
              <th className="p-3 text-left w-10"></th>
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, index) => (
              <tr
                key={index}
                className={cn(
                  "border-b border-cyan-500/10 hover:bg-cyan-500/5 transition-colors",
                  onRowClick && "cursor-pointer",
                  selectedRows.includes(row) && "bg-cyan-500/10"
                )}
                onClick={() => onRowClick?.(row)}
              >
                {onSelectionChange && (
                  <td className="p-3">
                    <input
                      type="checkbox"
                      checked={selectedRows.includes(row)}
                      onChange={() => handleRowSelection(row)}
                      className="rounded border-cyan-500/30 bg-black/50 text-cyan-400"
                    />
                  </td>
                )}
                {columns.map(col => (
                  <td key={col.key} className="p-3 text-sm text-slate-300">
                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                  </td>
                ))}
                <td className="p-3">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-slate-400 hover:text-white"
                  >
                    <MoreHorizontal className="w-4 h-4" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 페이지네이션 */}
      {pagination && totalPages > 1 && (
        <div className="p-4 border-t border-cyan-500/20 flex items-center justify-between">
          <div className="text-sm text-slate-400">
            {((currentPage - 1) * pageSize) + 1} - {Math.min(currentPage * pageSize, sortedData.length)} / {sortedData.length}개
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="text-slate-400 hover:text-white disabled:opacity-50"
            >
              이전
            </Button>
            
            {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
              <Button
                key={page}
                variant={currentPage === page ? "default" : "ghost"}
                size="sm"
                onClick={() => setCurrentPage(page)}
                className={cn(
                  currentPage === page
                    ? "bg-cyan-500 text-white"
                    : "text-slate-400 hover:text-white"
                )}
              >
                {page}
              </Button>
            ))}
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="text-slate-400 hover:text-white disabled:opacity-50"
            >
              다음
            </Button>
          </div>
        </div>
      )}

      {/* 선택된 행 정보 */}
      {onSelectionChange && selectedRows.length > 0 && (
        <div className="p-4 border-t border-cyan-500/20 bg-cyan-500/10">
          <div className="text-sm text-cyan-400">
            {selectedRows.length}개 행이 선택됨
          </div>
        </div>
      )}
    </div>
  );
};

// 간단한 데이터 카드 (대시보드용)
export const DataCard = ({ 
  title, 
  value, 
  change, 
  icon: Icon,
  color = 'cyan'
}: {
  title: string;
  value: string | number;
  change?: number;
  icon: any;
  color?: string;
}) => {
  return (
    <div className="p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm">
      <div className="flex items-center justify-between mb-2">
        <div className={cn(
          "p-2 rounded-lg",
          color === 'cyan' && "bg-cyan-500/20",
          color === 'green' && "bg-green-500/20",
          color === 'yellow' && "bg-yellow-500/20",
          color === 'red' && "bg-red-500/20"
        )}>
          <Icon className={cn(
            "w-4 h-4",
            color === 'cyan' && "text-cyan-400",
            color === 'green' && "text-green-400",
            color === 'yellow' && "text-yellow-400",
            color === 'red' && "text-red-400"
          )} />
        </div>
        {change !== undefined && (
          <span className={cn(
            "text-xs font-mono",
            change > 0 ? "text-green-400" : "text-red-400"
          )}>
            {change > 0 ? '+' : ''}{change}%
          </span>
        )}
      </div>
      
      <div className="mb-1">
        <span className="text-2xl font-bold text-white">
          {value}
        </span>
      </div>
      
      <div className="text-xs text-slate-400">
        {title}
      </div>
    </div>
  );
}; 