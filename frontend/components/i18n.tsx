import React, { createContext, useContext, useMemo } from 'react';
import en from './locales/en.json';
import ko from './locales/ko.json';

const resources: Record<string, Record<string, string>> = { en, ko };

const I18nContext = createContext<{ t: (key: string) => string; lang: string; setLang: (lang: string) => void }>({
  t: (k) => k,
  lang: 'ko',
  setLang: () => {},
});

export const I18nProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [lang, setLang] = React.useState('ko');
  const t = useMemo(() => (key: string) => resources[lang]?.[key] || key, [lang]);
  return (
    <I18nContext.Provider value={{ t, lang, setLang }}>
      {children}
    </I18nContext.Provider>
  );
};

export const useI18n = () => useContext(I18nContext); 