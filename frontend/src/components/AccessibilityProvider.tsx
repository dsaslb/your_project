'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

interface AccessibilityContextType {
  highContrast: boolean;
  largeText: boolean;
  reducedMotion: boolean;
  toggleHighContrast: () => void;
  toggleLargeText: () => void;
  toggleReducedMotion: () => void;
  resetPreferences: () => void;
}

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined);

export function AccessibilityProvider({ children }: { children: React.ReactNode }) {
  const [highContrast, setHighContrast] = useState(false);
  const [largeText, setLargeText] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);

  // 로컬 스토리지에서 설정 불러오기
  useEffect(() => {
    const savedHighContrast = localStorage.getItem('accessibility-highContrast') === 'true';
    const savedLargeText = localStorage.getItem('accessibility-largeText') === 'true';
    const savedReducedMotion = localStorage.getItem('accessibility-reducedMotion') === 'true';

    setHighContrast(savedHighContrast);
    setLargeText(savedLargeText);
    setReducedMotion(savedReducedMotion);
  }, []);

  // 설정 변경 시 로컬 스토리지에 저장
  useEffect(() => {
    localStorage.setItem('accessibility-highContrast', highContrast.toString());
    localStorage.setItem('accessibility-largeText', largeText.toString());
    localStorage.setItem('accessibility-reducedMotion', reducedMotion.toString());
  }, [highContrast, largeText, reducedMotion]);

  // CSS 변수 적용
  useEffect(() => {
    const root = document.documentElement;
    
    if (highContrast) {
      root.style.setProperty('--high-contrast', '1');
    } else {
      root.style.setProperty('--high-contrast', '0');
    }

    if (largeText) {
      root.style.setProperty('--text-scale', '1.2');
    } else {
      root.style.setProperty('--text-scale', '1');
    }

    if (reducedMotion) {
      root.style.setProperty('--reduced-motion', '1');
    } else {
      root.style.setProperty('--reduced-motion', '0');
    }
  }, [highContrast, largeText, reducedMotion]);

  const toggleHighContrast = () => setHighContrast(prev => !prev);
  const toggleLargeText = () => setLargeText(prev => !prev);
  const toggleReducedMotion = () => setReducedMotion(prev => !prev);

  const resetPreferences = () => {
    setHighContrast(false);
    setLargeText(false);
    setReducedMotion(false);
  };

  return (
    <AccessibilityContext.Provider value={{
      highContrast,
      largeText,
      reducedMotion,
      toggleHighContrast,
      toggleLargeText,
      toggleReducedMotion,
      resetPreferences
    }}>
      {children}
    </AccessibilityContext.Provider>
  );
}

export function useAccessibility() {
  const context = useContext(AccessibilityContext);
  if (context === undefined) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
}

// 접근성 설정 컴포넌트
export function AccessibilitySettings() {
  const {
    highContrast,
    largeText,
    reducedMotion,
    toggleHighContrast,
    toggleLargeText,
    toggleReducedMotion,
    resetPreferences
  } = useAccessibility();

  return (
    <div className="p-4 space-y-4 bg-slate-800/50 border border-slate-600/30 rounded-lg">
      <h3 className="text-lg font-semibold text-white">접근성 설정</h3>
      
      <div className="space-y-3">
        <label className="flex items-center space-x-3 cursor-pointer">
          <input
            type="checkbox"
            checked={highContrast}
            onChange={toggleHighContrast}
            className="w-4 h-4 text-cyan-500 bg-slate-700 border-slate-600 rounded focus:ring-cyan-500"
          />
          <span className="text-slate-300">고대비 모드</span>
        </label>

        <label className="flex items-center space-x-3 cursor-pointer">
          <input
            type="checkbox"
            checked={largeText}
            onChange={toggleLargeText}
            className="w-4 h-4 text-cyan-500 bg-slate-700 border-slate-600 rounded focus:ring-cyan-500"
          />
          <span className="text-slate-300">큰 글씨</span>
        </label>

        <label className="flex items-center space-x-3 cursor-pointer">
          <input
            type="checkbox"
            checked={reducedMotion}
            onChange={toggleReducedMotion}
            className="w-4 h-4 text-cyan-500 bg-slate-700 border-slate-600 rounded focus:ring-cyan-500"
          />
          <span className="text-slate-300">모션 감소</span>
        </label>
      </div>

      <button
        onClick={resetPreferences}
        className="px-3 py-1 text-sm bg-slate-700 text-slate-300 rounded hover:bg-slate-600 transition-colors"
      >
        기본값으로 초기화
      </button>
    </div>
  );
} 