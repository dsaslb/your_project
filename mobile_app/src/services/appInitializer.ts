import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SplashScreen from 'expo-splash-screen';
import * as Notifications from 'expo-notifications';
import * as Location from 'expo-location';
import * as Device from 'expo-device';
import Constants from 'expo-constants';

/**
 * 앱 초기화 서비스
 * 앱 시작 시 필요한 모든 설정과 권한을 초기화합니다.
 */
export class AppInitializer {
  private static instance: AppInitializer;
  private isInitialized = false;

  private constructor() {}

  public static getInstance(): AppInitializer {
    if (!AppInitializer.instance) {
      AppInitializer.instance = new AppInitializer();
    }
    return AppInitializer.instance;
  }

  /**
   * 앱 초기화 실행
   */
  public async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    try {
      console.log('🚀 앱 초기화 시작...');

      // 1. 스플래시 스크린 유지
      await this.keepSplashScreen();

      // 2. 기본 설정 로드
      await this.loadDefaultSettings();

      // 3. 권한 요청
      await this.requestPermissions();

      // 4. 알림 설정
      await this.setupNotifications();

      // 5. 위치 서비스 설정
      await this.setupLocationServices();

      // 6. 네트워크 상태 확인
      await this.checkNetworkStatus();

      // 7. 캐시 정리
      await this.cleanupCache();

      this.isInitialized = true;
      console.log('✅ 앱 초기화 완료');
    } catch (error) {
      console.error('❌ 앱 초기화 실패:', error);
      throw error;
    }
  }

  /**
   * 스플래시 스크린 유지
   */
  private async keepSplashScreen(): Promise<void> {
    try {
      await SplashScreen.preventAutoHideAsync();
    } catch (error) {
      console.warn('스플래시 스크린 설정 실패:', error);
    }
  }

  /**
   * 기본 설정 로드
   */
  private async loadDefaultSettings(): Promise<void> {
    try {
      const defaultSettings = {
        theme: 'light',
        language: 'ko',
        notifications: true,
        locationTracking: true,
        autoSync: true,
        lastSync: null,
        appVersion: Constants.expoConfig?.version || '1.0.0',
      };

      // 기존 설정 확인
      const existingSettings = await AsyncStorage.getItem('app_settings');
      
      if (!existingSettings) {
        // 기본 설정 저장
        await AsyncStorage.setItem('app_settings', JSON.stringify(defaultSettings));
        console.log('📝 기본 설정 저장됨');
      } else {
        // 기존 설정과 기본 설정 병합
        const settings = JSON.parse(existingSettings);
        const mergedSettings = { ...defaultSettings, ...settings };
        await AsyncStorage.setItem('app_settings', JSON.stringify(mergedSettings));
        console.log('📝 설정 병합 완료');
      }
    } catch (error) {
      console.error('설정 로드 실패:', error);
    }
  }

  /**
   * 필요한 권한 요청
   */
  private async requestPermissions(): Promise<void> {
    try {
      console.log('🔐 권한 요청 시작...');

      // 위치 권한
      const locationPermission = await Location.requestForegroundPermissionsAsync();
      if (locationPermission.status !== 'granted') {
        console.warn('위치 권한이 거부됨');
      } else {
        console.log('✅ 위치 권한 허용됨');
      }

      // 알림 권한
      if (Device.isDevice) {
        const notificationPermission = await Notifications.requestPermissionsAsync();
        if (notificationPermission.status !== 'granted') {
          console.warn('알림 권한이 거부됨');
        } else {
          console.log('✅ 알림 권한 허용됨');
        }
      }

      // 카메라 권한 (필요시)
      // const cameraPermission = await Camera.requestCameraPermissionsAsync();
      // if (cameraPermission.status !== 'granted') {
      //   console.warn('카메라 권한이 거부됨');
      // }

    } catch (error) {
      console.error('권한 요청 실패:', error);
    }
  }

  /**
   * 알림 설정
   */
  private async setupNotifications(): Promise<void> {
    try {
      // 알림 핸들러 설정
      Notifications.setNotificationHandler({
        handleNotification: async () => ({
          shouldShowAlert: true,
          shouldPlaySound: true,
          shouldSetBadge: false,
        }),
      });

      // 기본 알림 채널 설정 (Android)
      if (Device.isDevice) {
        await Notifications.setNotificationChannelAsync('default', {
          name: '기본 알림',
          importance: Notifications.AndroidImportance.HIGH,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#FF231F7C',
        });

        // 출근 알림 채널
        await Notifications.setNotificationChannelAsync('attendance', {
          name: '출근 알림',
          importance: Notifications.AndroidImportance.HIGH,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#10B981',
        });

        // 주문 알림 채널
        await Notifications.setNotificationChannelAsync('orders', {
          name: '주문 알림',
          importance: Notifications.AndroidImportance.HIGH,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#3B82F6',
        });
      }

      console.log('🔔 알림 설정 완료');
    } catch (error) {
      console.error('알림 설정 실패:', error);
    }
  }

  /**
   * 위치 서비스 설정
   */
  private async setupLocationServices(): Promise<void> {
    try {
      // 위치 서비스 활성화 확인
      const locationEnabled = await Location.hasServicesEnabledAsync();
      if (!locationEnabled) {
        console.warn('위치 서비스가 비활성화됨');
        return;
      }

      // 현재 위치 가져오기 (권한 확인용)
      const currentLocation = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });

      if (currentLocation) {
        console.log('📍 현재 위치 확인됨:', {
          latitude: currentLocation.coords.latitude,
          longitude: currentLocation.coords.longitude,
        });
      }

      console.log('📍 위치 서비스 설정 완료');
    } catch (error) {
      console.error('위치 서비스 설정 실패:', error);
    }
  }

  /**
   * 네트워크 상태 확인
   */
  private async checkNetworkStatus(): Promise<void> {
    try {
      // 네트워크 연결 상태 확인
      const response = await fetch('https://www.google.com', {
        method: 'HEAD',
        timeout: 5000,
      });

      if (response.ok) {
        console.log('🌐 네트워크 연결 확인됨');
      } else {
        console.warn('⚠️ 네트워크 연결 불안정');
      }
    } catch (error) {
      console.warn('⚠️ 네트워크 연결 확인 실패:', error);
    }
  }

  /**
   * 캐시 정리
   */
  private async cleanupCache(): Promise<void> {
    try {
      // 오래된 캐시 데이터 정리
      const cacheKeys = await AsyncStorage.getAllKeys();
      const oldCacheKeys = cacheKeys.filter(key => 
        key.startsWith('cache_') && 
        key.includes('temp_')
      );

      if (oldCacheKeys.length > 0) {
        await AsyncStorage.multiRemove(oldCacheKeys);
        console.log(`🗑️ ${oldCacheKeys.length}개의 오래된 캐시 정리됨`);
      }
    } catch (error) {
      console.error('캐시 정리 실패:', error);
    }
  }

  /**
   * 앱 설정 가져오기
   */
  public async getSettings(): Promise<any> {
    try {
      const settings = await AsyncStorage.getItem('app_settings');
      return settings ? JSON.parse(settings) : {};
    } catch (error) {
      console.error('설정 가져오기 실패:', error);
      return {};
    }
  }

  /**
   * 앱 설정 업데이트
   */
  public async updateSettings(newSettings: any): Promise<void> {
    try {
      const currentSettings = await this.getSettings();
      const updatedSettings = { ...currentSettings, ...newSettings };
      await AsyncStorage.setItem('app_settings', JSON.stringify(updatedSettings));
      console.log('📝 설정 업데이트됨');
    } catch (error) {
      console.error('설정 업데이트 실패:', error);
    }
  }

  /**
   * 앱 버전 확인
   */
  public getAppVersion(): string {
    return Constants.expoConfig?.version || '1.0.0';
  }

  /**
   * 디바이스 정보 가져오기
   */
  public getDeviceInfo(): any {
    return {
      brand: Device.brand,
      manufacturer: Device.manufacturer,
      modelName: Device.modelName,
      osName: Device.osName,
      osVersion: Device.osVersion,
      platformApiLevel: Device.platformApiLevel,
    };
  }
}

// 싱글톤 인스턴스 내보내기
export const appInitializer = AppInitializer.getInstance();

// 편의 함수
export const initializeApp = async (): Promise<void> => {
  return appInitializer.initialize();
}; 