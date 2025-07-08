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
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useAuth } from '../../contexts/AuthContext';
import { apiClient } from '../../services/apiClient';

interface DashboardStats {
  totalOrders: number;
  pendingOrders: number;
  completedOrders: number;
  totalRevenue: number;
  activeStaff: number;
  todayAttendance: number;
}

interface QuickAction {
  id: string;
  title: string;
  icon: string;
  color: string;
  onPress: () => void;
}

const DashboardScreen: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get('/api/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      // 더미 데이터로 대체
      setStats({
        totalOrders: 45,
        pendingOrders: 8,
        completedOrders: 37,
        totalRevenue: 1250000,
        activeStaff: 12,
        todayAttendance: 15,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const getQuickActions = (): QuickAction[] => {
    const baseActions: QuickAction[] = [
      {
        id: 'attendance',
        title: '출근 체크',
        icon: 'person-add',
        color: '#10b981',
        onPress: () => Alert.alert('출근 체크', '출근 체크 기능'),
      },
      {
        id: 'orders',
        title: '주문 확인',
        icon: 'shopping-cart',
        color: '#3b82f6',
        onPress: () => Alert.alert('주문 확인', '주문 확인 기능'),
      },
      {
        id: 'schedule',
        title: '근무 일정',
        icon: 'schedule',
        color: '#f59e0b',
        onPress: () => Alert.alert('근무 일정', '근무 일정 확인'),
      },
      {
        id: 'notifications',
        title: '알림',
        icon: 'notifications',
        color: '#ef4444',
        onPress: () => Alert.alert('알림', '알림 확인'),
      },
    ];

    // 관리자 전용 액션 추가
    if (user?.role === 'admin' || user?.role === 'manager') {
      baseActions.push(
        {
          id: 'staff',
          title: '직원 관리',
          icon: 'people',
          color: '#8b5cf6',
          onPress: () => Alert.alert('직원 관리', '직원 관리 기능'),
        },
        {
          id: 'inventory',
          title: '재고 관리',
          icon: 'inventory',
          color: '#06b6d4',
          onPress: () => Alert.alert('재고 관리', '재고 관리 기능'),
        }
      );
    }

    return baseActions;
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
    }).format(amount);
  };

  const StatCard: React.FC<{ title: string; value: string | number; icon: string; color: string }> = ({
    title,
    value,
    icon,
    color,
  }) => (
    <View style={[styles.statCard, { borderLeftColor: color }]}>
      <View style={styles.statHeader}>
        <Icon name={icon} size={24} color={color} />
        <Text style={styles.statTitle}>{title}</Text>
      </View>
      <Text style={styles.statValue}>{value}</Text>
    </View>
  );

  const QuickActionButton: React.FC<{ action: QuickAction }> = ({ action }) => (
    <TouchableOpacity
      style={[styles.quickActionButton, { backgroundColor: action.color }]}
      onPress={action.onPress}
    >
      <Icon name={action.icon} size={32} color="#ffffff" />
      <Text style={styles.quickActionText}>{action.title}</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>안녕하세요!</Text>
            <Text style={styles.userName}>{user?.name}님</Text>
          </View>
          <View style={styles.headerActions}>
            <TouchableOpacity style={styles.headerButton}>
              <Icon name="notifications" size={24} color="#6b7280" />
            </TouchableOpacity>
            <TouchableOpacity style={styles.headerButton}>
              <Icon name="settings" size={24} color="#6b7280" />
            </TouchableOpacity>
          </View>
        </View>

        {/* Stats Grid */}
        {stats && (
          <View style={styles.statsContainer}>
            <Text style={styles.sectionTitle}>오늘의 통계</Text>
            <View style={styles.statsGrid}>
              <StatCard
                title="총 주문"
                value={stats.totalOrders}
                icon="shopping-cart"
                color="#3b82f6"
              />
              <StatCard
                title="대기 주문"
                value={stats.pendingOrders}
                icon="pending"
                color="#f59e0b"
              />
              <StatCard
                title="완료 주문"
                value={stats.completedOrders}
                icon="check-circle"
                color="#10b981"
              />
              <StatCard
                title="총 매출"
                value={formatCurrency(stats.totalRevenue)}
                icon="attach-money"
                color="#8b5cf6"
              />
              <StatCard
                title="출근 직원"
                value={stats.activeStaff}
                icon="people"
                color="#06b6d4"
              />
              <StatCard
                title="오늘 출근"
                value={stats.todayAttendance}
                icon="person-add"
                color="#ef4444"
              />
            </View>
          </View>
        )}

        {/* Quick Actions */}
        <View style={styles.quickActionsContainer}>
          <Text style={styles.sectionTitle}>빠른 액션</Text>
          <View style={styles.quickActionsGrid}>
            {getQuickActions().map((action) => (
              <QuickActionButton key={action.id} action={action} />
            ))}
          </View>
        </View>

        {/* Recent Activity */}
        <View style={styles.recentActivityContainer}>
          <Text style={styles.sectionTitle}>최근 활동</Text>
          <View style={styles.activityList}>
            <View style={styles.activityItem}>
              <Icon name="shopping-cart" size={20} color="#3b82f6" />
              <View style={styles.activityContent}>
                <Text style={styles.activityTitle}>새 주문 접수</Text>
                <Text style={styles.activityTime}>2분 전</Text>
              </View>
            </View>
            <View style={styles.activityItem}>
              <Icon name="person-add" size={20} color="#10b981" />
              <View style={styles.activityContent}>
                <Text style={styles.activityTitle}>김철수 출근</Text>
                <Text style={styles.activityTime}>5분 전</Text>
              </View>
            </View>
            <View style={styles.activityItem}>
              <Icon name="check-circle" size={20} color="#10b981" />
              <View style={styles.activityContent}>
                <Text style={styles.activityTitle}>주문 #1234 완료</Text>
                <Text style={styles.activityTime}>10분 전</Text>
              </View>
            </View>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: '#ffffff',
  },
  greeting: {
    fontSize: 16,
    color: '#6b7280',
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  headerActions: {
    flexDirection: 'row',
  },
  headerButton: {
    padding: 8,
    marginLeft: 8,
  },
  statsContainer: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    width: '48%',
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  statHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  statTitle: {
    fontSize: 14,
    color: '#6b7280',
    marginLeft: 8,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  quickActionsContainer: {
    padding: 20,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickActionButton: {
    width: '48%',
    height: 100,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  quickActionText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
    marginTop: 8,
  },
  recentActivityContainer: {
    padding: 20,
  },
  activityList: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  activityContent: {
    marginLeft: 12,
    flex: 1,
  },
  activityTitle: {
    fontSize: 16,
    color: '#1f2937',
    fontWeight: '500',
  },
  activityTime: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 2,
  },
});

export default DashboardScreen; 