"use client";

import React, { useState } from 'react';
import Link from 'next/link';

export default function RestaurantHierarchyPage() {
  const [currentLevel, setCurrentLevel] = useState<'brand' | 'branch' | 'staff'>('brand');

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* 헤더 */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">레스토랑 계층 관리</h1>
              <p className="text-sm text-gray-500">브랜드 &gt; 매장 &gt; 직원 계층별 관리</p>
            </div>
            <Link href="/" className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
              홈으로
            </Link>
          </div>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">전체 브랜드</h3>
            <p className="text-2xl font-bold">12개</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">전체 매장</h3>
            <p className="text-2xl font-bold">156개</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">전체 직원</h3>
            <p className="text-2xl font-bold">1,234명</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">오늘 매출</h3>
            <p className="text-2xl font-bold">₩45,678,900</p>
          </div>
        </div>

        {/* 탭 네비게이션 */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b">
            <div className="flex">
              <button
                onClick={() => setCurrentLevel('brand')}
                className={`px-6 py-3 font-medium ${
                  currentLevel === 'brand' 
                    ? 'border-b-2 border-blue-500 text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                브랜드 관리
              </button>
              <button
                onClick={() => setCurrentLevel('branch')}
                className={`px-6 py-3 font-medium ${
                  currentLevel === 'branch' 
                    ? 'border-b-2 border-blue-500 text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                매장 관리
              </button>
              <button
                onClick={() => setCurrentLevel('staff')}
                className={`px-6 py-3 font-medium ${
                  currentLevel === 'staff' 
                    ? 'border-b-2 border-blue-500 text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                직원 관리
              </button>
            </div>
          </div>
          <div className="p-6">
            {currentLevel === 'brand' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">브랜드별 관리</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">스타벅스</h4>
                    <p className="text-sm text-gray-600">5개 매장, 45명 직원</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">맥도날드</h4>
                    <p className="text-sm text-gray-600">4개 매장, 38명 직원</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">버거킹</h4>
                    <p className="text-sm text-gray-600">3개 매장, 25명 직원</p>
                  </div>
                </div>
              </div>
            )}
            {currentLevel === 'branch' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">매장별 관리</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">강남점</h4>
                    <p className="text-sm text-gray-600">스타벅스, 12명 직원</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">홍대점</h4>
                    <p className="text-sm text-gray-600">스타벅스, 10명 직원</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">강남점</h4>
                    <p className="text-sm text-gray-600">맥도날드, 15명 직원</p>
                  </div>
                </div>
              </div>
            )}
            {currentLevel === 'staff' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">직원별 관리</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">김철수</h4>
                    <p className="text-sm text-gray-600">매니저, 강남점</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">이영희</h4>
                    <p className="text-sm text-gray-600">바리스타, 강남점</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">박민수</h4>
                    <p className="text-sm text-gray-600">매니저, 홍대점</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 빠른 액션 */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4">빠른 액션</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <button className="border rounded-lg p-4 hover:bg-gray-50">
                <span className="text-sm">새 브랜드 추가</span>
              </button>
              <button className="border rounded-lg p-4 hover:bg-gray-50">
                <span className="text-sm">새 매장 등록</span>
              </button>
              <button className="border rounded-lg p-4 hover:bg-gray-50">
                <span className="text-sm">직원 등록</span>
              </button>
              <button className="border rounded-lg p-4 hover:bg-gray-50">
                <span className="text-sm">성과 리포트</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 