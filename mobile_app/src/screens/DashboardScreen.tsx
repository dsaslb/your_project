import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  ScrollView, 
  TouchableOpacity, 
  Alert,
  RefreshControl,
  Dimensions
} from 'react-native';
import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';
import { useAuth } from '../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';

interface SystemHealth {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  status: string;
  last_check: string;
}

interface AIInsight {
  type: string;
  title: string;
  description: string;
  priority: string;
  trend: string;
  change_percent: number;
}

interface PredictionAlert {
  type: string;
  title: string;
  description: string;
  severity: string;
  action_required: boolean;
}

interface SatisfactionMetrics {
  employee_satisfaction: number;
  customer_satisfaction: number;
  health_score: number;
  stress_level: number;
  trend: string;
}

const { width } = Dimensions.get('window');

const DashboardScreen: React.FC = () => {
  const { user } = useAuth();
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [aiInsights, setAiInsights] = useState<AIInsight[]>([]);
  const [alerts, setAlerts] = useState<PredictionAlert[]>([]);
  const [satisfactionMetrics, setSatisfactionMetrics] = useState<SatisfactionMetrics | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  // 데이터 로드 함수
  const loadDashboardData = async () => {
    try {
      setRefreshing(true);
      
      // 시스템 건강 상태
      const healthResponse = await fetch('/api/system/health');
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        setSystemHealth(healthData);
      }
      
      // AI 인사이트
      const insightsResponse = await fetch('/api/ai/prediction/insights');
      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json();
        setAiInsights(insightsData.insights.slice(0, 3)); // 상위 3개만
      }
      
      // 알림
      const alertsResponse = await fetch('/api/ai/prediction/alerts');
      if (alertsResponse.ok) {
        const alertsData = await alertsResponse.json();
        setAlerts(alertsData.alerts.slice(0, 5)); // 상위 5개만
      }
      
      // 만족도 메트릭
      const satisfactionResponse = await fetch('/api/satisfaction/ai-analysis');
      if (satisfactionResponse.ok) {
        const satisfactionData = await satisfactionResponse.json();
        setSatisfactionMetrics(satisfactionData);
      }
      
    } catch (error) {
      console.error('대시보드 데이터 로드 실패:', error);
      Alert.alert('오류', '데이터를 불러오는데 실패했습니다.');
    } finally {
      setRefreshing(false);
    }
  };

  // 시스템 복구 실행
  const executeSystemRecovery = async (recoveryType: string) => {
    try {
      const response = await fetch('/api/system/recovery', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ recovery_type: recoveryType }),
      });
      
      if (response.ok) {
        Alert.alert('성공', `${recoveryType} 복구가 실행되었습니다.`);
        await loadDashboardData();
      } else {
        Alert.alert('오류', '시스템 복구에 실패했습니다.');
      }
    } catch (error) {
      console.error('시스템 복구 실패:', error);
      Alert.alert('오류', '시스템 복구 중 오류가 발생했습니다.');
    }
  };

  // 초기 로드 및 주기적 업데이트
  useEffect(() => {
    loadDashboardData();
    
    // 3분마다 자동 새로고침
    const interval = setInterval(loadDashboardData, 3 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  // 우선순위별 색상
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#EF4444';
      case 'medium': return '#F59E0B';
      case 'low': return '#10B981';
      default: return '#6B7280';
    }
  };

  // 심각도별 색상
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#EF4444';
      case 'high': return '#F97316';
      case 'medium': return '#F59E0B';
      case 'low': return '#10B981';
      default: return '#6B7280';
    }
  };

  // 시스템 상태 색상
  const getSystemStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return '#10B981';
      case 'warning': return '#F59E0B';
      case 'critical': return '#EF4444';
      default: return '#6B7280';
    }
  };

  // 차트 데이터
  const chartData = {
    labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
    datasets: [
      {
        data: [45, 35, 65, 80, 75, 60],
        color: (opacity = 1) => `rgba(59, 130, 246, ${opacity})`,
        strokeWidth: 2,
      },
    ],
  };

  const barData = {
    labels: ['CPU', '메모리', '디스크'],
    datasets: [
      {
        data: [
          systemHealth?.cpu_usage || 0,
          systemHealth?.memory_usage || 0,
          systemHealth?.disk_usage || 0,
        ],
      },
    ],
  };

  const pieData = [
    {
      name: '만족',
      population: satisfactionMetrics?.employee_satisfaction || 0,
      color: '#10B981',
      legendFontColor: '#7F7F7F',
    },
    {
      name: '보통',
      population: 100 - (satisfactionMetrics?.employee_satisfaction || 0),
      color: '#F59E0B',
      legendFontColor: '#7F7F7F',
    },
  ];

  const chartConfig = {
    backgroundColor: '#ffffff',
    backgroundGradientFrom: '#ffffff',
    backgroundGradientTo: '#ffffff',
    decimalPlaces: 1,
    color: (opacity = 1) => `rgba(59, 130, 246, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '6',
      strokeWidth: '2',
      stroke: '#3B82F6',
    },
  };

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={loadDashboardData} />
      }
    >
      {/* 헤더 */}
      <View style={styles.header}>
        <Text style={styles.title}>AI 대시보드</Text>
        <Text style={styles.subtitle}>안녕하세요, {user?.name}님!</Text>
        <Text style={styles.statusText}>
          시스템 상태: 
          <Text style={{ color: getSystemStatusColor(systemHealth?.status || 'unknown') }}>
            {' '}{systemHealth?.status?.toUpperCase() || 'UNKNOWN'}
          </Text>
        </Text>
      </View>
      
      {/* 탭 네비게이션 */}
      <View style={styles.tabContainer}>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'overview' && styles.activeTab]}
          onPress={() => setActiveTab('overview')}
        >
          <Text style={[styles.tabText, activeTab === 'overview' && styles.activeTabText]}>
            개요
          </Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'system' && styles.activeTab]}
          onPress={() => setActiveTab('system')}
        >
          <Text style={[styles.tabText, activeTab === 'system' && styles.activeTabText]}>
            시스템
          </Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'alerts' && styles.activeTab]}
          onPress={() => setActiveTab('alerts')}
        >
          <Text style={[styles.tabText, activeTab === 'alerts' && styles.activeTabText]}>
            알림
          </Text>
        </TouchableOpacity>
      </View>

      {/* 개요 탭 */}
      {activeTab === 'overview' && (
        <View style={styles.content}>
          {/* 시스템 상태 카드 */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>시스템 상태</Text>
            <View style={styles.metricsContainer}>
              <View style={styles.metric}>
                <Text style={styles.metricLabel}>CPU</Text>
                <Text style={styles.metricValue}>{systemHealth?.cpu_usage?.toFixed(1)}%</Text>
                <View style={[styles.progressBar, { width: `${systemHealth?.cpu_usage || 0}%` }]} />
              </View>
              <View style={styles.metric}>
                <Text style={styles.metricLabel}>메모리</Text>
                <Text style={styles.metricValue}>{systemHealth?.memory_usage?.toFixed(1)}%</Text>
                <View style={[styles.progressBar, { width: `${systemHealth?.memory_usage || 0}%` }]} />
              </View>
              <View style={styles.metric}>
                <Text style={styles.metricLabel}>디스크</Text>
                <Text style={styles.metricValue}>{systemHealth?.disk_usage?.toFixed(1)}%</Text>
                <View style={[styles.progressBar, { width: `${systemHealth?.disk_usage || 0}%` }]} />
              </View>
            </View>
          </View>

          {/* AI 인사이트 */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>AI 인사이트</Text>
            {aiInsights.map((insight, index) => (
              <View key={index} style={styles.insightItem}>
                <View style={styles.insightHeader}>
                  <Text style={styles.insightTitle}>{insight.title}</Text>
                  <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(insight.priority) }]}>
                    <Text style={styles.priorityText}>{insight.priority}</Text>
                  </View>
                </View>
                <Text style={styles.insightDescription}>{insight.description}</Text>
                <View style={styles.trendContainer}>
                  <Ionicons 
                    name={insight.trend === 'up' ? 'trending-up' : 'trending-down'} 
                    size={16} 
                    color={insight.trend === 'up' ? '#10B981' : '#EF4444'} 
                  />
                  <Text style={[styles.trendText, { color: insight.trend === 'up' ? '#10B981' : '#EF4444' }]}>
                    {insight.change_percent}%
                  </Text>
                </View>
              </View>
            ))}
          </View>

          {/* 만족도 분석 */}
          {satisfactionMetrics && (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>만족도 분석</Text>
              <View style={styles.satisfactionContainer}>
                <View style={styles.satisfactionMetric}>
                  <Text style={styles.satisfactionLabel}>직원 만족도</Text>
                  <Text style={styles.satisfactionValue}>
                    {satisfactionMetrics.employee_satisfaction?.toFixed(1)}%
                  </Text>
                </View>
                <View style={styles.satisfactionMetric}>
                  <Text style={styles.satisfactionLabel}>고객 만족도</Text>
                  <Text style={styles.satisfactionValue}>
                    {satisfactionMetrics.customer_satisfaction?.toFixed(1)}%
                  </Text>
                </View>
                <View style={styles.satisfactionMetric}>
                  <Text style={styles.satisfactionLabel}>스트레스 수준</Text>
                  <Text style={styles.satisfactionValue}>
                    {satisfactionMetrics.stress_level?.toFixed(1)}/5
                  </Text>
                </View>
              </View>
            </View>
          )}
        </View>
      )}

      {/* 시스템 탭 */}
      {activeTab === 'system' && (
        <View style={styles.content}>
          {/* 시스템 메트릭 차트 */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>시스템 메트릭 트렌드</Text>
            <LineChart
              data={chartData}
              width={width - 60}
              height={220}
              chartConfig={chartConfig}
              bezier
              style={styles.chart}
            />
          </View>

          {/* 시스템 사용률 차트 */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>현재 사용률</Text>
            <BarChart
              data={barData}
              width={width - 60}
              height={220}
              chartConfig={chartConfig}
              style={styles.chart}
            />
          </View>

          {/* 시스템 복구 액션 */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>시스템 복구 액션</Text>
            <TouchableOpacity 
              style={styles.actionButton}
              onPress={() => executeSystemRecovery('memory_cleanup')}
            >
              <Ionicons name="shield-outline" size={20} color="#3B82F6" />
              <Text style={styles.actionButtonText}>메모리 캐시 정리</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.actionButton}
              onPress={() => executeSystemRecovery('disk_cleanup')}
            >
              <Ionicons name="trash-outline" size={20} color="#3B82F6" />
              <Text style={styles.actionButtonText}>디스크 정리</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.actionButton}
              onPress={() => executeSystemRecovery('process_restart')}
            >
              <Ionicons name="refresh-outline" size={20} color="#3B82F6" />
              <Text style={styles.actionButtonText}>프로세스 재시작</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* 알림 탭 */}
      {activeTab === 'alerts' && (
        <View style={styles.content}>
          <Text style={styles.sectionTitle}>실시간 알림 ({alerts.length})</Text>
          {alerts.map((alert, index) => (
            <View key={index} style={[styles.alertCard, { borderLeftColor: getSeverityColor(alert.severity) }]}>
              <View style={styles.alertHeader}>
                <Text style={styles.alertTitle}>{alert.title}</Text>
                <View style={[styles.severityBadge, { backgroundColor: getSeverityColor(alert.severity) }]}>
                  <Text style={styles.severityText}>{alert.severity}</Text>
                </View>
              </View>
              <Text style={styles.alertDescription}>{alert.description}</Text>
              {alert.action_required && (
                <View style={styles.actionRequiredBadge}>
                  <Text style={styles.actionRequiredText}>액션 필요</Text>
                </View>
              )}
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#3B82F6',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  subtitle: {
    fontSize: 16,
    color: '#ffffff',
    marginTop: 5,
  },
  statusText: {
    fontSize: 14,
    color: '#ffffff',
    marginTop: 10,
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    paddingHorizontal: 20,
    paddingVertical: 10,
  },
  tab: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 8,
  },
  activeTab: {
    backgroundColor: '#3B82F6',
  },
  tabText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
  },
  activeTabText: {
    color: '#ffffff',
  },
  content: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333333',
  },
  card: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 10,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 15,
  },
  metricsContainer: {
    spaceY: 10,
  },
  metric: {
    marginBottom: 15,
  },
  metricLabel: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 5,
  },
  metricValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333333',
    marginBottom: 5,
  },
  progressBar: {
    height: 4,
    backgroundColor: '#3B82F6',
    borderRadius: 2,
  },
  insightItem: {
    marginBottom: 15,
    padding: 15,
    backgroundColor: '#F8FAFC',
    borderRadius: 8,
  },
  insightHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  insightTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333333',
    flex: 1,
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  priorityText: {
    fontSize: 12,
    color: '#ffffff',
    fontWeight: '600',
  },
  insightDescription: {
    fontSize: 13,
    color: '#6B7280',
    marginBottom: 8,
  },
  trendContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  trendText: {
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4,
  },
  satisfactionContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  satisfactionMetric: {
    alignItems: 'center',
    flex: 1,
  },
  satisfactionLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 5,
  },
  satisfactionValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#3B82F6',
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#F8FAFC',
    borderRadius: 8,
    marginBottom: 10,
  },
  actionButtonText: {
    fontSize: 14,
    color: '#3B82F6',
    fontWeight: '600',
    marginLeft: 10,
  },
  alertCard: {
    backgroundColor: '#ffffff',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 3,
  },
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  alertTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333333',
    flex: 1,
  },
  severityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  severityText: {
    fontSize: 12,
    color: '#ffffff',
    fontWeight: '600',
  },
  alertDescription: {
    fontSize: 13,
    color: '#6B7280',
    marginBottom: 8,
  },
  actionRequiredBadge: {
    alignSelf: 'flex-start',
    backgroundColor: '#EF4444',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  actionRequiredText: {
    fontSize: 12,
    color: '#ffffff',
    fontWeight: '600',
  },
});

export default DashboardScreen; 