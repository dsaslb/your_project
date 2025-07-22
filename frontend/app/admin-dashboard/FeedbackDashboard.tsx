import React, { useEffect, useState } from 'react';
import { useToast } from '../../components/GlobalToast';

interface Feedback {
  id: number;
  user: string;
  message: string;
  type: string;
  created_at: string;
}
interface FAQ {
  id: number;
  question: string;
  answer: string;
  created_at: string;
}

const FeedbackDashboard: React.FC = () => {
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [loading, setLoading] = useState(true);
  const [editFaq, setEditFaq] = useState<FAQ | null>(null);
  const [faqQ, setFaqQ] = useState('');
  const [faqA, setFaqA] = useState('');
  const { showToast } = useToast();

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [fbRes, faqRes] = await Promise.all([
        fetch('/api/support/feedback'),
        fetch('/api/support/faq'),
      ]);
      setFeedbacks((await fbRes.json()).feedbacks || []);
      setFaqs((await faqRes.json()).faqs || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const handleAddFaq = async () => {
    if (!faqQ || !faqA) {
      showToast('질문과 답변을 입력하세요.', 'warning');
      return;
    }
    try {
      const res = await fetch('/api/support/faq', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: faqQ, answer: faqA }),
      });
      if (res.ok) {
        showToast('FAQ 등록 완료', 'success');
        setFaqQ(''); setFaqA('');
        fetchAll();
      } else {
        showToast('등록 실패', 'error');
      }
    } catch {
      showToast('등록 실패', 'error');
    }
  };

  const handleEditFaq = (faq: FAQ) => {
    setEditFaq(faq);
    setFaqQ(faq.question);
    setFaqA(faq.answer);
  };

  const handleUpdateFaq = async () => {
    if (!editFaq) return;
    try {
      const res = await fetch(`/api/support/faq/${editFaq.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: faqQ, answer: faqA }),
      });
      if (res.ok) {
        showToast('FAQ 수정 완료', 'success');
        setEditFaq(null); setFaqQ(''); setFaqA('');
        fetchAll();
      } else {
        showToast('수정 실패', 'error');
      }
    } catch {
      showToast('수정 실패', 'error');
    }
  };

  const handleDeleteFaq = async (id: number) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return;
    try {
      const res = await fetch(`/api/support/faq/${id}`, { method: 'DELETE' });
      if (res.ok) {
        showToast('삭제 완료', 'success');
        fetchAll();
      } else {
        showToast('삭제 실패', 'error');
      }
    } catch {
      showToast('삭제 실패', 'error');
    }
  };

  return (
    <div className="p-4 max-w-5xl mx-auto">
      <h2 className="text-xl font-bold mb-4">피드백/FAQ 관리</h2>
      <div className="mb-8">
        <h3 className="font-semibold mb-2">피드백/문의 목록</h3>
        {loading ? (
          <div className="text-gray-500">불러오는 중...</div>
        ) : (
          <table className="w-full text-sm border">
            <thead>
              <tr className="bg-gray-100">
                <th className="p-2">유형</th>
                <th className="p-2">이름</th>
                <th className="p-2">메시지</th>
                <th className="p-2">일시</th>
              </tr>
            </thead>
            <tbody>
              {feedbacks.map((f) => (
                <tr key={f.id} className="border-t">
                  <td className="p-2">{f.type}</td>
                  <td className="p-2">{f.user}</td>
                  <td className="p-2">{f.message}</td>
                  <td className="p-2">{new Date(f.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      <div className="mb-8">
        <h3 className="font-semibold mb-2">FAQ 관리</h3>
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            placeholder="질문"
            value={faqQ}
            onChange={e => setFaqQ(e.target.value)}
            className="border rounded px-2 py-1 text-sm w-64"
          />
          <input
            type="text"
            placeholder="답변"
            value={faqA}
            onChange={e => setFaqA(e.target.value)}
            className="border rounded px-2 py-1 text-sm w-64"
          />
          {editFaq ? (
            <>
              <button className="bg-blue-600 text-white px-3 py-1 rounded" onClick={handleUpdateFaq}>
                수정
              </button>
              <button className="px-3 py-1 border rounded" onClick={() => { setEditFaq(null); setFaqQ(''); setFaqA(''); }}>
                취소
              </button>
            </>
          ) : (
            <button className="bg-blue-600 text-white px-3 py-1 rounded" onClick={handleAddFaq}>
              등록
            </button>
          )}
        </div>
        <table className="w-full text-sm border">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-2">질문</th>
              <th className="p-2">답변</th>
              <th className="p-2">일시</th>
              <th className="p-2">관리</th>
            </tr>
          </thead>
          <tbody>
            {faqs.map((faq) => (
              <tr key={faq.id} className="border-t">
                <td className="p-2">{faq.question}</td>
                <td className="p-2">{faq.answer}</td>
                <td className="p-2">{new Date(faq.created_at).toLocaleString()}</td>
                <td className="p-2 flex gap-2">
                  <button className="text-blue-600 underline" onClick={() => handleEditFaq(faq)}>
                    수정
                  </button>
                  <button className="text-red-600 underline" onClick={() => handleDeleteFaq(faq.id)}>
                    삭제
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default FeedbackDashboard; 