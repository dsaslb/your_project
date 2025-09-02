/**
 * 🕐 출퇴근 화면
 * 
 * GPS 위치 기반 출퇴근 체크 기능
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  ScrollView,
  Platform,
} from 'react-native';
import * as Location from 'expo-location';
// import { BarCodeScanner } from 'expo-barcode-scanner'; // QR 코드 기능 비활성화
import { mobileAPI } from '../api/client';
import { subscribeToAttendanceUpdates } from '../api/socket';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface AttendanceData {
  user_id: number;
  type: 'in' | 'out';
  at: string;
  lat?: number;
  lng?: number;
  qr?: string;
}

export default function AttendanceScreen() {
  const [loading, setLoading] = useState(false);
  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  // const [scanned, setScanned] = useState(false); // QR 코드 기능 비활성화
  // const [showScanner, setShowScanner] = useState(false); // QR 코드 기능 비활성화
  const [attendanceHistory, setAttendanceHistory] = useState<AttendanceData[]>([]);

  useEffect(() => {
    // 위치 권한 요청
    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      setHasPermission(status === 'granted');
      
      if (status === 'granted') {
        getCurrentLocation();
      }
    })();

    // 실시간 출퇴근 업데이트 구독
    const unsubscribe = subscribeToAttendanceUpdates((data: AttendanceData) => {
      setAttendanceHistory(prev => [data, ...prev]);
      Alert.alert(
        '출퇴근 업데이트',
        `${data.type === 'in' ? '출근' : '퇴근'} 기록이 업데이트되었습니다.`
      );
    });

    return unsubscribe;
  }, []);

  const getCurrentLocation = async () => {
    try {
      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });
      setLocation(location);
    } catch (error) {
      console.error('위치 가져오기 실패:', error);
      Alert.alert('오류', '현재 위치를 가져올 수 없습니다.');
    }
  };

  const handleAttendance = async (type: 'in' | 'out') => {
    if (!location) {
      Alert.alert('오류', '위치 정보가 필요합니다. 위치 권한을 확인해주세요.');
      return;
    }

    setLoading(true);
    try {
      const result = await mobileAPI.clockAttendance(type, {
        lat: location.coords.latitude,
        lng: location.coords.longitude,
      });

      if (result.ok) {
        Alert.alert(
          '성공',
          `${type === 'in' ? '출근' : '퇴근'}이 기록되었습니다.`,
          [{ text: '확인' }]
        );
        
        // 출퇴근 기록을 로컬에 저장
        const newRecord: AttendanceData = {
          user_id: result.user_id,
          type: result.type,
          at: result.at,
          lat: result.lat,
          lng: result.lng,
          qr: result.qr,
        };
        
        setAttendanceHistory(prev => [newRecord, ...prev]);
      }
    } catch (error) {
      console.error('출퇴근 기록 실패:', error);
      Alert.alert('오류', '출퇴근 기록에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // QR 코드 기능 비활성화
  // const handleBarCodeScanned = ({ type, data }: { type: string; data: string }) => {
  //   setScanned(true);
  //   setShowScanner(false);
  //   
  //   // QR 코드로 출퇴근 체크
  //   if (location) {
  //     mobileAPI.clockAttendance('in', {
  //       lat: location.coords.latitude,
  //       lng: location.coords.longitude,
  //       qr: data,
  //     }).then(result => {
  //       if (result.ok) {
  //         Alert.alert('성공', 'QR 코드로 출근이 기록되었습니다.');
  //       }
  //     }).catch(error => {
  //       Alert.alert('오류', 'QR 코드 출근 기록에 실패했습니다.');
  //     });
  //   }
  // };

  // const requestCameraPermission = async () => {
  //   const { status } = await BarCodeScanner.requestPermissionsAsync();
  //   setHasPermission(status === 'granted');
  //   
  //   if (status === 'granted') {
  //     setShowScanner(true);
  //   } else {
  //     Alert.alert('권한 필요', 'QR 코드 스캔을 위해 카메라 권한이 필요합니다.');
  //   }
  // };

  // QR 코드 스캐너 화면 비활성화
  // if (showScanner) {
  //   return (
  //     <View style={styles.container}>
  //       <BarCodeScanner
  //         onBarCodeScanned={scanned ? undefined : handleBarCodeScanned}
  //         style={StyleSheet.absoluteFillObject}
  //       />
  //       <View style={styles.scannerOverlay}>
  //         <TouchableOpacity
  //           style={styles.closeButton}
  //           onPress={() => setShowScanner(false)}
  //         >
  //           <Text style={styles.closeButtonText}>닫기</Text>
  //         </TouchableOpacity>
  //       </View>
  //     </View>
  //   );
  // }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>출퇴근 관리</Text>
        <Text style={styles.subtitle}>GPS 위치 기반 출퇴근 체크</Text>
      </View>

      {/* 현재 위치 정보 */}
      <View style={styles.locationCard}>
        <Text style={styles.cardTitle}>📍 현재 위치</Text>
        {location ? (
          <View>
            <Text style={styles.locationText}>
              위도: {location.coords.latitude.toFixed(6)}
            </Text>
            <Text style={styles.locationText}>
              경도: {location.coords.longitude.toFixed(6)}
            </Text>
            <Text style={styles.locationText}>
              정확도: {location.coords.accuracy?.toFixed(1)}m
            </Text>
          </View>
        ) : (
          <Text style={styles.noLocationText}>위치 정보를 가져오는 중...</Text>
        )}
        <TouchableOpacity
          style={styles.refreshButton}
          onPress={getCurrentLocation}
        >
          <Text style={styles.refreshButtonText}>위치 새로고침</Text>
        </TouchableOpacity>
      </View>

      {/* 출퇴근 버튼 */}
      <View style={styles.attendanceButtons}>
        <TouchableOpacity
          style={[styles.attendanceButton, styles.clockInButton]}
          onPress={() => handleAttendance('in')}
          disabled={loading || !location}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.attendanceButtonText}>출근 체크</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.attendanceButton, styles.clockOutButton]}
          onPress={() => handleAttendance('out')}
          disabled={loading || !location}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.attendanceButtonText}>퇴근 체크</Text>
          )}
        </TouchableOpacity>
      </View>

      {/* QR 코드 스캔 버튼 비활성화 */}
      {/* <TouchableOpacity
        style={styles.qrButton}
        onPress={requestCameraPermission}
      >
        <Text style={styles.qrButtonText}>📱 QR 코드로 출근</Text>
      </TouchableOpacity> */}

      {/* 출퇴근 기록 */}
      <View style={styles.historyCard}>
        <Text style={styles.cardTitle}>📋 최근 기록</Text>
        {attendanceHistory.length > 0 ? (
          attendanceHistory.map((record, index) => (
            <View key={index} style={styles.historyItem}>
              <Text style={styles.historyType}>
                {record.type === 'in' ? '출근' : '퇴근'}
              </Text>
              <Text style={styles.historyTime}>
                {new Date(record.at).toLocaleString('ko-KR')}
              </Text>
              {record.lat && record.lng && (
                <Text style={styles.historyLocation}>
                  위치: {record.lat.toFixed(4)}, {record.lng.toFixed(4)}
                </Text>
              )}
            </View>
          ))
        ) : (
          <Text style={styles.noHistoryText}>출퇴근 기록이 없습니다.</Text>
        )}
      </View>
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
  locationCard: {
    backgroundColor: 'white',
    margin: 20,
    padding: 20,
    borderRadius: 10,
    elevation: 3,
    ...(Platform.OS === 'ios' ? {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
    } : {}),
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  locationText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  noLocationText: {
    fontSize: 14,
    color: '#999',
    fontStyle: 'italic',
  },
  refreshButton: {
    backgroundColor: '#4CAF50',
    padding: 10,
    borderRadius: 5,
    alignItems: 'center',
    marginTop: 15,
  },
  refreshButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  attendanceButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginHorizontal: 20,
    marginBottom: 20,
  },
  attendanceButton: {
    flex: 1,
    padding: 20,
    borderRadius: 10,
    alignItems: 'center',
    marginHorizontal: 5,
  },
  clockInButton: {
    backgroundColor: '#4CAF50',
  },
  clockOutButton: {
    backgroundColor: '#F44336',
  },
  attendanceButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  qrButton: {
    backgroundColor: '#FF9800',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginHorizontal: 20,
    marginBottom: 20,
  },
  qrButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  historyCard: {
    backgroundColor: 'white',
    margin: 20,
    padding: 20,
    borderRadius: 10,
    elevation: 3,
    ...(Platform.OS === 'ios' ? {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
    } : {}),
  },
  historyItem: {
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    paddingVertical: 10,
  },
  historyType: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  historyTime: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  historyLocation: {
    fontSize: 12,
    color: '#999',
    marginTop: 3,
  },
  noHistoryText: {
    fontSize: 14,
    color: '#999',
    fontStyle: 'italic',
    textAlign: 'center',
    paddingVertical: 20,
  },
  scannerOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  closeButton: {
    position: 'absolute',
    top: 50,
    right: 20,
    backgroundColor: 'rgba(0,0,0,0.7)',
    padding: 10,
    borderRadius: 5,
  },
  closeButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
});
