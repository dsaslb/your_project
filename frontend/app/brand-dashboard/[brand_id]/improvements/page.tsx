// /brand-dashboard/[brand_id]/improvements/page.tsx
'use client';
import { useParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import { Dialog } from '@headlessui/react';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import useUserStore from '@/store/useUserStore';
import { toast } from 'react-hot-toast';

// 개선요청 타입 예시
interface Improvement {
  id: string;
  title: string;
  status: string;
  created_at: string;
}

export default function BrandImprovementsPage() {
  // URL에서 brand_id 추출
  const params = useParams();
  const brandId = params?.brand_id as string;
  const [improvements, setImprovements] = useState<Improvement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 개선요청 등록 모달 상태
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newImprovementTitle, setNewImprovementTitle] = useState('');
  const [submitLoading, setSubmitLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { user } = useUserStore();
  const canManage = user && ['admin', 'brand_admin', 'store_manager'].includes(user.role);

  // 브랜드별 개선요청 목록 불러오기
  useEffect(() => {
    async function fetchImprovements() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/admin/brand/${brandId}/improvements`);
        if (res.ok) {
          const data = await res.json();
          setImprovements(data.improvements || []);
        } else {
          setError('개선요청 목록을 불러오지 못했습니다.');
        }
      } catch (e) {
        setError('네트워크 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    }
    if (brandId) fetchImprovements();
  }, [brandId]);

  // 개선요청 등록 핸들러
  async function handleAddImprovement(e: React.FormEvent) {
    e.preventDefault();
    setSubmitLoading(true);
    setSubmitError(null);
    try {
      const res = await fetch(`/api/admin/brand/${brandId}/improvements`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          brand_id: brandId,
          title: newImprovementTitle,
        }),
      });
      if (res.ok) {
        setIsModalOpen(false);
        setNewImprovementTitle('');
        // 등록 후 목록 새로고침
        const data = await res.json();
        setImprovements(prev => [...prev, data.improvement]);
        toast.success('개선요청 등록 완료!');
      } else {
        setSubmitError('개선요청 등록에 실패했습니다.');
        toast.error('개선요청 등록에 실패했습니다.');
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
        <h1 className="text-2xl font-bold mb-4" aria-label="브랜드별 개선요청 목록">개선요청 목록</h1>
        {canManage ? (
          <button
            tabIndex={0}
            className="mb-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline focus:outline-2 focus:outline-blue-500"
            aria-label="개선요청 등록"
          >
            + 개선요청 등록
            <span className="sr-only">새 개선요청을 등록하려면 클릭하세요.</span>
          </button>
        ) : (
          <div className="mb-4 text-red-500">권한이 없습니다. 관리자에게 문의하세요.</div>
        )}
        {/* 개선요청 등록 모달 */}
        <Dialog open={isModalOpen} onClose={() => setIsModalOpen(false)} className="fixed z-50 inset-0 flex items-center justify-center">
          <Dialog.Overlay className="fixed inset-0 bg-black opacity-30" />
          <div className="relative bg-white rounded p-6 w-full max-w-md mx-auto">
            <Dialog.Title className="text-lg font-bold mb-2">개선요청 등록</Dialog.Title>
            <form onSubmit={handleAddImprovement} className="space-y-4">
              <div>
                <label htmlFor="improvementTitle" className="block text-sm font-medium">제목</label>
                <input
                  id="improvementTitle"
                  type="text"
                  value={newImprovementTitle}
                  onChange={e => setNewImprovementTitle(e.target.value)}
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
        ) : improvements.length === 0 ? (
          <div>개선요청이 없습니다.</div>
        ) : (
          <ul className="space-y-2">
            {improvements.map(impr => (
              <li key={impr.id} className="border rounded p-4 flex flex-col md:flex-row md:items-center md:justify-between">
                <span className="font-semibold">{impr.title}</span>
                <span className="text-sm text-gray-500">{impr.status}</span>
                <span className="ml-2 text-xs text-gray-400">{impr.created_at}</span>
              </li>
            ))}
          </ul>
        )}
      </main>
    </ProtectedRoute>
  );
} 