'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  BarChart3, 
  Search, 
  Plus, 
  Edit, 
  Trash2,
  Building2,
  Store,
  Users,
  TrendingUp
} from 'lucide-react';

interface Industry {
  id: number;
  name: string;
  code: string;
  description: string;
  icon: string;
  color: string;
  brand_count: number;
  store_count: number;
  employee_count: number;
  total_revenue: number;
  status: 'active' | 'inactive';
  created_at: string;
}

export default function IndustriesPage() {
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    loadIndustries();
  }, []);

  const loadIndustries = async () => {
    try {
      const response = await fetch('/api/admin/industries');
      if (response.ok) {
        const data = await response.json();
        setIndustries(data.industries || []);
      }
    } catch (error) {
      console.error('업종 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredIndustries = industries.filter(industry => {
    const matchesSearch = industry.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         industry.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || industry.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50">활성</Badge>;
      case 'inactive':
        return <Badge className="bg-red-500/20 text-red-400 border-red-500/50">비활성</Badge>;
      default:
        return <Badge className="bg-slate-500/20 text-slate-400 border-slate-500/50">알 수 없음</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent">
            업종 관리
          </h1>
          <p className="text-slate-400 mt-2">업종 목록 및 관리</p>
        </div>
        <Button className="bg-cyan-500/20 text-cyan-400 border-cyan-500/50 hover:bg-cyan-500/30">
          <Plus className="h-4 w-4 mr-2" />
          새 업종 추가
        </Button>
      </div>

      {/* 필터 및 검색 */}
      <Card className="bg-black/50 border-cyan-500/20 backdrop-blur-xl">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="업종명 또는 코드로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-slate-800/50 border-slate-600 text-white"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-md text-white"
            >
              <option value="all">전체 상태</option>
              <option value="active">활성</option>
              <option value="inactive">비활성</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* 업종 목록 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredIndustries.map((industry) => (
          <Card key={industry.id} className="bg-black/50 border-slate-500/20 backdrop-blur-xl hover:border-cyan-500/50 transition-all duration-300">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white flex items-center gap-2">
                  <div 
                    className="w-8 h-8 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: industry.color + '20', border: `1px solid ${industry.color}40` }}
                  >
                    <BarChart3 className="h-4 w-4" style={{ color: industry.color }} />
                  </div>
                  {industry.name}
                </CardTitle>
                {getStatusBadge(industry.status)}
              </div>
              <p className="text-sm text-slate-400">{industry.code}</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-slate-300 text-sm">{industry.description}</p>
              
              {/* 통계 */}
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-emerald-400">
                    <Building2 className="h-4 w-4" />
                    <span className="text-lg font-semibold">{industry.brand_count}</span>
                  </div>
                  <p className="text-xs text-slate-400">브랜드</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-blue-400">
                    <Store className="h-4 w-4" />
                    <span className="text-lg font-semibold">{industry.store_count}</span>
                  </div>
                  <p className="text-xs text-slate-400">매장</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-purple-400">
                    <Users className="h-4 w-4" />
                    <span className="text-lg font-semibold">{industry.employee_count}</span>
                  </div>
                  <p className="text-xs text-slate-400">직원</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-orange-400">
                    <TrendingUp className="h-4 w-4" />
                    <span className="text-lg font-semibold">₩{(industry.total_revenue / 1000000).toFixed(1)}M</span>
                  </div>
                  <p className="text-xs text-slate-400">매출</p>
                </div>
              </div>

              {/* 액션 버튼 */}
              <div className="flex gap-2">
                <Button size="sm" className="flex-1 bg-blue-500/20 text-blue-400 border-blue-500/50 hover:bg-blue-500/30">
                  <Edit className="h-3 w-3 mr-1" />
                  수정
                </Button>
                <Button size="sm" variant="outline" className="border-red-500/50 text-red-400 hover:bg-red-500/10">
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>

              <div className="text-xs text-slate-400">
                생성일: {new Date(industry.created_at).toLocaleDateString('ko-KR')}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredIndustries.length === 0 && (
        <Card className="bg-black/50 border-slate-500/20 backdrop-blur-xl">
          <CardContent className="p-12 text-center">
            <BarChart3 className="h-12 w-12 text-slate-400 mx-auto mb-4" />
            <p className="text-slate-400">업종이 없습니다.</p>
            <Button className="mt-4 bg-cyan-500/20 text-cyan-400 border-cyan-500/50 hover:bg-cyan-500/30">
              <Plus className="h-4 w-4 mr-2" />
              첫 번째 업종 추가
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 