import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import { mobileAPI } from '../api/client';

// 알림 핸들러 설정
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export class NotificationService {
  private static instance: NotificationService;
  private pushToken: string | null = null;

  private constructor() {}

  public static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }

  /**
   * 푸시 알림 권한 요청 및 토큰 등록
   */
  async initialize(): Promise<string | null> {
    try {
      // 권한 요청
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        console.warn('푸시 알림 권한이 거부되었습니다.');
        return null;
      }

      // 물리적 디바이스에서만 토큰 생성
      if (Device.isDevice) {
        const token = await Notifications.getExpoPushTokenAsync({
          projectId: 'mobile-app-test', // app.config.ts의 projectId와 일치해야 함
        });
        
        this.pushToken = token.data;
        console.log('푸시 토큰 획득:', this.pushToken);

        // 서버에 토큰 등록
        await this.registerPushToken(this.pushToken);
        
        return this.pushToken;
      } else {
        console.warn('시뮬레이터에서는 푸시 알림을 사용할 수 없습니다.');
        return null;
      }
    } catch (error) {
      console.error('푸시 알림 초기화 실패:', error);
      return null;
    }
  }

  /**
   * 서버에 푸시 토큰 등록
   */
  private async registerPushToken(token: string): Promise<void> {
    try {
      await mobileAPI.registerPushToken(token, Platform.OS);
      console.log('푸시 토큰 서버 등록 완료');
    } catch (error) {
      console.error('푸시 토큰 서버 등록 실패:', error);
      // 로그인 후에 다시 시도할 수 있도록 토큰을 저장
      this.pushToken = token;
    }
  }

  /**
   * 로컬 알림 스케줄링
   */
  async scheduleLocalNotification(
    title: string,
    body: string,
    data?: any,
    trigger?: Notifications.NotificationTriggerInput
  ): Promise<string> {
    try {
      const notificationId = await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data,
          sound: 'default',
        },
        trigger: trigger || null, // 즉시 발송
      });

      console.log('로컬 알림 스케줄링 완료:', notificationId);
      return notificationId;
    } catch (error) {
      console.error('로컬 알림 스케줄링 실패:', error);
      throw error;
    }
  }

  /**
   * 출근 시간 알림 스케줄링
   */
  async scheduleClockInReminder(hour: number = 9, minute: number = 0): Promise<void> {
    try {
      await this.scheduleLocalNotification(
        '출근 시간입니다!',
        '오늘도 좋은 하루 되세요. 출근 체크를 해주세요.',
        { type: 'clock_in_reminder' },
        {
          hour,
          minute,
          repeats: true,
        }
      );
    } catch (error) {
      console.error('출근 알림 스케줄링 실패:', error);
    }
  }

  /**
   * 퇴근 시간 알림 스케줄링
   */
  async scheduleClockOutReminder(hour: number = 18, minute: number = 0): Promise<void> {
    try {
      await this.scheduleLocalNotification(
        '퇴근 시간입니다!',
        '수고하셨습니다. 퇴근 체크를 해주세요.',
        { type: 'clock_out_reminder' },
        {
          hour,
          minute,
          repeats: true,
        }
      );
    } catch (error) {
      console.error('퇴근 알림 스케줄링 실패:', error);
    }
  }

  /**
   * 재고 부족 알림
   */
  async scheduleLowStockAlert(productName: string, currentStock: number): Promise<void> {
    try {
      await this.scheduleLocalNotification(
        '재고 부족 알림',
        `${productName}의 재고가 ${currentStock}개 남았습니다.`,
        { type: 'low_stock', productName, currentStock }
      );
    } catch (error) {
      console.error('재고 부족 알림 실패:', error);
    }
  }

  /**
   * 발주 승인 알림
   */
  async schedulePurchaseOrderApproval(orderId: string, amount: number): Promise<void> {
    try {
      await this.scheduleLocalNotification(
        '발주 승인 완료',
        `발주 #${orderId} (${amount.toLocaleString()}원)이 승인되었습니다.`,
        { type: 'po_approval', orderId, amount }
      );
    } catch (error) {
      console.error('발주 승인 알림 실패:', error);
    }
  }

  /**
   * 모든 예약된 알림 취소
   */
  async cancelAllScheduledNotifications(): Promise<void> {
    try {
      await Notifications.cancelAllScheduledNotificationsAsync();
      console.log('모든 예약된 알림이 취소되었습니다.');
    } catch (error) {
      console.error('알림 취소 실패:', error);
    }
  }

  /**
   * 특정 알림 취소
   */
  async cancelNotification(notificationId: string): Promise<void> {
    try {
      await Notifications.cancelScheduledNotificationAsync(notificationId);
      console.log('알림 취소 완료:', notificationId);
    } catch (error) {
      console.error('알림 취소 실패:', error);
    }
  }

  /**
   * 알림 리스너 설정
   */
  addNotificationListener(
    listener: (notification: Notifications.Notification) => void
  ): Notifications.Subscription {
    return Notifications.addNotificationReceivedListener(listener);
  }

  /**
   * 알림 응답 리스너 설정 (사용자가 알림을 탭했을 때)
   */
  addNotificationResponseListener(
    listener: (response: Notifications.NotificationResponse) => void
  ): Notifications.Subscription {
    return Notifications.addNotificationResponseReceivedListener(listener);
  }

  /**
   * 현재 푸시 토큰 반환
   */
  getPushToken(): string | null {
    return this.pushToken;
  }

  /**
   * 알림 배지 수 초기화
   */
  async clearBadge(): Promise<void> {
    try {
      await Notifications.setBadgeCountAsync(0);
    } catch (error) {
      console.error('배지 초기화 실패:', error);
    }
  }
}

// 싱글톤 인스턴스 내보내기
export const notificationService = NotificationService.getInstance();
