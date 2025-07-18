import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import fetchWithCSRF from '../../../src/utils/fetchWithCSRF';
import { toast } from 'react-hot-toast';

export default function FeedbackListPage({ params }: { params: { brand_id: string } }) {
  const { brand_id } = params;
  const [feedbacks, setFeedbacks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: '', status: '' });
  const [editingId, setEditingId] = useState<string|null>(null);
  const [userRole, setUserRole] = useState('');

  useEffect(() => {
    async function fetchFeedbacks() {
      setLoading(true);
      try {
        const res = await fetchWithCSRF(`/api/feedback?brand_id=${brand_id}`);
        if (res.ok) {
          const data = await res.json();
          setFeedbacks(data.feedbacks || []);
        } else {
          setFeedbacks([]);
        }
      } catch {
        setFeedbacks([]);
      } finally {
        setLoading(false);
      }
    }
    fetchFeedbacks();
  }, [brand_id]);

  useEffect(() => {
    fetchWithCSRF('/api/profile').then(res => res.json()).then(data => setUserRole(data.role || ''));
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title || !form.status) return;
    if (editingId) {
      await fetchWithCSRF(`/api/feedback/${editingId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, brand_id }),
      });
    } else {
      await fetchWithCSRF('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, brand_id }),
      });
    }
    setShowForm(false);
    setForm({ title: '', status: '' });
    setEditingId(null);
    const res = await fetchWithCSRF(`/api/feedback?brand_id=${brand_id}`);
    const data = await res.json();
    setFeedbacks(data.feedbacks || []);
  };

  const handleEdit = (fb: any) => {
    setForm({ title: fb.title, status: fb.status });
    setEditingId(fb.id);
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return;
    await fetchWithCSRF(`/api/feedback/${id}`, { method: 'DELETE' });
    setFeedbacks(feedbacks.filter(fb => fb.id !== id));
  };

  const handleSample = async () => {
    await fetchWithCSRF('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: '샘플 피드백', status: 'open', brand_id }),
    });
    const res = await fetchWithCSRF(`/api/feedback?brand_id=${brand_id}`);
    const data = await res.json();
    setFeedbacks(data.feedbacks || []);
  };

  return (
    <div>
      <h1>브랜드별 개선요청 목록</h1>
      {userRole === 'admin' || userRole === 'brand_manager' ? (
        <>
          <button onClick={() => setShowForm(!showForm)}>{showForm ? '취소' : '피드백 추가'}</button>
          <button onClick={handleSample}>샘플 피드백 자동 추가</button>
          {showForm && (
            <form onSubmit={handleSubmit}>
              <input name="title" value={form.title} onChange={handleChange} placeholder="제목" />
              <input name="status" value={form.status} onChange={handleChange} placeholder="상태(open/closed)" />
              <button type="submit">{editingId ? '수정' : '추가'}</button>
            </form>
          )}
        </>
      ) : null}
      {loading ? (
        <div>로딩 중...</div>
      ) : (
        <ul>
          {feedbacks.map(fb => (
            <li key={fb.id}>
              {fb.title} ({fb.status})
              {userRole === 'admin' || userRole === 'brand_manager' ? (
                <>
                  <button onClick={() => handleEdit(fb)}>수정</button>
                  <button onClick={() => handleDelete(fb.id)}>삭제</button>
                </>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
} 