'use client';

import { PerformanceDashboard } from '@/components/PerformanceOptimizer';
import { MobileBottomNavigation } from '@/components/MobileOptimized';

export default function PerformancePage() {
  return (
    <div className="container mx-auto p-6 pb-20">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-2">성능 모니터링</h1>
        <p className="text-slate-400">시스템 성능을 실시간으로 모니터링하고 최적화하세요</p>
      </div>
      
      <PerformanceDashboard />
      
      {/* 모바일 하단 네비게이션 */}
      <MobileBottomNavigation />
    </div>
  );
} 