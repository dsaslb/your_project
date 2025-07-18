import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import fetchWithCSRF from '../../../src/utils/fetchWithCSRF';
import { toast } from 'react-hot-toast';

export default function StaffListPage({ params }: { params: { brand_id: string } }) {
  const { brand_id } = params;
  const [staff, setStaff] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', username: '', password: '' });
  const [editingId, setEditingId] = useState<string|null>(null);
  const [userRole, setUserRole] = useState('');

  useEffect(() => {
    async function fetchStaff() {
      setLoading(true);
      try {
        const res = await fetchWithCSRF(`/api/users?brand_id=${brand_id}`);
        if (res.ok) {
          const data = await res.json();
          setStaff(data.users || []);
        } else {
          setStaff([]);
        }
      } catch {
        setStaff([]);
      } finally {
        setLoading(false);
      }
    }
    fetchStaff();
  }, [brand_id]);

  useEffect(() => {
    fetchWithCSRF('/api/profile').then(res => res.json()).then(data => setUserRole(data.role || ''));
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.email || !form.username || !form.password) return;
    if (editingId) {
      await fetchWithCSRF(`/api/users/${editingId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, brand_id }),
      });
    } else {
      await fetchWithCSRF('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, brand_id, role: 'employee' }),
      });
    }
    setShowForm(false);
    setForm({ name: '', email: '', username: '', password: '' });
    setEditingId(null);
    const res = await fetchWithCSRF(`/api/users?brand_id=${brand_id}`);
    const data = await res.json();
    setStaff(data.users || []);
  };

  const handleEdit = (user: any) => {
    setForm({ name: user.name, email: user.email, username: user.username, password: '' });
    setEditingId(user.id);
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return;
    await fetchWithCSRF(`/api/users/${id}`, { method: 'DELETE' });
    setStaff(staff.filter(u => u.id !== id));
  };

  const handleSample = async () => {
    await fetchWithCSRF('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: '샘플직원', email: 'sample@brand.com', username: 'sampleuser', password: '1234', brand_id, role: 'employee' }),
    });
    const res = await fetchWithCSRF(`/api/users?brand_id=${brand_id}`);
    const data = await res.json();
    setStaff(data.users || []);
  };

  return (
    <div>
      <h1>브랜드별 직원 목록</h1>
      {userRole === 'admin' || userRole === 'brand_manager' ? (
        <>
          <button onClick={() => setShowForm(!showForm)}>{showForm ? '취소' : '직원 추가'}</button>
          <button onClick={handleSample}>샘플 직원 자동 추가</button>
          {showForm && (
            <form onSubmit={handleSubmit}>
              <input name="name" value={form.name} onChange={handleChange} placeholder="이름" />
              <input name="email" value={form.email} onChange={handleChange} placeholder="이메일" />
              <input name="username" value={form.username} onChange={handleChange} placeholder="아이디" />
              <input name="password" value={form.password} onChange={handleChange} placeholder="비밀번호" type="password" />
              <button type="submit">{editingId ? '수정' : '추가'}</button>
            </form>
          )}
        </>
      ) : null}
      {loading ? (
        <div>로딩 중...</div>
      ) : (
        <ul>
          {staff.map(user => (
            <li key={user.id}>
              {user.name} ({user.email})
              {userRole === 'admin' || userRole === 'brand_manager' ? (
                <>
                  <button onClick={() => handleEdit(user)}>수정</button>
                  <button onClick={() => handleDelete(user.id)}>삭제</button>
                </>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
} 