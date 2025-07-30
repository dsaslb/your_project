'use client';

import { NotificationCenter } from '@/components/NotificationCenter';
import { MobileBottomNavigation } from '@/components/MobileOptimized';

export default function NotificationsPage() {
  return (
    <div className="container mx-auto p-6 pb-20">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-2">알림 센터</h1>
        <p className="text-slate-400">시스템 알림과 업데이트를 확인하세요</p>
      </div>
      
      <NotificationCenter />
      
      {/* 모바일 하단 네비게이션 */}
      <MobileBottomNavigation />
    </div>
  );
} 