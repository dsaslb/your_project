"use client";

import React, { useState } from 'react';
import Link from 'next/link';

export default function IndustryAdminPage() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* 헤더 */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">업종 관리자 대시보드</h1>
              <p className="text-sm text-gray-500">레스토랑 업종 전체 관리</p>
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
            <h3 className="text-sm font-medium text-gray-500">전체 브랜드</h3>
            <p className="text-2xl font-bold">12개</p>
            <p className="text-xs text-gray-500">활성: 10개</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">전체 매장</h3>
            <p className="text-2xl font-bold">156개</p>
            <p className="text-xs text-gray-500">운영 중인 매장</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">전체 직원</h3>
            <p className="text-2xl font-bold">1,234명</p>
            <p className="text-xs text-gray-500">근무 중인 직원</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500">오늘 매출</h3>
            <p className="text-2xl font-bold">₩45,678,900</p>
            <p className="text-xs text-gray-500">업종 전체 매출</p>
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
                onClick={() => setActiveTab('brands')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'brands' 
                    ? 'border-b-2 border-blue-500 text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                브랜드 관리
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
              <button
                onClick={() => setActiveTab('alerts')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'alerts' 
                    ? 'border-b-2 border-blue-500 text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                알림
              </button>
            </div>
          </div>
          <div className="p-6">
            {activeTab === 'overview' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">업종 개요</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">최근 활동</h4>
                    <ul className="space-y-2 text-sm">
                      <li>• 스타벅스 강남점 매출 증가 (15%)</li>
                      <li>• 맥도날드 신규 매장 오픈</li>
                      <li>• 버거킹 직원 교육 완료</li>
                    </ul>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">성과 지표</h4>
                    <ul className="space-y-2 text-sm">
                      <li>• 평균 매출: ₩3,200,000/매장</li>
                      <li>• 고객 만족도: 4.5/5.0</li>
                      <li>• 직원 이직률: 8%</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'brands' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">브랜드 관리</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">스타벅스</h4>
                    <p className="text-sm text-gray-600">5개 매장, 45명 직원</p>
                    <p className="text-sm text-green-600">활성</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">맥도날드</h4>
                    <p className="text-sm text-gray-600">4개 매장, 38명 직원</p>
                    <p className="text-sm text-green-600">활성</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold">버거킹</h4>
                    <p className="text-sm text-gray-600">3개 매장, 25명 직원</p>
                    <p className="text-sm text-green-600">활성</p>
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
                    <p className="text-sm text-gray-600">이번 달 매출이 지난 달 대비 12% 증가</p>
                  </div>
                  <div className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">인기 브랜드</h4>
                    <p className="text-sm text-gray-600">스타벅스가 가장 높은 매출을 기록</p>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'alerts' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">알림</h3>
                <div className="space-y-3">
                  <div className="border rounded-lg p-4 bg-yellow-50">
                    <h4 className="font-semibold text-yellow-800">매출 경고</h4>
                    <p className="text-sm text-yellow-700">버거킹 홍대점 매출이 목표의 80%에 도달</p>
                  </div>
                  <div className="border rounded-lg p-4 bg-green-50">
                    <h4 className="font-semibold text-green-800">성과 달성</h4>
                    <p className="text-sm text-green-700">스타벅스 강남점이 목표 매출을 초과 달성</p>
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