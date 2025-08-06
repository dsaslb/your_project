"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart3, TrendingUp, Users, Target, Zap, Award, TrendingDown, Activity } from 'lucide-react';

export default function AnalyticsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-pink-600 rounded-xl flex items-center justify-center">
            <BarChart3 className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              퀀텀 데이터 분석
            </h1>
            <p className="text-slate-300">고급 데이터 분석 및 인사이트</p>
          </div>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-gradient-to-br from-purple-500/10 to-purple-600/10 border-purple-500/20 backdrop-blur-xl hover:from-purple-500/20 hover:to-purple-600/20 transition-all duration-300 group">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-300">총 방문자</CardTitle>
            <div className="p-2 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg group-hover:scale-110 transition-transform duration-300">
              <Users className="h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-400">12,456명</div>
            <div className="flex items-center gap-2 mt-2">
              <TrendingUp className="h-4 w-4 text-green-400" />
              <p className="text-xs text-purple-300">이번 달 방문자</p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-pink-500/10 to-pink-600/10 border-pink-500/20 backdrop-blur-xl hover:from-pink-500/20 hover:to-pink-600/20 transition-all duration-300 group">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-pink-300">전환율</CardTitle>
            <div className="p-2 bg-gradient-to-br from-pink-500 to-pink-600 rounded-lg group-hover:scale-110 transition-transform duration-300">
              <Target className="h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-pink-400">23.5%</div>
            <div className="flex items-center gap-2 mt-2">
              <TrendingUp className="h-4 w-4 text-green-400" />
              <p className="text-xs text-pink-300">방문자 대비 주문율</p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-indigo-500/10 to-indigo-600/10 border-indigo-500/20 backdrop-blur-xl hover:from-indigo-500/20 hover:to-indigo-600/20 transition-all duration-300 group">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-indigo-300">평균 주문</CardTitle>
            <div className="p-2 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg group-hover:scale-110 transition-transform duration-300">
              <TrendingUp className="h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-indigo-400">₩8,500</div>
            <div className="flex items-center gap-2 mt-2">
              <TrendingUp className="h-4 w-4 text-green-400" />
              <p className="text-xs text-indigo-300">주문당 평균</p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-cyan-500/10 to-cyan-600/10 border-cyan-500/20 backdrop-blur-xl hover:from-cyan-500/20 hover:to-cyan-600/20 transition-all duration-300 group">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-cyan-300">재방문율</CardTitle>
            <div className="p-2 bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-lg group-hover:scale-110 transition-transform duration-300">
              <BarChart3 className="h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-cyan-400">67.8%</div>
            <div className="flex items-center gap-2 mt-2">
              <TrendingUp className="h-4 w-4 text-green-400" />
              <p className="text-xs text-cyan-300">고객 재방문율</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 분석 차트 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-700/50 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-slate-200 flex items-center gap-2">
              <Activity className="h-5 w-5" />
              월별 매출 트렌드
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-purple-500/10 to-purple-600/10 rounded-lg border border-purple-500/20">
                <span className="text-sm text-purple-300">1월</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 bg-gray-700 rounded-full h-2">
                    <div className="bg-purple-500 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                  </div>
                  <span className="text-sm font-medium text-purple-300">₩60M</span>
                </div>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-pink-500/10 to-pink-600/10 rounded-lg border border-pink-500/20">
                <span className="text-sm text-pink-300">2월</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 bg-gray-700 rounded-full h-2">
                    <div className="bg-pink-500 h-2 rounded-full animate-pulse" style={{ width: '75%' }}></div>
                  </div>
                  <span className="text-sm font-medium text-pink-300">₩75M</span>
                </div>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-indigo-500/10 to-indigo-600/10 rounded-lg border border-indigo-500/20">
                <span className="text-sm text-indigo-300">3월</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 bg-gray-700 rounded-full h-2">
                    <div className="bg-indigo-500 h-2 rounded-full animate-pulse" style={{ width: '90%' }}></div>
                  </div>
                  <span className="text-sm font-medium text-indigo-300">₩90M</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-700/50 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-slate-200 flex items-center gap-2">
              <Award className="h-5 w-5" />
              고객 세그먼트
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-amber-500/10 to-amber-600/10 rounded-lg border border-amber-500/20">
                <span className="text-sm text-amber-300">VIP 고객</span>
                <div className="flex items-center gap-2">
                  <div className="w-16 bg-gray-700 rounded-full h-2">
                    <div className="bg-amber-500 h-2 rounded-full animate-pulse" style={{ width: '15%' }}></div>
                  </div>
                  <span className="text-sm font-medium text-amber-300">15%</span>
                </div>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-emerald-500/10 to-emerald-600/10 rounded-lg border border-emerald-500/20">
                <span className="text-sm text-emerald-300">일반 고객</span>
                <div className="flex items-center gap-2">
                  <div className="w-16 bg-gray-700 rounded-full h-2">
                    <div className="bg-emerald-500 h-2 rounded-full animate-pulse" style={{ width: '65%' }}></div>
                  </div>
                  <span className="text-sm font-medium text-emerald-300">65%</span>
                </div>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-cyan-500/10 to-cyan-600/10 rounded-lg border border-cyan-500/20">
                <span className="text-sm text-cyan-300">신규 고객</span>
                <div className="flex items-center gap-2">
                  <div className="w-16 bg-gray-700 rounded-full h-2">
                    <div className="bg-cyan-500 h-2 rounded-full animate-pulse" style={{ width: '20%' }}></div>
                  </div>
                  <span className="text-sm font-medium text-cyan-300">20%</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 