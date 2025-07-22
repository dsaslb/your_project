"use client";

import React, { useState } from 'react';
import Link from 'next/link';

export default function StaffPage() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* 헤더 */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">직원 대시보드</h1>
              <p className="text-sm text-gray-500">김철수 - 스타벅스 강남점 매니저</p>
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
            <h3 className="text-sm font-medium text-gray-500">오늘 주문</h3>
            <p className="text-2xl font-bold">25건</p>
            <p className="text-xs text-gray-500">처리한 주문</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">오늘 매출</h3>
            <p className="text-2xl font-bold">₩600,000</p>
            <p className="text-xs text-gray-500">생성한 매출</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">평균 주문</h3>
            <p className="text-2xl font-bold">₩24,000</p>
            <p className="text-xs text-gray-500">주문당 평균</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">근무 시간</h3>
            <p className="text-2xl font-bold">8시간</p>
            <p className="text-xs text-gray-500">오늘 근무</p>
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
                onClick={() => setActiveTab('tasks')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'tasks' 
                    ? 'border-b-2 border-blue-500 text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                업무 관리
              </button>
              <button
                onClick={() => setActiveTab('performance')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'performance' 
                    ? 'border-b-2 border-blue-500 text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                성과
              </button>
            </div>
          </div>
          <div className="p-6">
            {activeTab === 'overview' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">직원 개요</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">개인 정보</h4>
                    <ul className="space-y-2 text-sm">
                      <li>• 이름: 김철수</li>
                      <li>• 직책: 매니저</li>
                      <li>• 소속: 스타벅스 강남점</li>
                      <li>• 입사일: 2023년 3월 15일</li>
                    </ul>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">오늘 업무</h4>
                    <ul className="space-y-2 text-sm">
                      <li>• 매장 운영 관리</li>
                      <li>• 직원 교육 진행</li>
                      <li>• 고객 응대</li>
                      <li>• 재고 확인</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'orders' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">주문 관리</h3>
                <div className="space-y-3">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">오늘 처리한 주문</h4>
                    <p className="text-sm text-gray-600">총 25건의 주문을 처리했습니다.</p>
                    <p className="text-sm text-green-600">평균 처리 시간: 2분 30초</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">인기 메뉴</h4>
                    <p className="text-sm text-gray-600">아메리카노, 카페라떼, 카푸치노</p>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'tasks' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">업무 관리</h3>
                <div className="space-y-3">
                  <div className="border rounded-lg p-4 bg-green-50">
                    <h4 className="font-semibold text-green-800">완료된 업무</h4>
                    <ul className="space-y-1 text-sm text-green-700">
                      <li>• 매장 오픈 준비</li>
                      <li>• 직원 근무표 확인</li>
                      <li>• 재고 점검</li>
                    </ul>
                  </div>
                  <div className="border rounded-lg p-4 bg-yellow-50">
                    <h4 className="font-semibold text-yellow-800">진행 중인 업무</h4>
                    <ul className="space-y-1 text-sm text-yellow-700">
                      <li>• 신입 직원 교육</li>
                      <li>• 고객 만족도 조사</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'performance' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">성과</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">이번 달 성과</h4>
                    <ul className="space-y-2 text-sm">
                      <li>• 매출 목표 달성률: 120%</li>
                      <li>• 고객 만족도: 4.8/5.0</li>
                      <li>• 주문 처리 속도: 상위 10%</li>
                    </ul>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">성과 지표</h4>
                    <ul className="space-y-2 text-sm">
                      <li>• 월 평균 주문: 450건</li>
                      <li>• 월 평균 매출: ₩10,800,000</li>
                      <li>• 고객 재방문률: 85%</li>
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
