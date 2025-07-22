import React, { useEffect, useState } from 'react';
import { useToast } from '../../components/GlobalToast';

interface Payment {
  id: string;
  amount: number;
  currency: string;
  status: string;
  created: number;
  receipt_url?: string;
}

const PaymentDashboard: React.FC = () => {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [amount, setAmount] = useState('');
  const [desc, setDesc] = useState('서비스 결제');
  const { showToast } = useToast();

  const fetchPayments = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/admin/payments/history');
      const data = await res.json();
      setPayments(data.payments || []);
    } catch {
      showToast('결제 내역을 불러오지 못했습니다.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPayments();
  }, []);

  const handleCheckout = async () => {
    if (!amount || isNaN(Number(amount))) {
      showToast('금액을 입력하세요.', 'warning');
      return;
    }
    try {
      const res = await fetch('/api/admin/payments/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: Number(amount),
          description: desc,
          success_url: window.location.origin + '/admin-dashboard/payments?success=1',
          cancel_url: window.location.origin + '/admin-dashboard/payments?cancel=1',
        }),
      });
      const data = await res.json();
      if (data.checkout_url) {
        window.open(data.checkout_url, '_blank');
        showToast('결제 페이지가 열렸습니다.', 'success');
      } else {
        showToast(data.error || '결제 생성 실패', 'error');
      }
    } catch {
      showToast('결제 생성 실패', 'error');
    }
  };

  return (
    <div className="p-4 max-w-3xl mx-auto">
      <h2 className="text-xl font-bold mb-4">결제 관리</h2>
      <div className="mb-4 flex gap-2 items-end">
        <input
          type="number"
          placeholder="금액(USD)"
          value={amount}
          onChange={e => setAmount(e.target.value)}
          className="border rounded px-2 py-1 text-sm w-32"
        />
        <input
          type="text"
          placeholder="설명"
          value={desc}
          onChange={e => setDesc(e.target.value)}
          className="border rounded px-2 py-1 text-sm w-64"
        />
        <button
          className="bg-blue-600 text-white px-3 py-1 rounded"
          onClick={handleCheckout}
        >
          결제 생성(Stripe)
        </button>
      </div>
      <h3 className="font-semibold mb-2">최근 결제 내역</h3>
      {loading ? (
        <div className="text-gray-500">불러오는 중...</div>
      ) : (
        <table className="w-full text-sm border">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-2">ID</th>
              <th className="p-2">금액</th>
              <th className="p-2">통화</th>
              <th className="p-2">상태</th>
              <th className="p-2">일시</th>
              <th className="p-2">영수증</th>
            </tr>
          </thead>
          <tbody>
            {payments.map((p) => (
              <tr key={p.id} className="border-t">
                <td className="p-2">{p.id}</td>
                <td className="p-2">{p.amount}</td>
                <td className="p-2">{p.currency}</td>
                <td className="p-2">{p.status}</td>
                <td className="p-2">{new Date(p.created * 1000).toLocaleString()}</td>
                <td className="p-2">
                  {p.receipt_url ? (
                    <a href={p.receipt_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">
                      영수증
                    </a>
                  ) : (
                    '-'
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default PaymentDashboard; 