"use client";
import useUserStore from '@/store/useUserStore';
import { useSearchParams } from 'next/navigation';

export default function BranchAdminPage() {
  const { user } = useUserStore();
  const searchParams = useSearchParams();
  const branchId = searchParams.get('branchId');
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">매장 관리자 페이지</h1>
      <p>현재 역할: <b>{user?.role}</b></p>
      <p>branchId: <b>{branchId}</b></p>
      <div className="mt-4">(여기에 매장 관리 UI가 들어갈 예정입니다)</div>
    </div>
  );
} 