import React, { useEffect, useState } from 'react';
import { useToast } from '../../components/GlobalToast';
import { useI18n } from '../../components/i18n';

interface Branch {
  id: number;
  name: string;
  brand_id: number;
  description?: string;
  created_at?: string;
}

const BranchList: React.FC = () => {
  const [branches, setBranches] = useState<Branch[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [perPage] = useState(10);
  const [q, setQ] = useState('');
  const [brandId, setBrandId] = useState('');
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Branch | null>(null);
  const [editMode, setEditMode] = useState<'create' | 'edit' | null>(null);
  const { showToast } = useToast();
  const { t } = useI18n();

  const fetchBranches = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/admin/branches?q=${encodeURIComponent(q)}&brand_id=${brandId}&page=${page}&per_page=${perPage}`);
      const data = await res.json();
      setBranches(data.branches || []);
      setTotal(data.total || 0);
    } catch (e) {
      showToast('지점 목록을 불러오지 못했습니다.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBranches();
    // eslint-disable-next-line
  }, [q, page, brandId]);

  const handleDelete = async (id: number) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return;
    try {
      const res = await fetch(`/api/admin/branches/${id}`, { method: 'DELETE' });
      if (res.ok) {
        showToast('삭제되었습니다.', 'success');
        fetchBranches();
      } else {
        showToast('삭제 실패', 'error');
      }
    } catch {
      showToast('삭제 실패', 'error');
    }
  };

  const handleEdit = (branch: Branch) => {
    setSelected(branch);
    setEditMode('edit');
  };

  const handleCreate = () => {
    setSelected(null);
    setEditMode('create');
  };

  const handleSave = async (branch: Partial<Branch>) => {
    try {
      const res = await fetch(
        editMode === 'edit' && branch.id
          ? `/api/admin/branches/${branch.id}`
          : '/api/admin/branches',
        {
          method: editMode === 'edit' ? 'PUT' : 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(branch),
        }
      );
      if (res.ok) {
        showToast('저장되었습니다.', 'success');
        setEditMode(null);
        fetchBranches();
      } else {
        showToast('저장 실패', 'error');
      }
    } catch {
      showToast('저장 실패', 'error');
    }
  };

  return (
    <div className="p-4 max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">지점 관리</h2>
        <button
          className="bg-blue-600 text-white px-3 py-1 rounded"
          onClick={handleCreate}
        >
          + 새 지점
        </button>
      </div>
      <div className="mb-2 flex gap-2">
        <input
          type="text"
          placeholder="검색..."
          value={q}
          onChange={e => setQ(e.target.value)}
          className="border rounded px-2 py-1 text-sm w-48"
        />
        <input
          type="number"
          placeholder="브랜드 ID"
          value={brandId}
          onChange={e => setBrandId(e.target.value)}
          className="border rounded px-2 py-1 text-sm w-32"
        />
      </div>
      {loading ? (
        <div className="text-gray-500">불러오는 중...</div>
      ) : (
        <table className="w-full text-sm border">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-2">ID</th>
              <th className="p-2">이름</th>
              <th className="p-2">브랜드ID</th>
              <th className="p-2">설명</th>
              <th className="p-2">관리</th>
            </tr>
          </thead>
          <tbody>
            {branches.map((b) => (
              <tr key={b.id} className="border-t">
                <td className="p-2">{b.id}</td>
                <td className="p-2">{b.name}</td>
                <td className="p-2">{b.brand_id}</td>
                <td className="p-2">{b.description}</td>
                <td className="p-2 flex gap-2">
                  <button className="text-blue-600 underline" onClick={() => handleEdit(b)}>
                    수정
                  </button>
                  <button className="text-red-600 underline" onClick={() => handleDelete(b.id)}>
                    삭제
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
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
        <BranchForm
          branch={editMode === 'edit' ? selected : undefined}
          onSave={handleSave}
          onCancel={() => setEditMode(null)}
        />
      )}
    </div>
  );
};

// 지점 등록/수정 폼 컴포넌트
const BranchForm: React.FC<{
  branch?: Branch | null;
  onSave: (branch: Partial<Branch>) => void;
  onCancel: () => void;
}> = ({ branch, onSave, onCancel }) => {
  const [name, setName] = useState(branch?.name || '');
  const [brandId, setBrandId] = useState(branch?.brand_id?.toString() || '');
  const [description, setDescription] = useState(branch?.description || '');
  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div className="bg-white rounded shadow p-6 w-full max-w-sm">
        <h3 className="text-lg font-bold mb-2">{branch ? '지점 수정' : '새 지점 등록'}</h3>
        <div className="mb-2">
          <label className="block text-sm mb-1">이름</label>
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            className="border rounded px-2 py-1 w-full"
          />
        </div>
        <div className="mb-2">
          <label className="block text-sm mb-1">브랜드 ID</label>
          <input
            type="number"
            value={brandId}
            onChange={e => setBrandId(e.target.value)}
            className="border rounded px-2 py-1 w-full"
          />
        </div>
        <div className="mb-2">
          <label className="block text-sm mb-1">설명</label>
          <input
            type="text"
            value={description}
            onChange={e => setDescription(e.target.value)}
            className="border rounded px-2 py-1 w-full"
          />
        </div>
        <div className="flex gap-2 mt-4">
          <button
            className="bg-blue-600 text-white px-3 py-1 rounded"
            onClick={() => onSave({ id: branch?.id, name, brand_id: Number(brandId), description })}
          >
            저장
          </button>
          <button className="px-3 py-1 border rounded" onClick={onCancel}>
            취소
          </button>
        </div>
      </div>
    </div>
  );
};

export default BranchList; 