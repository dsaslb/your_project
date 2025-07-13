import React from 'react';
import SyncStatus from '@/components/SyncStatus';
import PluginManager from '@/components/PluginManager';
import AIAnalytics from '@/components/AIAnalytics';
import RealTimeMonitor from '@/components/RealTimeMonitor';
import SecurityManager from '@/components/SecurityManager';
import DataVisualization from '@/components/DataVisualization';
import MobileOptimizer from '@/components/MobileOptimizer';
import OfflineManager from '@/components/OfflineManager';

export default function AdvancedFeaturesPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            고급 기능 관리
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            실시간 동기화, 오프라인 대응, AI 분석, 플러그인 관리, 보안, 데이터 시각화, 모바일 최적화 등 고급 기능을 확인하고 관리하세요.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* AI 분석 */}
          <div className="lg:col-span-2">
            <AIAnalytics />
          </div>

          {/* 데이터 시각화 */}
          <div className="lg:col-span-2">
            <DataVisualization />
          </div>

          {/* 실시간 모니터링 */}
          <RealTimeMonitor />

          {/* 보안 관리 */}
          <SecurityManager />

          {/* 플러그인 관리 */}
          <PluginManager />

          {/* 오프라인 관리 */}
          <OfflineManager />

          {/* 모바일 최적화 */}
          <div className="lg:col-span-2">
            <MobileOptimizer />
          </div>
        </div>

        {/* 실시간 동기화 상태 */}
        <SyncStatus />
      </div>
    </div>
  );
} 
