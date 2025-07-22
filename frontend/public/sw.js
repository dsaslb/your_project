/**
 * 서비스 워커 - PWA 오프라인 지원
 */

const CACHE_NAME = 'mtms-v1.0.0';
const STATIC_CACHE = 'mtms-static-v1.0.0';
const DYNAMIC_CACHE = 'mtms-dynamic-v1.0.0';

// 캐시할 정적 리소스
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/static/css/tailwind.css',
  '/static/js/main.js',
  '/manifest.json',
  '/favicon.ico',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
  // API 엔드포인트
  '/api/health',
  '/swagger-ui',
  '/openapi.json'
];

// 네트워크 우선 전략을 사용할 리소스
const NETWORK_FIRST_RESOURCES = [
  '/api/',
  '/swagger-ui/',
  '/openapi.json'
];

// 캐시 우선 전략을 사용할 리소스
const CACHE_FIRST_RESOURCES = [
  '/static/',
  '/icons/',
  '/images/',
  '.css',
  '.js',
  '.png',
  '.jpg',
  '.jpeg',
  '.gif',
  '.svg',
  '.woff',
  '.woff2'
];

// 설치 이벤트
self.addEventListener('install', (event) => {
  console.log('Service Worker 설치 중...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('정적 리소스 캐싱 중...');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('Service Worker 설치 완료');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker 설치 실패:', error);
      })
  );
});

// 활성화 이벤트
self.addEventListener('activate', (event) => {
  console.log('Service Worker 활성화 중...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('오래된 캐시 삭제:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker 활성화 완료');
        return self.clients.claim();
      })
  );
});

// 페치 이벤트
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // GET 요청만 처리
  if (request.method !== 'GET') {
    return;
  }
  
  // 외부 리소스는 네트워크 우선
  if (url.origin !== self.location.origin) {
    event.respondWith(networkFirst(request));
    return;
  }
  
  // API 요청은 네트워크 우선
  if (isNetworkFirstResource(request.url)) {
    event.respondWith(networkFirst(request));
    return;
  }
  
  // 정적 리소스는 캐시 우선
  if (isCacheFirstResource(request.url)) {
    event.respondWith(cacheFirst(request));
    return;
  }
  
  // 기본적으로 네트워크 우선
  event.respondWith(networkFirst(request));
});

// 네트워크 우선 전략
async function networkFirst(request) {
  try {
    // 네트워크 요청 시도
    const networkResponse = await fetch(request);
    
    // 성공하면 캐시에 저장
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('네트워크 요청 실패, 캐시에서 조회:', request.url);
    
    // 네트워크 실패 시 캐시에서 조회
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // 캐시에도 없으면 오프라인 페이지 반환
    return getOfflineResponse(request);
  }
}

// 캐시 우선 전략
async function cacheFirst(request) {
  try {
    // 캐시에서 먼저 조회
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // 캐시에 없으면 네트워크 요청
    const networkResponse = await fetch(request);
    
    // 성공하면 캐시에 저장
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('캐시 및 네트워크 요청 실패:', request.url);
    return getOfflineResponse(request);
  }
}

// 오프라인 응답 생성
async function getOfflineResponse(request) {
  const url = new URL(request.url);
  
  // HTML 요청인 경우 오프라인 페이지 반환
  if (request.headers.get('accept')?.includes('text/html')) {
    const offlineResponse = await caches.match('/offline.html');
    if (offlineResponse) {
      return offlineResponse;
    }
    
    // 오프라인 페이지가 없으면 기본 오프라인 메시지
    return new Response(
      `
      <!DOCTYPE html>
      <html lang="ko">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>오프라인 - 멀티테넌시 관리 시스템</title>
        <style>
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
          }
          .offline-container {
            text-align: center;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 1rem;
            backdrop-filter: blur(10px);
            max-width: 400px;
          }
          .offline-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
          }
          h1 {
            margin: 0 0 1rem 0;
            font-size: 1.5rem;
          }
          p {
            margin: 0 0 1rem 0;
            opacity: 0.9;
          }
          .retry-btn {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            cursor: pointer;
            font-size: 1rem;
            transition: background 0.3s;
          }
          .retry-btn:hover {
            background: rgba(255, 255, 255, 0.3);
          }
        </style>
      </head>
      <body>
        <div class="offline-container">
          <div class="offline-icon">📶</div>
          <h1>오프라인 상태</h1>
          <p>인터넷 연결을 확인하고 다시 시도해주세요.</p>
          <button class="retry-btn" onclick="window.location.reload()">
            다시 시도
          </button>
        </div>
      </body>
      </html>
      `,
      {
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
        },
      }
    );
  }
  
  // API 요청인 경우 오류 응답
  if (url.pathname.startsWith('/api/')) {
    return new Response(
      JSON.stringify({
        success: false,
        error: '오프라인 상태입니다. 인터넷 연결을 확인해주세요.',
        offline: true
      }),
      {
        status: 503,
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
        },
      }
    );
  }
  
  // 기타 요청은 기본 오류 응답
  return new Response('오프라인 상태입니다.', {
    status: 503,
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
    },
  });
}

