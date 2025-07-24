import React from 'react';
import { useI18n } from './i18n';

const LanguageSwitcher: React.FC = () => {
  const { lang, setLang } = useI18n();
  return (
    <div className="flex gap-2 items-center">
      <button
        className={`px-2 py-1 rounded ${lang === 'ko' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        onClick={() => setLang('ko')}
        disabled={lang === 'ko'}
      >
        한국어
      </button>
      <button
        className={`px-2 py-1 rounded ${lang === 'en' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        onClick={() => setLang('en')}
        disabled={lang === 'en'}
      >
        English
      </button>
    </div>
  );
};

export default LanguageSwitcher; 