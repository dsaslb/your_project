import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import fetchWithCSRF from '../../../src/utils/fetchWithCSRF';
import { toast } from 'react-hot-toast';

export default function SalesListPage({ params }: { params: { brand_id: string } }) {
  const { brand_id } = params;
  const [sales, setSales] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ date: '', amount: '' });
  const [editingId, setEditingId] = useState<string|null>(null);
  const [userRole, setUserRole] = useState('');

  useEffect(() => {
    async function fetchSales() {
      setLoading(true);
      try {
        const res = await fetchWithCSRF(`/api/sales?brand_id=${brand_id}`);
        if (res.ok) {
          const data = await res.json();
          setSales(data.sales || []);
        } else {
          setSales([]);
        }
      } catch {
        setSales([]);
      } finally {
        setLoading(false);
      }
    }
    fetchSales();
  }, [brand_id]);

  useEffect(() => {
    fetchWithCSRF('/api/profile').then(res => res.json()).then(data => setUserRole(data.role || ''));
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.date || !form.amount) return;
    if (editingId) {
      await fetchWithCSRF(`/api/sales/${editingId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, brand_id }),
      });
    } else {
      await fetchWithCSRF('/api/sales', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, brand_id }),
      });
    }
    setShowForm(false);
    setForm({ date: '', amount: '' });
    setEditingId(null);
    const res = await fetchWithCSRF(`/api/sales?brand_id=${brand_id}`);
    const data = await res.json();
    setSales(data.sales || []);
  };

  const handleEdit = (sale: any) => {
    setForm({ date: sale.date, amount: sale.amount });
    setEditingId(sale.id);
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return;
    await fetchWithCSRF(`/api/sales/${id}`, { method: 'DELETE' });
    setSales(sales.filter(s => s.id !== id));
  };

  const handleSample = async () => {
    await fetchWithCSRF('/api/sales', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date: '2024-06-01', amount: 100000, brand_id }),
    });
    const res = await fetchWithCSRF(`/api/sales?brand_id=${brand_id}`);
    const data = await res.json();
    setSales(data.sales || []);
  };

  return (
    <div>
      <h1>브랜드별 매출 목록</h1>
      {userRole === 'admin' || userRole === 'brand_manager' ? (
        <>
          <button onClick={() => setShowForm(!showForm)} aria-label={showForm ? '취소' : '매출 추가'}>{showForm ? '취소' : '매출 추가'}</button>
          <button onClick={handleSample} aria-label="샘플 매출 자동 추가">샘플 매출 자동 추가</button>
          {showForm && (
            <form onSubmit={handleSubmit}>
              <input name="date" value={form.date} onChange={handleChange} placeholder="날짜(YYYY-MM-DD)" aria-label="매출 날짜" />
              <input name="amount" value={form.amount} onChange={handleChange} placeholder="금액" aria-label="매출 금액" />
              <button type="submit" aria-label={editingId ? '수정' : '추가'}>{editingId ? '수정' : '추가'}</button>
            </form>
          )}
        </>
      ) : null}
      {loading ? (
        <div>로딩 중...</div>
      ) : (
        <ul>
          {sales.map(sale => (
            <li key={sale.id}>
              {sale.date} - {sale.amount}원
              {userRole === 'admin' || userRole === 'brand_manager' ? (
                <>
                  <button onClick={() => handleEdit(sale)} aria-label="매출 수정">수정</button>
                  <button onClick={() => handleDelete(sale.id)} aria-label="매출 삭제">삭제</button>
                </>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
} 