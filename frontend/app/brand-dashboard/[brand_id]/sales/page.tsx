// /brand-dashboard/[brand_id]/sales/page.tsx
'use client';
import { useParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import { Dialog } from '@headlessui/react';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import useUserStore from '@/store/useUserStore';
import { toast } from 'react-hot-toast';

// 매출 타입 예시
interface Sale {
  id: string;
  amount: number;
  date: string;
}

export default function BrandSalesPage() {
  // URL에서 brand_id 추출
  const params = useParams();
  const brandId = params?.brand_id as string;
  const [sales, setSales] = useState<Sale[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 매출 등록 모달 상태
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newSaleAmount, setNewSaleAmount] = useState('');
  const [newSaleDate, setNewSaleDate] = useState('');
  const [submitLoading, setSubmitLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { user } = useUserStore();
  const canManage = user && ['admin', 'brand_admin', 'store_manager'].includes(user.role);

  // 브랜드별 매출 목록 불러오기
  useEffect(() => {
    async function fetchSales() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/admin/brand/${brandId}/sales`);
        if (res.ok) {
          const data = await res.json();
          setSales(data.sales || []);
        } else {
          setError('매출 데이터를 불러오지 못했습니다.');
        }
      } catch (e) {
        setError('네트워크 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    }
    if (brandId) fetchSales();
  }, [brandId]);

  // 매출 등록 핸들러
  async function handleAddSale(e: React.FormEvent) {
    e.preventDefault();
    setSubmitLoading(true);
    setSubmitError(null);
    try {
      const res = await fetch(`/api/admin/brand/${brandId}/sales`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          brand_id: brandId,
          amount: Number(newSaleAmount),
          date: newSaleDate,
        }),
      });
      if (res.ok) {
        setIsModalOpen(false);
        setNewSaleAmount('');
        setNewSaleDate('');
        // 등록 후 목록 새로고침
        const data = await res.json();
        setSales(prev => [...prev, data.sale]);
        toast.success('매출 등록 완료!');
      } else {
        setSubmitError('매출 등록에 실패했습니다.');
        toast.error('매출 등록에 실패했습니다.');
      }
    } catch (e) {
      setSubmitError('네트워크 오류가 발생했습니다.');
      toast.error('네트워크 오류가 발생했습니다.');
    } finally {
      setSubmitLoading(false);
    }
  }

  return (
    <ProtectedRoute requiredRoles={['admin', 'brand_admin', 'store_manager']} redirectTo="/admin-dashboard">
      <main className="p-8">
        <h1 className="text-2xl font-bold mb-4" aria-label="브랜드별 매출 목록">매출 목록</h1>
        {canManage ? (
          <button
            tabIndex={0}
            className="mb-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline focus:outline-2 focus:outline-blue-500"
            onClick={() => setIsModalOpen(true)}
            aria-label="매출 등록"
          >
            + 매출 등록
            <span className="sr-only">새 매출을 등록하려면 클릭하세요.</span>
          </button>
        ) : (
          <div className="mb-4 text-red-500">권한이 없습니다. 관리자에게 문의하세요.</div>
        )}
        {/* 매출 등록 모달 */}
        <Dialog open={isModalOpen} onClose={() => setIsModalOpen(false)} className="fixed z-50 inset-0 flex items-center justify-center">
          <Dialog.Overlay className="fixed inset-0 bg-black opacity-30" />
          <div className="relative bg-white rounded p-6 w-full max-w-md mx-auto">
            <Dialog.Title className="text-lg font-bold mb-2">매출 등록</Dialog.Title>
            <form onSubmit={handleAddSale} className="space-y-4">
              <div>
                <label htmlFor="saleAmount" className="block text-sm font-medium">금액(원)</label>
                <input
                  id="saleAmount"
                  type="number"
                  value={newSaleAmount}
                  onChange={e => setNewSaleAmount(e.target.value)}
                  className="w-full border rounded p-2"
                  required
                  aria-required="true"
                  min="0"
                />
              </div>
              <div>
                <label htmlFor="saleDate" className="block text-sm font-medium">날짜</label>
                <input
                  id="saleDate"
                  type="date"
                  value={newSaleDate}
                  onChange={e => setNewSaleDate(e.target.value)}
                  className="w-full border rounded p-2"
                  required
                  aria-required="true"
                />
              </div>
              {submitError && <div className="text-red-500">{submitError}</div>}
              <div className="flex gap-2 justify-end">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 bg-gray-200 rounded">취소</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded" disabled={submitLoading}>
                  {submitLoading ? '등록 중...' : '등록'}
                </button>
              </div>
            </form>
          </div>
        </Dialog>
        {loading ? (
          <div>로딩 중...</div>
        ) : error ? (
          <div className="text-red-500">{error}</div>
        ) : sales.length === 0 ? (
          <div>매출 데이터가 없습니다.</div>
        ) : (
          <ul className="space-y-2">
            {sales.map(sale => (
              <li key={sale.id} className="border rounded p-4 flex flex-col md:flex-row md:items-center md:justify-between">
                <span className="font-semibold">{sale.date}</span>
                <span className="text-sm text-gray-500">{sale.amount.toLocaleString()}원</span>
              </li>
            ))}
          </ul>
        )}
      </main>
    </ProtectedRoute>
  );
} 