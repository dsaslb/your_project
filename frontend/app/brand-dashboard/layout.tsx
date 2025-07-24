'use client';

import React from 'react';
import Sidebar from '@/components/Sidebar';

export default function BrandDashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* 사이드바 */}
      <Sidebar />
      
      {/* 메인 콘텐츠 */}
      <div className="flex-1 overflow-auto">
        {children}
      </div>
    </div>
  );
} 