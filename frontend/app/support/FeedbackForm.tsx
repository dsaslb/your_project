import React, { useState } from 'react';
import { useToast } from '../../components/GlobalToast';

const FeedbackForm: React.FC = () => {
  const [user, setUser] = useState('');
  const [message, setMessage] = useState('');
  const [type, setType] = useState<'feedback' | 'inquiry'>('feedback');
  const [loading, setLoading] = useState(false);
  const { showToast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message) {
      showToast('메시지를 입력하세요.', 'warning');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('/api/support/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user, message, type }),
      });
      if (res.ok) {
        showToast('피드백이 등록되었습니다.', 'success');
        setMessage('');
      } else {
        showToast('등록 실패', 'error');
      }
    } catch {
      showToast('등록 실패', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto bg-white rounded shadow p-6 mt-8">
      <h2 className="text-lg font-bold mb-2">피드백/문의 남기기</h2>
      <div className="mb-2">
        <label className="block text-sm mb-1">이름(선택)</label>
        <input
          type="text"
          value={user}
          onChange={e => setUser(e.target.value)}
          className="border rounded px-2 py-1 w-full"
        />
      </div>
      <div className="mb-2">
        <label className="block text-sm mb-1">유형</label>
        <select value={type} onChange={e => setType(e.target.value as any)} className="border rounded px-2 py-1 w-full">
          <option value="feedback">피드백</option>
          <option value="inquiry">문의</option>
        </select>
      </div>
      <div className="mb-2">
        <label className="block text-sm mb-1">메시지</label>
        <textarea
          value={message}
          onChange={e => setMessage(e.target.value)}
          className="border rounded px-2 py-1 w-full"
          rows={4}
        />
      </div>
      <button
        type="submit"
        className="bg-blue-600 text-white px-4 py-2 rounded"
        disabled={loading}
      >
        {loading ? '등록 중...' : '등록'}
      </button>
    </form>
  );
};

export default FeedbackForm; 