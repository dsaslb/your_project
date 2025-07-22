import { createContext, useContext, useState, ReactNode } from 'react';

// 다국어 메시지 예시
const messages = {
  ko: {
    dashboard: '운영자/관리자 실시간 대시보드',
    serviceStatus: '서비스 상태',
    logs: '장애/복구 로그',
    alerts: '장애 알림',
    noLogs: '로그 없음',
    noAlerts: '알림 없음',
    loading: '불러오는 중...',
    autoRefresh: '30초마다 자동 새로고침',
    unauthorized: '접근 권한이 없습니다.',
  },
  en: {
    dashboard: 'Admin/Operator Realtime Dashboard',
    serviceStatus: 'Service Status',
    logs: 'Incident/Recovery Logs',
    alerts: 'Incident Alerts',
    noLogs: 'No logs',
    noAlerts: 'No alerts',
    loading: 'Loading...',
    autoRefresh: 'Auto refresh every 30 seconds',
    unauthorized: 'Unauthorized access.',
  },
};

interface I18nContextProps {
  lang: 'ko' | 'en';
  setLang: (lang: 'ko' | 'en') => void;
  t: (key: keyof typeof messages['ko']) => string;
}

const I18nContext = createContext<I18nContextProps | undefined>(undefined);

export const useI18n = () => {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useI18n must be used within I18nProvider');
  return ctx;
};

export const I18nProvider = ({ children }: { children: ReactNode }) => {
  const [lang, setLang] = useState<'ko' | 'en'>('ko');
  const t = (key: keyof typeof messages['ko']) => messages[lang][key] || key;
  return (
    <I18nContext.Provider value={{ lang, setLang, t }}>
      {children}
    </I18nContext.Provider>
  );
}; 