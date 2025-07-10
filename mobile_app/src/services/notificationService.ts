import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * 알림 서비스
 * 앱의 모든 알림 기능을 관리합니다.
 */
export class NotificationService {
  private static instance: NotificationService;
  private isInitialized = false;

  private constructor() {}

  public static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }

  /**
   * 알림 서비스 초기화
   */
  public async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    try {
      console.log('🔔 알림 서비스 초기화 시작...');

      // 알림 핸들러 설정
      Notifications.setNotificationHandler({
        handleNotification: async () => ({
          shouldShowAlert: true,
          shouldPlaySound: true,
          shouldSetBadge: false,
        }),
      });

      // 알림 채널 설정 (Android)
      if (Device.isDevice) {
        await this.setupNotificationChannels();
      }

      // 알림 토큰 가져오기
      await this.getNotificationToken();

      this.isInitialized = true;
      console.log('✅ 알림 서비스 초기화 완료');
    } catch (error) {
      console.error('❌ 알림 서비스 초기화 실패:', error);
      throw error;
    }
  }

  /**
   * 알림 채널 설정
   */
  private async setupNotificationChannels(): Promise<void> {
    try {
      // 기본 알림 채널
      await Notifications.setNotificationChannelAsync('default', {
        name: '기본 알림',
        importance: Notifications.AndroidImportance.HIGH,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF231F7C',
        sound: 'default',
      });

      // 출근 알림 채널
      await Notifications.setNotificationChannelAsync('attendance', {
        name: '출근 알림',
        importance: Notifications.AndroidImportance.HIGH,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#10B981',
        sound: 'default',
      });

      // 주문 알림 채널
      await Notifications.setNotificationChannelAsync('orders', {
        name: '주문 알림',
        importance: Notifications.AndroidImportance.HIGH,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#3B82F6',
        sound: 'default',
      });

      // 재고 알림 채널
      await Notifications.setNotificationChannelAsync('inventory', {
        name: '재고 알림',
        importance: Notifications.AndroidImportance.MEDIUM,
        vibrationPattern: [0, 250],
        lightColor: '#F59E0B',
        sound: 'default',
      });

      // 시스템 알림 채널
      await Notifications.setNotificationChannelAsync('system', {
        name: '시스템 알림',
        importance: Notifications.AndroidImportance.LOW,
        vibrationPattern: [0, 100],
        lightColor: '#6B7280',
        sound: 'default',
      });

      console.log('📱 알림 채널 설정 완료');
    } catch (error) {
      console.error('알림 채널 설정 실패:', error);
    }
  }

  /**
   * 알림 토큰 가져오기
   */
  private async getNotificationToken(): Promise<void> {
    try {
      if (!Device.isDevice) {
        console.log('시뮬레이터에서는 푸시 알림을 받을 수 없습니다.');
        return;
      }

      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        console.warn('알림 권한이 거부됨');
        return;
      }

      const token = await Notifications.getExpoPushTokenAsync({
        projectId: 'your-project-id', // Expo 프로젝트 ID로 변경
      });

      // 토큰 저장
      await AsyncStorage.setItem('notification_token', token.data);
      console.log('📱 알림 토큰 저장됨:', token.data);

      // 서버에 토큰 전송 (필요시)
      // await this.sendTokenToServer(token.data);

    } catch (error) {
      console.error('알림 토큰 가져오기 실패:', error);
    }
  }

  /**
   * 로컬 알림 보내기
   */
  public async sendLocalNotification(
    title: string,
    body: string,
    data?: any,
    channelId: string = 'default'
  ): Promise<string> {
    try {
      const notificationId = await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data,
          sound: 'default',
        },
        trigger: null, // 즉시 발송
      });

      console.log('📱 로컬 알림 발송됨:', notificationId);
      return notificationId;
    } catch (error) {
      console.error('로컬 알림 발송 실패:', error);
      throw error;
    }
  }

  /**
   * 예약 알림 보내기
   */
  public async scheduleNotification(
    title: string,
    body: string,
    trigger: Notifications.NotificationTriggerInput,
    data?: any,
    channelId: string = 'default'
  ): Promise<string> {
    try {
      const notificationId = await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data,
          sound: 'default',
        },
        trigger,
      });

      console.log('📱 예약 알림 설정됨:', notificationId);
      return notificationId;
    } catch (error) {
      console.error('예약 알림 설정 실패:', error);
      throw error;
    }
  }

  /**
   * 출근 알림 보내기
   */
  public async sendAttendanceNotification(
    type: 'checkin' | 'checkout' | 'reminder',
    userName?: string
  ): Promise<void> {
    try {
      let title = '';
      let body = '';

      switch (type) {
        case 'checkin':
          title = '출근 완료';
          body = `${userName || '직원'}님이 출근하셨습니다.`;
          break;
        case 'checkout':
          title = '퇴근 완료';
          body = `${userName || '직원'}님이 퇴근하셨습니다.`;
          break;
        case 'reminder':
          title = '출근 알림';
          body = '출근 시간이 되었습니다. 출근을 확인해주세요.';
          break;
      }

      await this.sendLocalNotification(title, body, { type: 'attendance' }, 'attendance');
    } catch (error) {
      console.error('출근 알림 발송 실패:', error);
    }
  }

  /**
   * 주문 알림 보내기
   */
  public async sendOrderNotification(
    type: 'new' | 'update' | 'complete',
    orderId: string,
    orderDetails?: string
  ): Promise<void> {
    try {
      let title = '';
      let body = '';

      switch (type) {
        case 'new':
          title = '새 주문';
          body = `새로운 주문이 들어왔습니다. (주문번호: ${orderId})`;
          break;
        case 'update':
          title = '주문 상태 변경';
          body = `주문 상태가 변경되었습니다. (주문번호: ${orderId})`;
          break;
        case 'complete':
          title = '주문 완료';
          body = `주문이 완료되었습니다. (주문번호: ${orderId})`;
          break;
      }

      await this.sendLocalNotification(title, body, { type: 'order', orderId }, 'orders');
    } catch (error) {
      console.error('주문 알림 발송 실패:', error);
    }
  }

  /**
   * 재고 알림 보내기
   */
  public async sendInventoryNotification(
    type: 'low' | 'out' | 'expired',
    itemName: string,
    quantity?: number
  ): Promise<void> {
    try {
      let title = '';
      let body = '';

      switch (type) {
        case 'low':
          title = '재고 부족';
          body = `${itemName}의 재고가 부족합니다. (현재: ${quantity}개)`;
          break;
        case 'out':
          title = '재고 소진';
          body = `${itemName}의 재고가 소진되었습니다.`;
          break;
        case 'expired':
          title = '유통기한 만료';
          body = `${itemName}의 유통기한이 만료되었습니다.`;
          break;
      }

      await this.sendLocalNotification(title, body, { type: 'inventory', itemName }, 'inventory');
    } catch (error) {
      console.error('재고 알림 발송 실패:', error);
    }
  }

  /**
   * 시스템 알림 보내기
   */
  public async sendSystemNotification(
    title: string,
    body: string,
    data?: any
  ): Promise<void> {
    try {
      await this.sendLocalNotification(title, body, { type: 'system', ...data }, 'system');
    } catch (error) {
      console.error('시스템 알림 발송 실패:', error);
    }
  }

  /**
   * 모든 알림 취소
   */
  public async cancelAllNotifications(): Promise<void> {
    try {
      await Notifications.cancelAllScheduledNotificationsAsync();
      console.log('📱 모든 예약 알림 취소됨');
    } catch (error) {
      console.error('알림 취소 실패:', error);
    }
  }

  /**
   * 특정 알림 취소
   */
  public async cancelNotification(notificationId: string): Promise<void> {
    try {
      await Notifications.cancelScheduledNotificationAsync(notificationId);
      console.log('📱 알림 취소됨:', notificationId);
    } catch (error) {
      console.error('알림 취소 실패:', error);
    }
  }

  /**
   * 알림 권한 확인
   */
  public async checkPermission(): Promise<boolean> {
    try {
      const { status } = await Notifications.getPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('알림 권한 확인 실패:', error);
      return false;
    }
  }

  /**
   * 알림 권한 요청
   */
  public async requestPermission(): Promise<boolean> {
    try {
      const { status } = await Notifications.requestPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('알림 권한 요청 실패:', error);
      return false;
    }
  }

  /**
   * 알림 설정 가져오기
   */
  public async getNotificationSettings(): Promise<any> {
    try {
      const settings = await AsyncStorage.getItem('notification_settings');
      return settings ? JSON.parse(settings) : {
        enabled: true,
        sound: true,
        vibration: true,
        attendance: true,
        orders: true,
        inventory: true,
        system: true,
      };
    } catch (error) {
      console.error('알림 설정 가져오기 실패:', error);
      return {};
    }
  }

  /**
   * 알림 설정 업데이트
   */
  public async updateNotificationSettings(settings: any): Promise<void> {
    try {
      await AsyncStorage.setItem('notification_settings', JSON.stringify(settings));
      console.log('📝 알림 설정 업데이트됨');
    } catch (error) {
      console.error('알림 설정 업데이트 실패:', error);
    }
  }
}

// 싱글톤 인스턴스 내보내기
export const notificationService = NotificationService.getInstance();

// 편의 함수
export const setupNotifications = async (): Promise<void> => {
  return notificationService.initialize();
}; 