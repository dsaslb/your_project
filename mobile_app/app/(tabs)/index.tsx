import { View, Text, StyleSheet, Alert, ScrollView } from "react-native";
import { useEffect, useState } from "react";
import { useAuth } from "../../src/auth/AuthContext";
import { mobileAPI } from "../../src/api/client";
import { socketEvents } from "../../src/api/socket";
import { OfflineIndicator } from "../../src/components/OfflineIndicator";

export default function Home() {
  const { user, loading } = useAuth();
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [realtimeUpdates, setRealtimeUpdates] = useState<string[]>([]);

  useEffect(() => {
    // 대시보드 데이터 로드
    const loadDashboard = async () => {
      try {
        const data = await mobileAPI.getDashboard();
        setDashboardData(data);
      } catch (error) {
        console.error('대시보드 로드 실패:', error);
      }
    };

    if (user) {
      loadDashboard();
    }

    // 실시간 이벤트 구독
    const unsubscribeAttendance = socketEvents.subscribeToAttendanceUpdates((data) => {
      setRealtimeUpdates(prev => [...prev, `출퇴근 업데이트: ${data.type}`]);
      Alert.alert('실시간 알림', `${data.type === 'in' ? '출근' : '퇴근'} 기록이 업데이트되었습니다.`);
    });

    const unsubscribeInventory = socketEvents.subscribeToInventoryUpdates((data) => {
      setRealtimeUpdates(prev => [...prev, `재고 업데이트: ${data.barcode}`]);
    });

    const unsubscribePO = socketEvents.subscribeToPurchaseOrderUpdates((data) => {
      setRealtimeUpdates(prev => [...prev, `발주 생성: ${data.order_id}`]);
    });

    return () => {
      unsubscribeAttendance();
      unsubscribeInventory();
      unsubscribePO();
    };
  }, [user]);

  if (loading) {
    return (
      <View style={styles.container}>
        <Text>로딩 중...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <OfflineIndicator />
      
      <View style={styles.content}>
        <Text style={styles.title}>🏠 홈</Text>
        {user ? (
          <>
            <Text style={styles.welcome}>안녕하세요, {user.username}님!</Text>
            
            {dashboardData && (
              <View style={styles.dashboard}>
                <Text style={styles.sectionTitle}>📊 대시보드</Text>
                <Text>대기 중인 발주: {dashboardData.pending_orders}건</Text>
                {dashboardData.today_schedule && (
                  <Text>오늘 스케줄: {dashboardData.today_schedule.start_time} - {dashboardData.today_schedule.end_time}</Text>
                )}
              </View>
            )}

            {realtimeUpdates.length > 0 && (
              <View style={styles.updates}>
                <Text style={styles.sectionTitle}>🔔 실시간 업데이트</Text>
                {realtimeUpdates.slice(-3).map((update, index) => (
                  <Text key={index} style={styles.updateText}>• {update}</Text>
                ))}
              </View>
            )}
          </>
        ) : (
          <Text style={styles.welcome}>로그인이 필요합니다.</Text>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    padding: 16,
    justifyContent: "flex-start",
    alignItems: "center",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 20,
  },
  welcome: {
    fontSize: 16,
    textAlign: "center",
    marginBottom: 20,
  },
  dashboard: {
    backgroundColor: '#f0f0f0',
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
    width: '100%',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  updates: {
    backgroundColor: '#e8f4fd',
    padding: 16,
    borderRadius: 8,
    width: '100%',
  },
  updateText: {
    fontSize: 14,
    marginBottom: 4,
  },
});
