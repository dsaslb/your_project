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
            <h3 className="text-sm font-medium text-gray-500">오늘 매출</h3>
            <p className="text-2xl font-bold">₩2,456,800</p>
            <p className="text-xs text-gray-500">목표 대비 105%</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">오늘 주문</h3>
            <p className="text-2xl font-bold">289건</p>
            <p className="text-xs text-gray-500">평균 ₩8,500</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">근무 직원</h3>
            <p className="text-2xl font-bold">8명</p>
            <p className="text-xs text-gray-500">총 12명 중</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">고객 만족도</h3>
            <p className="text-2xl font-bold">4.8/5.0</p>
            <p className="text-xs text-gray-500">오늘 평가</p>
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
                onClick={() => setActiveTab('employees')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'employees' 
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
                onClick={() => setActiveTab('inventory')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'inventory' 
                    ? 'border-b-2 border-blue-500 text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                재고 관리
              </button>
            </div>
          </div>
          <div className="p-6">
            {activeTab === 'overview' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">매장 개요</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">오늘 현황</h4>
                    <ul className="space-y-2 text-sm">
                      <li>• 오픈: 07:00</li>
                      <li>• 마감 예정: 23:00</li>
                      <li>• 현재 대기: 3팀</li>
                      <li>• 평균 대기시간: 8분</li>
                    </ul>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">성과 지표</h4>
                    <ul className="space-y-2 text-sm">
                      <li>• 시간당 매출: ₩245,680</li>
                      <li>• 고객 만족도: 4.8/5.0</li>
                      <li>• 직원 효율성: 92%</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'employees' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">직원 관리</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">김철수 (매니저)</h4>
                    <p className="text-sm text-gray-600">근무시간: 09:00-18:00</p>
                    <p className="text-sm text-green-600">근무 중</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">이영희 (바리스타)</h4>
                    <p className="text-sm text-gray-600">근무시간: 07:00-16:00</p>
                    <p className="text-sm text-green-600">근무 중</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">박민수 (바리스타)</h4>
                    <p className="text-sm text-gray-600">근무시간: 12:00-21:00</p>
                    <p className="text-sm text-green-600">근무 중</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">정수진 (서버)</h4>
                    <p className="text-sm text-gray-600">근무시간: 10:00-19:00</p>
                    <p className="text-sm text-green-600">근무 중</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">최지원 (서버)</h4>
                    <p className="text-sm text-gray-600">근무시간: 14:00-23:00</p>
                    <p className="text-sm text-green-600">근무 중</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">김미영 (바리스타)</h4>
                    <p className="text-sm text-gray-600">근무시간: 16:00-01:00</p>
                    <p className="text-sm text-green-600">근무 중</p>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'orders' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">주문 관리</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">실시간 주문</h4>
                    <ul className="space-y-2 text-sm">
                      <li>• #1234 아메리카노 2잔 - 준비 중</li>
                      <li>• #1235 카페라떼 1잔 - 완료</li>
                      <li>• #1236 카푸치노 3잔 - 대기 중</li>
                    </ul>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">주문 통계</h4>
                    <ul className="space-y-2 text-sm">
                      <li>• 오늘 총 주문: 289건</li>
                      <li>• 평균 주문 금액: ₩8,500</li>
                      <li>• 인기 메뉴: 아메리카노</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'inventory' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">재고 관리</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">재고 현황</h4>
                    <ul className="space-y-2 text-sm">
                      <li>• 원두: 15kg (충분)</li>
                      <li>• 우유: 8L (보충 필요)</li>
                      <li>• 시럽: 3L (충분)</li>
                      <li>• 컵: 200개 (충분)</li>
                    </ul>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">발주 예정</h4>
                    <ul className="space-y-2 text-sm">
                      <li>• 우유 10L - 내일 오전</li>
                      <li>• 원두 20kg - 다음 주</li>
                      <li>• 컵 500개 - 다음 주</li>
                    </ul>
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