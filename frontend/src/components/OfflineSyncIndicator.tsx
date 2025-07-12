import React from 'react';
import { isOnline, setupNetworkListener, setupPeriodicSync } from '@/utils/offlineStorage';

const OfflineSyncIndicator: React.FC = () => {
  const [online, setOnline] = React.useState(true);
  const [syncing, setSyncing] = React.useState(false);

  React.useEffect(() => {
    setOnline(isOnline());

    const handleOnline = () => {
      setOnline(true);
      setSyncing(true);
      // 온라인 상태가 되면 동기화 시도
      setTimeout(() => setSyncing(false), 2000);
    };

    const handleOffline = () => {
      setOnline(false);
    };

    setupNetworkListener(handleOnline, handleOffline);

    // 정기적인 동기화 설정 (30초마다)
    const syncInterval = setupPeriodicSync(30000);

    return () => {
      clearInterval(syncInterval);
    };
  }, []);

  if (online && !syncing) {
    return null; // 온라인이고 동기화 중이 아니면 표시하지 않음
  }

  return (
    <div className="fixed bottom-4 left-4 z-50">
      {!online ? (
        <div className="bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center space-x-2">
          <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
          <span className="text-sm font-medium">오프라인 모드</span>
        </div>
      ) : syncing ? (
        <div className="bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center space-x-2">
          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium">동기화 중...</span>
        </div>
      ) : null}
    </div>
  );
};

export default OfflineSyncIndicator; 
