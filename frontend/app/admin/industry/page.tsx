import React, { useEffect, useState } from 'react';
import PluginManager from '../../components/plugins/PluginManager';
import { apiFetch } from '../../utils/api';

type Brand = { id: string; name: string; };
type Branch = { id: string; name: string; brand_id: string; };

const IndustryAdminPage = () => {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const brandsData = await apiFetch<Brand[]>('/api/brands');
        const branchesData = await apiFetch<Branch[]>('/api/branches');
        setBrands(brandsData);
        setBranches(branchesData);
      } catch (e) {
        setBrands([
          { id: 'b1', name: '테스트 브랜드1' },
          { id: 'b2', name: '테스트 브랜드2' },
        ]);
        setBranches([
          { id: 's1', name: '테스트 매장1', brand_id: 'b1' },
          { id: 's2', name: '테스트 매장2', brand_id: 'b2' },
        ]);
        setError('API 연동 실패, 샘플 데이터로 대체');
      }
      setLoading(false);
    }
    fetchData();
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">업종(레스토랑) 관리자 대시보드</h1>
      <div className="mb-6">
        <h2 className="text-xl font-semibold">전체 브랜드/매장 현황</h2>
        {loading ? (
          <div>로딩 중...</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th>브랜드명</th>
                <th>매장명</th>
              </tr>
            </thead>
            <tbody>
              {brands.map((brand) => (
                branches.filter((b) => b.brand_id === brand.id).map((branch) => (
                  <tr key={brand.id + branch.id}>
                    <td>{brand.name}</td>
                    <td>{branch.name}</td>
                  </tr>
                ))
              ))}
            </tbody>
          </table>
        )}
        {error && <div className="text-red-500 mt-2">{error}</div>}
      </div>
      <div className="mb-6">
        <h2 className="text-xl font-semibold">플러그인 관리</h2>
        <PluginManager level="industry" />
      </div>
    </div>
  );
};

export default IndustryAdminPage; 