import React from 'react';
import AdvancedAIDashboard from '@/components/AdvancedAIDashboard';

export const metadata = {
  title: '고급 AI 분석 - Your Program',
  description: '엔터프라이즈급 AI 분석 및 예측 시스템',
};

export default function AdvancedAIPage() {
  return (
    <div className="container mx-auto py-6">
      <AdvancedAIDashboard />
    </div>
  );
} 