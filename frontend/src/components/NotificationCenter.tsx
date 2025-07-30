'use client';

import { useState, useEffect } from 'react';
import { useSystemStatus } from '@/hooks/useSystemStatus';
import { cn } from '@/lib/utils';
import { Bell, X, AlertTriangle, Info, CheckCircle, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  category: string;
}

export const NotificationCenter = () => {
  const { status } = useSystemStatus();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [filter, setFilter] = useState<'all' | 'unread' | 'error' | 'warning'>('all');

  useEffect(() => {
    // 알림 데이터 가져오기
    const fetchNotifications = async () => {
      try {
        const response = await fetch('/api/notifications');
        if (response.ok) {
          const data = await response.json();
          setNotifications(data);
        }
      } catch (error) {
        console.error('알림 로드 실패:', error);
      }
    };

    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000); // 30초마다 업데이트

    return () => clearInterval(interval);
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;
  const errorCount = notifications.filter(n => n.type === 'error').length;
  const warningCount = notifications.filter(n => n.type === 'warning').length;

  const getFilteredNotifications = () => {
    switch (filter) {
      case 'unread':
        return notifications.filter(n => !n.read);
      case 'error':
        return notifications.filter(n => n.type === 'error');
      case 'warning':
        return notifications.filter(n => n.type === 'warning');
      default:
        return notifications;
    }
  };

  const markAsRead = async (id: string) => {
    try {
      await fetch(`/api/notifications/${id}/read`, { method: 'POST' });
      setNotifications(prev => 
        prev.map(n => n.id === id ? { ...n, read: true } : n)
      );
    } catch (error) {
      console.error('알림 읽음 처리 실패:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await fetch('/api/notifications/read-all', { method: 'POST' });
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    } catch (error) {
      console.error('모든 알림 읽음 처리 실패:', error);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <AlertTriangle className="w-4 h-4 text-red-400" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      default:
        return <Info className="w-4 h-4 text-blue-400" />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'error':
        return 'border-red-500/30 bg-red-500/10';
      case 'warning':
        return 'border-yellow-500/30 bg-yellow-500/10';
      case 'success':
        return 'border-green-500/30 bg-green-500/10';
      default:
        return 'border-blue-500/30 bg-blue-500/10';
    }
  };

  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - new Date(date).getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    
    if (minutes < 1) return '방금 전';
    if (minutes < 60) return `${minutes}분 전`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}시간 전`;
    
    const days = Math.floor(hours / 24);
    return `${days}일 전`;
  };

  return (
    <div className="relative">
      {/* 알림 버튼 */}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-slate-400 hover:text-white hover:bg-cyan-500/10"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </Button>

      {/* 알림 패널 */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-black/95 backdrop-blur-xl border border-cyan-500/30 rounded-lg shadow-xl z-50">
          {/* 헤더 */}
          <div className="flex items-center justify-between p-4 border-b border-cyan-500/20">
            <h3 className="text-sm font-semibold text-white">알림</h3>
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={markAllAsRead}
                className="text-xs text-slate-400 hover:text-white"
              >
                모두 읽음
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* 필터 */}
          <div className="flex items-center space-x-1 p-2 border-b border-cyan-500/20">
            {[
              { key: 'all', label: '전체', count: notifications.length },
              { key: 'unread', label: '읽지 않음', count: unreadCount },
              { key: 'error', label: '오류', count: errorCount },
              { key: 'warning', label: '경고', count: warningCount },
            ].map(({ key, label, count }) => (
              <Button
                key={key}
                variant="ghost"
                size="sm"
                onClick={() => setFilter(key as any)}
                className={cn(
                  "text-xs px-2 py-1 h-auto",
                  filter === key 
                    ? "bg-cyan-500/20 text-cyan-400" 
                    : "text-slate-400 hover:text-white"
                )}
              >
                {label} ({count})
              </Button>
            ))}
          </div>

          {/* 알림 목록 */}
          <div className="max-h-96 overflow-y-auto">
            {getFilteredNotifications().length === 0 ? (
              <div className="p-4 text-center text-slate-400">
                <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">알림이 없습니다</p>
              </div>
            ) : (
              <div className="p-2 space-y-2">
                {getFilteredNotifications().map((notification) => (
                  <div
                    key={notification.id}
                    className={cn(
                      "p-3 rounded-lg border transition-all duration-200 cursor-pointer",
                      getNotificationColor(notification.type),
                      !notification.read && "ring-1 ring-cyan-500/50",
                      "hover:bg-white/5"
                    )}
                    onClick={() => markAsRead(notification.id)}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-0.5">
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <h4 className="text-sm font-medium text-white">
                            {notification.title}
                          </h4>
                          <span className="text-xs text-slate-400">
                            {formatTime(notification.timestamp)}
                          </span>
                        </div>
                        <p className="text-xs text-slate-300 mt-1">
                          {notification.message}
                        </p>
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-xs text-slate-400">
                            {notification.category}
                          </span>
                          {!notification.read && (
                            <div className="w-2 h-2 bg-cyan-400 rounded-full"></div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// 간단한 알림 배지 (사이드바용)
export const NotificationBadge = () => {
  const { status } = useSystemStatus();
  const alertCount = status.alerts.length;

  if (alertCount === 0) return null;

  return (
    <div className="flex items-center space-x-2 p-2 bg-red-500/20 border border-red-500/30 rounded-lg">
      <AlertTriangle className="w-4 h-4 text-red-400" />
      <span className="text-xs text-red-400">
        {alertCount}개의 알림
      </span>
    </div>
  );
}; 
