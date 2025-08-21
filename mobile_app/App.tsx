import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  Alert,
  SafeAreaView,
  StatusBar,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { api } from './src/api/client';
import { socket } from './src/api/socket';
import InventoryScreen from './src/screens/InventoryScreen';
import PurchaseOrderScreen from './src/screens/PurchaseOrderScreen';
import ScheduleScreen from './src/screens/ScheduleScreen';
import { safePost, flushQueue, getQueueStatus } from './src/utils/queue';

export default function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [currentScreen, setCurrentScreen] = useState<'dashboard' | 'inventory' | 'purchase_order' | 'schedule'>('dashboard');

  useEffect(() => {
    // 소켓 연결 상태 모니터링
    socket.onConnectionChange((connected) => {
      console.log('소켓 연결 상태:', connected);
      
      // 네트워크 연결 복구 시 오프라인 큐 처리
      if (connected) {
        setTimeout(async () => {
          try {
            const status = await getQueueStatus();
            if (status.total > 0) {
              console.log(`📥 오프라인 큐 발견: ${status.total}개 작업`);
              const results = await flushQueue();
              if (results.success > 0) {
                Alert.alert('동기화 완료', `${results.success}개 작업이 동기화되었습니다.`);
              }
            }
          } catch (error) {
            console.error('오프라인 큐 처리 실패:', error);
          }
        }, 1000);
      }
    });

    // 실시간 이벤트 구독
    socket.on('attendance:update', (data) => {
      console.log('출퇴근 업데이트:', data);
      Alert.alert('출퇴근 알림', `${data.user_name}님이 ${data.type === 'in' ? '출근' : '퇴근'}했습니다.`);
    });

    socket.on('inventory:update', (data) => {
      console.log('재고 업데이트:', data);
      Alert.alert('재고 알림', `재고가 업데이트되었습니다. (${data.barcode})`);
    });

    return () => {
      socket.off('attendance:update');
      socket.off('inventory:update');
    };
  }, []);

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert('오류', '사용자명과 비밀번호를 입력해주세요.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await api.login({ username, password });
      setUser(response.user);
      setIsLoggedIn(true);
      Alert.alert('성공', '로그인되었습니다!');
    } catch (error: any) {
      console.error('로그인 오류:', error);
      Alert.alert('로그인 실패', error.response?.data?.error || '로그인에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await api.logout();
      setIsLoggedIn(false);
      setUser(null);
      setUsername('');
      setPassword('');
      Alert.alert('로그아웃', '로그아웃되었습니다.');
    } catch (error) {
      console.error('로그아웃 오류:', error);
    }
  };

  const handleTestAttendance = async () => {
    try {
      const response = await safePost('/api/mobile/attendance/clock', {
        type: 'in',
        lat: 37.5665, // 서울 시청 좌표 (테스트용)
        lng: 126.9780,
      });
      Alert.alert('출근 기록', '출근이 기록되었습니다!');
      console.log('출근 기록 응답:', response);
    } catch (error: any) {
      console.error('출근 기록 실패:', error);
      Alert.alert('오류', error.response?.data?.error || '출근 기록에 실패했습니다.');
    }
  };

  if (isLoggedIn) {
    console.log('🔍 현재 화면:', currentScreen);
    
    if (currentScreen === 'inventory') {
      console.log('📦 재고 조사 화면으로 이동');
      return <InventoryScreen onBack={() => setCurrentScreen('dashboard')} />;
    }
    
    if (currentScreen === 'purchase_order') {
      console.log('📋 발주 관리 화면으로 이동');
      return <PurchaseOrderScreen onBack={() => setCurrentScreen('dashboard')} />;
    }
    
    if (currentScreen === 'schedule') {
      console.log('📅 스케줄 관리 화면으로 이동');
      return <ScheduleScreen onBack={() => setCurrentScreen('dashboard')} />;
    }
    
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="dark-content" />
        <View style={styles.content}>
          <Text style={styles.welcomeText}>환영합니다, {user?.username}님!</Text>
          
          <View style={styles.menuContainer}>
            <TouchableOpacity style={styles.menuButton} onPress={handleTestAttendance}>
              <Text style={styles.menuButtonText}>⏰ 출근 기록 (테스트)</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.menuButton} 
              onPress={() => setCurrentScreen('inventory')}
            >
              <Text style={styles.menuButtonText}>📦 재고 조사</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.menuButton} 
              onPress={() => {
                console.log('📋 발주 관리 버튼 클릭됨');
                setCurrentScreen('purchase_order');
              }}
            >
              <Text style={styles.menuButtonText}>📋 발주 관리</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.menuButton}
              onPress={() => {
                console.log('📅 스케줄 관리 버튼 클릭됨');
                setCurrentScreen('schedule');
              }}
            >
              <Text style={styles.menuButtonText}>📅 스케줄 관리</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.menuButton}>
              <Text style={styles.menuButtonText}>🍽️ 주문 관리</Text>
            </TouchableOpacity>
          </View>
          
          <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
            <Text style={styles.logoutButtonText}>로그아웃</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <View style={styles.content}>
          <Text style={styles.title}>📱 직원 관리 앱</Text>
          <Text style={styles.subtitle}>출퇴근 • 재고 • 발주 • 스케줄</Text>
          
          <View style={styles.formContainer}>
            <TextInput
              style={styles.input}
              placeholder="사용자명"
              value={username}
              onChangeText={setUsername}
              autoCapitalize="none"
              autoCorrect={false}
            />
            
            <TextInput
              style={styles.input}
              placeholder="비밀번호"
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              autoCapitalize="none"
              autoCorrect={false}
            />
            
            <TouchableOpacity
              style={[styles.loginButton, isLoading && styles.loginButtonDisabled]}
              onPress={handleLogin}
              disabled={isLoading}
            >
              <Text style={styles.loginButtonText}>
                {isLoading ? '로그인 중...' : '로그인'}
              </Text>
            </TouchableOpacity>
          </View>
          
          <Text style={styles.note}>
            💡 개발 모드: 실제 서버 연결을 위해 IP 주소를 확인하세요
          </Text>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  keyboardView: {
    flex: 1,
  },
  content: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 40,
    color: '#666',
  },
  formContainer: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    fontSize: 16,
    backgroundColor: '#fafafa',
  },
  loginButton: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  loginButtonDisabled: {
    backgroundColor: '#ccc',
  },
  loginButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  note: {
    textAlign: 'center',
    marginTop: 20,
    color: '#999',
    fontSize: 12,
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 30,
    color: '#333',
  },
  menuContainer: {
    marginBottom: 30,
  },
  menuButton: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
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
  menuButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    textAlign: 'center',
  },
  logoutButton: {
    backgroundColor: '#FF3B30',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  logoutButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});