// 리소스 타입 확인 함수들
function isNetworkFirstResource(url) {
  return NETWORK_FIRST_RESOURCES.some(resource => url.includes(resource));
}

function isCacheFirstResource(url) {
  return CACHE_FIRST_RESOURCES.some(resource => url.includes(resource));
}

// 백그라운드 동기화
self.addEventListener('sync', (event) => {
  console.log('백그라운드 동기화:', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(performBackgroundSync());
  }
});

// 백그라운드 동기화 수행
async function performBackgroundSync() {
  try {
    // 오프라인 데이터 동기화
    const offlineData = await getOfflineData();
    
    if (offlineData.length > 0) {
      console.log('오프라인 데이터 동기화 중...');
      
      for (const data of offlineData) {
        try {
          await syncOfflineData(data);
        } catch (error) {
          console.error('데이터 동기화 실패:', error);
        }
      }
      
      // 동기화 완료 후 오프라인 데이터 삭제
      await clearOfflineData();
    }
  } catch (error) {
    console.error('백그라운드 동기화 실패:', error);
  }
}

// 오프라인 데이터 가져오기
async function getOfflineData() {
  try {
    const cache = await caches.open(DYNAMIC_CACHE);
    const requests = await cache.keys();
    const offlineRequests = requests.filter(req => 
      req.url.includes('/api/') && req.method === 'POST'
    );
    
    return offlineRequests;
  } catch (error) {
    console.error('오프라인 데이터 조회 실패:', error);
    return [];
  }
}

// 오프라인 데이터 동기화
async function syncOfflineData(request) {
  try {
    const response = await fetch(request.url, {
      method: request.method,
      headers: request.headers,
      body: await request.clone().text()
    });
    
    if (response.ok) {
      console.log('데이터 동기화 성공:', request.url);
    }
  } catch (error) {
    console.error('데이터 동기화 실패:', error);
    throw error;
  }
}

// 오프라인 데이터 삭제
async function clearOfflineData() {
  try {
    const cache = await caches.open(DYNAMIC_CACHE);
    const requests = await cache.keys();
    const offlineRequests = requests.filter(req => 
      req.url.includes('/api/') && req.method === 'POST'
    );
    
    await Promise.all(offlineRequests.map(req => cache.delete(req)));
    console.log('오프라인 데이터 삭제 완료');
  } catch (error) {
    console.error('오프라인 데이터 삭제 실패:', error);
  }
}

// 푸시 알림 처리
self.addEventListener('push', (event) => {
  console.log('푸시 알림 수신:', event);
  
  if (event.data) {
    const data = event.data.json();
    
    const options = {
      body: data.body || '새로운 알림이 있습니다.',
      icon: '/icons/icon-192x192.png',
      badge: '/icons/badge-72x72.png',
      vibrate: [200, 100, 200],
      data: {
        url: data.url || '/',
        timestamp: Date.now()
      },
      actions: [
        {
          action: 'view',
          title: '보기',
          icon: '/icons/view-96x96.png'
        },
        {
          action: 'close',
          title: '닫기',
          icon: '/icons/close-96x96.png'
        }
      ]
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title || '멀티테넌시 관리 시스템', options)
    );
  }
});

// 알림 클릭 처리
self.addEventListener('notificationclick', (event) => {
  console.log('알림 클릭:', event);
  
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow(event.notification.data.url)
    );
  }
});

// 메시지 처리
self.addEventListener('message', (event) => {
  console.log('Service Worker 메시지 수신:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
});

// 에러 처리
self.addEventListener('error', (event) => {
  console.error('Service Worker 오류:', event.error);
});

// 언핸들드 리젝션 처리
self.addEventListener('unhandledrejection', (event) => {
  console.error('Service Worker 처리되지 않은 Promise 거부:', event.reason);
});
