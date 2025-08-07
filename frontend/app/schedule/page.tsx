'use client';

import React from 'react';

export default function SchedulePage() {
  return (
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          📅 스케줄 관리
        </h1>
        <p className="text-gray-300">
          인력 배치, 출퇴근 관리, AI 분석을 통한 효율적인 스케줄 관리
        </p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-4 mb-8 flex-wrap">
        <button className="px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl">
          + 스케줄 추가
        </button>
        <button className="px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg font-medium hover:from-green-600 hover:to-green-700 transition-all duration-200 shadow-lg hover:shadow-xl">
          🤖 AI 분석
        </button>
        <button className="px-6 py-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg font-medium hover:from-purple-600 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl">
          📊 리포트 생성
        </button>
      </div>

      {/* 기능 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {/* 인력 관리 카드 */}
        <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-400 to-blue-600 rounded-lg flex items-center justify-center mr-4">
              <span className="text-2xl">👥</span>
            </div>
            <h3 className="text-xl font-semibold text-white">인력 관리</h3>
          </div>
          <p className="text-gray-300 mb-4">
            최적화된 인력 배치와 효율적인 스케줄 관리
          </p>
          <div className="flex justify-between items-center">
            <span className="text-green-400 text-sm font-medium">상태: 최적</span>
            <span className="bg-green-500/20 text-green-400 px-2 py-1 rounded text-xs">
              95% 효율성
            </span>
          </div>
        </div>

        {/* 출퇴근 관리 카드 */}
        <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center mr-4">
              <span className="text-2xl">⏰</span>
            </div>
            <h3 className="text-xl font-semibold text-white">출퇴근 관리</h3>
          </div>
          <p className="text-gray-300 mb-4">
            실시간 출퇴근 체크 및 시간 관리 시스템
          </p>
          <div className="flex justify-between items-center">
            <span className="text-yellow-400 text-sm font-medium">상태: 양호</span>
            <span className="bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded text-xs">
              87% 출근률
            </span>
          </div>
        </div>

        {/* AI 분석 카드 */}
        <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-400 to-purple-600 rounded-lg flex items-center justify-center mr-4">
              <span className="text-2xl">🤖</span>
            </div>
            <h3 className="text-xl font-semibold text-white">AI 분석</h3>
          </div>
          <p className="text-gray-300 mb-4">
            AI 기반 스케줄 최적화 및 인사이트 제공
          </p>
          <div className="flex justify-between items-center">
            <span className="text-purple-400 text-sm font-medium">상태: 활성</span>
            <span className="bg-purple-500/20 text-purple-400 px-2 py-1 rounded text-xs">
              AI 준비완료
            </span>
          </div>
        </div>
      </div>

      {/* 통계 대시보드 */}
      <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 mb-8">
        <h2 className="text-2xl font-bold text-white mb-6">성과 대시보드</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-400 mb-2">24</div>
            <div className="text-gray-300 text-sm">활성 직원</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-400 mb-2">87%</div>
            <div className="text-gray-300 text-sm">출근률</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-yellow-400 mb-2">8.2h</div>
            <div className="text-gray-300 text-sm">평균 근무시간</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-400 mb-2">92</div>
            <div className="text-gray-300 text-sm">효율성 점수</div>
          </div>
        </div>
      </div>

      {/* 빠른 액션 */}
      <div className="flex gap-4 justify-center flex-wrap">
        <button className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-cyan-600 text-white rounded-lg font-medium hover:from-cyan-600 hover:to-cyan-700 transition-all duration-200 shadow-lg hover:shadow-xl">
          📅 캘린더 보기
        </button>
        <button className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-lg font-medium hover:from-emerald-600 hover:to-emerald-700 transition-all duration-200 shadow-lg hover:shadow-xl">
          📊 리포트 생성
        </button>
        <button className="px-6 py-3 bg-gradient-to-r from-violet-500 to-violet-600 text-white rounded-lg font-medium hover:from-violet-600 hover:to-violet-700 transition-all duration-200 shadow-lg hover:shadow-xl">
          🤖 AI 분석 실행
        </button>
      </div>
    </div>
  );
}
