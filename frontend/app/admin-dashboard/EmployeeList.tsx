import React, { useEffect, useState } from 'react';
import { useToast } from '../../components/GlobalToast';
import { useI18n } from '../../components/i18n';

interface Employee {
  id: number;
  name: string;
  branch_id: number;
  brand_id?: number;
  role?: string;
  email?: string;
  phone?: string;
  status?: string;
  description?: string;
  created_at?: string;
}

const EmployeeList: React.FC = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [perPage] = useState(10);
  const [q, setQ] = useState('');
  const [branchId, setBranchId] = useState('');
  const [brandId, setBrandId] = useState('');
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Employee | null>(null);
  const [editMode, setEditMode] = useState<'create' | 'edit' | null>(null);
  const { showToast } = useToast();
  const { t } = useI18n();

  const fetchEmployees = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/admin/employees?q=${encodeURIComponent(q)}&branch_id=${branchId}&brand_id=${brandId}&page=${page}&per_page=${perPage}`);
      const data = await res.json();
      setEmployees(data.employees || []);
      setTotal(data.total || 0);
    } catch (e) {
      showToast('직원 목록을 불러오지 못했습니다.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
    // eslint-disable-next-line
  }, [q, page, branchId, brandId]);

  const handleDelete = async (id: number) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return;
    try {
      const res = await fetch(`/api/admin/employees/${id}`, { method: 'DELETE' });
      if (res.ok) {
        showToast('삭제되었습니다.', 'success');
        fetchEmployees();
      } else {
        showToast('삭제 실패', 'error');
      }
    } catch {
      showToast('삭제 실패', 'error');
    }
  };

  const handleEdit = (employee: Employee) => {
    setSelected(employee);
    setEditMode('edit');
  };

  const handleCreate = () => {
    setSelected(null);
    setEditMode('create');
  };

  const handleSave = async (employee: Partial<Employee>) => {
    try {
      const res = await fetch(
        editMode === 'edit' && employee.id
          ? `/api/admin/employees/${employee.id}`
          : '/api/admin/employees',
        {
          method: editMode === 'edit' ? 'PUT' : 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(employee),
        }
      );
      if (res.ok) {
        showToast('저장되었습니다.', 'success');
        setEditMode(null);
        fetchEmployees();
      } else {
        showToast('저장 실패', 'error');
      }
    } catch {
      showToast('저장 실패', 'error');
    }
  };

  return (
    <div className="p-4 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">직원 관리</h2>
        <button
          className="bg-blue-600 text-white px-3 py-1 rounded"
          onClick={handleCreate}
        >
          + 새 직원
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
          placeholder="지점 ID"
          value={branchId}
          onChange={e => setBranchId(e.target.value)}
          className="border rounded px-2 py-1 text-sm w-32"
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
              <th className="p-2">지점ID</th>
              <th className="p-2">브랜드ID</th>
              <th className="p-2">역할</th>
              <th className="p-2">이메일</th>
              <th className="p-2">상태</th>
              <th className="p-2">관리</th>
            </tr>
          </thead>
          <tbody>
            {employees.map((e) => (
              <tr key={e.id} className="border-t">
                <td className="p-2">{e.id}</td>
                <td className="p-2">{e.name}</td>
                <td className="p-2">{e.branch_id}</td>
                <td className="p-2">{e.brand_id}</td>
                <td className="p-2">{e.role}</td>
                <td className="p-2">{e.email}</td>
                <td className="p-2">{e.status}</td>
                <td className="p-2 flex gap-2">
                  <button className="text-blue-600 underline" onClick={() => handleEdit(e)}>
                    수정
                  </button>
                  <button className="text-red-600 underline" onClick={() => handleDelete(e.id)}>
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
        <EmployeeForm
          employee={editMode === 'edit' ? selected : undefined}
          onSave={handleSave}
          onCancel={() => setEditMode(null)}
        />
      )}
    </div>
  );
};

// 직원 등록/수정 폼 컴포넌트
const EmployeeForm: React.FC<{
  employee?: Employee | null;
  onSave: (employee: Partial<Employee>) => void;
  onCancel: () => void;
}> = ({ employee, onSave, onCancel }) => {
  const [name, setName] = useState(employee?.name || '');
  const [branchId, setBranchId] = useState(employee?.branch_id?.toString() || '');
  const [brandId, setBrandId] = useState(employee?.brand_id?.toString() || '');
  const [role, setRole] = useState(employee?.role || 'staff');
  const [email, setEmail] = useState(employee?.email || '');
  const [phone, setPhone] = useState(employee?.phone || '');
  const [status, setStatus] = useState(employee?.status || 'active');
  const [description, setDescription] = useState(employee?.description || '');
  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div className="bg-white rounded shadow p-6 w-full max-w-sm">
        <h3 className="text-lg font-bold mb-2">{employee ? '직원 수정' : '새 직원 등록'}</h3>
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
          <label className="block text-sm mb-1">지점 ID</label>
          <input
            type="number"
            value={branchId}
            onChange={e => setBranchId(e.target.value)}
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
          <label className="block text-sm mb-1">역할</label>
          <select
            value={role}
            onChange={e => setRole(e.target.value)}
            className="border rounded px-2 py-1 w-full"
          >
            <option value="admin">관리자</option>
            <option value="manager">지점장</option>
            <option value="staff">직원</option>
          </select>
        </div>
        <div className="mb-2">
          <label className="block text-sm mb-1">이메일</label>
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            className="border rounded px-2 py-1 w-full"
          />
        </div>
        <div className="mb-2">
          <label className="block text-sm mb-1">전화번호</label>
          <input
            type="text"
            value={phone}
            onChange={e => setPhone(e.target.value)}
            className="border rounded px-2 py-1 w-full"
          />
        </div>
        <div className="mb-2">
          <label className="block text-sm mb-1">상태</label>
          <select
            value={status}
            onChange={e => setStatus(e.target.value)}
            className="border rounded px-2 py-1 w-full"
          >
            <option value="active">활성</option>
            <option value="inactive">비활성</option>
            <option value="suspended">정지</option>
          </select>
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
            onClick={() => onSave({
              id: employee?.id,
              name,
              branch_id: Number(branchId),
              brand_id: brandId ? Number(brandId) : undefined,
              role,
              email,
              phone,
              status,
              description,
            })}
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

export default EmployeeList; 