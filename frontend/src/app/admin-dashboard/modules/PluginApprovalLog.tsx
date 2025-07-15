import React, { useEffect, useState } from 'react';

interface ApprovalLog {
  plugin_id: string;
  action: string;
  user: string;
  reason?: string;
  timestamp: string;
}

const API_LOG = '/api/marketplace/approval_log'; // 감사 로그 API (가정)

const PluginApprovalLog: React.FC = () => {
  const [logs, setLogs] = useState<ApprovalLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLogs = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(API_LOG);
        const data = await res.json();
        if (Array.isArray(data)) {
          setLogs(data);
        } else if (data.logs) {
          setLogs(data.logs);
        } else {
          setError('감사 로그를 불러오지 못했습니다.');
        }
      } catch (e) {
        setError('서버 오류: ' + (e as any).toString());
      }
      setLoading(false);
    };
    fetchLogs();
  }, []);

  return (
    <div style={{ padding: 24 }}>
      <h2>플러그인 승인/거절 감사 로그</h2>
      {loading && <div>로딩 중...</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 16 }}>
        <thead>
          <tr>
            <th>플러그인</th>
            <th>액션</th>
            <th>관리자</th>
            <th>사유</th>
            <th>일시</th>
          </tr>
        </thead>
        <tbody>
          {logs.length === 0 && !loading && (
            <tr><td colSpan={5}>로그가 없습니다.</td></tr>
          )}
          {logs.map((log, idx) => (
            <tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
              <td>{log.plugin_id}</td>
              <td>{log.action}</td>
              <td>{log.user}</td>
              <td>{log.reason || '-'}</td>
              <td>{log.timestamp}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PluginApprovalLog; 