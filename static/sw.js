// Service Worker for your_program Management PWA
const CACHE_NAME = 'your_program-pwa-v1';
const urlsToCache = [
    '/m',
    '/static/css/common.css',
    '/static/manifest.json',
    '/api/new_notifications',
    '/api/latest_notifications'
];

// Install event - cache resources
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Push notification event
self.addEventListener('push', function(event) {
    console.log('Push event received');
    
    let options = {
        body: '새로운 알림이 있습니다.',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/icon-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: '확인하기',
                icon: '/static/icons/icon-72x72.png'
            },
            {
                action: 'close',
                title: '닫기',
                icon: '/static/icons/icon-72x72.png'
            }
        ]
    };
    
    if (event.data) {
        const data = event.data.json();
        options.body = data.message || options.body;
        options.data = { ...options.data, ...data };
    }
    
    event.waitUntil(
        self.registration.showNotification('레스토랑 알림', options)
    );
});

// Notification click event
self.addEventListener('notificationclick', function(event) {
    console.log('Notification click received');
    
    event.notification.close();
    
    if (event.action === 'explore') {
        // 알림 확인 시 모바일 대시보드로 이동
        event.waitUntil(
            clients.openWindow('/m')
        );
    } else if (event.action === 'close') {
        // 알림 닫기
        event.notification.close();
    } else {
        // 기본 동작 - 모바일 대시보드로 이동
        event.waitUntil(
            clients.openWindow('/m')
        );
    }
});

// Background sync (선택사항)
self.addEventListener('sync', function(event) {
    if (event.tag === 'background-sync') {
        event.waitUntil(
            // 백그라운드 동기화 작업
            console.log('Background sync triggered')
        );
    }
});

// Message event - from main thread
self.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
}); 
