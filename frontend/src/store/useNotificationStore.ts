import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export type Notification = {
  id: string;
  title: string;
  message: string;
  type: NotificationType;
  timestamp: string;
  isRead: boolean;
  category?: string;
  actionUrl?: string;
};

interface NotificationStore {
  notifications: Notification[];
  unreadCount: number;
  isConnected: boolean;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'isRead'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string) => void;
  clearAll: () => void;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
}

export const useNotificationStore = create<NotificationStore>()(
  persist(
    (set, get) => ({
      notifications: [],
      unreadCount: 0,
      isConnected: false,
      
      addNotification: (notification) => {
        const newNotification: Notification = {
          ...notification,
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          isRead: false,
        };
        
        set((state) => ({
          notifications: [newNotification, ...state.notifications],
          unreadCount: state.unreadCount + 1,
        }));
        
        // 브라우저 알림 표시 (사용자 권한 확인 필요)
        if ('Notification' in window && Notification.permission === 'granted') {
          new Notification(notification.title, {
            body: notification.message,
            icon: '/favicon.ico',
          });
        }
      },
      
      markAsRead: (id: string) => {
        set((state) => ({
          notifications: state.notifications.map((n) =>
            n.id === id ? { ...n, isRead: true } : n
          ),
          unreadCount: Math.max(0, state.unreadCount - 1),
        }));
      },
      
      markAllAsRead: () => {
        set((state) => ({
          notifications: state.notifications.map((n) => ({ ...n, isRead: true })),
          unreadCount: 0,
        }));
      },
      
      removeNotification: (id: string) => {
        set((state) => {
          const notification = state.notifications.find((n) => n.id === id);
          return {
            notifications: state.notifications.filter((n) => n.id !== id),
            unreadCount: notification?.isRead ? state.unreadCount : Math.max(0, state.unreadCount - 1),
          };
        });
      },
      
      clearAll: () => {
        set({ notifications: [], unreadCount: 0 });
      },
      
      connectWebSocket: () => {
        // WebSocket 연결 (실제 서버 주소로 교체)
        try {
          const ws = new WebSocket('ws://localhost:5001');
          
          ws.onopen = () => {
            set({ isConnected: true });
            console.log('WebSocket 연결됨');
          };
          
          ws.onmessage = (event) => {
            try {
              const data = JSON.parse(event.data);
              if (data.type === 'notification' || data.title) {
                get().addNotification({
                  title: data.title,
                  message: data.message,
                  type: data.type || data.notificationType || 'info',
                  category: data.category,
                  actionUrl: data.actionUrl,
                });
              }
            } catch (error) {
              console.error('알림 데이터 파싱 오류:', error);
            }
          };
          
          ws.onclose = () => {
            set({ isConnected: false });
            console.log('WebSocket 연결 끊어짐');
            // 재연결 시도
            setTimeout(() => {
              get().connectWebSocket();
            }, 5000);
          };
          
          ws.onerror = (error) => {
            console.error('WebSocket 오류:', error);
            set({ isConnected: false });
          };
          
          // WebSocket 인스턴스를 저장 (필요시)
          (window as any).notificationWebSocket = ws;
        } catch (error) {
          console.error('WebSocket 연결 실패:', error);
          set({ isConnected: false });
        }
      },
      
      disconnectWebSocket: () => {
        const ws = (window as any).notificationWebSocket;
        if (ws) {
          ws.close();
          (window as any).notificationWebSocket = null;
        }
        set({ isConnected: false });
      },
    }),
    {
      name: 'notification-store',
    }
  )
); 