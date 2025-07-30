'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  User, 
  Clock, 
  Calendar,
  TrendingUp,
  Activity,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

export default function EmployeeDashboard() {
  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent">
            직원 대시보드
          </h1>
          <p className="text-slate-400 mt-2">내 근무 현황 및 업무 관리</p>
        </div>
        <div className="flex items-center space-x-4">
          <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50">
            출근 중
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
            <CardTitle className="text-sm font-medium text-slate-300">이번 주 근무시간</CardTitle>
            <Clock className="h-4 w-4 text-cyan-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">32시간</div>
            <p className="text-xs text-cyan-400">목표 40시간</p>
          </CardContent>
        </Card>

        <Card className="bg-black/50 border-emerald-500/20 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">완료된 업무</CardTitle>
            <CheckCircle className="h-4 w-4 text-emerald-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">15건</div>
            <p className="text-xs text-emerald-400">이번 주</p>
          </CardContent>
        </Card>

        <Card className="bg-black/50 border-orange-500/20 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">대기 업무</CardTitle>
            <AlertCircle className="h-4 w-4 text-orange-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">3건</div>
            <p className="text-xs text-orange-400">우선순위 높음</p>
          </CardContent>
        </Card>

        <Card className="bg-black/50 border-purple-500/20 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">성과 점수</CardTitle>
            <TrendingUp className="h-4 w-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">85점</div>
            <p className="text-xs text-purple-400">+5점 지난주 대비</p>
          </CardContent>
        </Card>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 오늘 근무표 */}
        <Card className="bg-black/50 border-cyan-500/20 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-cyan-400 flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              오늘 근무표
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
              <div>
                <p className="text-lg font-semibold text-white">09:00 - 18:00</p>
                <p className="text-sm text-slate-400">정규 근무</p>
              </div>
              <Badge className="bg-emerald-500/20 text-emerald-400">출근</Badge>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-slate-800/30 rounded-lg">
                <p className="text-sm text-slate-400">시작 시간</p>
                <p className="text-lg font-semibold text-white">09:00</p>
              </div>
              <div className="text-center p-3 bg-slate-800/30 rounded-lg">
                <p className="text-sm text-slate-400">종료 시간</p>
                <p className="text-lg font-semibold text-white">18:00</p>
              </div>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-800/30 rounded-lg">
              <span className="text-sm text-slate-300">휴식 시간</span>
              <span className="text-sm text-white">12:00 - 13:00 (1시간)</span>
            </div>
          </CardContent>
        </Card>

        {/* 업무 현황 */}
        <Card className="bg-black/50 border-purple-500/20 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-purple-400 flex items-center gap-2">
              <Activity className="h-5 w-5" />
              업무 현황
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-white">재고 정리</p>
                  <p className="text-xs text-slate-400">창고 A 구역</p>
                </div>
                <Badge className="bg-emerald-500/20 text-emerald-400 text-xs">완료</Badge>
              </div>
              <div className="flex items-center justify-between p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-white">고객 응대</p>
                  <p className="text-xs text-slate-400">전화 상담</p>
                </div>
                <Badge className="bg-blue-500/20 text-blue-400 text-xs">진행중</Badge>
              </div>
              <div className="flex items-center justify-between p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-white">매장 청소</p>
                  <p className="text-xs text-slate-400">마감 후</p>
                </div>
                <Badge className="bg-orange-500/20 text-orange-400 text-xs">대기</Badge>
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
              <CheckCircle className="h-4 w-4 mr-2" />
              업무 완료
            </Button>
            <Button className="bg-blue-500/20 text-blue-400 border-blue-500/50 hover:bg-blue-500/30">
              <Clock className="h-4 w-4 mr-2" />
              휴식 시작
            </Button>
            <Button className="bg-purple-500/20 text-purple-400 border-purple-500/50 hover:bg-purple-500/30">
              <Calendar className="h-4 w-4 mr-2" />
              근무표 확인
            </Button>
            <Button className="bg-orange-500/20 text-orange-400 border-orange-500/50 hover:bg-orange-500/30">
              <AlertCircle className="h-4 w-4 mr-2" />
              긴급 보고
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 