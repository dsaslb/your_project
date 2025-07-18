// CSRF 토큰을 자동으로 포함하는 fetch 유틸리티
export default async function fetchWithCSRF(input: RequestInfo, init: RequestInit = {}) {
  // CSRF 토큰을 쿠키에서 추출
  function getCSRFToken() {
    if (typeof document === 'undefined') return '';
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
  }
  const method = (init.method || 'GET').toUpperCase();
  const headers = {
    ...(init.headers || {}),
    ...(method !== 'GET' && method !== 'HEAD' ? { 'X-CSRFToken': getCSRFToken() } : {})
  };
  return fetch(input, { ...init, headers });
} 