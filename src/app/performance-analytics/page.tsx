import React from 'react';
import PerformanceAnalytics from '@/components/PerformanceAnalytics';

export const metadata = {
  title: '성능 분석 대시보드',
  description: '운영 데이터 기반 성능 분석 및 최적화 제안',
};

const PerformanceAnalyticsPage: React.FC = () => {
  return (
    <div className="container mx-auto py-6">
      <PerformanceAnalytics />
    </div>
  );
};

export default PerformanceAnalyticsPage; 