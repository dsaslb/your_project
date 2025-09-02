import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  StyleSheet,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform
} from 'react-native';
import PurchaseOrderAPI, { PurchaseOrderItem } from '../api/purchaseOrders';
import SafePost from '../utils/safePost';

interface CreatePurchaseOrderScreenProps {
  navigation: any;
  route: {
    params: {
      branchId: string;
      branchName: string;
    };
  };
}

export default function CreatePurchaseOrderScreen({ 
  navigation, 
  route 
}: CreatePurchaseOrderScreenProps) {
  const { branchId, branchName } = route.params;
  
  const [items, setItems] = useState<PurchaseOrderItem[]>([
    { barcode: '', name: '', qty: 1 }
  ]);
  const [notes, setNotes] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 아이템 추가
  const addItem = () => {
    setItems([...items, { barcode: '', name: '', qty: 1 }]);
  };

  // 아이템 제거
  const removeItem = (index: number) => {
    if (items.length > 1) {
      const newItems = items.filter((_, i) => i !== index);
      setItems(newItems);
    }
  };

  // 아이템 업데이트
  const updateItem = (index: number, field: keyof PurchaseOrderItem, value: string | number) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    setItems(newItems);
  };

  // 발주 생성
  const handleSubmit = async () => {
    // 유효성 검사
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const request = {
        branch_id: branchId,
        items: items.filter(item => item.barcode && item.name && item.qty > 0),
        notes,
        priority
      };

      console.log('📋 발주 생성 요청:', request);

      const response = await PurchaseOrderAPI.createPurchaseOrder(request);

      if (response.success) {
        Alert.alert(
          '✅ 발주 생성 성공',
          `발주가 성공적으로 생성되었습니다.\n발주 ID: ${response.data?.po_id}`,
          [
            {
              text: '확인',
              onPress: () => navigation.goBack()
            }
          ]
        );
      } else {
        if (response.error === 'offline') {
          Alert.alert(
            '📱 오프라인 상태',
            '발주가 오프라인 큐에 저장되었습니다. 네트워크 연결 시 자동으로 전송됩니다.',
            [{ text: '확인' }]
          );
        } else {
          Alert.alert(
            '❌ 발주 생성 실패',
            response.message || '알 수 없는 오류가 발생했습니다.',
            [{ text: '확인' }]
          );
        }
      }

    } catch (error) {
      console.error('❌ 발주 생성 오류:', error);
      Alert.alert(
        '❌ 오류',
        '발주 생성 중 오류가 발생했습니다.',
        [{ text: '확인' }]
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // 폼 유효성 검사
  const validateForm = (): boolean => {
    // 최소 1개 아이템 필요
    const validItems = items.filter(item => 
      item.barcode.trim() && item.name.trim() && item.qty > 0
    );

    if (validItems.length === 0) {
      Alert.alert('⚠️ 경고', '최소 1개 이상의 아이템을 입력해주세요.');
      return false;
    }

    // 바코드 중복 확인
    const barcodes = validItems.map(item => item.barcode.trim());
    const uniqueBarcodes = new Set(barcodes);
    
    if (barcodes.length !== uniqueBarcodes.size) {
      Alert.alert('⚠️ 경고', '중복된 바코드가 있습니다.');
      return false;
    }

    return true;
  };

  // 오프라인 큐 상태 확인
  const checkQueueStatus = async () => {
    const status = await SafePost.getQueueStatus();
    Alert.alert(
      '📦 오프라인 큐 상태',
      `대기 중인 요청: ${status.count}개\n${
        status.oldestRequest 
          ? `가장 오래된 요청: ${new Date(status.oldestRequest.timestamp).toLocaleString()}`
          : '대기 중인 요청이 없습니다.'
      }`
    );
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
            await SafePost.flushQueue();
            Alert.alert('✅ 완료', '오프라인 큐 처리가 완료되었습니다.');
          }
        }
      ]
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoidingView}
      >
        <ScrollView style={styles.scrollView}>
          {/* 헤더 */}
          <View style={styles.header}>
            <Text style={styles.title}>📋 새 발주 생성</Text>
            <Text style={styles.subtitle}>{branchName}</Text>
          </View>

          {/* 아이템 목록 */}
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>📦 발주 아이템</Text>
              <TouchableOpacity onPress={addItem} style={styles.addButton}>
                <Text style={styles.addButtonText}>+ 추가</Text>
              </TouchableOpacity>
            </View>

            {items.map((item, index) => (
              <View key={index} style={styles.itemContainer}>
                <View style={styles.itemRow}>
                  <TextInput
                    style={[styles.input, styles.barcodeInput]}
                    placeholder="바코드"
                    value={item.barcode}
                    onChangeText={(value) => updateItem(index, 'barcode', value)}
                    autoCapitalize="none"
                  />
                  <TextInput
                    style={[styles.input, styles.nameInput]}
                    placeholder="상품명"
                    value={item.name}
                    onChangeText={(value) => updateItem(index, 'name', value)}
                  />
                  <TextInput
                    style={[styles.input, styles.qtyInput]}
                    placeholder="수량"
                    value={item.qty.toString()}
                    onChangeText={(value) => updateItem(index, 'qty', parseInt(value) || 0)}
                    keyboardType="numeric"
                  />
                  {items.length > 1 && (
                    <TouchableOpacity 
                      onPress={() => removeItem(index)}
                      style={styles.removeButton}
                    >
                      <Text style={styles.removeButtonText}>×</Text>
                    </TouchableOpacity>
                  )}
                </View>
              </View>
            ))}
          </View>

          {/* 우선순위 */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🎯 우선순위</Text>
            <View style={styles.priorityContainer}>
              {(['low', 'medium', 'high'] as const).map((p) => (
                <TouchableOpacity
                  key={p}
                  style={[
                    styles.priorityButton,
                    priority === p && styles.priorityButtonActive
                  ]}
                  onPress={() => setPriority(p)}
                >
                  <Text style={[
                    styles.priorityButtonText,
                    priority === p && styles.priorityButtonTextActive
                  ]}>
                    {p === 'low' ? '낮음' : p === 'medium' ? '보통' : '높음'}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* 메모 */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>📝 메모</Text>
            <TextInput
              style={[styles.input, styles.notesInput]}
              placeholder="발주 관련 메모를 입력하세요"
              value={notes}
              onChangeText={setNotes}
              multiline
              numberOfLines={3}
            />
          </View>

          {/* 오프라인 큐 관리 */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>📱 오프라인 큐</Text>
            <View style={styles.queueButtons}>
              <TouchableOpacity 
                onPress={checkQueueStatus}
                style={styles.queueButton}
              >
                <Text style={styles.queueButtonText}>상태 확인</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                onPress={flushQueue}
                style={styles.queueButton}
              >
                <Text style={styles.queueButtonText}>큐 비우기</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* 제출 버튼 */}
          <TouchableOpacity
            style={[styles.submitButton, isSubmitting && styles.submitButtonDisabled]}
            onPress={handleSubmit}
            disabled={isSubmitting}
          >
            <Text style={styles.submitButtonText}>
              {isSubmitting ? '처리 중...' : '📋 발주 생성'}
            </Text>
          </TouchableOpacity>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  keyboardAvoidingView: {
    flex: 1,
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
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
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
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  addButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  addButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '500',
  },
  itemContainer: {
    marginBottom: 12,
  },
  itemRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 16,
    backgroundColor: 'white',
  },
  barcodeInput: {
    flex: 2,
  },
  nameInput: {
    flex: 3,
  },
  qtyInput: {
    flex: 1,
    textAlign: 'center',
  },
  notesInput: {
    height: 80,
    textAlignVertical: 'top',
  },
  removeButton: {
    backgroundColor: '#FF3B30',
    width: 30,
    height: 30,
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
  },
  removeButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  priorityContainer: {
    flexDirection: 'row',
    gap: 12,
  },
  priorityButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
    backgroundColor: 'white',
    alignItems: 'center',
  },
  priorityButtonActive: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  priorityButtonText: {
    fontSize: 16,
    color: '#333',
    fontWeight: '500',
  },
  priorityButtonTextActive: {
    color: 'white',
  },
  queueButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  queueButton: {
    flex: 1,
    backgroundColor: '#34C759',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  queueButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '500',
  },
  submitButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 16,
    marginBottom: 32,
  },
  submitButtonDisabled: {
    backgroundColor: '#ccc',
  },
  submitButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
  },
});
