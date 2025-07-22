import React, { useEffect, useState, useRef } from 'react';
import { useToast } from '../../components/GlobalToast';
import { useI18n } from '../../components/i18n';

interface StatusData {
  status: string;
  output: string;
}

interface LogsData {
  logs: string[];
}

interface AlertsData {
  alerts: string[];
}

const fetchJson = async (url: string) => {
  const res = await fetch(url);
  return res.json();
};

const OpsStatus: React.FC = () => {
  const [status, setStatus] = useState<StatusData | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [alerts, setAlerts] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const prevAlertsRef = useRef<string[]>([]);
  const { showToast } = useToast();
  const { t, lang, setLang } = useI18n();

  const fetchAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statusData, logsData, alertsData] = await Promise.all([
        fetchJson('/api/admin/ops/status'),
        fetchJson('/api/admin/ops/logs'),
        fetchJson('/api/admin/ops/alerts'),
      ]);
      setStatus(statusData);
      setLogs(logsData.logs || []);
      setAlerts(alertsData.alerts || []);
      // 새 알림 Toast
      const prevAlerts = prevAlertsRef.current;
      const newAlerts = (alertsData.alerts || []).filter(
        (a: string) => !prevAlerts.includes(a)
      );
      newAlerts.forEach((alert: string) => {
        showToast(alert, 'error', 8000);
      });
      prevAlertsRef.current = alertsData.alerts || [];
    } catch (e: any) {
      setError(e.message || t('loading'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold" tabIndex={0} aria-label={t('dashboard')}>{t('dashboard')}</h1>
        <div>
          <label htmlFor="lang-select" className="sr-only">언어</label>
          <select
            id="lang-select"
            value={lang}
            onChange={e => setLang(e.target.value as 'ko' | 'en')}
            className="border rounded px-2 py-1 text-sm"
            aria-label="언어 선택"
          >
            <option value="ko">한국어</option>
            <option value="en">English</option>
          </select>
        </div>
      </div>
      {loading && <div className="text-gray-500" aria-live="polite">{t('loading')}</div>}
      {error && <div className="text-red-500" role="alert">{error}</div>}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
        {/* 서비스 상태 */}
        <section className="bg-white rounded shadow p-4" aria-labelledby="service-status-heading">
          <h2 id="service-status-heading" className="text-lg font-semibold mb-2">{t('serviceStatus')}</h2>
          <pre className="text-xs bg-gray-100 rounded p-2 overflow-x-auto" tabIndex={0} aria-label={t('serviceStatus')}>
            {status?.output || t('serviceStatus')}
          </pre>
        </section>
        {/* 장애/복구 로그 */}
        <section className="bg-white rounded shadow p-4" aria-labelledby="logs-heading">
          <h2 id="logs-heading" className="text-lg font-semibold mb-2">{t('logs')}</h2>
          <div className="h-64 overflow-y-auto text-xs bg-gray-100 rounded p-2" tabIndex={0} aria-label={t('logs')}>
            {logs.length === 0 ? (
              <div className="text-gray-400">{t('noLogs')}</div>
            ) : (
              logs.map((line, i) => (
                <div key={i} className={line.includes('[ALERT]') ? 'text-red-600 font-bold' : ''}>
                  {line}
                </div>
              ))
            )}
          </div>
        </section>
        {/* 장애 알림 */}
        <section className="bg-white rounded shadow p-4" aria-labelledby="alerts-heading">
          <h2 id="alerts-heading" className="text-lg font-semibold mb-2">{t('alerts')}</h2>
          <div className="h-64 overflow-y-auto text-xs bg-gray-100 rounded p-2" tabIndex={0} aria-label={t('alerts')}>
            {alerts.length === 0 ? (
              <div className="text-gray-400">{t('noAlerts')}</div>
            ) : (
              alerts.map((alert, i) => (
                <div key={i} className="text-red-600 font-bold">
                  {alert}
                </div>
              ))
            )}
          </div>
        </section>
      </div>
      <div className="text-xs text-gray-400 mt-4" aria-live="polite">{t('autoRefresh')}</div>
    </div>
  );
};

export default OpsStatus; 