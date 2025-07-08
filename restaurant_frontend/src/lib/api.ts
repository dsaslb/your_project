// API 유틸리티 함수들
const API_BASE_URL = 'http://localhost:5000';

// 백엔드 연결 상태 확인
export const checkBackendConnection = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // 3초 타임아웃 설정
      signal: AbortSignal.timeout(3000),
    });
    return response.ok;
  } catch (error) {
    console.log('백엔드 서버에 연결할 수 없습니다:', error);
    return false;
  }
};

// API 호출 래퍼 함수 (백엔드 연결 확인 없이)
export const apiCall = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<{ data: T | null; error?: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
      signal: AbortSignal.timeout(5000), // 5초 타임아웃
    });

    // HTML 응답인 경우 (로그인 페이지로 리다이렉트)
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('text/html')) {
      window.location.href = '/login';
      return {
        data: null,
        error: '인증이 필요합니다.'
      };
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      data
    };
  } catch (error) {
    console.error('API 호출 오류:', error);
    return {
      data: null,
      error: error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.'
    };
  }
};

// GET 요청
export const apiGet = <T>(endpoint: string) => 
  apiCall<T>(endpoint, { method: 'GET' });

// POST 요청
export const apiPost = <T>(endpoint: string, data: any) => 
  apiCall<T>(endpoint, {
    method: 'POST',
    body: JSON.stringify(data)
  });

// PUT 요청
export const apiPut = <T>(endpoint: string, data: any) => 
  apiCall<T>(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data)
  });

// DELETE 요청
export const apiDelete = <T>(endpoint: string) => 
  apiCall<T>(endpoint, { method: 'DELETE' }); 