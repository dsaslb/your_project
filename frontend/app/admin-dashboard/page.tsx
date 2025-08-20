'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Building2, 
  Users, 
  Store, 
  TrendingUp,
  Settings,
  Activity,
  Shield,
  Zap,
  RefreshCw
} from 'lucide-react';
import { useDashboardData, useBrands, useIndustries } from '@/hooks/useDashboard';

export default function AdminDashboard() {
  const { stats, loading, error, refetch } = useDashboardData();
  const { brands } = useBrands(1, 5);
  const { industries } = useIndustries(1, 5);

  // 데이터 안전성 확인
  const safeStats = stats || {};
  const safeBrands = brands || [];
  const safeIndustries = industries || [];

  const dashboardStats = [
    {
      label: '총 브랜드',
      value: (safeStats as any).total_brands || 0,
      icon: <Building2 className="w-6 h-6" />,
      color: 'text-cyan-400'
    },
    {
      label: '총 매장',
      value: (safeStats as any).total_stores || 0,
      icon: <Store className="w-6 h-6" />,
      color: 'text-emerald-400'
    },
    {
      label: '총 직원',
      value: (safeStats as any).total_employees || 0,
      icon: <Users className="w-6 h-6" />,
      color: 'text-purple-400'
    },
    {
      label: '총 매출',
      value: `₩${((safeStats as any).total_revenue || 0).toLocaleString()}`,
      icon: <TrendingUp className="w-6 h-6" />,
      color: 'text-yellow-400'
    }
  ];

  return (
    <div className="min-h-screen p-8">
      {/* 헤더 */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Settings className="w-6 h-6" />
            관리자 대시보드
          </h1>
          <p className="text-slate-400 mt-2">전체 시스템 현황 및 관리</p>
        </div>
        
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={refetch}
            disabled={loading}
            className="flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            새로고침
          </Button>
          
          <Button
            variant="outline"
            onClick={() => window.location.href = '/brands'}
            className="flex items-center gap-2"
          >
            <Building2 className="w-4 h-4" />
            브랜드 관리
          </Button>
          
          <Button
            variant="outline"
            onClick={() => window.location.href = '/industries'}
            className="flex items-center gap-2"
          >
            <Store className="w-4 h-4" />
            업종 관리
          </Button>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {dashboardStats.map((stat, index) => (
          <Card key={index} className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">{stat.label}</p>
                  <p className="text-2xl font-bold text-white">{stat.value}</p>
                </div>
                <div className={stat.color}>
                  {stat.icon}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 최근 활동 */}
      <Card className="bg-slate-800/50 border-slate-600 backdrop-blur-xl mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-cyan-400">
            <Activity className="w-5 h-5" />
            최근 활동
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {(safeStats as any).recent_activities?.slice(0, 5).map((activity: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                <div>
                  <p className="text-white">{activity.description}</p>
                  <p className="text-sm text-slate-400">{activity.timestamp}</p>
                </div>
                <Badge className="bg-slate-600 text-slate-300">
                  {activity.type}
                </Badge>
              </div>
            ))}
            {(!(safeStats as any).recent_activities || (safeStats as any).recent_activities.length === 0) && (
              <p className="text-slate-400 text-center py-4">최근 활동이 없습니다.</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 브랜드 및 업종 현황 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-emerald-400">
              <Building2 className="w-5 h-5" />
              브랜드 현황
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {safeBrands.slice(0, 5).map((brand: any) => (
                <div key={brand.id} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                  <div>
                    <p className="text-white font-medium">{brand.name}</p>
                    <p className="text-sm text-slate-400">{brand.store_count}개 매장</p>
                  </div>
                  <Badge className={brand.status === 'active' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}>
                    {brand.status === 'active' ? '활성' : '비활성'}
                  </Badge>
                </div>
              ))}
              {safeBrands.length === 0 && (
                <p className="text-slate-400 text-center py-4">브랜드가 없습니다.</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-purple-400">
              <Store className="w-5 h-5" />
              업종 현황
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {safeIndustries.slice(0, 5).map((industry: any) => (
                <div key={industry.id} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                  <div>
                    <p className="text-white font-medium">{industry.name}</p>
                    <p className="text-sm text-slate-400">{industry.brand_count}개 브랜드</p>
                  </div>
                  <Badge className={industry.status === 'active' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}>
                    {industry.status === 'active' ? '활성' : '비활성'}
                  </Badge>
                </div>
              ))}
              {safeIndustries.length === 0 && (
                <p className="text-slate-400 text-center py-4">업종이 없습니다.</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 시스템 상태 */}
      <Card className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-cyan-400">
            <Shield className="w-5 h-5" />
            시스템 상태
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-emerald-500/10 rounded-lg border border-emerald-500/30">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-emerald-400">백엔드 서버</span>
              </div>
              <p className="text-2xl font-bold text-white">정상</p>
            </div>
            <div className="p-4 bg-blue-500/10 rounded-lg border border-blue-500/30">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-blue-400">데이터베이스</span>
              </div>
              <p className="text-2xl font-bold text-white">온라인</p>
            </div>
            <div className="p-4 bg-purple-500/10 rounded-lg border border-purple-500/30">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-purple-400">AI 시스템</span>
              </div>
              <p className="text-2xl font-bold text-white">활성</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 