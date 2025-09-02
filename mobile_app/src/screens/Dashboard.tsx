/**
 * 🏠 대시보드 화면
 * 
 * 모바일 앱의 메인 대시보드
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { mobileAPI } from '../api/client';
import { subscribeToAttendanceUpdates, subscribeToInventoryUpdates } from '../api/socket';

interface DashboardData {
  user: {
    id: number;
    username: string;
    role: string;
  };
  today_schedule: string;
  attendance_status: string;
  pending_orders: number;
  inventory_alerts: number;
}

export default function DashboardScreen() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [realtimeUpdates, setRealtimeUpdates] = useState({
    attendance: 0,
    inventory: 0,
  });

  useEffect(() => {
    loadDashboardData();

    // 실시간 업데이트 구독 (에러 처리 포함)
    let unsubscribeAttendance: (() => void) | null = null;
    let unsubscribeInventory: (() => void) | null = null;

    try {
      unsubscribeAttendance = subscribeToAttendanceUpdates((data) => {
        setRealtimeUpdates(prev => ({
          ...prev,
          attendance: prev.attendance + 1
        }));
      });

      unsubscribeInventory = subscribeToInventoryUpdates((data) => {
        setRealtimeUpdates(prev => ({
          ...prev,
          inventory: prev.inventory + 1
        }));
      });
    } catch (error) {
      console.warn('Socket 구독 실패 (오프라인 모드):', error);
    }

    return () => {
      if (unsubscribeAttendance) unsubscribeAttendance();
      if (unsubscribeInventory) unsubscribeInventory();
    };
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const result = await mobileAPI.getDashboard();
      setDashboardData(result);
      console.log('대시보드 데이터 로드 성공:', result);
    } catch (error) {
      console.error('대시보드 데이터 로드 실패:', error);
      // 에러가 발생해도 기본 데이터는 표시됨 (API에서 기본값 반환)
      Alert.alert('알림', '서버에 연결할 수 없어 오프라인 모드로 실행 중입니다.');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case '출근':
        return '#4CAF50';
      case '퇴근':
        return '#F44336';
      default:
        return '#9E9E9E';
    }
  };

  const getRoleText = (role: string) => {
    switch (role) {
      case 'admin':
        return '관리자';
      case 'manager':
        return '매니저';
      case 'employee':
        return '직원';
      default:
        return role;
    }
  };

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* 헤더 */}
      <View style={styles.header}>
        <Text style={styles.title}>🏠 대시보드</Text>
        <Text style={styles.subtitle}>오늘의 업무 현황</Text>
      </View>

      {/* 사용자 정보 카드 */}
      {dashboardData?.user && (
        <View style={styles.userCard}>
          <View style={styles.userInfo}>
            <Text style={styles.userName}>{dashboardData.user.username}</Text>
            <Text style={styles.userRole}>{getRoleText(dashboardData.user.role)}</Text>
          </View>
          <View style={styles.userStatus}>
            <View style={[styles.statusDot, { backgroundColor: getStatusColor(dashboardData.attendance_status) }]} />
            <Text style={styles.statusText}>{dashboardData.attendance_status}</Text>
          </View>
        </View>
      )}

      {/* 오늘 스케줄 */}
      <View style={styles.scheduleCard}>
        <Text style={styles.cardTitle}>📅 오늘 스케줄</Text>
        <Text style={styles.scheduleText}>
          {dashboardData?.today_schedule || '스케줄 정보가 없습니다.'}
        </Text>
      </View>

      {/* 실시간 통계 */}
      <View style={styles.statsCard}>
        <Text style={styles.cardTitle}>📊 실시간 통계</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{realtimeUpdates.attendance}</Text>
            <Text style={styles.statLabel}>출퇴근</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{realtimeUpdates.inventory}</Text>
            <Text style={styles.statLabel}>재고</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{dashboardData?.pending_orders || 0}</Text>
            <Text style={styles.statLabel}>대기 주문</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{dashboardData?.inventory_alerts || 0}</Text>
            <Text style={styles.statLabel}>재고 알림</Text>
          </View>
        </View>
      </View>

      {/* 빠른 액션 */}
      <View style={styles.actionsCard}>
        <Text style={styles.cardTitle}>⚡ 빠른 액션</Text>
        <View style={styles.actionButtons}>
          <TouchableOpacity style={[styles.actionButton, styles.primaryButton]}>
            <Text style={styles.actionButtonText}>📱 출퇴근 체크</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.actionButton, styles.secondaryButton]}>
            <Text style={styles.actionButtonText}>📦 재고 조사</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.actionButtons}>
          <TouchableOpacity style={[styles.actionButton, styles.warningButton]}>
            <Text style={styles.actionButtonText}>📋 발주 생성</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.actionButton, styles.infoButton]}>
            <Text style={styles.actionButtonText}>📊 보고서</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* 최근 활동 */}
      <View style={styles.activityCard}>
        <Text style={styles.cardTitle}>🕒 최근 활동</Text>
        {dashboardData?.recent_activities && dashboardData.recent_activities.length > 0 ? (
          dashboardData.recent_activities.map((activity: any, index: number) => (
            <View key={activity.id || index} style={styles.activityItem}>
              <Text style={styles.activityText}>{activity.title}</Text>
              <Text style={styles.activityTime}>
                {activity.timestamp ? new Date(activity.timestamp).toLocaleTimeString() : '방금 전'}
              </Text>
            </View>
          ))
        ) : (
          <>
            <View style={styles.activityItem}>
              <Text style={styles.activityText}>출근 체크 완료</Text>
              <Text style={styles.activityTime}>방금 전</Text>
            </View>
            <View style={styles.activityItem}>
              <Text style={styles.activityText}>재고 조사 완료 (바코드: 123456789)</Text>
              <Text style={styles.activityTime}>5분 전</Text>
            </View>
            <View style={styles.activityItem}>
              <Text style={styles.activityText}>발주 요청 완료</Text>
              <Text style={styles.activityTime}>10분 전</Text>
            </View>
          </>
        )}
      </View>

      {/* 새로고침 버튼 */}
      <TouchableOpacity 
        style={styles.refreshButton}
        onPress={loadDashboardData}
        disabled={loading}
      >
        <Text style={styles.refreshButtonText}>
          {loading ? '로딩 중...' : '🔄 새로고침'}
        </Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#2196F3',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: 'white',
    opacity: 0.8,
  },
  userCard: {
    backgroundColor: 'white',
    margin: 20,
    padding: 20,
    borderRadius: 10,
    elevation: 3,
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)', // shadow* 대신 boxShadow 사용
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  userRole: {
    fontSize: 14,
    color: '#666',
  },
  userStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  statusText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  scheduleCard: {
    backgroundColor: 'white',
    margin: 20,
    padding: 20,
    borderRadius: 10,
    elevation: 3,
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  scheduleText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    paddingVertical: 10,
  },
  statsCard: {
    backgroundColor: 'white',
    margin: 20,
    padding: 20,
    borderRadius: 10,
    elevation: 3,
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 5,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
  },
  actionsCard: {
    backgroundColor: 'white',
    margin: 20,
    padding: 20,
    borderRadius: 10,
    elevation: 3,
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  actionButton: {
    flex: 1,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 5,
  },
  primaryButton: {
    backgroundColor: '#4CAF50',
  },
  secondaryButton: {
    backgroundColor: '#2196F3',
  },
  warningButton: {
    backgroundColor: '#FF9800',
  },
  infoButton: {
    backgroundColor: '#9C27B0',
  },
  actionButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  activityCard: {
    backgroundColor: 'white',
    margin: 20,
    padding: 20,
    borderRadius: 10,
    elevation: 3,
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  activityItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  activityText: {
    fontSize: 14,
    color: '#333',
    flex: 1,
  },
  activityTime: {
    fontSize: 12,
    color: '#999',
  },
  refreshButton: {
    backgroundColor: '#2196F3',
    margin: 20,
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  refreshButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
