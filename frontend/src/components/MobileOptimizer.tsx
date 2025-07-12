import React, { useState, useEffect } from 'react';

interface MobileSettings {
  enableGestures: boolean;
  enableHapticFeedback: boolean;
  enableOfflineMode: boolean;
  enablePushNotifications: boolean;
  fontSize: 'small' | 'medium' | 'large';
  theme: 'light' | 'dark' | 'auto';
}

const MobileOptimizer: React.FC = () => {
  const [isMobile, setIsMobile] = useState(false);
  const [settings, setSettings] = useState<MobileSettings>({
    enableGestures: true,
    enableHapticFeedback: true,
    enableOfflineMode: true,
    enablePushNotifications: true,
    fontSize: 'medium',
    theme: 'auto',
  });

  const [batteryLevel, setBatteryLevel] = useState<number | null>(null);
  const [networkType, setNetworkType] = useState<string>('unknown');

  useEffect(() => {
    // 모바일 디바이스 감지
    const checkMobile = () => {
      const userAgent = navigator.userAgent;
      const mobileRegex = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i;
      setIsMobile(mobileRegex.test(userAgent));
    };

    checkMobile();

    // 배터리 정보 가져오기 (지원하는 브라우저에서만)
    if ('getBattery' in navigator) {
      (navigator as any).getBattery().then((battery: any) => {
        setBatteryLevel(battery.level * 100);
        battery.addEventListener('levelchange', () => {
          setBatteryLevel(battery.level * 100);
        });
      });
    }

    // 네트워크 정보 가져오기
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      setNetworkType(connection.effectiveType || 'unknown');
      connection.addEventListener('change', () => {
        setNetworkType(connection.effectiveType || 'unknown');
      });
    }

    // 화면 방향 변경 감지
    const handleOrientationChange = () => {
      // 모바일 최적화 레이아웃 조정
      console.log('화면 방향 변경됨:', window.orientation);
    };

    window.addEventListener('orientationchange', handleOrientationChange);

    return () => {
      window.removeEventListener('orientationchange', handleOrientationChange);
    };
  }, []);

  const updateSettings = (newSettings: Partial<MobileSettings>) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
    // TODO: 실제 설정 저장 API 호출
  };

  const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      if (permission === 'granted') {
        updateSettings({ enablePushNotifications: true });
      }
    }
  };

  const triggerHapticFeedback = () => {
    if ('vibrate' in navigator && settings.enableHapticFeedback) {
      navigator.vibrate(50);
    }
  };

  const installPWA = () => {
    // PWA 설치 로직
    console.log('PWA 설치 요청');
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl flex items-center justify-center">
          <span className="text-2xl">📱</span>
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">모바일 최적화</h3>
          <p className="text-sm text-gray-500">
            {isMobile ? '모바일 디바이스 감지됨' : '데스크톱 환경'}
          </p>
        </div>
      </div>

      <div className="space-y-6">
        {/* 디바이스 정보 */}
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-3">디바이스 정보</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-blue-800 dark:text-blue-200">화면 크기:</span>
              <div className="font-medium">
                {window.innerWidth} × {window.innerHeight}
              </div>
            </div>
            <div>
              <span className="text-blue-800 dark:text-blue-200">배터리:</span>
              <div className="font-medium">
                {batteryLevel ? `${Math.round(batteryLevel)}%` : '알 수 없음'}
              </div>
            </div>
            <div>
              <span className="text-blue-800 dark:text-blue-200">네트워크:</span>
              <div className="font-medium capitalize">{networkType}</div>
            </div>
            <div>
              <span className="text-blue-800 dark:text-blue-200">방향:</span>
              <div className="font-medium">
                {window.orientation === 0 ? '세로' : '가로'}
              </div>
            </div>
          </div>
        </div>

        {/* 모바일 설정 */}
        <div>
          <h4 className="font-medium text-gray-900 dark:text-white mb-3">모바일 설정</h4>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300">터치 제스처</span>
              <input
                type="checkbox"
                checked={settings.enableGestures}
                onChange={(e) => updateSettings({ enableGestures: e.target.checked })}
                className="w-4 h-4"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300">햅틱 피드백</span>
              <input
                type="checkbox"
                checked={settings.enableHapticFeedback}
                onChange={(e) => updateSettings({ enableHapticFeedback: e.target.checked })}
                className="w-4 h-4"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300">오프라인 모드</span>
              <input
                type="checkbox"
                checked={settings.enableOfflineMode}
                onChange={(e) => updateSettings({ enableOfflineMode: e.target.checked })}
                className="w-4 h-4"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300">푸시 알림</span>
              <input
                type="checkbox"
                checked={settings.enablePushNotifications}
                onChange={(e) => updateSettings({ enablePushNotifications: e.target.checked })}
                className="w-4 h-4"
              />
            </div>
          </div>
        </div>

        {/* 접근성 설정 */}
        <div>
          <h4 className="font-medium text-gray-900 dark:text-white mb-3">접근성 설정</h4>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-gray-700 dark:text-gray-300">글자 크기</label>
              <select
                value={settings.fontSize}
                onChange={(e) => updateSettings({ fontSize: e.target.value as any })}
                className="w-full mt-1 px-3 py-2 border rounded-lg text-sm bg-white dark:bg-gray-700 dark:border-gray-600"
              >
                <option value="small">작게</option>
                <option value="medium">보통</option>
                <option value="large">크게</option>
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-700 dark:text-gray-300">테마</label>
              <select
                value={settings.theme}
                onChange={(e) => updateSettings({ theme: e.target.value as any })}
                className="w-full mt-1 px-3 py-2 border rounded-lg text-sm bg-white dark:bg-gray-700 dark:border-gray-600"
              >
                <option value="light">라이트</option>
                <option value="dark">다크</option>
                <option value="auto">자동</option>
              </select>
            </div>
          </div>
        </div>

        {/* 모바일 전용 기능 */}
        {isMobile && (
          <div className="space-y-3">
            <button
              onClick={requestNotificationPermission}
              className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              푸시 알림 권한 요청
            </button>
            <button
              onClick={triggerHapticFeedback}
              className="w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
            >
              햅틱 피드백 테스트
            </button>
            <button
              onClick={installPWA}
              className="w-full px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors"
            >
              앱으로 설치
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MobileOptimizer; 