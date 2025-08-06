"use client";

import { useEffect, useState } from 'react'
import { initializePerformanceMonitoring, cleanupPerformanceMonitoring } from '@/utils/performance'
import Sidebar, { SidebarToggle } from '@/components/Sidebar'

// 성능 모니터링 컴포넌트
function PerformanceMonitor() {
  useEffect(() => {
    // 성능 모니터링 초기화
    initializePerformanceMonitoring();

    // 컴포넌트 언마운트 시 정리
    return () => {
      cleanupPerformanceMonitoring();
    };
  }, []);

  return null; // 이 컴포넌트는 UI를 렌더링하지 않음
}

// Google Analytics 스크립트
function GoogleAnalytics() {
  useEffect(() => {
    // Google Analytics 초기화
    if (typeof window !== 'undefined' && process.env.NEXT_PUBLIC_GA_ID) {
      // Google Analytics 4 설정
      (window as any).dataLayer = (window as any).dataLayer || [];
      function gtag(...args: any[]) {
        (window as any).dataLayer.push(args);
      }
      (window as any).gtag = gtag;
      gtag('js', new Date());
      gtag('config', process.env.NEXT_PUBLIC_GA_ID, {
        page_title: document.title,
        page_location: window.location.href,
      });
    }
  }, []);

  return null;
}

// 메인 레이아웃 컴포넌트
export function MainLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 사이드바 */}
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      
      {/* 모바일 토글 버튼 */}
      <SidebarToggle onToggle={() => setSidebarOpen(!sidebarOpen)} />
      
      {/* 메인 컨텐츠 영역 */}
      <div className="lg:ml-64 transition-all duration-300 ease-in-out">
        <main className="min-h-screen">
          {children}
        </main>
      </div>
    </div>
  );
}

export function ClientProviders({ children }: { children: React.ReactNode }) {
  return (
    <>
      {/* 성능 모니터링 */}
      <PerformanceMonitor />
      
      {/* Google Analytics */}
      <GoogleAnalytics />
      
      {/* 메인 레이아웃 */}
      <MainLayout>
        {children}
      </MainLayout>
    </>
  );
} 