'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Store, 
  Users, 
  DollarSign, 
  TrendingUp, 
  Activity,
  Package,
  Calendar,
  AlertTriangle
} from 'lucide-react';

export default function StoreDashboard() {
  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent">
            매장 대시보드
          </h1>
          <p className="text-slate-400 mt-2">매장 운영 현황 및 관리</p>
        </div>
        <div className="flex items-center space-x-4">
          <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50">
            운영 중
          </Badge>
          <Button variant="outline" className="border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/10">
            새로고침
          </Button>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-black/50 border-cyan-500/20 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">총 매출</CardTitle>
            <DollarSign className="h-4 w-4 text-emerald-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">₩12,345,678</div>
            <p className="text-xs text-emerald-400">+12.5% 지난달 대비</p>
          </CardContent>
        </Card>

        <Card className="bg-black/50 border-purple-500/20 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">직원 수</CardTitle>
            <Users className="h-4 w-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">24명</div>
            <p className="text-xs text-purple-400">+2명 이번 주</p>
          </CardContent>
        </Card>

        <Card className="bg-black/50 border-blue-500/20 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">주문 수</CardTitle>
            <Package className="h-4 w-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">156건</div>
            <p className="text-xs text-blue-400">오늘 기준</p>
          </CardContent>
        </Card>

        <Card className="bg-black/50 border-orange-500/20 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">재고 알림</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">3건</div>
            <p className="text-xs text-orange-400">발주 필요</p>
          </CardContent>
        </Card>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 실시간 활동 */}
        <Card className="bg-black/50 border-cyan-500/20 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-cyan-400 flex items-center gap-2">
              <Activity className="h-5 w-5" />
              실시간 활동
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                <span className="text-sm text-slate-300">새 주문 접수</span>
              </div>
              <span className="text-xs text-slate-400">2분 전</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                <span className="text-sm text-slate-300">직원 출근</span>
              </div>
              <span className="text-xs text-slate-400">5분 전</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse"></div>
                <span className="text-sm text-slate-300">재고 부족 알림</span>
              </div>
              <span className="text-xs text-slate-400">10분 전</span>
            </div>
          </CardContent>
        </Card>

        {/* 근무표 */}
        <Card className="bg-black/50 border-purple-500/20 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-purple-400 flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              오늘 근무표
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-white">김철수</p>
                <p className="text-xs text-slate-400">매니저</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-white">09:00 - 18:00</p>
                <Badge className="bg-emerald-500/20 text-emerald-400 text-xs">출근</Badge>
              </div>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-white">이영희</p>
                <p className="text-xs text-slate-400">직원</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-white">10:00 - 19:00</p>
                <Badge className="bg-emerald-500/20 text-emerald-400 text-xs">출근</Badge>
              </div>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-white">박민수</p>
                <p className="text-xs text-slate-400">직원</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-white">14:00 - 23:00</p>
                <Badge className="bg-yellow-500/20 text-yellow-400 text-xs">대기</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 빠른 액션 */}
      <Card className="bg-black/50 border-slate-500/20 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-white">빠른 액션</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <Button className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50 hover:bg-emerald-500/30">
              <Package className="h-4 w-4 mr-2" />
              주문 관리
            </Button>
            <Button className="bg-blue-500/20 text-blue-400 border-blue-500/50 hover:bg-blue-500/30">
              <Users className="h-4 w-4 mr-2" />
              직원 관리
            </Button>
            <Button className="bg-purple-500/20 text-purple-400 border-purple-500/50 hover:bg-purple-500/30">
              <Calendar className="h-4 w-4 mr-2" />
              근무표 관리
            </Button>
            <Button className="bg-orange-500/20 text-orange-400 border-orange-500/50 hover:bg-orange-500/30">
              <TrendingUp className="h-4 w-4 mr-2" />
              매출 리포트
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 