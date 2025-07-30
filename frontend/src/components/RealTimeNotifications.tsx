import React, { useEffect, useState } from 'react';
import { Bell, X, Check, AlertCircle, Info, Clock, Trash2 } from 'lucide-react';
import { useWebSocket, Notification } from '@/hooks/useWebSocket';

interface RealTimeNotificationsProps {
  maxNotifications?: number;
  showBadge?: boolean;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

export const RealTimeNotifications: React.FC<RealTimeNotificationsProps> = ({
  maxNotifications = 5,
  showBadge = true,
  position = 'top-right'
}) => {
  const {
    status,
    notifications,
    stats,
    subscribeNotifications,
    markNotificationRead,
    markAllNotificationsRead,
    fetchNotificationStats
  } = useWebSocket({ userId: 'user123' });

  const [isOpen, setIsOpen] = useState(false);
  const [filter, setFilter] = useState<'all' | 'unread' | 'high'>('all');

  // 컴포넌트 마운트 시 알림 구독
  useEffect(() => {
    subscribeNotifications(['system_alert', 'ai_prediction', 'performance_alert', 'user_activity', 'data_update']);
    fetchNotificationStats();
  }, [subscribeNotifications, fetchNotificationStats]);

  // 필터링된 알림
  const filteredNotifications = notifications.filter(notification => {
    switch (filter) {
      case 'unread':
        return !notification.read;
      case 'high':
        return notification.priority === 'high';
      default:
        return true;
    }
  }).slice(0, maxNotifications);

  // 읽지 않은 알림 수
  const unreadCount = notifications.filter(n => !n.read).length;

  // 알림 읽음 처리
  const handleMarkRead = (notificationId: string) => {
    markNotificationRead(notificationId);
  };

  // 모든 알림 읽음 처리
  const handleMarkAllRead = () => {
    markAllNotificationsRead();
  };

  // 알림 우선순위별 아이콘
  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'medium':
        return <Info className="w-4 h-4 text-yellow-500" />;
      case 'low':
        return <Info className="w-4 h-4 text-blue-500" />;
      default:
        return <Info className="w-4 h-4 text-gray-500" />;
    }
  };

  // 알림 타입별 색상
  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'system_alert':
        return 'border-l-red-500 bg-red-50';
      case 'ai_prediction':
        return 'border-l-blue-500 bg-blue-50';
      case 'performance_alert':
        return 'border-l-orange-500 bg-orange-50';
      case 'user_activity':
        return 'border-l-green-500 bg-green-50';
      case 'data_update':
        return 'border-l-purple-500 bg-purple-50';
      default:
        return 'border-l-gray-500 bg-gray-50';
    }
  };

  // 시간 포맷팅
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) return '방금 전';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}분 전`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}시간 전`;
    return date.toLocaleDateString();
  };

  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4'
  };

  return (
    <div className={`fixed ${positionClasses[position]} z-50`}>
      {/* 알림 버튼 */}
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="relative p-3 bg-white rounded-full shadow-lg hover:shadow-xl transition-shadow duration-200 border border-gray-200"
        >
          <Bell className="w-6 h-6 text-gray-600" />
          {showBadge && unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          )}
        </button>

        {/* 연결 상태 표시 */}
        {!status.connected && (
          <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse" />
        )}
      </div>

      {/* 알림 패널 */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 max-h-96 overflow-hidden">
          {/* 헤더 */}
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-800">알림</h3>
              <div className="flex items-center space-x-2">
                {unreadCount > 0 && (
                  <button
                    onClick={handleMarkAllRead}
                    className="text-xs text-blue-600 hover:text-blue-800"
                  >
                    모두 읽음
                  </button>
                )}
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* 필터 */}
            <div className="flex space-x-2 mt-3">
              {[
                { key: 'all', label: '전체', count: notifications.length },
                { key: 'unread', label: '읽지 않음', count: unreadCount },
                { key: 'high', label: '중요', count: notifications.filter(n => n.priority === 'high').length }
              ].map(({ key, label, count }) => (
                <button
                  key={key}
                  onClick={() => setFilter(key as any)}
                  className={`px-2 py-1 text-xs rounded ${
                    filter === key
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {label} ({count})
                </button>
              ))}
            </div>
          </div>

          {/* 알림 목록 */}
          <div className="max-h-64 overflow-y-auto">
            {filteredNotifications.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                <Bell className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                <p>알림이 없습니다</p>
              </div>
            ) : (
              filteredNotifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-4 border-l-4 ${getNotificationColor(notification.type)} ${
                    !notification.read ? 'bg-opacity-100' : 'bg-opacity-50'
                  } hover:bg-opacity-75 transition-all duration-200`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      {getPriorityIcon(notification.priority)}
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm font-medium ${
                          !notification.read ? 'text-gray-900' : 'text-gray-600'
                        }`}>
                          {notification.message}
                        </p>
                        {notification.data && Object.keys(notification.data).length > 0 && (
                          <div className="mt-1 text-xs text-gray-500">
                            {Object.entries(notification.data).map(([key, value]) => (
                              <span key={key} className="mr-2">
                                {key}: {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                              </span>
                            ))}
                          </div>
                        )}
                        <div className="flex items-center mt-2 text-xs text-gray-400">
                          <Clock className="w-3 h-3 mr-1" />
                          {formatTime(notification.created_at)}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-1 ml-2">
                      {!notification.read && (
                        <button
                          onClick={() => handleMarkRead(notification.id)}
                          className="p-1 text-gray-400 hover:text-green-600 transition-colors"
                          title="읽음 처리"
                        >
                          <Check className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* 푸터 */}
          <div className="p-3 border-t border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  status.connected ? 'bg-green-500' : 'bg-red-500'
                }`} />
                <span>{status.connected ? '연결됨' : '연결 끊김'}</span>
              </div>
              {stats && (
                <span>총 {stats.total_notifications}개</span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RealTimeNotifications; 