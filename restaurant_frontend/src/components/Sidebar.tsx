"use client";
import React from 'react';

interface SidebarProps {
  className?: string;
}

export default function Sidebar({ className = "" }: SidebarProps) {
  return (
    <div className={`bg-white border-r border-gray-200 w-64 ${className}`}>
      <div className="p-4">
        <h2 className="text-lg font-semibold text-gray-900">레스토랑 관리</h2>
        <p className="text-sm text-gray-500 mt-1">사이드바가 임시로 비활성화되었습니다.</p>
      </div>
      <div className="p-4">
        <div className="text-center py-8">
          <p className="text-gray-500">빌드 오류 수정 후 다시 활성화됩니다.</p>
          <p className="text-sm text-gray-400 mt-2">현재 기본 기능만 사용 가능합니다.</p>
        </div>
      </div>
    </div>
  );
}
