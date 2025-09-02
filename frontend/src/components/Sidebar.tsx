'use client';

import React from 'react';
import Link from 'next/link';
import { useBadges } from '@/store/useBadges';

interface SidebarProps {
  branchId: string; // string으로 변경
  brandId?: string; // string으로 변경
}

export default function Sidebar({ branchId, brandId }: SidebarProps) {
  const { badges, isConnected } = useBadges(branchId);

  return (
    <nav className="bg-white shadow-lg w-64 min-h-screen p-4">
      {/* 연결 상태 표시 */}
      <div className="mb-6 p-3 bg-gray-50 rounded-lg">
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-600">
            {isConnected ? '실시간 연결됨' : '연결 끊김'}
          </span>
        </div>
      </div>

      {/* 메인 메뉴 */}
      <div className="space-y-2">
        {/* 대시보드 */}
        <Link 
          href="/dashboard" 
          className="flex items-center justify-between p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
        >
          <span>📊 대시보드</span>
        </Link>

        {/* 주문 관리 */}
        <Link 
          href="/orders" 
          className="flex items-center justify-between p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
        >
          <span>🛒 주문</span>
          {badges.orders > 0 && (
            <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
              {badges.orders}
            </span>
          )}
        </Link>

        {/* 발주 관리 */}
        <Link 
          href="/purchase-orders" 
          className="flex items-center justify-between p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
        >
          <span>📋 발주</span>
          {badges.purchaseOrders > 0 && (
            <span className="bg-orange-500 text-white text-xs px-2 py-1 rounded-full">
              {badges.purchaseOrders}
            </span>
          )}
        </Link>

        {/* 출퇴근 관리 */}
        <Link 
          href="/attendance" 
          className="flex items-center justify-between p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
        >
          <span>⏰ 출퇴근</span>
          {badges.attendance > 0 && (
            <span className="bg-purple-500 text-white text-xs px-2 py-1 rounded-full">
              {badges.attendance}
            </span>
          )}
        </Link>

        {/* 재고 관리 */}
        <Link 
          href="/inventory" 
          className="flex items-center justify-between p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
        >
          <span>📦 재고</span>
          {badges.inventory > 0 && (
            <span className="bg-yellow-500 text-white text-xs px-2 py-1 rounded-full">
              {badges.inventory}
            </span>
          )}
        </Link>

        {/* 스케줄 관리 */}
        <Link 
          href="/schedule" 
          className="flex items-center justify-between p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
        >
          <span>📅 스케줄</span>
          {badges.schedule > 0 && (
            <span className="bg-indigo-500 text-white text-xs px-2 py-1 rounded-full">
              {badges.schedule}
            </span>
          )}
        </Link>

        {/* 직원 관리 */}
        <Link 
          href="/employees" 
          className="flex items-center justify-between p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
        >
          <span>👥 직원</span>
        </Link>

        {/* 지점 관리 */}
        <Link 
          href="/branches" 
          className="flex items-center justify-between p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
        >
          <span>🏢 지점</span>
        </Link>

        {/* 브랜드 관리 */}
        <Link 
          href="/brands" 
          className="flex items-center justify-between p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
        >
          <span>🏷️ 브랜드</span>
        </Link>

        {/* 업종 관리 */}
        <Link 
          href="/industries" 
          className="flex items-center justify-between p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
        >
          <span>🏭 업종</span>
        </Link>

        {/* 설정 */}
        <Link 
          href="/settings" 
          className="flex items-center justify-between p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
        >
          <span>⚙️ 설정</span>
        </Link>
      </div>

      {/* 배지 설명 */}
      <div className="mt-8 p-3 bg-gray-50 rounded-lg">
        <h3 className="text-sm font-medium text-gray-700 mb-2">배지 색상 의미</h3>
        <div className="space-y-1 text-xs text-gray-600">
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 bg-orange-500 rounded-full"></span>
            <span>발주 대기</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 bg-blue-500 rounded-full"></span>
            <span>주문</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 bg-purple-500 rounded-full"></span>
            <span>출퇴근</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 bg-yellow-500 rounded-full"></span>
            <span>재고</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 bg-indigo-500 rounded-full"></span>
            <span>스케줄</span>
          </div>
        </div>
      </div>
    </nav>
  );
}

// 모바일 사이드바 토글 버튼
export function SidebarToggle({ onToggle }: { onToggle: () => void }) {
  return (
    <button
      onClick={onToggle}
      className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-lg hover:bg-gray-50 transition-colors"
      aria-label="사이드바 토글"
    >
      <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>
  );
}
