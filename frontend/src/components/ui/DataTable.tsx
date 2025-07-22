import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './card';
import { Button } from './button';
import { Input } from './input';
import { Badge } from './badge';
import { Search, Filter, Download, Plus } from 'lucide-react';

export interface Column<T = any> {
  key: string;
  title: string;
  render?: (value: any, record: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

export interface DataTableProps<T = any> {
  title?: string;
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
  onAdd?: () => void;
  onExport?: () => void;
  searchable?: boolean;
  onSearch?: (query: string) => void;
  pagination?: {
    current: number;
    total: number;
    pageSize: number;
    onChange: (page: number) => void;
  };
  actions?: {
    label: string;
    onClick: (record: T) => void;
    variant?: 'default' | 'outline' | 'destructive';
    size?: 'sm' | 'lg';
  }[];
  emptyMessage?: string;
  emptyAction?: {
    label: string;
    onClick: () => void;
  };
}

export function DataTable<T = any>({
  title,
  data,
  columns,
  loading = false,
  error = null,
  onRefresh,
  onAdd,
  onExport,
  searchable = false,
  onSearch,
  pagination,
  actions = [],
  emptyMessage = '데이터가 없습니다.',
  emptyAction
}: DataTableProps<T>) {
  const [searchQuery, setSearchQuery] = React.useState('');

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    onSearch?.(query);
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4 text-gray-600">데이터를 불러오는 중...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <div className="text-center">
            <p className="text-red-500 mb-4">{error}</p>
            {onRefresh && (
              <Button onClick={onRefresh} variant="outline">
                다시 시도
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      {/* 헤더 */}
      {(title || onAdd || onExport || searchable) && (
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-4">
              {title && <CardTitle>{title}</CardTitle>}
              {onAdd && (
                <Button onClick={onAdd} size="sm" className="flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  추가
                </Button>
              )}
            </div>
            <div className="flex items-center gap-2">
              {searchable && (
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="검색..."
                    value={searchQuery}
                    onChange={(e) => handleSearch(e.target.value)}
                    className="pl-10 w-64"
                  />
                </div>
              )}
              {onExport && (
                <Button onClick={onExport} variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  내보내기
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
      )}

      {/* 테이블 */}
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                {columns.map((column) => (
                  <th
                    key={column.key}
                    className={`px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider ${
                      column.align === 'center' ? 'text-center' : 
                      column.align === 'right' ? 'text-right' : 'text-left'
                    }`}
                    style={{ width: column.width }}
                  >
                    {column.title}
                  </th>
                ))}
                {actions.length > 0 && (
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    작업
                  </th>
                )}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.length === 0 ? (
                <tr>
                  <td
                    colSpan={columns.length + (actions.length > 0 ? 1 : 0)}
                    className="px-6 py-12 text-center"
                  >
                    <div className="flex flex-col items-center">
                      <p className="text-gray-500 mb-4">{emptyMessage}</p>
                      {emptyAction && (
                        <Button onClick={emptyAction.onClick} variant="outline">
                          {emptyAction.label}
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ) : (
                data.map((record, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    {columns.map((column) => (
                      <td
                        key={column.key}
                        className={`px-6 py-4 whitespace-nowrap text-sm text-gray-900 ${
                          column.align === 'center' ? 'text-center' : 
                          column.align === 'right' ? 'text-right' : 'text-left'
                        }`}
                      >
                        {column.render
                          ? column.render((record as any)[column.key], record)
                          : (record as any)[column.key]}
                      </td>
                    ))}
                    {actions.length > 0 && (
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center gap-2">
                          {actions.map((action, actionIndex) => (
                            <Button
                              key={actionIndex}
                              onClick={() => action.onClick(record)}
                              variant={action.variant || 'outline'}
                              size={action.size || 'sm'}
                            >
                              {action.label}
                            </Button>
                          ))}
                        </div>
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* 페이지네이션 */}
        {pagination && (
          <div className="px-6 py-4 border-t bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-700">
                총 {pagination.total}개 중 {(pagination.current - 1) * pagination.pageSize + 1}-
                {Math.min(pagination.current * pagination.pageSize, pagination.total)}개
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => pagination.onChange(pagination.current - 1)}
                  disabled={pagination.current <= 1}
                >
                  이전
                </Button>
                <span className="text-sm text-gray-700">
                  {pagination.current} / {Math.ceil(pagination.total / pagination.pageSize)}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => pagination.onChange(pagination.current + 1)}
                  disabled={pagination.current >= Math.ceil(pagination.total / pagination.pageSize)}
                >
                  다음
                </Button>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
} 