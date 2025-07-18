import React, { useEffect, useState } from 'react';
import PluginManager from '../../components/plugins/PluginManager';
import { apiFetch } from '../../utils/api';

type Branch = { id: string; name: string; };
type Staff = { id: string; name: string; branch_id: string; };
type Sales = { id: string; branch_id: string; amount: number; };

const BrandAdminPage = () => {
  const [branches, setBranches] = useState<Branch[]>([]);
  const [staffs, setStaffs] = useState<Staff[]>([]);
  const [sales, setSales] = useState<Sales[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const branchesData = await apiFetch<Branch[]>('/api/branches');
        const staffsData = await apiFetch<Staff[]>('/api/users');
        // 매출은 샘플 데이터 사용
        setBranches(branchesData);
        setStaffs(staffsData);
        setSales([
          { id: 'sale1', branch_id: branchesData[0]?.id || 'b1', amount: 1000000 },
          { id: 'sale2', branch_id: branchesData[1]?.id || 'b2', amount: 800000 },
        ]);
      } catch (e) {
        setBranches([
          { id: 'b1', name: '테스트 매장1' },
          { id: 'b2', name: '테스트 매장2' },
        ]);
        setStaffs([
          { id: 'u1', name: '직원1', branch_id: 'b1' },
          { id: 'u2', name: '직원2', branch_id: 'b2' },
        ]);
        setSales([
          { id: 'sale1', branch_id: 'b1', amount: 1000000 },
          { id: 'sale2', branch_id: 'b2', amount: 800000 },
        ]);
        setError('API 연동 실패, 샘플 데이터로 대체');
      }
      setLoading(false);
    }
    fetchData();
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">브랜드 관리자 대시보드</h1>
      <div className="mb-6">
        <h2 className="text-xl font-semibold">매장/직원/매출 관리</h2>
        {loading ? (
          <div>로딩 중...</div>
        ) : (
          <>
            <table className="w-full text-sm mb-4">
              <thead>
                <tr>
                  <th>매장명</th>
                  <th>직원명</th>
                  <th>매출(원)</th>
                </tr>
              </thead>
              <tbody>
                {branches.map((branch) => (
                  staffs.filter((s) => s.branch_id === branch.id).map((staff) => (
                    <tr key={branch.id + staff.id}>
                      <td>{branch.name}</td>
                      <td>{staff.name}</td>
                      <td>{sales.find((sale) => sale.branch_id === branch.id)?.amount?.toLocaleString() || '-'}</td>
                    </tr>
                  ))
                ))}
              </tbody>
            </table>
          </>
        )}
        {error && <div className="text-red-500 mt-2">{error}</div>}
      </div>
      <div className="mb-6">
        <h2 className="text-xl font-semibold">플러그인 관리</h2>
        <PluginManager level="brand" />
      </div>
      <div className="mb-6">
        <h2 className="text-xl font-semibold">AI 분석 리포트</h2>
        <div className="bg-white rounded shadow p-4 mt-2">간단한 AI 분석 결과 샘플</div>
      </div>
    </div>
  );
};

export default BrandAdminPage; 