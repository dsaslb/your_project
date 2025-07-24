import React, { useEffect, useState } from 'react';
import { useToast } from '../../components/GlobalToast';
import { useI18n } from '../../components/i18n';
import useUserStore from '@/store/useUserStore';
import { toast } from 'sonner';
import { saveAs } from 'file-saver';
import LanguageSwitcher from '../../components/LanguageSwitcher';

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
  branch_name?: string; // Added for profile display
  brand_name?: string; // Added for profile display
}

const EmployeeList: React.FC = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [perPage] = useState(10);
  const [q, setQ] = useState('');
  const [branchId, setBranchId] = useState('');
  const [brandId, setBrandId] = useState('');
  const [role, setRole] = useState('');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Employee | null>(null);
  const [editMode, setEditMode] = useState<'create' | 'edit' | null>(null);
  const [profileOpen, setProfileOpen] = useState(false);
  const [profileEmployee, setProfileEmployee] = useState<Employee | null>(null);
  const { showToast } = useToast();
  const { t } = useI18n();
  const { user } = useUserStore();
  // 권한별 액션 제한(더 세밀하게)
  const canEdit = user && (user.role === 'admin' || user.role === 'store_admin');
  const [wsStatus, setWsStatus] = React.useState<'connected' | 'disconnected' | 'connecting'>('connecting');
  const [announcements, setAnnouncements] = React.useState<any[]>([]);
  // 실시간 동기화: WebSocket 연결
  React.useEffect(() => {
    setWsStatus('connecting');
    const ws = new WebSocket('wss://yourserver/ws/employees');
    ws.onopen = () => setWsStatus('connected');
    ws.onclose = () => setWsStatus('disconnected');
    ws.onerror = () => setWsStatus('disconnected');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (["employee_created", "employee_updated", "employee_deleted"].includes(data.type)) {
        fetchEmployees();
        // 실시간 알림/토스트
        let msg = '';
        if (data.type === 'employee_created') msg = `${data.user || '누군가'}님이 직원 "${data.target?.name || ''}"을(를) 추가했습니다.`;
        if (data.type === 'employee_updated') msg = `${data.user || '누군가'}님이 직원 "${data.target?.name || ''}"을(를) 수정했습니다.`;
        if (data.type === 'employee_deleted') msg = `${data.user || '누군가'}님이 직원 "${data.target?.name || ''}"을(를) 삭제했습니다.`;
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

  const fetchEmployees = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        q,
        branch_id: branchId,
        brand_id: brandId,
        role,
        status,
        page: String(page),
        per_page: String(perPage),
      });
      const res = await fetch(`/api/admin/employees?${params.toString()}`);
      const data = await res.json();
      setEmployees(data.employees || []);
      setTotal(data.total || 0);
    } catch (e) {
      setError('직원 목록을 불러오지 못했습니다.');
      showToast('직원 목록을 불러오지 못했습니다.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
    // eslint-disable-next-line
  }, [q, page, branchId, brandId, role, status]);

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

  const handleProfile = (employee: Employee) => {
    setProfileEmployee(employee);
    setProfileOpen(true);
  };
  const closeProfile = () => {
    setProfileOpen(false);
    setProfileEmployee(null);
  };

  const handleEditClick = (event: React.MouseEvent, employee: Employee) => {
    event.stopPropagation();
    handleEdit(employee);
  };
  const handleDeleteClick = (event: React.MouseEvent, id: number) => {
    event.stopPropagation();
    handleDelete(id);
  };

  // CSV 내보내기
  const exportCSV = () => {
    const header = ['ID', '이름', '이메일', '역할', '상태', '전화번호', '지점', '브랜드', '등록일'];
    const rows = employees.map(e => [e.id, e.name, e.email, e.role, e.status, e.phone || '', e.branch_name || '', e.brand_name || '', e.created_at || '']);
    const csv = [header, ...rows].map(r => r.map(x => `"${(x ?? '').toString().replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, 'employees.csv');
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
      <div className="p-4 max-w-5xl mx-auto">
        <div className="flex justify-between items-center mb-2">
          <span className="text-md font-semibold">{t('직원 목록')}</span>
          <div className="flex gap-2">
            <button className="px-3 py-1 bg-blue-600 text-white rounded" onClick={() => setEditMode('create')} aria-label="새 직원 등록">+ {t('새 직원')}</button>
            <button className="px-3 py-1 bg-green-600 text-white rounded" onClick={exportCSV} aria-label="CSV 내보내기">{t('CSV 내보내기')}</button>
          </div>
        </div>
        <div className="mb-2 flex gap-2 items-end">
          <input
            type="text"
            placeholder="이름/이메일 검색"
            value={q}
            onChange={e => { setQ(e.target.value); setPage(1); }}
            className="border rounded px-2 py-1 text-sm w-40"
          />
          <input
            type="number"
            placeholder="지점 ID"
            value={branchId}
            onChange={e => { setBranchId(e.target.value); setPage(1); }}
            className="border rounded px-2 py-1 text-sm w-32"
          />
          <input
            type="number"
            placeholder="브랜드 ID"
            value={brandId}
            onChange={e => { setBrandId(e.target.value); setPage(1); }}
            className="border rounded px-2 py-1 text-sm w-32"
          />
          <select className="border rounded px-2 py-1 text-sm" value={role} onChange={e => { setRole(e.target.value); setPage(1); }}>
            <option value="">전체 역할</option>
            <option value="admin">관리자</option>
            <option value="manager">지점장</option>
            <option value="staff">직원</option>
          </select>
          <select className="border rounded px-2 py-1 text-sm" value={status} onChange={e => { setStatus(e.target.value); setPage(1); }}>
            <option value="">전체 상태</option>
            <option value="active">활성</option>
            <option value="inactive">비활성</option>
            <option value="suspended">정지</option>
          </select>
        </div>
        {loading && <div className="flex items-center gap-2 text-sm text-gray-500 mb-2"><span className="animate-spin">⏳</span>로딩 중...</div>}
        {error && <div className="text-sm text-red-500 mb-2">{error}</div>}
        <div className="overflow-x-auto">
          <table className="w-full text-sm border min-w-[500px] md:min-w-0" role="table" aria-label="직원 목록">
            <thead>
              <tr className="bg-gray-100" role="row">
                <th className="p-2" role="columnheader">{t('ID')}</th>
                <th className="p-2" role="columnheader">{t('이름')}</th>
                <th className="p-2" role="columnheader">{t('이메일')}</th>
                <th className="p-2" role="columnheader">{t('역할')}</th>
                <th className="p-2" role="columnheader">{t('상태')}</th>
                <th className="p-2" role="columnheader">{t('관리')}</th>
              </tr>
            </thead>
            <tbody>
              {employees.map((e) => (
                <tr key={e.id} className="border-t hover:bg-blue-50 cursor-pointer md:table-row block mb-2 md:mb-0 bg-white md:bg-transparent rounded-lg md:rounded-none shadow md:shadow-none" onClick={() => handleProfile(e)} role="row">
                  <td className="p-2 md:table-cell block font-bold md:font-normal" role="cell">{e.id}</td>
                  <td className="p-2 md:table-cell block" role="cell">{e.name}</td>
                  <td className="p-2 md:table-cell block" role="cell">{e.email}</td>
                  <td className="p-2 md:table-cell block" role="cell">{e.role}</td>
                  <td className="p-2 md:table-cell block" role="cell">{e.status}</td>
                  <td className="p-2 flex gap-2 md:table-cell block" role="cell">
                    <button className="text-blue-600 underline text-sm md:text-base" onClick={ev => { ev.stopPropagation(); handleEdit(e); }} aria-label="직원 수정" disabled={!canEdit} style={!canEdit ? { opacity: 0.5, pointerEvents: 'none' } : {}}>
                      수정
                    </button>
                    <button className="text-red-600 underline text-sm md:text-base" onClick={ev => { ev.stopPropagation(); handleDelete(e.id); }} aria-label="직원 삭제" disabled={!canEdit} style={!canEdit ? { opacity: 0.5, pointerEvents: 'none' } : {}}>
                      삭제
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {/* 프로필 패널 */}
        {profileOpen && profileEmployee && (
          <div className="fixed top-0 right-0 h-full w-full max-w-sm bg-white shadow-2xl z-50 animate-slide-in flex flex-col md:max-w-sm w-full md:w-[400px]">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-lg font-bold">직원 상세 정보</h3>
              <button className="text-2xl text-gray-400 hover:text-gray-700" onClick={closeProfile}>&times;</button>
            </div>
            <div className="p-6 space-y-3 flex-1 overflow-y-auto text-base md:text-sm">
              <div><b>이름:</b> {profileEmployee.name}</div>
              <div><b>이메일:</b> {profileEmployee.email}</div>
              <div><b>역할:</b> {profileEmployee.role}</div>
              <div><b>상태:</b> {profileEmployee.status}</div>
              <div><b>전화번호:</b> {profileEmployee.phone || '-'}</div>
              <div><b>지점:</b> {profileEmployee.branch_name || '-'}</div>
              <div><b>브랜드:</b> {profileEmployee.brand_name || '-'}</div>
              <div><b>등록일:</b> {profileEmployee.created_at || '-'}</div>
            </div>
          </div>
        )}
        {/* 등록/수정 폼 */}
        {editMode && (
          <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
            <div className="bg-white rounded shadow p-4 w-full max-w-sm mx-2 md:mx-0">
              <EmployeeForm
                employee={editMode === 'edit' ? selected : undefined}
                onSave={handleSave}
                onCancel={() => setEditMode(null)}
              />
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
  const [error, setError] = useState<string | null>(null);

  const validate = () => {
    if (!name.trim()) return '이름을 입력하세요.';
    if (!email.trim()) return '이메일을 입력하세요.';
    if (!/^[\w-.]+@[\w-]+\.[a-zA-Z]{2,}$/.test(email)) return '이메일 형식이 올바르지 않습니다.';
    if (phone && !/^01[016789]-?\d{3,4}-?\d{4}$/.test(phone)) return '전화번호 형식이 올바르지 않습니다.';
    if (!role) return '역할을 선택하세요.';
    if (!status) return '상태를 선택하세요.';
    if (!branchId.trim()) return '지점 ID를 입력하세요.';
    return null;
  };

  const handleSave = () => {
    const err = validate();
    if (err) {
      setError(err);
      return;
    }
    setError(null);
    onSave({
      id: employee?.id,
      name,
      branch_id: Number(branchId),
      brand_id: brandId ? Number(brandId) : undefined,
      role,
      email,
      phone,
      status,
      description,
    });
  };

  return (
    <div className="bg-white rounded shadow p-6 w-full max-w-sm">
      <h3 className="text-lg font-bold mb-2">{employee ? '직원 수정' : '새 직원 등록'}</h3>
      <div className="mb-2">
        <label className="block text-sm mb-1">이름</label>
        <input
          type="text"
          value={name}
          onChange={e => setName(e.target.value)}
          className="border rounded px-2 py-1 w-full"
          required
        />
      </div>
      <div className="mb-2">
        <label className="block text-sm mb-1">지점 ID</label>
        <input
          type="number"
          value={branchId}
          onChange={e => setBranchId(e.target.value)}
          className="border rounded px-2 py-1 w-full"
          required
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
          required
        >
          <option value="">역할 선택</option>
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
          required
        />
      </div>
      <div className="mb-2">
        <label className="block text-sm mb-1">전화번호</label>
        <input
          type="text"
          value={phone}
          onChange={e => setPhone(e.target.value)}
          className="border rounded px-2 py-1 w-full"
          placeholder="010-1234-5678"
        />
      </div>
      <div className="mb-2">
        <label className="block text-sm mb-1">상태</label>
        <select
          value={status}
          onChange={e => setStatus(e.target.value)}
          className="border rounded px-2 py-1 w-full"
          required
        >
          <option value="">상태 선택</option>
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
      {error && <div className="text-red-500 text-sm mb-2">{error}</div>}
      <div className="flex gap-2 mt-4">
        <button
          className="bg-blue-600 text-white px-3 py-1 rounded"
          onClick={handleSave}
        >
          저장
        </button>
        <button className="px-3 py-1 border rounded" onClick={onCancel}>
          취소
        </button>
      </div>
    </div>
  );
};

export default EmployeeList; 