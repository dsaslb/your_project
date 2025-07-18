import React, { useEffect, useState } from 'react';
import PluginManager from '../components/plugins/PluginManager';
import { apiFetch } from '../utils/api';

type Work = { id: string; date: string; status: string; };
type Salary = { id: string; month: string; amount: number; };
type MyPlugin = { id: string; name: string; is_active: boolean; };

const UserPage = () => {
  const [works, setWorks] = useState<Work[]>([]);
  const [salaries, setSalaries] = useState<Salary[]>([]);
  const [myPlugins, setMyPlugins] = useState<MyPlugin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        // 실제 API 연동 시 아래 주석 해제
        // const worksData = await apiFetch<Work[]>('/api/works');
        // const salariesData = await apiFetch<Salary[]>('/api/salaries');
        // const pluginsData = await apiFetch<MyPlugin[]>('/api/plugins?level=user');
        setWorks([
          { id: 'w1', date: '2024-06-01', status: '출근' },
          { id: 'w2', date: '2024-06-02', status: '퇴근' },
        ]);
        setSalaries([
          { id: 's1', month: '2024-05', amount: 2000000 },
        ]);
        setMyPlugins([
          { id: 'attendance', name: '출근 관리', is_active: true },
          { id: 'inventory', name: '재고 관리', is_active: false },
        ]);
      } catch (e) {
        setWorks([
          { id: 'w1', date: '2024-06-01', status: '출근' },
          { id: 'w2', date: '2024-06-02', status: '퇴근' },
        ]);
        setSalaries([
          { id: 's1', month: '2024-05', amount: 2000000 },
        ]);
        setMyPlugins([
          { id: 'attendance', name: '출근 관리', is_active: true },
          { id: 'inventory', name: '재고 관리', is_active: false },
        ]);
        setError('API 연동 실패, 샘플 데이터로 대체');
      }
      setLoading(false);
    }
    fetchData();
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">직원(사용자) 페이지</h1>
      <div className="mb-6">
        <h2 className="text-xl font-semibold">근무/급여/플러그인</h2>
        {loading ? (
          <div>로딩 중...</div>
        ) : (
          <>
            <table className="w-full text-sm mb-4">
              <thead>
                <tr>
                  <th>날짜</th>
                  <th>근무상태</th>
                  <th>급여(원)</th>
                  <th>플러그인</th>
                </tr>
              </thead>
              <tbody>
                {works.map((work, idx) => (
                  <tr key={work.id}>
                    <td>{work.date}</td>
                    <td>{work.status}</td>
                    <td>{salaries[idx]?.amount?.toLocaleString() || '-'}</td>
                    <td>{myPlugins[idx]?.name}({myPlugins[idx]?.is_active ? 'ON' : 'OFF'})</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
        {error && <div className="text-red-500 mt-2">{error}</div>}
      </div>
      <div className="mb-6">
        <h2 className="text-xl font-semibold">내 플러그인</h2>
        <PluginManager level="user" />
      </div>
    </div>
  );
};

export default UserPage; 