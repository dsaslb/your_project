import React from 'react';
import AlertManagement from '@/components/AlertManagement'; // pyright: ignore

export const metadata = {
  title: '알림 관리 대시보드',
  description: '알림 로그, 통계, 설정 관리',
};

const AlertManagementPage: React.FC = () => {
  return (
    <div className="container mx-auto py-6">
      <AlertManagement />
    </div>
  );
};

export default AlertManagementPage; 