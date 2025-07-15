import React, { useEffect, useState } from 'react';

interface PluginStats {
  rating_sum: number;
  rating_cnt: number;
  feedback_cnt: number;
  avg_rating: number | null;
}

interface Stats {
  approve_rate: number;
  avg_speed_sec: number;
  admin_stats: { [admin: string]: number };
  plugin_stats: { [plugin_id: string]: PluginStats };
}

const API_STATS = '/api/marketplace/stats';

const PluginMarketplaceStats: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(API_STATS);
        const data = await res.json();
        if (data && typeof data === 'object') {
          setStats(data);
        } else {
          setError('통계 데이터를 불러오지 못했습니다.');
        }
      } catch (e) {
        setError('서버 오류: ' + (e as any).toString());
      }
      setLoading(false);
    };
    fetchStats();
  }, []);

  return (
    <div style={{ padding: 24 }}>
      <h2>플러그인 마켓플레이스 통계 대시보드</h2>
      {loading && <div>로딩 중...</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {stats && (
        <>
          <div style={{ marginBottom: 16 }}>
            <strong>승인률:</strong> {stats.approve_rate.toFixed(1)}%<br />
            <strong>평균 처리속도:</strong> {stats.avg_speed_sec.toFixed(1)}초<br />
          </div>
          <div style={{ marginBottom: 16 }}>
            <strong>관리자별 승인 건수</strong>
            <table style={{ width: 400, borderCollapse: 'collapse', marginTop: 8 }}>
              <thead>
                <tr><th>관리자</th><th>승인 건수</th></tr>
              </thead>
              <tbody>
                {Object.entries(stats.admin_stats).map(([admin, cnt]) => (
                  <tr key={admin}><td>{admin}</td><td>{cnt}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
          <div>
            <strong>플러그인별 평균 별점/피드백 수</strong>
            <table style={{ width: 600, borderCollapse: 'collapse', marginTop: 8 }}>
              <thead>
                <tr><th>플러그인</th><th>평균 별점</th><th>별점 수</th><th>피드백 수</th></tr>
              </thead>
              <tbody>
                {Object.entries(stats.plugin_stats).map(([pid, s]) => (
                  <tr key={pid}>
                    <td>{pid}</td>
                    <td>{s.avg_rating !== null ? s.avg_rating : '-'}</td>
                    <td>{s.rating_cnt}</td>
                    <td>{s.feedback_cnt}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default PluginMarketplaceStats; 