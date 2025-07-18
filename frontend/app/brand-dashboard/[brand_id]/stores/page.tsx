// /brand-dashboard/[brand_id]/stores/page.tsx
'use client';
import { useParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import { Dialog } from '@headlessui/react';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import useUserStore from '@/store/useUserStore';
import Toast from '@/components/ui/Toast';

// 매장 타입 예시
interface Store {
  id: string;
  name: string;
  address: string;
  status: string;
}

export default function BrandStoresPage() {
  // URL에서 brand_id 추출
  const params = useParams();
  const brandId = params?.brand_id as string;
  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 매장 등록 모달 상태
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newStoreName, setNewStoreName] = useState('');
  const [newStoreAddress, setNewStoreAddress] = useState('');
  const [submitLoading, setSubmitLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { user } = useUserStore();
  const canManage = user && ['admin', 'brand_admin', 'store_manager'].includes(user.role);

  // 브랜드별 매장 목록 불러오기
  useEffect(() => {
    async function fetchStores() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/admin/stores?brand_id=${brandId}`);
        if (res.ok) {
          const data = await res.json();
          setStores(data.stores || []);
        } else {
          setError('매장 목록을 불러오지 못했습니다.');
        }
      } catch (e) {
        setError('네트워크 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    }
    if (brandId) fetchStores();
  }, [brandId]);

  // 매장 등록 핸들러
  async function handleAddStore(e: React.FormEvent) {
    e.preventDefault();
    setSubmitLoading(true);
    setSubmitError(null);
    try {
      const res = await fetch('/api/admin/stores', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          brand_id: brandId,
          name: newStoreName,
          address: newStoreAddress,
        }),
      });
      if (res.ok) {
        setIsModalOpen(false);
        setNewStoreName('');
        setNewStoreAddress('');
        // 등록 후 목록 새로고침
        const data = await res.json();
        setStores(prev => [...prev, data.store]);
        Toast.success('매장 등록 완료!');
      } else {
        setSubmitError('매장 등록에 실패했습니다.');
        Toast.error('매장 등록에 실패했습니다.');
      }
    } catch (e) {
      setSubmitError('네트워크 오류가 발생했습니다.');
      Toast.error('네트워크 오류가 발생했습니다.');
    } finally {
      setSubmitLoading(false);
    }
  }

  return (
    <ProtectedRoute requiredRoles={['admin', 'brand_admin', 'store_manager']} redirectTo="/admin-dashboard">
      <main className="p-8">
        <h1 className="text-2xl font-bold mb-4" aria-label="브랜드별 매장 목록">매장 목록</h1>
        {canManage ? (
          <button
            tabIndex={0}
            className="mb-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline focus:outline-2 focus:outline-blue-500"
            onClick={() => setIsModalOpen(true)}
            aria-label="매장 등록"
          >
            + 매장 등록
            <span className="sr-only">새 매장을 등록하려면 클릭하세요.</span>
          </button>
        ) : (
          <div className="mb-4 text-red-500">권한이 없습니다. 관리자에게 문의하세요.</div>
        )}
        {/* 매장 등록 모달 */}
        <Dialog open={isModalOpen} onClose={() => setIsModalOpen(false)} className="fixed z-50 inset-0 flex items-center justify-center">
          <Dialog.Overlay className="fixed inset-0 bg-black opacity-30" />
          <div className="relative bg-white rounded p-6 w-full max-w-md mx-auto">
            <Dialog.Title className="text-lg font-bold mb-2">매장 등록</Dialog.Title>
            <form onSubmit={handleAddStore} className="space-y-4">
              <div>
                <label htmlFor="storeName" className="block text-sm font-medium">매장명</label>
                <input
                  id="storeName"
                  type="text"
                  value={newStoreName}
                  onChange={e => setNewStoreName(e.target.value)}
                  className="w-full border rounded p-2"
                  required
                  aria-required="true"
                />
              </div>
              <div>
                <label htmlFor="storeAddress" className="block text-sm font-medium">주소</label>
                <input
                  id="storeAddress"
                  type="text"
                  value={newStoreAddress}
                  onChange={e => setNewStoreAddress(e.target.value)}
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
        ) : stores.length === 0 ? (
          <div>매장이 없습니다.</div>
        ) : (
          <ul className="space-y-2">
            {stores.map(store => (
              <li key={store.id} className="border rounded p-4 flex flex-col md:flex-row md:items-center md:justify-between">
                <span className="font-semibold">{store.name}</span>
                <span className="text-sm text-gray-500">{store.address}</span>
                <span className={`ml-2 text-xs ${store.status === 'active' ? 'text-green-600' : 'text-gray-400'}`}>{store.status === 'active' ? '운영중' : '비활성'}</span>
              </li>
            ))}
          </ul>
        )}
      </main>
    </ProtectedRoute>
  );
} 