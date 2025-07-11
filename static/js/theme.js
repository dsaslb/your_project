// Theme Provider for Flask your_program Management System
// 중복 로드 방지
if (typeof window.BackendThemeProvider !== 'undefined') {
  console.warn('BackendThemeProvider already loaded, skipping...');
} else {
class BackendThemeProvider {
  constructor() {
    this.theme = this.getStoredTheme();
    this.systemTheme = this.getSystemTheme();
    this.init();
  }

  init() {
    this.applyTheme();
    this.setupThemeToggle();
    this.watchSystemTheme();
  }

  // 저장된 테마 가져오기
  getStoredTheme() {
    return localStorage.getItem('theme') || 'system';
  }

  // 시스템 테마 감지
  getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  // 테마 적용
  applyTheme() {
    const effectiveTheme = this.theme === 'system' ? this.systemTheme : this.theme;
    
    if (document.documentElement && document.body) {
      if (effectiveTheme === 'dark') {
        document.documentElement.classList.add('dark');
        document.body.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
        document.body.classList.remove('dark');
      }
    }

    // 메타 태그 업데이트
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', effectiveTheme === 'dark' ? '#0f172a' : '#ffffff');
    }
  }

  // 테마 토글 설정
  setupThemeToggle() {
    // 이미 존재하는 토글 버튼 찾기
    const existingToggle = document.getElementById('theme-toggle');
    
    if (existingToggle) {
      // 기존 토글에 이벤트 리스너 추가
      existingToggle.addEventListener('click', () => {
        this.cycleTheme();
      });
      // 아이콘 업데이트
      existingToggle.innerHTML = this.getToggleIcon();
      return;
    }

    // 기존 토글이 없으면 동적으로 생성
    this.createThemeToggle();
  }

  // 테마 토글 버튼 생성
  createThemeToggle() {
    // 이미 존재하면 스킵
    if (document.getElementById('theme-toggle')) {
      return;
    }

    const toggle = document.createElement('button');
    toggle.id = 'theme-toggle';
    toggle.className = 'theme-toggle-btn';
    toggle.setAttribute('aria-label', '테마 변경');
    toggle.innerHTML = this.getToggleIcon();

    // 클릭 이벤트
    toggle.addEventListener('click', (e) => {
      e.preventDefault();
      this.cycleTheme();
    });

    // 간단한 위치 찾기 - body에 직접 추가
    if (document.body) {
      document.body.appendChild(toggle);
    } else {
      // body가 없으면 DOMContentLoaded 이벤트를 기다림
      document.addEventListener('DOMContentLoaded', () => {
        if (document.body && !document.getElementById('theme-toggle')) {
          document.body.appendChild(toggle);
        }
      });
    }
  }

  // 테마 순환 (light → dark → system)
  cycleTheme() {
    const themes = ['light', 'dark', 'system'];
    const currentIndex = themes.indexOf(this.theme);
    const nextIndex = (currentIndex + 1) % themes.length;
    this.setTheme(themes[nextIndex]);
  }

  // 테마 설정
  setTheme(theme) {
    this.theme = theme;
    localStorage.setItem('theme', theme);
    this.applyTheme();
    
    // 토글 버튼 아이콘 업데이트
    const toggle = document.getElementById('theme-toggle');
    if (toggle) {
      toggle.innerHTML = this.getToggleIcon();
    }

    // 이벤트 발생
    window.dispatchEvent(new CustomEvent('themeChange', { detail: { theme } }));
  }

  // 토글 아이콘 가져오기
  getToggleIcon() {
    const effectiveTheme = this.theme === 'system' ? this.systemTheme : this.theme;
    
    if (effectiveTheme === 'dark') {
      return `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="5"/>
          <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
        </svg>
      `;
    } else {
      return `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      `;
    }
  }

  // 시스템 테마 변경 감지
  watchSystemTheme() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', (e) => {
      this.systemTheme = e.matches ? 'dark' : 'light';
      if (this.theme === 'system') {
        this.applyTheme();
        const toggle = document.getElementById('theme-toggle');
        if (toggle) {
          toggle.innerHTML = this.getToggleIcon();
        }
      }
    });
  }

  // 현재 테마 가져오기
  getCurrentTheme() {
    return this.theme;
  }

  // 현재 적용된 테마 가져오기
  getEffectiveTheme() {
    return this.theme === 'system' ? this.systemTheme : this.theme;
  }
}

// CSS 스타일 추가
const style = document.createElement('style');
style.textContent = `
  .theme-toggle-btn {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 8px;
    border: 1px solid rgba(148, 163, 184, 0.3);
    background: rgba(15, 23, 42, 0.8);
    color: white;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .theme-toggle-btn:hover {
    background: rgba(59, 130, 246, 0.8);
    border-color: rgba(59, 130, 246, 0.5);
    transform: scale(1.05);
  }

  .theme-toggle-btn:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
  }

  .theme-toggle-btn svg {
    transition: transform 0.2s ease;
  }

  .theme-toggle-btn:hover svg {
    transform: scale(1.1);
  }

  /* 다크모드에서의 토글 버튼 */
  .dark .theme-toggle-btn {
    border-color: rgba(148, 163, 184, 0.5);
    background: rgba(30, 41, 59, 0.8);
    color: white;
  }

  .dark .theme-toggle-btn:hover {
    background: rgba(59, 130, 246, 0.8);
    border-color: rgba(59, 130, 246, 0.5);
  }

  /* 모바일에서의 토글 버튼 */
  @media (max-width: 768px) {
    .theme-toggle-btn {
      width: 36px;
      height: 36px;
      top: 10px;
      right: 10px;
    }
  }
`;

// 스타일을 head에 추가
if (document.head) {
  document.head.appendChild(style);
} else {
  document.addEventListener('DOMContentLoaded', () => {
    document.head.appendChild(style);
  });
}

// 전역 테마 프로바이더 인스턴스 생성
let themeProvider = null;

function initThemeProvider() {
  // 프론트엔드 환경이나 Next.js 환경에서는 백엔드 테마 시스템을 비활성화
  if (window.location.hostname === 'localhost' && (window.location.port === '3000' || window.location.port === '')) {
    return;
  }
  
  // 이미 다른 테마 시스템이 로드되어 있는지 확인
  if (window.__NEXT_DATA__ || document.querySelector('[data-nextjs-router]')) {
    return;
  }
  
  if (!themeProvider) {
    themeProvider = new BackendThemeProvider();
    window.themeProvider = themeProvider;
  }
}

// DOM이 로드되면 테마 프로바이더 초기화
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initThemeProvider);
} else {
  initThemeProvider();
}

// 모듈 내보내기 (ES6 모듈 지원)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = BackendThemeProvider;
}

// 전역에 클래스 등록
window.BackendThemeProvider = BackendThemeProvider;
} 
