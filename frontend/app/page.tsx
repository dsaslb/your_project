"use client";
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomeRedirect() {
  const router = useRouter();
  useEffect(() => {
    // 개발용: 항상 대시보드로 이동
    router.replace('/dashboard');
  }, [router]);
  return null;
} 