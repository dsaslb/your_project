"use client";

import React from 'react';

interface PerformanceMonitorProps {
  className?: string;
}

export default function PerformanceMonitor({ className = "" }: PerformanceMonitorProps) {
  return (
    <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">성능 모니터링</h2>
        <div className="flex items-center space-x-2 text-xs text-gray-500">
          <span>실시간</span>
        </div>
      </div>
      
      <div className="text-center py-8">
        <p className="text-gray-500">성능 모니터링 기능이 임시로 비활성화되었습니다.</p>
        <p className="text-sm text-gray-400 mt-2">빌드 오류 수정 후 다시 활성화됩니다.</p>
      </div>
    </div>
  );
} 