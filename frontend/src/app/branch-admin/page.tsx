"use client";

import React, { useState } from 'react';
import Link from 'next/link';

export default function BranchAdminPage() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* 헤더 */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">매장 관리자 대시보드</h1>
              <p className="text-sm text-gray-500">스타벅스 강남점 관리</p>
            </div>
            <div className="flex items-center space-x-4">
              <button className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">
                설정
              </button>
              <Link href="/restaurant/hierarchy" className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                계층 관리
              </Link>
            </div>
          </div>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">전체 직원</h3>
            <p className="text-2xl font-bold">12명</p>
            <p className="text-xs text-gray-500">근무 중인 직원</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">오늘 주문</h3>
            <p className="text-2xl font-bold">150건</p>
            <p className="text-xs text-gray-500">처리된 주문</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">오늘 매출</h3>
            <p className="text-2xl font-bold">₩3,500,000</p>
            <p className="text-xs text-gray-500">일일 매출</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">평균 주문</h3>
            <p className="text-2xl font-bold">₩23,333</p>
            <p className="text-xs text-gray-500">주문당 평균</p>
          </div>
        </div>

        {/* 탭 네비게이션 */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b">
            <div className="flex">
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'overview' 
                    ? 'border-b-2 border-blue-500 text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                개요
              </button>
              <button
                onClick={() => setActiveTab('staff')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'staff' 
                    ? 'border-b-2 border-blue-500 text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                직원 관리
              </button>
              <button
                onClick={() => setActiveTab('orders')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'orders' 
                    ? 'border-b-2 border-blue-500 text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                주문 관리
              </button>
              <button
                onClick={() => setActiveTab('analytics')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'analytics' 
                    ? 'border-b-2 border-blue-500 text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                분석
              </button>
            </div>
          </div>
          <div className="p-6">
            {activeTab === 'overview' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">매장 개요</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">최근 활동</h4>
                    <ul className="space-y-2 text-sm">
                      <li>• 신규 직원 김영희 입사</li>
                      <li>• 오늘 매출 목표 달성 (120%)</li>
                      <li>• 고객 만족도 조사 완료</li>
                    </ul>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">성과 지표</h4>
                    <ul className="space-y-2 text-sm">
                      <li>• 평균 주문 처리 시간: 3분</li>
                      <li>• 고객 만족도: 4.8/5.0</li>
                      <li>• 직원 만족도: 4.5/5.0</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'staff' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">직원 관리</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">김철수</h4>
                    <p className="text-sm text-gray-600">매니저</p>
                    <p className="text-sm text-blue-600">근무 중</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">이영희</h4>
                    <p className="text-sm text-gray-600">바리스타</p>
                    <p className="text-sm text-blue-600">근무 중</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">박민수</h4>
                    <p className="text-sm text-gray-600">서버</p>
                    <p className="text-sm text-blue-600">근무 중</p>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'orders' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">주문 관리</h3>
                <div className="space-y-3">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">오늘 주문 현황</h4>
                    <p className="text-sm text-gray-600">총 150건의 주문이 처리되었습니다.</p>
                    <p className="text-sm text-green-600">평균 처리 시간: 3분</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">인기 메뉴</h4>
                    <p className="text-sm text-gray-600">아메리카노, 카페라떼, 카푸치노</p>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'analytics' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">분석</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">매출 트렌드</h4>
                    <p className="text-sm text-gray-600">이번 주 매출이 지난 주 대비 15% 증가</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">고객 분석</h4>
                    <p className="text-sm text-gray-600">주 고객층: 20-30대 직장인</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 