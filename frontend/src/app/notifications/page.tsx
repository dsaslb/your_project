"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Bell, AlertTriangle, Info, CheckCircle, Zap, Target, Award } from 'lucide-react';

export default function NotificationsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 p-8">
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-indigo-400 to-purple-600 rounded-xl flex items-center justify-center">
            <Bell className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
              퀀텀 알림 센터
            </h1>
            <p className="text-slate-300">실시간 알림 관리 시스템</p>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <Card className="bg-gradient-to-br from-red-500/10 to-red-600/10 border-red-500/20 backdrop-blur-xl hover:from-red-500/20 hover:to-red-600/20 transition-all duration-300 group">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-gradient-to-br from-red-500 to-red-600 rounded-xl group-hover:scale-110 transition-transform duration-300">
                <AlertTriangle className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h4 className="text-lg font-semibold text-red-300">재고 부족 알림</h4>
                  <div className="px-2 py-1 bg-red-500/20 rounded-full">
                    <span className="text-xs text-red-300 font-medium">긴급</span>
                  </div>
                </div>
                <p className="text-sm text-red-400 mb-3">우유 재고가 부족합니다. 발주가 필요합니다.</p>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-red-500">2분 전</span>
                  <div className="flex gap-2">
                    <button className="px-3 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-300 text-xs rounded-lg transition-colors duration-200">
                      발주하기
                    </button>
                    <button className="px-3 py-1 bg-slate-500/20 hover:bg-slate-500/30 text-slate-300 text-xs rounded-lg transition-colors duration-200">
                      나중에
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-yellow-500/10 to-yellow-600/10 border-yellow-500/20 backdrop-blur-xl hover:from-yellow-500/20 hover:to-yellow-600/20 transition-all duration-300 group">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-xl group-hover:scale-110 transition-transform duration-300">
                <Bell className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h4 className="text-lg font-semibold text-yellow-300">새로운 주문</h4>
                  <div className="px-2 py-1 bg-yellow-500/20 rounded-full">
                    <span className="text-xs text-yellow-300 font-medium">주문</span>
                  </div>
                </div>
                <p className="text-sm text-yellow-400 mb-3">새로운 주문이 들어왔습니다. #ORD-004</p>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-yellow-500">5분 전</span>
                  <div className="flex gap-2">
                    <button className="px-3 py-1 bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-300 text-xs rounded-lg transition-colors duration-200">
                      확인하기
                    </button>
                    <button className="px-3 py-1 bg-slate-500/20 hover:bg-slate-500/30 text-slate-300 text-xs rounded-lg transition-colors duration-200">
                      무시
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-500/10 to-blue-600/10 border-blue-500/20 backdrop-blur-xl hover:from-blue-500/20 hover:to-blue-600/20 transition-all duration-300 group">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl group-hover:scale-110 transition-transform duration-300">
                <Info className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h4 className="text-lg font-semibold text-blue-300">시스템 업데이트</h4>
                  <div className="px-2 py-1 bg-blue-500/20 rounded-full">
                    <span className="text-xs text-blue-300 font-medium">정보</span>
                  </div>
                </div>
                <p className="text-sm text-blue-400 mb-3">시스템이 성공적으로 업데이트되었습니다.</p>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-blue-500">10분 전</span>
                  <div className="flex gap-2">
                    <button className="px-3 py-1 bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 text-xs rounded-lg transition-colors duration-200">
                      자세히 보기
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500/10 to-green-600/10 border-green-500/20 backdrop-blur-xl hover:from-green-500/20 hover:to-green-600/20 transition-all duration-300 group">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-gradient-to-br from-green-500 to-green-600 rounded-xl group-hover:scale-110 transition-transform duration-300">
                <CheckCircle className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h4 className="text-lg font-semibold text-green-300">매출 목표 달성</h4>
                  <div className="px-2 py-1 bg-green-500/20 rounded-full">
                    <span className="text-xs text-green-300 font-medium">성공</span>
                  </div>
                </div>
                <p className="text-sm text-green-400 mb-3">오늘 매출 목표를 달성했습니다!</p>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-green-500">1시간 전</span>
                  <div className="flex gap-2">
                    <button className="px-3 py-1 bg-green-500/20 hover:bg-green-500/30 text-green-300 text-xs rounded-lg transition-colors duration-200">
                      축하하기
                    </button>
                    <button className="px-3 py-1 bg-slate-500/20 hover:bg-slate-500/30 text-slate-300 text-xs rounded-lg transition-colors duration-200">
                      무시
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500/10 to-purple-600/10 border-purple-500/20 backdrop-blur-xl hover:from-purple-500/20 hover:to-purple-600/20 transition-all duration-300 group">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl group-hover:scale-110 transition-transform duration-300">
                <Award className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h4 className="text-lg font-semibold text-purple-300">성과 달성</h4>
                  <div className="px-2 py-1 bg-purple-500/20 rounded-full">
                    <span className="text-xs text-purple-300 font-medium">성과</span>
                  </div>
                </div>
                <p className="text-sm text-purple-400 mb-3">이번 주 고객 만족도가 목표를 초과 달성했습니다!</p>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-purple-500">2시간 전</span>
                  <div className="flex gap-2">
                    <button className="px-3 py-1 bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 text-xs rounded-lg transition-colors duration-200">
                      보고서 보기
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 