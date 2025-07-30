import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
  Dimensions,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { useNotifications } from '../contexts/NotificationContext';
import { API_BASE_URL } from '../utils/config';

const { width } = Dimensions.get('window');

interface DashboardData {
  totalSales: number;
  totalOrders: number;
  activeUsers: number;
  systemHealth: string;
  recentActivity: Array<{
    id: string;
    type: string;
    message: string;
    timestamp: string;
  }>;
  quickStats: {
    todaySales: number;
    weeklyGrowth: number;
    monthlyGrowth: number;
  };
}

const DashboardScreen: React.FC = () => {
  const { theme } = useTheme();
  const { user, token } = useAuth();
  const { unreadCount } = useNotifications();
  
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // 대시보드 데이터 가져오기
  const fetchDashboardData = async () => {
    try {
      if (!token) return;

      const response = await fetch(`${API_BASE_URL}/api/dashboard/mobile`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      } else {
        throw new Error('대시보드 데이터를 가져올 수 없습니다');
      }
    } catch (error) {
      console.error('대시보드 데이터 가져오기 오류:', error);
      Alert.alert('오류', '대시보드 데이터를 불러올 수 없습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // 새로고침
  const onRefresh = async () => {
    setRefreshing(true);
    await fetchDashboardData();
    setRefreshing(false);
  };

  // 초기화
  useEffect(() => {
    fetchDashboardData();
  }, [token]);

  // 로딩 화면
  if (isLoading) {
    return (
      <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
        <View style={styles.loadingContainer}>
          <Icon name="refresh" size={40} color={theme.colors.primary} />
          <Text style={[styles.loadingText, { color: theme.colors.text }]}>
            대시보드 로딩 중...
          </Text>
        </View>
      </View>
    );
  }

  // 통계 카드 컴포넌트
  const StatCard = ({ title, value, icon, color, onPress }: {
    title: string;
    value: string | number;
    icon: string;
    color: string;
    onPress?: () => void;
  }) => (
    <TouchableOpacity
      style={[styles.statCard, { backgroundColor: theme.colors.surface }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={[styles.statIcon, { backgroundColor: color }]}>
        <Icon name={icon} size={24} color="white" />
      </View>
      <View style={styles.statContent}>
        <Text style={[styles.statValue, { color: theme.colors.text }]}>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </Text>
        <Text style={[styles.statTitle, { color: theme.colors.textSecondary }]}>
          {title}
        </Text>
      </View>
    </TouchableOpacity>
  );

  // 시스템 상태 컴포넌트
  const SystemStatusCard = () => {
    if (!dashboardData) return null;

    const getStatusColor = (status: string) => {
      switch (status.toLowerCase()) {
        case 'healthy':
          return theme.colors.success;
        case 'warning':
          return theme.colors.warning;
        case 'error':
          return theme.colors.error;
        default:
          return theme.colors.gray;
      }
    };

    return (
      <View style={[styles.systemStatusCard, { backgroundColor: theme.colors.surface }]}>
        <View style={styles.systemStatusHeader}>
          <Icon name="computer" size={20} color={theme.colors.primary} />
          <Text style={[styles.systemStatusTitle, { color: theme.colors.text }]}>
            시스템 상태
          </Text>
        </View>
        <View style={styles.systemStatusContent}>
          <View style={[styles.statusIndicator, { backgroundColor: getStatusColor(dashboardData.systemHealth) }]} />
          <Text style={[styles.systemStatusText, { color: theme.colors.text }]}>
            {dashboardData.systemHealth}
          </Text>
        </View>
      </View>
    );
  };

  // 최근 활동 컴포넌트
  const RecentActivityCard = () => {
    if (!dashboardData?.recentActivity) return null;

    return (
      <View style={[styles.recentActivityCard, { backgroundColor: theme.colors.surface }]}>
        <View style={styles.recentActivityHeader}>
          <Icon name="history" size={20} color={theme.colors.primary} />
          <Text style={[styles.recentActivityTitle, { color: theme.colors.text }]}>
            최근 활동
          </Text>
        </View>
        <View style={styles.recentActivityList}>
          {dashboardData.recentActivity.slice(0, 5).map((activity, index) => (
            <View key={activity.id} style={styles.activityItem}>
              <View style={[styles.activityIcon, { backgroundColor: theme.colors.primary }]}>
                <Icon name="fiber-manual-record" size={8} color="white" />
              </View>
              <View style={styles.activityContent}>
                <Text style={[styles.activityMessage, { color: theme.colors.text }]}>
                  {activity.message}
                </Text>
                <Text style={[styles.activityTime, { color: theme.colors.textSecondary }]}>
                  {new Date(activity.timestamp).toLocaleString()}
                </Text>
              </View>
            </View>
          ))}
        </View>
      </View>
    );
  };

  // 빠른 액션 컴포넌트
  const QuickActionsCard = () => (
    <View style={[styles.quickActionsCard, { backgroundColor: theme.colors.surface }]}>
      <Text style={[styles.quickActionsTitle, { color: theme.colors.text }]}>
        빠른 액션
      </Text>
      <View style={styles.quickActionsGrid}>
        <TouchableOpacity style={styles.quickActionButton}>
          <Icon name="add" size={24} color={theme.colors.primary} />
          <Text style={[styles.quickActionText, { color: theme.colors.text }]}>
            새 주문
          </Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.quickActionButton}>
          <Icon name="analytics" size={24} color={theme.colors.primary} />
          <Text style={[styles.quickActionText, { color: theme.colors.text }]}>
            분석
          </Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.quickActionButton}>
          <Icon name="notifications" size={24} color={theme.colors.primary} />
          <Text style={[styles.quickActionText, { color: theme.colors.text }]}>
            알림
          </Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.quickActionButton}>
          <Icon name="settings" size={24} color={theme.colors.primary} />
          <Text style={[styles.quickActionText, { color: theme.colors.text }]}>
            설정
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: theme.colors.background }]}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
      showsVerticalScrollIndicator={false}
    >
      {/* 환영 메시지 */}
      <View style={styles.welcomeSection}>
        <Text style={[styles.welcomeText, { color: theme.colors.text }]}>
          안녕하세요, {user?.name}님!
        </Text>
        <Text style={[styles.welcomeSubtext, { color: theme.colors.textSecondary }]}>
          오늘도 좋은 하루 되세요.
        </Text>
      </View>

      {/* 통계 카드들 */}
      {dashboardData && (
        <View style={styles.statsGrid}>
          <StatCard
            title="총 매출"
            value={dashboardData.totalSales}
            icon="attach-money"
            color={theme.colors.success}
          />
          <StatCard
            title="총 주문"
            value={dashboardData.totalOrders}
            icon="shopping-cart"
            color={theme.colors.primary}
          />
          <StatCard
            title="활성 사용자"
            value={dashboardData.activeUsers}
            icon="people"
            color={theme.colors.secondary}
          />
          <StatCard
            title="읽지 않은 알림"
            value={unreadCount}
            icon="notifications"
            color={theme.colors.warning}
          />
        </View>
      )}

      {/* 성장률 카드 */}
      {dashboardData?.quickStats && (
        <View style={[styles.growthCard, { backgroundColor: theme.colors.surface }]}>
          <Text style={[styles.growthTitle, { color: theme.colors.text }]}>
            성장률
          </Text>
          <View style={styles.growthStats}>
            <View style={styles.growthItem}>
              <Text style={[styles.growthLabel, { color: theme.colors.textSecondary }]}>
                오늘 매출
              </Text>
              <Text style={[styles.growthValue, { color: theme.colors.success }]}>
                +{dashboardData.quickStats.todaySales.toLocaleString()}원
              </Text>
            </View>
            <View style={styles.growthItem}>
              <Text style={[styles.growthLabel, { color: theme.colors.textSecondary }]}>
                주간 성장
              </Text>
              <Text style={[styles.growthValue, { color: theme.colors.primary }]}>
                +{dashboardData.quickStats.weeklyGrowth}%
              </Text>
            </View>
            <View style={styles.growthItem}>
              <Text style={[styles.growthLabel, { color: theme.colors.textSecondary }]}>
                월간 성장
              </Text>
              <Text style={[styles.growthValue, { color: theme.colors.secondary }]}>
                +{dashboardData.quickStats.monthlyGrowth}%
              </Text>
            </View>
          </View>
        </View>
      )}

      {/* 시스템 상태 */}
      <SystemStatusCard />

      {/* 빠른 액션 */}
      <QuickActionsCard />

      {/* 최근 활동 */}
      <RecentActivityCard />

      {/* 하단 여백 */}
      <View style={styles.bottomSpacing} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    fontWeight: '600',
  },
  welcomeSection: {
    padding: 20,
    paddingBottom: 10,
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  welcomeSubtext: {
    fontSize: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 10,
    marginBottom: 20,
  },
  statCard: {
    width: (width - 40) / 2,
    margin: 5,
    padding: 16,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  statIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  statContent: {
    flex: 1,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  statTitle: {
    fontSize: 14,
  },
  growthCard: {
    margin: 15,
    padding: 20,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  growthTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  growthStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  growthItem: {
    alignItems: 'center',
    flex: 1,
  },
  growthLabel: {
    fontSize: 12,
    marginBottom: 4,
  },
  growthValue: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  systemStatusCard: {
    margin: 15,
    padding: 20,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  systemStatusHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  systemStatusTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  systemStatusContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  systemStatusText: {
    fontSize: 16,
    fontWeight: '600',
  },
  quickActionsCard: {
    margin: 15,
    padding: 20,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  quickActionsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  quickActionButton: {
    width: (width - 70) / 4,
    alignItems: 'center',
    paddingVertical: 16,
  },
  quickActionText: {
    fontSize: 12,
    marginTop: 8,
    textAlign: 'center',
  },
  recentActivityCard: {
    margin: 15,
    padding: 20,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  recentActivityHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  recentActivityTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  recentActivityList: {
    gap: 12,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  activityIcon: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginTop: 6,
    marginRight: 12,
  },
  activityContent: {
    flex: 1,
  },
  activityMessage: {
    fontSize: 14,
    marginBottom: 4,
  },
  activityTime: {
    fontSize: 12,
  },
  bottomSpacing: {
    height: 20,
  },
});

export default DashboardScreen; 