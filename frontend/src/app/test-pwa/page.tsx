'use client';

import React, { useState, useEffect } from 'react';

export default function TestPWAPage() {
  const [isOnline, setIsOnline] = useState(true);
  const [isStandalone, setIsStandalone] = useState(false);
  const [serviceWorkerStatus, setServiceWorkerStatus] = useState<string>('unknown');
  const [cacheStatus, setCacheStatus] = useState<string>('unknown');

  useEffect(() => {
    // 온라인 상태 확인
    const updateOnlineStatus = () => {
      setIsOnline(navigator.onLine);
    };

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();

    // PWA 설치 상태 확인
    setIsStandalone(
      window.matchMedia('(display-mode: standalone)').matches ||
      (window.navigator as any).standalone === true
    );

    // 서비스 워커 상태 확인
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then((registration) => {
        setServiceWorkerStatus('active');
      }).catch(() => {
        setServiceWorkerStatus('not available');
      });
    } else {
      setServiceWorkerStatus('not supported');
    }

    // 캐시 상태 확인
    if ('caches' in window) {
      caches.keys().then((cacheNames) => {
        setCacheStatus(`${cacheNames.length}개 캐시 발견`);
      }).catch(() => {
        setCacheStatus('캐시 확인 실패');
      });
    } else {
      setCacheStatus('캐시 API 미지원');
    }

    return () => {
      window.removeEventListener('online', updateOnlineStatus);
      window.removeEventListener('offline', updateOnlineStatus);
    };
  }, []);

  const testOfflineFunctionality = () => {
    // 오프라인 기능 테스트
    if (!navigator.onLine) {
      alert('오프라인 모드에서 테스트 중입니다!');
    } else {
      alert('온라인 모드입니다. 네트워크를 끊고 다시 시도해보세요.');
    }
  };

  const clearCache = async () => {
    if ('caches' in window) {
      try {
        const cacheNames = await caches.keys();
        await Promise.all(
          cacheNames.map(cacheName => caches.delete(cacheName))
        );
        setCacheStatus('캐시가 삭제되었습니다');
        alert('캐시가 성공적으로 삭제되었습니다!');
      } catch (error) {
        alert('캐시 삭제 중 오류가 발생했습니다.');
      }
    }
  };

  const unregisterServiceWorker = async () => {
    if ('serviceWorker' in navigator) {
      try {
        const registrations = await navigator.serviceWorker.getRegistrations();
        await Promise.all(
          registrations.map(registration => registration.unregister())
        );
        setServiceWorkerStatus('unregistered');
        alert('서비스 워커가 해제되었습니다!');
      } catch (error) {
        alert('서비스 워커 해제 중 오류가 발생했습니다.');
      }
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">PWA 테스트 페이지</h1>
      
      {/* 상태 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="font-semibold mb-2">네트워크 상태</h3>
          <div className={`text-sm px-2 py-1 rounded inline-block ${
            isOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {isOnline ? '온라인' : '오프라인'}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="font-semibold mb-2">PWA 설치 상태</h3>
          <div className={`text-sm px-2 py-1 rounded inline-block ${
            isStandalone ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
          }`}>
            {isStandalone ? '설치됨' : '설치되지 않음'}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="font-semibold mb-2">서비스 워커</h3>
          <div className={`text-sm px-2 py-1 rounded inline-block ${
            serviceWorkerStatus === 'active' ? 'bg-green-100 text-green-800' :
            serviceWorkerStatus === 'not supported' ? 'bg-red-100 text-red-800' :
            'bg-yellow-100 text-yellow-800'
          }`}>
            {serviceWorkerStatus === 'active' ? '활성' :
             serviceWorkerStatus === 'not supported' ? '미지원' :
             serviceWorkerStatus === 'unregistered' ? '해제됨' : '확인 중'}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="font-semibold mb-2">캐시 상태</h3>
          <div className="text-sm px-2 py-1 rounded inline-block bg-blue-100 text-blue-800">
            {cacheStatus}
          </div>
        </div>
      </div>

      {/* 테스트 버튼 */}
      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-xl font-semibold mb-4">PWA 기능 테스트</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={testOfflineFunctionality}
            className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="font-medium">오프라인 기능 테스트</div>
            <div className="text-sm text-gray-600">네트워크를 끊고 테스트</div>
          </button>

          <button
            onClick={clearCache}
            className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="font-medium">캐시 삭제</div>
            <div className="text-sm text-gray-600">모든 캐시 데이터 삭제</div>
          </button>

          <button
            onClick={unregisterServiceWorker}
            className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="font-medium">서비스 워커 해제</div>
            <div className="text-sm text-gray-600">PWA 기능 비활성화</div>
          </button>

          <button
            onClick={() => window.location.reload()}
            className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="font-medium">페이지 새로고침</div>
            <div className="text-sm text-gray-600">캐시된 콘텐츠 확인</div>
          </button>
        </div>
      </div>

      {/* PWA 정보 */}
      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-xl font-semibold mb-4">PWA 정보</h2>
        <div className="space-y-3 text-sm">
          <div>
            <strong>User Agent:</strong> {navigator.userAgent}
          </div>
          <div>
            <strong>Platform:</strong> {navigator.platform}
          </div>
          <div>
            <strong>Language:</strong> {navigator.language}
          </div>
          <div>
            <strong>Cookie Enabled:</strong> {navigator.cookieEnabled ? 'Yes' : 'No'}
          </div>
          <div>
            <strong>Service Worker:</strong> {'serviceWorker' in navigator ? 'Supported' : 'Not Supported'}
          </div>
          <div>
            <strong>Cache API:</strong> {'caches' in window ? 'Supported' : 'Not Supported'}
          </div>
          <div>
            <strong>IndexedDB:</strong> {'indexedDB' in window ? 'Supported' : 'Not Supported'}
          </div>
        </div>
      </div>

      {/* 사용법 안내 */}
      <div className="bg-blue-50 p-6 rounded-lg">
        <h3 className="font-semibold text-blue-800 mb-2">PWA 테스트 방법</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• <strong>설치 테스트:</strong> 브라우저 주소창 옆의 설치 아이콘을 클릭하거나, 하단의 설치 프롬프트를 사용</li>
          <li>• <strong>오프라인 테스트:</strong> 네트워크를 끊고 페이지 새로고침하여 캐시된 콘텐츠 확인</li>
          <li>• <strong>앱 모드 테스트:</strong> 설치 후 독립 실행 모드에서 앱처럼 동작하는지 확인</li>
          <li>• <strong>캐시 테스트:</strong> 캐시 삭제 후 새로고침하여 오프라인 동작 확인</li>
          <li>• <strong>모바일 테스트:</strong> 모바일 브라우저에서 "홈 화면에 추가" 기능 사용</li>
        </ul>
      </div>
    </div>
  );
} 