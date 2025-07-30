'use client';

import React, { useEffect, useState } from 'react';

export default function IndustryAdminIntegrationStatusPage() {
  const [integration, setIntegration] = useState<any>(null);
  useEffect(() => {
    // 실제 API 연동(fetch)
    const fetchStatus = () => {
      fetch('/api/integration/status')
        .then(res => res.json())
        .then(setIntegration)
        .catch(() => setIntegration({ api: '오류', external: '오류', history: [] }));
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // 10초마다 자동 갱신
    return () => clearInterval(interval);
  }, []);
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">연동 상태 확인</h1>
      <div className="bg-white rounded shadow p-6 max-w-2xl">
        <h2 className="text-lg font-semibold mb-2">백엔드/외부 시스템 연동</h2>
        <div className="mb-2">- API 서버: <b className={integration?.api === '정상' ? 'text-green-600' : 'text-red-600'}>{integration?.api || '확인 중...'}</b></div>
        <div className="mb-2">- 외부 연동 시스템: <b className={integration?.external === '정상' ? 'text-green-600' : 'text-red-600'}>{integration?.external || '확인 중...'}</b></div>
        <div className="mb-2">- 최근 연동 이력:</div>
        <ul className="list-disc ml-6">
          {(integration?.history || []).map((h: string, i: number) => <li key={i}>{h}</li>)}
        </ul>
      </div>
    </div>
  );
} 