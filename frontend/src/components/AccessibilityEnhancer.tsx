import React, { useEffect, useState } from 'react';

interface AccessibilityEnhancerProps {
  children: React.ReactNode;
}

export const AccessibilityEnhancer: React.FC<AccessibilityEnhancerProps> = ({ children }) => {
  const [isHighContrast, setIsHighContrast] = useState(false);
  const [isReducedMotion, setIsReducedMotion] = useState(false);
  const [fontSize, setFontSize] = useState(16);

  useEffect(() => {
    // 시스템 접근성 설정 감지
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setIsReducedMotion(mediaQuery.matches);

    const handleMotionChange = (e: MediaQueryListEvent) => {
      setIsReducedMotion(e.matches);
    };

    mediaQuery.addEventListener('change', handleMotionChange);

    return () => mediaQuery.removeEventListener('change', handleMotionChange);
  }, []);

  useEffect(() => {
    // 전역 CSS 변수 설정
    document.documentElement.style.setProperty('--font-size', `${fontSize}px`);
    document.documentElement.style.setProperty('--high-contrast', isHighContrast ? '1' : '0');
    document.documentElement.style.setProperty('--reduced-motion', isReducedMotion ? '1' : '0');
  }, [fontSize, isHighContrast, isReducedMotion]);

  return (
    <div 
      className={`accessibility-enhancer ${isHighContrast ? 'high-contrast' : ''} ${isReducedMotion ? 'reduced-motion' : ''}`}
      style={{ fontSize: `${fontSize}px` }}
    >
      {children}
    </div>
  );
};

// 접근성 컨트롤 컴포넌트
export const AccessibilityControls: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const increaseFontSize = () => {
    const currentSize = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--font-size')) || 16;
    document.documentElement.style.setProperty('--font-size', `${Math.min(currentSize + 2, 24)}px`);
  };

  const decreaseFontSize = () => {
    const currentSize = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--font-size')) || 16;
    document.documentElement.style.setProperty('--font-size', `${Math.max(currentSize - 2, 12)}px`);
  };

  const toggleHighContrast = () => {
    const current = getComputedStyle(document.documentElement).getPropertyValue('--high-contrast') === '1';
    document.documentElement.style.setProperty('--high-contrast', current ? '0' : '1');
  };

  return (
    <div className="accessibility-controls">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="accessibility-toggle"
        aria-label="접근성 설정 열기"
        aria-expanded={isOpen}
      >
        <span role="img" aria-label="접근성">♿</span>
      </button>
      
      {isOpen && (
        <div className="accessibility-panel" role="dialog" aria-label="접근성 설정">
          <h3>접근성 설정</h3>
          
          <div className="control-group">
            <label htmlFor="font-size">글자 크기</label>
            <div className="font-controls">
              <button onClick={decreaseFontSize} aria-label="글자 크기 줄이기">A-</button>
              <button onClick={increaseFontSize} aria-label="글자 크기 늘리기">A+</button>
            </div>
          </div>
          
          <div className="control-group">
            <label htmlFor="high-contrast">
              <input
                type="checkbox"
                id="high-contrast"
                onChange={toggleHighContrast}
                aria-label="고대비 모드"
              />
              고대비 모드
            </label>
          </div>
          
          <button
            onClick={() => setIsOpen(false)}
            className="close-button"
            aria-label="접근성 설정 닫기"
          >
            닫기
          </button>
        </div>
      )}
    </div>
  );
};

// 접근성 스타일
export const accessibilityStyles = `
  .accessibility-enhancer {
    --font-size: 16px;
    --high-contrast: 0;
    --reduced-motion: 0;
  }

  .accessibility-enhancer.high-contrast {
    filter: contrast(1.5) brightness(1.2);
  }

  .accessibility-enhancer.reduced-motion * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }

  .accessibility-controls {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
  }

  .accessibility-toggle {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: #007bff;
    color: white;
    border: none;
    cursor: pointer;
    font-size: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    transition: transform 0.2s;
  }

  .accessibility-toggle:hover {
    transform: scale(1.1);
  }

  .accessibility-toggle:focus {
    outline: 3px solid #ff6b6b;
    outline-offset: 2px;
  }

  .accessibility-panel {
    position: absolute;
    bottom: 70px;
    right: 0;
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    min-width: 250px;
  }

  .accessibility-panel h3 {
    margin: 0 0 15px 0;
    font-size: 16px;
    color: #333;
  }

  .control-group {
    margin-bottom: 15px;
  }

  .control-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
    color: #555;
  }

  .font-controls {
    display: flex;
    gap: 10px;
  }

  .font-controls button {
    padding: 8px 12px;
    border: 1px solid #ddd;
    background: #f8f9fa;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
  }

  .font-controls button:hover {
    background: #e9ecef;
  }

  .font-controls button:focus {
    outline: 2px solid #007bff;
    outline-offset: 1px;
  }

  .close-button {
    width: 100%;
    padding: 8px;
    background: #6c757d;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 10px;
  }

  .close-button:hover {
    background: #5a6268;
  }

  .close-button:focus {
    outline: 2px solid #007bff;
    outline-offset: 1px;
  }

  /* 고대비 모드 스타일 */
  .high-contrast {
    color-scheme: dark;
  }

  .high-contrast * {
    border-color: #fff !important;
  }

  .high-contrast button {
    background: #000 !important;
    color: #fff !important;
    border: 2px solid #fff !important;
  }

  .high-contrast input {
    background: #000 !important;
    color: #fff !important;
    border: 2px solid #fff !important;
  }

  /* 포커스 표시 강화 */
  *:focus {
    outline: 2px solid #007bff !important;
    outline-offset: 2px !important;
  }

  /* 스크린 리더 전용 텍스트 */
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }
`; 