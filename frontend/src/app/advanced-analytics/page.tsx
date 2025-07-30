'use client';

import { AdvancedAnalyticsDashboard } from '@/components/AdvancedAnalytics';
import { MobileBottomNavigation } from '@/components/MobileOptimized';

export default function AdvancedAnalyticsPage() {
  return (
    <div className="container mx-auto p-6 pb-20">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-2">고급 분석</h1>
        <p className="text-slate-400">AI 기반 예측 분석 및 실시간 인사이트를 확인하세요</p>
      </div>
      
      <AdvancedAnalyticsDashboard />
      
      {/* 모바일 하단 네비게이션 */}
      <MobileBottomNavigation />
    </div>
  );
} 