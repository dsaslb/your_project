/**
 * 고급 푸시 알림 시스템
 * 실시간 알림, 스케줄링, 액션 버튼, 딥링크 지원
 */

import PushNotification from 'react-native-push-notification';
import PushNotificationIOS from '@react-native-community/push-notification-ios';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { v4 as uuidv4 } from 'uuid';

export interface NotificationConfig {
  id: string;
  title: string;
  message: string;
  data?: any;
  sound?: string;
  badge?: number;
  category?: string;
  actions?: NotificationAction[];
  schedule?: NotificationSchedule;
  priority?: 'high' | 'default' | 'low';
  autoCancel?: boolean;
  vibrate?: boolean;
  vibration?: number;
  tag?: string;
  group?: string;
  groupSummary?: boolean;
  ongoing?: boolean;
  autoClear?: boolean;
  largeIcon?: string;
  bigText?: string;
  subText?: string;
  color?: string;
  number?: number;
  channelId?: string;
}

export interface NotificationAction {
  id: string;
  title: string;
  icon?: string;
  launchApp?: boolean;
  foreground?: boolean;
  destructive?: boolean;
  authenticationRequired?: boolean;
}

export interface NotificationSchedule {
  date?: Date;
  repeatType?: 'time' | 'day' | 'week' | 'month' | 'year';
  repeatTime?: number;
  fireDate?: number;
  exact?: boolean;
  allowWhileIdle?: boolean;
}

export interface NotificationCategory {
  id: string;
  actions: NotificationAction[];
  options?: {
    allowInCarPlay?: boolean;
    allowAnnouncement?: boolean;
    hiddenPreviewsShowTitle?: boolean;
    hiddenPreviewsShowSubtitle?: boolean;
  };
}

export class AdvancedPushNotificationService {
  private isInitialized = false;
  private notificationCategories: Map<string, NotificationCategory> = new Map();
  private notificationListeners: Map<string, (notification: any) => void> = new Map();
  private scheduledNotifications: Map<string, NotificationConfig> = new Map();

  constructor() {
    this.initialize();
  }

  /**
   * 서비스 초기화
   */
  private initialize(): void {
    if (this.isInitialized) return;

    // 기본 채널 설정 (Android)
    if (Platform.OS === 'android') {
      this.createDefaultChannels();
    }

    // 알림 권한 요청
    this.requestPermissions();

    // 이벤트 리스너 설정
    this.setupEventListeners();

    // 기본 카테고리 설정
    this.setupDefaultCategories();

    this.isInitialized = true;
    console.log('고급 푸시 알림 서비스 초기화 완료');
  }

  /**
   * 기본 채널 생성 (Android)
   */
  private createDefaultChannels(): void {
    const channels = [
      {
        channelId: 'default',
        channelName: '기본 알림',
        channelDescription: '일반적인 알림',
        playSound: true,
        soundName: 'default',
        importance: 4,
        vibrate: true,
        vibration: 300,
      },
      {
        channelId: 'high_priority',
        channelName: '중요 알림',
        channelDescription: '중요한 알림',
        playSound: true,
        soundName: 'default',
        importance: 5,
        vibrate: true,
        vibration: 500,
      },
      {
        channelId: 'silent',
        channelName: '조용한 알림',
        channelDescription: '소리 없는 알림',
        playSound: false,
        importance: 3,
        vibrate: false,
      },
    ];

    channels.forEach(channel => {
      PushNotification.createChannel(channel, (created) => {
        console.log(`채널 생성 ${channel.channelId}: ${created}`);
      });
    });
  }

  /**
   * 알림 권한 요청
   */
  private async requestPermissions(): Promise<void> {
    try {
      if (Platform.OS === 'ios') {
        const authStatus = await PushNotificationIOS.requestPermissions({
          alert: true,
          badge: true,
          sound: true,
          critical: true,
          provisional: false,
        });
        console.log('iOS 알림 권한 상태:', authStatus);
      } else {
        PushNotification.requestPermissions(['alert', 'badge', 'sound']);
      }
    } catch (error) {
      console.error('알림 권한 요청 오류:', error);
    }
  }

  /**
   * 이벤트 리스너 설정
   */
  private setupEventListeners(): void {
    // 알림 수신
    PushNotification.onNotification((notification) => {
      console.log('알림 수신:', notification);
      this.handleNotificationReceived(notification);
    });

    // 알림 열림
    PushNotification.onNotificationOpenedApp((notification) => {
      console.log('앱이 알림으로 열림:', notification);
      this.handleNotificationOpened(notification);
    });

    // 초기 알림 (앱이 종료된 상태에서 알림으로 열림)
    PushNotification.getInitialNotification().then((notification) => {
      if (notification) {
        console.log('초기 알림:', notification);
        this.handleInitialNotification(notification);
      }
    });

    // iOS 전용 이벤트
    if (Platform.OS === 'ios') {
      PushNotificationIOS.addEventListener('notification', (notification) => {
        console.log('iOS 알림 수신:', notification);
        this.handleIOSNotification(notification);
      });

      PushNotificationIOS.addEventListener('localNotification', (notification) => {
        console.log('iOS 로컬 알림:', notification);
        this.handleIOSLocalNotification(notification);
      });

      PushNotificationIOS.addEventListener('register', (token) => {
        console.log('iOS 디바이스 토큰:', token);
        this.saveDeviceToken(token);
      });

      PushNotificationIOS.addEventListener('registrationError', (error) => {
        console.error('iOS 토큰 등록 오류:', error);
      });
    }
  }

