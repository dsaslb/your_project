/**
 * 🏠 대시보드 페이지
 * 
 * 실시간 업데이트 위젯이 포함된 메인 대시보드
 */

import React from 'react';
import RealtimeWidget from '../../src/components/RealtimeWidget';

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">🏠 대시보드</h1>
          <p className="text-gray-600 mt-2">실시간 업데이트와 함께하는 비즈니스 현황</p>
        </div>

        {/* 실시간 업데이트 위젯 */}
        <div className="mb-8">
          <RealtimeWidget />
        </div>

        {/* 기존 대시보드 콘텐츠 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* 출퇴근 현황 카드 */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">🕐 출퇴근 현황</h3>
              <span className="text-sm text-gray-500">오늘</span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">출근 인원</span>
                <span className="text-2xl font-bold text-green-600">24</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">퇴근 인원</span>
                <span className="text-2xl font-bold text-red-600">18</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">근무율</span>
                <span className="text-lg font-semibold text-blue-600">75%</span>
              </div>
            </div>
          </div>

          {/* 재고 현황 카드 */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">📦 재고 현황</h3>
              <span className="text-sm text-gray-500">실시간</span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">총 상품</span>
                <span className="text-2xl font-bold text-blue-600">156</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">부족 상품</span>
                <span className="text-2xl font-bold text-red-600">8</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">재고율</span>
                <span className="text-lg font-semibold text-green-600">95%</span>
              </div>
            </div>
          </div>

          {/* 주문 현황 카드 */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">🛒 주문 현황</h3>
              <span className="text-sm text-gray-500">오늘</span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">신규 주문</span>
                <span className="text-2xl font-bold text-blue-600">12</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">처리 중</span>
                <span className="text-2xl font-bold text-yellow-600">8</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">완료</span>
                <span className="text-lg font-semibold text-green-600">15</span>
              </div>
            </div>
          </div>

          {/* 발주 현황 카드 */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">📋 발주 현황</h3>
              <span className="text-sm text-gray-500">이번 주</span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">요청됨</span>
                <span className="text-2xl font-bold text-blue-600">5</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">승인됨</span>
                <span className="text-2xl font-bold text-green-600">3</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">발주됨</span>
                <span className="text-lg font-semibold text-purple-600">2</span>
              </div>
            </div>
          </div>

          {/* 매출 현황 카드 */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">💰 매출 현황</h3>
              <span className="text-sm text-gray-500">이번 달</span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">총 매출</span>
                <span className="text-2xl font-bold text-green-600">₩2.4M</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">전월 대비</span>
                <span className="text-lg font-semibold text-blue-600">+12%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">목표 달성</span>
                <span className="text-lg font-semibold text-green-600">85%</span>
              </div>
            </div>
          </div>

          {/* 시스템 상태 카드 */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">⚙️ 시스템 상태</h3>
              <span className="text-sm text-gray-500">실시간</span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">서버 상태</span>
                <span className="flex items-center">
                  <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                  <span className="text-green-600 font-semibold">정상</span>
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">데이터베이스</span>
                <span className="flex items-center">
                  <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                  <span className="text-green-600 font-semibold">정상</span>
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">실시간 통신</span>
                <span className="flex items-center">
                  <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                  <span className="text-green-600 font-semibold">연결됨</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* 추가 정보 섹션 */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 최근 활동 로그 */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🕒 최근 활동</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">김철수님이 출근했습니다</p>
                  <p className="text-xs text-gray-500">2분 전</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">재고 조사가 완료되었습니다</p>
                  <p className="text-xs text-gray-500">5분 전</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">새로운 발주가 요청되었습니다</p>
                  <p className="text-xs text-gray-500">10분 전</p>
                </div>
              </div>
            </div>
          </div>

          {/* 빠른 액션 */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">⚡ 빠른 액션</h3>
            <div className="grid grid-cols-2 gap-3">
              <button className="p-3 bg-blue-100 hover:bg-blue-200 rounded-lg text-blue-800 font-medium transition-colors">
                📱 모바일 앱 열기
              </button>
              <button className="p-3 bg-green-100 hover:bg-green-200 rounded-lg text-green-800 font-medium transition-colors">
                📊 보고서 생성
              </button>
              <button className="p-3 bg-yellow-100 hover:bg-yellow-200 rounded-lg text-yellow-800 font-medium transition-colors">
                🔔 알림 설정
              </button>
              <button className="p-3 bg-purple-100 hover:bg-purple-200 rounded-lg text-purple-800 font-medium transition-colors">
                ⚙️ 설정
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 