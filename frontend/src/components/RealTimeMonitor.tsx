import React from 'react';
import { useRealTimeSync } from '@/hooks/useRealTimeSync';

const RealTimeMonitor: React.FC = () => {
  const { isConnected, lastSyncTime, error, manualSync, reconnect } = useRealTimeSync({
    autoSync: true,
    syncInterval: 30000,
    retryAttempts: 3
  });

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
          isConnected 
            ? 'bg-gradient-to-br from-green-400 to-green-600' 
            : 'bg-gradient-to-br from-red-400 to-red-600'
        }`}>
          <span className="text-2xl">
            {isConnected ? '🟢' : '🔴'}
          </span>
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">실시간 모니터링</h3>
          <p className="text-sm text-gray-500">
            {isConnected ? '실시간 연결됨' : '연결 끊어짐'}
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {/* 연결 상태 */}
        <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">연결 상태</span>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            isConnected 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}>
            {isConnected ? '온라인' : '오프라인'}
          </span>
        </div>

        {/* 마지막 동기화 */}
        <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">마지막 동기화</span>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {lastSyncTime ? lastSyncTime.toLocaleTimeString() : '없음'}
          </span>
        </div>

        {/* 오류 메시지 */}
        {error && (
          <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <div className="flex items-center space-x-2">
              <span className="text-red-500">⚠️</span>
              <span className="text-sm text-red-700 dark:text-red-300">{error}</span>
            </div>
          </div>
        )}

        {/* 액션 버튼 */}
        <div className="flex space-x-3">
          <button
            onClick={manualSync}
            disabled={!isConnected}
            className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            수동 동기화
          </button>
          <button
            onClick={reconnect}
            className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
          >
            재연결
          </button>
        </div>

        {/* 연결 정보 */}
        <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
          <div>WebSocket 서버: ws://192.168.45.44:8765</div>
          <div>동기화 간격: 30초</div>
          <div>재시도 횟수: 3회</div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeMonitor; 