  /**
   * 기본 카테고리 설정
   */
  private setupDefaultCategories(): void {
    const categories: NotificationCategory[] = [
      {
        id: 'message',
        actions: [
          {
            id: 'reply',
            title: '답장',
            icon: 'reply',
            foreground: true,
          },
          {
            id: 'mark_read',
            title: '읽음 표시',
            icon: 'check',
          },
        ],
      },
      {
        id: 'order',
        actions: [
          {
            id: 'view_order',
            title: '주문 보기',
            icon: 'eye',
            foreground: true,
          },
          {
            id: 'track_order',
            title: '배송 추적',
            icon: 'location',
            foreground: true,
          },
        ],
      },
      {
        id: 'promotion',
        actions: [
          {
            id: 'view_offer',
            title: '혜택 보기',
            icon: 'gift',
            foreground: true,
          },
          {
            id: 'dismiss',
            title: '닫기',
            icon: 'close',
            destructive: true,
          },
        ],
      },
    ];

    categories.forEach(category => {
      this.addNotificationCategory(category);
    });
  }

  /**
   * 알림 카테고리 추가
   */
  addNotificationCategory(category: NotificationCategory): void {
    this.notificationCategories.set(category.id, category);

    if (Platform.OS === 'ios') {
      const actions = category.actions.map(action => ({
        id: action.id,
        title: action.title,
        options: {
          foreground: action.foreground,
          destructive: action.destructive,
          authenticationRequired: action.authenticationRequired,
        },
      }));

      PushNotificationIOS.addNotificationRequest({
        id: category.id,
        title: '',
        body: '',
        categoryId: category.id,
        threadId: category.id,
      });
    }
  }

  /**
   * 즉시 알림 전송
   */
  async sendNotification(config: NotificationConfig): Promise<string> {
    const notificationId = config.id || uuidv4();

    try {
      if (Platform.OS === 'android') {
        PushNotification.localNotification({
          id: notificationId,
          channelId: config.channelId || 'default',
          title: config.title,
          message: config.message,
          data: config.data,
          soundName: config.sound || 'default',
          number: config.badge || config.number,
          autoCancel: config.autoCancel !== false,
          vibrate: config.vibrate !== false,
          vibration: config.vibration || 300,
          tag: config.tag,
          group: config.group,
          groupSummary: config.groupSummary,
          ongoing: config.ongoing,
          autoClear: config.autoClear !== false,
          largeIcon: config.largeIcon,
          bigText: config.bigText,
          subText: config.subText,
          color: config.color,
          priority: config.priority || 'default',
        });
      } else {
        PushNotificationIOS.addNotificationRequest({
          id: notificationId,
          title: config.title,
          body: config.message,
          data: config.data,
          sound: config.sound || 'default',
          badge: config.badge,
          categoryId: config.category,
          threadId: config.group,
          userInfo: config.data,
        });
      }

      console.log(`알림 전송 완료: ${notificationId}`);
      return notificationId;
    } catch (error) {
      console.error('알림 전송 오류:', error);
      throw error;
    }
  }

  /**
   * 스케줄된 알림 전송
   */
  async scheduleNotification(config: NotificationConfig): Promise<string> {
    const notificationId = config.id || uuidv4();

    if (!config.schedule) {
      throw new Error('스케줄 정보가 필요합니다');
    }

    try {
      const scheduleConfig = {
        id: notificationId,
        channelId: config.channelId || 'default',
        title: config.title,
        message: config.message,
        data: config.data,
        soundName: config.sound || 'default',
        number: config.badge || config.number,
        autoCancel: config.autoCancel !== false,
        vibrate: config.vibrate !== false,
        vibration: config.vibration || 300,
        tag: config.tag,
        group: config.group,
        groupSummary: config.groupSummary,
        ongoing: config.ongoing,
        autoClear: config.autoClear !== false,
        largeIcon: config.largeIcon,
        bigText: config.bigText,
        subText: config.subText,
        color: config.color,
        priority: config.priority || 'default',
        date: config.schedule.date,
        repeatType: config.schedule.repeatType,
        repeatTime: config.schedule.repeatTime,
        fireDate: config.schedule.fireDate,
        exact: config.schedule.exact,
        allowWhileIdle: config.schedule.allowWhileIdle,
      };

      PushNotification.localNotificationSchedule(scheduleConfig);

      this.scheduledNotifications.set(notificationId, config);
      console.log(`스케줄된 알림 등록 완료: ${notificationId}`);
      return notificationId;
    } catch (error) {
      console.error('스케줄된 알림 등록 오류:', error);
      throw error;
    }
  }

