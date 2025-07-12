import React from 'react';
import { useGlobalStore } from '@/store/useGlobalStore';

const SyncStatus: React.FC = () => {
  const isOnline = useGlobalStore((state) => state.isOnline);
  const lastSync = useGlobalStore((state) => state.lastSync);
  const syncData = useGlobalStore((state) => state.syncData);
  const [showNotice, setShowNotice] = React.useState(false);

  const handleSync = () => {
    syncData();
    setShowNotice(true);
    setTimeout(() => setShowNotice(false), 2000);
  };

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col items-end">
      <button
        className={`px-4 py-2 rounded shadow transition-colors mb-2 ${isOnline ? 'bg-green-500 text-white' : 'bg-gray-400 text-gray-100'}`}
        onClick={handleSync}
        disabled={!isOnline}
      >
        {isOnline ? '동기화' : '오프라인'}
      </button>
      <span className="text-xs text-gray-500">{lastSync ? `마지막 동기화: ${lastSync}` : '동기화 기록 없음'}</span>
      {showNotice && (
        <div className="mt-2 px-3 py-2 bg-blue-100 text-blue-700 rounded shadow animate-fade-in">
          데이터가 최신 상태로 동기화되었습니다.
        </div>
      )}
    </div>
  );
};

export default SyncStatus; 
