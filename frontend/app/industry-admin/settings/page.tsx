'use client';

import React, { useEffect, useState } from 'react';

export default function IndustryAdminSettingsPage() {
  const [settings, setSettings] = useState<any>(null);
  useEffect(() => {
    // 실제 API 연동(fetch)
    const fetchSettings = () => {
      fetch('/api/industry-admin/settings')
        .then(res => res.json())
        .then(setSettings)
        .catch(() => setSettings({ lang: '한국어', email: 'admin@example.com', backup: '매일 자동', alarm: 'ON', etc: '...' }));
    };
    fetchSettings();
    const interval = setInterval(fetchSettings, 10000); // 10초마다 자동 갱신
    return () => clearInterval(interval);
  }, []);
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">설정</h1>
      <div className="bg-white rounded shadow p-6 max-w-xl">
        <h2 className="text-lg font-semibold mb-2">시스템 환경설정</h2>
        <div className="mb-2">- 기본 언어: <b>{settings?.lang || '확인 중...'}</b></div>
        <div className="mb-2">- 알림 수신: <b>{settings?.alarm || '확인 중...'}</b></div>
        <div className="mb-2">- 관리자 이메일: <b>{settings?.email || '확인 중...'}</b></div>
        <div className="mb-2">- 데이터 백업: <b>{settings?.backup || '확인 중...'}</b></div>
        <div className="mb-2">- 기타 옵션: {settings?.etc || '확인 중...'}</div>
      </div>
    </div>
  );
} 