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
import { Ionicons } from '@expo/vector-icons';

interface DashboardStats {
  totalStores: number;
  activeOrders: number;
  lowStockItems: number;
  todaySales: number;
  pendingTasks: number;
  notifications: number;
}

export default function DashboardScreen() {
  const [stats, setStats] = useState<DashboardStats>({
    totalStores: 0,
    activeOrders: 0,
    lowStockItems: 0,
    todaySales: 0,
    pendingTasks: 0,
    notifications: 0,
  });
  const [refreshing, setRefreshing] = useState(false);

  // 데이터 로드
  const loadDashboardData = async () => {
    try {
      // 실제 API 호출로 대체
      const mockData: DashboardStats = {
        totalStores: 12,
        activeOrders: 8,
        lowStockItems: 5,
        todaySales: 1250000,
        pendingTasks: 3,
        notifications: 7,
      };
      setStats(mockData);
    } catch (error) {
      Alert.alert('오류', '데이터를 불러오는데 실패했습니다.');
    }
  };

  // 새로고침
  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  // 통계 카드 컴포넌트
  const StatCard = ({ title, value, icon, color, onPress }: any) => (
    <TouchableOpacity style={[styles.statCard, { borderLeftColor: color }]} onPress={onPress}>
      <View style={styles.statContent}>
        <View style={[styles.iconContainer, { backgroundColor: color }]}>
          <Ionicons name={icon} size={24} color="white" />
        </View>
        <View style={styles.statText}>
          <Text style={styles.statValue}>{value}</Text>
          <Text style={styles.statTitle}>{title}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  // 빠른 액션 컴포넌트
  const QuickAction = ({ title, icon, onPress }: any) => (
    <TouchableOpacity style={styles.quickAction} onPress={onPress}>
      <View style={styles.quickActionIcon}>
        <Ionicons name={icon} size={28} color="#3b82f6" />
      </View>
      <Text style={styles.quickActionText}>{title}</Text>
    </TouchableOpacity>
  );

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* 헤더 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>대시보드</Text>
        <Text style={styles.headerSubtitle}>오늘의 현황을 확인하세요</Text>
      </View>

      {/* 통계 카드 */}
      <View style={styles.statsContainer}>
        <StatCard
          title="총 매장"
          value={stats.totalStores}
          icon="business"
          color="#3b82f6"
          onPress={() => Alert.alert('매장 관리', '매장 관리 화면으로 이동')}
        />
        <StatCard
          title="진행중 주문"
          value={stats.activeOrders}
          icon="cart"
          color="#10b981"
          onPress={() => Alert.alert('주문 관리', '주문 관리 화면으로 이동')}
        />
        <StatCard
          title="재고 부족"
          value={stats.lowStockItems}
          icon="warning"
          color="#f59e0b"
          onPress={() => Alert.alert('재고 관리', '재고 관리 화면으로 이동')}
        />
        <StatCard
          title="오늘 매출"
          value={`₩${stats.todaySales.toLocaleString()}`}
          icon="trending-up"
          color="#8b5cf6"
          onPress={() => Alert.alert('매출 분석', '매출 분석 화면으로 이동')}
        />
      </View>

      {/* 빠른 액션 */}
      <View style={styles.quickActionsContainer}>
        <Text style={styles.sectionTitle}>빠른 액션</Text>
        <View style={styles.quickActionsGrid}>
          <QuickAction
            title="새 주문"
            icon="add-circle"
            onPress={() => Alert.alert('새 주문', '새 주문 생성')}
          />
          <QuickAction
            title="재고 확인"
            icon="cube"
            onPress={() => Alert.alert('재고 확인', '재고 현황 확인')}
          />
          <QuickAction
            title="스케줄"
            icon="calendar"
            onPress={() => Alert.alert('스케줄', '스케줄 관리')}
          />
          <QuickAction
            title="알림"
            icon="notifications"
            onPress={() => Alert.alert('알림', '알림 확인')}
          />
        </View>
      </View>

      {/* 최근 활동 */}
      <View style={styles.recentActivityContainer}>
        <Text style={styles.sectionTitle}>최근 활동</Text>
        <View style={styles.activityList}>
          <View style={styles.activityItem}>
            <View style={[styles.activityIcon, { backgroundColor: '#10b981' }]}>
              <Ionicons name="checkmark" size={16} color="white" />
            </View>
            <View style={styles.activityContent}>
              <Text style={styles.activityTitle}>주문 #1234 완료</Text>
              <Text style={styles.activityTime}>5분 전</Text>
            </View>
          </View>
          <View style={styles.activityItem}>
            <View style={[styles.activityIcon, { backgroundColor: '#f59e0b' }]}>
              <Ionicons name="warning" size={16} color="white" />
            </View>
            <View style={styles.activityContent}>
              <Text style={styles.activityTitle}>재고 부족 알림</Text>
              <Text style={styles.activityTime}>15분 전</Text>
            </View>
          </View>
          <View style={styles.activityItem}>
            <View style={[styles.activityIcon, { backgroundColor: '#3b82f6' }]}>
              <Ionicons name="person" size={16} color="white" />
            </View>
            <View style={styles.activityContent}>
              <Text style={styles.activityTitle}>새 직원 등록</Text>
              <Text style={styles.activityTime}>1시간 전</Text>
            </View>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    padding: 20,
    backgroundColor: '#3b82f6',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#e0e7ff',
  },
  statsContainer: {
    padding: 16,
  },
  statCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  statContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  statText: {
    flex: 1,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  statTitle: {
    fontSize: 14,
    color: '#6b7280',
  },
  quickActionsContainer: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 16,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickAction: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    width: '48%',
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  quickActionIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#eff6ff',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  quickActionText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
  },
  recentActivityContainer: {
    padding: 16,
    paddingBottom: 32,
  },
  activityList: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  activityIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  activityContent: {
    flex: 1,
  },
  activityTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 2,
  },
  activityTime: {
    fontSize: 14,
    color: '#6b7280',
  },
}); 