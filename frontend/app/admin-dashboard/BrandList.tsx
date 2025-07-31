'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Building2, 
  Plus, 
  Edit, 
  Trash2,
  Search
} from 'lucide-react';
import { useBrands } from '@/hooks/useDashboard';
import { toast } from 'sonner';

interface Brand {
  id: number;
  name: string;
  description?: string;
  status: 'active' | 'inactive' | 'pending';
  store_count: number;
  employee_count: number;
  total_revenue: number;
  created_at: string;
}

export default function BrandList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const { brands, loading, error, refetch } = useBrands(1, 50, searchTerm, statusFilter);

  const filteredBrands = brands.filter((brand: Brand) => {
    const matchesSearch = brand.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         brand.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || brand.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50';
      case 'inactive':
        return 'bg-red-500/20 text-red-400 border-red-500/50';
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50';
      default:
        return 'bg-slate-500/20 text-slate-400 border-slate-500/50';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center">
        <p className="text-red-400 mb-4">오류가 발생했습니다: {error}</p>
        <Button onClick={refetch} variant="outline">
          다시 시도
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">브랜드 관리</h1>
          <p className="text-slate-400 mt-1">브랜드 목록 및 관리</p>
        </div>
        <Button className="bg-cyan-500/20 text-cyan-400 border-cyan-500/50 hover:bg-cyan-500/30">
          <Plus className="w-4 h-4 mr-2" />
          새 브랜드 추가
        </Button>
      </div>

      {/* 검색 및 필터 */}
      <Card className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
        <CardContent className="p-6">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
              <input
                type="text"
                placeholder="브랜드명 또는 설명으로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder:text-slate-400 focus:border-cyan-400/50 focus:outline-none"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:border-cyan-400/50 focus:outline-none"
            >
              <option value="all">전체 상태</option>
              <option value="active">활성</option>
              <option value="inactive">비활성</option>
              <option value="pending">대기중</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* 브랜드 목록 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredBrands.map((brand: Brand) => (
          <Card 
            key={brand.id}
            className="group bg-slate-800/50 border-slate-600 backdrop-blur-xl hover:border-cyan-400/50 transition-all duration-300"
          >
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <CardTitle className="text-white group-hover:text-cyan-400 transition-colors duration-300">
                  {brand.name}
                </CardTitle>
                <Badge className={getStatusColor(brand.status)}>
                  {brand.status === 'active' ? '활성' : 
                   brand.status === 'inactive' ? '비활성' : '대기중'}
                </Badge>
              </div>
              {brand.description && (
                <p className="text-sm text-slate-400">{brand.description}</p>
              )}
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-slate-700/50 rounded-lg">
                  <div className="flex items-center justify-center gap-2 mb-1">
                    <Building2 className="w-4 h-4 text-emerald-400" />
                    <span className="text-sm text-slate-400">매장</span>
                  </div>
                  <p className="text-lg font-bold text-white">{brand.store_count}개</p>
                </div>
                <div className="text-center p-3 bg-slate-700/50 rounded-lg">
                  <div className="flex items-center justify-center gap-2 mb-1">
                    <Building2 className="w-4 h-4 text-purple-400" />
                    <span className="text-sm text-slate-400">직원</span>
                  </div>
                  <p className="text-lg font-bold text-white">{brand.employee_count}명</p>
                </div>
              </div>
              
              <div className="p-3 bg-slate-700/50 rounded-lg">
                <div className="flex items-center justify-center gap-2 mb-1">
                  <Building2 className="w-4 h-4 text-yellow-400" />
                  <span className="text-sm text-slate-400">총 매출</span>
                </div>
                <p className="text-lg font-bold text-white text-center">
                  ₩{brand.total_revenue?.toLocaleString() || '0'}
                </p>
              </div>
              
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm"
                  className="flex-1 border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
                >
                  <Edit className="w-4 h-4 mr-2" />
                  수정
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  className="flex-1 border-red-500/30 text-red-400 hover:bg-red-500/10"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  삭제
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 빈 상태 */}
      {filteredBrands.length === 0 && (
        <Card className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
          <CardContent className="p-12 text-center">
            <Building2 className="w-16 h-16 text-slate-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">브랜드를 찾을 수 없습니다</h3>
            <p className="text-slate-400 mb-4">
              검색어를 변경하거나 새 브랜드를 추가해보세요.
            </p>
            <Button className="bg-cyan-500/20 text-cyan-400 border-cyan-500/50 hover:bg-cyan-500/30">
              <Plus className="h-4 w-4 mr-2" />
              새 브랜드 추가
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 