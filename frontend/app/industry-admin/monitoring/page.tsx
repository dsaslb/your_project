'use client';

import React, { useEffect, useState } from 'react';
import { Line, Pie } from 'react-chartjs-2';

interface KpiData {
  dates: string[];
  values: number[];
}

interface AlertStats {
  success: number;
  warning: number;
  error: number;
}

export default function IndustryAdminMonitoringPage() {
  const [status, setStatus] = useState('정상');
  const [alerts, setAlerts] = useState<string[]>([]);
  const [kpi, setKpi] = useState<KpiData>({ dates: [], values: [] });
  const [alertStats, setAlertStats] = useState<AlertStats>({ success: 0, warning: 0, error: 0 });

  useEffect(() => {
    // WebSocket 연동 (더미 주소)
    const ws = new WebSocket('ws://localhost:5000/ws/monitoring');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'status') setStatus(data.value);
      if (data.type === 'alert') setAlerts(prev => [data.message, ...prev].slice(0, 10));
      if (data.type === 'kpi') setKpi(data.value);
      if (data.type === 'alertStats') setAlertStats(data.value);
    };
    return () => ws.close();
  }, []);

  // 더미 실시간 데이터 (WebSocket 미연결 시)
  useEffect(() => {
    const interval = setInterval(() => {
      setKpi((prev: KpiData) => {
        const now = new Date();
        const dates = [...(prev.dates || []), now.toLocaleTimeString()].slice(-7);
        return {
          dates,
          values: [...(prev.values || []), Math.floor(Math.random() * 100 + 100)].slice(-7),
        };
      });
      setAlertStats({
        success: Math.floor(Math.random() * 10 + 20),
        warning: Math.floor(Math.random() * 3),
        error: Math.floor(Math.random() * 2),
      });
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">실시간 모니터링</h1>
      <div className="bg-white rounded shadow p-6 max-w-2xl mb-6">
        <h2 className="text-lg font-semibold mb-2">서버 상태</h2>
        <div className="mb-2">- 서버 상태: <b className={status === '정상' ? 'text-green-600' : 'text-red-600'}>{status}</b></div>
        <div className="mb-2">- 실시간 알림:</div>
        <ul className="list-disc ml-6">
          {alerts.map((msg, i) => <li key={i}>{msg}</li>)}
        </ul>
      </div>
      <div className="bg-white rounded shadow p-6 max-w-2xl mb-6">
        <h2 className="text-lg font-semibold mb-2">실시간 KPI 변화</h2>
        <Line
          data={{
            labels: kpi.dates,
            datasets: [
              { label: '서버 부하', data: kpi.values, borderColor: 'rgba(59,130,246,1)', backgroundColor: 'rgba(59,130,246,0.2)', fill: true },
            ]
          }}
          options={{ responsive: true, plugins: { legend: { position: 'top' } } }}
        />
      </div>
      <div className="bg-white rounded shadow p-6 max-w-2xl">
        <h2 className="text-lg font-semibold mb-2">알림/이상탐지 통계</h2>
        <Pie
          data={{
            labels: ['성공', '경고', '오류'],
            datasets: [
              { data: [alertStats.success, alertStats.warning, alertStats.error], backgroundColor: ['#22c55e', '#facc15', '#ef4444'] }
            ]
          }}
          options={{ responsive: true, plugins: { legend: { position: 'bottom' } } }}
        />
      </div>
    </div>
  );
} 