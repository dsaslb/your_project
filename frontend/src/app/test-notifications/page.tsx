'use client';

import React from 'react';
import { useNotificationStore } from '@/store/useNotificationStore';

export default function TestNotificationsPage() {
  const { addNotification, notifications, clearAll } = useNotificationStore();

  const testNotifications = [
    {
      title: '새 주문',
      message: '테이블 5번에서 새로운 주문이 들어왔습니다.',
      type: 'info' as const,
      category: 'order',
    },
    {
      title: '재고 부족',
      message: '김치가 부족합니다. 발주가 필요합니다.',
      type: 'warning' as const,
      category: 'inventory',
    },
    {
      title: '직원 출근',
      message: '김직원님이 출근하셨습니다.',
      type: 'success' as const,
      category: 'attendance',
    },
    {
      title: '시스템 오류',
      message: '결제 시스템에 일시적인 오류가 발생했습니다.',
      type: 'error' as const,
      category: 'system',
    },
  ];

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">알림 테스트 페이지</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">알림 생성 테스트</h2>
          <div className="space-y-3">
            {testNotifications.map((notification, index) => (
              <button
                key={index}
                onClick={() => addNotification(notification)}
                className="w-full p-3 text-left border rounded hover:bg-gray-50 transition-colors"
              >
                <div className="font-medium">{notification.title}</div>
                <div className="text-sm text-gray-600">{notification.message}</div>
                <div className="text-xs text-gray-400 mt-1">
                  타입: {notification.type} | 카테고리: {notification.category}
                </div>
              </button>
            ))}
          </div>
          
          <div className="mt-4 space-x-2">
            <button
              onClick={() => {
                testNotifications.forEach((notification, index) => {
                  setTimeout(() => {
                    addNotification(notification);
                  }, index * 1000);
                });
              }}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              순차적으로 알림 생성 (1초 간격)
            </button>
            
            <button
              onClick={clearAll}
              className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
            >
              모든 알림 삭제
            </button>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">현재 알림 목록</h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <p className="text-gray-500">알림이 없습니다</p>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-3 border rounded ${
                    notification.isRead ? 'bg-gray-50' : 'bg-white'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="font-medium text-sm">{notification.title}</div>
                      <div className="text-xs text-gray-600">{notification.message}</div>
                      <div className="text-xs text-gray-400 mt-1">
                        {new Date(notification.timestamp).toLocaleString()}
                      </div>
                    </div>
                    <div className="text-xs text-gray-400">
                      {notification.isRead ? '읽음' : '안읽음'}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
      
      <div className="mt-6 bg-yellow-50 p-4 rounded-lg">
        <h3 className="font-semibold text-yellow-800 mb-2">사용법</h3>
        <ul className="text-sm text-yellow-700 space-y-1">
          <li>• 각 버튼을 클릭하여 다양한 타입의 알림을 생성할 수 있습니다</li>
          <li>• "순차적으로 알림 생성" 버튼으로 1초 간격으로 알림을 생성할 수 있습니다</li>
          <li>• 오른쪽 상단의 알림 센터에서 실시간으로 알림을 확인할 수 있습니다</li>
          <li>• 브라우저 알림 권한을 허용하면 데스크톱 알림도 받을 수 있습니다</li>
        </ul>
      </div>
    </div>
  );
} 
