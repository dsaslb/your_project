'use client';

import React from 'react';
import Link from 'next/link';
import { Building2, Store, Users, User, Settings, ActivitySquare, Link2 } from 'lucide-react';

export default function Navigation() {
  return (
    <nav className="fixed top-0 left-0 h-screen w-56 bg-white shadow flex flex-col gap-2 p-4 z-40">
      {/* 로고/타이틀 */}
      <div className="mb-6 text-xl font-bold text-blue-700">멀티테넌시<br/>관리 시스템</div>
      {/* 업종별 관리자 대시보드(최상단) */}
      {/* 계층별 대시보드 버튼 */}
      <div className="flex flex-col gap-2 mb-4">
        <Link href="/admin-dashboard" className="flex items-center gap-2 px-3 py-2 rounded bg-blue-100 hover:bg-blue-200 font-semibold text-blue-800">
          <Building2 className="w-5 h-5" /> Admin 대시보드
        </Link>
        <Link href="/brand-dashboard/1" className="flex items-center gap-2 px-3 py-2 rounded bg-green-100 hover:bg-green-200 font-semibold text-green-800">
          <Store className="w-5 h-5" /> 브랜드 대시보드
        </Link>
        <Link href="/store-dashboard" className="flex items-center gap-2 px-3 py-2 rounded bg-yellow-100 hover:bg-yellow-200 font-semibold text-yellow-800">
          <Users className="w-5 h-5" /> 매장 대시보드
        </Link>
        <Link href="/employee-dashboard" className="flex items-center gap-2 px-3 py-2 rounded bg-purple-100 hover:bg-purple-200 font-semibold text-purple-800">
          <User className="w-5 h-5" /> 직원 대시보드
        </Link>
      </div>
      {/* 설정, 실시간 모니터링, 연동 상태 확인 */}
      <Link href="/industry-admin/settings" className="flex items-center gap-2 px-3 py-2 rounded bg-gray-100 hover:bg-gray-200 font-semibold text-gray-800">
        <Settings className="w-5 h-5" /> 설정
      </Link>
      <Link href="/industry-admin/monitoring" className="flex items-center gap-2 px-3 py-2 rounded bg-pink-100 hover:bg-pink-200 font-semibold text-pink-800">
        <ActivitySquare className="w-5 h-5" /> 실시간 모니터링
      </Link>
      <Link href="/industry-admin/integration-status" className="flex items-center gap-2 px-3 py-2 rounded bg-teal-100 hover:bg-teal-200 font-semibold text-teal-800">
        <Link2 className="w-5 h-5" /> 연동 상태 확인
      </Link>
    </nav>
  );
} 