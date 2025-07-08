// Theme Provider for Flask Restaurant Management System
class ThemeProvider {
  constructor() {
    this.theme = this.getStoredTheme() || 'system';
    this.systemTheme = this.getSystemTheme();
    this.init();
  }

  // 초기화
  init() {
    this.applyTheme();
    this.createThemeToggle();
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
    
    // document.documentElement과 document.body가 존재하는지 확인
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

  // 테마 토글 버튼 생성
  createThemeToggle() {
    const toggle = document.createElement('button');
    toggle.id = 'theme-toggle';
    toggle.className = 'theme-toggle-btn';
    toggle.setAttribute('aria-label', '테마 변경');
    toggle.innerHTML = this.getToggleIcon();
    toggle.addEventListener('click', () => this.cycleTheme());

    // 더 구체적인 선택자들로 개선
    const headerSelectors = [
      // Next.js App Router 특화 선택자
      '[data-testid="header"]', '.flex.w-full', '.min-h-screen',
      '.bg-gradient-to-br', '.flex.items-center', '.justify-center',
      // 로그인 페이지 특화 선택자
      '.max-w-md', '.space-y-8', '.text-center',
      // 대시보드 페이지 특화 선택자
      '.bg-background', '.flex-1', '.ml-0', '.lg\\:ml-64',
      // 일반적인 헤더 선택자
      'header', '.header', '.navbar', '.nav', '.top-bar',
      '.logo-container', '.brand-container', '.title-container',
      '.login-container', '.auth-container', '.form-header',
      // 추가적인 선택자들
      '.flex.justify-between', '.flex.items-center',
      '.container', '.main-header', '.app-header'
    ];

    let header = null;
    for (const selector of headerSelectors) {
      const elements = document.querySelectorAll(selector);
      for (const element of elements) {
        // 로그인 페이지의 경우 오른쪽 컨테이너에 추가
        if (selector.includes('max-w-md') || selector.includes('space-y-8')) {
          header = element;
          break;
        }
        // 대시보드의 경우 상단 영역에 추가
        if (element.offsetTop < 100 || element.classList.contains('header') || element.classList.contains('navbar')) {
          header = element;
          break;
        }
        // flex 컨테이너인 경우
        if (element.classList.contains('flex') || getComputedStyle(element).display === 'flex') {
          header = element;
          break;
        }
      }
      if (header) break;
    }

    if (header) {
      // 헤더가 flex 컨테이너인 경우 적절한 위치에 추가
      if (header.classList.contains('flex') || getComputedStyle(header).display === 'flex') {
        header.appendChild(toggle);
      } else {
        // 일반 컨테이너인 경우 첫 번째 자식으로 추가
        header.insertBefore(toggle, header.firstChild);
      }
    } else {
      // 헤더가 없으면 body에 추가
      if (document.body) {
        // body의 첫 번째 자식으로 추가
        document.body.insertBefore(toggle, document.body.firstChild);
      } else {
        // body도 없으면 아무것도 하지 않음
        console.warn('테마 토글을 추가할 위치를 찾을 수 없습니다.');
      }
    }
    
    // 토글이 성공적으로 추가되었는지 확인
    if (!document.getElementById('theme-toggle')) {
      // 마지막 수단: body에 강제로 추가
      if (document.body) {
        document.body.appendChild(toggle);
        console.log('테마 토글을 body에 강제로 추가했습니다.');
      }
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

// 전역 테마 프로바이더 인스턴스
window.themeProvider = new ThemeProvider();

// CSS 스타일 추가
const style = document.createElement('style');
style.textContent = `
  .theme-toggle-btn {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 8px;
    border: 1px solid hsl(var(--border));
    background: hsl(var(--background));
    color: hsl(var(--foreground));
    cursor: pointer;
    transition: all 0.2s ease;
    margin-left: 8px;
  }

  .theme-toggle-btn:hover {
    background: hsl(var(--accent));
    border-color: hsl(var(--accent));
  }

  .theme-toggle-btn:focus {
    outline: none;
    ring: 2px;
    ring-color: hsl(var(--ring));
    ring-offset: 2px;
  }

  .theme-toggle-btn svg {
    transition: transform 0.2s ease;
  }

  .theme-toggle-btn:hover svg {
    transform: scale(1.1);
  }

  /* 다크모드에서의 토글 버튼 */
  .dark .theme-toggle-btn {
    border-color: hsl(var(--border));
    background: hsl(var(--background));
    color: hsl(var(--foreground));
  }

  .dark .theme-toggle-btn:hover {
    background: hsl(var(--accent));
    border-color: hsl(var(--accent));
  }

  /* 모바일에서의 토글 버튼 */
  @media (max-width: 768px) {
    .theme-toggle-btn {
      width: 36px;
      height: 36px;
      margin-left: 4px;
    }
  }
`;
document.head.appendChild(style);

// 페이지 로드 시 테마 적용
document.addEventListener('DOMContentLoaded', () => {
  // 이미 초기화되었으면 스킵
  if (window.themeProvider) {
    return;
  }
  
  // 테마 프로바이더 초기화
  window.themeProvider = new ThemeProvider();
});

// 모듈 내보내기 (ES6 모듈 지원)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ThemeProvider;
} 