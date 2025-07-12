"use client";

import React from "react";
import Sidebar from '@/Sidebar';
import { useState } from 'react';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  return (
    <div className="min-h-screen bg-background">
      <div className="flex">
        {/* Sidebar */}
        <Sidebar />
        {/* Main Content */}
        <main className="flex-1 ml-0 lg:ml-64">
          {/* 모바일에서 햄버거 버튼 */}
          <button
            className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white dark:bg-gray-800 rounded-full shadow"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="사이드바 열기"
          >
            <span className="sr-only">사이드바 열기</span>
            <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12" /><line x1="3" y1="6" x2="21" y2="6" /><line x1="3" y1="18" x2="21" y2="18" /></svg>
          </button>
          {children}
        </main>
      </div>
    </div>
  );
} 
