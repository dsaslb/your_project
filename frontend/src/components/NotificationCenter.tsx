"use client";

import React from 'react';
import { useNotificationStore, NotificationType } from '@/store/useNotificationStore';

const NotificationCenter: React.FC = () => {
  const { 
    notifications, 
    unreadCount, 
    isConnected, 
    markAsRead, 
    markAllAsRead, 
    removeNotification,
    connectWebSocket,
    disconnectWebSocket 
  } = useNotificationStore();

  React.useEffect(() => {
    // 브라우저 알림 권한 요청
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
    
    // WebSocket 연결
    connectWebSocket();
    
    return () => {
      disconnectWebSocket();
    };
  }, [connectWebSocket, disconnectWebSocket]);

  const getNotificationIcon = (type: NotificationType) => {
    switch (type) {
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      default: return 'ℹ️';
    }
  };

  const getNotificationColor = (type: NotificationType) => {
    switch (type) {
      case 'success': return 'border-green-500 bg-green-50';
      case 'warning': return 'border-yellow-500 bg-yellow-50';
      case 'error': return 'border-red-500 bg-red-50';
      default: return 'border-blue-500 bg-blue-50';
    }
  };

  return (
    <div className="fixed top-4 right-4 w-80 bg-white rounded-lg shadow-lg border">
      <div className="flex items-center justify-between p-3 border-b">
        <h3 className="font-semibold">알림</h3>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-xs text-gray-500">
            {isConnected ? '연결됨' : '연결 끊어짐'}
          </span>
          {unreadCount > 0 && (
            <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1">
              {unreadCount}
            </span>
          )}
        </div>
      </div>
      
      <div className="max-h-96 overflow-y-auto">
        {notifications.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            알림이 없습니다
          </div>
        ) : (
          <div className="p-2">
            {notifications.map((notification) => (
              <div
                key={notification.id}
                className={`mb-2 p-3 rounded border-l-4 ${getNotificationColor(notification.type)} ${
                  !notification.isRead ? 'opacity-100' : 'opacity-75'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-2 flex-1">
                    <span className="text-lg">{getNotificationIcon(notification.type)}</span>
                    <div className="flex-1">
                      <div className="font-medium text-sm">{notification.title}</div>
                      <div className="text-xs text-gray-600 mt-1">{notification.message}</div>
                      <div className="text-xs text-gray-400 mt-1">
                        {new Date(notification.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-1">
                    {!notification.isRead && (
                      <button
                        onClick={() => markAsRead(notification.id)}
                        className="text-xs text-blue-600 hover:text-blue-800"
                      >
                        읽음
                      </button>
                    )}
                    <button
                      onClick={() => removeNotification(notification.id)}
                      className="text-xs text-red-600 hover:text-red-800"
                    >
                      삭제
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {notifications.length > 0 && (
        <div className="p-3 border-t bg-gray-50">
          <div className="flex justify-between items-center">
            <button
              onClick={markAllAsRead}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              모두 읽음으로 표시
            </button>
            <span className="text-xs text-gray-500">
              총 {notifications.length}개
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationCenter; 
