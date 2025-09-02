import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { safePost, flushQueue, getQueueStatus } from '../utils/safePost';

// API 클라이언트 타입 (실제 구현에 맞게 수정 필요)
interface ApiClient {
  post: (url: string, body: any, options?: any) => Promise<any>;
}

// 상품 타입
interface Product {
  id: string;
  barcode: string;
  name: string;
  currentStock: number;
}

// 발주 아이템 타입
interface OrderItem {
  barcode: string;
  name: string;
  qty: number;
}

interface PurchaseOrderScreenProps {
  navigation: any;
  route: any;
}

export default function PurchaseOrderScreen({ navigation, route }: PurchaseOrderScreenProps) {
  const [selectedItems, setSelectedItems] = useState<OrderItem[]>([]);
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [queueStatus, setQueueStatus] = useState({ total: 0, recent: 0, old: 0 });
  
  // 현재 지점 ID (실제로는 인증/컨텍스트에서 가져와야 함)
  const currentBranchId = route.params?.branchId || 1;
  
  // 샘플 상품 데이터 (실제로는 API에서 가져와야 함)
  const sampleProducts: Product[] = [
    { id: '1', barcode: '123456789', name: '상품 A', currentStock: 10 },
    { id: '2', barcode: '987654321', name: '상품 B', currentStock: 5 },
    { id: '3', barcode: '456789123', name: '상품 C', currentStock: 15 },
  ];

  // 큐 상태 확인
  useEffect(() => {
    checkQueueStatus();
  }, []);

  const checkQueueStatus = async () => {
    try {
      const status = await getQueueStatus();
      setQueueStatus(status);
    } catch (error) {
      console.error('큐 상태 확인 실패:', error);
    }
  };

  // 상품 선택/해제
  const toggleProduct = (product: Product) => {
    setSelectedItems(prev => {
      const existing = prev.find(item => item.barcode === product.barcode);
      if (existing) {
        return prev.filter(item => item.barcode !== product.barcode);
      } else {
        return [...prev, { barcode: product.barcode, name: product.name, qty: 1 }];
      }
    });
  };

  // 수량 변경
  const updateQuantity = (barcode: string, qty: number) => {
    if (qty < 1) return;
    
    setSelectedItems(prev =>
      prev.map(item =>
        item.barcode === barcode ? { ...item, qty } : item
      )
    );
  };

  // 발주 생성
  const createPurchaseOrder = async () => {
    if (selectedItems.length === 0) {
      Alert.alert('알림', '발주할 상품을 선택해주세요.');
      return;
    }

    setIsSubmitting(true);

    try {
      // API 클라이언트 (실제 구현에 맞게 수정 필요)
      const apiClient: ApiClient = {
        post: async (url: string, body: any, options?: any) => {
          // 실제 API 호출 구현
          const response = await fetch(`http://localhost:5000${url}`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...options?.headers,
            },
            body: JSON.stringify(body),
          });
          
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
          
          return response.json();
        }
      };

      // 발주 데이터 구성
      const orderData = {
        branch_id: currentBranchId,
        items: selectedItems,
        notes: notes.trim(),
      };

      // 안전한 POST 요청
      const result = await safePost(
        apiClient,
        '/api/mobile/purchase_orders',
        orderData
      );

      Alert.alert(
        '성공',
        '발주가 성공적으로 생성되었습니다.',
        [
          {
            text: '확인',
            onPress: () => {
              // 발주 목록 화면으로 이동
              navigation.navigate('PurchaseOrderList');
            }
          }
        ]
      );

      // 폼 초기화
      setSelectedItems([]);
      setNotes('');

    } catch (error) {
      console.error('발주 생성 실패:', error);
      
      // 오프라인 큐에 저장된 경우
      if (error.message?.includes('Network request failed')) {
        Alert.alert(
          '오프라인 상태',
          '네트워크 연결이 없습니다. 발주가 오프라인 큐에 저장되었으며, 연결 복구 시 자동으로 전송됩니다.',
          [{ text: '확인' }]
        );
        
        // 큐 상태 업데이트
        checkQueueStatus();
      } else {
        Alert.alert('오류', '발주 생성 중 오류가 발생했습니다. 다시 시도해주세요.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // 오프라인 큐 처리
  const processOfflineQueue = async () => {
    try {
      const apiClient: ApiClient = {
        post: async (url: string, body: any, options?: any) => {
          const response = await fetch(`http://localhost:5000${url}`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...options?.headers,
            },
            body: JSON.stringify(body),
          });
          
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
          
          return response.json();
        }
      };

      const processedCount = await flushQueue(apiClient);
      
      if (processedCount > 0) {
        Alert.alert('성공', `${processedCount}개의 오프라인 작업이 처리되었습니다.`);
        checkQueueStatus();
      } else {
        Alert.alert('알림', '처리할 오프라인 작업이 없습니다.');
      }
      
    } catch (error) {
      console.error('오프라인 큐 처리 실패:', error);
      Alert.alert('오류', '오프라인 큐 처리 중 오류가 발생했습니다.');
    }
  };

  return (
    <ScrollView style={styles.container}>
      {/* 헤더 */}
      <View style={styles.header}>
        <Text style={styles.title}>발주 생성</Text>
        <Text style={styles.subtitle}>지점: {currentBranchId}</Text>
      </View>

      {/* 오프라인 큐 상태 */}
      {queueStatus.total > 0 && (
        <View style={styles.queueStatus}>
          <Text style={styles.queueTitle}>📱 오프라인 큐</Text>
          <Text style={styles.queueText}>
            총 {queueStatus.total}개 작업 (최근: {queueStatus.recent}개)
          </Text>
          <TouchableOpacity
            style={styles.queueButton}
            onPress={processOfflineQueue}
          >
            <Text style={styles.queueButtonText}>큐 처리하기</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* 상품 선택 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>상품 선택</Text>
        {sampleProducts.map(product => {
          const isSelected = selectedItems.some(item => item.barcode === product.barcode);
          const selectedItem = selectedItems.find(item => item.barcode === product.barcode);
          
          return (
            <View key={product.id} style={styles.productItem}>
              <TouchableOpacity
                style={[styles.productCheckbox, isSelected && styles.productCheckboxSelected]}
                onPress={() => toggleProduct(product)}
              >
                {isSelected && <Text style={styles.checkmark}>✓</Text>}
              </TouchableOpacity>
              
              <View style={styles.productInfo}>
                <Text style={styles.productName}>{product.name}</Text>
                <Text style={styles.productBarcode}>바코드: {product.barcode}</Text>
                <Text style={styles.productStock}>현재 재고: {product.currentStock}개</Text>
              </View>
              
              {isSelected && (
                <View style={styles.quantityControl}>
                  <TouchableOpacity
                    style={styles.quantityButton}
                    onPress={() => updateQuantity(product.barcode, (selectedItem?.qty || 1) - 1)}
                  >
                    <Text style={styles.quantityButtonText}>-</Text>
                  </TouchableOpacity>
                  
                  <Text style={styles.quantityText}>{selectedItem?.qty || 1}</Text>
                  
                  <TouchableOpacity
                    style={styles.quantityButton}
                    onPress={() => updateQuantity(product.barcode, (selectedItem?.qty || 1) + 1)}
                  >
                    <Text style={styles.quantityButtonText}>+</Text>
                  </TouchableOpacity>
                </View>
              )}
            </View>
          );
        })}
      </View>

      {/* 선택된 상품 요약 */}
      {selectedItems.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>선택된 상품</Text>
          {selectedItems.map((item, index) => (
            <View key={index} style={styles.selectedItem}>
              <Text style={styles.selectedItemName}>{item.name}</Text>
              <Text style={styles.selectedItemQty}>수량: {item.qty}개</Text>
            </View>
          ))}
        </View>
      )}

      {/* 비고 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>비고</Text>
        <TextInput
          style={styles.notesInput}
          placeholder="발주 관련 특이사항을 입력하세요..."
          value={notes}
          onChangeText={setNotes}
          multiline
          numberOfLines={3}
        />
      </View>

      {/* 발주 생성 버튼 */}
      <TouchableOpacity
        style={[styles.submitButton, isSubmitting && styles.submitButtonDisabled]}
        onPress={createPurchaseOrder}
        disabled={isSubmitting || selectedItems.length === 0}
      >
        {isSubmitting ? (
          <ActivityIndicator color="white" />
        ) : (
          <Text style={styles.submitButtonText}>
            발주 생성 ({selectedItems.length}개 상품)
          </Text>
        )}
      </TouchableOpacity>

      {/* 안내 메시지 */}
      <View style={styles.infoSection}>
        <Text style={styles.infoTitle}>💡 안내사항</Text>
        <Text style={styles.infoText}>
          • 모든 발주 요청에는 고유한 멱등성 키가 포함됩니다{'\n'}
          • 오프라인 상태에서는 요청이 큐에 저장됩니다{'\n'}
          • 네트워크 복구 시 자동으로 전송됩니다{'\n'}
          • 중복 요청은 자동으로 방지됩니다
        </Text>
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
    backgroundColor: 'white',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 5,
  },
  queueStatus: {
    backgroundColor: '#fff3cd',
    margin: 15,
    padding: 15,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ffeaa7',
  },
  queueTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#856404',
    marginBottom: 5,
  },
  queueText: {
    fontSize: 14,
    color: '#856404',
    marginBottom: 10,
  },
  queueButton: {
    backgroundColor: '#856404',
    padding: 8,
    borderRadius: 4,
    alignSelf: 'flex-start',
  },
  queueButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '500',
  },
  section: {
    backgroundColor: 'white',
    margin: 15,
    padding: 15,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  productItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  productCheckbox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#ddd',
    marginRight: 15,
    alignItems: 'center',
    justifyContent: 'center',
  },
  productCheckboxSelected: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  checkmark: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  productInfo: {
    flex: 1,
  },
  productName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
  },
  productBarcode: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  productStock: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  quantityControl: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  quantityButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#007AFF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  quantityButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  quantityText: {
    fontSize: 16,
    fontWeight: '500',
    marginHorizontal: 15,
    minWidth: 30,
    textAlign: 'center',
  },
  selectedItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  selectedItemName: {
    fontSize: 16,
    color: '#333',
  },
  selectedItemQty: {
    fontSize: 14,
    color: '#666',
  },
  notesInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    minHeight: 80,
    textAlignVertical: 'top',
  },
  submitButton: {
    backgroundColor: '#007AFF',
    margin: 15,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  submitButtonDisabled: {
    backgroundColor: '#ccc',
  },
  submitButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  infoSection: {
    backgroundColor: '#e3f2fd',
    margin: 15,
    padding: 15,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#bbdefb',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1976d2',
    marginBottom: 10,
  },
  infoText: {
    fontSize: 14,
    color: '#1976d2',
    lineHeight: 20,
  },
});

