import React from 'react';
import { Metadata } from 'next';
import IoTDashboard from '@/components/IoTDashboard';

export const metadata: Metadata = {
  title: 'IoT 대시보드 | 레스토랑 관리 시스템',
  description: '스마트 레스토랑 IoT 기기 모니터링 및 제어',
};

export default function IoTPage() {
  return (
    <div className="container mx-auto p-6">
      <IoTDashboard />
    </div>
  );
} 