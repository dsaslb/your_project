import React, { useEffect, useState } from 'react';
import { useToast } from '../../components/GlobalToast';
import { useI18n } from '../../components/i18n';

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
  const [selected, setSelected] = useState<Brand | null>(null);
  const [editMode, setEditMode] = useState<'create' | 'edit' | null>(null);
  const { showToast } = useToast();
  const { t } = useI18n();

  const fetchBrands = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/admin/brands?q=${encodeURIComponent(q)}&page=${page}&per_page=${perPage}`);
      const data = await res.json();
      setBrands(data.brands || []);
      setTotal(data.total || 0);
    } catch (e) {
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

  const handleSave = async (brand: Partial<Brand>) => {
    try {
      const res = await fetch(
        editMode === 'edit' && brand.id
          ? `/api/admin/brands/${brand.id}`
          : '/api/admin/brands',
        {
          method: editMode === 'edit' ? 'PUT' : 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(brand),
        }
      );
      if (res.ok) {
        showToast('저장되었습니다.', 'success');
        setEditMode(null);
        fetchBrands();
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
        <h2 className="text-xl font-bold">브랜드 관리</h2>
        <button
          className="bg-blue-600 text-white px-3 py-1 rounded"
          onClick={handleCreate}
        >
          + 새 브랜드
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
      </div>
      {loading ? (
        <div className="text-gray-500">불러오는 중...</div>
      ) : (
        <table className="w-full text-sm border">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-2">ID</th>
              <th className="p-2">이름</th>
              <th className="p-2">설명</th>
              <th className="p-2">관리</th>
            </tr>
          </thead>
          <tbody>
            {brands.map((b) => (
              <tr key={b.id} className="border-t">
                <td className="p-2">{b.id}</td>
                <td className="p-2">{b.name}</td>
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
        <BrandForm
          brand={editMode === 'edit' ? selected : undefined}
          onSave={handleSave}
          onCancel={() => setEditMode(null)}
        />
      )}
    </div>
  );
};

// 브랜드 등록/수정 폼 컴포넌트
const BrandForm: React.FC<{
  brand?: Brand | null;
  onSave: (brand: Partial<Brand>) => void;
  onCancel: () => void;
}> = ({ brand, onSave, onCancel }) => {
  const [name, setName] = useState(brand?.name || '');
  const [description, setDescription] = useState(brand?.description || '');
  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div className="bg-white rounded shadow p-6 w-full max-w-sm">
        <h3 className="text-lg font-bold mb-2">{brand ? '브랜드 수정' : '새 브랜드 등록'}</h3>
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
            onClick={() => onSave({ id: brand?.id, name, description })}
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

export default BrandList; 