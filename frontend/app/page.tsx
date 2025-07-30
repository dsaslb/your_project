'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // 메인 페이지 접속 시 dashboard로 자동 리다이렉트
    router.push('/dashboard');
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-black">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-4"></div>
        <h1 className="text-2xl font-bold text-cyan-400 mb-4">
          🚀 퀀텀 시스템
        </h1>
        <p className="text-slate-400">
          대시보드로 이동 중...
        </p>
      </div>
    </div>
  );
} 