"use client";

import React, { useState } from 'react';

const defaultSettings = {
  chartColor: '#3b82f6',
  refreshInterval: 60,
  enablePush: true,
  enableSSE: true,
};

export default function AdminSettingsPage() {
  const [settings, setSettings] = useState(defaultSettings);
  return (
    <main className="max-w-xl mx-auto p-6" aria-label="운영자 설정 패널">
      <h1 className="text-2xl font-bold mb-4">운영자 설정 패널</h1>
      <form className="space-y-4" aria-label="설정 폼">
        <div>
          <label htmlFor="chartColor" className="block font-semibold mb-1">차트 기본 색상</label>
          <input id="chartColor" type="color" value={settings.chartColor} onChange={e => setSettings(s => ({ ...s, chartColor: e.target.value }))} aria-label="차트 색상 선택" />
        </div>
        <div>
          <label htmlFor="refreshInterval" className="block font-semibold mb-1">자동 새로고침 주기(초)</label>
          <input id="refreshInterval" type="number" min={10} max={600} value={settings.refreshInterval} onChange={e => setSettings(s => ({ ...s, refreshInterval: Number(e.target.value) }))} aria-label="새로고침 주기 입력" />
        </div>
        <div>
          <label className="block font-semibold mb-1">실시간 알림(SSE)</label>
          <input type="checkbox" checked={settings.enableSSE} onChange={e => setSettings(s => ({ ...s, enableSSE: e.target.checked }))} aria-label="SSE 알림 활성화" /> SSE 사용
        </div>
        <div>
          <label className="block font-semibold mb-1">푸시 알림</label>
          <input type="checkbox" checked={settings.enablePush} onChange={e => setSettings(s => ({ ...s, enablePush: e.target.checked }))} aria-label="푸시 알림 활성화" /> 푸시 사용
        </div>
        <button type="submit" className="btn" aria-label="설정 저장">설정 저장</button>
      </form>
      <div className="mt-4 text-xs text-gray-500">설정은 로컬에만 저장됩니다. (실제 운영환경에서는 서버 연동 필요)</div>
    </main>
  );
} 