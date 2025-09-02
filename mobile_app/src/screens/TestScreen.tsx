import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  SafeAreaView,
  Alert
} from 'react-native';
import SafePost from '../utils/safePost';
import PurchaseOrderAPI from '../api/purchaseOrders';

export default function TestScreen() {
  const [queueStatus, setQueueStatus] = useState<{ count: number; oldestRequest?: any }>({ count: 0 });
  const [isOnline, setIsOnline] = useState(true);

  // 큐 상태 주기적 업데이트
  useEffect(() => {
    const updateQueueStatus = async () => {
      const status = await SafePost.getQueueStatus();
      setQueueStatus(status);
    };

    updateQueueStatus();
    const interval = setInterval(updateQueueStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  // 테스트 발주 생성
  const testCreatePurchaseOrder = async () => {
    const testRequest = {
      branch_id: 'test_branch_001',
      items: [
        { barcode: 'TEST001', name: '테스트 상품 1', qty: 5 },
        { barcode: 'TEST002', name: '테스트 상품 2', qty: 3 }
      ],
      notes: '테스트 발주입니다',
      priority: 'high' as const
    };

    try {
      console.log('🧪 테스트 발주 생성 시작');
      const response = await PurchaseOrderAPI.createPurchaseOrder(testRequest);
      
      if (response.success) {
        Alert.alert('✅ 성공', `발주 생성 성공!\n발주 ID: ${response.data?.po_id}`);
      } else if (response.error === 'offline') {
        Alert.alert('📱 오프라인', '발주가 오프라인 큐에 저장되었습니다.');
      } else {
        Alert.alert('❌ 실패', response.message || '알 수 없는 오류');
      }
    } catch (error) {
      console.error('❌ 테스트 발주 생성 오류:', error);
      Alert.alert('❌ 오류', '테스트 발주 생성 중 오류가 발생했습니다.');
    }
  };

  // 큐 수동 비우기
  const flushQueue = async () => {
    Alert.alert(
      '🔄 큐 비우기',
      '오프라인 큐의 모든 요청을 처리하시겠습니까?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '확인',
          onPress: async () => {
            try {
              await SafePost.flushQueue();
              Alert.alert('✅ 완료', '오프라인 큐 처리가 완료되었습니다.');
            } catch (error) {
              Alert.alert('❌ 오류', '큐 비우기 중 오류가 발생했습니다.');
            }
          }
        }
      ]
    );
  };

  // 큐 초기화
  const clearQueue = async () => {
    Alert.alert(
      '🗑️ 큐 초기화',
      '오프라인 큐의 모든 요청을 삭제하시겠습니까?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '확인',
          onPress: async () => {
            try {
              await SafePost.clearQueue();
              Alert.alert('✅ 완료', '오프라인 큐가 초기화되었습니다.');
            } catch (error) {
              Alert.alert('❌ 오류', '큐 초기화 중 오류가 발생했습니다.');
            }
          }
        }
      ]
    );
  };

  // 네트워크 상태 시뮬레이션
  const simulateOffline = () => {
    Alert.alert(
      '📱 오프라인 시뮬레이션',
      '이 기능을 테스트하려면 실제로 네트워크를 끊거나 비행기 모드를 활성화하세요.',
      [{ text: '확인' }]
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {/* 헤더 */}
        <View style={styles.header}>
          <Text style={styles.title}>🧪 실시간 이벤트 시스템 테스트</Text>
          <Text style={styles.subtitle}>모바일 앱 테스트 화면</Text>
        </View>

        {/* 큐 상태 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📦 오프라인 큐 상태</Text>
          <View style={styles.statusContainer}>
            <Text style={styles.statusText}>
              대기 중인 요청: <Text style={styles.statusValue}>{queueStatus.count}개</Text>
            </Text>
            {queueStatus.oldestRequest && (
              <Text style={styles.statusText}>
                가장 오래된 요청: {new Date(queueStatus.oldestRequest.timestamp).toLocaleString()}
              </Text>
            )}
          </View>
        </View>

        {/* 테스트 기능 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🧪 테스트 기능</Text>
          
          <TouchableOpacity 
            onPress={testCreatePurchaseOrder}
            style={styles.testButton}
          >
            <Text style={styles.testButtonText}>📋 테스트 발주 생성</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            onPress={simulateOffline}
            style={styles.testButton}
          >
            <Text style={styles.testButtonText}>📱 오프라인 테스트</Text>
          </TouchableOpacity>
        </View>

        {/* 큐 관리 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>⚙️ 큐 관리</Text>
          
          <TouchableOpacity 
            onPress={flushQueue}
            style={[styles.queueButton, styles.flushButton]}
          >
            <Text style={styles.queueButtonText}>🔄 큐 비우기</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            onPress={clearQueue}
            style={[styles.queueButton, styles.clearButton]}
          >
            <Text style={styles.queueButtonText}>🗑️ 큐 초기화</Text>
          </TouchableOpacity>
        </View>

        {/* 사용법 안내 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📖 사용법</Text>
          <Text style={styles.instructionText}>
            1. "테스트 발주 생성" 버튼을 눌러 발주를 생성합니다{'\n'}
            2. 네트워크를 끊고 다시 시도하면 오프라인 큐에 저장됩니다{'\n'}
            3. 네트워크를 다시 연결하면 자동으로 큐가 비워집니다{'\n'}
            4. "큐 비우기" 버튼으로 수동으로 큐를 처리할 수 있습니다
          </Text>
        </View>

        {/* 실시간 이벤트 정보 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>⚡ 실시간 이벤트</Text>
          <Text style={styles.instructionText}>
            • 발주 생성 시 `po:created` 이벤트가 발생합니다{'\n'}
            • 웹 사이드바의 배지가 실시간으로 업데이트됩니다{'\n'}
            • 2초 후 백그라운드에서 정확한 값으로 보정됩니다{'\n'}
            • 모든 이벤트는 권한 범위(`branch_id`)로 필터링됩니다
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
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
  header: {
    alignItems: 'center',
    marginBottom: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  section: {
    marginBottom: 24,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 16,
  },
  statusContainer: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
  },
  statusText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  statusValue: {
    fontWeight: 'bold',
    color: '#007AFF',
  },
  testButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  testButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '500',
  },
  queueButton: {
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  flushButton: {
    backgroundColor: '#34C759',
  },
  clearButton: {
    backgroundColor: '#FF9500',
  },
  queueButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '500',
  },
  instructionText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
});
