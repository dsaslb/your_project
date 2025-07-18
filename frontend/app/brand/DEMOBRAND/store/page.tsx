import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import fetchWithCSRF from '../../../src/utils/fetchWithCSRF';
import { toast } from 'react-hot-toast';

export default function StoreListPage({ params }: { params: { brand_id: string } }) {
  const { brand_id } = params;
  const [stores, setStores] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', address: '' });
  const [editingId, setEditingId] = useState<string|null>(null);
  const [userRole, setUserRole] = useState(''); // 권한 체크용

  useEffect(() => {
    async function fetchStores() {
      setLoading(true);
      try {
        const res = await fetchWithCSRF(`/api/stores?brand_id=${brand_id}`);
        if (res.ok) {
          const data = await res.json();
          setStores(data.stores || []);
        } else {
          setStores([]);
        }
      } catch {
        setStores([]);
      } finally {
        setLoading(false);
      }
    }
    fetchStores();
  }, [brand_id]);

  useEffect(() => {
    // 권한 정보 불러오기(예시)
    fetchWithCSRF('/api/profile').then(res => res.json()).then(data => setUserRole(data.role || ''));
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.address) return;
    if (editingId) {
      // 수정
      await fetchWithCSRF(`/api/stores/${editingId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, brand_id }),
      });
    } else {
      // 추가
      await fetchWithCSRF('/api/stores', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, brand_id }),
      });
    }
    setShowForm(false);
    setForm({ name: '', address: '' });
    setEditingId(null);
    // 새로고침
    const res = await fetchWithCSRF(`/api/stores?brand_id=${brand_id}`);
    const data = await res.json();
    setStores(data.stores || []);
  };

  const handleEdit = (store: any) => {
    setForm({ name: store.name, address: store.address });
    setEditingId(store.id);
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return;
    await fetchWithCSRF(`/api/stores/${id}`, { method: 'DELETE' });
    setStores(stores.filter(s => s.id !== id));
  };

  const handleSample = async () => {
    // 샘플 매장 자동 추가
    await fetchWithCSRF('/api/stores', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: '샘플매장', address: '서울시 강남구', brand_id }),
    });
    const res = await fetchWithCSRF(`/api/stores?brand_id=${brand_id}`);
    const data = await res.json();
    setStores(data.stores || []);
  };

  return (
    <div>
      <h1>브랜드별 매장 목록</h1>
      {userRole === 'admin' || userRole === 'brand_manager' ? (
        <>
          <button onClick={() => setShowForm(!showForm)}>{showForm ? '취소' : '매장 추가'}</button>
          <button onClick={handleSample}>샘플 매장 자동 추가</button>
          {showForm && (
            <form onSubmit={handleSubmit}>
              <input name="name" value={form.name} onChange={handleChange} placeholder="매장명" />
              <input name="address" value={form.address} onChange={handleChange} placeholder="주소" />
              <button type="submit">{editingId ? '수정' : '추가'}</button>
            </form>
          )}
        </>
      ) : null}
      {loading ? (
        <div>로딩 중...</div>
      ) : (
        <ul>
          {stores.map(store => (
            <li key={store.id}>
              {store.name} ({store.address})
              {userRole === 'admin' || userRole === 'brand_manager' ? (
                <>
                  <button onClick={() => handleEdit(store)}>수정</button>
                  <button onClick={() => handleDelete(store.id)}>삭제</button>
                </>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
} 