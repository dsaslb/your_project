"use client";
import useUserStore from '@/store/useUserStore';
import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';

function StaffDetail() {
  const searchParams = useSearchParams();
  const staffId = searchParams.get('staffId');
  return (
    <>
      <p>staffId: <b>{staffId}</b></p>
      <div className="mt-4">(여기에 직원 상세/관리 UI가 들어갈 예정입니다)</div>
    </>
  );
}

export default function StaffPage() {
  const { user } = useUserStore();
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">직원 상세 페이지</h1>
      <p>현재 역할: <b>{user?.role}</b></p>
      <Suspense>
        <StaffDetail />
      </Suspense>
    </div>
  );
} 