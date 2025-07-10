"use client";

import React from 'react';

interface SecurityDashboardProps {
  className?: string;
}

export default function SecurityDashboard({ className = "" }: SecurityDashboardProps) {
  return (
    <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">보안 대시보드</h2>
        <div className="flex items-center space-x-2 text-xs text-gray-500">
          <span>실시간</span>
        </div>
      </div>
      
      <div className="text-center py-8">
        <p className="text-gray-500">보안 대시보드 기능이 임시로 비활성화되었습니다.</p>
        <p className="text-sm text-gray-400 mt-2">빌드 오류 수정 후 다시 활성화됩니다.</p>
      </div>
    </div>
  );
} 