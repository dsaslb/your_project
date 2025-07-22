import React, { useEffect, useState } from 'react';

interface Summary {
  total_sales: number;
  total_users: number;
  active_users: number;
  total_plugins: number;
  active_plugins: number;
  date: string;
}
interface Timeseries {
  sales: { date: string; sales: number }[];
  users: { date: string; users: number }[];
}
interface PluginStat {
  name: string;
  usage: number;
  sales: number;
}

const StatsDashboard: React.FC = () => {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [timeseries, setTimeseries] = useState<Timeseries | null>(null);
  const [pluginStats, setPluginStats] = useState<PluginStat[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const [summaryRes, timeseriesRes, pluginRes] = await Promise.all([
        fetch('/api/admin/stats/summary'),
        fetch(`/api/admin/stats/timeseries?days=${days}`),
        fetch('/api/admin/stats/plugin'),
      ]);
      setSummary(await summaryRes.json());
      setTimeseries(await timeseriesRes.json());
      setPluginStats((await pluginRes.json()).plugins || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    // eslint-disable-next-line
  }, [days]);

  return (
    <div className="p-4 max-w-5xl mx-auto">
      <h2 className="text-xl font-bold mb-4">통계/리포트 대시보드</h2>
      {loading ? (
        <div className="text-gray-500">불러오는 중...</div>
      ) : (
        <>
          {/* 주요 지표 카드 */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <StatCard label="총 매출" value={summary?.total_sales?.toLocaleString() + ' USD'} />
            <StatCard label="총 사용자" value={summary?.total_users?.toLocaleString()} />
            <StatCard label="활성 사용자" value={summary?.active_users?.toLocaleString()} />
            <StatCard label="플러그인(활성/전체)" value={`${summary?.active_plugins}/${summary?.total_plugins}`} />
          </div>
          {/* 기간별 차트 (간단한 SVG 차트 예시) */}
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-semibold">기간별 매출/사용자</span>
              <select value={days} onChange={e => setDays(Number(e.target.value))} className="border rounded px-2 py-1 text-sm">
                <option value={7}>7일</option>
                <option value={30}>30일</option>
                <option value={90}>90일</option>
              </select>
            </div>
            <div className="flex flex-col md:flex-row gap-4">
              <LineChart data={timeseries?.sales || []} label="매출" color="#2563eb" />
              <LineChart data={timeseries?.users || []} label="사용자" color="#10b981" />
            </div>
          </div>
          {/* 플러그인별 통계 */}
          <div>
            <h3 className="font-semibold mb-2">플러그인별 통계</h3>
            <table className="w-full text-sm border">
              <thead>
                <tr className="bg-gray-100">
                  <th className="p-2">플러그인</th>
                  <th className="p-2">사용량</th>
                  <th className="p-2">매출</th>
                </tr>
              </thead>
              <tbody>
                {pluginStats.map((p) => (
                  <tr key={p.name} className="border-t">
                    <td className="p-2">{p.name}</td>
                    <td className="p-2">{p.usage}</td>
                    <td className="p-2">{p.sales.toLocaleString()} USD</td>
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

const StatCard: React.FC<{ label: string; value?: string }> = ({ label, value }) => (
  <div className="bg-white rounded shadow p-4 flex flex-col items-center">
    <span className="text-xs text-gray-500 mb-1">{label}</span>
    <span className="text-lg font-bold">{value || '-'}</span>
  </div>
);

// 간단한 SVG 라인차트 컴포넌트
const LineChart: React.FC<{ data: any[]; label: string; color: string }> = ({ data, label, color }) => {
  if (!data || data.length === 0) return <div className="text-gray-400">데이터 없음</div>;
  const max = Math.max(...data.map((d) => d[label === '매출' ? 'sales' : 'users']));
  const min = Math.min(...data.map((d) => d[label === '매출' ? 'sales' : 'users']));
  const points = data.map((d, i) => {
    const v = d[label === '매출' ? 'sales' : 'users'];
    const y = 80 - ((v - min) / (max - min || 1)) * 60;
    const x = 20 + (i * 160) / (data.length - 1 || 1);
    return `${x},${y}`;
  });
  return (
    <div className="bg-white rounded shadow p-4 flex-1">
      <div className="text-xs text-gray-500 mb-1">{label}</div>
      <svg width={200} height={100}>
        <polyline
          fill="none"
          stroke={color}
          strokeWidth={2}
          points={points.join(' ')}
        />
        {data.map((d, i) => {
          const v = d[label === '매출' ? 'sales' : 'users'];
          const y = 80 - ((v - min) / (max - min || 1)) * 60;
          const x = 20 + (i * 160) / (data.length - 1 || 1);
          return <circle key={i} cx={x} cy={y} r={2} fill={color} />;
        })}
      </svg>
      <div className="flex justify-between text-xs text-gray-400 mt-1">
        <span>{data[0]?.date}</span>
        <span>{data[data.length - 1]?.date}</span>
      </div>
    </div>
  );
};

export default StatsDashboard; 