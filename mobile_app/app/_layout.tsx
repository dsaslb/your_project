import { Tabs } from "expo-router";
import { AuthProvider } from "../src/auth/AuthContext";
import { useEffect } from "react";
import { notificationService } from "../src/services/NotificationService";
import { localStorageService } from "../src/services/LocalStorageService";
import { syncManager } from "../src/services/SyncManager";

export default function RootLayout() {
  useEffect(() => {
    // 서비스 초기화
    const initializeServices = async () => {
      try {
        // 로컬 스토리지 초기화
        await localStorageService.initialize();
        console.log('로컬 스토리지 초기화 완료');

        // 푸시 알림 초기화
        await notificationService.initialize();
        
        // 출근/퇴근 알림 스케줄링 (기본값: 9시 출근, 18시 퇴근)
        await notificationService.scheduleClockInReminder(9, 0);
        await notificationService.scheduleClockOutReminder(18, 0);
        
        console.log('푸시 알림 초기화 완료');
      } catch (error) {
        console.error('서비스 초기화 실패:', error);
      }
    };

    initializeServices();

    // 알림 응답 리스너 설정
    const notificationResponseListener = notificationService.addNotificationResponseListener(
      (response) => {
        const data = response.notification.request.content.data;
        console.log('알림 응답:', data);
        
        // 알림 타입에 따른 처리
        if (data?.type === 'clock_in_reminder') {
          // 출근 체크 화면으로 이동
          console.log('출근 체크 알림 탭됨');
        } else if (data?.type === 'clock_out_reminder') {
          // 퇴근 체크 화면으로 이동
          console.log('퇴근 체크 알림 탭됨');
        }
      }
    );

    return () => {
      notificationResponseListener.remove();
      // 서비스 정리
      syncManager.destroy();
    };
  }, []);

  return (
    <AuthProvider>
      <Tabs>
        <Tabs.Screen name="(tabs)/index"    options={{ title: "홈" }} />
        <Tabs.Screen name="(tabs)/clock"    options={{ title: "출/퇴근" }} />
        <Tabs.Screen name="(tabs)/schedule" options={{ title: "스케줄" }} />
        <Tabs.Screen name="(tabs)/tasks"    options={{ title: "업무" }} />
        <Tabs.Screen name="(tabs)/profile"  options={{ title: "마이" }} />
      </Tabs>
    </AuthProvider>
  );
}
