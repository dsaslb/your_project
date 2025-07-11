'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function SuperAdminPage() {
  const router = useRouter();

  useEffect(() => {
    // 백엔드 슈퍼관리자 대시보드로 리다이렉트
    window.location.href = 'http://localhost:5000/super-admin';
  }, []);

  return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
        <p className="text-muted-foreground">슈퍼관리자 대시보드로 이동 중...</p>
      </div>
    </div>
  );
} 