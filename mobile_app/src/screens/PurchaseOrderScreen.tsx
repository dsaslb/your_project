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

interface PurchaseOrderItem {
  barcode: string;
  name: string;
  quantity: number;
}

interface PurchaseOrder {
  id: string;
  status: string;
  items: PurchaseOrderItem[];
  created_at: string;
}

export default function PurchaseOrderScreen({ onBack }: { onBack: () => void }) {
  console.log('📋 PurchaseOrderScreen 렌더링됨');
  
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newItems, setNewItems] = useState<PurchaseOrderItem[]>([
    { barcode: '', name: '', quantity: 1 }
  ]);

  useEffect(() => {
    console.log('📋 PurchaseOrderScreen useEffect 실행됨');
    loadPurchaseOrders();
  }, []);

  const loadPurchaseOrders = async () => {
    try {
      setIsLoading(true);
      const response = await api.getPurchaseOrders();
      setOrders(response.data || []);
    } catch (error: any) {
      console.error('발주 목록 조회 실패:', error);
      Alert.alert('오류', '발주 목록을 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const addItem = () => {
    setNewItems([...newItems, { barcode: '', name: '', quantity: 1 }]);
  };

  const removeItem = (index: number) => {
    if (newItems.length > 1) {
      setNewItems(newItems.filter((_, i) => i !== index));
    }
  };

  const updateItem = (index: number, field: keyof PurchaseOrderItem, value: string | number) => {
    const updatedItems = [...newItems];
    updatedItems[index] = { ...updatedItems[index], [field]: value };
    setNewItems(updatedItems);
  };

  const createPurchaseOrder = async () => {
    // 유효성 검사
    const validItems = newItems.filter(item => 
      item.barcode.trim() && item.name.trim() && item.quantity > 0
    );

    if (validItems.length === 0) {
      Alert.alert('오류', '최소 하나의 발주 항목을 입력해주세요.');
      return;
    }

    try {
      setIsLoading(true);
      const response = await safePost('/api/mobile/purchase_orders', {
        items: validItems
      });

      Alert.alert('성공', '발주가 성공적으로 생성되었습니다!');
      setShowCreateModal(false);
      setNewItems([{ barcode: '', name: '', quantity: 1 }]);
      loadPurchaseOrders(); // 목록 새로고침
    } catch (error: any) {
      console.error('발주 생성 실패:', error);
      Alert.alert('오류', error.response?.data?.error || '발주 생성에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'requested': return '#FF9500';
      case 'approved': return '#34C759';
      case 'ordered': return '#007AFF';
      case 'received': return '#5856D6';
      case 'rejected': return '#FF3B30';
      default: return '#8E8E93';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'requested': return '요청됨';
      case 'approved': return '승인됨';
      case 'ordered': return '주문됨';
      case 'received': return '수령됨';
      case 'rejected': return '거부됨';
      default: return status;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* 헤더 */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <Text style={styles.backButtonText}>← 뒤로</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>📋 발주 관리</Text>
        <TouchableOpacity 
          onPress={() => setShowCreateModal(true)}
          style={styles.createButton}
        >
          <Text style={styles.createButtonText}>+ 새 발주</Text>
        </TouchableOpacity>
      </View>

      {/* 발주 목록 */}
      <ScrollView style={styles.content}>
        {isLoading ? (
          <ActivityIndicator size="large" color="#007AFF" style={styles.loader} />
        ) : orders.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>아직 발주가 없습니다</Text>
            <Text style={styles.emptyStateSubtext}>새 발주를 생성해보세요</Text>
          </View>
        ) : (
          orders.map((order) => (
            <View key={order.id} style={styles.orderCard}>
              <View style={styles.orderHeader}>
                <Text style={styles.orderId}>#{order.id}</Text>
                <View style={[styles.statusBadge, { backgroundColor: getStatusColor(order.status) }]}>
                  <Text style={styles.statusText}>{getStatusText(order.status)}</Text>
                </View>
              </View>
              
              <Text style={styles.orderDate}>
                {new Date(order.created_at).toLocaleDateString('ko-KR')}
              </Text>
              
              <View style={styles.itemsContainer}>
                {order.items.map((item, index) => (
                  <View key={index} style={styles.itemRow}>
                    <Text style={styles.itemBarcode}>{item.barcode}</Text>
                    <Text style={styles.itemName}>{item.name}</Text>
                    <Text style={styles.itemQuantity}>x{item.quantity}</Text>
                  </View>
                ))}
              </View>
            </View>
          ))
        )}
      </ScrollView>

      {/* 발주 생성 모달 */}
      <Modal
        visible={showCreateModal}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setShowCreateModal(false)}>
              <Text style={styles.cancelButton}>취소</Text>
            </TouchableOpacity>
            <Text style={styles.modalTitle}>새 발주 생성</Text>
            <TouchableOpacity onPress={createPurchaseOrder} disabled={isLoading}>
              <Text style={[styles.saveButton, isLoading && styles.saveButtonDisabled]}>
                {isLoading ? '생성 중...' : '생성'}
              </Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.modalContent}>
            <Text style={styles.sectionTitle}>발주 항목</Text>
            
            {newItems.map((item, index) => (
              <View key={index} style={styles.itemInputContainer}>
                <View style={styles.itemInputRow}>
                  <TextInput
                    style={styles.barcodeInput}
                    placeholder="바코드"
                    value={item.barcode}
                    onChangeText={(text) => updateItem(index, 'barcode', text)}
                  />
                  <TextInput
                    style={styles.nameInput}
                    placeholder="상품명"
                    value={item.name}
                    onChangeText={(text) => updateItem(index, 'name', text)}
                  />
                  <TextInput
                    style={styles.quantityInput}
                    placeholder="수량"
                    value={item.quantity.toString()}
                    onChangeText={(text) => updateItem(index, 'quantity', parseInt(text) || 1)}
                    keyboardType="numeric"
                  />
                  {newItems.length > 1 && (
                    <TouchableOpacity onPress={() => removeItem(index)} style={styles.removeButton}>
                      <Text style={styles.removeButtonText}>×</Text>
                    </TouchableOpacity>
                  )}
                </View>
              </View>
            ))}

            <TouchableOpacity onPress={addItem} style={styles.addItemButton}>
              <Text style={styles.addItemButtonText}>+ 항목 추가</Text>
            </TouchableOpacity>
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
  createButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  createButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
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
  orderCard: {
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
  orderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  orderId: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000000',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
  },
  orderDate: {
    fontSize: 14,
    color: '#8E8E93',
    marginBottom: 12,
  },
  itemsContainer: {
    gap: 8,
  },
  itemRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 4,
  },
  itemBarcode: {
    fontSize: 12,
    color: '#8E8E93',
    width: 80,
  },
  itemName: {
    flex: 1,
    fontSize: 14,
    color: '#000000',
    marginHorizontal: 8,
  },
  itemQuantity: {
    fontSize: 14,
    fontWeight: '600',
    color: '#007AFF',
    width: 40,
    textAlign: 'right',
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
    marginBottom: 16,
  },
  itemInputContainer: {
    marginBottom: 16,
  },
  itemInputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  barcodeInput: {
    flex: 2,
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    backgroundColor: '#FFFFFF',
  },
  nameInput: {
    flex: 3,
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    backgroundColor: '#FFFFFF',
  },
  quantityInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    backgroundColor: '#FFFFFF',
    textAlign: 'center',
  },
  removeButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#FF3B30',
    alignItems: 'center',
    justifyContent: 'center',
  },
  removeButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  addItemButton: {
    alignItems: 'center',
    paddingVertical: 16,
    borderWidth: 2,
    borderColor: '#007AFF',
    borderStyle: 'dashed',
    borderRadius: 8,
    marginTop: 8,
  },
  addItemButtonText: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '600',
  },
});
