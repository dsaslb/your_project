"use client";
import useUserStore from '@/store/useUserStore';
import { useEffect, useState } from 'react';
import { Dialog } from '@/components/ui/dialog';
import { X } from 'lucide-react';

export default function BrandAdminPage() {
  const { user } = useUserStore();
  const [brands, setBrands] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editBrand, setEditBrand] = useState<any>(null);
  const [form, setForm] = useState<any>({ name: '', description: '', status: 'active' });
  const [submitLoading, setSubmitLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // 목록 fetch
  const fetchBrands = () => {
    setLoading(true);
    setError(null);
    fetch('/api/brands')
      .then(res => res.json())
      .then(data => setBrands(data.brands || []))
      .catch(() => setError('브랜드 목록을 불러오지 못했습니다.'))
      .finally(() => setLoading(false));
  };
  useEffect(fetchBrands, []);

  // 생성/수정 핸들러
  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setSubmitLoading(true);
    setSubmitError(null);
    try {
      const method = editBrand ? 'PUT' : 'POST';
      const url = editBrand ? `/api/brands/${editBrand.id}` : '/api/brands';
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error('저장 실패');
      setModalOpen(false);
      setEditBrand(null);
      setForm({ name: '', description: '', status: 'active' });
      fetchBrands();
    } catch (err) {
      setSubmitError('저장에 실패했습니다.');
    } finally {
      setSubmitLoading(false);
    }
  };

  // 삭제 핸들러
  const handleDelete = async (id: number) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/brands/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('삭제 실패');
      fetchBrands();
    } catch (err) {
      setError('삭제에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 폼 열기/닫기
  const openCreate = () => {
    setEditBrand(null);
    setForm({ name: '', description: '', status: 'active' });
    setModalOpen(true);
  };
  const openEdit = (brand: any) => {
    setEditBrand(brand);
    setForm({ ...brand });
    setModalOpen(true);
  };
  const closeModal = () => {
    setModalOpen(false);
    setEditBrand(null);
    setForm({ name: '', description: '', status: 'active' });
    setSubmitError(null);
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">브랜드 관리자 페이지</h1>
      <p>현재 역할: <b>{user?.role}</b></p>
      <div className="flex justify-between items-center mb-4">
        <span className="text-lg font-semibold">브랜드 목록</span>
        <button className="px-3 py-1 bg-blue-600 text-white rounded" onClick={openCreate}>+ 새 브랜드</button>
      </div>
      {loading && <div className="text-sm text-gray-500 mb-2">로딩 중...</div>}
      {error && <div className="text-sm text-red-500 mb-2">{error}</div>}
      <table className="w-full border text-sm mb-6">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-2">브랜드명</th>
            <th className="p-2">설명</th>
            <th className="p-2">상태</th>
            <th className="p-2">액션</th>
          </tr>
        </thead>
        <tbody>
          {brands.map((b: any) => (
            <tr key={b.id} className="border-t">
              <td className="p-2">{b.name}</td>
              <td className="p-2">{b.description}</td>
              <td className="p-2">{b.status}</td>
              <td className="p-2 flex gap-2">
                <button className="px-2 py-1 bg-yellow-500 text-white rounded" onClick={() => openEdit(b)}>수정</button>
                <button className="px-2 py-1 bg-red-500 text-white rounded" onClick={() => handleDelete(b.id)}>삭제</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {/* 브랜드 생성/수정 모달 */}
      <Dialog open={modalOpen} onOpenChange={closeModal}>
        <div className={`fixed inset-0 z-50 flex items-center justify-center ${modalOpen ? '' : 'hidden'}`}> 
          <div className="bg-white rounded-xl shadow-2xl p-6 min-w-[320px] max-w-md relative animate-fade-in">
            <button className="absolute top-2 right-2 text-gray-400 hover:text-gray-700 text-2xl" onClick={closeModal} aria-label="닫기"><X /></button>
            <h2 className="text-lg font-bold mb-3 text-indigo-700">{editBrand ? '브랜드 수정' : '새 브랜드 추가'}</h2>
            <form onSubmit={handleSubmit} className="space-y-3">
              <input className="w-full border rounded px-2 py-1" placeholder="브랜드명" value={form.name} onChange={e => setForm((f: any) => ({ ...f, name: e.target.value }))} required />
              <input className="w-full border rounded px-2 py-1" placeholder="설명" value={form.description} onChange={e => setForm((f: any) => ({ ...f, description: e.target.value }))} />
              <select className="w-full border rounded px-2 py-1" value={form.status} onChange={e => setForm((f: any) => ({ ...f, status: e.target.value }))}>
                <option value="active">활성</option>
                <option value="inactive">비활성</option>
                <option value="pending">승인대기</option>
              </select>
              {submitError && <div className="text-red-500 text-sm">{submitError}</div>}
              <button type="submit" className="w-full bg-blue-600 text-white rounded py-2 font-semibold mt-2" disabled={submitLoading}>{submitLoading ? '저장 중...' : (editBrand ? '수정' : '등록')}</button>
            </form>
          </div>
        </div>
      </Dialog>
    </div>
  );
} 