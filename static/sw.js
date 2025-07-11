// Service Worker for Your Program PWA
const CACHE_NAME = 'your-program-v1.0.0';
const STATIC_CACHE = 'static-v1.0.0';
const DYNAMIC_CACHE = 'dynamic-v1.0.0';

// 캐시할 정적 파일들
const STATIC_FILES = [
  '/',
  '/static/css/common.css',
  '/static/css/tailwind.css',
  '/static/js/theme.js',
  '/static/manifest.json',
  '/static/favicon.ico',
  '/static/favicon.svg',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png'
];

// API 엔드포인트들 (오프라인 지원)
const API_CACHE = [
  '/api/mobile/dashboard',
  '/api/mobile/offline-data',
  '/api/mobile/notifications',
  '/api/mobile/inventory/check'
];

// 설치 이벤트
self.addEventListener('install', (event) => {
  console.log('Service Worker 설치 중...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('정적 파일 캐싱 중...');
        return cache.addAll(STATIC_FILES);
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
            // 이전 캐시 삭제
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('이전 캐시 삭제:', cacheName);
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

// fetch 이벤트 (네트워크 요청 가로채기)
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // API 요청 처리
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }
  
  // 정적 파일 요청 처리
  if (request.method === 'GET') {
    event.respondWith(handleStaticRequest(request));
    return;
  }
});

// API 요청 처리 함수
async function handleApiRequest(request) {
  try {
    // 먼저 네트워크 요청 시도
    const networkResponse = await fetch(request);
    
    // 성공하면 캐시에 저장
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('네트워크 요청 실패, 캐시에서 검색:', request.url);
    
    // 캐시에서 검색
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // 오프라인 응답 생성
    return createOfflineResponse(request);
  }
}

// 정적 파일 요청 처리 함수
async function handleStaticRequest(request) {
  try {
    // 캐시에서 먼저 검색
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // 네트워크 요청
    const networkResponse = await fetch(request);
    
    // 성공하면 캐시에 저장
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('정적 파일 요청 실패:', request.url);
    
    // 기본 오프라인 페이지 반환
    if (request.destination === 'document') {
      return caches.match('/offline.html');
    }
    
    return new Response('오프라인 모드', {
      status: 503,
      statusText: 'Service Unavailable',
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

// 오프라인 응답 생성 함수
function createOfflineResponse(request) {
  const url = new URL(request.url);
  
  // API별 오프라인 응답
  if (url.pathname === '/api/mobile/dashboard') {
    return new Response(JSON.stringify({
      success: true,
      offline: true,
      data: {
        user_info: { offline: true },
        quick_stats: { offline: true },
        recent_activities: [],
        quick_actions: []
      },
      message: '오프라인 모드입니다.'
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  if (url.pathname === '/api/mobile/offline-data') {
    return new Response(JSON.stringify({
      success: true,
      offline: true,
      data: {
        menu_items: [],
        staff_list: [],
        tables: [],
        settings: { offline: true }
      },
      message: '오프라인 데이터입니다.'
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  // 기본 오프라인 응답
  return new Response(JSON.stringify({
    success: false,
    error: '오프라인 모드입니다. 인터넷 연결을 확인해주세요.',
    offline: true
  }), {
    status: 503,
    headers: { 'Content-Type': 'application/json' }
  });
}

// 백그라운드 동기화 (데이터 동기화)
self.addEventListener('sync', (event) => {
  console.log('백그라운드 동기화:', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(performBackgroundSync());
  }
});

// 백그라운드 동기화 수행
async function performBackgroundSync() {
  try {
    // IndexedDB에서 오프라인 데이터 가져오기
    const offlineData = await getOfflineData();
    
    if (offlineData.length > 0) {
      // 서버에 동기화
      const response = await fetch('/api/mobile/sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          sync_data: offlineData
        })
      });
      
      if (response.ok) {
        // 동기화 성공 시 로컬 데이터 삭제
        await clearOfflineData();
        console.log('백그라운드 동기화 완료');
      }
    }
  } catch (error) {
    console.error('백그라운드 동기화 실패:', error);
  }
}

// 푸시 알림 처리
self.addEventListener('push', (event) => {
  console.log('푸시 알림 수신:', event);
  
  if (event.data) {
    const data = event.data.json();
    
    const options = {
      body: data.message || '새로운 알림이 있습니다.',
      icon: '/static/icons/icon-192x192.png',
      badge: '/static/icons/icon-72x72.png',
      vibrate: [200, 100, 200],
      data: {
        url: data.url || '/',
        notification_id: data.id
      },
      actions: [
        {
          action: 'view',
          title: '보기',
          icon: '/static/icons/view-96x96.png'
        },
        {
          action: 'dismiss',
          title: '닫기',
          icon: '/static/icons/dismiss-96x96.png'
        }
      ]
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title || 'Your Program', options)
    );
  }
});

// 알림 클릭 처리
self.addEventListener('notificationclick', (event) => {
  console.log('알림 클릭:', event);
  
  event.notification.close();
  
  if (event.action === 'view') {
    // 알림 클릭 시 해당 페이지로 이동
    event.waitUntil(
      clients.openWindow(event.notification.data.url)
    );
  }
});

// IndexedDB 관련 함수들 (간단한 구현)
async function getOfflineData() {
  // 실제로는 IndexedDB에서 데이터를 가져옴
  return [];
}

async function clearOfflineData() {
  // 실제로는 IndexedDB에서 데이터를 삭제함
  console.log('오프라인 데이터 삭제');
}

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

// 오류 처리
self.addEventListener('error', (event) => {
  console.error('Service Worker 오류:', event.error);
});

self.addEventListener('unhandledrejection', (event) => {
  console.error('Service Worker 처리되지 않은 Promise 거부:', event.reason);
}); 
