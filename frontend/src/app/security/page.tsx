"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Shield, Lock, Eye, AlertTriangle, Zap, Target, Award, CheckCircle } from 'lucide-react';

export default function SecurityPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-slate-400 to-slate-600 rounded-xl flex items-center justify-center">
            <Shield className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-slate-400 to-slate-300 bg-clip-text text-transparent">
              퀀텀 보안 센터
            </h1>
            <p className="text-slate-300">보안 관리 및 모니터링 시스템</p>
          </div>
        </div>
      </div>

      {/* 보안 상태 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card className="bg-gradient-to-br from-green-500/10 to-green-600/10 border-green-500/20 backdrop-blur-xl hover:from-green-500/20 hover:to-green-600/20 transition-all duration-300 group">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-green-300">시스템 보안</CardTitle>
            <div className="p-2 bg-gradient-to-br from-green-500 to-green-600 rounded-lg group-hover:scale-110 transition-transform duration-300">
              <Shield className="h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-400">안전</div>
            <div className="flex items-center gap-2 mt-2">
              <CheckCircle className="h-4 w-4 text-green-400" />
              <p className="text-xs text-green-300">모든 보안 체크 통과</p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-500/10 to-blue-600/10 border-blue-500/20 backdrop-blur-xl hover:from-blue-500/20 hover:to-blue-600/20 transition-all duration-300 group">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-300">접속 기록</CardTitle>
            <div className="p-2 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg group-hover:scale-110 transition-transform duration-300">
              <Eye className="h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-400">156회</div>
            <div className="flex items-center gap-2 mt-2">
              <Eye className="h-4 w-4 text-blue-400" />
              <p className="text-xs text-blue-300">오늘 접속 횟수</p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-yellow-500/10 to-yellow-600/10 border-yellow-500/20 backdrop-blur-xl hover:from-yellow-500/20 hover:to-yellow-600/20 transition-all duration-300 group">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-yellow-300">보안 경고</CardTitle>
            <div className="p-2 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-lg group-hover:scale-110 transition-transform duration-300">
              <AlertTriangle className="h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-yellow-400">2건</div>
            <div className="flex items-center gap-2 mt-2">
              <AlertTriangle className="h-4 w-4 text-yellow-400" />
              <p className="text-xs text-yellow-300">처리 대기 중</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 보안 설정 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-700/50 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-slate-200 flex items-center gap-2">
              <Lock className="h-5 w-5" />
              보안 설정
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gradient-to-r from-green-500/10 to-green-600/10 rounded-lg border border-green-500/20">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-400" />
                  <span className="text-sm text-green-300">2단계 인증</span>
                </div>
                <input type="checkbox" defaultChecked className="rounded bg-green-500/20 border-green-500/50" />
              </div>
              <div className="flex items-center justify-between p-3 bg-gradient-to-r from-green-500/10 to-green-600/10 rounded-lg border border-green-500/20">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-400" />
                  <span className="text-sm text-green-300">자동 로그아웃</span>
                </div>
                <input type="checkbox" defaultChecked className="rounded bg-green-500/20 border-green-500/50" />
              </div>
              <div className="flex items-center justify-between p-3 bg-gradient-to-r from-green-500/10 to-green-600/10 rounded-lg border border-green-500/20">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-4 w-4 text-green-400" />
                  <span className="text-sm text-green-300">로그인 알림</span>
                </div>
                <input type="checkbox" defaultChecked className="rounded bg-green-500/20 border-green-500/50" />
              </div>
              <div className="flex items-center justify-between p-3 bg-gradient-to-r from-slate-500/10 to-slate-600/10 rounded-lg border border-slate-500/20">
                <div className="flex items-center gap-3">
                  <Lock className="h-4 w-4 text-slate-400" />
                  <span className="text-sm text-slate-300">IP 제한</span>
                </div>
                <input type="checkbox" className="rounded bg-slate-500/20 border-slate-500/50" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-700/50 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-slate-200 flex items-center gap-2">
              <Eye className="h-5 w-5" />
              최근 접속 기록
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-blue-500/10 to-blue-600/10 rounded-lg border border-blue-500/20">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-sm text-blue-300">192.168.1.100</span>
                </div>
                <span className="text-xs text-blue-400">2분 전</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-blue-500/10 to-blue-600/10 rounded-lg border border-blue-500/20">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-sm text-blue-300">192.168.1.101</span>
                </div>
                <span className="text-xs text-blue-400">5분 전</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-yellow-500/10 to-yellow-600/10 rounded-lg border border-yellow-500/20">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                  <span className="text-sm text-yellow-300">192.168.1.102</span>
                </div>
                <span className="text-xs text-yellow-400">10분 전</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-blue-500/10 to-blue-600/10 rounded-lg border border-blue-500/20">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-sm text-blue-300">192.168.1.103</span>
                </div>
                <span className="text-xs text-blue-400">15분 전</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 