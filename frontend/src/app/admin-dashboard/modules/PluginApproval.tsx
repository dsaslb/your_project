import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';

// 플러그인 정보 타입 정의
interface PluginInfo {
  plugin_id: string;
  name: string;
  status: string;
  uploaded_at?: string;
  approved_at?: string;
  rejected_at?: string;
  meta?: any;
  first_approved_by?: string;
  second_approved_by?: string;
}

const API_LIST = '/api/marketplace/list'; // 플러그인 목록 조회 API (가정)
const API_APPROVE = (id: string) => `/api/marketplace/approve/${id}`;
const API_REJECT = (id: string) => `/api/marketplace/reject/${id}`;
const API_STATUS = (id: string) => `/api/marketplace/status/${id}`;

const SOCKET_URL = 'http://localhost:5000'; // 실제 서버 주소로 변경 가능

const PluginApproval: React.FC = () => {
  const [plugins, setPlugins] = useState<PluginInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  // 플러그인 목록 불러오기
  const fetchPlugins = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(API_LIST);
      const data = await res.json();
      if (data.success && data.plugins) {
        setPlugins(data.plugins);
      } else {
        setError('플러그인 목록을 불러오지 못했습니다.');
      }
    } catch (e) {
      setError('서버 오류: ' + (e as any).toString());
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchPlugins();
  }, []);

  // WebSocket 연결 및 실시간 알림 구독
  useEffect(() => {
    const socket = io(SOCKET_URL);
    socket.on('plugin_approval', (data: any) => {
      // 승인/거절 이벤트 발생 시 토스트 메시지 표시
      setToast(`플러그인 ${data.plugin_id}이(가) ${data.action === 'approve' ? '승인' : '거절'}되었습니다. (by ${data.user})`);
      // 3초 후 토스트 자동 숨김
      setTimeout(() => setToast(null), 3000);
    });
    return () => {
      socket.disconnect();
    };
  }, []);

  // 승인/거절 처리
  const handleAction = async (plugin_id: string, action: 'approve' | 'reject') => {
    let reason = '';
    if (action === 'reject' || action === 'approve') {
      reason = window.prompt(`플러그인 ${action === 'approve' ? '승인' : '거절'} 사유를 입력하세요 (필수)`);
      if (!reason) {
        setError('사유를 입력해야 합니다.');
        return;
      }
    }
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const api = action === 'approve' ? API_APPROVE(plugin_id) : API_REJECT(plugin_id);
      const res = await fetch(api, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason })
      });
      const data = await res.json();
      if (data.success) {
        setSuccess(`플러그인 ${action === 'approve' ? '승인' : '거절'} 완료!`);
        // 상태 갱신
        const statusRes = await fetch(API_STATUS(plugin_id));
        const statusData = await statusRes.json();
        setPlugins(prev => prev.map(p => p.plugin_id === plugin_id ? { ...p, ...statusData } : p));
      } else {
        setError(data.msg || '처리 실패');
      }
    } catch (e) {
      setError('서버 오류: ' + (e as any).toString());
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: 24 }}>
      <h2>플러그인 승인/거절 관리</h2>
      {toast && (
        <div style={{ position: 'fixed', top: 20, right: 20, background: '#333', color: '#fff', padding: 12, borderRadius: 8, zIndex: 9999 }}>
          {toast}
        </div>
      )}
      {loading && <div>로딩 중...</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {success && <div style={{ color: 'green' }}>{success}</div>}
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 16 }}>
        <thead>
          <tr>
            <th>이름</th>
            <th>상태</th>
            <th>업로드 일시</th>
            <th>1차 승인자</th>
            <th>2차 승인자</th>
            <th>상세정보</th>
            <th>액션</th>
          </tr>
        </thead>
        <tbody>
          {plugins.length === 0 && !loading && (
            <tr><td colSpan={7}>플러그인이 없습니다.</td></tr>
          )}
          {plugins.map(plugin => (
            <tr key={plugin.plugin_id} style={{ borderBottom: '1px solid #eee' }}>
              <td>{plugin.name}</td>
              <td>{plugin.status}</td>
              <td>{plugin.uploaded_at || '-'}</td>
              <td>{plugin.first_approved_by || '-'}</td>
              <td>{plugin.second_approved_by || '-'}</td>
              <td>
                <details>
                  <summary>상세</summary>
                  <pre style={{ fontSize: 12 }}>{JSON.stringify(plugin.meta, null, 2)}</pre>
                </details>
              </td>
              <td>
                {plugin.status === 'pending' && (
                  <>
                    <button onClick={() => handleAction(plugin.plugin_id, 'approve')} disabled={loading} style={{ marginRight: 8 }}>1차 승인</button>
                    <button onClick={() => handleAction(plugin.plugin_id, 'reject')} disabled={loading}>거절</button>
                  </>
                )}
                {plugin.status === 'waiting_second_approval' && (
                  <button onClick={() => handleAction(plugin.plugin_id, 'approve')} disabled={loading}>2차 승인</button>
                )}
                {plugin.status === 'approved' && <span>최종 승인됨</span>}
                {plugin.status === 'rejected' && <span>거절됨</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PluginApproval; 