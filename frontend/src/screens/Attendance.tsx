/**
 * 📱 출퇴근 화면
 * 
 * 오프라인 큐 시스템과 멱등성 키를 적용한 안전한 출퇴근 처리
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  ActivityIndicator,
  StatusBar
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import * as Location from 'expo-location';
import { v4 as uuid } from 'uuid';
import { useAuth } from '../hooks/useAuth';
import { offlineQueue, safeApiCall } from '../utils/offlineQueue';
import { API_BASE_URL } from '../config/api';

interface AttendanceData {
  type: 'in' | 'out';
  lat: number;
  lng: number;
  qr?: string;
}

interface QueueStatus {
  isOnline: boolean;
  queueLength: number;
  lastSync: number | null;
  isProcessing: boolean;
}

export default function AttendanceScreen() {
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [attendanceType, setAttendanceType] = useState<'in' | 'out'>('in');
  const [queueStatus, setQueueStatus] = useState<QueueStatus>({
    isOnline: true,
    queueLength: 0,
    lastSync: null,
    isProcessing: false
  });
  const [lastAttendance, setLastAttendance] = useState<any>(null);

  // 위치 권한 요청 및 현재 위치 가져오기
  useEffect(() => {
    requestLocationPermission();
    updateQueueStatus();
    
    // 네트워크 상태 변경 모니터링
    const unsubscribe = offlineQueue.onNetworkStatusChange((isOnline) => {
      updateQueueStatus();
      if (isOnline) {
        Alert.alert('🌐 네트워크 연결', '네트워크가 복구되었습니다. 큐에 저장된 요청을 동기화합니다.');
      } else {
        Alert.alert('📱 오프라인 모드', '네트워크 연결이 끊어졌습니다. 요청은 로컬에 저장됩니다.');
      }
    });

    // 주기적으로 큐 상태 업데이트
    const interval = setInterval(updateQueueStatus, 5000);

    return () => {
      unsubscribe();
      clearInterval(interval);
    };
  }, []);

  const requestLocationPermission = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        const currentLocation = await Location.getCurrentPositionAsync({
          accuracy: Location.Accuracy.High
        });
        setLocation(currentLocation);
      } else {
        Alert.alert('위치 권한 필요', '출퇴근 기록을 위해 위치 권한이 필요합니다.');
      }
    } catch (error) {
      console.error('위치 권한 요청 실패:', error);
      Alert.alert('오류', '위치 정보를 가져올 수 없습니다.');
    }
  };

  const updateQueueStatus = () => {
    setQueueStatus(offlineQueue.getQueueStatus());
  };

  const handleAttendance = async (type: 'in' | 'out') => {
    if (!location) {
      Alert.alert('위치 정보 없음', '현재 위치를 가져올 수 없습니다. 위치 권한을 확인해주세요.');
      return;
    }

    if (!token) {
      Alert.alert('인증 오류', '로그인이 필요합니다.');
      return;
    }

    setLoading(true);
    setAttendanceType(type);

    try {
      const attendanceData: AttendanceData = {
        type,
        lat: location.coords.latitude,
        lng: location.coords.longitude
      };

      // 멱등성 키 생성
      const idempotencyKey = uuid();
      
      // 안전한 API 호출 (오프라인 큐 지원)
      const result = await safeApiCall(
        `${API_BASE_URL}/api/mobile/attendance/clock`,
        'POST',
        attendanceData,
        {
          'Authorization': `Bearer ${token}`,
          'X-Idempotency-Key': idempotencyKey,
          'X-Device-ID': user?.deviceId || 'unknown'
        }
      );

      if (result.success) {
        // 성공적으로 서버에 전송됨
        setLastAttendance({
          type,
          timestamp: new Date().toLocaleString(),
          location: `${attendanceData.lat.toFixed(6)}, ${attendanceData.lng.toFixed(6)}`
        });
        
        Alert.alert(
          '✅ 출퇴근 기록 완료',
          `${type === 'in' ? '출근' : '퇴근'}이 기록되었습니다.\n시간: ${new Date().toLocaleString()}\n위치: ${attendanceData.lat.toFixed(6)}, ${attendanceData.lng.toFixed(6)}`
        );
      } else if (result.queueId) {
        // 오프라인 상태: 큐에 저장됨
        Alert.alert(
          '📱 오프라인 저장',
          `${type === 'in' ? '출근' : '퇴근'} 요청이 로컬에 저장되었습니다.\n네트워크 연결 시 자동으로 동기화됩니다.\n큐 ID: ${result.queueId}`
        );
        
        // 큐 상태 업데이트
        updateQueueStatus();
      } else {
        // 기타 오류
        Alert.alert('❌ 오류', `출퇴근 기록에 실패했습니다: ${result.error}`);
      }
    } catch (error) {
      console.error('출퇴근 처리 오류:', error);
      Alert.alert('❌ 오류', '출퇴근 처리 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleRetryQueue = async () => {
    if (queueStatus.queueLength === 0) {
      Alert.alert('알림', '재시도할 큐 항목이 없습니다.');
      return;
    }

    Alert.alert(
      '🔄 큐 재시도',
      `${queueStatus.queueLength}개의 저장된 요청을 다시 시도하시겠습니까?`,
      [
        { text: '취소', style: 'cancel' },
        { 
          text: '재시도', 
          onPress: () => {
            offlineQueue.processQueue();
            updateQueueStatus();
          }
        }
      ]
    );
  };

  const handleClearQueue = async () => {
    if (queueStatus.queueLength === 0) {
      Alert.alert('알림', '초기화할 큐 항목이 없습니다.');
      return;
    }

    Alert.alert(
      '🗑️ 큐 초기화',
      '저장된 모든 요청을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.',
      [
        { text: '취소', style: 'cancel' },
        { 
          text: '삭제', 
          style: 'destructive',
          onPress: async () => {
            await offlineQueue.clearQueue();
            updateQueueStatus();
            Alert.alert('완료', '큐가 초기화되었습니다.');
          }
        }
      ]
    );
  };

  const getQueueStatusText = () => {
    if (queueStatus.queueLength === 0) {
      return '대기 중인 요청 없음';
    }
    
    const lastSyncText = queueStatus.lastSync 
      ? `마지막: ${new Date(queueStatus.lastSync).toLocaleString()}`
      : '';
    
    return `${queueStatus.queueLength}개 요청 대기 중\n${lastSyncText}`;
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#f8f9fa" />
      
      {/* 헤더 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>출퇴근 관리</Text>
        <View style={styles.networkStatus}>
          <Ionicons 
            name={queueStatus.isOnline ? 'wifi' : 'wifi-outline'} 
            size={20} 
            color={queueStatus.isOnline ? '#28a745' : '#dc3545'} 
          />
          <Text style={[styles.networkText, { color: queueStatus.isOnline ? '#28a745' : '#dc3545' }]}>
            {queueStatus.isOnline ? '온라인' : '오프라인'}
          </Text>
        </View>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* 사용자 정보 */}
        <View style={styles.userInfo}>
          <Ionicons name="person-circle" size={50} color="#007bff" />
          <Text style={styles.userName}>{user?.username || '사용자'}</Text>
          <Text style={styles.userRole}>{user?.role || '직원'}</Text>
        </View>

        {/* 출퇴근 버튼 */}
        <View style={styles.attendanceButtons}>
          <TouchableOpacity
            style={[styles.attendanceButton, styles.clockInButton]}
            onPress={() => handleAttendance('in')}
            disabled={loading}
          >
            <Ionicons name="log-in" size={40} color="white" />
            <Text style={styles.attendanceButtonText}>출근</Text>
            {loading && attendanceType === 'in' && (
              <ActivityIndicator size="small" color="white" style={styles.loadingIndicator} />
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.attendanceButton, styles.clockOutButton]}
            onPress={() => handleAttendance('out')}
            disabled={loading}
          >
            <Ionicons name="log-out" size={40} color="white" />
            <Text style={styles.attendanceButtonText}>퇴근</Text>
            {loading && attendanceType === 'out' && (
              <ActivityIndicator size="small" color="white" style={styles.loadingIndicator} />
            )}
          </TouchableOpacity>
        </View>

        {/* 마지막 출퇴근 기록 */}
        {lastAttendance && (
          <View style={styles.lastAttendance}>
            <Text style={styles.lastAttendanceTitle}>마지막 기록</Text>
            <View style={styles.lastAttendanceContent}>
              <Ionicons 
                name={lastAttendance.type === 'in' ? 'log-in' : 'log-out'} 
                size={24} 
                color={lastAttendance.type === 'in' ? '#28a745' : '#dc3545'} 
              />
              <View style={styles.lastAttendanceText}>
                <Text style={styles.lastAttendanceType}>
                  {lastAttendance.type === 'in' ? '출근' : '퇴근'}
                </Text>
                <Text style={styles.lastAttendanceTime}>{lastAttendance.timestamp}</Text>
                <Text style={styles.lastAttendanceLocation}>{lastAttendance.location}</Text>
              </View>
            </View>
          </View>
        )}

        {/* 오프라인 큐 상태 */}
        <View style={styles.queueStatus}>
          <Text style={styles.queueStatusTitle}>동기화 상태</Text>
          <View style={styles.queueStatusContent}>
            <Text style={styles.queueStatusText}>{getQueueStatusText()}</Text>
            
            {queueStatus.queueLength > 0 && (
              <View style={styles.queueActions}>
                <TouchableOpacity
                  style={[styles.queueButton, styles.retryButton]}
                  onPress={handleRetryQueue}
                  disabled={queueStatus.isProcessing}
                >
                  <Ionicons name="refresh" size={16} color="white" />
                  <Text style={styles.queueButtonText}>재시도</Text>
                </TouchableOpacity>
                
                <TouchableOpacity
                  style={[styles.queueButton, styles.clearButton]}
                  onPress={handleClearQueue}
                >
                  <Ionicons name="trash" size={16} color="white" />
                  <Text style={styles.queueButtonText}>초기화</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        </View>

        {/* 위치 정보 */}
        <View style={styles.locationInfo}>
          <Text style={styles.locationInfoTitle}>현재 위치</Text>
          {location ? (
            <View style={styles.locationContent}>
              <Ionicons name="location" size={20} color="#007bff" />
              <Text style={styles.locationText}>
                {location.coords.latitude.toFixed(6)}, {location.coords.longitude.toFixed(6)}
              </Text>
            </View>
          ) : (
            <Text style={styles.locationError}>위치 정보를 가져올 수 없습니다</Text>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#212529',
  },
  networkStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  networkText: {
    fontSize: 14,
    fontWeight: '500',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  userInfo: {
    alignItems: 'center',
    marginBottom: 30,
    padding: 20,
    backgroundColor: 'white',
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  userName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#212529',
    marginTop: 10,
  },
  userRole: {
    fontSize: 14,
    color: '#6c757d',
    marginTop: 5,
  },
  attendanceButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 30,
    gap: 15,
  },
  attendanceButton: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 25,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 10,
    elevation: 5,
    position: 'relative',
  },
  clockInButton: {
    backgroundColor: '#28a745',
  },
  clockOutButton: {
    backgroundColor: '#dc3545',
  },
  attendanceButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 10,
  },
  loadingIndicator: {
    position: 'absolute',
    top: 10,
    right: 10,
  },
  lastAttendance: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  lastAttendanceTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#212529',
    marginBottom: 15,
  },
  lastAttendanceContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 15,
  },
  lastAttendanceText: {
    flex: 1,
  },
  lastAttendanceType: {
    fontSize: 16,
    fontWeight: '600',
    color: '#212529',
  },
  lastAttendanceTime: {
    fontSize: 14,
    color: '#6c757d',
    marginTop: 2,
  },
  lastAttendanceLocation: {
    fontSize: 12,
    color: '#adb5bd',
    marginTop: 2,
  },
  queueStatus: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  queueStatusTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#212529',
    marginBottom: 15,
  },
  queueStatusContent: {
    gap: 15,
  },
  queueStatusText: {
    fontSize: 14,
    color: '#6c757d',
    lineHeight: 20,
  },
  queueActions: {
    flexDirection: 'row',
    gap: 10,
  },
  queueButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 8,
    gap: 5,
  },
  retryButton: {
    backgroundColor: '#007bff',
  },
  clearButton: {
    backgroundColor: '#6c757d',
  },
  queueButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '500',
  },
  locationInfo: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  locationInfoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#212529',
    marginBottom: 15,
  },
  locationContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  locationText: {
    fontSize: 14,
    color: '#6c757d',
    fontFamily: 'monospace',
  },
  locationError: {
    fontSize: 14,
    color: '#dc3545',
    fontStyle: 'italic',
  },
});
