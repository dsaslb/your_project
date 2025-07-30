import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { Alert, AppState, AppStateStatus } from 'react-native';
import PushNotification from 'react-native-push-notification';
import { useAuth } from './AuthContext';
import { API_BASE_URL } from '../utils/config';

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  category: string;
  data?: any;
  timestamp: string;
  read: boolean;
  priority: 'low' | 'normal' | 'high';
}

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  fetchNotifications: () => Promise<void>;
  markAsRead: (notificationId: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  deleteNotification: (notificationId: string) => Promise<void>;
  clearAllNotifications: () => Promise<void>;
  sendLocalNotification: (title: string, message: string, data?: any) => void;
  configurePushNotifications: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

interface NotificationProviderProps {
  children: React.ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const { user, token } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const appState = useRef(AppState.currentState);
  const wsRef = useRef<WebSocket | null>(null);

  // 푸시 알림 설정
  const configurePushNotifications = () => {
    PushNotification.configure({
      onRegister: function (token) {
        console.log('TOKEN:', token);
        // 서버에 토큰 등록
        registerPushToken(token);
      },

      onNotification: function (notification) {
        console.log('NOTIFICATION:', notification);
        
        // 알림 클릭 시 처리
        if (notification.userInteraction) {
          handleNotificationTap(notification);
        }
      },

      permissions: {
        alert: true,
        badge: true,
        sound: true,
      },

      popInitialNotification: true,
      requestPermissions: true,
    });

    // 알림 채널 생성 (Android)
    PushNotification.createChannel(
      {
        channelId: 'default',
        channelName: '기본 알림',
        channelDescription: '기본 알림 채널',
        playSound: true,
        soundName: 'default',
        importance: 4,
        vibrate: true,
      },
      (created) => console.log(`알림 채널 생성: ${created}`)
    );

    // 카테고리별 채널 생성
    const categories = [
      {
        channelId: 'system',
        channelName: '시스템 알림',
        channelDescription: '시스템 관련 알림',
        importance: 4,
      },
      {
        channelId: 'business',
        channelName: '비즈니스 알림',
        channelDescription: '비즈니스 관련 알림',
        importance: 3,
      },
      {
        channelId: 'security',
        channelName: '보안 알림',
        channelDescription: '보안 관련 알림',
        importance: 5,
      },
    ];

    categories.forEach(category => {
      PushNotification.createChannel(category, (created) => 
        console.log(`${category.channelName} 채널 생성: ${created}`)
      );
    });
  };

  // 푸시 토큰 서버 등록
  const registerPushToken = async (pushToken: string) => {
    try {
      if (!token) return;

      const response = await fetch(`${API_BASE_URL}/api/notifications/register-token`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ push_token: pushToken }),
      });

      if (response.ok) {
        console.log('푸시 토큰 등록 성공');
      } else {
        console.error('푸시 토큰 등록 실패');
      }
    } catch (error) {
      console.error('푸시 토큰 등록 오류:', error);
    }
  };

  // 알림 목록 가져오기
  const fetchNotifications = async () => {
    try {
      if (!token) return;

      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/notifications`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
      } else {
        console.error('알림 목록 가져오기 실패');
      }
    } catch (error) {
      console.error('알림 목록 가져오기 오류:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 읽음 표시
  const markAsRead = async (notificationId: string) => {
    try {
      if (!token) return;

      const response = await fetch(`${API_BASE_URL}/api/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setNotifications(prev => 
          prev.map(notification => 
            notification.id === notificationId 
              ? { ...notification, read: true }
              : notification
          )
        );
      }
    } catch (error) {
      console.error('읽음 표시 오류:', error);
    }
  };

  // 전체 읽음 표시
  const markAllAsRead = async () => {
    try {
      if (!token) return;

      const response = await fetch(`${API_BASE_URL}/api/notifications/mark-all-read`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setNotifications(prev => 
          prev.map(notification => ({ ...notification, read: true }))
        );
      }
    } catch (error) {
      console.error('전체 읽음 표시 오류:', error);
    }
  };

  // 알림 삭제
  const deleteNotification = async (notificationId: string) => {
    try {
      if (!token) return;

      const response = await fetch(`${API_BASE_URL}/api/notifications/${notificationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setNotifications(prev => 
          prev.filter(notification => notification.id !== notificationId)
        );
      }
    } catch (error) {
      console.error('알림 삭제 오류:', error);
    }
  };

  // 전체 알림 삭제
  const clearAllNotifications = async () => {
    try {
      if (!token) return;

      const response = await fetch(`${API_BASE_URL}/api/notifications/clear-all`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setNotifications([]);
      }
    } catch (error) {
      console.error('전체 알림 삭제 오류:', error);
    }
  };

  // 로컬 알림 전송
  const sendLocalNotification = (title: string, message: string, data?: any) => {
    PushNotification.localNotification({
      channelId: 'default',
      title: title,
      message: message,
      data: data,
      playSound: true,
      soundName: 'default',
      importance: 'high',
      priority: 'high',
      vibrate: true,
      vibration: 300,
      autoCancel: true,
      largeIcon: 'ic_launcher',
      smallIcon: 'ic_notification',
    });
  };

  // 알림 탭 처리
  const handleNotificationTap = (notification: any) => {
    // 알림 데이터에 따라 적절한 화면으로 이동
    if (notification.data) {
      // 네비게이션 처리
      console.log('알림 탭됨:', notification.data);
    }
  };

  // WebSocket 연결
  const connectWebSocket = () => {
    if (!token || !user) return;

    try {
      const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws/notifications';
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket 연결됨');
        // 사용자 인증
        wsRef.current?.send(JSON.stringify({
          type: 'auth',
          token: token
        }));
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'notification') {
            // 새 알림 추가
            setNotifications(prev => [data.notification, ...prev]);
            
            // 로컬 알림 표시
            sendLocalNotification(
              data.notification.title,
              data.notification.message,
              data.notification.data
            );
          }
        } catch (error) {
          console.error('WebSocket 메시지 파싱 오류:', error);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket 오류:', error);
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket 연결 종료');
        // 재연결 시도
        setTimeout(connectWebSocket, 5000);
      };
    } catch (error) {
      console.error('WebSocket 연결 오류:', error);
    }
  };

  // 앱 상태 변경 처리
  const handleAppStateChange = (nextAppState: AppStateStatus) => {
    if (appState.current.match(/inactive|background/) && nextAppState === 'active') {
      // 앱이 포그라운드로 돌아올 때 알림 새로고침
      fetchNotifications();
    }
    appState.current = nextAppState;
  };

  // 초기화
  useEffect(() => {
    configurePushNotifications();
    
    if (user && token) {
      fetchNotifications();
      connectWebSocket();
    }

    const subscription = AppState.addEventListener('change', handleAppStateChange);

    return () => {
      subscription?.remove();
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [user, token]);

  // 읽지 않은 알림 수 계산
  const unreadCount = notifications.filter(notification => !notification.read).length;

  const value: NotificationContextType = {
    notifications,
    unreadCount,
    isLoading,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearAllNotifications,
    sendLocalNotification,
    configurePushNotifications,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
}; 