import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  TextInput,
  Chip,
  FAB,
  Portal,
  Modal,
  Text,
} from 'react-native-paper';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { apiClient } from '../services/apiClient';

interface AttendanceRecord {
  id: string;
  userId: string;
  userName: string;
  checkIn: string;
  checkOut?: string;
  date: string;
  status: 'present' | 'absent' | 'late' | 'leave';
  notes?: string;
}

interface AttendanceScreenProps {
  navigation: any;
}

export default function AttendanceScreen({ navigation }: AttendanceScreenProps) {
  const [visible, setVisible] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [searchQuery, setSearchQuery] = useState('');
  const queryClient = useQueryClient();

  // 출근 기록 조회
  const { data: attendanceRecords, isLoading } = useQuery(
    ['attendance', selectedDate.toISOString().split('T')[0]],
    () => apiClient.get('/attendance', {
      params: {
        date: selectedDate.toISOString().split('T')[0],
        search: searchQuery,
      },
    }),
    {
      select: (response) => response.data,
    }
  );

  // 출근 체크인
  const checkInMutation = useMutation(
    () => apiClient.post('/attendance/check-in'),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['attendance']);
        Alert.alert('성공', '출근이 기록되었습니다.');
      },
      onError: (error) => {
        Alert.alert('오류', '출근 기록에 실패했습니다.');
      },
    }
  );

  // 퇴근 체크아웃
  const checkOutMutation = useMutation(
    () => apiClient.post('/attendance/check-out'),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['attendance']);
        Alert.alert('성공', '퇴근이 기록되었습니다.');
      },
      onError: (error) => {
        Alert.alert('오류', '퇴근 기록에 실패했습니다.');
      },
    }
  );

  const handleCheckIn = () => {
    checkInMutation.mutate();
  };

  const handleCheckOut = () => {
    checkOutMutation.mutate();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'present':
        return '#10B981';
      case 'absent':
        return '#EF4444';
      case 'late':
        return '#F59E0B';
      case 'leave':
        return '#6B7280';
      default:
        return '#6B7280';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'present':
        return '출근';
      case 'absent':
        return '결근';
      case 'late':
        return '지각';
      case 'leave':
        return '휴가';
      default:
        return '알 수 없음';
    }
  };

  const showModal = () => setVisible(true);
  const hideModal = () => setVisible(false);

  if (isLoading) {
    return (
      <View style={styles.container}>
        <Text>로딩 중...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {/* 검색 및 필터 */}
        <Card style={styles.searchCard}>
          <Card.Content>
            <TextInput
              label="직원 검색"
              value={searchQuery}
              onChangeText={setSearchQuery}
              mode="outlined"
              style={styles.searchInput}
            />
          </Card.Content>
        </Card>

        {/* 출근 통계 */}
        <Card style={styles.statsCard}>
          <Card.Content>
            <Title>오늘 출근 현황</Title>
            <View style={styles.statsRow}>
              <View style={styles.statItem}>
                <Text style={styles.statNumber}>
                  {attendanceRecords?.filter((r: AttendanceRecord) => r.status === 'present').length || 0}
                </Text>
                <Text style={styles.statLabel}>출근</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statNumber}>
                  {attendanceRecords?.filter((r: AttendanceRecord) => r.status === 'absent').length || 0}
                </Text>
                <Text style={styles.statLabel}>결근</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statNumber}>
                  {attendanceRecords?.filter((r: AttendanceRecord) => r.status === 'late').length || 0}
                </Text>
                <Text style={styles.statLabel}>지각</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statNumber}>
                  {attendanceRecords?.filter((r: AttendanceRecord) => r.status === 'leave').length || 0}
                </Text>
                <Text style={styles.statLabel}>휴가</Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        {/* 출근 기록 목록 */}
        {attendanceRecords?.map((record: AttendanceRecord) => (
          <Card key={record.id} style={styles.recordCard}>
            <Card.Content>
              <View style={styles.recordHeader}>
                <Title>{record.userName}</Title>
                <Chip
                  mode="outlined"
                  textStyle={{ color: getStatusColor(record.status) }}
                  style={[styles.statusChip, { borderColor: getStatusColor(record.status) }]}
                >
                  {getStatusText(record.status)}
                </Chip>
              </View>
              <View style={styles.recordDetails}>
                <Paragraph>출근: {record.checkIn}</Paragraph>
                {record.checkOut && <Paragraph>퇴근: {record.checkOut}</Paragraph>}
                {record.notes && <Paragraph>비고: {record.notes}</Paragraph>}
              </View>
            </Card.Content>
          </Card>
        ))}

        {/* 출근 기록이 없을 때 */}
        {(!attendanceRecords || attendanceRecords.length === 0) && (
          <Card style={styles.emptyCard}>
            <Card.Content>
              <Text style={styles.emptyText}>오늘의 출근 기록이 없습니다.</Text>
            </Card.Content>
          </Card>
        )}
      </ScrollView>

      {/* 출근/퇴근 버튼 */}
      <View style={styles.buttonContainer}>
        <Button
          mode="contained"
          onPress={handleCheckIn}
          loading={checkInMutation.isLoading}
          style={[styles.button, styles.checkInButton]}
        >
          출근
        </Button>
        <Button
          mode="outlined"
          onPress={handleCheckOut}
          loading={checkOutMutation.isLoading}
          style={[styles.button, styles.checkOutButton]}
        >
          퇴근
        </Button>
      </View>

      {/* FAB */}
      <Portal>
        <FAB
          style={styles.fab}
          icon="plus"
          onPress={showModal}
        />
      </Portal>

      {/* 모달 */}
      <Portal>
        <Modal
          visible={visible}
          onDismiss={hideModal}
          contentContainerStyle={styles.modal}
        >
          <Title>출근 관리</Title>
          <Text>추가 기능을 구현할 수 있습니다.</Text>
          <Button onPress={hideModal}>닫기</Button>
        </Modal>
      </Portal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
    padding: 16,
  },
  searchCard: {
    marginBottom: 16,
  },
  searchInput: {
    marginBottom: 8,
  },
  statsCard: {
    marginBottom: 16,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#3B82F6',
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  recordCard: {
    marginBottom: 12,
  },
  recordHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusChip: {
    height: 24,
  },
  recordDetails: {
    marginTop: 8,
  },
  emptyCard: {
    marginTop: 32,
    alignItems: 'center',
  },
  emptyText: {
    color: '#6B7280',
    fontSize: 16,
  },
  buttonContainer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  button: {
    flex: 1,
    marginHorizontal: 8,
  },
  checkInButton: {
    backgroundColor: '#10B981',
  },
  checkOutButton: {
    borderColor: '#6B7280',
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 80,
  },
  modal: {
    backgroundColor: 'white',
    padding: 20,
    margin: 20,
    borderRadius: 8,
  },
}); 