import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  TextInput,
  Modal,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { api } from '../api/client';
import { safePost } from '../utils/queue';

interface ScheduleItem {
  id: string;
  date: string;
  type: 'work' | 'off' | 'leave' | 'swap';
  start_time?: string;
  end_time?: string;
  status: 'confirmed' | 'pending' | 'rejected';
}

interface LeaveRequest {
  type: string;
  start_date: string;
  end_date: string;
  reason: string;
}

interface SwapRequest {
  target_date: string;
  swap_with_user: string;
  reason: string;
}

export default function ScheduleScreen({ onBack }: { onBack: () => void }) {
  console.log('📅 ScheduleScreen 렌더링됨');
  
  const [schedules, setSchedules] = useState<ScheduleItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showLeaveModal, setShowLeaveModal] = useState(false);
  const [showSwapModal, setShowSwapModal] = useState(false);
  const [leaveRequest, setLeaveRequest] = useState<LeaveRequest>({
    type: 'annual',
    start_date: '',
    end_date: '',
    reason: ''
  });
  const [swapRequest, setSwapRequest] = useState<SwapRequest>({
    target_date: '',
    swap_with_user: '',
    reason: ''
  });

  useEffect(() => {
    console.log('📅 ScheduleScreen useEffect 실행됨');
    loadSchedule();
  }, []);

  const loadSchedule = async () => {
    try {
      setIsLoading(true);
      const response = await api.getSchedule();
      setSchedules(response.data || []);
    } catch (error: any) {
      console.error('스케줄 조회 실패:', error);
      Alert.alert('오류', '스케줄을 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLeaveRequest = async () => {
    if (!leaveRequest.start_date || !leaveRequest.end_date) {
      Alert.alert('오류', '시작일과 종료일을 입력해주세요.');
      return;
    }

    try {
      setIsLoading(true);
      await safePost('/api/mobile/schedule/leave', leaveRequest);
      
      Alert.alert('성공', '휴가 신청이 완료되었습니다!');
      setShowLeaveModal(false);
      setLeaveRequest({
        type: 'annual',
        start_date: '',
        end_date: '',
        reason: ''
      });
      loadSchedule(); // 스케줄 새로고침
    } catch (error: any) {
      console.error('휴가 신청 실패:', error);
      Alert.alert('오류', error.response?.data?.error || '휴가 신청에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSwapRequest = async () => {
    if (!swapRequest.target_date || !swapRequest.swap_with_user) {
      Alert.alert('오류', '교대 날짜와 교대할 직원을 입력해주세요.');
      return;
    }

    try {
      setIsLoading(true);
      await safePost('/api/mobile/schedule/swap', swapRequest);
      
      Alert.alert('성공', '근무 교대 신청이 완료되었습니다!');
      setShowSwapModal(false);
      setSwapRequest({
        target_date: '',
        swap_with_user: '',
        reason: ''
      });
      loadSchedule(); // 스케줄 새로고침
    } catch (error: any) {
      console.error('근무 교대 신청 실패:', error);
      Alert.alert('오류', error.response?.data?.error || '근무 교대 신청에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const getScheduleTypeText = (type: string) => {
    switch (type) {
      case 'work': return '근무';
      case 'off': return '휴무';
      case 'leave': return '휴가';
      case 'swap': return '교대';
      default: return type;
    }
  };

  const getScheduleTypeColor = (type: string) => {
    switch (type) {
      case 'work': return '#34C759';
      case 'off': return '#8E8E93';
      case 'leave': return '#FF9500';
      case 'swap': return '#007AFF';
      default: return '#8E8E93';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'confirmed': return '확정';
      case 'pending': return '대기';
      case 'rejected': return '거부';
      default: return status;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return '#34C759';
      case 'pending': return '#FF9500';
      case 'rejected': return '#FF3B30';
      default: return '#8E8E93';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
      weekday: 'short'
    });
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* 헤더 */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <Text style={styles.backButtonText}>← 뒤로</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>📅 스케줄 관리</Text>
        <View style={styles.headerButtons}>
          <TouchableOpacity 
            onPress={() => setShowLeaveModal(true)}
            style={[styles.headerButton, styles.leaveButton]}
          >
            <Text style={styles.headerButtonText}>휴가 신청</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            onPress={() => setShowSwapModal(true)}
            style={[styles.headerButton, styles.swapButton]}
          >
            <Text style={styles.headerButtonText}>교대 신청</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* 스케줄 목록 */}
      <ScrollView style={styles.content}>
        {isLoading ? (
          <ActivityIndicator size="large" color="#007AFF" style={styles.loader} />
        ) : schedules.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>스케줄이 없습니다</Text>
            <Text style={styles.emptyStateSubtext}>새로운 스케줄을 확인해보세요</Text>
          </View>
        ) : (
          schedules.map((schedule) => (
            <View key={schedule.id} style={styles.scheduleCard}>
              <View style={styles.scheduleHeader}>
                <Text style={styles.scheduleDate}>{formatDate(schedule.date)}</Text>
                <View style={[styles.typeBadge, { backgroundColor: getScheduleTypeColor(schedule.type) }]}>
                  <Text style={styles.typeText}>{getScheduleTypeText(schedule.type)}</Text>
                </View>
                <View style={[styles.statusBadge, { backgroundColor: getStatusColor(schedule.status) }]}>
                  <Text style={styles.statusText}>{getStatusText(schedule.status)}</Text>
                </View>
              </View>
              
              {schedule.start_time && schedule.end_time && (
                <Text style={styles.timeText}>
                  {schedule.start_time} - {schedule.end_time}
                </Text>
              )}
            </View>
          ))
        )}
      </ScrollView>

      {/* 휴가 신청 모달 */}
      <Modal
        visible={showLeaveModal}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setShowLeaveModal(false)}>
              <Text style={styles.cancelButton}>취소</Text>
            </TouchableOpacity>
            <Text style={styles.modalTitle}>휴가 신청</Text>
            <TouchableOpacity onPress={handleLeaveRequest} disabled={isLoading}>
              <Text style={[styles.saveButton, isLoading && styles.saveButtonDisabled]}>
                {isLoading ? '신청 중...' : '신청'}
              </Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.modalContent}>
            <Text style={styles.sectionTitle}>휴가 유형</Text>
            <View style={styles.typeSelector}>
              {['annual', 'sick', 'personal'].map((type) => (
                <TouchableOpacity
                  key={type}
                  style={[
                    styles.typeOption,
                    leaveRequest.type === type && styles.typeOptionSelected
                  ]}
                  onPress={() => setLeaveRequest({ ...leaveRequest, type })}
                >
                  <Text style={[
                    styles.typeOptionText,
                    leaveRequest.type === type && styles.typeOptionTextSelected
                  ]}>
                    {type === 'annual' ? '연차' : type === 'sick' ? '병가' : '개인휴가'}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <Text style={styles.sectionTitle}>휴가 기간</Text>
            <View style={styles.dateInputs}>
              <TextInput
                style={styles.dateInput}
                placeholder="시작일 (YYYY-MM-DD)"
                value={leaveRequest.start_date}
                onChangeText={(text) => setLeaveRequest({ ...leaveRequest, start_date: text })}
              />
              <TextInput
                style={styles.dateInput}
                placeholder="종료일 (YYYY-MM-DD)"
                value={leaveRequest.end_date}
                onChangeText={(text) => setLeaveRequest({ ...leaveRequest, end_date: text })}
              />
            </View>

            <Text style={styles.sectionTitle}>사유</Text>
            <TextInput
              style={styles.reasonInput}
              placeholder="휴가 사유를 입력하세요"
              value={leaveRequest.reason}
              onChangeText={(text) => setLeaveRequest({ ...leaveRequest, reason: text })}
              multiline
              numberOfLines={3}
            />
          </ScrollView>
        </SafeAreaView>
      </Modal>

      {/* 근무 교대 신청 모달 */}
      <Modal
        visible={showSwapModal}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setShowSwapModal(false)}>
              <Text style={styles.cancelButton}>취소</Text>
            </TouchableOpacity>
            <Text style={styles.modalTitle}>근무 교대 신청</Text>
            <TouchableOpacity onPress={handleSwapRequest} disabled={isLoading}>
              <Text style={[styles.saveButton, isLoading && styles.saveButtonDisabled]}>
                {isLoading ? '신청 중...' : '신청'}
              </Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.modalContent}>
            <Text style={styles.sectionTitle}>교대 날짜</Text>
            <TextInput
              style={styles.dateInput}
              placeholder="교대할 날짜 (YYYY-MM-DD)"
              value={swapRequest.target_date}
              onChangeText={(text) => setSwapRequest({ ...swapRequest, target_date: text })}
            />

            <Text style={styles.sectionTitle}>교대할 직원</Text>
            <TextInput
              style={styles.textInput}
              placeholder="교대할 직원의 이름 또는 ID"
              value={swapRequest.swap_with_user}
              onChangeText={(text) => setSwapRequest({ ...swapRequest, swap_with_user: text })}
            />

            <Text style={styles.sectionTitle}>교대 사유</Text>
            <TextInput
              style={styles.reasonInput}
              placeholder="교대 사유를 입력하세요"
              value={swapRequest.reason}
              onChangeText={(text) => setSwapRequest({ ...swapRequest, reason: text })}
              multiline
              numberOfLines={3}
            />
          </ScrollView>
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  backButton: {
    padding: 8,
  },
  backButtonText: {
    fontSize: 16,
    color: '#007AFF',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#000000',
  },
  headerButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  headerButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  leaveButton: {
    backgroundColor: '#FF9500',
  },
  swapButton: {
    backgroundColor: '#007AFF',
  },
  headerButtonText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  loader: {
    marginTop: 50,
  },
  emptyState: {
    alignItems: 'center',
    marginTop: 100,
  },
  emptyStateText: {
    fontSize: 18,
    color: '#8E8E93',
    marginBottom: 8,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#C7C7CC',
  },
  scheduleCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  scheduleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  scheduleDate: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000000',
    flex: 1,
  },
  typeBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    marginRight: 8,
  },
  typeText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  statusText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
  },
  timeText: {
    fontSize: 14,
    color: '#8E8E93',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  cancelButton: {
    fontSize: 16,
    color: '#FF3B30',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#000000',
  },
  saveButton: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '600',
  },
  saveButtonDisabled: {
    color: '#C7C7CC',
  },
  modalContent: {
    flex: 1,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000000',
    marginBottom: 12,
    marginTop: 16,
  },
  typeSelector: {
    flexDirection: 'row',
    gap: 8,
  },
  typeOption: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5E5EA',
    alignItems: 'center',
  },
  typeOptionSelected: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  typeOptionText: {
    fontSize: 14,
    color: '#8E8E93',
  },
  typeOptionTextSelected: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  dateInputs: {
    gap: 12,
  },
  dateInput: {
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    backgroundColor: '#FFFFFF',
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    backgroundColor: '#FFFFFF',
  },
  reasonInput: {
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    backgroundColor: '#FFFFFF',
    height: 80,
    textAlignVertical: 'top',
  },
});
