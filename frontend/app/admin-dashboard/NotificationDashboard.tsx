import React, { useEffect, useState } from 'react';
import { useToast } from '../../components/GlobalToast';

interface NotificationHistory {
  type: string;
  to: string;
  subject: string;
  message: string;
  status: string;
  error?: string;
  timestamp: number;
}

const NotificationDashboard: React.FC = () => {
  const [type, setType] = useState<'email' | 'sms' | 'push'>('email');
  const [to, setTo] = useState('');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState<NotificationHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/admin/notifications/history');
      const data = await res.json();
      setHistory(data.history || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleSend = async () => {
    if (!to || !message) {
      showToast('수신자와 메시지를 입력하세요.', 'warning');
      return;
    }
    try {
      const res = await fetch('/api/admin/notifications/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, to, subject, message }),
      });
      const data = await res.json();
      if (res.ok) {
        showToast('알림 발송 성공', 'success');
        setTo(''); setSubject(''); setMessage('');
        fetchHistory();
      } else {
        showToast(data.error || '알림 발송 실패', 'error');
      }
    } catch {
      showToast('알림 발송 실패', 'error');
    }
  };

  return (
    <div className="p-4 max-w-3xl mx-auto">
      <h2 className="text-xl font-bold mb-4">알림 관리</h2>
      <div className="mb-4 bg-white rounded shadow p-4">
        <div className="flex gap-2 mb-2">
          <select value={type} onChange={e => setType(e.target.value as any)} className="border rounded px-2 py-1 text-sm">
            <option value="email">이메일</option>
            <option value="sms">SMS</option>
            <option value="push">푸시</option>
          </select>
          <input
            type="text"
            placeholder={type === 'email' ? '이메일 주소' : type === 'sms' ? '전화번호' : '푸시 토큰'}
            value={to}
            onChange={e => setTo(e.target.value)}
            className="border rounded px-2 py-1 text-sm w-64"
          />
          {type === 'email' && (
            <input
              type="text"
              placeholder="제목"
              value={subject}
              onChange={e => setSubject(e.target.value)}
              className="border rounded px-2 py-1 text-sm w-48"
            />
          )}
        </div>
        <textarea
          placeholder="메시지"
          value={message}
          onChange={e => setMessage(e.target.value)}
          className="border rounded px-2 py-1 text-sm w-full mb-2"
          rows={3}
        />
        <button
          className="bg-blue-600 text-white px-3 py-1 rounded"
          onClick={handleSend}
        >
          알림 발송
        </button>
      </div>
      <h3 className="font-semibold mb-2">알림 발송 내역</h3>
      {loading ? (
        <div className="text-gray-500">불러오는 중...</div>
      ) : (
        <table className="w-full text-sm border">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-2">유형</th>
              <th className="p-2">수신자</th>
              <th className="p-2">제목</th>
              <th className="p-2">상태</th>
              <th className="p-2">일시</th>
              <th className="p-2">오류</th>
            </tr>
          </thead>
          <tbody>
            {history.map((h, i) => (
              <tr key={i} className="border-t">
                <td className="p-2">{h.type}</td>
                <td className="p-2">{h.to}</td>
                <td className="p-2">{h.subject}</td>
                <td className={
                  'p-2 ' + (h.status === 'success' ? 'text-green-600' : 'text-red-600')
                }>{h.status}</td>
                <td className="p-2">{new Date(h.timestamp * 1000).toLocaleString()}</td>
                <td className="p-2 text-xs text-red-500">{h.error || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default NotificationDashboard; 