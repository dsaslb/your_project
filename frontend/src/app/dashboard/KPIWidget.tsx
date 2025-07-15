import React, { useEffect, useState } from 'react';
// 실시간 KPI 위젯 (매출, 주문, 고객, 재고 등)
// 글로벌 다국어(i18n) 및 접근성(aria-label) 지원 구조 포함

// 다국어 메시지 예시
const messages = {
  sales: { ko: '매출', en: 'Sales' },
  orders: { ko: '주문', en: 'Orders' },
  customers: { ko: '고객', en: 'Customers' },
  inventory: { ko: '재고', en: 'Inventory' },
  loading: { ko: '로딩 중...', en: 'Loading...' }
};

// 언어 감지(기본값: 한국어)
function getLang() {
  if (typeof window !== 'undefined') {
    return (navigator.language || 'ko').startsWith('en') ? 'en' : 'ko';
  }
  return 'ko';
}

const KPIWidget: React.FC = () => {
  const [kpi, setKpi] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const lang = getLang();

  useEffect(() => {
    // 실시간 KPI 데이터 API 호출 (예시)
    fetch('/api/realtime/dashboard')
      .then(res => res.json())
      .then(data => {
        setKpi({
          sales: data.performance_metrics?.sales_today || 0,
          orders: data.performance_metrics?.orders_today || 0,
          customers: data.performance_metrics?.customers_today || 0,
          inventory: data.performance_metrics?.inventory_total || 0
        });
        setLoading(false);
      });
  }, []);

  if (loading) return <div aria-label={messages.loading[lang]}>{messages.loading[lang]}</div>;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4" aria-label="KPI 위젯">
      <div className="bg-white dark:bg-gray-900 rounded-lg p-4 shadow" aria-label={messages.sales[lang]}>
        <div className="text-xs text-gray-500 mb-1">{messages.sales[lang]}</div>
        <div className="text-2xl font-bold">{kpi.sales.toLocaleString()}</div>
      </div>
      <div className="bg-white dark:bg-gray-900 rounded-lg p-4 shadow" aria-label={messages.orders[lang]}>
        <div className="text-xs text-gray-500 mb-1">{messages.orders[lang]}</div>
        <div className="text-2xl font-bold">{kpi.orders.toLocaleString()}</div>
      </div>
      <div className="bg-white dark:bg-gray-900 rounded-lg p-4 shadow" aria-label={messages.customers[lang]}>
        <div className="text-xs text-gray-500 mb-1">{messages.customers[lang]}</div>
        <div className="text-2xl font-bold">{kpi.customers.toLocaleString()}</div>
      </div>
      <div className="bg-white dark:bg-gray-900 rounded-lg p-4 shadow" aria-label={messages.inventory[lang]}>
        <div className="text-xs text-gray-500 mb-1">{messages.inventory[lang]}</div>
        <div className="text-2xl font-bold">{kpi.inventory.toLocaleString()}</div>
      </div>
    </div>
  );
};

export default KPIWidget; 