import React, { useEffect, useState } from 'react';
import PluginManager from '../../components/plugins/PluginManager';
import { apiFetch } from '../../utils/api';

type Staff = { id: string; name: string; };
type Sales = { id: string; amount: number; };
type Order = { id: string; item: string; qty: number; };
type Inventory = { id: string; item: string; stock: number; };

const BranchAdminPage = () => {
  const [staffs, setStaffs] = useState<Staff[]>([]);
  const [sales, setSales] = useState<Sales[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [inventory, setInventory] = useState<Inventory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const staffsData = await apiFetch<Staff[]>('/api/users');
        setStaffs(staffsData);
        setSales([
          { id: 'sale1', amount: 500000 },
        ]);
        setOrders([
          { id: 'order1', item: '식자재A', qty: 10 },
        ]);
        setInventory([
          { id: 'inv1', item: '식자재A', stock: 50 },
        ]);
      } catch (e) {
        setStaffs([
          { id: 'u1', name: '직원1' },
          { id: 'u2', name: '직원2' },
        ]);
        setSales([
          { id: 'sale1', amount: 500000 },
        ]);
        setOrders([
          { id: 'order1', item: '식자재A', qty: 10 },
        ]);
        setInventory([
          { id: 'inv1', item: '식자재A', stock: 50 },
        ]);
        setError('API 연동 실패, 샘플 데이터로 대체');
      }
      setLoading(false);
    }
    fetchData();
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">매장 관리자 대시보드</h1>
      <div className="mb-6">
        <h2 className="text-xl font-semibold">직원/매출/발주/재고 관리</h2>
        {loading ? (
          <div>로딩 중...</div>
        ) : (
          <>
            <table className="w-full text-sm mb-4">
              <thead>
                <tr>
                  <th>직원명</th>
                  <th>매출(원)</th>
                  <th>발주</th>
                  <th>재고</th>
                </tr>
              </thead>
              <tbody>
                {staffs.map((staff) => (
                  <tr key={staff.id}>
                    <td>{staff.name}</td>
                    <td>{sales[0]?.amount?.toLocaleString() || '-'}</td>
                    <td>{orders[0]?.item}({orders[0]?.qty})</td>
                    <td>{inventory[0]?.item}({inventory[0]?.stock})</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
        {error && <div className="text-red-500 mt-2">{error}</div>}
      </div>
      <div className="mb-6">
        <h2 className="text-xl font-semibold">플러그인 권한 관리</h2>
        <PluginManager level="branch" />
      </div>
    </div>
  );
};

export default BranchAdminPage; 