  /**
   * 알림 취소
   */
  cancelNotification(notificationId: string): void {
    try {
      PushNotification.cancelLocalNotification(notificationId);
      this.scheduledNotifications.delete(notificationId);
      console.log(`알림 취소 완료: ${notificationId}`);
    } catch (error) {
      console.error('알림 취소 오류:', error);
    }
  }

  /**
   * 모든 알림 취소
   */
  cancelAllNotifications(): void {
    try {
      PushNotification.cancelAllLocalNotifications();
      this.scheduledNotifications.clear();
      console.log('모든 알림 취소 완료');
    } catch (error) {
      console.error('모든 알림 취소 오류:', error);
    }
  }

  /**
   * 알림 수신 처리
   */
  private handleNotificationReceived(notification: any): void {
    const listener = this.notificationListeners.get('received');
    if (listener) {
      listener(notification);
    }
  }

  /**
   * 알림 열림 처리
   */
  private handleNotificationOpened(notification: any): void {
    const listener = this.notificationListeners.get('opened');
    if (listener) {
      listener(notification);
    }
  }

  /**
   * 초기 알림 처리
   */
  private handleInitialNotification(notification: any): void {
    const listener = this.notificationListeners.get('initial');
    if (listener) {
      listener(notification);
    }
  }

  /**
   * iOS 알림 처리
   */
  private handleIOSNotification(notification: any): void {
    const listener = this.notificationListeners.get('ios');
    if (listener) {
      listener(notification);
    }
  }

  /**
   * iOS 로컬 알림 처리
   */
  private handleIOSLocalNotification(notification: any): void {
    const listener = this.notificationListeners.get('ios_local');
    if (listener) {
      listener(notification);
    }
  }

  /**
   * 디바이스 토큰 저장
   */
  private async saveDeviceToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem('device_token', token);
      console.log('디바이스 토큰 저장 완료');
    } catch (error) {
      console.error('디바이스 토큰 저장 오류:', error);
    }
  }

  /**
   * 디바이스 토큰 가져오기
   */
  async getDeviceToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem('device_token');
    } catch (error) {
      console.error('디바이스 토큰 가져오기 오류:', error);
      return null;
    }
  }

  /**
   * 알림 리스너 추가
   */
  addNotificationListener(
    event: 'received' | 'opened' | 'initial' | 'ios' | 'ios_local',
    listener: (notification: any) => void
  ): () => void {
    this.notificationListeners.set(event, listener);

    return () => {
      this.notificationListeners.delete(event);
    };
  }

  /**
   * 스케줄된 알림 목록 가져오기
   */
  getScheduledNotifications(): NotificationConfig[] {
    return Array.from(this.scheduledNotifications.values());
  }

  /**
   * 알림 배지 설정
   */
  setBadgeCount(count: number): void {
    try {
      if (Platform.OS === 'ios') {
        PushNotificationIOS.setApplicationIconBadgeNumber(count);
      } else {
        PushNotification.setApplicationIconBadgeNumber(count);
      }
    } catch (error) {
      console.error('배지 설정 오류:', error);
    }
  }

  /**
   * 알림 배지 초기화
   */
  clearBadge(): void {
    this.setBadgeCount(0);
  }

  /**
   * 서비스 정리
   */
  destroy(): void {
    this.notificationListeners.clear();
    this.scheduledNotifications.clear();
    console.log('고급 푸시 알림 서비스 정리 완료');
  }
}

// 싱글톤 인스턴스
export const advancedPushNotificationService = new AdvancedPushNotificationService();

// 사용 예시
export const useAdvancedPushNotifications = () => {
  return {
    sendNotification: advancedPushNotificationService.sendNotification.bind(advancedPushNotificationService),
    scheduleNotification: advancedPushNotificationService.scheduleNotification.bind(advancedPushNotificationService),
    cancelNotification: advancedPushNotificationService.cancelNotification.bind(advancedPushNotificationService),
    cancelAllNotifications: advancedPushNotificationService.cancelAllNotifications.bind(advancedPushNotificationService),
    getDeviceToken: advancedPushNotificationService.getDeviceToken.bind(advancedPushNotificationService),
    setBadgeCount: advancedPushNotificationService.setBadgeCount.bind(advancedPushNotificationService),
    clearBadge: advancedPushNotificationService.clearBadge.bind(advancedPushNotificationService),
    addNotificationListener: advancedPushNotificationService.addNotificationListener.bind(advancedPushNotificationService),
  };
}; 