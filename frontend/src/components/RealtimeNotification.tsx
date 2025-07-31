import React, { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { toast } from 'sonner';

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

export const RealtimeNotification: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  
  const { status, notifications: wsNotifications } = useWebSocket({
    userId: 'current_user',
    autoConnect: true
  });

  useEffect(() => {
    // WebSocket 알림 처리 (실제로는 WebSocket 메시지로 처리)
    // 현재는 더미 데이터로 시뮬레이션
    const interval = setInterval(() => {
      const shouldShowNotification = Math.random() > 0.8; // 20% 확률로 알림 생성
      
      if (shouldShowNotification) {
        const types: ('info' | 'success' | 'warning' | 'error')[] = ['info', 'success', 'warning', 'error'];
        const randomType = types[Math.floor(Math.random() * types.length)];
        
        const newNotification: Notification = {
          id: Date.now().toString(),
          type: randomType,
          title: '새 알림',
          message: `새로운 ${randomType} 알림이 도착했습니다.`,
          timestamp: new Date().toISOString(),
          read: false
        };

        setNotifications(prev => [newNotification, ...prev]);
        setUnreadCount(prev => prev + 1);
        
        // Toast 알림 표시
        toast[randomType](newNotification.message, {
          description: newNotification.title
        });
      }
    }, 10000); // 10초마다 체크

    return () => clearInterval(interval);
  }, []);

  const markAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === id ? { ...notif, read: true } : notif
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notif => ({ ...notif, read: true }))
    );
    setUnreadCount(0);
  };

  return (
    <div className="relative">
      {/* 알림 버튼 */}
      <button 
        className="relative p-2 text-gray-600 hover:text-gray-800"
        onClick={() => document.getElementById('notification-panel')?.classList.toggle('hidden')}
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5z" />
        </svg>
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount}
          </span>
        )}
      </button>

      {/* 연결 상태 표시 */}
      <div className={`absolute top-0 right-0 w-2 h-2 rounded-full ${status.connected ? 'bg-green-500' : 'bg-red-500'}`} />

      {/* 알림 패널 */}
      <div id="notification-panel" className="hidden absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
        <div className="p-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">알림</h3>
            <button 
              onClick={markAllAsRead}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              모두 읽음
            </button>
          </div>
        </div>
        
        <div className="max-h-96 overflow-y-auto">
          {notifications.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              알림이 없습니다
            </div>
          ) : (
            notifications.map(notification => (
              <div 
                key={notification.id}
                className={`p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${
                  !notification.read ? 'bg-blue-50' : ''
                }`}
                onClick={() => markAsRead(notification.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className={`inline-block w-2 h-2 rounded-full ${
                        notification.type === 'error' ? 'bg-red-500' :
                        notification.type === 'warning' ? 'bg-yellow-500' :
                        notification.type === 'success' ? 'bg-green-500' :
                        'bg-blue-500'
                      }`} />
                      <h4 className="text-sm font-medium text-gray-900">
                        {notification.title}
                      </h4>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {notification.message}
                    </p>
                    <p className="text-xs text-gray-400 mt-2">
                      {new Date(notification.timestamp).toLocaleString()}
                    </p>
                  </div>
                  {!notification.read && (
                    <div className="w-2 h-2 bg-blue-500 rounded-full ml-2" />
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}; 