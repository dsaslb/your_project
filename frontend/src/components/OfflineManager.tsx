﻿// @ts-nocheck
import React, { useEffect, useState } from 'react';
import { useGlobalStore } from '@/store/useGlobalStore';

// IndexedDB 타입 정의
declare global {
  interface Window {
    indexedDB: IDBFactory;
  }
}

interface OfflineDataItem {
  id: number;
  type: string;
  action: string;
  data: any;
}

const OfflineManager: React.FC = () => {
  const isOnline = useGlobalStore((state: any) => state.isOnline);
  const setOnline = useGlobalStore((state: any) => state.setOnline);
  const offlineQueue = useGlobalStore((state: any) => state.offlineQueue);
  const [offlineData, setOfflineData] = useState<OfflineDataItem[]>([]);

  useEffect(() => {
    // 온라인/오프라인 상태 감지
    const handleOnline = () => setOnline(true);
    const handleOffline = () => setOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // IndexedDB에서 오프라인 데이터 로드
    loadOfflineData();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const loadOfflineData = async () => {
    try {
      // IndexedDB에서 오프라인 저장된 데이터 로드
      const request = window.indexedDB.open('your_programDB', 1);
      
      request.onerror = () => {
        console.error('IndexedDB 열기 실패');
        setOfflineData([]);
      };
      
      request.onsuccess = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        const transaction = db.transaction(['offlineQueue'], 'readonly');
        const store = transaction.objectStore('offlineQueue');
        const getRequest = store.getAll();
        
        getRequest.onsuccess = () => {
          setOfflineData(getRequest.result || []);
        };
        
        getRequest.onerror = () => {
          console.error('오프라인 데이터 로드 실패');
          setOfflineData([]);
        };
      };
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        if (!db.objectStoreNames.contains('offlineQueue')) {
          db.createObjectStore('offlineQueue', { keyPath: 'id', autoIncrement: true });
        }
      };
    } catch (error) {
      console.error('오프라인 데이터 로드 실패:', error);
      // 폴백: 기본 데이터 사용
      setOfflineData([
        { id: 1, type: 'staff', action: 'add', data: { name: '김직원', role: '직원' } },
        { id: 2, type: 'order', action: 'update', data: { orderId: '123', status: 'completed' } },
      ]);
    }
  };

  const syncOfflineData = async () => {
    // TODO: 오프라인 데이터를 서버와 동기화
    console.log('오프라인 데이터 동기화 중...');
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">오프라인 관리</h3>
      
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <span className={`w-3 h-3 rounded-full ${isOnline ? 'bg-green-400' : 'bg-red-400'}`}></span>
          <span className="text-sm font-medium">
            {isOnline ? '온라인' : '오프라인'}
          </span>
        </div>

        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 dark:text-white mb-2">오프라인 대기 데이터</h4>
          <div className="space-y-2">
            {offlineData.map((item: OfflineDataItem) => (
              <div key={item.id} className="text-sm text-gray-600 dark:text-gray-300">
                {item.type} - {item.action}: {JSON.stringify(item.data)}
              </div>
            ))}
          </div>
        </div>

        <button
          onClick={syncOfflineData}
          disabled={!isOnline || offlineData.length === 0}
          className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          오프라인 데이터 동기화
        </button>
      </div>
    </div>
  );
};

export default OfflineManager; 
