import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Schedule {
  id: number;
  employeeName: string;
  date: string;
  startTime: string;
  endTime: string;
  position: string;
  status: 'scheduled' | 'working' | 'completed' | 'absent';
}

export default function ScheduleScreen() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadSchedules = async () => {
    try {
      const mockSchedules: Schedule[] = [
        {
          id: 1,
          employeeName: '김직원',
          date: '2024-01-15',
          startTime: '09:00',
          endTime: '17:00',
          position: '바리스타',
          status: 'working',
        },
        {
          id: 2,
          employeeName: '이직원',
          date: '2024-01-15',
          startTime: '13:00',
          endTime: '21:00',
          position: '서버',
          status: 'scheduled',
        },
        {
          id: 3,
          employeeName: '박직원',
          date: '2024-01-15',
          startTime: '08:00',
          endTime: '16:00',
          position: '매니저',
          status: 'completed',
        },
      ];
      setSchedules(mockSchedules);
    } catch (error) {
      Alert.alert('오류', '스케줄 데이터를 불러오는데 실패했습니다.');
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadSchedules();
    setRefreshing(false);
  };

  useEffect(() => {
    loadSchedules();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled': return '#3b82f6';
      case 'working': return '#10b981';
      case 'completed': return '#6b7280';
      case 'absent': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'scheduled': return '예정';
      case 'working': return '근무중';
      case 'completed': return '완료';
      case 'absent': return '결근';
      default: return '알 수 없음';
    }
  };

  const ScheduleCard = ({ schedule }: { schedule: Schedule }) => (
    <TouchableOpacity 
      style={[styles.scheduleCard, { borderLeftColor: getStatusColor(schedule.status) }]}
      onPress={() => Alert.alert('스케줄 상세', `${schedule.employeeName} 스케줄 상세`)}
    >
      <View style={styles.scheduleHeader}>
        <Text style={styles.employeeName}>{schedule.employeeName}</Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(schedule.status) }]}>
          <Text style={styles.statusText}>{getStatusText(schedule.status)}</Text>
        </View>
      </View>

      <View style={styles.scheduleDetails}>
        <View style={styles.detailRow}>
          <Ionicons name="calendar" size={16} color="#6b7280" />
          <Text style={styles.detailText}>{schedule.date}</Text>
        </View>
        <View style={styles.detailRow}>
          <Ionicons name="time" size={16} color="#6b7280" />
          <Text style={styles.detailText}>{schedule.startTime} - {schedule.endTime}</Text>
        </View>
        <View style={styles.detailRow}>
          <Ionicons name="person" size={16} color="#6b7280" />
          <Text style={styles.detailText}>{schedule.position}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>스케줄</Text>
        <TouchableOpacity 
          style={styles.addButton}
          onPress={() => Alert.alert('새 스케줄', '새 스케줄 생성')}
        >
          <Ionicons name="add" size={24} color="white" />
        </TouchableOpacity>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{schedules.length}</Text>
          <Text style={styles.statLabel}>총 스케줄</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>
            {schedules.filter(s => s.status === 'working').length}
          </Text>
          <Text style={styles.statLabel}>근무중</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>
            {schedules.filter(s => s.status === 'scheduled').length}
          </Text>
          <Text style={styles.statLabel}>예정</Text>
        </View>
      </View>

      <FlatList
        data={schedules}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => <ScheduleCard schedule={item} />}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#3b82f6',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  addButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 4,
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#3b82f6',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#6b7280',
  },
  listContainer: {
    padding: 16,
  },
  scheduleCard: {
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
  scheduleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  employeeName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: 'white',
  },
  scheduleDetails: {
    gap: 6,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  detailText: {
    fontSize: 14,
    color: '#6b7280',
    marginLeft: 8,
  },
}); 