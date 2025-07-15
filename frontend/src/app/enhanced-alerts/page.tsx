import React from 'react';
import EnhancedAlertSystem from '../../components/EnhancedAlertSystem';
import PolicyManager from './PolicyManager';

export default function EnhancedAlertsPage() {
  return (
    <div className="container mx-auto p-6">
      {/* 고급 알림 시스템 + 운영 정책 관리 UI */}
      <EnhancedAlertSystem />
      <div className="my-8" />
      <PolicyManager />
    </div>
  );
} 