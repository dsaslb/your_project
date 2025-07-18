import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  ScrollView,
  RefreshControl,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';
import { MaterialIcons, MaterialCommunityIcons, Ionicons } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';

const { width } = Dimensions.get('window');

interface DashboardData {
  timestamp: string;
  system_status: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    active_connections: number;
    uptime: string;
    database_status: string;
    api_response_time: number;
  };
  performance_metrics: {
    today_orders: {
      total: number;
      pending: number;
      completed: number;
      total_sales: number;
    };
    today_attendance: {
      total: number;
      on_time: number;
      late: number;
    };
    active_users: number;
  };
  active_alerts: Array<{
    type: string;
    severity: 'info' | 'warning' | 'critical';
    message: string;
    timestamp: string;
  }>;
  user_activity: {
    recent_orders: number;
    recent_logins: number;
    active_sessions: number;
    peak_hours: number[];
  };
  ai_insights: {
    recommendations: Array<{
      type: string;
      title: string;
      description: string;
      priority: string;
      action: string;
    }>;
  };
}

interface MetricCardProps {
  title: string;
  value: number | string;
  unit?: string;
  icon: string;
  color: string;
  onPress?: () => void;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  icon,
  color,
  onPress,
}) => {
  return (
    <TouchableOpacity
      style={[styles.metricCard, { borderLeftColor: color }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.metricHeader}>
        <MaterialIcons name={icon as any} size={24} color={color} />
        <Text style={styles.metricTitle}>{title}</Text>
      </View>
      <View style={styles.metricValue}>
        <Text style={[styles.metricNumber, { color }]}>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </Text>
        {unit && <Text style={styles.metricUnit}>{unit}</Text>}
      </View>
    </TouchableOpacity>
  );
};

interface AlertItemProps {
  alert: {
    type: string;
    severity: 'info' | 'warning' | 'critical';
    message: string;
    timestamp: string;
  };
}

const AlertItem: React.FC<AlertItemProps> = ({ alert }) => {
  const getSeverityColor = () => {
    switch (alert.severity) {
      case 'critical': return '#ef4444';
      case 'warning': return '#f59e0b';
      case 'info': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  const getSeverityIcon = () => {
    switch (alert.severity) {
      case 'critical': return 'error';
      case 'warning': return 'warning';
      case 'info': return 'info';
      default: return 'info';
    }
  };

  return (
    <View style={[styles.alertItem, { borderLeftColor: getSeverityColor() }]}>
      <View style={styles.alertHeader}>
        <MaterialIcons name={getSeverityIcon() as any} size={20} color={getSeverityColor()} />
        <Text style={[styles.alertSeverity, { color: getSeverityColor() }]}>
          {alert.severity.toUpperCase()}
        </Text>
      </View>
      <Text style={styles.alertMessage}>{alert.message}</Text>
      <Text style={styles.alertTime}>
        {new Date(alert.timestamp).toLocaleString()}
      </Text>
    </View>
  );
};

interface ProgressBarProps {
  label: string;
  value: number;
  max: number;
  color: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ label, value, max, color }) => {
  const percentage = max > 0 ? (value / max) * 100 : 0;

  return (
    <View style={styles.progressContainer}>
      <View style={styles.progressHeader}>
        <Text style={styles.progressLabel}>{label}</Text>
        <Text style={styles.progressValue}>{percentage.toFixed(1)}%</Text>
      </View>
      <View style={styles.progressBar}>
        <View
          style={[
            styles.progressFill,
            { width: `${percentage}%`, backgroundColor: color },
          ]}
        />
      </View>
    </View>
  );
};

const IntegratedDashboardScreen: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const [error, setError] = useState<string>('');
  const { token } = useAuth();
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    fetchDashboardData();
    setupSSEConnection();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/dashboard/integrated', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('대시보드 데이터를 불러올 수 없습니다.');
      }

      const data = await response.json();
      if (data.success) {
        setDashboardData(data.data);
        setLastUpdate(new Date().toLocaleString());
        setError('');
      } else {
        setError(data.error || '데이터 로드 실패');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류');
    } finally {
      setIsLoading(false);
    }
  };

  const setupSSEConnection = () => {
    try {
      const eventSource = new EventSource('/api/dashboard/stream', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      eventSource.onopen = () => {
        setIsConnected(true);
        setError('');
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'dashboard_update') {
            setDashboardData(data.data);
            setLastUpdate(new Date().toLocaleString());
          } else if (data.type === 'heartbeat') {
            setIsConnected(true);
          }
        } catch (err) {
          console.error('SSE 데이터 파싱 오류:', err);
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE 연결 오류:', error);
        setIsConnected(false);
        setError('실시간 연결이 끊어졌습니다.');
        
        setTimeout(() => {
          if (eventSourceRef.current) {
            eventSourceRef.current.close();
          }
          setupSSEConnection();
        }, 5000);
      };

      eventSourceRef.current = eventSource;
    } catch (err) {
      setError('실시간 연결을 설정할 수 없습니다.');
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchDashboardData();
    setRefreshing(false);
  };

  const handleMetricPress = (metric: string) => {
    Alert.alert('상세 정보', `${metric}에 대한 상세 정보를 확인할 수 있습니다.`);
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#3b82f6" />
          <Text style={styles.loadingText}>대시보드 데이터를 불러오는 중...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (error) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <MaterialIcons name="error" size={48} color="#ef4444" />
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={fetchDashboardData}>
            <Text style={styles.retryButtonText}>다시 시도</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  if (!dashboardData) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>데이터를 불러올 수 없습니다.</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* 헤더 */}
        <View style={styles.header}>
          <View>
            <Text style={styles.title}>통합 대시보드</Text>
            <Text style={styles.subtitle}>
              마지막 업데이트: {lastUpdate}
            </Text>
          </View>
          <View style={styles.connectionStatus}>
            <View
              style={[
                styles.connectionDot,
                { backgroundColor: isConnected ? '#10b981' : '#ef4444' },
              ]}
            />
            <Text style={styles.connectionText}>
              {isConnected ? '실시간' : '오프라인'}
            </Text>
          </View>
        </View>

        {/* 성과 메트릭 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>오늘의 성과</Text>
          <View style={styles.metricsGrid}>
            <MetricCard
              title="총 주문"
              value={dashboardData.performance_metrics.today_orders.total}
              icon="shopping-cart"
              color="#3b82f6"
              onPress={() => handleMetricPress('총 주문')}
            />
            <MetricCard
              title="대기 주문"
              value={dashboardData.performance_metrics.today_orders.pending}
              icon="schedule"
              color="#f59e0b"
              onPress={() => handleMetricPress('대기 주문')}
            />
            <MetricCard
              title="완료 주문"
              value={dashboardData.performance_metrics.today_orders.completed}
              icon="check-circle"
              color="#10b981"
              onPress={() => handleMetricPress('완료 주문')}
            />
            <MetricCard
              title="총 매출"
              value={dashboardData.performance_metrics.today_orders.total_sales}
              unit="원"
              icon="trending-up"
              color="#8b5cf6"
              onPress={() => handleMetricPress('총 매출')}
            />
          </View>
        </View>

        {/* 시스템 상태 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>시스템 상태</Text>
          <View style={styles.systemMetrics}>
            <MetricCard
              title="CPU 사용률"
              value={dashboardData.system_status.cpu_usage}
              unit="%"
              icon="memory"
              color="#ef4444"
            />
            <MetricCard
              title="메모리 사용률"
              value={dashboardData.system_status.memory_usage}
              unit="%"
              icon="storage"
              color="#f59e0b"
            />
            <MetricCard
              title="디스크 사용률"
              value={dashboardData.system_status.disk_usage}
              unit="%"
              icon="hard-drive"
              color="#3b82f6"
            />
            <MetricCard
              title="응답 시간"
              value={dashboardData.system_status.api_response_time}
              unit="ms"
              icon="speed"
              color="#10b981"
            />
          </View>
        </View>

        {/* 성과 차트 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>성과 분석</Text>
          <View style={styles.chartContainer}>
            <View style={styles.progressSection}>
              <ProgressBar
                label="주문 완료율"
                value={dashboardData.performance_metrics.today_orders.completed}
                max={dashboardData.performance_metrics.today_orders.total}
                color="#10b981"
              />
              <ProgressBar
                label="정시 출근율"
                value={dashboardData.performance_metrics.today_attendance.on_time}
                max={dashboardData.performance_metrics.today_attendance.total}
                color="#3b82f6"
              />
            </View>
          </View>
        </View>

        {/* 사용자 활동 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>사용자 활동</Text>
          <View style={styles.activityGrid}>
            <MetricCard
              title="최근 주문"
              value={dashboardData.user_activity.recent_orders}
              icon="receipt"
              color="#8b5cf6"
            />
            <MetricCard
              title="최근 로그인"
              value={dashboardData.user_activity.recent_logins}
              icon="login"
              color="#06b6d4"
            />
            <MetricCard
              title="활성 세션"
              value={dashboardData.user_activity.active_sessions}
              icon="people"
              color="#f59e0b"
            />
            <MetricCard
              title="피크 시간"
              value={dashboardData.user_activity.peak_hours[0] || 0}
              unit="시"
              icon="schedule"
              color="#ef4444"
            />
          </View>
        </View>

        {/* AI 인사이트 */}
        {dashboardData.ai_insights.recommendations && dashboardData.ai_insights.recommendations.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>AI 인사이트</Text>
            <View style={styles.insightsContainer}>
              {dashboardData.ai_insights.recommendations.slice(0, 3).map((insight, index) => (
                <View key={index} style={styles.insightItem}>
                  <View style={styles.insightHeader}>
                    <MaterialIcons name="lightbulb" size={20} color="#f59e0b" />
                    <Text style={styles.insightTitle}>{insight.title}</Text>
                  </View>
                  <Text style={styles.insightDescription}>{insight.description}</Text>
                  <View style={styles.insightPriority}>
                    <Text style={styles.priorityText}>{insight.priority}</Text>
                  </View>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* 알림 */}
        {dashboardData.active_alerts.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>활성 알림 ({dashboardData.active_alerts.length})</Text>
            <View style={styles.alertsContainer}>
              {dashboardData.active_alerts.slice(0, 5).map((alert, index) => (
                <AlertItem key={index} alert={alert} />
              ))}
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1e293b',
  },
  subtitle: {
    fontSize: 14,
    color: '#64748b',
    marginTop: 4,
  },
  connectionStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  connectionDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  connectionText: {
    fontSize: 12,
    color: '#64748b',
  },
  section: {
    margin: 16,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 16,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metricCard: {
    width: (width - 64) / 2 - 8,
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  metricHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  metricTitle: {
    fontSize: 12,
    color: '#64748b',
    marginLeft: 8,
    flex: 1,
  },
  metricValue: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  metricNumber: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  metricUnit: {
    fontSize: 12,
    color: '#64748b',
    marginLeft: 4,
  },
  systemMetrics: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  chartContainer: {
    marginTop: 8,
  },
  progressSection: {
    gap: 16,
  },
  progressContainer: {
    marginBottom: 12,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  progressLabel: {
    fontSize: 14,
    color: '#374151',
  },
  progressValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e293b',
  },
  progressBar: {
    height: 8,
    backgroundColor: '#e5e7eb',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 4,
  },
  activityGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  insightsContainer: {
    gap: 12,
  },
  insightItem: {
    backgroundColor: '#fef3c7',
    borderRadius: 8,
    padding: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#f59e0b',
  },
  insightHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  insightTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#92400e',
    marginLeft: 8,
    flex: 1,
  },
  insightDescription: {
    fontSize: 12,
    color: '#92400e',
    lineHeight: 16,
  },
  insightPriority: {
    marginTop: 8,
  },
  priorityText: {
    fontSize: 10,
    color: '#92400e',
    backgroundColor: '#fbbf24',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    alignSelf: 'flex-start',
  },
  alertsContainer: {
    gap: 12,
  },
  alertItem: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 12,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  alertHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  alertSeverity: {
    fontSize: 10,
    fontWeight: '600',
    marginLeft: 8,
  },
  alertMessage: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
  },
  alertTime: {
    fontSize: 12,
    color: '#9ca3af',
    marginTop: 8,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#64748b',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  errorText: {
    fontSize: 16,
    color: '#64748b',
    textAlign: 'center',
    marginTop: 16,
  },
  retryButton: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    marginTop: 16,
  },
  retryButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default IntegratedDashboardScreen; 