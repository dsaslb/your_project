import React, { useEffect, useState } from 'react';

export default function NotificationSSE() {
  const [message, setMessage] = useState<string|null>(null);
  useEffect(() => {
    const es = new EventSource('/api/admin/monitor/stream');
    es.onmessage = (e) => {
      const data = JSON.parse(e.data);
      setMessage(`${data.time}: ${data.message}`);
      setTimeout(() => setMessage(null), 5000);
    };
    return () => es.close();
  }, []);
  return message ? (
    <div className="fixed top-4 right-4 z-50 bg-blue-600 text-white px-4 py-2 rounded shadow-lg" role="status" aria-live="polite">
      <span aria-label="실시간 알림">🔔 {message}</span>
    </div>
  ) : null;
} 