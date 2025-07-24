import React, { useEffect, useState } from 'react';
import { useToast } from '../../components/GlobalToast';
import { useI18n } from '../../components/i18n';
import useUserStore from '@/store/useUserStore';
import { toast } from 'sonner';
import { saveAs } from 'file-saver';
import LanguageSwitcher from '../../components/LanguageSwitcher';

interface Brand {
  id: number;
  name: string;
  description?: string;
  created_at?: string;
}

const BrandList: React.FC = () => {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [perPage] = useState(10);
  const [q, setQ] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { showToast } = useToast();
  const { t } = useI18n();
  const [selected, setSelected] = useState<Brand | null>(null);
  const [editMode, setEditMode] = useState<'create' | 'edit' | null>(null);
  const [profileOpen, setProfileOpen] = useState(false);
  const [profileBrand, setProfileBrand] = useState<Brand | null>(null);
  const { user } = useUserStore();
  // 권한별 액션 제한(더 세밀하게)
  const canEdit = user && (user.role === 'admin' || user.role === 'brand_admin');
  const [wsStatus, setWsStatus] = React.useState<'connected' | 'disconnected' | 'connecting'>('connecting');
  const [announcements, setAnnouncements] = React.useState<any[]>([]);
  // 실시간 동기화: WebSocket 연결
  React.useEffect(() => {
    setWsStatus('connecting');
    const ws = new WebSocket('wss://yourserver/ws/brands');
    ws.onopen = () => setWsStatus('connected');
    ws.onclose = () => setWsStatus('disconnected');
    ws.onerror = () => setWsStatus('disconnected');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (["brand_created", "brand_updated", "brand_deleted"].includes(data.type)) {
        fetchBrands();
        // 실시간 알림/토스트
        let msg = '';
        if (data.type === 'brand_created') msg = `${data.user || '누군가'}님이 브랜드 "${data.target?.name || ''}"을(를) 추가했습니다.`;
        if (data.type === 'brand_updated') msg = `${data.user || '누군가'}님이 브랜드 "${data.target?.name || ''}"을(를) 수정했습니다.`;
        if (data.type === 'brand_deleted') msg = `${data.user || '누군가'}님이 브랜드 "${data.target?.name || ''}"을(를) 삭제했습니다.`;
        if (msg) toast(msg, { icon: '🔔' });
      }
    };
    return () => ws.close();
  }, []);

  // 실시간 공지사항/피드백 WebSocket 연동
  React.useEffect(() => {
    const ws = new WebSocket('wss://yourserver/ws/announcements');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'announcement') {
        setAnnouncements((prev) => [data, ...prev].slice(0, 10));
        toast(`새 공지: ${data.title || data.message || ''}`, { icon: '📢' });
      }
      if (data.type === 'feedback') {
        toast(`새 피드백: ${data.user || '익명'} - ${data.message || ''}`, { icon: '💬' });
      }
    };
    return () => ws.close();
  }, []);

  const fetchBrands = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        q,
        page: String(page),
        per_page: String(perPage),
      });
      const res = await fetch(`/api/admin/brands?${params.toString()}`);
      const data = await res.json();
      setBrands(data.brands || []);
      setTotal(data.total || 0);
    } catch (e) {
      setError('브랜드 목록을 불러오지 못했습니다.');
      showToast('브랜드 목록을 불러오지 못했습니다.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBrands();
    // eslint-disable-next-line
  }, [q, page]);

  const handleDelete = async (id: number) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return;
    try {
      const res = await fetch(`/api/admin/brands/${id}`, { method: 'DELETE' });
      if (res.ok) {
        showToast('삭제되었습니다.', 'success');
        fetchBrands();
      } else {
        showToast('삭제 실패', 'error');
      }
    } catch {
      showToast('삭제 실패', 'error');
    }
  };

  const handleEdit = (brand: Brand) => {
    setSelected(brand);
    setEditMode('edit');
  };

  const handleCreate = () => {
    setSelected(null);
    setEditMode('create');
  };

  const handleSave = async (data: any) => {
    try {
      await (editMode === 'edit' ? updateBrand(data) : createBrand(data));
      setEditMode(null);
      fetchBrands();
      toast.success(editMode === 'edit' ? '브랜드 수정 완료!' : '브랜드 등록 완료!');
    } catch (err) {
      toast.error('저장에 실패했습니다.');
    }
  };

  const handleProfile = (brand: Brand) => {
    setProfileBrand(brand);
    setProfileOpen(true);
  };
  const closeProfile = () => {
    setProfileOpen(false);
    setProfileBrand(null);
  };

  // CSV 내보내기
  const exportCSV = () => {
    const header = ['ID', '이름', '설명', '상태', '등록일', '관리자'];
    const rows = brands.map(b => [b.id, b.name, b.description, b.status || '', b.created_at || '', b.admin_name || '']);
    const csv = [header, ...rows].map(r => r.map(x => `"${(x ?? '').toString().replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, 'brands.csv');
  };

  return (
    <>
      <div className="flex justify-end items-center p-2 bg-white shadow mb-2 gap-2">
        <span className={`text-xs px-2 py-1 rounded ${wsStatus === 'connected' ? 'bg-green-100 text-green-700' : wsStatus === 'connecting' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}
          aria-live="polite" aria-label="실시간 동기화 상태">
          {wsStatus === 'connected' ? '동기화됨' : wsStatus === 'connecting' ? '동기화 중...' : '동기화 끊김'}
        </span>
        <LanguageSwitcher />
      </div>
      <div className="p-4 max-w-3xl mx-auto">
        <div className="flex justify-between items-center mb-2">
          <span className="text-md font-semibold">{t('브랜드 목록')}</span>
          <div className="flex gap-2">
            <button className="px-3 py-1 bg-blue-600 text-white rounded" onClick={() => setEditMode('create')} aria-label="새 브랜드 등록">+ {t('새 브랜드')}</button>
            <button className="px-3 py-1 bg-green-600 text-white rounded" onClick={exportCSV} aria-label="CSV 내보내기">{t('CSV 내보내기')}</button>
          </div>
        </div>
        <div className="mb-2 flex gap-2 items-end">
          <input
            type="text"
            placeholder="이름/설명 검색"
            value={q}
            onChange={e => { setQ(e.target.value); setPage(1); }}
            className="border rounded px-2 py-1 text-sm w-48"
          />
        </div>
        {loading && <div className="flex items-center gap-2 text-sm text-gray-500 mb-2"><span className="animate-spin">⏳</span>로딩 중...</div>}
        {error && <div className="text-sm text-red-500 mb-2">{error}</div>}
        {loading ? (
          <div className="text-gray-500">불러오는 중...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border min-w-[500px] md:min-w-0" role="table" aria-label="브랜드 목록">
              <thead>
                <tr className="bg-gray-100" role="row">
                  <th className="p-2" role="columnheader">{t('ID')}</th>
                  <th className="p-2" role="columnheader">{t('이름')}</th>
                  <th className="p-2" role="columnheader">{t('설명')}</th>
                  <th className="p-2" role="columnheader">{t('관리')}</th>
                </tr>
              </thead>
              <tbody>
                {brands.map((b) => (
                  <tr key={b.id} className="border-t hover:bg-blue-50 cursor-pointer md:table-row block mb-2 md:mb-0 bg-white md:bg-transparent rounded-lg md:rounded-none shadow md:shadow-none" onClick={() => handleProfile(b)} role="row">
                    <td className="p-2 md:table-cell block font-bold md:font-normal" role="cell">{b.id}</td>
                    <td className="p-2 md:table-cell block" role="cell">{b.name}</td>
                    <td className="p-2 md:table-cell block" role="cell">{b.description}</td>
                    <td className="p-2 flex gap-2 md:table-cell block" role="cell">
                      <button className="text-blue-600 underline text-sm md:text-base" onClick={e => { e.stopPropagation(); handleEdit(b); }} aria-label="브랜드 수정" disabled={!canEdit} style={!canEdit ? { opacity: 0.5, pointerEvents: 'none' } : {}}>
                        수정
                      </button>
                      <button className="text-red-600 underline text-sm md:text-base" onClick={e => { e.stopPropagation(); handleDelete(b.id); }} aria-label="브랜드 삭제" disabled={!canEdit} style={!canEdit ? { opacity: 0.5, pointerEvents: 'none' } : {}}>
                        삭제
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {/* 프로필 패널 */}
        {profileOpen && profileBrand && (
          <div className="fixed top-0 right-0 h-full w-full max-w-sm bg-white shadow-2xl z-50 animate-slide-in flex flex-col md:max-w-sm w-full md:w-[400px]">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-lg font-bold">브랜드 상세 정보</h3>
              <button className="text-2xl text-gray-400 hover:text-gray-700" onClick={closeProfile}>&times;</button>
            </div>
            <div className="p-6 space-y-3 flex-1 overflow-y-auto text-base md:text-sm">
              <div><b>이름:</b> {profileBrand.name}</div>
              <div><b>설명:</b> {profileBrand.description}</div>
              <div><b>상태:</b> {profileBrand.status || '알 수 없음'}</div>
              <div><b>등록일:</b> {profileBrand.created_at || '-'}</div>
              <div><b>관리자:</b> {profileBrand.admin_name || '-'}</div>
            </div>
          </div>
        )}
        {/* 페이징 */}
        <div className="flex gap-2 mt-4">
          <button
            className="px-2 py-1 border rounded disabled:opacity-50"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            이전
          </button>
          <span>
            {page} / {Math.ceil(total / perPage) || 1}
          </span>
          <button
            className="px-2 py-1 border rounded disabled:opacity-50"
            onClick={() => setPage((p) => p + 1)}
            disabled={page * perPage >= total}
          >
            다음
          </button>
        </div>
        {/* 등록/수정 폼 */}
        {editMode && (
          <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
            <div className="bg-white rounded shadow p-4 w-full max-w-sm mx-2 md:mx-0">
              <BrandForm
                brand={editMode === 'edit' ? selected : undefined}
                onSave={handleSave}
                onCancel={() => setEditMode(null)}
              />
            </div>
          </div>
        )}
        {/* 실시간 공지사항 리스트 */}
        <div className="bg-white dark:bg-slate-800 rounded shadow p-4 animate-fade-in mt-4">
          <h2 className="font-bold mb-2 text-slate-900 dark:text-white">공지사항</h2>
          <ul className="list-disc pl-6 space-y-1">
            {announcements.length === 0 ? (
              <li className="text-gray-400">최근 공지사항이 없습니다.</li>
            ) : (
              announcements.map((a, idx) => (
                <li key={idx} className="text-slate-800 dark:text-white">
                  <b>{a.title || '공지'}</b> <span className="text-xs text-gray-500">{a.created_at || ''}</span>
                  <div className="text-sm">{a.message}</div>
                </li>
              ))
            )}
          </ul>
        </div>
      </div>
    </>
  );
};

// 브랜드 등록/수정 폼 컴포넌트
function BrandForm({ brand, onSave, onCancel }: { brand?: any; onSave: (data: any) => void; onCancel: () => void }) {
  const [form, setForm] = React.useState<any>(brand || { name: '', description: '' });
  const [error, setError] = React.useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm((f: any) => ({ ...f, [e.target.name]: e.target.value }));
    setError(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError('브랜드 이름을 입력하세요.');
      return;
    }
    if (!form.description || form.description.length < 2) {
      setError('설명은 2자 이상 입력하세요.');
      return;
    }
    setError(null);
    onSave(form);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <input
        className="w-full border rounded px-2 py-1"
        name="name"
        placeholder="브랜드 이름"
        value={form.name}
        onChange={handleChange}
        required
      />
      <textarea
        className="w-full border rounded px-2 py-1"
        name="description"
        placeholder="설명 (2자 이상)"
        value={form.description}
        onChange={handleChange}
        minLength={2}
        required
      />
      {error && <div className="text-red-500 text-sm mb-2">{error}</div>}
      <div className="flex gap-2 justify-end">
        <button type="button" className="px-3 py-1 border rounded" onClick={onCancel}>취소</button>
        <button type="submit" className="px-3 py-1 bg-blue-600 text-white rounded">{brand ? '수정' : '등록'}</button>
      </div>
    </form>
  );
}

export default BrandList; 