"use client";

import { useState, useEffect } from "react";
import { useNotifications, useMarkNotificationRead, useMarkAllNotificationsRead, useDeleteNotification } from "@/hooks/useNotifications";
import { 
  Bell, 
  Check, 
  X, 
  Trash2, 
  Settings, 
  AlertTriangle, 
  Info, 
  CheckCircle,
  Clock,
  MoreHorizontal
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface NotificationCenterProps {
  className?: string;
}

export default function NotificationCenter({ className = "" }: NotificationCenterProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'all' | 'unread'>('all');
  
  const { data: notificationsData, isLoading } = useNotifications({
    page: 1,
    per_page: 20,
    unread_only: activeTab === 'unread'
  });
  
  const markRead = useMarkNotificationRead();
  const markAllRead = useMarkAllNotificationsRead();
  const deleteNotification = useDeleteNotification();

  const notifications = notificationsData?.notifications || [];
  const unreadCount = notificationsData?.unread_count || 0;

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'order_new':
        return <Bell className="h-4 w-4 text-blue-600" />;
      case 'order_status':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'inventory_low':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      case 'staff_attendance':
        return <Clock className="h-4 w-4 text-purple-600" />;
      case 'system_alert':
        return <Info className="h-4 w-4 text-gray-600" />;
      case 'security_alert':
        return <AlertTriangle className="h-4 w-4 text-orange-600" />;
      default:
        return <Bell className="h-4 w-4 text-gray-600" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'low':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return '방금 전';
    if (diffInMinutes < 60) return `${diffInMinutes}분 전`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}시간 전`;
    return date.toLocaleDateString('ko-KR');
  };

  const handleMarkRead = (notificationId: number) => {
    markRead.mutate(notificationId);
  };

  const handleMarkAllRead = () => {
    markAllRead.mutate();
  };

  const handleDelete = (notificationId: number) => {
    deleteNotification.mutate(notificationId);
  };

  return (
    <div className={`relative ${className}`}>
      {/* 알림 버튼 */}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <Badge 
            variant="destructive" 
            className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center"
          >
            {unreadCount > 99 ? '99+' : unreadCount}
          </Badge>
        )}
      </Button>

      {/* 알림 패널 */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-lg shadow-lg border z-50">
          {/* 헤더 */}
          <div className="flex items-center justify-between p-4 border-b">
            <h3 className="font-semibold text-gray-900">알림</h3>
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleMarkAllRead}
                disabled={unreadCount === 0}
                className="text-xs"
              >
                모두 읽음
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsOpen(false)}
                className="text-xs"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* 탭 */}
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('all')}
              className={`flex-1 px-4 py-2 text-sm font-medium ${
                activeTab === 'all'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              전체
            </button>
            <button
              onClick={() => setActiveTab('unread')}
              className={`flex-1 px-4 py-2 text-sm font-medium ${
                activeTab === 'unread'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              읽지 않음
              {unreadCount > 0 && (
                <Badge variant="secondary" className="ml-1 text-xs">
                  {unreadCount}
                </Badge>
              )}
            </button>
          </div>

          {/* 알림 목록 */}
          <div className="max-h-96 overflow-y-auto">
            {isLoading ? (
              <div className="p-4 text-center text-gray-500">
                로딩 중...
              </div>
            ) : notifications.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <Bell className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                <p>알림이 없습니다</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {notifications.map((notification: any) => (
                  <div
                    key={notification.id}
                    className={`p-4 hover:bg-gray-50 transition-colors ${
                      !notification.read ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-0.5">
                        {getNotificationIcon(notification.type)}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-900">
                            {notification.title}
                          </p>
                          <div className="flex items-center space-x-1">
                            <Badge 
                              variant="outline" 
                              className={`text-xs ${getPriorityColor(notification.priority)}`}
                            >
                              {notification.priority}
                            </Badge>
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                                  <MoreHorizontal className="h-3 w-3" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                {!notification.read && (
                                  <DropdownMenuItem
                                    onClick={() => handleMarkRead(notification.id)}
                                  >
                                    <Check className="h-4 w-4 mr-2" />
                                    읽음 처리
                                  </DropdownMenuItem>
                                )}
                                <DropdownMenuItem
                                  onClick={() => handleDelete(notification.id)}
                                  className="text-red-600"
                                >
                                  <Trash2 className="h-4 w-4 mr-2" />
                                  삭제
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </div>
                        </div>
                        
                        <p className="text-sm text-gray-600 mt-1">
                          {notification.message}
                        </p>
                        
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-xs text-gray-400">
                            {formatTime(notification.created_at)}
                          </span>
                          
                          {!notification.read && (
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 푸터 */}
          {notifications.length > 0 && (
            <div className="p-3 border-t bg-gray-50">
              <Button
                variant="ghost"
                size="sm"
                className="w-full text-sm text-gray-600 hover:text-gray-900"
                onClick={() => {
                  // 알림 설정 페이지로 이동
                  window.location.href = '/notifications';
                }}
              >
                <Settings className="h-4 w-4 mr-2" />
                알림 설정
              </Button>
            </div>
          )}
        </div>
      )}

      {/* 백드롭 */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
} 